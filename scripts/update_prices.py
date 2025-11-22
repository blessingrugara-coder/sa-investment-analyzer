#!/usr/bin/env python
"""
Update market prices for all products
Can be run manually or scheduled
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from datetime import datetime
from data.price_fetcher import PriceFetcher
from database.session import get_session
from database.models import InvestmentProduct


def update_prices(period='1y', delay=1.0):
    """
    Update prices for all products
    
    Args:
        period: Historical period to fetch ('1d', '1mo', '1y', '5y', etc.)
        delay: Delay between requests (seconds)
    """
    print("\n" + "="*60)
    print("SA Investment Analyzer - Price Update")
    print("="*60)
    print(f"\nStarting price update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Period: {period}")
    print(f"Delay: {delay}s between requests")
    print()
    
    fetcher = PriceFetcher()
    
    # Get products to update
    session = get_session()
    products = session.query(InvestmentProduct).filter_by(has_api_data=True).all()
    session.close()
    
    if not products:
        print("⚠ No products with API data found")
        return
    
    print(f"Found {len(products)} products to update:\n")
    for p in products:
        print(f"  • {p.identifier:15s} - {p.name}")
    
    print("\n" + "-"*60)
    
    response = input("\nProceed with update? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Update cancelled")
        return
    
    print("\n" + "="*60)
    print("Updating prices...")
    print("="*60 + "\n")
    
    # Update all products
    stats = fetcher.update_all_products(delay_seconds=delay)
    
    print("\n" + "="*60)
    print("Update Complete")
    print("="*60)
    print(f"\nTotal products: {stats['total']}")
    print(f"✅ Successful:   {stats['success']}")
    print(f"❌ Failed:       {stats['failed']}")
    
    if stats['success'] > 0:
        print("\n✨ Price data updated successfully!")
        print("\nYou can now:")
        print("  • View real-time portfolio values")
        print("  • Calculate accurate performance metrics")
        print("  • Compare against benchmarks")
    
    print()


def update_single_product(identifier):
    """Update prices for a single product"""
    print(f"\nUpdating prices for: {identifier}")
    
    session = get_session()
    product = session.query(InvestmentProduct).filter_by(identifier=identifier).first()
    session.close()
    
    if not product:
        print(f"❌ Product {identifier} not found")
        return
    
    if not product.has_api_data:
        print(f"⚠ Product {identifier} does not have API data")
        return
    
    fetcher = PriceFetcher()
    success = fetcher.update_product_prices(product.id)
    
    if success:
        print(f"✅ Successfully updated {identifier}")
    else:
        print(f"❌ Failed to update {identifier}")


def check_data_availability(identifier):
    """Check if data is available for a ticker"""
    print(f"\nChecking data availability for: {identifier}")
    
    fetcher = PriceFetcher()
    info = fetcher.check_data_availability(identifier)
    
    print("\nResult:")
    for key, value in info.items():
        print(f"  {key}: {value}")


def main():
    parser = argparse.ArgumentParser(description='Update market prices')
    parser.add_argument('--product', type=str, help='Update single product by identifier')
    parser.add_argument('--check', type=str, help='Check data availability for ticker')
    parser.add_argument('--period', type=str, default='1y', 
                       help='Historical period (1d, 1mo, 1y, 5y, max)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between requests (seconds)')
    parser.add_argument('--auto', action='store_true',
                       help='Auto-confirm (for scheduled runs)')
    
    args = parser.parse_args()
    
    try:
        if args.check:
            check_data_availability(args.check)
        elif args.product:
            update_single_product(args.product)
        else:
            if args.auto:
                # Auto mode - skip confirmation
                fetcher = PriceFetcher()
                stats = fetcher.update_all_products(delay_seconds=args.delay)
                print(f"Updated: {stats['success']}/{stats['total']} products")
            else:
                update_prices(period=args.period, delay=args.delay)
    
    except KeyboardInterrupt:
        print("\n\nUpdate cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()