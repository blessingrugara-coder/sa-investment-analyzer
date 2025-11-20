"""Helper functions"""


def convert_zac_to_zar(amount: float) -> float:
    """Convert ZAc (cents) to ZAR"""
    return amount / 100.0


def clean_ticker(ticker: str) -> str:
    """Clean ticker symbol"""
    ticker = ticker.strip().upper()
    if not any(ticker.endswith(s) for s in ['.JO', '.L']):
        ticker = f"{ticker}.JO"
    return ticker


def format_currency(amount: float, currency: str = 'ZAR') -> str:
    """Format currency"""
    if currency == 'ZAR':
        return f"R {amount:,.2f}"
    return f"{currency} {amount:,.2f}"