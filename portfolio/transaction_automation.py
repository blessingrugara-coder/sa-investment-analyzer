"""
Recurring Transaction Engine - Automate predictable financial events
Handles dividends, coupons, fees, interest, etc.
"""
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, Optional, List
import logging

from sqlalchemy.orm import Session
from sqlalchemy import or_

from database.models import (
    RecurringTransactionRule, Transaction, CashPool,
    TransactionType, CalculationMethod, Frequency
)
from analytics.ledger_calculator import LedgerCalculator

logger = logging.getLogger(__name__)


class RecurringTransactionEngine:
    """
    Process any recurring transaction events
    Asset-class agnostic, handles all event types
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_rule(self, portfolio_id: int, rule_config: Dict) -> RecurringTransactionRule:
        """
        Create a new recurring transaction rule
        
        Args:
            portfolio_id: Portfolio ID
            rule_config: Dict with all rule parameters
            
        Returns:
            RecurringTransactionRule object
        """
        rule_config['portfolio_id'] = portfolio_id
        rule = RecurringTransactionRule(**rule_config)
        self.session.add(rule)
        self.session.commit()
        
        logger.info(f"Created recurring rule: {rule.rule_name} for portfolio {portfolio_id}")
        return rule
    
    def process_pending_events(self, as_of_date: Optional[date] = None) -> int:
        """
        Check for and execute all due recurring transactions
        
        Args:
            as_of_date: Process events up to this date (default: today)
            
        Returns:
            Number of events executed
        """
        if as_of_date is None:
            as_of_date = datetime.now().date()
        
        # Get all active rules due for execution
        rules = self.session.query(RecurringTransactionRule).filter(
            RecurringTransactionRule.is_active == True,
            RecurringTransactionRule.next_execution_date <= as_of_date,
            or_(
                RecurringTransactionRule.end_date.is_(None),
                RecurringTransactionRule.end_date >= as_of_date
            )
        ).all()
        
        executed_count = 0
        for rule in rules:
            if self._should_execute(rule, as_of_date):
                try:
                    self._execute_rule(rule, as_of_date)
                    executed_count += 1
                except Exception as e:
                    logger.error(f"Error executing rule {rule.rule_name}: {e}")
        
        self.session.commit()
        logger.info(f"Processed {executed_count} recurring events")
        return executed_count
    
    def _should_execute(self, rule: RecurringTransactionRule, as_of_date: date) -> bool:
        """Check if rule should execute on this date"""
        # Don't execute if before start date
        if rule.start_date and as_of_date < rule.start_date:
            return False
        
        # Don't execute if already executed today
        if rule.last_execution_date == as_of_date:
            return False
        
        return True
    
    def _execute_rule(self, rule: RecurringTransactionRule, execution_date: date):
        """
        Execute a recurring transaction rule
        Creates transaction(s) in ledger
        """
        # Calculate amount based on method
        amount = self._calculate_amount(rule, execution_date)
        
        if amount == 0:
            logger.warning(f"Rule {rule.rule_name} calculated amount is 0, skipping")
            return
        
        # Determine transaction type and sign
        if rule.transaction_type in [TransactionType.DIVIDEND, TransactionType.COUPON, TransactionType.INTEREST]:
            # Income event
            net_amount = self._apply_tax(amount, rule.tax_rate)
            gross_amount = amount
            taxes = amount - net_amount if rule.tax_rate else 0
        else:  # FEE, TAX
            # Cost event (negative)
            gross_amount = amount
            net_amount = -abs(amount)
            taxes = 0
        
        # Get current quantity if needed
        quantity = None
        if rule.applies_to_quantity and rule.product_id:
            quantity = self._get_current_quantity(rule)
        
        # Create transaction
        txn = Transaction(
            portfolio_id=rule.portfolio_id,
            product_id=rule.product_id,
            cash_pool_id=rule.cash_pool_id if rule.affects_cash_pool else None,
            transaction_type=rule.transaction_type,
            transaction_date=execution_date,
            quantity=quantity,
            price=rule.amount_value if rule.calculation_method in [CalculationMethod.PER_SHARE, CalculationMethod.PER_UNIT] else None,
            gross_amount=gross_amount,
            fees=0,
            taxes=taxes,
            net_amount=net_amount,
            notes=f"Auto: {rule.rule_name}",
            is_auto_generated=True
        )
        
        # Add specific fields based on transaction type
        if rule.transaction_type == TransactionType.DIVIDEND:
            txn.dividend_per_share = rule.amount_value if rule.calculation_method == CalculationMethod.PER_SHARE else None
        elif rule.transaction_type == TransactionType.INTEREST:
            txn.interest_rate = rule.amount_value if rule.calculation_method == CalculationMethod.PERCENTAGE_NAV else None
        
        self.session.add(txn)
        
        # Handle dividend reinvestment
        if rule.is_reinvested and net_amount > 0 and rule.reinvestment_product_id:
            self._process_reinvestment(rule, net_amount, execution_date)
        
        # Update cash pool
        if rule.affects_cash_pool and rule.cash_pool_id:
            self._update_cash_pool(rule.cash_pool_id, net_amount)
        
        # Update rule execution dates
        rule.last_execution_date = execution_date
        rule.next_execution_date = self._calculate_next_date(
            execution_date, 
            rule.frequency, 
            rule.custom_frequency_days
        )
        
        logger.info(f"Executed rule {rule.rule_name}: {rule.transaction_type.value} amount={net_amount}")
    
    def _calculate_amount(self, rule: RecurringTransactionRule, execution_date: date) -> float:
        """
        Calculate transaction amount based on rule method
        """
        if rule.calculation_method in [CalculationMethod.PER_SHARE, CalculationMethod.PER_UNIT]:
            # Per share/unit calculation
            quantity = self._get_current_quantity(rule)
            return rule.amount_value * quantity
        
        elif rule.calculation_method == CalculationMethod.FIXED_AMOUNT:
            # Fixed amount
            return rule.amount_value
        
        elif rule.calculation_method in [CalculationMethod.PERCENTAGE_NAV, CalculationMethod.PERCENTAGE_VALUE, CalculationMethod.PERCENTAGE_COST]:
            # Percentage-based calculation
            basis_value = self._get_basis_value(
                rule.portfolio_id,
                rule.product_id,
                rule.percentage_basis,
                execution_date
            )
            return basis_value * (rule.amount_value / 100)
        
        return 0
    
    def _get_current_quantity(self, rule: RecurringTransactionRule) -> float:
        """Get current holdings for this product"""
        if not rule.product_id:
            return 0
        
        calculator = LedgerCalculator(rule.portfolio_id, self.session)
        holdings = calculator.get_current_holdings()
        return holdings.get(rule.product_id, 0)
    
    def _get_basis_value(self, portfolio_id: int, product_id: Optional[int], 
                         basis_type: str, as_of_date: date) -> float:
        """
        Get value basis for percentage calculations
        
        Args:
            basis_type: NAV, MARKET_VALUE, COST_BASIS
        """
        calculator = LedgerCalculator(portfolio_id, self.session)
        
        if basis_type == 'COST_BASIS':
            return calculator.calculate_cost_basis_at_date(as_of_date)
        
        elif basis_type in ['NAV', 'MARKET_VALUE']:
            # For now, return cost basis
            # TODO: Implement with price fetcher in Phase 3
            return calculator.calculate_cost_basis_at_date(as_of_date)
        
        return 0
    
    def _apply_tax(self, amount: float, tax_rate: Optional[float]) -> float:
        """Apply tax rate to amount"""
        if tax_rate is None or tax_rate == 0:
            return amount
        return amount * (1 - tax_rate)
    
    def _process_reinvestment(self, rule: RecurringTransactionRule, 
                              net_amount: float, execution_date: date):
        """
        Auto-purchase shares with dividend/income (DRIP)
        """
        if not rule.reinvestment_product_id:
            return
        
        # TODO: Get current price for reinvestment product
        # For now, create placeholder transaction
        # Will implement with price fetcher in Phase 3
        
        buy_txn = Transaction(
            portfolio_id=rule.portfolio_id,
            product_id=rule.reinvestment_product_id,
            transaction_type=TransactionType.BUY,
            transaction_date=execution_date,
            quantity=0,  # Will calculate with price
            price=0,     # Need current market price
            gross_amount=net_amount,
            net_amount=net_amount,
            notes=f"DRIP: Reinvested from {rule.rule_name}",
            is_auto_generated=True
        )
        self.session.add(buy_txn)
        logger.info(f"Created DRIP transaction for {net_amount}")
    
    def _update_cash_pool(self, cash_pool_id: int, amount: float):
        """Update cash pool balance"""
        pool = self.session.query(CashPool).get(cash_pool_id)
        if pool:
            pool.current_balance += amount
            logger.debug(f"Updated cash pool {pool.name}: balance now {pool.current_balance}")
    
    def _calculate_next_date(self, current_date: date, frequency: Frequency, 
                            custom_days: Optional[int] = None) -> date:
        """Calculate next execution date based on frequency"""
        if frequency == Frequency.DAILY:
            return current_date + timedelta(days=1)
        elif frequency == Frequency.WEEKLY:
            return current_date + timedelta(weeks=1)
        elif frequency == Frequency.MONTHLY:
            return current_date + relativedelta(months=1)
        elif frequency == Frequency.QUARTERLY:
            return current_date + relativedelta(months=3)
        elif frequency == Frequency.SEMI_ANNUAL:
            return current_date + relativedelta(months=6)
        elif frequency == Frequency.ANNUAL:
            return current_date + relativedelta(years=1)
        elif frequency == Frequency.CUSTOM and custom_days:
            return current_date + timedelta(days=custom_days)
        else:
            # Default to monthly
            return current_date + relativedelta(months=1)
    
    def get_active_rules(self, portfolio_id: Optional[int] = None) -> List[RecurringTransactionRule]:
        """
        Get all active rules, optionally filtered by portfolio
        
        Args:
            portfolio_id: Optional portfolio filter
            
        Returns:
            List of active rules
        """
        query = self.session.query(RecurringTransactionRule).filter_by(is_active=True)
        
        if portfolio_id:
            query = query.filter_by(portfolio_id=portfolio_id)
        
        return query.order_by(RecurringTransactionRule.next_execution_date).all()
    
    def pause_rule(self, rule_id: int):
        """Pause a recurring rule"""
        rule = self.session.query(RecurringTransactionRule).get(rule_id)
        if rule:
            rule.is_active = False
            self.session.commit()
            logger.info(f"Paused rule: {rule.rule_name}")
    
    def resume_rule(self, rule_id: int):
        """Resume a paused rule"""
        rule = self.session.query(RecurringTransactionRule).get(rule_id)
        if rule:
            rule.is_active = True
            self.session.commit()
            logger.info(f"Resumed rule: {rule.rule_name}")
    
    def delete_rule(self, rule_id: int):
        """Delete a recurring rule"""
        rule = self.session.query(RecurringTransactionRule).get(rule_id)
        if rule:
            rule_name = rule.rule_name
            self.session.delete(rule)
            self.session.commit()
            logger.info(f"Deleted rule: {rule_name}")