"""
SQLAlchemy database models for SA Investment Analyzer
"""
from sqlalchemy import (
    Column, Integer, String, Float, Date, ForeignKey,
    JSON, Boolean, DateTime, Text, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class InvestmentProduct(Base):
    """Master table for all investment products"""
    __tablename__ = 'investment_products'
    
    id = Column(Integer, primary_key=True)
    product_type = Column(String(50), index=True)
    identifier = Column(String(50), unique=True, index=True)
    name = Column(String(200))
    provider = Column(String(100), index=True)
    category = Column(String(100), index=True)
    currency = Column(String(3), default='ZAR')
    
    has_api_data = Column(Boolean, default=False)
    requires_scraping = Column(Boolean, default=False)
    manual_entry = Column(Boolean, default=False)
    
    primary_data_source = Column(String(50))
    last_updated = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prices = relationship("Price", back_populates="product", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_product_type_category', 'product_type', 'category'),
    )


class Price(Base):
    """Price history for all products"""
    __tablename__ = 'prices'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('investment_products.id'), index=True)
    date = Column(Date, index=True)
    
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    nav = Column(Float, nullable=True)
    
    source = Column(String(50))
    is_estimated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("InvestmentProduct", back_populates="prices")
    
    __table_args__ = (
        Index('idx_product_date', 'product_id', 'date', unique=True),
    )


class Portfolio(Base):
    """Saved portfolio configurations"""
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(Text)
    created_date = Column(Date, default=lambda: datetime.utcnow().date())
    base_currency = Column(String(3), default='ZAR')
    is_active = Column(Boolean, default=True)
    
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")


class PortfolioHolding(Base):
    """Individual holdings within a portfolio"""
    __tablename__ = 'portfolio_holdings'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), index=True)
    product_id = Column(Integer, ForeignKey('investment_products.id'), index=True)
    
    quantity = Column(Float)
    entry_price = Column(Float)
    entry_date = Column(Date)
    
    portfolio = relationship("Portfolio", back_populates="holdings")
    product = relationship("InvestmentProduct")