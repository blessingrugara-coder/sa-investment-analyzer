"""
Price Fetcher - Fetch market data from various sources
Supports yfinance for JSE stocks, ETFs, and FX
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
import logging
from pathlib import Path
import time

from database.session import get_session
from database.models import InvestmentProduct, Price, AssetClass

logger = logging.getLogger(__name__)


class PriceFetcher:
    """
    Fetch and store market prices from various sources
    Primary: yfinance for JSE, FX, and global assets
    """
    
    def __init__(self):
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = None
    
    def fetch_current_price(self, ticker: str) -> Optional[float]:
        """
        Fetch current price for a single ticker
        
        Args:
            ticker: Ticker symbol (e.g., 'NPN.JO', 'USDZAR=X')
            
        Returns:
            Current price or None if failed
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Try to get current price
            info = stock.info
            
            # Try different price fields
            price = None
            for field in ['currentPrice', 'regularMarketPrice', 'previousClose', 'ask', 'bid']:
                if field in info and info[field]:
                    price = float(info[field])
                    break
            
            if price:
                # Convert ZAc to ZAR for JSE stocks (divide by 100)
                if ticker.endswith('.JO'):
                    price = price / 100.0
                
                logger.info(f"Fetched current price for {ticker}: {price}")
                return price
            
            # Fallback: get latest from history
            hist = stock.history(period='1d')
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
                
                # Convert ZAc to ZAR for JSE stocks
                if ticker.endswith('.JO'):
                    price = price / 100.0
                
                logger.info(f"Fetched price from history for {ticker}: {price}")
                return price
            
            logger.warning(f"No price data available for {ticker}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {e}")
            return None
    
    def fetch_historical_prices(self, ticker: str, 
                                start_date: Optional[date] = None,
                                end_date: Optional[date] = None,
                                period: str = '5y') -> pd.DataFrame:
        """
        Fetch historical prices for a ticker
        
        Args:
            ticker: Ticker symbol
            start_date: Start date (optional)
            end_date: End date (optional)
            period: Period string if dates not provided ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            stock = yf.Ticker(ticker)
            
            if start_date and end_date:
                hist = stock.history(start=start_date, end=end_date)
            else:
                hist = stock.history(period=period)
            
            if hist.empty:
                logger.warning(f"No historical data for {ticker}")
                return pd.DataFrame()
            
            # Rename columns to match our schema
            hist = hist.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Add adjusted close if available
            if 'Adj Close' in hist.columns:
                hist['adjusted_close'] = hist['Adj Close']
            
            logger.info(f"Fetched {len(hist)} historical prices for {ticker}")
            return hist
            
        except Exception as e:
            logger.error(f"Error fetching historical prices for {ticker}: {e}")
            return pd.DataFrame()
    
    def store_prices(self, product_id: int, prices_df: pd.DataFrame, 
                    source: str = 'yfinance') -> int:
        """
        Store prices in database
        
        Args:
            product_id: Product ID
            prices_df: DataFrame with price data
            source: Data source name
            
        Returns:
            Number of prices stored
        """
        if prices_df.empty:
            return 0
        
        session = get_session()
        stored_count = 0
        
        try:
            for date_index, row in prices_df.iterrows():
                price_date = date_index.date()
                
                # Check if price already exists
                existing = session.query(Price).filter_by(
                    product_id=product_id,
                    date=price_date
                ).first()
                
                if existing:
                    # Update existing
                    existing.open = row.get('open')
                    existing.high = row.get('high')
                    existing.low = row.get('low')
                    existing.close = row.get('close')
                    existing.volume = row.get('volume')
                    existing.adjusted_close = row.get('adjusted_close')
                    existing.source = source
                else:
                    # Create new
                    price = Price(
                        product_id=product_id,
                        date=price_date,
                        open=row.get('open'),
                        high=row.get('high'),
                        low=row.get('low'),
                        close=row.get('close'),
                        volume=row.get('volume'),
                        adjusted_close=row.get('adjusted_close'),
                        source=source
                    )
                    session.add(price)
                
                stored_count += 1
            
            session.commit()
            logger.info(f"Stored {stored_count} prices for product {product_id}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing prices: {e}")
            stored_count = 0
        finally:
            session.close()
        
        return stored_count
    
    def update_product_prices(self, product_id: int, period: str = '1y') -> bool:
        """
        Update prices for a single product
        
        Args:
            product_id: Product ID
            period: How much history to fetch
            
        Returns:
            True if successful
        """
        session = get_session()
        
        try:
            product = session.query(InvestmentProduct).get(product_id)
            if not product:
                logger.error(f"Product {product_id} not found")
                session.close()
                return False
            
            if not product.has_api_data:
                logger.info(f"Product {product.identifier} does not have API data")
                session.close()
                return False
            
            # Fetch prices
            logger.info(f"Fetching prices for {product.identifier}")
            prices_df = self.fetch_historical_prices(product.identifier, period=period)
            
            if prices_df.empty:
                logger.warning(f"No prices fetched for {product.identifier}")
                session.close()
                return False
            
            # Store prices
            stored = self.store_prices(product.id, prices_df)
            
            # Update last_updated
            product.last_updated = date.today()
            session.commit()
            
            logger.info(f"Updated {stored} prices for {product.identifier}")
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating prices for product {product_id}: {e}")
            session.close()
            return False
    
    def update_all_products(self, delay_seconds: float = 1.0) -> Dict:
        """
        Update prices for all products with API data
        
        Args:
            delay_seconds: Delay between requests to avoid rate limiting
            
        Returns:
            Dict with update statistics
        """
        session = get_session()
        
        # Get products with API data
        products = session.query(InvestmentProduct).filter_by(
            has_api_data=True
        ).all()
        
        session.close()
        
        if not products:
            logger.warning("No products with API data to update")
            return {'total': 0, 'success': 0, 'failed': 0}
        
        logger.info(f"Updating prices for {len(products)} products")
        
        success_count = 0
        failed_count = 0
        
        for product in products:
            try:
                success = self.update_product_prices(product.id)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                
                # Rate limiting
                time.sleep(delay_seconds)
                
            except Exception as e:
                logger.error(f"Error updating {product.identifier}: {e}")
                failed_count += 1
        
        stats = {
            'total': len(products),
            'success': success_count,
            'failed': failed_count
        }
        
        logger.info(f"Update complete: {success_count} success, {failed_count} failed")
        return stats
    
    def get_latest_price(self, product_id: int) -> Optional[float]:
        """
        Get latest price from database
        
        Args:
            product_id: Product ID
            
        Returns:
            Latest close price or None
        """
        session = get_session()
        
        try:
            latest = session.query(Price).filter_by(
                product_id=product_id
            ).order_by(Price.date.desc()).first()
            
            session.close()
            
            if latest:
                return latest.close
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest price: {e}")
            session.close()
            return None
    
    def get_price_at_date(self, product_id: int, target_date: date) -> Optional[float]:
        """
        Get price on specific date (or nearest prior date)
        
        Args:
            product_id: Product ID
            target_date: Target date
            
        Returns:
            Close price or None
        """
        session = get_session()
        
        try:
            # Try exact date first
            price = session.query(Price).filter_by(
                product_id=product_id,
                date=target_date
            ).first()
            
            if price:
                session.close()
                return price.close
            
            # Get nearest prior date
            price = session.query(Price).filter(
                Price.product_id == product_id,
                Price.date <= target_date
            ).order_by(Price.date.desc()).first()
            
            session.close()
            
            if price:
                return price.close
            return None
            
        except Exception as e:
            logger.error(f"Error getting price at date: {e}")
            session.close()
            return None
    
    def get_price_series(self, product_id: int,
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None) -> pd.Series:
        """
        Get price series for a product
        
        Args:
            product_id: Product ID
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            Series with dates as index, close prices as values
        """
        session = get_session()
        
        try:
            query = session.query(Price).filter_by(product_id=product_id)
            
            if start_date:
                query = query.filter(Price.date >= start_date)
            if end_date:
                query = query.filter(Price.date <= end_date)
            
            prices = query.order_by(Price.date).all()
            
            session.close()
            
            if not prices:
                return pd.Series(dtype=float)
            
            data = {pd.Timestamp(p.date): p.close for p in prices}
            return pd.Series(data).sort_index()
            
        except Exception as e:
            logger.error(f"Error getting price series: {e}")
            session.close()
            return pd.Series(dtype=float)
    
    def check_data_availability(self, ticker: str) -> Dict:
        """
        Check if data is available for a ticker
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Dict with availability info
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='5d')
            
            return {
                'ticker': ticker,
                'available': not hist.empty,
                'has_info': bool(info),
                'latest_date': hist.index[-1].date() if not hist.empty else None,
                'num_fields': len(info) if info else 0
            }
            
        except Exception as e:
            return {
                'ticker': ticker,
                'available': False,
                'error': str(e)
            }