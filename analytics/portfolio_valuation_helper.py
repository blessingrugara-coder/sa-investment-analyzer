"""
Portfolio Valuation Helper
Generate portfolio value time series from transaction ledger
Used for performance calculations
"""
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, Optional
import logging

from analytics.ledger_calculator import LedgerCalculator

logger = logging.getLogger(__name__)


class PortfolioValuationHelper:
    """
    Generate portfolio value time series
    Combines transaction ledger with price data (when available)
    """
    
    def __init__(self, calculator: LedgerCalculator):
        """
        Initialize helper
        
        Args:
            calculator: LedgerCalculator instance
        """
        self.calculator = calculator
    
    def generate_value_series_from_market_prices(self,
                                                 start_date: Optional[date] = None,
                                                 end_date: Optional[date] = None) -> pd.Series:
        """
        Generate portfolio value series based on actual market prices
        
        Args:
            start_date: Start date (default: first transaction date)
            end_date: End date (default: today)
            
        Returns:
            Series with dates as index, portfolio values as values
        """
        from data.price_fetcher import PriceFetcher
        
        transactions = self.calculator.transactions
        
        if not transactions:
            return pd.Series(dtype=float)
        
        # Determine date range
        if start_date is None:
            start_date = transactions[0].transaction_date
        if end_date is None:
            end_date = date.today()
        
        # Generate daily date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Initialize price fetcher
        fetcher = PriceFetcher()
        
        # Calculate portfolio value for each date
        values = []
        for current_date in date_range:
            # Get holdings at this date
            holdings = self.calculator.get_holdings_at_date(current_date.date())
            
            # Calculate value using market prices
            total_value = 0
            for product_id, quantity in holdings.items():
                # Get market price for this date
                price = fetcher.get_price_at_date(product_id, current_date.date())
                
                if price is None:
                    # Fallback to average cost if no market price
                    price = self.calculator.get_average_entry_price(product_id)
                
                total_value += quantity * price
            
            values.append(total_value)
        
        series = pd.Series(values, index=date_range)
        return series
    
    def generate_value_series(self,
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None,
                             use_market_prices: bool = True) -> pd.Series:
        """
        Generate portfolio value series (smart method)
        Uses market prices if available, falls back to cost basis
        
        Args:
            start_date: Start date
            end_date: End date
            use_market_prices: Try to use market prices
            
        Returns:
            Series with portfolio values
        """
        if use_market_prices:
            try:
                return self.generate_value_series_from_market_prices(start_date, end_date)
            except Exception as e:
                logger.warning(f"Market prices unavailable, using cost basis: {e}")
        
        return self.generate_value_series_from_cost_basis(start_date, end_date)
                                              start_date: Optional[date] = None,
                                              end_date: Optional[date] = None) -> pd.Series:
        """
        Generate portfolio value series based on cost basis
        (Used when market prices are not available)
        
        Args:
            start_date: Start date (default: first transaction date)
            end_date: End date (default: today)
            
        Returns:
            Series with dates as index, portfolio values as values
        """
        transactions = self.calculator.transactions
        
        if not transactions:
            return pd.Series(dtype=float)
        
        # Determine date range
        if start_date is None:
            start_date = transactions[0].transaction_date
        if end_date is None:
            end_date = date.today()
        
        # Generate daily date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Calculate portfolio value for each date
        values = []
        for current_date in date_range:
            # Get holdings at this date
            holdings = self.calculator.get_holdings_at_date(current_date.date())
            
            # Calculate value (using average cost basis as proxy for market value)
            total_value = 0
            for product_id, quantity in holdings.items():
                avg_price = self.calculator.get_average_entry_price(product_id)
                total_value += quantity * avg_price
            
            values.append(total_value)
        
        series = pd.Series(values, index=date_range)
        return series
    
    def generate_cash_flow_series(self,
                                  start_date: Optional[date] = None,
                                  end_date: Optional[date] = None) -> pd.Series:
        """
        Generate cash flow series from transactions
        Negative values = cash out (investments)
        Positive values = cash in (withdrawals)
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Series with dates as index, cash flows as values
        """
        from database.models import TransactionType
        
        transactions = self.calculator.transactions
        
        if not transactions:
            return pd.Series(dtype=float)
        
        # Filter transactions
        if start_date:
            transactions = [t for t in transactions if t.transaction_date >= start_date]
        if end_date:
            transactions = [t for t in transactions if t.transaction_date <= end_date]
        
        # Build cash flow series
        cash_flows = {}
        
        for txn in transactions:
            txn_date = pd.Timestamp(txn.transaction_date)
            
            # Cash outflows (negative)
            if txn.transaction_type in [TransactionType.BUY, TransactionType.DEPOSIT]:
                if txn_date not in cash_flows:
                    cash_flows[txn_date] = 0
                cash_flows[txn_date] -= abs(txn.net_amount) if txn.net_amount else 0
            
            # Cash inflows (positive)
            elif txn.transaction_type in [TransactionType.SELL, TransactionType.WITHDRAWAL]:
                if txn_date not in cash_flows:
                    cash_flows[txn_date] = 0
                cash_flows[txn_date] += abs(txn.net_amount) if txn.net_amount else 0
        
        # Convert to series
        series = pd.Series(cash_flows).sort_index()
        return series
    
    def calculate_returns_from_cost_basis(self) -> pd.Series:
        """
        Calculate daily returns based on cost basis changes
        (Proxy for actual returns when prices unavailable)
        
        Returns:
            Series of daily returns
        """
        value_series = self.generate_value_series_from_cost_basis()
        returns = value_series.pct_change().fillna(0)
        return returns
    
    def generate_summary_statistics(self) -> Dict:
        """
        Generate summary statistics from cost basis
        
        Returns:
            Dict with summary stats
        """
        value_series = self.generate_value_series_from_cost_basis()
        cash_flows = self.generate_cash_flow_series()
        
        if value_series.empty:
            return {
                'start_value': 0,
                'end_value': 0,
                'total_invested': 0,
                'total_withdrawn': 0,
                'net_invested': 0,
                'absolute_gain': 0,
                'percent_gain': 0
            }
        
        start_value = value_series.iloc[0]
        end_value = value_series.iloc[-1]
        
        total_invested = sum(abs(cf) for cf in cash_flows if cf < 0)
        total_withdrawn = sum(cf for cf in cash_flows if cf > 0)
        net_invested = total_invested - total_withdrawn
        
        absolute_gain = end_value - net_invested
        percent_gain = (absolute_gain / net_invested * 100) if net_invested > 0 else 0
        
        return {
            'start_value': start_value,
            'end_value': end_value,
            'total_invested': total_invested,
            'total_withdrawn': total_withdrawn,
            'net_invested': net_invested,
            'absolute_gain': absolute_gain,
            'percent_gain': percent_gain,
            'start_date': value_series.index[0].date(),
            'end_date': value_series.index[-1].date()
        }
    
    def generate_monthly_returns(self) -> pd.DataFrame:
        """
        Generate monthly return summary
        
        Returns:
            DataFrame with monthly returns
        """
        value_series = self.generate_value_series_from_cost_basis()
        
        if value_series.empty:
            return pd.DataFrame()
        
        # Resample to month-end
        monthly = value_series.resample('M').last()
        monthly_returns = monthly.pct_change().fillna(0)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Month': monthly.index.strftime('%Y-%m'),
            'Value': monthly.values,
            'Return': monthly_returns.values,
            'Return %': monthly_returns.values * 100
        })
        
        return df
    
    def generate_yearly_returns(self) -> pd.DataFrame:
        """
        Generate yearly return summary
        
        Returns:
            DataFrame with yearly returns
        """
        value_series = self.generate_value_series_from_cost_basis()
        
        if value_series.empty:
            return pd.DataFrame()
        
        # Resample to year-end
        yearly = value_series.resample('Y').last()
        yearly_returns = yearly.pct_change().fillna(0)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Year': yearly.index.year,
            'Value': yearly.values,
            'Return': yearly_returns.values,
            'Return %': yearly_returns.values * 100
        })
        
        return df
    
    def get_performance_data_for_calculator(self) -> tuple:
        """
        Get data in format needed for PerformanceMetrics calculator
        
        Returns:
            Tuple of (portfolio_values, cash_flows) as Series
        """
        portfolio_values = self.generate_value_series_from_cost_basis()
        cash_flows = self.generate_cash_flow_series()
        
        return portfolio_values, cash_flows