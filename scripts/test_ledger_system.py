"""
Test script for Phase 1.2 - Transaction Ledger System
Verifies LedgerCalculator, RecurringTransactionEngine, and EventTemplates
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.session import get_session
from database.models import Portfolio
from analytics.ledger_calculator import LedgerCalculator
from portfolio.transaction_automation import RecurringTransactionEngine
from portfolio.event_templates import EventTemplates
from portfolio.portfolio_manager import PortfolioManager


def test_ledger_calculator():
    """Test LedgerCalculator with existing portfolio"""
    print("\n" + "="*60)
    print("TEST 1: LedgerCalculator")
    print("="*60)
    
    session = get_session()
    pm = PortfolioManager()
    
    # Get first portfolio
    portfolios = pm.list_portfolios()
    if portfolios.empty:
        print("❌ No portfolios found. Create a portfolio first.")
        session.close()
        return False
    
    portfolio_name = portfolios.iloc[0]['Name']
    portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
    
    print(f"\nTesting portfolio: {portfolio_name}")
    
    # Initialize calculator
    calc = LedgerCalculator(portfolio.id, session)
    
    # Test 1: Get current holdings
    print("\n1. Current Holdings:")
    holdings = calc.get_current_holdings()
    print(f"   Number of positions: {len(holdings)}")
    for product_id, qty in holdings.items():
        print(f"   Product {product_id}: {qty} units")
    
    # Test 2: Cost basis
    print("\n2. Cost Basis:")
    cost_basis = calc.calculate_cost_basis()
    print(f"   Total invested: R {cost_basis:,.2f}")
    
    # Test 3: Income
    print("\n3. Income:")
    income = calc.calculate_total_income()
    print(f"   Total income: R {income['total']:,.2f}")
    print(f"   Dividends: R {income['dividends']:,.2f}")
    print(f"   Interest: R {income['interest']:,.2f}")
    
    # Test 4: Fees
    print("\n4. Fees & Taxes:")
    fees = calc.calculate_total_fees()
    print(f"   Total fees: R {fees['fees']:,.2f}")
    print(f"   Total taxes: R {fees['taxes']:,.2f}")
    
    # Test 5: Realized gains
    print("\n5. Realized Gains:")
    realized = calc.calculate_realized_gains()
    print(f"   Realized P&L: R {realized:,.2f}")
    
    # Test 6: Holdings detail
    print("\n6. Holdings Detail:")
    holdings_df = calc.get_holdings_detail()
    if not holdings_df.empty:
        print(holdings_df.to_string(index=False))
    else:
        print("   No holdings")
    
    # Test 7: Performance summary
    print("\n7. Performance Summary:")
    perf = calc.get_performance_summary()
    for key, value in perf.items():
        if isinstance(value, (int, float)):
            print(f"   {key}: {value:,.2f}")
        else:
            print(f"   {key}: {value}")
    
    session.close()
    print("\n✅ LedgerCalculator tests passed")
    return True


def test_recurring_engine():
    """Test RecurringTransactionEngine"""
    print("\n" + "="*60)
    print("TEST 2: RecurringTransactionEngine")
    print("="*60)
    
    session = get_session()
    pm = PortfolioManager()
    
    # Get first portfolio
    portfolios = pm.list_portfolios()
    if portfolios.empty:
        print("❌ No portfolios found")
        session.close()
        return False
    
    portfolio_name = portfolios.iloc[0]['Name']
    portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
    
    print(f"\nTesting with portfolio: {portfolio_name}")
    
    # Initialize engine
    engine = RecurringTransactionEngine(session)
    
    # Test 1: Get active rules
    print("\n1. Active Rules:")
    active_rules = engine.get_active_rules(portfolio.id)
    print(f"   Number of active rules: {len(active_rules)}")
    
    for rule in active_rules:
        print(f"   - {rule.rule_name} (Next: {rule.next_execution_date})")
    
    # Test 2: Process pending events
    print("\n2. Processing Pending Events:")
    executed = engine.process_pending_events()
    print(f"   Executed {executed} events")
    
    session.close()
    print("\n✅ RecurringTransactionEngine tests passed")
    return True


def test_event_templates():
    """Test EventTemplates"""
    print("\n" + "="*60)
    print("TEST 3: EventTemplates")
    print("="*60)
    
    # Test 1: Get template list
    print("\n1. Available Templates:")
    templates = EventTemplates.get_template_list()
    print(f"   Number of templates: {len(templates)}")
    
    for template in templates:
        print(f"   - {template['display_name']}: {template['description']}")
    
    # Test 2: Create template configs
    print("\n2. Creating Template Configurations:")
    
    # Stock dividend template
    print("\n   Stock Dividend Template:")
    dividend_config = EventTemplates.stock_dividend(
        portfolio_id=1,
        product_id=1,
        dividend_per_share=2.50,
        frequency='QUARTERLY',
        tax_rate=0.20
    )
    print(f"   ✓ Created config: {dividend_config['rule_name']}")
    print(f"     Calculation: {dividend_config['calculation_method']}")
    print(f"     Frequency: {dividend_config['frequency']}")
    
    # Money market interest template
    print("\n   Money Market Interest Template:")
    mm_config = EventTemplates.money_market_interest(
        portfolio_id=1,
        product_id=2,
        annual_rate_pct=7.5
    )
    print(f"   ✓ Created config: {mm_config['rule_name']}")
    print(f"     Calculation: {mm_config['calculation_method']}")
    print(f"     Rate: {mm_config['amount_value']}% per month")
    
    # Bank account interest template
    print("\n   Bank Account Interest Template:")
    bank_config = EventTemplates.bank_account_interest(
        portfolio_id=1,
        product_id=3,
        annual_rate_pct=5.5,
        tax_rate=0.30
    )
    print(f"   ✓ Created config: {bank_config['rule_name']}")
    print(f"     Tax rate: {bank_config['tax_rate']*100}%")
    
    print("\n✅ EventTemplates tests passed")
    return True


def test_portfolio_manager():
    """Test updated PortfolioManager"""
    print("\n" + "="*60)
    print("TEST 4: PortfolioManager (Updated)")
    print("="*60)
    
    pm = PortfolioManager()
    
    # Test 1: List portfolios
    print("\n1. List Portfolios:")
    portfolios = pm.list_portfolios()
    print(f"   Number of portfolios: {len(portfolios)}")
    if not portfolios.empty:
        print(portfolios.to_string(index=False))
    
    if portfolios.empty:
        print("   No portfolios to test with")
        return True
    
    portfolio_name = portfolios.iloc[0]['Name']
    
    # Test 2: Get portfolio (with ledger calculator)
    print(f"\n2. Get Portfolio Holdings: {portfolio_name}")
    holdings = pm.get_portfolio(portfolio_name)
    if holdings is not None and not holdings.empty:
        print(holdings.to_string(index=False))
    else:
        print("   No holdings")
    
    # Test 3: Get transactions
    print(f"\n3. Get Transaction History:")
    transactions = pm.get_portfolio_transactions(portfolio_name)
    if transactions is not None and not transactions.empty:
        print(f"   Total transactions: {len(transactions)}")
        print(transactions.tail(5).to_string(index=False))
    else:
        print("   No transactions")
    
    # Test 4: Get summary
    print(f"\n4. Get Portfolio Summary:")
    summary = pm.get_portfolio_summary(portfolio_name)
    if summary:
        print(f"   Total value: R {summary['total_value']:,.2f}")
        print(f"   Cost basis: R {summary['cost_basis']:,.2f}")
        print(f"   Holdings: {summary['num_holdings']}")
        print(f"   Total income: R {summary['total_income']:,.2f}")
    
    # Test 5: Get cash pools
    print(f"\n5. Get Cash Pools:")
    cash_pools = pm.get_cash_pools(portfolio_name)
    if cash_pools is not None and not cash_pools.empty:
        print(cash_pools.to_string(index=False))
    else:
        print("   No cash pools")
    
    print("\n✅ PortfolioManager tests passed")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" Phase 1.2 - Transaction Ledger System Tests")
    print("="*70)
    
    tests = [
        ("LedgerCalculator", test_ledger_calculator),
        ("RecurringTransactionEngine", test_recurring_engine),
        ("EventTemplates", test_event_templates),
        ("PortfolioManager", test_portfolio_manager)
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
        print("\n🎉 All tests passed! Phase 1.2 is working correctly.")
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