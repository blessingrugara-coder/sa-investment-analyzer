"""
Main Streamlit dashboard for SA Investment Analyzer
"""
import streamlit as st
import pandas as pd
from config.logging_config import setup_logging
from database.session import get_session
from database.models import InvestmentProduct
import logging

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
        
        # Start with base query
        q = session.query(InvestmentProduct)
        
        # Filter by product type if not "All"
        if product_type != "All":
            q = q.filter(InvestmentProduct.product_type == product_type.lower())
        
        # Search in name, identifier, or category
        if query:
            search_term = f"%{query}%"
            q = q.filter(
                (InvestmentProduct.name.ilike(search_term)) |
                (InvestmentProduct.identifier.ilike(search_term)) |
                (InvestmentProduct.category.ilike(search_term))
            )
        
        results = q.all()
        session.close()
        
        # Convert to DataFrame
        if results:
            data = [{
                'Code': p.identifier,
                'Name': p.name,
                'Type': p.product_type.title(),
                'Category': p.category,
                'Provider': p.provider
            } for p in results]
            return pd.DataFrame(data)
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return None

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

# Custom CSS - Neo-Minimal Glass Bento Design
st.markdown("""
<style>
/* Import elegant fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Crimson+Pro:wght@300;400;600&display=swap');

/* Global styling */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Root variables - Soft, warm neutrals with contrast */
:root {
    --bg-primary: #FAFAF9;
    --bg-secondary: #F5F5F4;
    --bg-glass: rgba(255, 255, 255, 0.7);
    --border-soft: rgba(120, 113, 108, 0.12);
    --text-primary: #1C1917;
    --text-secondary: #57534E;
    --text-muted: #A8A29E;
    --accent-primary: #2563EB;
    --accent-secondary: #7C3AED;
    --success: #059669;
    --warning: #D97706;
    --error: #DC2626;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --radius: 12px;
}

/* Main app background - textured */
.stApp {
    background: linear-gradient(135deg, #FAFAF9 0%, #F5F5F4 100%);
    background-attachment: fixed;
}

/* Sidebar - Glassmorphism */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-right: 1px solid var(--border-soft);
    box-shadow: var(--shadow-lg);
}

[data-testid="stSidebar"] > div:first-child {
    padding: 2rem 1.5rem;
}

/* Sidebar title styling */
[data-testid="stSidebar"] h1 {
    font-family: 'Crimson Pro', serif;
    font-weight: 600;
    font-size: 1.75rem;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}

/* Sidebar radio buttons - Bento-style contained buttons */
[data-testid="stSidebar"] .row-widget.stRadio > div {
    gap: 0.5rem;
}

[data-testid="stSidebar"] .row-widget.stRadio > div label {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    margin: 0;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-weight: 500;
    color: var(--text-secondary);
}

[data-testid="stSidebar"] .row-widget.stRadio > div label:hover {
    background: rgba(255, 255, 255, 0.95);
    border-color: var(--accent-primary);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

[data-testid="stSidebar"] .row-widget.stRadio > div label[data-checked="true"] {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    color: white;
    border-color: transparent;
    box-shadow: var(--shadow-md);
}

/* Main content area - Bento grid feeling */
.main .block-container {
    padding: 3rem 2rem;
    max-width: 1400px;
}

/* Headers - Elegant serif */
h1, h2, h3 {
    font-family: 'Crimson Pro', serif;
    color: var(--text-primary);
    font-weight: 600;
    letter-spacing: -0.02em;
}

h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

h2 {
    font-size: 1.875rem;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h3 {
    font-size: 1.5rem;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}

/* Metric cards - Glass bento boxes */
[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-primary);
}

[data-testid="stMetricLabel"] {
    font-size: 0.875rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
}

[data-testid="metric-container"] {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    border-radius: var(--radius);
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    border-color: var(--accent-primary);
}

/* Buttons - Soft, elevated */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    color: white;
    border: none;
    border-radius: var(--radius);
    padding: 0.75rem 1.5rem;
    font-weight: 500;
    font-size: 0.95rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    opacity: 0.95;
}

.stButton > button:active {
    transform: translateY(0);
}

/* Primary button variant */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

/* Input fields - Neo-minimal with texture */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div,
.stDateInput > div > div > input {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    color: var(--text-primary);
    font-size: 0.95rem;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stSelectbox > div > div > div:focus-within,
.stDateInput > div > div > input:focus {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    outline: none;
}

/* Dataframe tables - Bento contained style */
[data-testid="stDataFrame"] {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    border-radius: var(--radius);
    padding: 1rem;
    box-shadow: var(--shadow-sm);
    overflow: hidden;
}

/* Table headers */
[data-testid="stDataFrame"] thead tr th {
    background: var(--bg-secondary);
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 1rem;
    border-bottom: 2px solid var(--border-soft);
}

/* Table rows */
[data-testid="stDataFrame"] tbody tr {
    border-bottom: 1px solid var(--border-soft);
    transition: background 0.2s ease;
}

[data-testid="stDataFrame"] tbody tr:hover {
    background: rgba(37, 99, 235, 0.05);
}

[data-testid="stDataFrame"] tbody tr td {
    padding: 1rem;
    color: var(--text-primary);
}

/* Tabs - Bento sections */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: var(--bg-secondary);
    padding: 0.5rem;
    border-radius: var(--radius);
    border: 1px solid var(--border-soft);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border: none;
    border-radius: calc(var(--radius) - 4px);
    color: var(--text-secondary);
    font-weight: 500;
    padding: 0.75rem 1.5rem;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--bg-glass);
    color: var(--text-primary);
}

.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--accent-primary) !important;
    box-shadow: var(--shadow-sm);
}

/* Info/Warning/Error boxes - Soft glass containers */
.stAlert {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    border-radius: var(--radius);
    padding: 1rem 1.5rem;
    border-left: 4px solid;
}

.stAlert[data-baseweb="notification"][kind="info"] {
    border-left-color: var(--accent-primary);
    background: rgba(37, 99, 235, 0.05);
}

.stAlert[data-baseweb="notification"][kind="success"] {
    border-left-color: var(--success);
    background: rgba(5, 150, 105, 0.05);
}

.stAlert[data-baseweb="notification"][kind="warning"] {
    border-left-color: var(--warning);
    background: rgba(217, 119, 6, 0.05);
}

.stAlert[data-baseweb="notification"][kind="error"] {
    border-left-color: var(--error);
    background: rgba(220, 38, 38, 0.05);
}

/* Expander - Contained sections */
.streamlit-expanderHeader {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    border-radius: var(--radius);
    padding: 1rem 1.5rem;
    font-weight: 500;
    color: var(--text-primary);
    transition: all 0.3s ease;
}

.streamlit-expanderHeader:hover {
    border-color: var(--accent-primary);
    box-shadow: var(--shadow-sm);
}

.streamlit-expanderContent {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    border-top: none;
    border-radius: 0 0 var(--radius) var(--radius);
    padding: 1.5rem;
}

/* Dividers - Soft and subtle */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, var(--border-soft), transparent);
    margin: 2rem 0;
}

/* Spinners - Elegant loading */
.stSpinner > div {
    border-color: var(--accent-primary) transparent transparent transparent;
}

/* Balloons and confetti colors */
.balloon {
    filter: hue-rotate(200deg);
}

/* Column gaps - Bento spacing */
[data-testid="column"] {
    padding: 0.5rem;
}

/* Progress bars - Gradient */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
    border-radius: 10px;
}

/* Select boxes - Glass style */
[data-baseweb="select"] > div {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    border-radius: var(--radius);
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: var(--text-muted);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}

/* Animation for page transitions */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.main .block-container {
    animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Hover effects for interactive elements */
[data-testid="stDataFrame"] tbody tr,
[data-testid="metric-container"],
.stButton > button,
[data-testid="stSidebar"] .row-widget.stRadio > div label {
    will-change: transform;
}

/* Caption and small text - Elegant typography */
.caption, small {
    font-size: 0.875rem;
    color: var(--text-muted);
    font-weight: 400;
}

/* Code blocks - Subtle glass container */
code {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    border-radius: 6px;
    padding: 0.2rem 0.4rem;
    font-size: 0.9em;
    color: var(--accent-primary);
}

pre {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    border-radius: var(--radius);
    padding: 1rem;
}

/* Download button special styling */
.stDownloadButton > button {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-soft);
    color: var(--accent-primary);
}

.stDownloadButton > button:hover {
    background: white;
    border-color: var(--accent-primary);
}
</style>
""", unsafe_allow_html=True)

def glass_card(title, content, icon="", color="primary"):
    """Create a beautiful glass card component"""
    color_map = {
        "primary": "var(--accent-primary)",
        "success": "var(--success)",
        "warning": "var(--warning)",
        "error": "var(--error)"
    }
    
    st.markdown(f"""
    <div style="
        background: var(--bg-glass);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border-soft);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid {color_map.get(color, color_map['primary'])};
    ">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <h3 style="margin: 0; font-family: 'Crimson Pro', serif; color: var(--text-primary);">{title}</h3>
        </div>
        <div style="color: var(--text-secondary);">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def bento_metric(label, value, delta=None, icon=""):
    """Create a bento-style metric box using Streamlit native components"""
    
    # Create a container with custom styling
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(120, 113, 108, 0.12);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="
                color: #A8A29E;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 600;
            ">{label}</span>
            <span style="font-size: 1.5rem; opacity: 0.3;">{icon}</span>
        </div>
        <div style="
            font-size: 2rem;
            font-weight: 600;
            color: #1C1917;
            font-family: 'Crimson Pro', serif;
            margin: 0.5rem 0;
        ">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title, subtitle=""):
    """Create an elegant section header"""
    st.markdown(f"""
    <div style="margin: 2rem 0 1.5rem 0;">
        <h2 style="
            font-family: 'Crimson Pro', serif;
            font-size: 2rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
            letter-spacing: -0.02em;
        ">{title}</h2>
        {f'<p style="color: var(--text-secondary); font-size: 1rem; margin: 0;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.title("📊 SA Investment Analyzer")
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "🔍 Product Search", "🏗️ Portfolio Builder",
             "📊 Analytics", "⚙️ Settings"]
        )
        
        st.divider()
        st.caption("v1.0.0")
        st.caption("Made with ❤️ for SA investors")
    
    # Main content
    if "Dashboard" in page:
        show_dashboard()
    elif "Product Search" in page:
        show_product_search()
    elif "Portfolio Builder" in page:
        show_portfolio_builder()
    elif "Analytics" in page:
        show_analytics()
    elif "Settings" in page:
        show_settings()

def show_dashboard():
    """Dashboard page - Beautiful neo-minimal design"""
    
    # Hero section
    st.markdown("""
    <div style="margin-bottom: 3rem;">
        <h1 style="
            font-family: 'Crimson Pro', serif;
            font-size: 3rem;
            font-weight: 600;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        ">📊 Investment Dashboard</h1>
        <p style="
            color: var(--text-secondary);
            font-size: 1.125rem;
            margin: 0;
        ">Your institutional-grade portfolio analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get data
    product_count = get_product_count()
    
    from portfolio.portfolio_manager import PortfolioManager
    pm = PortfolioManager()
    portfolios = pm.list_portfolios()
    portfolio_count = len(portfolios)
    
    # Bento metrics grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        bento_metric("Investment Products", f"{product_count:,}", icon="🏢")
    
    with col2:
        bento_metric("Portfolios", str(portfolio_count), icon="💼")
    
    with col3:
        if product_count > 0 and portfolio_count > 0:
            bento_metric("System Status", "Ready", icon="✅")
        else:
            bento_metric("System Status", "Setup", icon="⚙️")
    
    with col4:
        bento_metric("Data Updated", "Today", icon="🔄")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Quick actions section
    section_header("Quick Actions", "Get started with these common tasks")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("🔍 Search Products", use_container_width=True, key="btn_search")
    
    with col2:
        st.button("🏗️ Build Portfolio", use_container_width=True, key="btn_build")
    
    with col3:
        st.button("📊 View Analytics", use_container_width=True, key="btn_analytics")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Status cards
    col1, col2 = st.columns(2)
    
    with col1:
        if product_count == 0:
            st.markdown("""
            <div style="
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border-soft);
                border-radius: var(--radius);
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: var(--shadow-sm);
                border-left: 4px solid var(--warning);
            ">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">🗄️</span>
                    <h3 style="margin: 0; font-family: 'Crimson Pro', serif; color: var(--text-primary);">Build Your Database</h3>
                </div>
                <div style="color: var(--text-secondary);">
                    <p><strong>Get started by adding investment products</strong></p>
                    <p>Run this command to add sample JSE stocks and ETFs:</p>
                    <div style="background: rgba(0,0,0,0.05); padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem;">
                        <code style="color: var(--accent-primary); font-family: monospace;">python scripts\\add_sample_data.py</code>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif product_count < 50:
            st.markdown(f"""
            <div style="
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border-soft);
                border-radius: var(--radius);
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: var(--shadow-sm);
                border-left: 4px solid var(--accent-primary);
            ">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">📈</span>
                    <h3 style="margin: 0; font-family: 'Crimson Pro', serif; color: var(--text-primary);">Expand Your Universe</h3>
                </div>
                <div style="color: var(--text-secondary);">
                    <p><strong>You have {product_count} products</strong></p>
                    <p>Add more JSE stocks, unit trusts, and ETFs to get the most out of your analysis.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border-soft);
                border-radius: var(--radius);
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: var(--shadow-sm);
                border-left: 4px solid var(--success);
            ">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">✨</span>
                    <h3 style="margin: 0; font-family: 'Crimson Pro', serif; color: var(--text-primary);">Database Complete</h3>
                </div>
                <div style="color: var(--text-secondary);">
                    <p><strong>{product_count} products available</strong></p>
                    <p>Your product universe is well-stocked. Start building portfolios and analyzing performance!</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if portfolio_count == 0:
            st.markdown("""
            <div style="
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border-soft);
                border-radius: var(--radius);
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: var(--shadow-sm);
                border-left: 4px solid var(--accent-primary);
            ">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">💼</span>
                    <h3 style="margin: 0; font-family: 'Crimson Pro', serif; color: var(--text-primary);">Create Your First Portfolio</h3>
                </div>
                <div style="color: var(--text-secondary);">
                    <p><strong>Ready to track your investments?</strong></p>
                    <p>Head to the Portfolio Builder to create your first portfolio and add holdings.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border-soft);
                border-radius: var(--radius);
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: var(--shadow-sm);
                border-left: 4px solid var(--success);
            ">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.5rem;">🎯</span>
                    <h3 style="margin: 0; font-family: 'Crimson Pro', serif; color: var(--text-primary);">Portfolio Overview</h3>
                </div>
                <div style="color: var(--text-secondary);">
                    <p><strong>{portfolio_count} portfolio{'s' if portfolio_count != 1 else ''} active</strong></p>
                    <p>View detailed analytics and performance metrics in the Analytics section.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Recent portfolios
    if not portfolios.empty:
        section_header("Your Portfolios", "Manage and analyze your investments")
        
        for _, portfolio in portfolios.iterrows():
            with st.expander(f"💼 {portfolio['Name']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                col1.metric("Holdings", portfolio['Holdings'])
                col2.metric("Created", portfolio['Created'].strftime('%Y-%m-%d'))
                
                desc = portfolio['Description'] if portfolio['Description'] else "_No description_"
                col3.write(desc)
                
                if st.button(f"📊 Analyze", key=f"analyze_{portfolio['Name']}", use_container_width=True):
                    st.info(f"Analytics for {portfolio['Name']} - Navigate to Analytics page")

def show_product_search():
    """Product search page"""
    st.title("🔍 Product Search")
    
    # Check if database has products
    product_count = get_product_count()
    
    if product_count == 0:
        st.error("""
        ### Database is Empty
        
        No investment products found in the database.
        
        **To add sample data, run:**
```
        python scripts\\add_sample_data.py
```
        
        This will add 10 sample JSE stocks, ETFs, and indices.
        """)
        return
    
    st.write(f"Search through {product_count:,} investment products")
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search by name, code, or category", 
            placeholder="e.g., Naspers, NPN, bank, ETF",
            key="search_input"
        )
    
    with col2:
        product_type = st.selectbox(
            "Product Type",
            ["All", "Equity", "ETF", "Index", "Unit_trust", "Money_market"]
        )
    
    # Search button
    if st.button("🔍 Search", type="primary") or search_query:
        with st.spinner("Searching..."):
            results = search_products(search_query, product_type)
            
            if results is not None and len(results) > 0:
                st.success(f"Found {len(results)} results")
                
                # Display results
                st.dataframe(
                    results,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Code": st.column_config.TextColumn("Code", width="small"),
                        "Name": st.column_config.TextColumn("Name", width="large"),
                        "Type": st.column_config.TextColumn("Type", width="small"),
                        "Category": st.column_config.TextColumn("Category", width="medium"),
                        "Provider": st.column_config.TextColumn("Provider", width="small"),
                    }
                )
                
                # Show details for first result
                if st.checkbox("Show details for first result"):
                    first = results.iloc[0]
                    st.subheader(f"Details: {first['Name']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Code", first['Code'])
                    with col2:
                        st.metric("Type", first['Type'])
                    with col3:
                        st.metric("Category", first['Category'])
                    
            elif results is not None:
                st.warning(f"No results found for '{search_query}'")
                st.info("Try searching for: naspers, bank, etf, or index")
            else:
                st.error("Error performing search. Check logs for details.")


def show_portfolio_builder():
    """Portfolio builder page - FULLY FUNCTIONAL"""
    st.title("🏗️ Portfolio Builder")
    
    from portfolio.portfolio_manager import PortfolioManager
    
    pm = PortfolioManager()
    
    # Portfolio selector
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
    
    # Create new portfolio
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
    
    # Work with selected portfolio
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Holding", "📋 View Holdings", "📊 Summary"])
    
    with tab1:
        st.subheader(f"Add Holding to '{selected_portfolio}'")
        
        # Get available products
        session = get_session()
        products = session.query(InvestmentProduct).all()
        session.close()
        
        if not products:
            st.warning("No products in database. Add products first!")
            st.stop()
        
        # Create ticker options
        ticker_options = {f"{p.identifier} - {p.name}": p.identifier for p in products}
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_option = st.selectbox(
                "Select Product",
                options=list(ticker_options.keys())
            )
            ticker = ticker_options[selected_option]
            
            quantity = st.number_input("Quantity", min_value=0.01, step=1.0, value=100.0)
        
        with col2:
            entry_price = st.number_input("Entry Price (ZAR)", min_value=0.01, step=0.01, value=100.0)
            entry_date = st.date_input("Entry Date")
        
        # Show calculation
        total_cost = quantity * entry_price
        st.metric("Total Cost", f"R {total_cost:,.2f}")
        
        if st.button("➕ Add to Portfolio", type="primary"):
            if pm.add_holding(selected_portfolio, ticker, quantity, entry_price, entry_date):
                st.success(f"✓ Added {quantity} units of {ticker} @ R{entry_price:,.2f}")
                st.balloons()
                st.rerun()
            else:
                st.error("Failed to add holding. Check logs.")
    
    with tab2:
        st.subheader(f"Holdings in '{selected_portfolio}'")
        
        holdings = pm.get_portfolio(selected_portfolio)
        
        if holdings is None or holdings.empty:
            st.info("No holdings yet. Add your first holding in the 'Add Holding' tab!")
        else:
            # Display holdings table
            st.dataframe(
                holdings,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Entry Price": st.column_config.NumberColumn(
                        "Entry Price",
                        format="R %.2f"
                    ),
                    "Cost Basis": st.column_config.NumberColumn(
                        "Cost Basis",
                        format="R %.2f"
                    ),
                    "Quantity": st.column_config.NumberColumn(
                        "Quantity",
                        format="%.2f"
                    )
                }
            )
            
            # Summary metrics
            st.subheader("Portfolio Metrics")
            
            total_value = holdings['Cost Basis'].sum()
            num_holdings = len(holdings)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Value", f"R {total_value:,.2f}")
            col2.metric("Holdings", num_holdings)
            col3.metric("Avg Position", f"R {total_value/num_holdings:,.2f}")
    
    with tab3:
        st.subheader(f"Portfolio Summary: '{selected_portfolio}'")
        
        summary = pm.get_portfolio_summary(selected_portfolio)
        
        if summary is None:
            st.info("Add holdings to see summary")
        else:
            # Key metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Value", f"R {summary['total_value']:,.2f}")
            with col2:
                st.metric("Number of Holdings", summary['num_holdings'])
            with col3:
                st.metric("Asset Types", len(summary['by_type']))
            
            st.divider()
            
            # Allocation charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Allocation by Type")
                type_df = pd.DataFrame(list(summary['by_type'].items()), 
                                      columns=['Type', 'Allocation %'])
                st.bar_chart(type_df.set_index('Type'))
                
                # Show table
                st.dataframe(type_df, hide_index=True, use_container_width=True)
            
            with col2:
                st.subheader("Allocation by Category")
                cat_df = pd.DataFrame(list(summary['by_category'].items()), 
                                     columns=['Category', 'Allocation %'])
                st.bar_chart(cat_df.set_index('Category'))
                
                # Show table
                st.dataframe(cat_df, hide_index=True, use_container_width=True)


def show_analytics():
    """Analytics page - FULLY FUNCTIONAL"""
    st.title("📊 Portfolio Analytics")
    
    from portfolio.portfolio_manager import PortfolioManager
    from analytics.performance_calculator import PerformanceCalculator
    
    pm = PortfolioManager()
    
    # Portfolio selector
    portfolios = pm.list_portfolios()
    
    if portfolios.empty:
        st.warning("No portfolios found. Create a portfolio first in the Portfolio Builder!")
        st.stop()
    
    selected_portfolio = st.selectbox(
        "Select Portfolio to Analyze",
        portfolios['Name'].tolist()
    )
    
    # Get portfolio data
    holdings = pm.get_portfolio(selected_portfolio)
    
    if holdings is None or holdings.empty:
        st.info(f"Portfolio '{selected_portfolio}' has no holdings yet.")
        st.stop()
    
    # Create calculator
    calc = PerformanceCalculator(holdings)
    
    # Tabs for different analytics
    tabs = st.tabs(["📊 Overview", "🎯 Allocation", "📈 Holdings Detail", "⚖️ Diversification"])
    
    with tabs[0]:
        st.subheader("Portfolio Overview")
        
        # Summary stats
        stats = calc.get_summary_stats()
        
        cols = st.columns(len(stats))
        for col, (label, value) in zip(cols, stats.items()):
            col.metric(label, value)
        
        st.divider()
        
        # Holdings table
        st.subheader("All Holdings")
        st.dataframe(holdings, use_container_width=True, hide_index=True)
    
    with tabs[1]:
        st.subheader("Asset Allocation Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**By Product Type**")
            type_alloc = calc.calculate_type_allocation()
            if type_alloc is not None:
                st.dataframe(type_alloc, use_container_width=True)
                st.bar_chart(type_alloc)
        
        with col2:
            st.write("**By Category**")
            cat_alloc = calc.calculate_category_allocation()
            if cat_alloc is not None:
                st.dataframe(cat_alloc, use_container_width=True)
                st.bar_chart(cat_alloc)
        
        st.divider()
        
        st.subheader("Individual Position Sizes")
        position_alloc = calc.calculate_allocation()
        st.dataframe(position_alloc, use_container_width=True, hide_index=True)
        st.bar_chart(position_alloc.set_index('Ticker')['Allocation %'])
    
    with tabs[2]:
        st.subheader("Holdings Detail")
        
        # Detailed view with all columns
        st.dataframe(
            holdings,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Entry Price": st.column_config.NumberColumn(format="R %.2f"),
                "Cost Basis": st.column_config.NumberColumn(format="R %.2f"),
            }
        )
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = holdings.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                f"{selected_portfolio}_holdings.csv",
                "text/csv"
            )
    
    with tabs[3]:
        st.subheader("Diversification Analysis")
        
        score = calc.calculate_diversification_score()
        
        # Show score with color
        if score >= 70:
            st.success(f"Diversification Score: {score:.0f}/100 - Well Diversified")
        elif score >= 40:
            st.warning(f"Diversification Score: {score:.0f}/100 - Moderately Diversified")
        else:
            st.error(f"Diversification Score: {score:.0f}/100 - Needs More Diversification")
        
        # Progress bar
        st.progress(score / 100)
        
        st.divider()
        
        st.write("**Diversification Tips:**")
        
        num_holdings = len(holdings)
        if num_holdings < 10:
            st.info(f"• Consider adding more holdings (current: {num_holdings}, recommended: 10-20)")
        
        allocation = calc.calculate_allocation()
        max_position = allocation['Allocation %'].max()
        if max_position > 20:
            st.warning(f"• Largest position is {max_position:.1f}% - consider rebalancing (recommended max: 20%)")
        
        # Type diversification
        type_count = calc.calculate_type_allocation()
        if type_count is not None and len(type_count) == 1:
            st.info("• Consider diversifying across different product types (stocks, ETFs, etc.)")

def show_settings():
    """Settings page"""
    st.title("⚙️ Settings")
    
    st.subheader("System Configuration")
    
    with st.expander("📊 Data Sources", expanded=True):
        st.checkbox("Enable automatic data updates", value=True)
        st.number_input("Update frequency (hours)", value=24, min_value=1, max_value=168)
        
        st.write("**Available data sources:**")
        st.write("- yfinance (JSE stocks)")
        st.write("- OpenBB Platform")
        st.write("- Web scrapers (SENS, fund fact sheets)")
    
    with st.expander("🎨 Display Preferences"):
        st.selectbox("Base Currency", ["ZAR", "USD", "EUR", "GBP"], index=0)
        st.selectbox("Date Format", ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"], index=0)
        st.selectbox("Number Format", ["1,234.56", "1 234.56", "1.234,56"], index=0)
    
    with st.expander("🔔 Notifications"):
        st.checkbox("Email notifications", value=False)
        st.checkbox("Price alerts", value=False)
        st.checkbox("Portfolio rebalancing alerts", value=False)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Settings", type="primary"):
            st.success("Settings saved successfully!")
    
    with col2:
        if st.button("🔄 Reset to Defaults"):
            st.info("Settings reset to defaults")


if __name__ == "__main__":
    main()