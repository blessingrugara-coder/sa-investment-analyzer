"""
Portfolio management - Enhanced with transaction ledger support
"""
from database.session import get_session, get_db_session
from database.models import (
    Portfolio, PortfolioHolding, InvestmentProduct, 
    Transaction, TransactionType, CashPool
)
from analytics.ledger_calculator import LedgerCalculator
from datetime import datetime, date
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class PortfolioManager:
    """Manage portfolio operations with transaction ledger support"""
    
    def __init__(self):
        self.session = None
    
    def create_portfolio(self, name, description=None):
        """
        Create a new portfolio with default cash pool
        
        Args:
            name: Portfolio name (must be unique)
            description: Optional description
            
        Returns:
            Portfolio object or None if name exists
        """
        try:
            with get_db_session() as session:
                # Check if name already exists
                existing = session.query(Portfolio).filter_by(name=name).first()
                if existing:
                    logger.warning(f"Portfolio '{name}' already exists")
                    return None
                
                portfolio = Portfolio(
                    name=name,
                    description=description,
                    created_date=date.today(),
                    base_currency='ZAR',
                    is_active=True
                )
                session.add(portfolio)
                session.flush()
                
                # Create default cash pool
                cash_pool = CashPool(
                    portfolio_id=portfolio.id,
                    name=f"{name} - Cash",
                    currency='ZAR',
                    account_type='CHECKING',
                    current_balance=0.0
                )
                session.add(cash_pool)
                
                logger.info(f"Created portfolio: {name} with cash pool")
                return portfolio
                
        except Exception as e:
            logger.error(f"Error creating portfolio: {e}")
            return None
    
    def add_transaction(self, portfolio_name: str, product_identifier: str,
                       transaction_type: str, quantity: float, price: float,
                       transaction_date: date = None, fees: float = 0,
                       taxes: float = 0, notes: str = None) -> bool:
        """
        Add a transaction to portfolio (NEW method using ledger)
        
        Args:
            portfolio_name: Name of portfolio
            product_identifier: Product ticker/identifier
            transaction_type: BUY, SELL, DIVIDEND, etc.
            quantity: Number of shares/units
            price: Price per unit
            transaction_date: Transaction date (defaults to today)
            fees: Transaction fees
            taxes: Taxes paid
            notes: Optional notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_session() as session:
                # Get portfolio
                portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
                if not portfolio:
                    logger.error(f"Portfolio '{portfolio_name}' not found")
                    return False
                
                # Get product
                product = session.query(InvestmentProduct).filter_by(
                    identifier=product_identifier
                ).first()
                if not product:
                    logger.error(f"Product '{product_identifier}' not found")
                    return False
                
                # Get default cash pool
                cash_pool = session.query(CashPool).filter_by(
                    portfolio_id=portfolio.id
                ).first()
                
                # Calculate amounts
                gross_amount = quantity * price
                net_amount = gross_amount + fees + taxes  # Total outflow for buy
                
                if transaction_type.upper() == 'SELL':
                    net_amount = gross_amount - fees - taxes  # Total inflow for sell
                
                # Create transaction
                txn = Transaction(
                    portfolio_id=portfolio.id,
                    product_id=product.id,
                    cash_pool_id=cash_pool.id if cash_pool else None,
                    transaction_type=TransactionType[transaction_type.upper()],
                    transaction_date=transaction_date or date.today(),
                    quantity=quantity if transaction_type.upper() == 'BUY' else -quantity,
                    price=price,
                    gross_amount=gross_amount,
                    fees=fees,
                    taxes=taxes,
                    net_amount=net_amount if transaction_type.upper() == 'BUY' else -net_amount,
                    notes=notes,
                    currency='ZAR'
                )
                session.add(txn)
                
                # Update cash pool if exists
                if cash_pool:
                    if transaction_type.upper() == 'BUY':
                        cash_pool.current_balance -= net_amount
                    elif transaction_type.upper() == 'SELL':
                        cash_pool.current_balance += abs(net_amount)
                
                logger.info(f"Added {transaction_type} transaction: {product_identifier} to {portfolio_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            return False
    
    def add_holding(self, portfolio_name, ticker, quantity, entry_price, entry_date=None):
        """
        Add a holding (LEGACY method - converts to transaction)
        Kept for backward compatibility
        
        Args:
            portfolio_name: Name of portfolio
            ticker: Product identifier
            quantity: Number of shares/units
            entry_price: Purchase price
            entry_date: Purchase date (defaults to today)
            
        Returns:
            True if successful, False otherwise
        """
        return self.add_transaction(
            portfolio_name=portfolio_name,
            product_identifier=ticker,
            transaction_type='BUY',
            quantity=quantity,
            price=entry_price,
            transaction_date=entry_date or date.today(),
            fees=0,
            taxes=0,
            notes="Added via legacy add_holding method"
        )
    
    def get_portfolio(self, portfolio_name, include_market_values=True):
        """
        Get portfolio with all holdings (calculated from transactions)
        
        Args:
            portfolio_name: Portfolio name
            include_market_values: Include current prices and market values
        
        Returns:
            DataFrame with holdings or None
        """
        try:
            session = get_session()
            
            portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
            if not portfolio:
                session.close()
                return None
            
            # Use LedgerCalculator to get holdings
            calculator = LedgerCalculator(portfolio.id, session)
            holdings_df = calculator.get_holdings_detail()
            
            if holdings_df.empty:
                session.close()
                return holdings_df
            
            # Add market values if requested
            if include_market_values:
                from data.price_fetcher import PriceFetcher
                fetcher = PriceFetcher()
                
                current_prices = []
                market_values = []
                unrealized_gains = []
                unrealized_pct = []
                
                for _, row in holdings_df.iterrows():
                    # Get product
                    product = session.query(InvestmentProduct).filter_by(
                        identifier=row['Ticker']
                    ).first()
                    
                    if product:
                        # Get latest price
                        current_price = fetcher.get_latest_price(product.id)
                        
                        if current_price:
                            market_value = row['Quantity'] * current_price
                            gain = market_value - row['Cost Basis']
                            gain_pct = (gain / row['Cost Basis'] * 100) if row['Cost Basis'] > 0 else 0
                        else:
                            # Fallback to cost basis
                            current_price = row['Avg Entry Price']
                            market_value = row['Cost Basis']
                            gain = 0
                            gain_pct = 0
                    else:
                        current_price = row['Avg Entry Price']
                        market_value = row['Cost Basis']
                        gain = 0
                        gain_pct = 0
                    
                    current_prices.append(current_price)
                    market_values.append(market_value)
                    unrealized_gains.append(gain)
                    unrealized_pct.append(gain_pct)
                
                holdings_df['Current Price'] = current_prices
                holdings_df['Market Value'] = market_values
                holdings_df['Unrealized Gain'] = unrealized_gains
                holdings_df['Gain %'] = unrealized_pct
            
            session.close()
            return holdings_df
            
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_portfolio_transactions(self, portfolio_name):
        """
        Get all transactions for a portfolio
        
        Returns:
            DataFrame with transaction history
        """
        try:
            session = get_session()
            
            portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
            if not portfolio:
                session.close()
                return None
            
            calculator = LedgerCalculator(portfolio.id, session)
            transactions_df = calculator.get_transaction_summary()
            
            session.close()
            return transactions_df
            
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            return None
    
    def list_portfolios(self):
        """Get list of all portfolios"""
        try:
            session = get_session()
            portfolios = session.query(Portfolio).filter_by(is_active=True).all()
            
            data = [{
                'Name': p.name,
                'Description': p.description or '',
                'Created': p.created_date,
                'Holdings': len(LedgerCalculator(p.id, session).get_current_holdings())
            } for p in portfolios]
            
            session.close()
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error listing portfolios: {e}")
            return pd.DataFrame()
    
    def delete_portfolio(self, portfolio_name):
        """Delete a portfolio (cascade deletes transactions and cash pools)"""
        try:
            with get_db_session() as session:
                portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
                if portfolio:
                    session.delete(portfolio)
                    logger.info(f"Deleted portfolio: {portfolio_name}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting portfolio: {e}")
            return False
    
    def get_portfolio_summary(self, portfolio_name):
        """
        Get portfolio summary statistics (using ledger calculator)
        
        Returns:
            Dict with summary stats
        """
        try:
            session = get_session()
            
            portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
            if not portfolio:
                session.close()
                return None
            
            calculator = LedgerCalculator(portfolio.id, session)
            
            # Get performance summary
            perf_summary = calculator.get_performance_summary()
            
            # Get holdings with market values
            holdings_df = self.get_portfolio(portfolio_name, include_market_values=True)
            
            if holdings_df is None or holdings_df.empty:
                session.close()
                return {
                    'total_value': 0,
                    'market_value': 0,
                    'cost_basis': 0,
                    'num_holdings': 0,
                    'by_type': {},
                    'by_category': {},
                    'total_unrealized_gain': 0,
                    'total_unrealized_pct': 0
                }
            
            cost_basis = holdings_df['Cost Basis'].sum()
            
            # Use market value if available, otherwise cost basis
            if 'Market Value' in holdings_df.columns:
                total_value = holdings_df['Market Value'].sum()
                total_unrealized = holdings_df['Unrealized Gain'].sum()
                total_unrealized_pct = (total_unrealized / cost_basis * 100) if cost_basis > 0 else 0
            else:
                total_value = cost_basis
                total_unrealized = 0
                total_unrealized_pct = 0
            
            # Group by type (using market value for allocation)
            by_type = holdings_df.groupby('Type')['Market Value' if 'Market Value' in holdings_df.columns else 'Cost Basis'].sum()
            type_allocation = (by_type / total_value * 100).round(2) if total_value > 0 else by_type * 0
            
            # Group by category
            by_category = holdings_df.groupby('Category')['Market Value' if 'Market Value' in holdings_df.columns else 'Cost Basis'].sum()
            category_allocation = (by_category / total_value * 100).round(2) if total_value > 0 else by_category * 0
            
            session.close()
            
            return {
                'total_value': total_value,
                'market_value': total_value,
                'cost_basis': cost_basis,
                'num_holdings': perf_summary['num_holdings'],
                'total_income': perf_summary['total_income'],
                'realized_gains': perf_summary['realized_gains'],
                'total_unrealized_gain': total_unrealized,
                'total_unrealized_pct': total_unrealized_pct,
                'by_type': type_allocation.to_dict(),
                'by_category': category_allocation.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_cash_pools(self, portfolio_name):
        """
        Get all cash pools for a portfolio
        
        Returns:
            DataFrame with cash pool details
        """
        try:
            session = get_session()
            
            portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
            if not portfolio:
                session.close()
                return None
            
            cash_pools = session.query(CashPool).filter_by(
                portfolio_id=portfolio.id,
                is_active=True
            ).all()
            
            data = [{
                'Name': cp.name,
                'Currency': cp.currency,
                'Type': cp.account_type or 'CHECKING',
                'Balance': cp.current_balance
            } for cp in cash_pools]
            
            session.close()
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error getting cash pools: {e}")
            return None
    
    def get_performance_analysis(self, portfolio_name):
        """
        Get performance analysis for portfolio
        
        Returns:
            Dict with performance metrics
        """
        try:
            session = get_session()
            
            portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
            if not portfolio:
                session.close()
                return None
            
            calculator = LedgerCalculator(portfolio.id, session)
            
            # Import here to avoid circular dependencies
            from analytics.portfolio_valuation_helper import PortfolioValuationHelper
            from analytics.performance_metrics import PerformanceMetrics
            
            # Generate portfolio value series
            helper = PortfolioValuationHelper(calculator)
            portfolio_values, cash_flows = helper.get_performance_data_for_calculator()
            
            if portfolio_values.empty:
                session.close()
                return None
            
            # Calculate performance metrics
            perf = PerformanceMetrics(portfolio_values, cash_flows)
            metrics = perf.get_performance_summary()
            
            # Add summary stats
            summary_stats = helper.generate_summary_statistics()
            metrics.update(summary_stats)
            
            session.close()
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance analysis: {e}")
            import traceback
            traceback.print_exc()
            return None