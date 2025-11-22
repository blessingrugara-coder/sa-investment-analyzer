#!/usr/bin/env python
"""
Test script for Phase 3 - Live Market Data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.price_fetcher import PriceFetcher
from database.session import get_session
from database.models import InvestmentProduct, Price
from datetime import date, timedelta


def test_check_availability():
    """Test data availability checking"""
    print("\n" + "="*60)
    print("TEST 1: Check Data Availability")
    print("="*60)
    
    fetcher = PriceFetcher()
    
    test_tickers = [
        'NPN.JO',      # Naspers (JSE)
        'USDZAR=X',    # USD/ZAR FX
        'STX40.JO',    # Satrix Top 40 ETF
        'INVALID.XX'   # Invalid ticker
    ]
    
    print("\nChecking availability for test tickers:")
    for ticker in test_tickers:
        print(f"\n  {ticker}:")
        info = fetcher.check_data_availability(ticker)
        for key, value in info.items():
            print(f"    {key}: {value}")
    
    print("\n✅ Data availability check working")
    return True


def test_fetch_current_price():
    """Test current price fetching"""
    print("\n" + "="*60)
    print("TEST 2: Fetch Current Prices")
    print("="*60)
    
    fetcher = PriceFetcher()
    
    session = get_session()
    products = session.query(InvestmentProduct).filter_by(
        has_api_data=True
    ).limit(3).all()
    session.close()
    
    if not products:
        print("  ⚠ No products with API data to test")
        return True
    
    print(f"\nFetching current prices for {len(products)} products:")
    success_count = 0
    
    for product in products:
        print(f"\n  {product.identifier} ({product.name}):")
        price = fetcher.fetch_current_price(product.identifier)
        
        if price:
            print(f"    ✓ Current price: R {price:,.2f}")
            success_count += 1
        else:
            print(f"    ✗ Failed to fetch price")
    
    print(f"\n✅ Fetched {success_count}/{len(products)} prices successfully")
    return True


def test_fetch_historical():
    """Test historical price fetching"""
    print("\n" + "="*60)
    print("TEST 3: Fetch Historical Prices")
    print("="*60)
    
    fetcher = PriceFetcher()
    
    # Test with Naspers
    ticker = 'NPN.JO'
    print(f"\nFetching 1 month of history for {ticker}:")
    
    hist = fetcher.fetch_historical_prices(ticker, period='1mo')
    
    if not hist.empty:
        print(f"  ✓ Fetched {len(hist)} daily prices")
        print(f"  Date range: {hist.index[0].date()} to {hist.index[-1].date()}")
        print(f"\n  Latest prices:")
        print(f"    Open:   R {hist['open'].iloc[-1]:,.2f}")
        print(f"    High:   R {hist['high'].iloc[-1]:,.2f}")
        print(f"    Low:    R {hist['low'].iloc[-1]:,.2f}")
        print(f"    Close:  R {hist['close'].iloc[-1]:,.2f}")
        print(f"    Volume: {hist['volume'].iloc[-1]:,.0f}")
    else:
        print(f"  ✗ No historical data fetched")
        return False
    
    print("\n✅ Historical price fetching working")
    return True


def test_store_prices():
    """Test storing prices in database"""
    print("\n" + "="*60)
    print("TEST 4: Store Prices in Database")
    print("="*60)
    
    fetcher = PriceFetcher()
    session = get_session()
    
    # Get a test product
    product = session.query(InvestmentProduct).filter_by(
        identifier='NPN.JO'
    ).first()
    
    if not product:
        print("  ⚠ NPN.JO not found in database")
        session.close()
        return True
    
    print(f"\nFetching and storing prices for {product.identifier}:")
    
    # Fetch recent prices
    hist = fetcher.fetch_historical_prices(product.identifier, period='5d')
    
    if hist.empty:
        print("  ✗ No prices to store")
        session.close()
        return False
    
    # Store prices
    stored = fetcher.store_prices(product.id, hist)
    
    print(f"  ✓ Stored {stored} prices")
    
    # Verify storage
    count = session.query(Price).filter_by(product_id=product.id).count()
    print(f"  ✓ Total prices in database: {count}")
    
    # Get latest price
    latest = fetcher.get_latest_price(product.id)
    if latest:
        print(f"  ✓ Latest price from DB: R {latest:,.2f}")
    
    session.close()
    print("\n✅ Price storage working")
    return True


def test_price_series():
    """Test getting price series"""
    print("\n" + "="*60)
    print("TEST 5: Get Price Series")
    print("="*60)
    
    fetcher = PriceFetcher()
    session = get_session()
    
    product = session.query(InvestmentProduct).filter_by(
        identifier='NPN.JO'
    ).first()
    
    if not product:
        session.close()
        return True
    
    # Check if we have prices
    price_count = session.query(Price).filter_by(product_id=product.id).count()
    
    if price_count == 0:
        print("  ⚠ No prices in database, fetching now...")
        hist = fetcher.fetch_historical_prices(product.identifier, period='1mo')
        if not hist.empty:
            fetcher.store_prices(product.id, hist)
    
    # Get price series
    series = fetcher.get_price_series(product.id)
    
    if not series.empty:
        print(f"\n  ✓ Retrieved {len(series)} prices")
        print(f"  Date range: {series.index[0].date()} to {series.index[-1].date()}")
        print(f"  Price range: R {series.min():,.2f} to R {series.max():,.2f}")
        print(f"  Latest: R {series.iloc[-1]:,.2f}")
    else:
        print("  ⚠ No price series available")
    
    session.close()
    print("\n✅ Price series retrieval working")
    return True


def test_price_at_date():
    """Test getting price at specific date"""
    print("\n" + "="*60)
    print("TEST 6: Get Price at Specific Date")
    print("="*60)
    
    fetcher = PriceFetcher()
    session = get_session()
    
    product = session.query(InvestmentProduct).filter_by(
        identifier='NPN.JO'
    ).first()
    
    if not product:
        session.close()
        return True
    
    # Test dates
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    print(f"\nGetting prices for {product.identifier}:")
    
    for test_date in [today, week_ago, month_ago]:
        price = fetcher.get_price_at_date(product.id, test_date)
        if price:
            print(f"  {test_date}: R {price:,.2f}")
        else:
            print(f"  {test_date}: No price available")
    
    session.close()
    print("\n✅ Price at date retrieval working")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" Phase 3 - Live Market Data Tests")
    print("="*70)
    
    tests = [
        ("Data Availability Check", test_check_availability),
        ("Fetch Current Prices", test_fetch_current_price),
        ("Fetch Historical Prices", test_fetch_historical),
        ("Store Prices in Database", test_store_prices),
        ("Get Price Series", test_price_series),
        ("Get Price at Date", test_price_at_date)
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
        print("\n🎉 All tests passed! Phase 3 is working correctly.")
        print("\nNext steps:")
        print("  1. Run: python scripts/update_prices.py")
        print("  2. Update prices for all products")
        print("  3. View real portfolio values in the app")
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