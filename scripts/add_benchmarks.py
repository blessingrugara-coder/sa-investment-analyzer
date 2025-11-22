#!/usr/bin/env python
"""
Add benchmark indices to database
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.session import get_session
from database.models import BenchmarkIndex
from datetime import datetime


def add_benchmarks():
    """Add common benchmark indices"""
    session = get_session()
    
    benchmarks = [
        # Global
        {
            'ticker': '^GSPC',
            'name': 'S&P 500',
            'description': 'US large-cap equity benchmark',
            'currency': 'USD',
            'data_source': 'yfinance'
        },
        {
            'ticker': '^DJI',
            'name': 'Dow Jones Industrial Average',
            'description': 'US blue-chip equity benchmark',
            'currency': 'USD',
            'data_source': 'yfinance'
        },
        {
            'ticker': '^IXIC',
            'name': 'NASDAQ Composite',
            'description': 'US technology-heavy benchmark',
            'currency': 'USD',
            'data_source': 'yfinance'
        },
        
        # JSE - Use ETFs as proxies since indices don't work
        {
            'ticker': 'STX40.JO',
            'name': 'Satrix Top 40 (ALSI Proxy)',
            'description': 'JSE Top 40 proxy via Satrix ETF',
            'currency': 'ZAR',
            'data_source': 'yfinance'
        },
        {
            'ticker': 'STXSWX.JO',
            'name': 'Satrix Swix (SWIX Proxy)',
            'description': 'FTSE/JSE Capped SWIX proxy',
            'currency': 'ZAR',
            'data_source': 'yfinance'
        },
        {
            'ticker': 'STXIND.JO',
            'name': 'Satrix INDI (Industrial Proxy)',
            'description': 'JSE Industrial sector proxy',
            'currency': 'ZAR',
            'data_source': 'yfinance'
        },
        
        # Emerging Markets
        {
            'ticker': 'EEM',
            'name': 'iShares MSCI Emerging Markets',
            'description': 'Emerging markets equity benchmark',
            'currency': 'USD',
            'data_source': 'yfinance'
        },
        
        # Bonds
        {
            'ticker': 'AGG',
            'name': 'iShares Core US Aggregate Bond',
            'description': 'US investment-grade bond benchmark',
            'currency': 'USD',
            'data_source': 'yfinance'
        }
    ]
    
    added_count = 0
    for benchmark_data in benchmarks:
        existing = session.query(BenchmarkIndex).filter_by(
            ticker=benchmark_data['ticker']
        ).first()
        
        if not existing:
            benchmark = BenchmarkIndex(**benchmark_data)
            session.add(benchmark)
            print(f"✓ Added: {benchmark_data['name']} ({benchmark_data['ticker']})")
            added_count += 1
        else:
            print(f"⚠ Already exists: {benchmark_data['name']}")
    
    session.commit()
    session.close()
    
    print(f"\n{'='*60}")
    print(f"✅ Added {added_count} new benchmarks")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Adding Benchmark Indices")
    print("="*60 + "\n")
    
    try:
        add_benchmarks()
        print("Benchmarks added successfully!")
        print("\nYou can now:")
        print("  1. Compare portfolio to S&P 500")
        print("  2. Compare portfolio to JSE Top 40")
        print("  3. View alpha, beta, and tracking error")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()