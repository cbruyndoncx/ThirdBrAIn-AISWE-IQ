"""Comprehensive unit tests for the currency converter module."""

import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from typing import Any

import pytest

from ccusage.core.exceptions import CcusageError
from ccusage.core.result import ok, err, unwrap
from ccusage.currency.cache import ExchangeRateCache
from ccusage.currency.converter import CurrencyConverter, CurrencyMode, CurrencyConversionError
from ccusage.currency.detector import LocaleDetector, LocaleInfo
from ccusage.currency.fetcher import ExchangeRateFetcher


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
class TestCurrencyMode:
    """Tests for CurrencyMode enum."""
    
    def test_currency_mode_values(self):
        """Test that CurrencyMode enum has correct values."""
        assert CurrencyMode.AUTO.value == "auto"
        assert CurrencyMode.USD_ONLY.value == "usd_only"
        assert CurrencyMode.CUSTOM.value == "custom"
    
    def test_currency_mode_from_string(self):
        """Test creating CurrencyMode from string values."""
        assert CurrencyMode("auto") == CurrencyMode.AUTO
        assert CurrencyMode("usd_only") == CurrencyMode.USD_ONLY
        assert CurrencyMode("custom") == CurrencyMode.CUSTOM


class TestCurrencyConverter:
    """Tests for the main CurrencyConverter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self.temp_dir.name)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_init_default_params(self):
        """Test CurrencyConverter initialization with default parameters."""
        converter = CurrencyConverter(self.cache_dir)
        
        assert converter.mode == CurrencyMode.AUTO
        assert converter.custom_currency is None
        assert converter.ttl_hours == 2
        assert isinstance(converter.locale_detector, LocaleDetector)
        assert isinstance(converter.cache, ExchangeRateCache)
        assert converter._locale_info is None
        assert converter._shown_offline_warning is False
        assert converter._shown_stale_warning is False

    def test_init_custom_params(self):
        """Test CurrencyConverter initialization with custom parameters."""
        converter = CurrencyConverter(
            cache_dir=self.cache_dir,
            mode=CurrencyMode.CUSTOM,
            custom_currency="EUR",
            ttl_hours=24
        )
        
        assert converter.mode == CurrencyMode.CUSTOM
        assert converter.custom_currency == "EUR"
        assert converter.ttl_hours == 24

    def test_get_target_currency_info_usd_only(self):
        """Test get_target_currency_info in USD_ONLY mode."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.USD_ONLY)
        
        code, symbol = converter.get_target_currency_info()
        assert code == "USD"
        assert symbol == "$"

    def test_get_target_currency_info_custom_mode(self):
        """Test get_target_currency_info in CUSTOM mode."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="EUR"
        )
        
        code, symbol = converter.get_target_currency_info()
        assert code == "EUR"
        assert symbol == "€"

    def test_get_target_currency_info_custom_mode_unknown_currency(self):
        """Test get_target_currency_info in CUSTOM mode with unknown currency."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="XYZ"
        )
        
        code, symbol = converter.get_target_currency_info()
        assert code == "XYZ"
        assert symbol == "XYZ"

    def test_get_target_currency_info_custom_mode_no_currency(self):
        """Test get_target_currency_info in CUSTOM mode with no custom currency."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency=None
        )
        
        with patch.object(converter.locale_detector, 'detect_locale') as mock_detect:
            mock_detect.return_value = LocaleInfo('en', 'US', 'USD', '$')
            
            code, symbol = converter.get_target_currency_info()
            assert code == "USD"
            assert symbol == "$"

    def test_get_target_currency_info_auto_mode(self):
        """Test get_target_currency_info in AUTO mode."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.AUTO)
        
        with patch.object(converter.locale_detector, 'detect_locale') as mock_detect:
            mock_detect.return_value = LocaleInfo('en', 'GB', 'GBP', '£')
            
            code, symbol = converter.get_target_currency_info()
            assert code == "GBP"
            assert symbol == "£"
            
            # Should cache the locale info
            assert converter._locale_info is not None
            assert converter._locale_info.currency_code == 'GBP'
            
            # Second call should use cached info
            code2, symbol2 = converter.get_target_currency_info()
            assert code2 == "GBP"
            assert symbol2 == "£"
            
            # Should only call detect_locale once due to caching
            mock_detect.assert_called_once()

    def test_get_currency_symbol_known_currencies(self):
        """Test _get_currency_symbol for known currencies."""
        converter = CurrencyConverter(self.cache_dir)
        
        test_cases = [
            ('USD', ('USD', '$')),
            ('GBP', ('GBP', '£')),
            ('EUR', ('EUR', '€')),
            ('JPY', ('JPY', '¥')),
            ('CNY', ('CNY', '¥')),
            ('CAD', ('CAD', 'C$')),
            ('AUD', ('AUD', 'A$')),
            ('NZD', ('NZD', 'NZ$')),
            ('CHF', ('CHF', 'CHF')),
            ('SEK', ('SEK', 'kr')),
            ('NOK', ('NOK', 'kr')),
            ('DKK', ('DKK', 'kr')),
            ('PLN', ('PLN', 'zł')),
            ('CZK', ('CZK', 'Kč')),
            ('HUF', ('HUF', 'Ft')),
            ('RUB', ('RUB', '₽')),
            ('INR', ('INR', '₹')),
            ('BRL', ('BRL', 'R$')),
            ('MXN', ('MXN', '$')),
            ('KRW', ('KRW', '₩')),
            ('ZAR', ('ZAR', 'R')),
            ('SGD', ('SGD', 'S$')),
            ('HKD', ('HKD', 'HK$')),
        ]
        
        for currency_code, expected in test_cases:
            result = converter._get_currency_symbol(currency_code)
            assert result == expected

    def test_get_currency_symbol_unknown_currency(self):
        """Test _get_currency_symbol for unknown currencies."""
        converter = CurrencyConverter(self.cache_dir)
        
        result = converter._get_currency_symbol('XYZ')
        assert result == ('XYZ', 'XYZ')

    def test_get_currency_symbol_case_insensitive(self):
        """Test _get_currency_symbol is case insensitive."""
        converter = CurrencyConverter(self.cache_dir)
        
        result = converter._get_currency_symbol('usd')
        assert result == ('USD', '$')
        
        result = converter._get_currency_symbol('gbp')
        assert result == ('GBP', '£')

    @pytest.mark.asyncio
    async def test_convert_amount_same_currency(self):
        """Test convert_amount with same source and target currency."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.USD_ONLY)
        
        result = await converter.convert_amount(100.0, "USD")
        assert result.is_ok()
        assert unwrap(result) == 100.0

    @pytest.mark.asyncio
    async def test_convert_amount_cached_fresh_rate(self):
        """Test convert_amount with fresh cached rate."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.CUSTOM, custom_currency="GBP")
        
        # Pre-populate cache with fresh rate
        converter.cache.set_rate("USD", "GBP", 0.79)
        
        result = await converter.convert_amount(100.0, "USD")
        assert result.is_ok()
        assert unwrap(result) == 79.0

    @pytest.mark.asyncio
    async def test_convert_amount_cached_stale_rate_fetch_success(self):
        """Test convert_amount with stale cached rate but successful fresh fetch."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.CUSTOM, custom_currency="GBP")
        
        # Pre-populate cache with stale rate
        old_timestamp = datetime.now() - timedelta(hours=5)
        converter.cache._memory_cache[("USD", "GBP")] = (0.75, old_timestamp)
        
        # Mock successful fresh rate fetch
        with patch.object(converter, '_fetch_fresh_rate') as mock_fetch:
            mock_fetch.return_value = ok(0.80)
            
            result = await converter.convert_amount(100.0, "USD")
            assert result.is_ok()
            assert unwrap(result) == 80.0
            
            # Should have called fetch and updated cache
            mock_fetch.assert_called_once_with("USD", "GBP")
            fresh_rate, _, _ = converter.cache.get_rate("USD", "GBP")
            assert fresh_rate == 0.80

    @pytest.mark.asyncio
    async def test_convert_amount_cached_stale_rate_fetch_fail(self):
        """Test convert_amount with stale cached rate and failed fresh fetch."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.CUSTOM, custom_currency="GBP")
        
        # Pre-populate cache with stale rate
        old_timestamp = datetime.now() - timedelta(hours=5)
        converter.cache._memory_cache[("USD", "GBP")] = (0.75, old_timestamp)
        
        # Mock failed fresh rate fetch
        with patch.object(converter, '_fetch_fresh_rate') as mock_fetch, \
             patch('builtins.print') as mock_print:
            mock_fetch.return_value = err("Network error")
            
            result = await converter.convert_amount(100.0, "USD")
            assert result.is_ok()
            assert unwrap(result) == 75.0  # Should use stale rate
            
            # Should have shown warning
            mock_print.assert_called_once()
            args = mock_print.call_args[0]
            assert "Warning: Using cached exchange rate" in args[0]
            
            # Should not show warning on subsequent calls
            converter._shown_stale_warning = True
            await converter.convert_amount(100.0, "USD")
            assert mock_print.call_count == 1  # Still only one call

    @pytest.mark.asyncio
    async def test_convert_amount_no_cache_fetch_success(self):
        """Test convert_amount with no cached rate and successful fetch."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.CUSTOM, custom_currency="GBP")
        
        # Mock successful fresh rate fetch
        with patch.object(converter, '_fetch_fresh_rate') as mock_fetch:
            mock_fetch.return_value = ok(0.80)
            
            result = await converter.convert_amount(100.0, "USD")
            assert result.is_ok()
            assert unwrap(result) == 80.0
            
            # Should have called fetch and cached the rate
            mock_fetch.assert_called_once_with("USD", "GBP")
            fresh_rate, _, _ = converter.cache.get_rate("USD", "GBP")
            assert fresh_rate == 0.80

    @pytest.mark.asyncio
    async def test_convert_amount_no_cache_fetch_fail(self):
        """Test convert_amount with no cached rate and failed fetch."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.CUSTOM, custom_currency="GBP")
        
        # Mock failed fresh rate fetch
        with patch.object(converter, '_fetch_fresh_rate') as mock_fetch:
            mock_fetch.return_value = err("Network error")
            
            result = await converter.convert_amount(100.0, "USD")
            assert result.is_err()
            assert "Failed to get exchange rate:" in str(result.error)

    @pytest.mark.asyncio
    async def test_fetch_fresh_rate_success(self):
        """Test _fetch_fresh_rate with successful fetch."""
        converter = CurrencyConverter(self.cache_dir)
        
        mock_fetcher = AsyncMock(spec=ExchangeRateFetcher)
        mock_fetcher.__aenter__.return_value = mock_fetcher
        mock_fetcher.fetch_rate.return_value = ok(0.80)
        
        with patch('ccusage.currency.converter.ExchangeRateFetcher', return_value=mock_fetcher):
            result = await converter._fetch_fresh_rate("USD", "GBP")
            
            assert result.is_ok()
            assert unwrap(result) == 0.80
            mock_fetcher.fetch_rate.assert_called_once_with("USD", "GBP")

    @pytest.mark.asyncio
    async def test_fetch_fresh_rate_exception(self):
        """Test _fetch_fresh_rate with exception."""
        converter = CurrencyConverter(self.cache_dir)
        
        with patch('ccusage.currency.converter.ExchangeRateFetcher') as mock_fetcher_class:
            mock_fetcher_class.side_effect = Exception("Network error")
            
            result = await converter._fetch_fresh_rate("USD", "GBP")
            
            assert result.is_err()
            assert "Exchange rate fetch error: Network error" in result.error

    def test_format_amount_usd(self):
        """Test format_amount for USD."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.USD_ONLY)
        
        assert converter.format_amount(1.23) == "$1.23"
        assert converter.format_amount(1234.56) == "$1,234.56"
        assert converter.format_amount(0.0) == "$0.00"
        assert converter.format_amount(1000000.99) == "$1,000,000.99"

    def test_format_amount_gbp(self):
        """Test format_amount for GBP."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="GBP"
        )
        
        assert converter.format_amount(1.23) == "£1.23"
        assert converter.format_amount(1234.56) == "£1,234.56"

    def test_format_amount_jpy_no_decimals(self):
        """Test format_amount for JPY (no decimal places)."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="JPY"
        )
        
        assert converter.format_amount(123) == "¥123"
        assert converter.format_amount(1234.56) == "¥1,235"
        assert converter.format_amount(1234.49) == "¥1,234"

    def test_format_amount_krw_no_decimals(self):
        """Test format_amount for KRW (no decimal places)."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="KRW"
        )
        
        assert converter.format_amount(1234.56) == "₩1,235"
        assert converter.format_amount(1234) == "₩1,234"

    def test_format_amount_with_currency_code_usd(self):
        """Test format_amount with currency code for USD (should not show code)."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.USD_ONLY)
        
        # USD should not include currency code even when requested
        result = converter.format_amount(123.45, include_currency_code=True)
        assert result == "$123.45"

    def test_format_amount_with_currency_code_non_usd(self):
        """Test format_amount with currency code for non-USD currencies."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="GBP"
        )
        
        result = converter.format_amount(123.45, include_currency_code=True)
        assert result == "£123.45 (GBP)"

    def test_get_currency_code(self):
        """Test get_currency_code method."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="EUR"
        )
        
        assert converter.get_currency_code() == "EUR"

    def test_get_currency_symbol(self):
        """Test get_currency_symbol method."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="EUR"
        )
        
        assert converter.get_currency_symbol() == "€"

    def test_get_conversion_info_usd_only_mode(self):
        """Test get_conversion_info in USD_ONLY mode."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.USD_ONLY)
        
        info = converter.get_conversion_info()
        
        assert info['mode'] == 'usd_only'
        assert info['target_currency'] == 'USD'
        assert info['currency_symbol'] == '$'
        assert 'cache_stats' in info
        assert 'detected_locale' not in info
        assert 'custom_currency' not in info

    def test_get_conversion_info_custom_mode(self):
        """Test get_conversion_info in CUSTOM mode."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="EUR"
        )
        
        info = converter.get_conversion_info()
        
        assert info['mode'] == 'custom'
        assert info['target_currency'] == 'EUR'
        assert info['currency_symbol'] == '€'
        assert info['custom_currency'] == 'EUR'
        assert 'cache_stats' in info
        assert 'detected_locale' not in info

    def test_get_conversion_info_auto_mode(self):
        """Test get_conversion_info in AUTO mode."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.AUTO)
        
        with patch.object(converter.locale_detector, 'detect_locale') as mock_detect:
            mock_detect.return_value = LocaleInfo('en', 'GB', 'GBP', '£')
            
            info = converter.get_conversion_info()
            
            assert info['mode'] == 'auto'
            assert info['target_currency'] == 'GBP'
            assert info['currency_symbol'] == '£'
            assert 'cache_stats' in info
            assert 'detected_locale' in info
            assert info['detected_locale']['language'] == 'en'
            assert info['detected_locale']['country'] == 'GB'
            assert info['detected_locale']['locale_based'] is True
            assert 'custom_currency' not in info

    def test_get_conversion_info_auto_mode_cached_locale(self):
        """Test get_conversion_info in AUTO mode with cached locale info."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.AUTO)
        
        # Pre-cache locale info
        converter._locale_info = LocaleInfo('de', 'DE', 'EUR', '€')
        
        with patch.object(converter.locale_detector, 'detect_locale') as mock_detect:
            info = converter.get_conversion_info()
            
            assert info['mode'] == 'auto'
            assert info['target_currency'] == 'EUR'
            assert info['currency_symbol'] == '€'
            assert info['detected_locale']['language'] == 'de'
            assert info['detected_locale']['country'] == 'DE'
            
            # Should not call detect_locale because it's cached
            mock_detect.assert_not_called()

    def test_get_conversion_info_auto_mode_no_cached_locale(self):
        """Test get_conversion_info in AUTO mode without cached locale info."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.AUTO)
        
        # Ensure no cached locale info
        converter._locale_info = None
        
        with patch.object(converter.locale_detector, 'detect_locale') as mock_detect:
            mock_detect.return_value = LocaleInfo('fr', 'FR', 'EUR', '€')
            
            info = converter.get_conversion_info()
            
            assert info['mode'] == 'auto'
            assert info['target_currency'] == 'EUR'
            assert info['currency_symbol'] == '€'
            assert info['detected_locale']['language'] == 'fr'
            assert info['detected_locale']['country'] == 'FR'
            
            # Should call detect_locale because it's not cached
            mock_detect.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test CurrencyConverter as async context manager."""
        with patch('locale.getlocale', return_value=(None, None)):
            async with CurrencyConverter(self.cache_dir) as converter:
                assert isinstance(converter, CurrencyConverter)
                assert converter.get_currency_code() == "USD"  # Should fall back to USD

    @pytest.mark.asyncio
    async def test_convert_amount_case_insensitive_currencies(self):
        """Test convert_amount is case insensitive for currency codes."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="gbp"
        )
        
        # Mock the cache to return a rate
        converter.cache.set_rate("usd", "gbp", 0.79)
        
        result = await converter.convert_amount(100.0, "usd")
        assert result.is_ok()
        assert unwrap(result) == 79.0

    @pytest.mark.asyncio 
    async def test_convert_amount_integration_with_cache_reverse_lookup(self):
        """Test convert_amount works with cache reverse lookup."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.USD_ONLY)
        
        # Set reverse rate in cache (GBP to USD)
        converter.cache.set_rate("GBP", "USD", 1.27)
        
        # Should find USD to GBP by inverse lookup
        result = await converter.convert_amount(100.0, "GBP")
        assert result.is_ok()
        converted_amount = unwrap(result)
        # When converting GBP to USD with GBP->USD rate of 1.27, 100 GBP = 127 USD
        assert converted_amount == 127.0

    def test_cache_integration(self):
        """Test that converter properly integrates with cache."""
        converter = CurrencyConverter(self.cache_dir, ttl_hours=4)
        
        # Verify cache is created with correct parameters
        assert converter.cache.ttl_hours == 4
        assert converter.cache.cache_dir == self.cache_dir

    def test_locale_detector_integration(self):
        """Test that converter properly integrates with locale detector."""
        converter = CurrencyConverter(self.cache_dir)
        
        with patch.object(converter.locale_detector, 'detect_locale') as mock_detect:
            mock_locale = LocaleInfo('fr', 'FR', 'EUR', '€')
            mock_detect.return_value = mock_locale
            
            code, symbol = converter.get_target_currency_info()
            assert code == 'EUR'
            assert symbol == '€'

    @pytest.mark.asyncio
    async def test_error_result_without_error_attribute(self):
        """Test convert_amount handles error results without error attribute."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.CUSTOM, custom_currency="GBP")
        
        # Create a mock error result without error attribute
        class MockError:
            def is_ok(self):
                return False
            
            def __str__(self):
                return "Mock error"
        
        with patch.object(converter, '_fetch_fresh_rate') as mock_fetch:
            mock_fetch.return_value = MockError()
            
            result = await converter.convert_amount(100.0, "USD")
            assert result.is_err()
            # Should handle the case where error doesn't have error attribute
            assert "Failed to get exchange rate:" in result.error

    def test_cache_directory_creation(self):
        """Test that cache directory is created during initialization."""
        non_existent_dir = self.cache_dir / "nested" / "cache"
        assert not non_existent_dir.exists()
        
        converter = CurrencyConverter(non_existent_dir)
        assert non_existent_dir.exists()

    @pytest.mark.asyncio
    async def test_multiple_warning_suppression(self):
        """Test that warnings are only shown once."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.CUSTOM, custom_currency="GBP")
        
        # Pre-populate cache with stale rate
        old_timestamp = datetime.now() - timedelta(hours=5)
        converter.cache._memory_cache[("USD", "GBP")] = (0.75, old_timestamp)
        
        with patch.object(converter, '_fetch_fresh_rate') as mock_fetch, \
             patch('builtins.print') as mock_print:
            mock_fetch.return_value = err("Network error")
            
            # First call should show warning
            await converter.convert_amount(100.0, "USD")
            assert mock_print.call_count == 1
            
            # Second call should not show warning
            await converter.convert_amount(200.0, "USD")
            assert mock_print.call_count == 1  # Still only one call


class TestCurrencyConversionError:
    """Tests for CurrencyConversionError exception."""
    
    def test_currency_conversion_error_inheritance(self):
        """Test that CurrencyConversionError inherits from CcusageError."""
        error = CurrencyConversionError("Test error")
        assert isinstance(error, CcusageError)
        assert str(error) == "Test error"

    def test_currency_conversion_error_creation(self):
        """Test creating CurrencyConversionError with message."""
        message = "Currency conversion failed"
        error = CurrencyConversionError(message)
        assert str(error) == message


class TestCurrencyConverterIntegration:
    """Integration tests for CurrencyConverter with real components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self.temp_dir.name)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    @pytest.mark.asyncio
    async def test_end_to_end_conversion_with_cache_persistence(self):
        """Test end-to-end currency conversion with cache persistence."""
        # First converter instance
        converter1 = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="GBP"
        )
        
        # Mock successful rate fetch
        with patch.object(converter1, '_fetch_fresh_rate') as mock_fetch:
            mock_fetch.return_value = ok(0.79)
            
            result1 = await converter1.convert_amount(100.0, "USD")
            assert result1.is_ok()
            assert unwrap(result1) == 79.0
        
        # Create second converter instance (should load from cache file)
        converter2 = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="GBP"
        )
        
        # Should use cached rate without fetching
        with patch.object(converter2, '_fetch_fresh_rate') as mock_fetch2:
            result2 = await converter2.convert_amount(100.0, "USD")
            assert result2.is_ok()
            assert unwrap(result2) == 79.0
            
            # Should not have called fetch (rate was cached)
            mock_fetch2.assert_not_called()

    @pytest.mark.asyncio
    async def test_conversion_with_locale_detection(self):
        """Test conversion with real locale detection."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.AUTO)
        
        with patch('locale.getlocale', return_value=('en_GB', 'UTF-8')):
            # Should detect GBP
            assert converter.get_currency_code() == 'GBP'
            assert converter.get_currency_symbol() == '£'
            
            # Test conversion (same currency should work)
            result = await converter.convert_amount(100.0, "GBP")
            assert result.is_ok()
            assert unwrap(result) == 100.0

    def test_cache_stats_integration(self):
        """Test that cache stats are properly integrated."""
        converter = CurrencyConverter(self.cache_dir)
        
        # Add some rates to cache
        converter.cache.set_rate("USD", "GBP", 0.79)
        converter.cache.set_rate("USD", "EUR", 0.85)
        
        info = converter.get_conversion_info()
        cache_stats = info['cache_stats']
        
        assert cache_stats['total_entries'] == 2
        assert cache_stats['fresh_entries'] == 2
        assert cache_stats['stale_entries'] == 0
        assert cache_stats['cache_file_exists'] is True
        assert cache_stats['ttl_hours'] == 2

    @pytest.mark.asyncio
    async def test_format_amount_comprehensive(self):
        """Test format_amount with various currencies and amounts."""
        test_cases = [
            (CurrencyMode.USD_ONLY, None, 1234.56, "$1,234.56"),
            (CurrencyMode.CUSTOM, "GBP", 1234.56, "£1,234.56"),
            (CurrencyMode.CUSTOM, "EUR", 1234.56, "€1,234.56"),
            (CurrencyMode.CUSTOM, "JPY", 1234.56, "¥1,235"),
            (CurrencyMode.CUSTOM, "KRW", 1234.56, "₩1,235"),
            (CurrencyMode.CUSTOM, "CAD", 1234.56, "C$1,234.56"),
            (CurrencyMode.CUSTOM, "AUD", 1234.56, "A$1,234.56"),
        ]
        
        for mode, currency, amount, expected in test_cases:
            converter = CurrencyConverter(
                self.cache_dir, 
                mode=mode, 
                custom_currency=currency
            )
            
            result = converter.format_amount(amount)
            assert result == expected, f"Failed for {currency}: expected {expected}, got {result}"

    @pytest.mark.asyncio
    async def test_concurrent_conversions(self):
        """Test multiple concurrent conversions."""
        converter = CurrencyConverter(
            self.cache_dir, 
            mode=CurrencyMode.CUSTOM, 
            custom_currency="GBP"
        )
        
        # Mock rate fetches
        with patch.object(converter, '_fetch_fresh_rate') as mock_fetch:
            mock_fetch.return_value = ok(0.79)
            
            # Run multiple concurrent conversions
            tasks = [
                converter.convert_amount(100.0, "USD"),
                converter.convert_amount(200.0, "USD"),
                converter.convert_amount(300.0, "USD"),
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert all(result.is_ok() for result in results)
            assert unwrap(results[0]) == 79.0
            assert unwrap(results[1]) == 158.0
            assert unwrap(results[2]) == 237.0

    def test_get_conversion_info_auto_mode_direct_call_without_cached_locale(self):
        """Test get_conversion_info in AUTO mode when called directly without locale info cached."""
        converter = CurrencyConverter(self.cache_dir, mode=CurrencyMode.AUTO)
        
        # Ensure no locale info is cached - this should be None by default, but let's be explicit
        converter._locale_info = None
        
        with patch.object(converter, 'get_target_currency_info') as mock_get_target, \
             patch.object(converter.locale_detector, 'detect_locale') as mock_detect:
            # Mock get_target_currency_info to return values without setting _locale_info
            mock_get_target.return_value = ('JPY', '¥')
            mock_detect.return_value = LocaleInfo('ja', 'JP', 'JPY', '¥')
            
            info = converter.get_conversion_info()
            
            assert info['mode'] == 'auto'
            assert info['target_currency'] == 'JPY'
            assert info['currency_symbol'] == '¥'
            assert 'detected_locale' in info
            assert info['detected_locale']['language'] == 'ja'
            assert info['detected_locale']['country'] == 'JP'
            assert info['detected_locale']['locale_based'] is True
            assert 'custom_currency' not in info
            
            # Should call detect_locale because it wasn't cached and get_target_currency_info was mocked
            mock_detect.assert_called_once()
            mock_get_target.assert_called_once()
            
            # Verify that the locale info is now cached
            assert converter._locale_info is not None
            assert converter._locale_info.language == 'ja'
            assert converter._locale_info.country == 'JP'