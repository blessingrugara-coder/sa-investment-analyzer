"""
Event Templates - Pre-configured recurring transaction templates
Quick setup for common scenarios by asset class
"""
from datetime import date
from typing import Dict

from database.models import TransactionType, CalculationMethod, Frequency


class EventTemplates:
    """
    Pre-configured templates for common recurring events by asset class
    """
    
    @staticmethod
    def stock_dividend(portfolio_id: int, product_id: int, dividend_per_share: float,
                       frequency: str = 'QUARTERLY', tax_rate: float = 0.20, 
                       reinvest: bool = False, cash_pool_id: int = None) -> Dict:
        """
        Template: Stock dividend (cash or reinvested)
        
        Args:
            portfolio_id: Portfolio ID
            product_id: Stock product ID
            dividend_per_share: Dividend amount per share (ZAR)
            frequency: QUARTERLY, SEMI_ANNUAL, ANNUAL
            tax_rate: Dividend withholding tax rate (default 0.20 for SA)
            reinvest: Auto-reinvest dividends (DRIP)
            cash_pool_id: Cash pool to credit (if not reinvesting)
        """
        return {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'cash_pool_id': cash_pool_id if not reinvest else None,
            'rule_name': 'Dividend Payment',
            'rule_type': 'DIVIDEND',
            'transaction_type': TransactionType.DIVIDEND,
            'calculation_method': CalculationMethod.PER_SHARE,
            'amount_value': dividend_per_share,
            'applies_to_quantity': True,
            'frequency': Frequency[frequency.upper()],
            'is_reinvested': reinvest,
            'reinvestment_product_id': product_id if reinvest else None,
            'tax_rate': tax_rate,
            'affects_cash_pool': not reinvest,
            'is_active': True,
            'next_execution_date': date.today()
        }
    
    @staticmethod
    def bond_coupon(portfolio_id: int, product_id: int, coupon_rate: float,
                    face_value: float, frequency: str = 'SEMI_ANNUAL',
                    cash_pool_id: int = None) -> Dict:
        """
        Template: Bond coupon payment
        
        Args:
            portfolio_id: Portfolio ID
            product_id: Bond product ID
            coupon_rate: Annual coupon rate (e.g., 0.085 for 8.5%)
            face_value: Face value per bond
            frequency: SEMI_ANNUAL, ANNUAL
            cash_pool_id: Cash pool to credit
        """
        # Calculate coupon per payment period
        payments_per_year = 2 if frequency.upper() == 'SEMI_ANNUAL' else 1
        coupon_per_payment = (face_value * coupon_rate) / payments_per_year
        
        return {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'cash_pool_id': cash_pool_id,
            'rule_name': 'Bond Coupon',
            'rule_type': 'COUPON',
            'transaction_type': TransactionType.COUPON,
            'calculation_method': CalculationMethod.PER_UNIT,
            'amount_value': coupon_per_payment,
            'applies_to_quantity': True,
            'frequency': Frequency[frequency.upper()],
            'affects_cash_pool': True,
            'is_active': True,
            'next_execution_date': date.today()
        }
    
    @staticmethod
    def unit_trust_management_fee(portfolio_id: int, product_id: int, 
                                   annual_fee_pct: float) -> Dict:
        """
        Template: Unit trust/mutual fund management fee
        
        Args:
            portfolio_id: Portfolio ID
            product_id: Fund product ID
            annual_fee_pct: Annual fee percentage (e.g., 1.5 for 1.5%)
        """
        return {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'cash_pool_id': None,  # Usually deducted from NAV
            'rule_name': 'Management Fee',
            'rule_type': 'MANAGEMENT_FEE',
            'transaction_type': TransactionType.FEE,
            'calculation_method': CalculationMethod.PERCENTAGE_NAV,
            'amount_value': annual_fee_pct,
            'percentage_basis': 'NAV',
            'applies_to_quantity': False,
            'frequency': Frequency.ANNUAL,
            'is_tax_deductible': False,
            'affects_cash_pool': False,  # Deducted from NAV
            'is_active': True,
            'next_execution_date': date.today()
        }
    
    @staticmethod
    def etf_management_fee(portfolio_id: int, product_id: int, ter_pct: float) -> Dict:
        """
        Template: ETF Total Expense Ratio (TER)
        
        Args:
            portfolio_id: Portfolio ID
            product_id: ETF product ID
            ter_pct: Total expense ratio percentage (e.g., 0.35 for 0.35%)
        """
        return {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'cash_pool_id': None,
            'rule_name': 'ETF TER',
            'rule_type': 'MANAGEMENT_FEE',
            'transaction_type': TransactionType.FEE,
            'calculation_method': CalculationMethod.PERCENTAGE_VALUE,
            'amount_value': ter_pct,
            'percentage_basis': 'MARKET_VALUE',
            'applies_to_quantity': False,
            'frequency': Frequency.ANNUAL,
            'affects_cash_pool': False,
            'is_active': True,
            'next_execution_date': date.today()
        }
    
    @staticmethod
    def platform_subscription(portfolio_id: int, monthly_fee: float,
                             cash_pool_id: int = None) -> Dict:
        """
        Template: Platform/brokerage subscription fee
        
        Args:
            portfolio_id: Portfolio ID
            monthly_fee: Monthly subscription amount
            cash_pool_id: Cash pool to debit
        """
        return {
            'portfolio_id': portfolio_id,
            'product_id': None,  # Portfolio-level, not product-specific
            'cash_pool_id': cash_pool_id,
            'rule_name': 'Platform Fee',
            'rule_type': 'SUBSCRIPTION',
            'transaction_type': TransactionType.FEE,
            'calculation_method': CalculationMethod.FIXED_AMOUNT,
            'amount_value': monthly_fee,
            'applies_to_quantity': False,
            'frequency': Frequency.MONTHLY,
            'affects_cash_pool': True,
            'is_active': True,
            'next_execution_date': date.today()
        }
    
    @staticmethod
    def money_market_interest(portfolio_id: int, product_id: int, 
                             annual_rate_pct: float, tax_rate: float = 0.0,
                             cash_pool_id: int = None) -> Dict:
        """
        Template: Money market fund interest (daily accrual, paid monthly)
        
        Args:
            portfolio_id: Portfolio ID
            product_id: Money market fund product ID
            annual_rate_pct: Annual interest rate (e.g., 7.5 for 7.5%)
            tax_rate: Interest tax rate (usually 0 for money market funds)
            cash_pool_id: Cash pool to credit (if separate)
        """
        return {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'cash_pool_id': cash_pool_id,
            'rule_name': 'Money Market Interest',
            'rule_type': 'INTEREST',
            'transaction_type': TransactionType.INTEREST,
            'calculation_method': CalculationMethod.PERCENTAGE_NAV,
            'amount_value': annual_rate_pct / 12,  # Monthly rate
            'percentage_basis': 'NAV',
            'applies_to_quantity': False,
            'frequency': Frequency.MONTHLY,
            'tax_rate': tax_rate,
            'affects_cash_pool': False,  # Usually reinvested in fund
            'is_active': True,
            'next_execution_date': date.today()
        }
    
    @staticmethod
    def bank_account_interest(portfolio_id: int, product_id: int,
                             annual_rate_pct: float, tax_rate: float = 0.30,
                             cash_pool_id: int = None) -> Dict:
        """
        Template: Bank account interest income
        
        Args:
            portfolio_id: Portfolio ID
            product_id: Bank account product ID
            annual_rate_pct: Annual interest rate (e.g., 5.5 for 5.5%)
            tax_rate: Interest tax rate (default 0.30 for SA)
            cash_pool_id: Cash pool to credit
        """
        return {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'cash_pool_id': cash_pool_id,
            'rule_name': 'Bank Interest',
            'rule_type': 'INTEREST',
            'transaction_type': TransactionType.INTEREST,
            'calculation_method': CalculationMethod.PERCENTAGE_COST,
            'amount_value': annual_rate_pct / 12,  # Monthly rate
            'percentage_basis': 'COST_BASIS',
            'applies_to_quantity': False,
            'frequency': Frequency.MONTHLY,
            'tax_rate': tax_rate,
            'affects_cash_pool': True,
            'is_active': True,
            'next_execution_date': date.today()
        }
    
    @staticmethod
    def bank_account_fee(portfolio_id: int, product_id: int, monthly_fee: float,
                        cash_pool_id: int = None) -> Dict:
        """
        Template: Bank account monthly fee
        
        Args:
            portfolio_id: Portfolio ID
            product_id: Bank account product ID
            monthly_fee: Monthly account fee
            cash_pool_id: Cash pool to debit
        """
        return {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'cash_pool_id': cash_pool_id,
            'rule_name': 'Account Fee',
            'rule_type': 'FEE',
            'transaction_type': TransactionType.FEE,
            'calculation_method': CalculationMethod.FIXED_AMOUNT,
            'amount_value': monthly_fee,
            'applies_to_quantity': False,
            'frequency': Frequency.MONTHLY,
            'affects_cash_pool': True,
            'is_active': True,
            'next_execution_date': date.today()
        }
    
    @staticmethod
    def property_rental_income(portfolio_id: int, product_id: int,
                              monthly_rental: float, cash_pool_id: int = None) -> Dict:
        """
        Template: Property rental income
        
        Args:
            portfolio_id: Portfolio ID
            product_id: Property product ID
            monthly_rental: Monthly rental income
            cash_pool_id: Cash pool to credit
        """
        return {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'cash_pool_id': cash_pool_id,
            'rule_name': 'Rental Income',
            'rule_type': 'INCOME',
            'transaction_type': TransactionType.INTEREST,  # Using INTEREST as general income
            'calculation_method': CalculationMethod.FIXED_AMOUNT,
            'amount_value': monthly_rental,
            'applies_to_quantity': False,
            'frequency': Frequency.MONTHLY,
            'affects_cash_pool': True,
            'is_active': True,
            'next_execution_date': date.today()
        }
    
    @staticmethod
    def fx_carry_trade_interest(portfolio_id: int, product_id: int,
                               interest_differential_pct: float,
                               cash_pool_id: int = None) -> Dict:
        """
        Template: FX carry trade interest differential
        
        Args:
            portfolio_id: Portfolio ID
            product_id: FX pair product ID
            interest_differential_pct: Annual interest differential (e.g., 2.5 for 2.5%)
            cash_pool_id: Cash pool to credit
        """
        return {
            'portfolio_id': portfolio_id,
            'product_id': product_id,
            'cash_pool_id': cash_pool_id,
            'rule_name': 'FX Carry Interest',
            'rule_type': 'INTEREST',
            'transaction_type': TransactionType.INTEREST,
            'calculation_method': CalculationMethod.PERCENTAGE_VALUE,
            'amount_value': interest_differential_pct / 365,  # Daily rate
            'percentage_basis': 'MARKET_VALUE',
            'applies_to_quantity': False,
            'frequency': Frequency.DAILY,
            'affects_cash_pool': True,
            'is_active': True,
            'next_execution_date': date.today()
        }
    
    @staticmethod
    def get_template_list() -> list:
        """
        Get list of all available templates
        
        Returns:
            List of template names and descriptions
        """
        return [
            {
                'name': 'stock_dividend',
                'display_name': 'Stock Dividend',
                'description': 'Quarterly/annual dividends from stocks',
                'asset_classes': ['EQUITY']
            },
            {
                'name': 'bond_coupon',
                'display_name': 'Bond Coupon',
                'description': 'Semi-annual or annual coupon payments',
                'asset_classes': ['BOND']
            },
            {
                'name': 'unit_trust_management_fee',
                'display_name': 'Unit Trust Management Fee',
                'description': 'Annual management fee (% of NAV)',
                'asset_classes': ['UNIT_TRUST']
            },
            {
                'name': 'etf_management_fee',
                'display_name': 'ETF TER',
                'description': 'Total Expense Ratio',
                'asset_classes': ['ETF']
            },
            {
                'name': 'platform_subscription',
                'display_name': 'Platform Subscription',
                'description': 'Monthly platform/brokerage fee',
                'asset_classes': ['ALL']
            },
            {
                'name': 'money_market_interest',
                'display_name': 'Money Market Interest',
                'description': 'Monthly interest income',
                'asset_classes': ['MONEY_MARKET']
            },
            {
                'name': 'bank_account_interest',
                'display_name': 'Bank Account Interest',
                'description': 'Monthly interest income',
                'asset_classes': ['BANK_ACCOUNT']
            },
            {
                'name': 'bank_account_fee',
                'display_name': 'Bank Account Fee',
                'description': 'Monthly account maintenance fee',
                'asset_classes': ['BANK_ACCOUNT']
            },
            {
                'name': 'property_rental_income',
                'display_name': 'Property Rental Income',
                'description': 'Monthly rental income',
                'asset_classes': ['PROPERTY']
            },
            {
                'name': 'fx_carry_trade_interest',
                'display_name': 'FX Carry Interest',
                'description': 'Daily interest differential',
                'asset_classes': ['FX']
            }
        ]