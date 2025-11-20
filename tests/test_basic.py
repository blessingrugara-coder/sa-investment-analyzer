"""Basic tests"""
import pytest
from config.settings import settings


def test_settings():
    assert settings.database_url is not None
    assert settings.log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']


def test_imports():
    """Test core imports"""
    from database.models import InvestmentProduct, Price
    from database.session import get_session
    assert InvestmentProduct is not None
    assert Price is not None