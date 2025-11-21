"""Add sample JSE products to database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.session import get_session
from database.models import InvestmentProduct
from datetime import datetime


def add_sample_products():
    session = get_session()
    
    # Sample JSE stocks and ETFs
    products = [
        {
            'product_type': 'equity',
            'identifier': 'NPN.JO',
            'name': 'Naspers Limited',
            'provider': 'JSE',
            'category': 'Technology/Media',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },
        {
            'product_type': 'equity',
            'identifier': 'FSR.JO',
            'name': 'FirstRand Limited',
            'provider': 'JSE',
            'category': 'Financials - Banks',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },
        {
            'product_type': 'equity',
            'identifier': 'SBK.JO',
            'name': 'Standard Bank Group Limited',
            'provider': 'JSE',
            'category': 'Financials - Banks',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },
        {
            'product_type': 'equity',
            'identifier': 'CPI.JO',
            'name': 'Capitec Bank Holdings Limited',
            'provider': 'JSE',
            'category': 'Financials - Banks',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },
        {
            'product_type': 'equity',
            'identifier': 'MTN.JO',
            'name': 'MTN Group Limited',
            'provider': 'JSE',
            'category': 'Telecommunications',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },
        {
            'product_type': 'equity',
            'identifier': 'SHP.JO',
            'name': 'Shoprite Holdings Limited',
            'provider': 'JSE',
            'category': 'Consumer - Retail',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },
        {
            'product_type': 'etf',
            'identifier': 'STX40.JO',
            'name': 'Satrix 40 ETF',
            'provider': 'Satrix',
            'category': 'ETF - SA Equity',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },
        {
            'product_type': 'etf',
            'identifier': 'STXWDM.JO',
            'name': 'Satrix MSCI World Equity ETF',
            'provider': 'Satrix',
            'category': 'ETF - Global Equity',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },
        {
            'product_type': 'index',
            'identifier': 'J203.L',
            'name': 'FTSE/JSE All Share Index',
            'provider': 'JSE',
            'category': 'Benchmark - SA',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },
        {
            'product_type': 'index',
            'identifier': 'J200.L',
            'name': 'FTSE/JSE Top 40 Index',
            'provider': 'JSE',
            'category': 'Benchmark - SA',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        }
    ]
    
    added_count = 0
    for product_data in products:
        # Check if already exists
        existing = session.query(InvestmentProduct).filter_by(
            identifier=product_data['identifier']
        ).first()
        
        if not existing:
            product = InvestmentProduct(**product_data)
            session.add(product)
            print(f"✓ Added: {product_data['name']}")
            added_count += 1
        else:
            print(f"⚠ Already exists: {product_data['name']}")
    
    session.commit()
    session.close()
    
    print(f"\n{'='*50}")
    print(f"✅ Added {added_count} new products to database")
    print(f"Total products in database: {added_count}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Adding Sample JSE Products")
    print("="*50 + "\n")
    
    try:
        add_sample_products()
        print("Sample data added successfully!")
        print("\nYou can now:")
        print("  1. Run: streamlit run app.py")
        print("  2. Go to 'Product Search'")
        print("  3. Search for 'naspers', 'bank', or 'etf'")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()