"""
Migration script: Migrate from PortfolioHolding to Transaction Ledger
Converts existing holdings into BUY transactions
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.session import get_session, init_db
from database.models import (
    Portfolio, PortfolioHolding, Transaction, InvestmentProduct,
    CashPool, TransactionType, AssetClass
)


def backup_database():
    """Create backup of database before migration"""
    import shutil
    
    db_path = Path('sa_investments.db')
    if db_path.exists():
        backup_path = Path(f'sa_investments_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        shutil.copy(db_path, backup_path)
        print(f"✓ Database backed up to: {backup_path}")
        return backup_path
    return None


def update_product_asset_classes(session):
    """
    Update existing products with new asset_class enum
    Maps old product_type string to new AssetClass enum
    """
    print("\n" + "="*60)
    print("Updating Product Asset Classes")
    print("="*60)
    
    mapping = {
        'equity': AssetClass.EQUITY,
        'etf': AssetClass.ETF,
        'index': AssetClass.INDEX,
        'bond': AssetClass.BOND,
        'unit_trust': AssetClass.UNIT_TRUST,
        'property': AssetClass.PROPERTY,
        'commodity': AssetClass.COMMODITY,
        'crypto': AssetClass.CRYPTO,
    }
    
    products = session.query(InvestmentProduct).all()
    updated_count = 0
    
    for product in products:
        # Map old product_type to new asset_class
        old_type = product.product_type.lower() if product.product_type else 'other'
        
        if old_type in mapping:
            product.asset_class = mapping[old_type]
        else:
            product.asset_class = AssetClass.OTHER
        
        updated_count += 1
        print(f"  {product.identifier}: {old_type} -> {product.asset_class.value}")
    
    session.commit()
    print(f"\n✓ Updated {updated_count} products")


def create_default_cash_pools(session):
    """
    Create default cash pool for each portfolio
    """
    print("\n" + "="*60)
    print("Creating Default Cash Pools")
    print("="*60)
    
    portfolios = session.query(Portfolio).filter_by(is_active=True).all()
    
    for portfolio in portfolios:
        # Check if cash pool already exists
        existing_pool = session.query(CashPool).filter_by(
            portfolio_id=portfolio.id,
            currency='ZAR'
        ).first()
        
        if not existing_pool:
            cash_pool = CashPool(
                portfolio_id=portfolio.id,
                name=f"{portfolio.name} - Cash",
                currency=portfolio.base_currency,
                account_type='CHECKING',
                current_balance=0.0
            )
            session.add(cash_pool)
            print(f"  ✓ Created cash pool for: {portfolio.name}")
        else:
            print(f"  ⚠ Cash pool already exists for: {portfolio.name}")
    
    session.commit()


def migrate_holdings_to_transactions(session):
    """
    Convert existing PortfolioHolding records into BUY transactions
    This preserves all historical holding data
    """
    print("\n" + "="*60)
    print("Migrating Holdings to Transaction Ledger")
    print("="*60)
    
    holdings = session.query(PortfolioHolding).all()
    
    if not holdings:
        print("  ℹ No holdings to migrate")
        return
    
    migrated_count = 0
    
    for holding in holdings:
        # Check if transaction already exists for this holding
        existing_txn = session.query(Transaction).filter_by(
            portfolio_id=holding.portfolio_id,
            product_id=holding.product_id,
            transaction_date=holding.entry_date,
            quantity=holding.quantity,
            price=holding.entry_price
        ).first()
        
        if existing_txn:
            print(f"  ⚠ Transaction already exists for: {holding.product.identifier}")
            continue
        
        # Calculate amounts
        gross_amount = holding.quantity * holding.entry_price
        
        # Create BUY transaction
        transaction = Transaction(
            portfolio_id=holding.portfolio_id,
            product_id=holding.product_id,
            transaction_type=TransactionType.BUY,
            transaction_date=holding.entry_date,
            quantity=holding.quantity,
            price=holding.entry_price,
            gross_amount=gross_amount,
            fees=0.0,  # We don't have fee data from old holdings
            taxes=0.0,
            net_amount=gross_amount,
            notes="Migrated from legacy holdings",
            is_auto_generated=False,
            currency='ZAR'
        )
        
        session.add(transaction)
        migrated_count += 1
        
        print(f"  ✓ Migrated: {holding.product.identifier} - {holding.quantity} @ R{holding.entry_price:,.2f}")
    
    session.commit()
    print(f"\n✓ Migrated {migrated_count} holdings to transactions")


def create_sample_recurring_rules(session):
    """
    Create sample recurring transaction rules for demonstration
    (Optional - only if user wants examples)
    """
    print("\n" + "="*60)
    print("Creating Sample Recurring Rules (Optional)")
    print("="*60)
    
    # This is optional - we'll skip for now
    print("  ℹ Skipping sample rules (can be created via UI)")


def verify_migration(session):
    """
    Verify that migration was successful
    """
    print("\n" + "="*60)
    print("Verification")
    print("="*60)
    
    # Count records
    product_count = session.query(InvestmentProduct).count()
    portfolio_count = session.query(Portfolio).count()
    holding_count = session.query(PortfolioHolding).count()
    transaction_count = session.query(Transaction).count()
    cash_pool_count = session.query(CashPool).count()
    
    print(f"\n  Products:         {product_count}")
    print(f"  Portfolios:       {portfolio_count}")
    print(f"  Legacy Holdings:  {holding_count}")
    print(f"  Transactions:     {transaction_count}")
    print(f"  Cash Pools:       {cash_pool_count}")
    
    # Verify transaction amounts match holdings
    if holding_count > 0 and transaction_count > 0:
        print("\n  Verifying data integrity...")
        
        holdings = session.query(PortfolioHolding).all()
        all_match = True
        
        for holding in holdings:
            expected_value = holding.quantity * holding.entry_price
            
            # Find matching transaction
            txn = session.query(Transaction).filter_by(
                portfolio_id=holding.portfolio_id,
                product_id=holding.product_id,
                transaction_type=TransactionType.BUY
            ).first()
            
            if txn and abs(txn.gross_amount - expected_value) < 0.01:
                print(f"    ✓ {holding.product.identifier}: Values match")
            else:
                print(f"    ✗ {holding.product.identifier}: Value mismatch!")
                all_match = False
        
        if all_match:
            print("\n  ✓ All data verified successfully!")
        else:
            print("\n  ⚠ Some data mismatches detected")
    
    print("\n" + "="*60)


def main():
    """Main migration function"""
    print("\n" + "="*70)
    print(" SA Investment Analyzer - Transaction Ledger Migration")
    print("="*70)
    
    print("\nThis script will:")
    print("  1. Backup your current database")
    print("  2. Create new transaction ledger tables")
    print("  3. Update product asset classes")
    print("  4. Create default cash pools")
    print("  5. Migrate existing holdings to transactions")
    print("  6. Verify migration")
    
    response = input("\nProceed with migration? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("\nMigration cancelled.")
        return
    
    print("\n" + "="*70)
    print("Starting Migration...")
    print("="*70)
    
    # Step 1: Backup
    print("\nStep 1: Creating backup...")
    backup_path = backup_database()
    
    # Step 2: Initialize new schema
    print("\nStep 2: Creating new tables...")
    try:
        init_db()
        print("✓ New tables created")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        print("\nTables may already exist - continuing...")
    
    # Get session
    session = get_session()
    
    try:
        # Step 3: Update asset classes
        print("\nStep 3: Updating asset classes...")
        update_product_asset_classes(session)
        
        # Step 4: Create cash pools
        print("\nStep 4: Creating cash pools...")
        create_default_cash_pools(session)
        
        # Step 5: Migrate holdings
        print("\nStep 5: Migrating holdings to transactions...")
        migrate_holdings_to_transactions(session)
        
        # Step 6: Verify
        print("\nStep 6: Verifying migration...")
        verify_migration(session)
        
        print("\n" + "="*70)
        print("✅ Migration Complete!")
        print("="*70)
        
        print("\nWhat's New:")
        print("  • Transaction ledger system activated")
        print("  • Cash pools created for each portfolio")
        print("  • Legacy holdings converted to transactions")
        print("  • Support for 12 asset classes (including FX, Money Market, Bank)")
        print("  • Ready for recurring transaction rules")
        
        print("\nNext Steps:")
        print("  1. Restart your Streamlit app: streamlit run app.py")
        print("  2. Existing portfolios will work with new system")
        print("  3. Start adding transactions via the new UI")
        
        if backup_path:
            print(f"\nBackup saved at: {backup_path}")
            print("(You can delete this after verifying everything works)")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        
        print("\nRollback instructions:")
        if backup_path:
            print(f"  1. Delete sa_investments.db")
            print(f"  2. Rename {backup_path} to sa_investments.db")
        
        session.rollback()
        sys.exit(1)
    
    finally:
        session.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)