"""Add sample products to database - including new asset classes"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.session import get_session
from database.models import InvestmentProduct, AssetClass
from datetime import datetime


def add_sample_products():
    session = get_session()

    # Comprehensive sample products across all asset classes
    products = [
        # === EQUITIES ===
        {
            'asset_class': AssetClass.EQUITY,
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
            'asset_class': AssetClass.EQUITY,
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
            'asset_class': AssetClass.EQUITY,
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
            'asset_class': AssetClass.EQUITY,
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
            'asset_class': AssetClass.EQUITY,
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
            'asset_class': AssetClass.EQUITY,
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

        # === ETFs ===
        {
            'asset_class': AssetClass.ETF,
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
            'asset_class': AssetClass.ETF,
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

        # === INDICES ===
        {
            'asset_class': AssetClass.INDEX,
            'product_type': 'index',
            'identifier': 'J203.JO',
            'name': 'FTSE/JSE All Share Index',
            'provider': 'JSE',
            'category': 'Benchmark - SA',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },
        {
            'asset_class': AssetClass.INDEX,
            'product_type': 'index',
            'identifier': 'J200.JO',
            'name': 'FTSE/JSE Top 40 Index',
            'provider': 'JSE',
            'category': 'Benchmark - SA',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date()
        },

        # === FX (NEW!) ===
        {
            'asset_class': AssetClass.FX,
            'product_type': 'fx',
            'identifier': 'USDZAR=X',
            'name': 'USD/ZAR',
            'provider': 'Forex',
            'category': 'Currency Pair',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date(),
            'details': {'base_currency': 'USD', 'quote_currency': 'ZAR'}
        },
        {
            'asset_class': AssetClass.FX,
            'product_type': 'fx',
            'identifier': 'EURZAR=X',
            'name': 'EUR/ZAR',
            'provider': 'Forex',
            'category': 'Currency Pair',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date(),
            'details': {'base_currency': 'EUR', 'quote_currency': 'ZAR'}
        },
        {
            'asset_class': AssetClass.FX,
            'product_type': 'fx',
            'identifier': 'GBPZAR=X',
            'name': 'GBP/ZAR',
            'provider': 'Forex',
            'category': 'Currency Pair',
            'currency': 'ZAR',
            'has_api_data': True,
            'primary_data_source': 'yfinance',
            'last_updated': datetime.now().date(),
            'details': {'base_currency': 'GBP', 'quote_currency': 'ZAR'}
        },

        # === MONEY MARKET (NEW!) ===
        {
            'asset_class': AssetClass.MONEY_MARKET,
            'product_type': 'money_market',
            'identifier': 'AGMMF',
            'name': 'Allan Gray Money Market Fund',
            'provider': 'Allan Gray',
            'category': 'Money Market Fund',
            'currency': 'ZAR',
            'has_api_data': False,
            'requires_scraping': True,
            'primary_data_source': 'manual',
            'last_updated': datetime.now().date(),
            'details': {'fund_type': 'money_market', 'ter': 0.15}
        },
        {
            'asset_class': AssetClass.MONEY_MARKET,
            'product_type': 'money_market',
            'identifier': 'INVMMF',
            'name': 'Investec Money Market Fund',
            'provider': 'Investec',
            'category': 'Money Market Fund',
            'currency': 'ZAR',
            'has_api_data': False,
            'requires_scraping': True,
            'primary_data_source': 'manual',
            'last_updated': datetime.now().date(),
            'details': {'fund_type': 'money_market', 'ter': 0.20}
        },

        # === BANK ACCOUNTS (NEW!) ===
        {
            'asset_class': AssetClass.BANK_ACCOUNT,
            'product_type': 'bank_account',
            'identifier': 'FNB-SAVINGS',
            'name': 'FNB Savings Account',
            'provider': 'FNB',
            'category': 'Savings Account',
            'currency': 'ZAR',
            'has_api_data': False,
            'manual_entry': True,
            'primary_data_source': 'manual',
            'last_updated': datetime.now().date(),
            'details': {'account_type': 'savings', 'interest_rate': 3.5}
        },
        {
            'asset_class': AssetClass.BANK_ACCOUNT,
            'product_type': 'bank_account',
            'identifier': 'ABSA-FIXED-12M',
            'name': 'ABSA 12-Month Fixed Deposit',
            'provider': 'ABSA',
            'category': 'Fixed Deposit',
            'currency': 'ZAR',
            'has_api_data': False,
            'manual_entry': True,
            'primary_data_source': 'manual',
            'last_updated': datetime.now().date(),
            'details': {'account_type': 'fixed_deposit', 'interest_rate': 7.5, 'term_months': 12}
        },
        {
            'asset_class': AssetClass.BANK_ACCOUNT,
            'product_type': 'bank_account',
            'identifier': 'CAPITEC-GLOBAL-ONE',
            'name': 'Capitec Global One Account',
            'provider': 'Capitec',
            'category': 'Savings Account',
            'currency': 'ZAR',
            'has_api_data': False,
            'manual_entry': True,
            'primary_data_source': 'manual',
            'last_updated': datetime.now().date(),
            'details': {'account_type': 'savings', 'interest_rate': 5.5}
        },

        # === UNIT TRUSTS ===
        {
            'asset_class': AssetClass.UNIT_TRUST,
            'product_type': 'unit_trust',
            'identifier': 'AGBAL',
            'name': 'Allan Gray Balanced Fund',
            'provider': 'Allan Gray',
            'category': 'Multi-Asset - Balanced',
            'currency': 'ZAR',
            'has_api_data': False,
            'requires_scraping': True,
            'primary_data_source': 'manual',
            'last_updated': datetime.now().date(),
            'details': {'fund_type': 'balanced', 'ter': 1.15}
        },
        {
            'asset_class': AssetClass.UNIT_TRUST,
            'product_type': 'unit_trust',
            'identifier': 'COREQ',
            'name': 'Coronation Equity Fund',
            'provider': 'Coronation',
            'category': 'Equity - General',
            'currency': 'ZAR',
            'has_api_data': False,
            'requires_scraping': True,
            'primary_data_source': 'manual',
            'last_updated': datetime.now().date(),
            'details': {'fund_type': 'equity', 'ter': 1.45}
        },
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
            print(f"✓ Added: {product_data['name']} ({product_data['asset_class'].value})")
            added_count += 1
        else:
            print(f"⚠ Already exists: {product_data['name']}")

    session.commit()
    session.close()

    print(f"\n{'='*50}")
    print(f"✅ Added {added_count} new products to database")
    print(f"{'='*50}\n")

    # Print summary by asset class
    session = get_session()
    from sqlalchemy import func

    print("Products by Asset Class:")
    results = session.query(
        InvestmentProduct.asset_class,
        func.count(InvestmentProduct.id)
    ).group_by(InvestmentProduct.asset_class).all()

    for asset_class, count in results:
        print(f"  {asset_class.value:20s}: {count} products")

    session.close()


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Adding Sample Products (All Asset Classes)")
    print("="*50 + "\n")

    try:
        add_sample_products()
        print("\nSample data added successfully!")
        print("\nYou can now:")
        print("  1. Run migration: python scripts/migrate_to_transaction_ledger.py")
        print("  2. Run app: streamlit run app.py")
        print("  3. Search for products across all asset classes")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()