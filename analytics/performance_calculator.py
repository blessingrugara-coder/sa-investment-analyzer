"""
Performance analytics calculator
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PerformanceCalculator:
    """Calculate portfolio performance metrics"""
    
    def __init__(self, holdings_df):
        """
        Initialize with portfolio holdings
        
        Args:
            holdings_df: DataFrame with columns: Ticker, Quantity, Entry Price, Entry Date
        """
        self.holdings_df = holdings_df
    
    def calculate_total_cost(self):
        """Calculate total cost basis"""
        if 'Cost Basis' in self.holdings_df.columns:
            return self.holdings_df['Cost Basis'].sum()
        return (self.holdings_df['Quantity'] * self.holdings_df['Entry Price']).sum()
    
    def calculate_allocation(self):
        """
        Calculate asset allocation
        
        Returns:
            DataFrame with allocation percentages
        """
        total = self.calculate_total_cost()
        
        allocation = self.holdings_df.copy()
        if 'Cost Basis' not in allocation.columns:
            allocation['Cost Basis'] = allocation['Quantity'] * allocation['Entry Price']
        
        allocation['Allocation %'] = (allocation['Cost Basis'] / total * 100).round(2)
        
        return allocation[['Ticker', 'Name', 'Cost Basis', 'Allocation %']].sort_values(
            'Allocation %', ascending=False
        )
    
    def calculate_type_allocation(self):
        """Calculate allocation by product type"""
        if 'Type' not in self.holdings_df.columns:
            return None
        
        total = self.calculate_total_cost()
        
        if 'Cost Basis' not in self.holdings_df.columns:
            self.holdings_df['Cost Basis'] = self.holdings_df['Quantity'] * self.holdings_df['Entry Price']
        
        by_type = self.holdings_df.groupby('Type')['Cost Basis'].sum()
        allocation = (by_type / total * 100).round(2)
        
        return allocation.to_frame(name='Allocation %')
    
    def calculate_category_allocation(self):
        """Calculate allocation by category"""
        if 'Category' not in self.holdings_df.columns:
            return None
        
        total = self.calculate_total_cost()
        
        if 'Cost Basis' not in self.holdings_df.columns:
            self.holdings_df['Cost Basis'] = self.holdings_df['Quantity'] * self.holdings_df['Entry Price']
        
        by_category = self.holdings_df.groupby('Category')['Cost Basis'].sum()
        allocation = (by_category / total * 100).round(2)
        
        return allocation.to_frame(name='Allocation %')
    
    def get_summary_stats(self):
        """
        Get summary statistics
        
        Returns:
            Dict with key metrics
        """
        total_cost = self.calculate_total_cost()
        num_holdings = len(self.holdings_df)
        
        # Calculate concentration
        allocation = self.calculate_allocation()
        top_holding_pct = allocation['Allocation %'].max()
        top_3_pct = allocation.head(3)['Allocation %'].sum()
        
        return {
            'Total Value': f"R {total_cost:,.2f}",
            'Number of Holdings': num_holdings,
            'Largest Position': f"{top_holding_pct:.1f}%",
            'Top 3 Concentration': f"{top_3_pct:.1f}%",
            'Average Position Size': f"{100/num_holdings:.1f}%"
        }
    
    def calculate_diversification_score(self):
        """
        Calculate simple diversification score (0-100)
        Higher = more diversified
        """
        num_holdings = len(self.holdings_df)
        allocation = self.calculate_allocation()
        
        # Penalize concentration
        max_allocation = allocation['Allocation %'].max()
        
        # Reward number of holdings (up to 20)
        holdings_score = min(num_holdings / 20 * 50, 50)
        
        # Reward low concentration
        concentration_score = max(0, 50 - max_allocation)
        
        total_score = holdings_score + concentration_score
        
        return min(100, total_score)