"""
Ledger Calculator - Calculate portfolio metrics from transaction ledger
Replaces static holdings with dynamic calculations
"""
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import pandas as pd
import logging

from database.models import Transaction, TransactionType, InvestmentProduct

logger = logging.getLogger(__name__)


class LedgerCalculator:
    """
    Calculate portfolio metrics dynamically from transaction ledger
    No static holdings - everything computed from events
    """
    
    def __init__(self, portfolio_id: int, session):
        """
        Initialize calculator for a specific portfolio
        
        Args:
            portfolio_id: Portfolio ID to calculate for
            session: SQLAlchemy session
        """
        self.portfolio_id = portfolio_id
        self.session = session
        self.transactions = self._load_transactions()
    
    def _load_transactions(self) -> List[Transaction]:
        """Load all transactions for portfolio, ordered by date"""
        return self.session.query(Transaction).filter_by(
            portfolio_id=self.portfolio_id
        ).order_by(Transaction.transaction_date).all()
    
    def get_current_holdings(self) -> Dict[int, float]:
        """
        Calculate current holdings by aggregating all transactions
        
        Returns:
            Dict[product_id, quantity] - current position sizes
        """
        holdings = defaultdict(float)
        
        for txn in self.transactions:
            if not txn.product_id:
                continue
            
            product_id = txn.product_id
            
            if txn.transaction_type in [
                TransactionType.BUY, 
                TransactionType.BONUS, 
                TransactionType.RIGHTS,
                TransactionType.TRANSFER_IN,
                TransactionType.DEPOSIT
            ]:
                holdings[product_id] += abs(txn.quantity) if txn.quantity else 0
                
            elif txn.transaction_type in [
                TransactionType.SELL,
                TransactionType.TRANSFER_OUT,
                TransactionType.WITHDRAWAL
            ]:
                holdings[product_id] -= abs(txn.quantity) if txn.quantity else 0
                
            elif txn.transaction_type == TransactionType.SPLIT:
                # Stock split: multiply holdings by split ratio
                if txn.split_ratio:
                    holdings[product_id] *= txn.split_ratio
        
        # Remove zero/closed positions
        return {pid: qty for pid, qty in holdings.items() if qty > 0.001}
    
    def get_holdings_at_date(self, target_date: date) -> Dict[int, float]:
        """
        Point-in-time reconstruction: holdings as of specific date
        Critical for historical portfolio valuation
        
        Args:
            target_date: Date to calculate holdings for
            
        Returns:
            Dict[product_id, quantity] as of that date
        """
        holdings = defaultdict(float)
        
        for txn in self.transactions:
            if txn.transaction_date > target_date:
                break
            
            if not txn.product_id:
                continue
                
            product_id = txn.product_id
            
            if txn.transaction_type in [
                TransactionType.BUY, 
                TransactionType.BONUS,
                TransactionType.TRANSFER_IN
            ]:
                holdings[product_id] += abs(txn.quantity) if txn.quantity else 0
                
            elif txn.transaction_type in [
                TransactionType.SELL,
                TransactionType.TRANSFER_OUT
            ]:
                holdings[product_id] -= abs(txn.quantity) if txn.quantity else 0
                
            elif txn.transaction_type == TransactionType.SPLIT:
                if txn.split_ratio:
                    holdings[product_id] *= txn.split_ratio
        
        return {pid: qty for pid, qty in holdings.items() if qty > 0.001}
    
    def calculate_cost_basis(self) -> float:
        """
        Total capital deployed (buys + fees - sells)
        Net amount invested in portfolio
        
        Returns:
            Total cost basis in base currency
        """
        total_invested = 0
        total_proceeds = 0
        
        for txn in self.transactions:
            if txn.transaction_type in [
                TransactionType.BUY,
                TransactionType.DEPOSIT
            ]:
                # Money going out (investment)
                total_invested += abs(txn.net_amount) if txn.net_amount else 0
                
            elif txn.transaction_type in [
                TransactionType.SELL,
                TransactionType.WITHDRAWAL
            ]:
                # Money coming in (divestment)
                total_proceeds += abs(txn.net_amount) if txn.net_amount else 0
        
        return total_invested - total_proceeds
    
    def calculate_cost_basis_at_date(self, target_date: date) -> float:
        """Calculate cost basis as of specific date"""
        total_invested = 0
        total_proceeds = 0
        
        for txn in self.transactions:
            if txn.transaction_date > target_date:
                break
                
            if txn.transaction_type in [TransactionType.BUY, TransactionType.DEPOSIT]:
                total_invested += abs(txn.net_amount) if txn.net_amount else 0
            elif txn.transaction_type in [TransactionType.SELL, TransactionType.WITHDRAWAL]:
                total_proceeds += abs(txn.net_amount) if txn.net_amount else 0
        
        return total_invested - total_proceeds
    
    def calculate_total_income(self) -> Dict[str, float]:
        """
        Calculate total income by type
        
        Returns:
            Dict with dividend, interest, and total income
        """
        dividends = 0
        interest = 0
        coupons = 0
        other_income = 0
        
        for txn in self.transactions:
            if txn.transaction_type == TransactionType.DIVIDEND:
                dividends += abs(txn.net_amount) if txn.net_amount else 0
            elif txn.transaction_type == TransactionType.INTEREST:
                interest += abs(txn.net_amount) if txn.net_amount else 0
            elif txn.transaction_type == TransactionType.COUPON:
                coupons += abs(txn.net_amount) if txn.net_amount else 0
            elif txn.transaction_type == TransactionType.OTHER and txn.net_amount and txn.net_amount > 0:
                other_income += abs(txn.net_amount)
        
        total = dividends + interest + coupons + other_income
        
        return {
            'dividends': dividends,
            'interest': interest,
            'coupons': coupons,
            'other': other_income,
            'total': total
        }
    
    def calculate_total_fees(self) -> Dict[str, float]:
        """
        Calculate total fees and taxes paid
        
        Returns:
            Dict with fees, taxes, and total costs
        """
        total_fees = 0
        total_taxes = 0
        
        for txn in self.transactions:
            if txn.fees:
                total_fees += abs(txn.fees)
            if txn.taxes:
                total_taxes += abs(txn.taxes)
            
            # Dedicated FEE and TAX transactions
            if txn.transaction_type == TransactionType.FEE:
                total_fees += abs(txn.net_amount) if txn.net_amount else 0
            elif txn.transaction_type == TransactionType.TAX:
                total_taxes += abs(txn.net_amount) if txn.net_amount else 0
        
        return {
            'fees': total_fees,
            'taxes': total_taxes,
            'total': total_fees + total_taxes
        }
    
    def get_average_entry_price(self, product_id: int) -> float:
        """
        Calculate weighted average entry price for a position
        Uses simple average cost method
        
        Args:
            product_id: Product to calculate for
            
        Returns:
            Average entry price
        """
        buys = [t for t in self.transactions 
                if t.product_id == product_id and 
                t.transaction_type == TransactionType.BUY and
                t.price is not None]
        
        if not buys:
            return 0
        
        total_cost = sum(abs(b.gross_amount) if b.gross_amount else 0 for b in buys)
        total_quantity = sum(abs(b.quantity) if b.quantity else 0 for b in buys)
        
        return total_cost / total_quantity if total_quantity > 0 else 0
    
    def calculate_realized_gains(self) -> float:
        """
        Calculate profit/loss from closed positions (sells)
        Uses FIFO (First In, First Out) method
        
        Returns:
            Total realized gains/losses
        """
        # Track cost basis per product using FIFO
        product_lots = defaultdict(list)  # product_id -> [(quantity, price), ...]
        realized_pl = 0
        
        for txn in self.transactions:
            if not txn.product_id or not txn.quantity:
                continue
            
            product_id = txn.product_id
            
            if txn.transaction_type == TransactionType.BUY:
                # Add to lots
                product_lots[product_id].append({
                    'quantity': abs(txn.quantity),
                    'price': txn.price or 0,
                    'date': txn.transaction_date
                })
            
            elif txn.transaction_type == TransactionType.SELL:
                # Remove from lots (FIFO) and calculate gain
                sell_quantity = abs(txn.quantity)
                sell_price = txn.price or 0
                
                while sell_quantity > 0 and product_lots[product_id]:
                    lot = product_lots[product_id][0]
                    
                    if lot['quantity'] <= sell_quantity:
                        # Entire lot sold
                        qty_sold = lot['quantity']
                        realized_pl += qty_sold * (sell_price - lot['price'])
                        sell_quantity -= qty_sold
                        product_lots[product_id].pop(0)
                    else:
                        # Partial lot sold
                        realized_pl += sell_quantity * (sell_price - lot['price'])
                        lot['quantity'] -= sell_quantity
                        sell_quantity = 0
        
        return realized_pl
    
    def get_transaction_summary(self) -> pd.DataFrame:
        """
        Get summary of all transactions
        
        Returns:
            DataFrame with transaction details
        """
        if not self.transactions:
            return pd.DataFrame()
        
        data = []
        for txn in self.transactions:
            product_name = txn.product.name if txn.product else "N/A"
            
            data.append({
                'Date': txn.transaction_date,
                'Type': txn.transaction_type.value.replace('_', ' ').title(),
                'Product': product_name,
                'Quantity': txn.quantity,
                'Price': txn.price,
                'Gross': txn.gross_amount,
                'Fees': txn.fees,
                'Taxes': txn.taxes,
                'Net': txn.net_amount,
                'Notes': txn.notes or ''
            })
        
        return pd.DataFrame(data)
    
    def get_holdings_detail(self) -> pd.DataFrame:
        """
        Get detailed holdings information
        Combines current holdings with product details and cost basis
        
        Returns:
            DataFrame with holdings details
        """
        holdings = self.get_current_holdings()
        
        if not holdings:
            return pd.DataFrame()
        
        data = []
        for product_id, quantity in holdings.items():
            product = self.session.query(InvestmentProduct).get(product_id)
            if not product:
                continue
            
            avg_price = self.get_average_entry_price(product_id)
            cost_basis = quantity * avg_price
            
            data.append({
                'Ticker': product.identifier,
                'Name': product.name,
                'Type': product.asset_class.value.replace('_', ' ').title() if product.asset_class else product.product_type,
                'Category': product.category,
                'Quantity': quantity,
                'Avg Entry Price': avg_price,
                'Cost Basis': cost_basis
            })
        
        return pd.DataFrame(data)
    
    def get_performance_summary(self) -> Dict:
        """
        Get overall portfolio performance summary
        
        Returns:
            Dict with key performance metrics
        """
        cost_basis = self.calculate_cost_basis()
        income = self.calculate_total_income()
        fees = self.calculate_total_fees()
        realized_gains = self.calculate_realized_gains()
        
        holdings = self.get_current_holdings()
        num_holdings = len(holdings)
        
        return {
            'cost_basis': cost_basis,
            'total_income': income['total'],
            'dividend_income': income['dividends'],
            'interest_income': income['interest'],
            'total_fees': fees['total'],
            'total_taxes': fees['taxes'],
            'realized_gains': realized_gains,
            'num_holdings': num_holdings,
            'num_transactions': len(self.transactions)
        }
    
    def get_income_by_product(self) -> pd.DataFrame:
        """
        Get income breakdown by product
        
        Returns:
            DataFrame with income per product
        """
        income_by_product = defaultdict(lambda: {
            'dividends': 0,
            'interest': 0,
            'coupons': 0,
            'total': 0
        })
        
        for txn in self.transactions:
            if not txn.product_id:
                continue
            
            amount = abs(txn.net_amount) if txn.net_amount else 0
            
            if txn.transaction_type == TransactionType.DIVIDEND:
                income_by_product[txn.product_id]['dividends'] += amount
                income_by_product[txn.product_id]['total'] += amount
            elif txn.transaction_type == TransactionType.INTEREST:
                income_by_product[txn.product_id]['interest'] += amount
                income_by_product[txn.product_id]['total'] += amount
            elif txn.transaction_type == TransactionType.COUPON:
                income_by_product[txn.product_id]['coupons'] += amount
                income_by_product[txn.product_id]['total'] += amount
        
        if not income_by_product:
            return pd.DataFrame()
        
        data = []
        for product_id, income in income_by_product.items():
            product = self.session.query(InvestmentProduct).get(product_id)
            if not product:
                continue
            
            data.append({
                'Product': product.name,
                'Ticker': product.identifier,
                'Dividends': income['dividends'],
                'Interest': income['interest'],
                'Coupons': income['coupons'],
                'Total Income': income['total']
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values('Total Income', ascending=False)
        
        return df