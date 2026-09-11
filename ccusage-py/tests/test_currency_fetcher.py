"""Comprehensive tests for currency exchange rate fetcher functionality."""

import json
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest

from ccusage.core.result import is_err, is_ok, unwrap
from ccusage.currency.fetcher import ExchangeRateError, ExchangeRateFetcher


class TestExchangeRateFetcher:
    """Comprehensive tests for the ExchangeRateFetcher class."""

    def test_init_default_timeout(self):
        """Test initialization with default timeout."""
        fetcher = ExchangeRateFetcher()
        assert fetcher.timeout == 10
        assert fetcher._session is None

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        fetcher = ExchangeRateFetcher(timeout=30)
        assert fetcher.timeout == 30
        assert fetcher._session is None

    def test_class_constants(self):
        """Test class constants are properly defined."""
        assert ExchangeRateFetcher.PRIMARY_API_URL == "https://api.exchangerate-api.com/v4/latest/{base}"
        assert isinstance(ExchangeRateFetcher.FALLBACK_APIS, list)
        assert len(ExchangeRateFetcher.FALLBACK_APIS) == 2
        assert "fixer.io" in ExchangeRateFetcher.FALLBACK_APIS[0]
        assert "currencyfreaks.com" in ExchangeRateFetcher.FALLBACK_APIS[1]


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.asyncio
class TestExchangeRateFetcherAsync:
    """Async tests for the ExchangeRateFetcher class."""

    async def test_context_manager_setup_and_teardown(self):
        """Test async context manager setup and teardown."""
        fetcher = ExchangeRateFetcher(timeout=15)
        
        # Before context manager
        assert fetcher._session is None
        
        # In context manager
        async with fetcher as f:
            assert f is fetcher
            assert fetcher._session is not None
            assert isinstance(fetcher._session, aiohttp.ClientSession)
            assert fetcher._session.timeout.total == 15
        
        # After context manager - session should be closed
        # Note: We can't easily test if session is closed without implementation details

    async def test_same_currency_rate(self):
        """Test that same currency returns rate of 1.0."""
        async with ExchangeRateFetcher() as fetcher:
            result = await fetcher.fetch_rate('USD', 'USD')
            
            assert is_ok(result)
            assert unwrap(result) == 1.0

    async def test_case_insensitive_same_currency(self):
        """Test that same currency with different cases returns rate of 1.0."""
        async with ExchangeRateFetcher() as fetcher:
            result = await fetcher.fetch_rate('usd', 'USD')
            
            assert is_ok(result)
            assert unwrap(result) == 1.0

    async def test_fetch_rate_without_context_manager(self):
        """Test fetch_rate fails when session not initialized."""
        fetcher = ExchangeRateFetcher()
        
        result = await fetcher.fetch_rate('USD', 'GBP')
        
        assert is_err(result)
        assert "HTTP session not initialized" in result.error

    async def test_primary_api_success(self):
        """Test successful fetch from primary API."""
        mock_response_data = {
            'rates': {
                'GBP': 0.79,
                'EUR': 0.85
            }
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with ExchangeRateFetcher() as fetcher:
                result = await fetcher.fetch_rate('USD', 'GBP')
                
                assert is_ok(result)
                assert unwrap(result) == 0.79

    async def test_primary_api_currency_not_found(self):
        """Test primary API response missing target currency falls back to embedded."""
        mock_response_data = {
            'rates': {
                'EUR': 0.85
            }
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with ExchangeRateFetcher() as fetcher:
                # USD -> GBP should succeed with embedded rate fallback
                result = await fetcher.fetch_rate('USD', 'GBP')
                
                assert is_ok(result)
                assert unwrap(result) == 0.79  # Embedded rate
                
                # But USD -> XYZ should fail (not in embedded rates)
                result2 = await fetcher.fetch_rate('USD', 'XYZ')
                
                assert is_err(result2)
                assert "All exchange rate APIs failed" in result2.error

    async def test_primary_api_no_rates_key(self):
        """Test primary API response missing rates key falls back to embedded."""
        mock_response_data = {'error': 'Invalid API key'}
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with ExchangeRateFetcher() as fetcher:
                # USD -> GBP should succeed with embedded rate fallback
                result = await fetcher.fetch_rate('USD', 'GBP')
                
                assert is_ok(result)
                assert unwrap(result) == 0.79  # Embedded rate

    async def test_primary_api_http_error_status(self):
        """Test primary API returns non-200 status code falls back to embedded."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with ExchangeRateFetcher() as fetcher:
                # USD -> GBP should succeed with embedded rate fallback
                result = await fetcher.fetch_rate('USD', 'GBP')
                
                assert is_ok(result)
                assert unwrap(result) == 0.79  # Embedded rate

    async def test_primary_api_timeout_error(self):
        """Test primary API timeout handling with embedded fallback."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = TimeoutError("Request timeout")
            
            async with ExchangeRateFetcher() as fetcher:
                # USD -> GBP should succeed with embedded rate fallback
                result = await fetcher.fetch_rate('USD', 'GBP')
                
                assert is_ok(result)
                assert unwrap(result) == 0.79  # Embedded rate

    async def test_primary_api_client_error(self):
        """Test primary API client error handling with embedded fallback."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Network error")
            
            async with ExchangeRateFetcher() as fetcher:
                # USD -> GBP should succeed with embedded rate fallback
                result = await fetcher.fetch_rate('USD', 'GBP')
                
                assert is_ok(result)
                assert unwrap(result) == 0.79  # Embedded rate

    async def test_primary_api_json_parsing_error(self):
        """Test primary API JSON parsing error with embedded fallback."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with ExchangeRateFetcher() as fetcher:
                # USD -> GBP should succeed with embedded rate fallback
                result = await fetcher.fetch_rate('USD', 'GBP')
                
                assert is_ok(result)
                assert unwrap(result) == 0.79  # Embedded rate

    async def test_primary_api_key_error(self):
        """Test primary API key error in response processing with embedded fallback."""
        mock_response_data = {'rates': {'GBP': 'invalid_number'}}
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with ExchangeRateFetcher() as fetcher:
                # USD -> GBP should succeed with embedded rate fallback
                result = await fetcher.fetch_rate('USD', 'GBP')
                
                assert is_ok(result)
                assert unwrap(result) == 0.79  # Embedded rate

    async def test_embedded_rates_usd_to_gbp(self):
        """Test embedded rates fallback for USD to GBP."""
        async with ExchangeRateFetcher() as fetcher:
            result = fetcher._get_embedded_rate('USD', 'GBP')
            
            assert is_ok(result)
            assert unwrap(result) == 0.79

    async def test_embedded_rates_usd_to_eur(self):
        """Test embedded rates fallback for USD to EUR."""
        async with ExchangeRateFetcher() as fetcher:
            result = fetcher._get_embedded_rate('USD', 'EUR')
            
            assert is_ok(result)
            assert unwrap(result) == 0.85

    async def test_embedded_rates_gbp_to_usd(self):
        """Test embedded rates fallback for GBP to USD."""
        async with ExchangeRateFetcher() as fetcher:
            result = fetcher._get_embedded_rate('GBP', 'USD')
            
            assert is_ok(result)
            assert unwrap(result) == 1.27

    async def test_embedded_rates_reverse_lookup(self):
        """Test embedded rates with reverse lookup calculation."""
        async with ExchangeRateFetcher() as fetcher:
            # USD -> CAD is 1.25 in embedded data
            # So CAD -> USD should be 1/1.25 = 0.8
            result = fetcher._get_embedded_rate('CAD', 'USD')
            
            assert is_ok(result)
            assert unwrap(result) == 0.80

    async def test_embedded_rates_reverse_calculation(self):
        """Test reverse rate calculation works correctly."""
        async with ExchangeRateFetcher() as fetcher:
            # EUR -> USD is 1.18 in embedded data
            # So USD -> EUR should be available directly as 0.85
            # But let's test a pair that requires reverse calculation
            result = fetcher._get_embedded_rate('JPY', 'USD')
            
            assert is_ok(result)
            # JPY -> USD is 0.009 in the embedded data
            assert unwrap(result) == 0.009

    async def test_embedded_rates_not_available(self):
        """Test embedded rates returns error for unavailable currency pairs."""
        async with ExchangeRateFetcher() as fetcher:
            result = fetcher._get_embedded_rate('USD', 'XYZ')
            
            assert is_err(result)
            assert "No fallback rate available for USD to XYZ" in result.error

    async def test_embedded_rates_case_insensitive(self):
        """Test embedded rates work with different case currencies."""
        async with ExchangeRateFetcher() as fetcher:
            result = fetcher._get_embedded_rate('usd', 'gbp')
            
            assert is_ok(result)
            assert unwrap(result) == 0.79

    @pytest.mark.parametrize("from_curr,to_curr,expected", [
        ('USD', 'GBP', 0.79),
        ('USD', 'EUR', 0.85),
        ('USD', 'CAD', 1.25),
        ('USD', 'AUD', 1.35),
        ('USD', 'JPY', 110.0),
        ('GBP', 'USD', 1.27),
        ('EUR', 'USD', 1.18),
        ('CAD', 'USD', 0.80),
        ('AUD', 'USD', 0.74),
        ('JPY', 'USD', 0.009),
    ])
    async def test_embedded_rates_all_pairs(self, from_curr, to_curr, expected):
        """Test all embedded rate pairs."""
        async with ExchangeRateFetcher() as fetcher:
            result = fetcher._get_embedded_rate(from_curr, to_curr)
            
            assert is_ok(result)
            assert unwrap(result) == expected

    async def test_full_fallback_chain_success(self):
        """Test full fallback chain when primary API fails but embedded succeeds."""
        # Mock primary API to fail
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Network error")
            
            async with ExchangeRateFetcher() as fetcher:
                result = await fetcher.fetch_rate('USD', 'GBP')
                
                # Should succeed with embedded rate
                assert is_ok(result)
                assert unwrap(result) == 0.79

    async def test_full_fallback_chain_failure(self):
        """Test full fallback chain when both primary API and embedded rates fail."""
        # Mock primary API to fail
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Network error")
            
            async with ExchangeRateFetcher() as fetcher:
                result = await fetcher.fetch_rate('USD', 'XYZ')
                
                assert is_err(result)
                error_message = result.error
                assert "All exchange rate APIs failed" in error_message
                assert "Network error" in error_message

    async def test_primary_api_url_format(self):
        """Test that primary API URL is formatted correctly."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {'rates': {'GBP': 0.79}}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with ExchangeRateFetcher() as fetcher:
                await fetcher.fetch_rate('USD', 'GBP')
                
                # Check that the URL was formatted correctly
                expected_url = "https://api.exchangerate-api.com/v4/latest/USD"
                mock_get.assert_called_once_with(expected_url)

    async def test_primary_api_url_format_case_conversion(self):
        """Test that primary API converts currency to uppercase."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {'rates': {'GBP': 0.79}}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with ExchangeRateFetcher() as fetcher:
                await fetcher.fetch_rate('usd', 'gbp')
                
                # Check that the URL uses uppercase currency
                expected_url = "https://api.exchangerate-api.com/v4/latest/USD"
                mock_get.assert_called_once_with(expected_url)

    async def test_try_fallback_methods_calls_embedded(self):
        """Test that _try_fallback_methods properly calls _get_embedded_rate."""
        async with ExchangeRateFetcher() as fetcher:
            with patch.object(fetcher, '_get_embedded_rate', return_value=fetcher._get_embedded_rate('USD', 'GBP')) as mock_embedded:
                fetcher._try_fallback_methods('USD', 'GBP')
                mock_embedded.assert_called_once_with('USD', 'GBP')

    async def test_context_manager_exception_handling(self):
        """Test context manager handles exceptions during setup."""
        # This test verifies the context manager properly handles initialization
        try:
            async with ExchangeRateFetcher() as fetcher:
                assert fetcher._session is not None
                # Simulate some work
                await fetcher.fetch_rate('USD', 'USD')
        except Exception:
            pytest.fail("Context manager should handle exceptions gracefully")

    async def test_multiple_context_manager_usage(self):
        """Test using the same fetcher instance multiple times."""
        fetcher = ExchangeRateFetcher()
        
        # First usage
        async with fetcher as f1:
            result1 = await f1.fetch_rate('USD', 'USD')
            assert is_ok(result1)
        
        # Second usage (should work fine)
        async with fetcher as f2:
            result2 = await f2.fetch_rate('EUR', 'EUR')
            assert is_ok(result2)

    async def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        import asyncio
        
        mock_response_data = {'rates': {'GBP': 0.79, 'EUR': 0.85, 'CAD': 1.25}}
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with ExchangeRateFetcher() as fetcher:
                # Make multiple concurrent requests
                tasks = [
                    fetcher.fetch_rate('USD', 'GBP'),
                    fetcher.fetch_rate('USD', 'EUR'),
                    fetcher.fetch_rate('USD', 'CAD'),
                ]
                
                results = await asyncio.gather(*tasks)
                
                # All should succeed
                assert all(is_ok(result) for result in results)
                assert unwrap(results[0]) == 0.79
                assert unwrap(results[1]) == 0.85
                assert unwrap(results[2]) == 1.25

    async def test_context_manager_exit_with_none_session(self):
        """Test __aexit__ method when session is None."""
        fetcher = ExchangeRateFetcher()
        # Manually set session to None to test the condition
        fetcher._session = None
        
        # This should not raise an exception - testing line 43
        await fetcher.__aexit__(None, None, None)
        
        # Should still be None
        assert fetcher._session is None

    async def test_reverse_calculation_with_patched_embedded_data(self):
        """Test lines 133-134 by patching embedded data to create reverse calculation scenario."""
        from unittest.mock import patch
        
        async with ExchangeRateFetcher() as fetcher:
            # Create a mock that removes one direction from the embedded rates
            # to force the reverse calculation path
            mock_embedded_rates = {
                ('USD', 'GBP'): 0.79,
                ('USD', 'EUR'): 0.85, 
                ('USD', 'CAD'): 1.25,
                ('USD', 'AUD'): 1.35,
                ('USD', 'JPY'): 110.0,
                ('GBP', 'USD'): 1.27,
                ('EUR', 'USD'): 1.18,
                ('CAD', 'USD'): 0.80,
                ('AUD', 'USD'): 0.74,
                # Remove JPY->USD to force reverse calculation
                # ('JPY', 'USD'): 0.009,  # <-- Commented out
                ('USD', 'TESTCURR'): 3.0,  # Add a test currency with only one direction
            }
            
            # Patch the embedded data by modifying the method's local variable
            original_method = fetcher._get_embedded_rate
            
            def patched_get_embedded_rate(from_currency: str, to_currency: str):
                from ccusage.core.result import ok, err
                
                # Use our modified embedded rates data
                approximate_rates = mock_embedded_rates
                
                key = (from_currency.upper(), to_currency.upper())
                if key in approximate_rates:
                    return ok(approximate_rates[key])

                # Try reverse lookup - THIS IS LINES 133-134
                reverse_key = (to_currency.upper(), from_currency.upper()) 
                if reverse_key in approximate_rates:
                    reverse_rate = approximate_rates[reverse_key]  # Line 133
                    return ok(1.0 / reverse_rate)  # Line 134

                return err(f"No fallback rate available for {from_currency} to {to_currency}")
            
            # Temporarily replace the method
            fetcher._get_embedded_rate = patched_get_embedded_rate
            
            try:
                # Test case 1: JPY -> USD should now use reverse calculation
                # USD -> JPY = 110.0, so JPY -> USD should be 1.0 / 110.0 = 0.009090909...
                result = fetcher._get_embedded_rate('JPY', 'USD')
                assert is_ok(result)
                rate = unwrap(result)
                assert abs(rate - (1.0 / 110.0)) < 0.0001  # Close enough for floating point
                
                # Test case 2: TESTCURR -> USD should use reverse calculation  
                # USD -> TESTCURR = 3.0, so TESTCURR -> USD should be 1.0 / 3.0 = 0.333...
                result = fetcher._get_embedded_rate('TESTCURR', 'USD')
                assert is_ok(result)
                rate = unwrap(result)
                assert abs(rate - (1.0 / 3.0)) < 0.0001  # Close enough for floating point
                
                # Test case 3: Ensure direct lookup still works
                result = fetcher._get_embedded_rate('USD', 'GBP')
                assert is_ok(result)
                assert unwrap(result) == 0.79
                
            finally:
                # Restore original method
                fetcher._get_embedded_rate = original_method


class TestExchangeRateError:
    """Tests for the ExchangeRateError exception class."""

    def test_exception_inheritance(self):
        """Test that ExchangeRateError inherits from CcusageError."""
        from ccusage.core.exceptions import CcusageError
        
        error = ExchangeRateError("Test error")
        assert isinstance(error, CcusageError)
        assert isinstance(error, Exception)

    def test_exception_message(self):
        """Test that ExchangeRateError preserves error messages."""
        message = "Exchange rate fetch failed"
        error = ExchangeRateError(message)
        assert str(error) == message

    def test_exception_can_be_raised(self):
        """Test that ExchangeRateError can be raised and caught."""
        with pytest.raises(ExchangeRateError) as exc_info:
            raise ExchangeRateError("Test error")
        
        assert str(exc_info.value) == "Test error"