"""
Benchmark Analyzer - Compare portfolio performance to benchmarks
Calculate alpha, beta, tracking error, and information ratio
"""
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Optional, Dict, Tuple
import logging

from data.price_fetcher import PriceFetcher

logger = logging.getLogger(__name__)


class BenchmarkAnalyzer:
    """
    Analyze portfolio performance relative to benchmarks
    Calculate alpha, beta, correlation, tracking error
    """
    
    def __init__(self, portfolio_returns: pd.Series, benchmark_ticker: str):
        """
        Initialize benchmark analyzer
        
        Args:
            portfolio_returns: Series of portfolio returns (daily)
            benchmark_ticker: Ticker symbol for benchmark (e.g., '^GSPC', 'STX40.JO')
        """
        self.portfolio_returns = portfolio_returns.sort_index()
        self.benchmark_ticker = benchmark_ticker
        self.benchmark_returns = None
        self.aligned_data = None
    
    def fetch_benchmark_data(self, start_date: Optional[date] = None,
                            end_date: Optional[date] = None) -> bool:
        """
        Fetch benchmark price data
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            True if successful
        """
        try:
            fetcher = PriceFetcher()
            
            # Use portfolio date range if not specified
            if start_date is None:
                start_date = self.portfolio_returns.index[0].date()
            if end_date is None:
                end_date = self.portfolio_returns.index[-1].date()
            
            # Fetch benchmark prices
            hist = fetcher.fetch_historical_prices(
                self.benchmark_ticker,
                start_date=start_date,
                end_date=end_date
            )
            
            if hist.empty:
                logger.error(f"No benchmark data for {self.benchmark_ticker}")
                return False
            
            # Calculate returns
            prices = pd.Series(hist['close'].values, index=hist.index)
            self.benchmark_returns = prices.pct_change().dropna()
            
            # Align portfolio and benchmark returns
            self._align_data()
            
            logger.info(f"Fetched benchmark data: {len(self.benchmark_returns)} periods")
            return True
            
        except Exception as e:
            logger.error(f"Error fetching benchmark data: {e}")
            return False
    
    def _align_data(self):
        """Align portfolio and benchmark returns to common dates"""
        if self.benchmark_returns is None:
            return
        
        # Find common dates
        common_dates = self.portfolio_returns.index.intersection(
            self.benchmark_returns.index
        )
        
        if len(common_dates) == 0:
            logger.warning("No common dates between portfolio and benchmark")
            return
        
        self.aligned_data = pd.DataFrame({
            'portfolio': self.portfolio_returns.loc[common_dates],
            'benchmark': self.benchmark_returns.loc[common_dates]
        })
        
        logger.info(f"Aligned {len(common_dates)} periods")
    
    def calculate_beta(self) -> float:
        """
        Calculate portfolio beta relative to benchmark
        Beta = Cov(Portfolio, Benchmark) / Var(Benchmark)
        
        Returns:
            Beta coefficient
        """
        if self.aligned_data is None or len(self.aligned_data) < 2:
            return 0.0
        
        covariance = self.aligned_data['portfolio'].cov(self.aligned_data['benchmark'])
        benchmark_variance = self.aligned_data['benchmark'].var()
        
        if benchmark_variance == 0:
            return 0.0
        
        beta = covariance / benchmark_variance
        return beta
    
    def calculate_alpha(self, risk_free_rate: float = 0.07) -> float:
        """
        Calculate Jensen's Alpha
        Alpha = Portfolio Return - (Risk Free Rate + Beta × (Benchmark Return - Risk Free Rate))
        
        Args:
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Annualized alpha
        """
        if self.aligned_data is None or len(self.aligned_data) < 2:
            return 0.0
        
        # Calculate average returns (annualized)
        portfolio_return = self.aligned_data['portfolio'].mean() * 252
        benchmark_return = self.aligned_data['benchmark'].mean() * 252
        
        beta = self.calculate_beta()
        
        # Jensen's Alpha
        alpha = portfolio_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))
        
        return alpha
    
    def calculate_correlation(self) -> float:
        """
        Calculate correlation between portfolio and benchmark
        
        Returns:
            Correlation coefficient (-1 to 1)
        """
        if self.aligned_data is None or len(self.aligned_data) < 2:
            return 0.0
        
        correlation = self.aligned_data['portfolio'].corr(self.aligned_data['benchmark'])
        return correlation
    
    def calculate_tracking_error(self) -> float:
        """
        Calculate tracking error (annualized)
        Standard deviation of difference between portfolio and benchmark returns
        
        Returns:
            Annualized tracking error
        """
        if self.aligned_data is None or len(self.aligned_data) < 2:
            return 0.0
        
        excess_returns = self.aligned_data['portfolio'] - self.aligned_data['benchmark']
        tracking_error = excess_returns.std() * np.sqrt(252)
        
        return tracking_error
    
    def calculate_information_ratio(self) -> float:
        """
        Calculate Information Ratio
        IR = (Portfolio Return - Benchmark Return) / Tracking Error
        
        Returns:
            Information ratio
        """
        tracking_error = self.calculate_tracking_error()
        
        if tracking_error == 0:
            return 0.0
        
        # Calculate excess return (annualized)
        excess_return = (self.aligned_data['portfolio'].mean() - 
                        self.aligned_data['benchmark'].mean()) * 252
        
        information_ratio = excess_return / tracking_error
        return information_ratio
    
    def calculate_up_capture(self) -> float:
        """
        Calculate upside capture ratio
        Measures portfolio performance in periods when benchmark is up
        
        Returns:
            Upside capture ratio (> 100% is good)
        """
        if self.aligned_data is None or len(self.aligned_data) < 2:
            return 0.0
        
        up_periods = self.aligned_data[self.aligned_data['benchmark'] > 0]
        
        if len(up_periods) == 0:
            return 0.0
        
        portfolio_up = up_periods['portfolio'].mean()
        benchmark_up = up_periods['benchmark'].mean()
        
        if benchmark_up == 0:
            return 0.0
        
        up_capture = (portfolio_up / benchmark_up) * 100
        return up_capture
    
    def calculate_down_capture(self) -> float:
        """
        Calculate downside capture ratio
        Measures portfolio performance in periods when benchmark is down
        
        Returns:
            Downside capture ratio (< 100% is good)
        """
        if self.aligned_data is None or len(self.aligned_data) < 2:
            return 0.0
        
        down_periods = self.aligned_data[self.aligned_data['benchmark'] < 0]
        
        if len(down_periods) == 0:
            return 0.0
        
        portfolio_down = down_periods['portfolio'].mean()
        benchmark_down = down_periods['benchmark'].mean()
        
        if benchmark_down == 0:
            return 0.0
        
        down_capture = (portfolio_down / benchmark_down) * 100
        return down_capture
    
    def calculate_relative_performance(self) -> pd.Series:
        """
        Calculate cumulative relative performance over time
        
        Returns:
            Series of cumulative excess returns
        """
        if self.aligned_data is None:
            return pd.Series(dtype=float)
        
        excess_returns = self.aligned_data['portfolio'] - self.aligned_data['benchmark']
        cumulative_excess = (1 + excess_returns).cumprod() - 1
        
        return cumulative_excess
    
    def get_benchmark_comparison(self, risk_free_rate: float = 0.07) -> Dict:
        """
        Get comprehensive benchmark comparison metrics
        
        Args:
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Dict with all comparison metrics
        """
        if self.aligned_data is None or len(self.aligned_data) < 2:
            return {
                'error': 'Insufficient data for comparison',
                'periods': 0
            }
        
        # Calculate portfolio metrics
        portfolio_return = self.aligned_data['portfolio'].mean() * 252
        portfolio_vol = self.aligned_data['portfolio'].std() * np.sqrt(252)
        
        # Calculate benchmark metrics
        benchmark_return = self.aligned_data['benchmark'].mean() * 252
        benchmark_vol = self.aligned_data['benchmark'].std() * np.sqrt(252)
        
        # Relative metrics
        beta = self.calculate_beta()
        alpha = self.calculate_alpha(risk_free_rate)
        correlation = self.calculate_correlation()
        tracking_error = self.calculate_tracking_error()
        info_ratio = self.calculate_information_ratio()
        up_capture = self.calculate_up_capture()
        down_capture = self.calculate_down_capture()
        
        # Excess return
        excess_return = portfolio_return - benchmark_return
        
        return {
            'benchmark_ticker': self.benchmark_ticker,
            'periods': len(self.aligned_data),
            'start_date': self.aligned_data.index[0],
            'end_date': self.aligned_data.index[-1],
            
            # Returns
            'portfolio_return': portfolio_return,
            'portfolio_return_pct': portfolio_return * 100,
            'benchmark_return': benchmark_return,
            'benchmark_return_pct': benchmark_return * 100,
            'excess_return': excess_return,
            'excess_return_pct': excess_return * 100,
            
            # Volatility
            'portfolio_volatility': portfolio_vol,
            'portfolio_volatility_pct': portfolio_vol * 100,
            'benchmark_volatility': benchmark_vol,
            'benchmark_volatility_pct': benchmark_vol * 100,
            
            # Relative metrics
            'beta': beta,
            'alpha': alpha,
            'alpha_pct': alpha * 100,
            'correlation': correlation,
            'tracking_error': tracking_error,
            'tracking_error_pct': tracking_error * 100,
            'information_ratio': info_ratio,
            
            # Capture ratios
            'upside_capture': up_capture,
            'downside_capture': down_capture,
            'capture_ratio': up_capture / down_capture if down_capture != 0 else 0
        }
    
    def generate_comparison_report(self, risk_free_rate: float = 0.07) -> str:
        """
        Generate formatted benchmark comparison report
        
        Args:
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Formatted report string
        """
        comparison = self.get_benchmark_comparison(risk_free_rate)
        
        if 'error' in comparison:
            return f"Error: {comparison['error']}"
        
        report = f"""
BENCHMARK COMPARISON REPORT
{'=' * 70}

Benchmark: {comparison['benchmark_ticker']}
Period: {comparison['start_date'].strftime('%Y-%m-%d')} to {comparison['end_date'].strftime('%Y-%m-%d')}
Periods: {comparison['periods']}

RETURNS (ANNUALIZED)
{'=' * 70}
Portfolio Return:          {comparison['portfolio_return_pct']:>10.2f}%
Benchmark Return:          {comparison['benchmark_return_pct']:>10.2f}%
Excess Return (Alpha):     {comparison['excess_return_pct']:>10.2f}%

RISK METRICS
{'=' * 70}
Portfolio Volatility:      {comparison['portfolio_volatility_pct']:>10.2f}%
Benchmark Volatility:      {comparison['benchmark_volatility_pct']:>10.2f}%
Tracking Error:            {comparison['tracking_error_pct']:>10.2f}%

RELATIVE PERFORMANCE
{'=' * 70}
Beta:                      {comparison['beta']:>10.2f}
Alpha (Jensen's):          {comparison['alpha_pct']:>10.2f}%
Correlation:               {comparison['correlation']:>10.2f}
Information Ratio:         {comparison['information_ratio']:>10.2f}

CAPTURE RATIOS
{'=' * 70}
Upside Capture:            {comparison['upside_capture']:>10.2f}%
Downside Capture:          {comparison['downside_capture']:>10.2f}%
Capture Ratio:             {comparison['capture_ratio']:>10.2f}

{'=' * 70}

Interpretation:
- Beta > 1: Portfolio is more volatile than benchmark
- Alpha > 0: Portfolio outperformed risk-adjusted benchmark
- IR > 0.5: Good active management
- Upside Capture > 100%: Better gains in up markets
- Downside Capture < 100%: Better protection in down markets
"""
        return report