"""
Portfolio management - save, load, and manage portfolios
"""
from database.session import get_session, get_db_session
from database.models import Portfolio, PortfolioHolding, InvestmentProduct, Price
from datetime import datetime, date
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class PortfolioManager:
    """Manage portfolio operations"""
    
    def __init__(self):
        self.session = None
    
    def create_portfolio(self, name, description=None):
        """
        Create a new portfolio
        
        Args:
            name: Portfolio name (must be unique)
            description: Optional description
            
        Returns:
            Portfolio object or None if name exists
        """
        try:
            with get_db_session() as session:
                # Check if name already exists
                existing = session.query(Portfolio).filter_by(name=name).first()
                if existing:
                    logger.warning(f"Portfolio '{name}' already exists")
                    return None
                
                portfolio = Portfolio(
                    name=name,
                    description=description,
                    created_date=date.today(),
                    base_currency='ZAR',
                    is_active=True
                )
                session.add(portfolio)
                session.flush()
                
                logger.info(f"Created portfolio: {name}")
                return portfolio
                
        except Exception as e:
            logger.error(f"Error creating portfolio: {e}")
            return None
    
    def add_holding(self, portfolio_name, ticker, quantity, entry_price, entry_date=None):
        """
        Add a holding to portfolio
        
        Args:
            portfolio_name: Name of portfolio
            ticker: Product identifier (e.g., 'NPN.JO')
            quantity: Number of shares/units
            entry_price: Purchase price
            entry_date: Purchase date (defaults to today)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_session() as session:
                # Get portfolio
                portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
                if not portfolio:
                    logger.error(f"Portfolio '{portfolio_name}' not found")
                    return False
                
                # Get product
                product = session.query(InvestmentProduct).filter_by(identifier=ticker).first()
                if not product:
                    logger.error(f"Product '{ticker}' not found")
                    return False
                
                # Check if holding already exists
                existing = session.query(PortfolioHolding).filter_by(
                    portfolio_id=portfolio.id,
                    product_id=product.id
                ).first()
                
                if existing:
                    # Update existing holding
                    existing.quantity += quantity
                    logger.info(f"Updated holding: {ticker} in {portfolio_name}")
                else:
                    # Create new holding
                    holding = PortfolioHolding(
                        portfolio_id=portfolio.id,
                        product_id=product.id,
                        quantity=quantity,
                        entry_price=entry_price,
                        entry_date=entry_date or date.today()
                    )
                    session.add(holding)
                    logger.info(f"Added holding: {ticker} to {portfolio_name}")
                
                return True
                
        except Exception as e:
            logger.error(f"Error adding holding: {e}")
            return False
    
    def get_portfolio(self, portfolio_name):
        """
        Get portfolio with all holdings
        
        Returns:
            DataFrame with holdings or None
        """
        try:
            session = get_session()
            
            portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
            if not portfolio:
                session.close()
                return None
            
            holdings = session.query(PortfolioHolding).filter_by(
                portfolio_id=portfolio.id
            ).all()
            
            if not holdings:
                session.close()
                return pd.DataFrame()
            
            data = []
            for holding in holdings:
                product = holding.product
                data.append({
                    'Ticker': product.identifier,
                    'Name': product.name,
                    'Type': product.product_type.title(),
                    'Quantity': holding.quantity,
                    'Entry Price': holding.entry_price,
                    'Entry Date': holding.entry_date,
                    'Cost Basis': holding.quantity * holding.entry_price,
                    'Category': product.category
                })
            
            session.close()
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            return None
    
    def list_portfolios(self):
        """Get list of all portfolios"""
        try:
            session = get_session()
            portfolios = session.query(Portfolio).filter_by(is_active=True).all()
            
            data = [{
                'Name': p.name,
                'Description': p.description or '',
                'Created': p.created_date,
                'Holdings': len(p.holdings)
            } for p in portfolios]
            
            session.close()
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error listing portfolios: {e}")
            return pd.DataFrame()
    
    def delete_portfolio(self, portfolio_name):
        """Delete a portfolio"""
        try:
            with get_db_session() as session:
                portfolio = session.query(Portfolio).filter_by(name=portfolio_name).first()
                if portfolio:
                    session.delete(portfolio)
                    logger.info(f"Deleted portfolio: {portfolio_name}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting portfolio: {e}")
            return False
    
    def get_portfolio_summary(self, portfolio_name):
        """
        Get portfolio summary statistics
        
        Returns:
            Dict with summary stats
        """
        holdings_df = self.get_portfolio(portfolio_name)
        
        if holdings_df is None or holdings_df.empty:
            return None
        
        total_value = holdings_df['Cost Basis'].sum()
        
        # Group by type
        by_type = holdings_df.groupby('Type')['Cost Basis'].sum()
        type_allocation = (by_type / total_value * 100).round(2)
        
        # Group by category
        by_category = holdings_df.groupby('Category')['Cost Basis'].sum()
        category_allocation = (by_category / total_value * 100).round(2)
        
        return {
            'total_value': total_value,
            'num_holdings': len(holdings_df),
            'by_type': type_allocation.to_dict(),
            'by_category': category_allocation.to_dict()
        }