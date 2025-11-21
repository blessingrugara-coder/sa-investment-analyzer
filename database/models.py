"""
SQLAlchemy database models for SA Investment Analyzer
Updated with Transaction Ledger System
"""
from sqlalchemy import (
    Column, Integer, String, Float, Date, ForeignKey,
    JSON, Boolean, DateTime, Text, Index, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class AssetClass(enum.Enum):
    """Asset class enumeration"""
    EQUITY = "equity"
    ETF = "etf"
    BOND = "bond"
    UNIT_TRUST = "unit_trust"
    PROPERTY = "property"
    COMMODITY = "commodity"
    CRYPTO = "crypto"
    FX = "fx"
    MONEY_MARKET = "money_market"
    BANK_ACCOUNT = "bank_account"
    INDEX = "index"
    OTHER = "other"


class TransactionType(enum.Enum):
    """Transaction type enumeration"""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    FEE = "fee"
    TAX = "tax"
    SPLIT = "split"
    BONUS = "bonus"
    RIGHTS = "rights"
    COUPON = "coupon"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    OTHER = "other"


class CalculationMethod(enum.Enum):
    """Calculation method for recurring transactions"""
    PER_SHARE = "per_share"
    PER_UNIT = "per_unit"
    PERCENTAGE_NAV = "percentage_nav"
    PERCENTAGE_VALUE = "percentage_value"
    PERCENTAGE_COST = "percentage_cost"
    FIXED_AMOUNT = "fixed_amount"


class Frequency(enum.Enum):
    """Frequency enumeration"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    CUSTOM = "custom"


class InvestmentProduct(Base):
    """Master table for all investment products"""
    __tablename__ = 'investment_products'

    id = Column(Integer, primary_key=True)
    product_type = Column(String(50), index=True)  # Legacy field
    asset_class = Column(Enum(AssetClass), index=True)  # New structured field
    identifier = Column(String(50), unique=True, index=True)
    name = Column(String(200))
    provider = Column(String(100), index=True)
    category = Column(String(100), index=True)
    currency = Column(String(3), default='ZAR')

    # Data availability flags
    has_api_data = Column(Boolean, default=False)
    requires_scraping = Column(Boolean, default=False)
    manual_entry = Column(Boolean, default=False)

    # Metadata
    primary_data_source = Column(String(50))
    last_updated = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Additional product details (JSON for flexibility)
    details = Column(JSON, nullable=True)  # e.g., {"isin": "...", "sector": "..."}

    # Relationships
    prices = relationship("Price", back_populates="product", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="product")
    holdings = relationship("PortfolioHolding", back_populates="product")

    __table_args__ = (
        Index('idx_asset_class_category', 'asset_class', 'category'),
    )


class Price(Base):
    """Price history for all products"""
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('investment_products.id'), index=True)
    date = Column(Date, index=True)

    # OHLCV data
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)

    # Additional fields
    nav = Column(Float, nullable=True)  # For funds
    adjusted_close = Column(Float, nullable=True)  # Split/dividend adjusted

    # Metadata
    source = Column(String(50))
    is_estimated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
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

    # Relationships
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")
    cash_pools = relationship("CashPool", back_populates="portfolio", cascade="all, delete-orphan")
    recurring_rules = relationship("RecurringTransactionRule", back_populates="portfolio", cascade="all, delete-orphan")


class PortfolioHolding(Base):
    """
    Individual holdings within a portfolio
    LEGACY TABLE - Kept for backward compatibility
    New system uses Transaction ledger for holdings calculation
    """
    __tablename__ = 'portfolio_holdings'

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), index=True)
    product_id = Column(Integer, ForeignKey('investment_products.id'), index=True)

    quantity = Column(Float)
    entry_price = Column(Float)
    entry_date = Column(Date)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    product = relationship("InvestmentProduct", back_populates="holdings")


class Transaction(Base):
    """
    Transaction ledger - single source of truth for all portfolio events
    Every financial event is logged here
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), index=True)
    product_id = Column(Integer, ForeignKey('investment_products.id'), index=True, nullable=True)
    cash_pool_id = Column(Integer, ForeignKey('cash_pools.id'), nullable=True)

    # Transaction classification
    transaction_type = Column(Enum(TransactionType), index=True)
    transaction_date = Column(Date, index=True)
    settlement_date = Column(Date, nullable=True)  # For T+3 settlement

    # Quantity and pricing
    quantity = Column(Float, nullable=True)  # Positive for buy, negative for sell
    price = Column(Float, nullable=True)  # Price per unit

    # Financial amounts (all in portfolio base currency)
    gross_amount = Column(Float)  # quantity * price (before fees)
    fees = Column(Float, default=0.0)  # Brokerage, exchange fees
    taxes = Column(Float, default=0.0)  # Capital gains tax, dividend tax
    net_amount = Column(Float)  # Final amount (gross ± fees ± taxes)

    # Dividend/Interest specific fields
    dividend_per_share = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)

    # Corporate actions
    split_ratio = Column(Float, nullable=True)  # e.g., 2.0 for 2-for-1 split

    # FX specific
    exchange_rate = Column(Float, nullable=True)
    foreign_currency = Column(String(3), nullable=True)
    foreign_amount = Column(Float, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    reference_number = Column(String(50), nullable=True)  # Broker reference
    is_auto_generated = Column(Boolean, default=False)  # From recurring rules
    currency = Column(String(3), default='ZAR')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    product = relationship("InvestmentProduct", back_populates="transactions")
    cash_pool = relationship("CashPool", back_populates="transactions")

    __table_args__ = (
        Index('idx_portfolio_date', 'portfolio_id', 'transaction_date'),
        Index('idx_portfolio_type', 'portfolio_id', 'transaction_type'),
        Index('idx_product_date', 'product_id', 'transaction_date'),
    )


class CashPool(Base):
    """
    Track cash positions within portfolio
    Receives dividends, interest, sale proceeds
    Pays for purchases, fees
    """
    __tablename__ = 'cash_pools'

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), index=True)

    name = Column(String(100))  # e.g., "Main Cash Account", "USD Cash"
    currency = Column(String(3), default='ZAR')
    account_type = Column(String(50), nullable=True)  # CHECKING, SAVINGS, MONEY_MARKET

    # Balance tracking (calculated from transactions)
    current_balance = Column(Float, default=0.0)

    # Interest on cash
    interest_rate = Column(Float, nullable=True)  # Annual rate

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="cash_pools")
    transactions = relationship("Transaction", back_populates="cash_pool")

    __table_args__ = (
        Index('idx_portfolio_currency', 'portfolio_id', 'currency'),
    )


class RecurringTransactionRule(Base):
    """
    Generic rules for any recurring transaction event
    Handles dividends, coupons, fees, subscriptions, interest, etc.
    """
    __tablename__ = 'recurring_transaction_rules'

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), index=True)
    product_id = Column(Integer, ForeignKey('investment_products.id'), index=True, nullable=True)
    cash_pool_id = Column(Integer, ForeignKey('cash_pools.id'), nullable=True)

    # Rule identification
    rule_name = Column(String(100))  # e.g., "NPN Quarterly Dividend"
    rule_type = Column(String(50))  # DIVIDEND, COUPON, FEE, INTEREST, SUBSCRIPTION

    # Transaction details
    transaction_type = Column(Enum(TransactionType))  # What transaction to create

    # Amount calculation
    calculation_method = Column(Enum(CalculationMethod))
    amount_value = Column(Float)  # The number used in calculation

    # For per-share/per-unit calculations
    applies_to_quantity = Column(Boolean, default=True)  # Multiply by holdings?

    # For percentage-based (e.g., management fees)
    percentage_basis = Column(String(50), nullable=True)  # NAV, MARKET_VALUE, COST_BASIS

    # Scheduling
    frequency = Column(Enum(Frequency))
    custom_frequency_days = Column(Integer, nullable=True)  # For CUSTOM frequency
    next_execution_date = Column(Date, index=True)
    last_execution_date = Column(Date, nullable=True)

    # Dividend reinvestment (DRIP)
    is_reinvested = Column(Boolean, default=False)  # Auto-buy more shares?
    reinvestment_product_id = Column(Integer, ForeignKey('investment_products.id'), nullable=True)

    # Tax treatment
    tax_rate = Column(Float, nullable=True)  # e.g., 0.20 for 20% dividend tax
    is_tax_deductible = Column(Boolean, default=False)  # For fees/expenses

    # Cash pool integration
    affects_cash_pool = Column(Boolean, default=True)  # Does this add/remove cash?

    # Rule lifecycle
    is_active = Column(Boolean, default=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)  # For finite rules

    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="recurring_rules")
    product = relationship("InvestmentProduct", foreign_keys=[product_id])
    reinvestment_product = relationship("InvestmentProduct", foreign_keys=[reinvestment_product_id])
    cash_pool = relationship("CashPool")

    __table_args__ = (
        Index('idx_portfolio_active', 'portfolio_id', 'is_active'),
        Index('idx_next_execution', 'next_execution_date', 'is_active'),
    )


class BenchmarkIndex(Base):
    """
    Benchmark indices for performance comparison
    """
    __tablename__ = 'benchmark_indices'

    id = Column(Integer, primary_key=True)
    ticker = Column(String(50), unique=True, index=True)
    name = Column(String(200))
    description = Column(Text, nullable=True)
    currency = Column(String(3), default='ZAR')

    # Data source
    data_source = Column(String(50))  # yfinance, openbb, manual

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)