"""Tests for currency conversion functionality."""

import pytest
from pathlib import Path
import tempfile
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from ccusage.currency.detector import LocaleDetector, LocaleInfo
from ccusage.currency.cache import ExchangeRateCache
from ccusage.currency.fetcher import ExchangeRateFetcher
from ccusage.currency.converter import CurrencyConverter, CurrencyMode
from ccusage.models.base import format_currency
from ccusage.core.result import unwrap


class TestLocaleDetector:
    """Tests for locale detection and currency mapping."""
    
    def test_detect_locale_uk_english(self):
        """Test detection of UK English locale."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', return_value=('en_GB', 'UTF-8')):
            locale_info = detector.detect_locale()
            
            assert locale_info.language == 'en'
            assert locale_info.country == 'GB'
            assert locale_info.currency_code == 'GBP'
            assert locale_info.currency_symbol == '£'
    
    def test_detect_locale_us_english(self):
        """Test detection of US English locale."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', return_value=('en_US', 'UTF-8')):
            locale_info = detector.detect_locale()
            
            assert locale_info.language == 'en'
            assert locale_info.country == 'US'
            assert locale_info.currency_code == 'USD'
            assert locale_info.currency_symbol == '$'
    
    def test_detect_locale_fallback(self):
        """Test fallback to USD when locale detection fails."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', return_value=(None, None)):
            locale_info = detector.detect_locale()
            
            assert locale_info.language == 'en'
            assert locale_info.country is None
            assert locale_info.currency_code == 'USD'
            assert locale_info.currency_symbol == '$'
    
    def test_get_currency_for_locale(self):
        """Test direct currency lookup for specific locales."""
        detector = LocaleDetector()
        
        # Test various locales
        assert detector.get_currency_for_locale('en_GB') == ('GBP', '£')
        assert detector.get_currency_for_locale('de_DE') == ('EUR', '€')
        assert detector.get_currency_for_locale('ja_JP') == ('JPY', '¥')
        assert detector.get_currency_for_locale('invalid') == ('USD', '$')


class TestExchangeRateCache:
    """Tests for exchange rate caching."""
    
    def test_cache_basic_operations(self):
        """Test basic cache operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Test setting and getting rates
            cache.set_rate('USD', 'GBP', 0.79)
            result = cache.get_rate('USD', 'GBP')
            
            assert result is not None
            rate, timestamp, is_stale = result
            assert rate == 0.79
            assert not is_stale
    
    def test_cache_reverse_lookup(self):
        """Test reverse rate lookup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Set GBP to USD rate
            cache.set_rate('GBP', 'USD', 1.27)
            
            # Should be able to get USD to GBP by inverse
            result = cache.get_rate('USD', 'GBP')
            
            assert result is not None
            rate, timestamp, is_stale = result
            assert abs(rate - (1.0 / 1.27)) < 0.001
    
    def test_same_currency_rate(self):
        """Test that same currency returns rate of 1.0."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            result = cache.get_rate('USD', 'USD')
            
            assert result is not None
            rate, timestamp, is_stale = result
            assert rate == 1.0
            assert not is_stale


@pytest.mark.asyncio
class TestExchangeRateFetcher:
    """Tests for exchange rate fetching."""
    
    async def test_same_currency_fetch(self):
        """Test fetching rate for same currency."""
        async with ExchangeRateFetcher() as fetcher:
            result = await fetcher.fetch_rate('USD', 'USD')
            
            assert result.is_ok()
            assert unwrap(result) == 1.0
    
    async def test_embedded_rate_fallback(self):
        """Test fallback to embedded rates."""
        async with ExchangeRateFetcher() as fetcher:
            # This should use the embedded fallback rates
            result = fetcher._get_embedded_rate('USD', 'GBP')
            
            assert result.is_ok()
            rate = unwrap(result)
            assert 0.7 < rate < 0.9  # Reasonable range for USD to GBP


@pytest.mark.asyncio 
class TestCurrencyConverter:
    """Tests for the main currency converter."""
    
    async def test_converter_auto_mode(self):
        """Test currency converter in auto mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            
            with patch('locale.getlocale', return_value=('en_GB', 'UTF-8')):
                async with CurrencyConverter(cache_dir, CurrencyMode.AUTO) as converter:
                    currency_code = converter.get_currency_code()
                    currency_symbol = converter.get_currency_symbol()
                    
                    assert currency_code == 'GBP'
                    assert currency_symbol == '£'
    
    async def test_converter_custom_mode(self):
        """Test currency converter in custom mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            
            async with CurrencyConverter(cache_dir, CurrencyMode.CUSTOM, 'EUR') as converter:
                currency_code = converter.get_currency_code()
                currency_symbol = converter.get_currency_symbol()
                
                assert currency_code == 'EUR'
                assert currency_symbol == '€'
    
    async def test_converter_usd_only_mode(self):
        """Test currency converter in USD only mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            
            async with CurrencyConverter(cache_dir, CurrencyMode.USD_ONLY) as converter:
                currency_code = converter.get_currency_code()
                currency_symbol = converter.get_currency_symbol()
                
                assert currency_code == 'USD'
                assert currency_symbol == '$'
    
    async def test_amount_conversion_same_currency(self):
        """Test converting amount with same currency."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            
            async with CurrencyConverter(cache_dir, CurrencyMode.USD_ONLY) as converter:
                result = await converter.convert_amount(100.0, 'USD')
                
                assert result.is_ok()
                assert unwrap(result) == 100.0


class TestFormatCurrency:
    """Tests for currency formatting function."""
    
    def test_format_usd(self):
        """Test formatting USD amounts."""
        assert format_currency(1.23, 'USD', '$') == '$1.23'
        assert format_currency(1234.56, 'USD', '$') == '$1,234.56'
        assert format_currency(0.0, 'USD', '$') == '$0.00'
    
    def test_format_gbp(self):
        """Test formatting GBP amounts.""" 
        assert format_currency(1.23, 'GBP', '£') == '£1.23'
        assert format_currency(1234.56, 'GBP', '£') == '£1,234.56'
    
    def test_format_eur(self):
        """Test formatting EUR amounts."""
        assert format_currency(1.23, 'EUR', '€') == '€1.23'
        assert format_currency(1234.56, 'EUR', '€') == '€1,234.56'
    
    def test_format_jpy(self):
        """Test formatting JPY amounts (no decimal places)."""
        assert format_currency(123, 'JPY', '¥') == '¥123'
        assert format_currency(1234.56, 'JPY', '¥') == '¥1,235'
        assert format_currency(1234, 'JPY', '¥') == '¥1,234'
    
    def test_format_krw(self):
        """Test formatting KRW amounts (no decimal places)."""
        assert format_currency(1234.56, 'KRW', '₩') == '₩1,235'
        assert format_currency(1234, 'KRW', '₩') == '₩1,234'