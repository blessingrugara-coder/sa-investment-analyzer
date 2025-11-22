"""
Performance Metrics Calculator
Calculate returns, risk metrics, and performance statistics
"""
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Calculate portfolio performance metrics
    Works with transaction ledger and market data
    """
    
    def __init__(self, portfolio_values: pd.Series, cash_flows: pd.Series = None):
        """
        Initialize performance calculator
        
        Args:
            portfolio_values: Series with dates as index, portfolio values as values
            cash_flows: Series with dates as index, cash flows as values (negative = investment)
        """
        self.portfolio_values = portfolio_values.sort_index()
        self.cash_flows = cash_flows.sort_index() if cash_flows is not None else pd.Series(dtype=float)
        
        if self.portfolio_values.empty:
            raise ValueError("Portfolio values cannot be empty")
    
    def calculate_simple_return(self) -> float:
        """
        Calculate simple total return
        
        Returns:
            Total return as decimal (e.g., 0.15 = 15%)
        """
        if len(self.portfolio_values) < 2:
            return 0.0
        
        start_value = self.portfolio_values.iloc[0]
        end_value = self.portfolio_values.iloc[-1]
        
        if start_value == 0:
            return 0.0
        
        return (end_value - start_value) / start_value
    
    def calculate_daily_returns(self) -> pd.Series:
        """
        Calculate daily returns
        
        Returns:
            Series of daily returns
        """
        return self.portfolio_values.pct_change().fillna(0)
    
    def calculate_cumulative_returns(self) -> pd.Series:
        """
        Calculate cumulative returns over time
        
        Returns:
            Series of cumulative returns
        """
        daily_returns = self.calculate_daily_returns()
        return (1 + daily_returns).cumprod() - 1
    
    def calculate_annualized_return(self) -> float:
        """
        Calculate annualized return
        
        Returns:
            Annualized return as decimal
        """
        if len(self.portfolio_values) < 2:
            return 0.0
        
        total_return = self.calculate_simple_return()
        
        # Calculate number of years
        start_date = self.portfolio_values.index[0]
        end_date = self.portfolio_values.index[-1]
        years = (end_date - start_date).days / 365.25
        
        if years == 0:
            return total_return
        
        # Annualize: (1 + total_return)^(1/years) - 1
        annualized = (1 + total_return) ** (1 / years) - 1
        return annualized
    
    def calculate_time_weighted_return(self) -> float:
        """
        Calculate Time-Weighted Return (TWR)
        Eliminates effect of cash flows - true portfolio performance
        
        Returns:
            TWR as decimal
        """
        if len(self.portfolio_values) < 2:
            return 0.0
        
        # If no cash flows, TWR = simple return
        if self.cash_flows.empty:
            return self.calculate_simple_return()
        
        # Split periods by cash flows
        cash_flow_dates = self.cash_flows[self.cash_flows != 0].index
        
        if len(cash_flow_dates) == 0:
            return self.calculate_simple_return()
        
        # Calculate sub-period returns
        period_returns = []
        
        all_dates = sorted(set(self.portfolio_values.index) | set(cash_flow_dates))
        
        for i in range(len(all_dates) - 1):
            start_date = all_dates[i]
            end_date = all_dates[i + 1]
            
            if start_date in self.portfolio_values.index and end_date in self.portfolio_values.index:
                start_val = self.portfolio_values.loc[start_date]
                end_val = self.portfolio_values.loc[end_date]
                
                # Adjust for cash flow at start of period
                if start_date in self.cash_flows.index:
                    start_val -= self.cash_flows.loc[start_date]
                
                if start_val != 0:
                    period_return = (end_val - start_val) / start_val
                    period_returns.append(1 + period_return)
        
        if not period_returns:
            return 0.0
        
        # Chain-link the returns
        twr = np.prod(period_returns) - 1
        return twr
    
    def calculate_money_weighted_return(self) -> float:
        """
        Calculate Money-Weighted Return (MWR) / Internal Rate of Return (IRR)
        Accounts for timing and size of cash flows
        
        Returns:
            IRR as decimal
        """
        if self.cash_flows.empty:
            return self.calculate_simple_return()
        
        # Prepare cash flows for IRR calculation
        all_dates = sorted(set(self.portfolio_values.index) | set(self.cash_flows.index))
        
        if len(all_dates) < 2:
            return 0.0
        
        # Build cash flow series
        cf_series = []
        date_series = []
        
        # Initial investment (negative)
        if self.cash_flows.index[0] in all_dates:
            cf_series.append(-abs(self.cash_flows.iloc[0]))
            date_series.append(self.cash_flows.index[0])
        
        # Intermediate cash flows
        for cf_date in self.cash_flows.index[1:]:
            cf_series.append(self.cash_flows.loc[cf_date])
            date_series.append(cf_date)
        
        # Final value (positive)
        final_date = self.portfolio_values.index[-1]
        final_value = self.portfolio_values.iloc[-1]
        cf_series.append(final_value)
        date_series.append(final_date)
        
        # Calculate IRR using numpy
        try:
            # Convert dates to days from start
            start_date = date_series[0]
            days = [(d - start_date).days for d in date_series]
            
            # Use numpy IRR approximation
            irr = np.irr(cf_series)
            
            # Annualize if needed
            if days[-1] > 0:
                periods_per_year = 365.25 / (days[-1] / len(days))
                annual_irr = (1 + irr) ** periods_per_year - 1
                return annual_irr
            
            return irr
        except:
            # Fallback to simple return
            return self.calculate_simple_return()
    
    def calculate_volatility(self, annualize: bool = True) -> float:
        """
        Calculate volatility (standard deviation of returns)
        
        Args:
            annualize: If True, annualize the volatility
            
        Returns:
            Volatility as decimal
        """
        daily_returns = self.calculate_daily_returns()
        
        if len(daily_returns) < 2:
            return 0.0
        
        vol = daily_returns.std()
        
        if annualize:
            # Annualize: multiply by sqrt(252) trading days
            vol = vol * np.sqrt(252)
        
        return vol
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.07) -> float:
        """
        Calculate Sharpe Ratio
        (Return - Risk Free Rate) / Volatility
        
        Args:
            risk_free_rate: Annual risk-free rate (default 7% for SA)
            
        Returns:
            Sharpe ratio
        """
        annual_return = self.calculate_annualized_return()
        volatility = self.calculate_volatility(annualize=True)
        
        if volatility == 0:
            return 0.0
        
        sharpe = (annual_return - risk_free_rate) / volatility
        return sharpe
    
    def calculate_sortino_ratio(self, risk_free_rate: float = 0.07, 
                                target_return: float = 0.0) -> float:
        """
        Calculate Sortino Ratio
        Like Sharpe, but only penalizes downside volatility
        
        Args:
            risk_free_rate: Annual risk-free rate
            target_return: Minimum acceptable return
            
        Returns:
            Sortino ratio
        """
        annual_return = self.calculate_annualized_return()
        
        # Calculate downside deviation
        daily_returns = self.calculate_daily_returns()
        downside_returns = daily_returns[daily_returns < target_return]
        
        if len(downside_returns) < 2:
            return 0.0
        
        downside_std = downside_returns.std() * np.sqrt(252)
        
        if downside_std == 0:
            return 0.0
        
        sortino = (annual_return - risk_free_rate) / downside_std
        return sortino
    
    def calculate_max_drawdown(self) -> Dict[str, float]:
        """
        Calculate maximum drawdown
        Largest peak-to-trough decline
        
        Returns:
            Dict with max_drawdown, peak_date, trough_date
        """
        cumulative = (1 + self.calculate_daily_returns()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = drawdown.min()
        
        if pd.isna(max_dd):
            return {
                'max_drawdown': 0.0,
                'max_drawdown_pct': 0.0,
                'peak_date': None,
                'trough_date': None
            }
        
        trough_date = drawdown.idxmin()
        peak_date = cumulative[:trough_date].idxmax()
        
        return {
            'max_drawdown': max_dd,
            'max_drawdown_pct': max_dd * 100,
            'peak_date': peak_date,
            'trough_date': trough_date
        }
    
    def calculate_value_at_risk(self, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)
        Maximum expected loss at given confidence level
        
        Args:
            confidence: Confidence level (0.95 = 95%)
            
        Returns:
            VaR as decimal (negative number)
        """
        daily_returns = self.calculate_daily_returns()
        
        if len(daily_returns) < 2:
            return 0.0
        
        var = daily_returns.quantile(1 - confidence)
        return var
    
    def calculate_conditional_var(self, confidence: float = 0.95) -> float:
        """
        Calculate Conditional VaR (CVaR) / Expected Shortfall
        Expected loss given that VaR threshold is breached
        
        Args:
            confidence: Confidence level (0.95 = 95%)
            
        Returns:
            CVaR as decimal (negative number)
        """
        daily_returns = self.calculate_daily_returns()
        
        if len(daily_returns) < 2:
            return 0.0
        
        var = self.calculate_value_at_risk(confidence)
        cvar = daily_returns[daily_returns <= var].mean()
        
        return cvar if not pd.isna(cvar) else 0.0
    
    def calculate_calmar_ratio(self) -> float:
        """
        Calculate Calmar Ratio
        Annualized Return / Maximum Drawdown
        
        Returns:
            Calmar ratio
        """
        annual_return = self.calculate_annualized_return()
        max_dd = abs(self.calculate_max_drawdown()['max_drawdown'])
        
        if max_dd == 0:
            return 0.0
        
        return annual_return / max_dd
    
    def calculate_rolling_returns(self, window: int = 30) -> pd.Series:
        """
        Calculate rolling returns
        
        Args:
            window: Window size in days
            
        Returns:
            Series of rolling returns
        """
        return self.portfolio_values.pct_change(periods=window)
    
    def calculate_rolling_volatility(self, window: int = 30) -> pd.Series:
        """
        Calculate rolling volatility
        
        Args:
            window: Window size in days
            
        Returns:
            Series of rolling volatility
        """
        daily_returns = self.calculate_daily_returns()
        rolling_vol = daily_returns.rolling(window=window).std() * np.sqrt(252)
        return rolling_vol
    
    def get_performance_summary(self, risk_free_rate: float = 0.07) -> Dict:
        """
        Get comprehensive performance summary
        
        Args:
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Dict with all performance metrics
        """
        max_dd = self.calculate_max_drawdown()
        
        return {
            'total_return': self.calculate_simple_return(),
            'total_return_pct': self.calculate_simple_return() * 100,
            'annualized_return': self.calculate_annualized_return(),
            'annualized_return_pct': self.calculate_annualized_return() * 100,
            'time_weighted_return': self.calculate_time_weighted_return(),
            'time_weighted_return_pct': self.calculate_time_weighted_return() * 100,
            'money_weighted_return': self.calculate_money_weighted_return(),
            'money_weighted_return_pct': self.calculate_money_weighted_return() * 100,
            'volatility': self.calculate_volatility(annualize=True),
            'volatility_pct': self.calculate_volatility(annualize=True) * 100,
            'sharpe_ratio': self.calculate_sharpe_ratio(risk_free_rate),
            'sortino_ratio': self.calculate_sortino_ratio(risk_free_rate),
            'max_drawdown': max_dd['max_drawdown'],
            'max_drawdown_pct': max_dd['max_drawdown_pct'],
            'calmar_ratio': self.calculate_calmar_ratio(),
            'var_95': self.calculate_value_at_risk(0.95),
            'cvar_95': self.calculate_conditional_var(0.95),
            'start_date': self.portfolio_values.index[0],
            'end_date': self.portfolio_values.index[-1],
            'num_periods': len(self.portfolio_values)
        }
    
    def generate_performance_report(self, risk_free_rate: float = 0.07) -> str:
        """
        Generate formatted performance report
        
        Args:
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Formatted report string
        """
        summary = self.get_performance_summary(risk_free_rate)
        
        report = f"""
PORTFOLIO PERFORMANCE REPORT
{'=' * 60}

Period: {summary['start_date'].strftime('%Y-%m-%d')} to {summary['end_date'].strftime('%Y-%m-%d')}
Number of Periods: {summary['num_periods']}

RETURNS
{'=' * 60}
Total Return:              {summary['total_return_pct']:>10.2f}%
Annualized Return:         {summary['annualized_return_pct']:>10.2f}%
Time-Weighted Return:      {summary['time_weighted_return_pct']:>10.2f}%
Money-Weighted Return:     {summary['money_weighted_return_pct']:>10.2f}%

RISK METRICS
{'=' * 60}
Volatility (Annualized):   {summary['volatility_pct']:>10.2f}%
Maximum Drawdown:          {summary['max_drawdown_pct']:>10.2f}%
Value at Risk (95%):       {summary['var_95']*100:>10.2f}%
Conditional VaR (95%):     {summary['cvar_95']*100:>10.2f}%

RISK-ADJUSTED RETURNS
{'=' * 60}
Sharpe Ratio:              {summary['sharpe_ratio']:>10.2f}
Sortino Ratio:             {summary['sortino_ratio']:>10.2f}
Calmar Ratio:              {summary['calmar_ratio']:>10.2f}

{'=' * 60}
"""