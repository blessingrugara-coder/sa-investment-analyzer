"""
Main Streamlit dashboard for SA Investment Analyzer
Updated with Transaction Ledger UI
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
from config.logging_config import setup_logging
from database.session import get_session
from database.models import InvestmentProduct, TransactionType
from portfolio.portfolio_manager import PortfolioManager
from analytics.ledger_calculator import LedgerCalculator
import logging

# Setup
setup_logging()
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="SA Investment Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [Keep all the existing CSS - the glassmorphism styling]
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Crimson+Pro:wght@300;400;600&display=swap');
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
:root {
    --bg-primary: #FAFAF9; --bg-secondary: #F5F5F4; --bg-glass: rgba(255, 255, 255, 0.7);
    --border-soft: rgba(120, 113, 108, 0.12); --text-primary: #1C1917; --text-secondary: #57534E;
    --text-muted: #A8A29E; --accent-primary: #2563EB; --accent-secondary: #7C3AED;
    --success: #059669; --warning: #D97706; --error: #DC2626;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05); --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1); --radius: 12px;
}
.stApp { background: linear-gradient(135deg, #FAFAF9 0%, #F5F5F4 100%); background-attachment: fixed; }
[data-testid="stSidebar"] { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(20px) saturate(180%);
    border-right: 1px solid var(--border-soft); box-shadow: var(--shadow-lg); }
[data-testid="stSidebar"] h1 { font-family: 'Crimson Pro', serif; font-weight: 600; font-size: 1.75rem;
    color: var(--text-primary); margin-bottom: 0.5rem; letter-spacing: -0.02em; }
.main .block-container { padding: 3rem 2rem; max-width: 1400px; }
h1, h2, h3 { font-family: 'Crimson Pro', serif; color: var(--text-primary); font-weight: 600; letter-spacing: -0.02em; }
[data-testid="metric-container"] { background: var(--bg-glass); backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft); border-radius: var(--radius); padding: 1.5rem;
    box-shadow: var(--shadow-sm); transition: all 0.3s ease; }
[data-testid="metric-container"]:hover { transform: translateY(-2px); box-shadow: var(--shadow-md);
    border-color: var(--accent-primary); }
.stButton > button { background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    color: white; border: none; border-radius: var(--radius); padding: 0.75rem 1.5rem;
    font-weight: 500; font-size: 0.95rem; box-shadow: var(--shadow-sm);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer; }
.stButton > button:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); opacity: 0.95; }
</style>
""", unsafe_allow_html=True)


def get_product_count():
    """Get total number of products in database"""
    try:
        session = get_session()
        count = session.query(InvestmentProduct).count()
        session.close()
        return count
    except Exception as e:
        logger.error(f"Error getting product count: {e}")
        return 0


def search_products(query, product_type):
    """Search for products in database"""
    try:
        session = get_session()
        q = session.query(InvestmentProduct)
        
        if product_type != "All":
            q = q.filter(InvestmentProduct.product_type == product_type.lower())
        
        if query:
            search_term = f"%{query}%"
            q = q.filter(
                (InvestmentProduct.name.ilike(search_term)) |
                (InvestmentProduct.identifier.ilike(search_term)) |
                (InvestmentProduct.category.ilike(search_term))
            )
        
        results = q.all()
        session.close()
        
        if results:
            data = [{
                'Code': p.identifier,
                'Name': p.name,
                'Type': p.asset_class.value.replace('_', ' ').title() if p.asset_class else p.product_type.title(),
                'Category': p.category,
                'Provider': p.provider
            } for p in results]
            return pd.DataFrame(data)
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return None


def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.title("📊 SA Investment Analyzer")
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "🔍 Product Search", "💼 Transactions", 
             "🏗️ Portfolio Builder", "📊 Analytics", "⚙️ Settings"]
        )
        
        st.divider()
        st.caption("v1.1.0 - Transaction Ledger")
        st.caption("Made with ❤️ for SA investors")
    
    # Main content
    if "Dashboard" in page:
        show_dashboard()
    elif "Product Search" in page:
        show_product_search()
    elif "Transactions" in page:
        show_transactions()
    elif "Portfolio Builder" in page:
        show_portfolio_builder()
    elif "Analytics" in page:
        show_analytics()
    elif "Settings" in page:
        show_settings()


def show_dashboard():
    """Dashboard page"""
    st.markdown("""
    <div style="margin-bottom: 3rem;">
        <h1 style="font-family: 'Crimson Pro', serif; font-size: 3rem; font-weight: 600;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            📊 Investment Dashboard</h1>
        <p style="color: var(--text-secondary); font-size: 1.125rem; margin: 0;">
            Your institutional-grade portfolio analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    product_count = get_product_count()
    pm = PortfolioManager()
    portfolios = pm.list_portfolios()
    portfolio_count = len(portfolios)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Investment Products", f"{product_count:,}")
    with col2:
        st.metric("Portfolios", str(portfolio_count))
    with col3:
        st.metric("System Status", "✅ Ready" if product_count > 0 else "⚙️ Setup")
    with col4:
        st.metric("Data Updated", "Today")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Search Products", use_container_width=True):
            st.switch_page("app.py")
    with col2:
        if st.button("💼 Add Transaction", use_container_width=True):
            st.switch_page("app.py")
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("app.py")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Recent portfolios
    if not portfolios.empty:
        st.subheader("Your Portfolios")
        for _, portfolio in portfolios.iterrows():
            with st.expander(f"💼 {portfolio['Name']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                col1.metric("Holdings", portfolio['Holdings'])
                col2.metric("Created", portfolio['Created'].strftime('%Y-%m-%d'))
                desc = portfolio['Description'] if portfolio['Description'] else "_No description_"
                col3.write(desc)


def show_product_search():
    """Product search page"""
    st.title("🔍 Product Search")
    
    product_count = get_product_count()
    
    if product_count == 0:
        st.error("Database is empty. Run: `python scripts/add_sample_data.py`")
        return
    
    st.write(f"Search through {product_count:,} investment products")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Search by name, code, or category", 
            placeholder="e.g., Naspers, NPN, bank, ETF"
        )
    with col2:
        product_type = st.selectbox(
            "Product Type",
            ["All", "Equity", "ETF", "Index", "Unit_trust", "Money_market", "Bank_account", "FX"]
        )
    
    if st.button("🔍 Search", type="primary") or search_query:
        with st.spinner("Searching..."):
            results = search_products(search_query, product_type)
            
            if results is not None and len(results) > 0:
                st.success(f"Found {len(results)} results")
                st.dataframe(results, use_container_width=True, hide_index=True)
            elif results is not None:
                st.warning(f"No results found for '{search_query}'")
            else:
                st.error("Error performing search")


def show_transactions():
    """NEW: Transaction management page"""
    st.title("💼 Transaction Manager")
    
    pm = PortfolioManager()
    portfolios = pm.list_portfolios()
    
    if portfolios.empty:
        st.warning("No portfolios found. Create a portfolio first!")
        return
    
    # Portfolio selector
    selected_portfolio = st.selectbox(
        "Select Portfolio",
        portfolios['Name'].tolist()
    )
    
    tabs = st.tabs(["➕ Add Transaction", "📋 Transaction History", "📊 Summary"])
    
    with tabs[0]:
        show_add_transaction_form(selected_portfolio)
    
    with tabs[1]:
        show_transaction_history(selected_portfolio)
    
    with tabs[2]:
        show_transaction_summary(selected_portfolio)


def show_add_transaction_form(portfolio_name):
    """Form to add new transaction"""
    st.subheader("Add New Transaction")
    
    # Get products
    session = get_session()
    products = session.query(InvestmentProduct).all()
    session.close()
    
    if not products:
        st.warning("No products in database")
        return
    
    # Product selector
    product_options = {f"{p.identifier} - {p.name}": p.identifier for p in products}
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_option = st.selectbox("Product", list(product_options.keys()))
        ticker = product_options[selected_option]
        
        transaction_type = st.selectbox(
            "Transaction Type",
            ["BUY", "SELL", "DIVIDEND", "INTEREST", "FEE"]
        )
        
        quantity = st.number_input("Quantity", min_value=0.01, step=1.0, value=100.0)
    
    with col2:
        price = st.number_input("Price per Unit (ZAR)", min_value=0.01, step=0.01, value=100.0)
        
        transaction_date = st.date_input("Transaction Date", value=date.today())
        
        fees = st.number_input("Fees (ZAR)", min_value=0.0, step=0.01, value=0.0)
    
    taxes = st.number_input("Taxes (ZAR)", min_value=0.0, step=0.01, value=0.0)
    notes = st.text_area("Notes (optional)", placeholder="Add any additional information")
    
    # Show calculation
    gross = quantity * price
    net = gross + fees + taxes if transaction_type == "BUY" else gross - fees - taxes
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Gross Amount", f"R {gross:,.2f}")
    col2.metric("Fees + Taxes", f"R {fees + taxes:,.2f}")
    col3.metric("Net Amount", f"R {net:,.2f}")
    
    if st.button("➕ Add Transaction", type="primary", use_container_width=True):
        pm = PortfolioManager()
        success = pm.add_transaction(
            portfolio_name=portfolio_name,
            product_identifier=ticker,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            transaction_date=transaction_date,
            fees=fees,
            taxes=taxes,
            notes=notes
        )
        
        if success:
            st.success(f"✅ Added {transaction_type} transaction!")
            st.balloons()
            st.rerun()
        else:
            st.error("Failed to add transaction")


def show_transaction_history(portfolio_name):
    """Show all transactions for portfolio"""
    st.subheader("Transaction History")
    
    pm = PortfolioManager()
    transactions = pm.get_portfolio_transactions(portfolio_name)
    
    if transactions is None or transactions.empty:
        st.info("No transactions yet. Add your first transaction!")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.multiselect(
            "Filter by Type",
            options=transactions['Type'].unique().tolist(),
            default=transactions['Type'].unique().tolist()
        )
    with col2:
        filter_product = st.multiselect(
            "Filter by Product",
            options=transactions['Product'].unique().tolist(),
            default=transactions['Product'].unique().tolist()
        )
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(transactions['Date'].min(), transactions['Date'].max()),
            key="txn_date_range"
        )
    
    # Apply filters
    filtered = transactions[
        (transactions['Type'].isin(filter_type)) &
        (transactions['Product'].isin(filter_product))
    ]
    
    if len(date_range) == 2:
        filtered = filtered[
            (filtered['Date'] >= date_range[0]) &
            (filtered['Date'] <= date_range[1])
        ]
    
    # Display
    st.write(f"Showing {len(filtered)} of {len(transactions)} transactions")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    
    # Export
    if st.button("📥 Export to CSV"):
        csv = filtered.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            f"{portfolio_name}_transactions.csv",
            "text/csv"
        )


def show_transaction_summary(portfolio_name):
    """Show transaction summary statistics"""
    st.subheader("Transaction Summary")
    
    session = get_session()
    from database.models import Portfolio
    portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
    
    if not portfolio:
        session.close()
        return
    
    calc = LedgerCalculator(portfolio.id, session)
    
    # Performance summary
    perf = calc.get_performance_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cost Basis", f"R {perf['cost_basis']:,.2f}")
    col2.metric("Total Income", f"R {perf['total_income']:,.2f}")
    col3.metric("Realized Gains", f"R {perf['realized_gains']:,.2f}")
    col4.metric("Total Fees", f"R {perf['total_fees']:,.2f}")
    
    st.divider()
    
    # Income breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Income Breakdown**")
        income_data = {
            'Type': ['Dividends', 'Interest', 'Total'],
            'Amount': [
                f"R {perf['dividend_income']:,.2f}",
                f"R {perf['interest_income']:,.2f}",
                f"R {perf['total_income']:,.2f}"
            ]
        }
        st.dataframe(pd.DataFrame(income_data), hide_index=True, use_container_width=True)
    
    with col2:
        st.write("**Portfolio Stats**")
        stats_data = {
            'Metric': ['Holdings', 'Transactions', 'Cost Basis'],
            'Value': [
                perf['num_holdings'],
                perf['num_transactions'],
                f"R {perf['cost_basis']:,.2f}"
            ]
        }
        st.dataframe(pd.DataFrame(stats_data), hide_index=True, use_container_width=True)
    
    # Income by product
    st.divider()
    st.write("**Income by Product**")
    income_by_product = calc.get_income_by_product()
    
    if not income_by_product.empty:
        st.dataframe(income_by_product, hide_index=True, use_container_width=True)
    else:
        st.info("No income recorded yet")
    
    session.close()


def show_portfolio_builder():
    """Portfolio builder page (legacy compatibility)"""
    st.title("🏗️ Portfolio Builder")
    
    pm = PortfolioManager()
    portfolios = pm.list_portfolios()
    
    st.subheader("Select or Create Portfolio")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not portfolios.empty:
            portfolio_names = portfolios['Name'].tolist()
            selected_portfolio = st.selectbox(
                "Active Portfolio",
                ['-- Create New --'] + portfolio_names
            )
        else:
            selected_portfolio = '-- Create New --'
            st.info("No portfolios yet. Create your first portfolio below!")
    
    with col2:
        if st.button("🗑️ Delete Portfolio", disabled=(selected_portfolio == '-- Create New --')):
            if pm.delete_portfolio(selected_portfolio):
                st.success(f"Deleted portfolio: {selected_portfolio}")
                st.rerun()
    
    if selected_portfolio == '-- Create New --':
        st.subheader("Create New Portfolio")
        new_name = st.text_input("Portfolio Name", placeholder="My JSE Portfolio")
        new_desc = st.text_area("Description (optional)", placeholder="Long-term growth portfolio")
        
        if st.button("✨ Create Portfolio", type="primary"):
            if new_name:
                result = pm.create_portfolio(new_name, new_desc)
                if result:
                    st.success(f"✓ Created portfolio: {new_name}")
                    st.rerun()
                else:
                    st.error("Portfolio name already exists")
            else:
                st.error("Please enter a portfolio name")
        st.stop()
    
    # Show portfolio details
    st.divider()
    holdings = pm.get_portfolio(selected_portfolio)
    
    if holdings is None or holdings.empty:
        st.info("No holdings yet. Add transactions via the Transactions page!")
    else:
        st.subheader(f"Holdings in '{selected_portfolio}'")
        st.dataframe(holdings, use_container_width=True, hide_index=True)
        
        # Summary
        st.subheader("Portfolio Summary")
        summary = pm.get_portfolio_summary(selected_portfolio)
        
        if summary:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Value", f"R {summary['total_value']:,.2f}")
            col2.metric("Holdings", summary['num_holdings'])
            col3.metric("Total Income", f"R {summary['total_income']:,.2f}")


def show_analytics():
    """Analytics page with enhanced metrics"""
    st.title("📊 Portfolio Analytics")
    
    pm = PortfolioManager()
    portfolios = pm.list_portfolios()
    
    if portfolios.empty:
        st.warning("No portfolios found")
        return
    
    selected_portfolio = st.selectbox("Select Portfolio", portfolios['Name'].tolist())
    
    # Get data with market values
    holdings = pm.get_portfolio(selected_portfolio, include_market_values=True)
    
    if holdings is None or holdings.empty:
        st.info("No holdings in this portfolio")
        return
    
    # Get session for additional calculations
    session = get_session()
    from database.models import Portfolio
    portfolio = session.query(Portfolio).filter_by(name=selected_portfolio).first()
    
    if not portfolio:
        session.close()
        return
    
    calc = LedgerCalculator(portfolio.id, session)
    
    # Tabs
    tabs = st.tabs(["📊 Overview", "📈 Performance", "💰 Income", "💸 Costs", "🏆 Holdings"])
    
    with tabs[0]:
        # Calculate totals
        cost_basis = holdings['Cost Basis'].sum()
        market_value = holdings['Market Value'].sum() if 'Market Value' in holdings.columns else cost_basis
        unrealized_gain = holdings['Unrealized Gain'].sum() if 'Unrealized Gain' in holdings.columns else 0
        
        perf = calc.get_performance_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cost Basis", f"R {cost_basis:,.2f}")
        col2.metric("Market Value", f"R {market_value:,.2f}", 
                   f"R {unrealized_gain:,.2f}" if unrealized_gain != 0 else None)
        col3.metric("Total Income", f"R {perf['total_income']:,.2f}")
        col4.metric("Total Fees", f"R {perf['total_fees']:,.2f}")
        
        st.divider()
        st.subheader("All Holdings")
        st.dataframe(holdings, use_container_width=True, hide_index=True)
    
    with tabs[1]:
        st.subheader("Performance Metrics")
        
        # Get performance analysis
        performance = pm.get_performance_analysis(selected_portfolio)
        
        if performance is None:
            st.info("Insufficient data for performance analysis")
        else:
            # Returns section
            st.write("**Returns**")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Return", f"{performance['total_return_pct']:.2f}%")
            col2.metric("Annualized Return", f"{performance['annualized_return_pct']:.2f}%")
            col3.metric("TWR", f"{performance['time_weighted_return_pct']:.2f}%")
            col4.metric("MWR (IRR)", f"{performance['money_weighted_return_pct']:.2f}%")
            
            st.divider()
            
            # Risk metrics
            st.write("**Risk Metrics**")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Volatility", f"{performance['volatility_pct']:.2f}%")
            col2.metric("Max Drawdown", f"{performance['max_drawdown_pct']:.2f}%")
            col3.metric("VaR (95%)", f"{performance['var_95']*100:.2f}%")
            col4.metric("CVaR (95%)", f"{performance['cvar_95']*100:.2f}%")
            
            st.divider()
            
            # Risk-adjusted returns
            st.write("**Risk-Adjusted Returns**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Sharpe Ratio", f"{performance['sharpe_ratio']:.2f}")
            col2.metric("Sortino Ratio", f"{performance['sortino_ratio']:.2f}")
            col3.metric("Calmar Ratio", f"{performance['calmar_ratio']:.2f}")
            
            st.divider()
            
            # Summary stats
            st.write("**Summary Statistics**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Invested", f"R {performance.get('total_invested', 0):,.2f}")
            col2.metric("Current Value", f"R {performance.get('end_value', 0):,.2f}")
            col3.metric("Absolute Gain", f"R {performance.get('absolute_gain', 0):,.2f}")
            
            # Period info
            st.caption(f"Period: {performance['start_date']} to {performance['end_date']} ({performance['num_periods']} days)")
    
    with tabs[2]:
        st.subheader("Income Analysis")
        income_df = calc.get_income_by_product()
        
        if not income_df.empty:
            st.dataframe(income_df, use_container_width=True, hide_index=True)
            st.bar_chart(income_df.set_index('Product')['Total Income'])
        else:
            st.info("No income recorded")
    
    with tabs[3]:
        st.subheader("Costs & Fees")
        fees = calc.calculate_total_fees()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Fees", f"R {fees['fees']:,.2f}")
        col2.metric("Total Taxes", f"R {fees['taxes']:,.2f}")
        col3.metric("Total Costs", f"R {fees['total']:,.2f}")
    
    with tabs[4]:
        st.subheader("Holdings Detail")
        st.dataframe(holdings, use_container_width=True, hide_index=True)
    
    session.close()


def show_settings():
    """Settings page"""
    st.title("⚙️ Settings")
    st.info("Settings page - Coming soon!")


if __name__ == "__main__":
    main()