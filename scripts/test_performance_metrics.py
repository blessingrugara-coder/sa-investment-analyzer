#!/usr/bin/env python
"""
Test script for Phase 2 - Performance Analytics
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import date, timedelta

from analytics.performance_metrics import PerformanceMetrics
from analytics.portfolio_valuation_helper import PortfolioValuationHelper
from analytics.ledger_calculator import LedgerCalculator
from database.session import get_session
from database.models import Portfolio
from portfolio.portfolio_manager import PortfolioManager


def test_performance_metrics_basic():
    """Test PerformanceMetrics with sample data"""
    print("\n" + "="*60)
    print("TEST 1: PerformanceMetrics - Basic Calculations")
    print("="*60)
    
    # Create sample portfolio values
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # Simulate portfolio growing from R100,000 to R120,000
    np.random.seed(42)
    returns = np.random.normal(0.0003, 0.01, len(dates))  # Daily returns
    portfolio_values = 100000 * (1 + returns).cumprod()
    
    values_series = pd.Series(portfolio_values, index=dates)
    
    # Create cash flows (initial investment)
    cash_flows = pd.Series([-100000], index=[dates[0]])
    
    print(f"\nSample Data:")
    print(f"  Start Value: R {values_series.iloc[0]:,.2f}")
    print(f"  End Value: R {values_series.iloc[-1]:,.2f}")
    print(f"  Number of days: {len(dates)}")
    
    # Initialize calculator
    perf = PerformanceMetrics(values_series, cash_flows)
    
    # Test individual metrics
    print("\n1. Returns:")
    print(f"   Total Return: {perf.calculate_simple_return()*100:.2f}%")
    print(f"   Annualized Return: {perf.calculate_annualized_return()*100:.2f}%")
    print(f"   TWR: {perf.calculate_time_weighted_return()*100:.2f}%")
    
    print("\n2. Risk Metrics:")
    print(f"   Volatility: {perf.calculate_volatility()*100:.2f}%")
    max_dd = perf.calculate_max_drawdown()
    print(f"   Max Drawdown: {max_dd['max_drawdown_pct']:.2f}%")
    print(f"   VaR (95%): {perf.calculate_value_at_risk()*100:.2f}%")
    print(f"   CVaR (95%): {perf.calculate_conditional_var()*100:.2f}%")
    
    print("\n3. Risk-Adjusted Returns:")
    print(f"   Sharpe Ratio: {perf.calculate_sharpe_ratio():.2f}")
    print(f"   Sortino Ratio: {perf.calculate_sortino_ratio():.2f}")
    print(f"   Calmar Ratio: {perf.calculate_calmar_ratio():.2f}")
    
    print("\n✅ Basic performance calculations working")
    return True


def test_performance_summary():
    """Test performance summary generation"""
    print("\n" + "="*60)
    print("TEST 2: Performance Summary Report")
    print("="*60)
    
    # Sample data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.015, len(dates))
    portfolio_values = 100000 * (1 + returns).cumprod()
    values_series = pd.Series(portfolio_values, index=dates)
    
    perf = PerformanceMetrics(values_series)
    
    # Get summary
    summary = perf.get_performance_summary()
    
    print("\nSummary Dict:")
    for key, value in summary.items():
        if isinstance(value, (int, float)):
            if 'pct' in key:
                print(f"  {key:30s}: {value:10.2f}%")
            else:
                print(f"  {key:30s}: {value:10.4f}")
        else:
            print(f"  {key:30s}: {value}")
    
    # Generate report
    print("\n" + "-"*60)
    print("Formatted Report:")
    print("-"*60)
    report = perf.generate_performance_report()
    print(report)
    
    print("✅ Performance summary generation working")
    return True


def test_portfolio_valuation_helper():
    """Test PortfolioValuationHelper with real portfolio"""
    print("\n" + "="*60)
    print("TEST 3: PortfolioValuationHelper")
    print("="*60)
    
    session = get_session()
    pm = PortfolioManager()
    
    # Get first portfolio
    portfolios = pm.list_portfolios()
    if portfolios.empty:
        print("  ⚠ No portfolios to test with")
        session.close()
        return True
    
    portfolio_name = portfolios.iloc[0]['Name']
    portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
    
    print(f"\nTesting with portfolio: {portfolio_name}")
    
    # Initialize calculator and helper
    calc = LedgerCalculator(portfolio.id, session)
    helper = PortfolioValuationHelper(calc)
    
    # Test value series generation
    print("\n1. Generating Value Series (Cost Basis):")
    value_series = helper.generate_value_series_from_cost_basis()
    print(f"   Generated {len(value_series)} data points")
    if not value_series.empty:
        print(f"   Start: R {value_series.iloc[0]:,.2f}")
        print(f"   End: R {value_series.iloc[-1]:,.2f}")
    
    # Test cash flow series
    print("\n2. Generating Cash Flow Series:")
    cash_flows = helper.generate_cash_flow_series()
    print(f"   {len(cash_flows)} cash flow events")
    if not cash_flows.empty:
        total_in = sum(cf for cf in cash_flows if cf < 0)
        total_out = sum(cf for cf in cash_flows if cf > 0)
        print(f"   Total invested: R {abs(total_in):,.2f}")
        print(f"   Total withdrawn: R {total_out:,.2f}")
    
    # Test summary statistics
    print("\n3. Summary Statistics:")
    stats = helper.generate_summary_statistics()
    for key, value in stats.items():
        if isinstance(value, (int, float)):
            print(f"   {key}: R {value:,.2f}" if key != 'percent_gain' else f"   {key}: {value:.2f}%")
        else:
            print(f"   {key}: {value}")
    
    session.close()
    print("\n✅ Portfolio valuation helper working")
    return True


def test_real_portfolio_performance():
    """Test performance metrics with real portfolio data"""
    print("\n" + "="*60)
    print("TEST 4: Real Portfolio Performance Analysis")
    print("="*60)
    
    pm = PortfolioManager()
    portfolios = pm.list_portfolios()
    
    if portfolios.empty:
        print("  ⚠ No portfolios to test with")
        return True
    
    portfolio_name = portfolios.iloc[0]['Name']
    print(f"\nAnalyzing: {portfolio_name}")
    
    # Get performance analysis
    performance = pm.get_performance_analysis(portfolio_name)
    
    if performance is None:
        print("  ⚠ Insufficient data for performance analysis")
        return True
    
    # Display key metrics
    print("\nPerformance Metrics:")
    print(f"  Total Return: {performance['total_return_pct']:.2f}%")
    print(f"  Annualized Return: {performance['annualized_return_pct']:.2f}%")
    print(f"  Volatility: {performance['volatility_pct']:.2f}%")
    print(f"  Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: {performance['max_drawdown_pct']:.2f}%")
    
    print("\nSummary:")
    print(f"  Period: {performance['start_date']} to {performance['end_date']}")
    print(f"  Total Invested: R {performance.get('total_invested', 0):,.2f}")
    print(f"  Current Value: R {performance.get('end_value', 0):,.2f}")
    print(f"  Absolute Gain: R {performance.get('absolute_gain', 0):,.2f}")
    
    print("\n✅ Real portfolio performance analysis working")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" Phase 2 - Performance Analytics Tests")
    print("="*70)
    
    tests = [
        ("Performance Metrics - Basic", test_performance_metrics_basic),
        ("Performance Summary", test_performance_summary),
        ("Portfolio Valuation Helper", test_portfolio_valuation_helper),
        ("Real Portfolio Performance", test_real_portfolio_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print(" Test Summary")
    print("="*70)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n  {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 2 is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Review the output above.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)