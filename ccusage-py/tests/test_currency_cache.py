"""Comprehensive tests for currency exchange rate cache functionality."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from ccusage.currency.cache import ExchangeRateCache


class TestExchangeRateCacheInit:
    """Test ExchangeRateCache initialization."""
    
    def test_init_creates_cache_dir(self):
        """Test that initialization creates the cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "nonexistent" / "cache"
            cache = ExchangeRateCache(cache_dir, ttl_hours=2)
            
            assert cache.cache_dir == cache_dir
            assert cache.ttl_hours == 2
            assert cache.cache_file == cache_dir / "exchange_rates_cache.json"
            assert cache_dir.exists()
            assert cache_dir.is_dir()
    
    def test_init_default_ttl(self):
        """Test initialization with default TTL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir)
            
            assert cache.ttl_hours == 2  # Default value
    
    def test_init_custom_ttl(self):
        """Test initialization with custom TTL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=6)
            
            assert cache.ttl_hours == 6
    
    def test_init_existing_cache_dir(self):
        """Test initialization with existing cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            # Directory already exists
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            assert cache.cache_dir.exists()
            assert len(cache._memory_cache) == 0
    
    def test_init_loads_existing_cache(self):
        """Test that initialization loads existing cache file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "exchange_rates_cache.json"
            
            # Create cache file with test data
            test_data = {
                "USD_GBP": [0.79, "2023-01-01T12:00:00"],
                "EUR_USD": [1.08, "2023-01-01T13:00:00"]
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f)
            
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            assert len(cache._memory_cache) == 2
            assert ("USD", "GBP") in cache._memory_cache
            assert ("EUR", "USD") in cache._memory_cache


class TestExchangeRateCacheLoadFileCache:
    """Test _load_file_cache method."""
    
    def test_load_file_cache_nonexistent_file(self):
        """Test loading when cache file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache.__new__(ExchangeRateCache)  # Skip __init__
            cache.cache_dir = cache_dir
            cache.cache_file = cache_dir / "nonexistent.json"
            cache._memory_cache = {}
            
            cache._load_file_cache()
            
            assert len(cache._memory_cache) == 0
    
    def test_load_file_cache_valid_data(self):
        """Test loading valid cache data from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "test_cache.json"
            
            test_data = {
                "USD_GBP": [0.79, "2023-01-01T12:00:00"],
                "EUR_USD": [1.08, "2023-01-01T13:00:00.123456"]
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f)
            
            cache = ExchangeRateCache.__new__(ExchangeRateCache)
            cache.cache_dir = cache_dir
            cache.cache_file = cache_file
            cache._memory_cache = {}
            
            cache._load_file_cache()
            
            assert len(cache._memory_cache) == 2
            
            # Check USD_GBP entry
            assert ("USD", "GBP") in cache._memory_cache
            rate, timestamp = cache._memory_cache[("USD", "GBP")]
            assert rate == 0.79
            assert timestamp == datetime(2023, 1, 1, 12, 0, 0)
            
            # Check EUR_USD entry
            assert ("EUR", "USD") in cache._memory_cache
            rate, timestamp = cache._memory_cache[("EUR", "USD")]
            assert rate == 1.08
            assert timestamp == datetime(2023, 1, 1, 13, 0, 0, 123456)
    
    def test_load_file_cache_invalid_key_format(self):
        """Test loading cache with invalid key format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "test_cache.json"
            
            test_data = {
                "USD_GBP": [0.79, "2023-01-01T12:00:00"],
                "INVALID": [1.08, "2023-01-01T13:00:00"],  # Invalid key format
                "EUR_USD": [1.10, "2023-01-01T14:00:00"]
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f)
            
            cache = ExchangeRateCache.__new__(ExchangeRateCache)
            cache.cache_dir = cache_dir
            cache.cache_file = cache_file
            cache._memory_cache = {}
            
            cache._load_file_cache()
            
            # Should only load valid entries
            assert len(cache._memory_cache) == 2
            assert ("USD", "GBP") in cache._memory_cache
            assert ("EUR", "USD") in cache._memory_cache
    
    def test_load_file_cache_invalid_timestamp(self):
        """Test loading cache with invalid timestamp format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "test_cache.json"
            
            test_data = {
                "USD_GBP": [0.79, "invalid-timestamp"],
                "EUR_USD": [1.08, "2023-01-01T13:00:00"]
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f)
            
            cache = ExchangeRateCache.__new__(ExchangeRateCache)
            cache.cache_dir = cache_dir
            cache.cache_file = cache_file
            cache._memory_cache = {}
            
            cache._load_file_cache()
            
            # Should only load valid entries
            assert len(cache._memory_cache) == 1
            assert ("EUR", "USD") in cache._memory_cache
    
    def test_load_file_cache_os_error_handling(self):
        """Test OS error handling during cache loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "test_cache.json"
            
            cache = ExchangeRateCache.__new__(ExchangeRateCache)
            cache.cache_dir = cache_dir
            cache.cache_file = cache_file
            cache._memory_cache = {}
            
            with patch('builtins.open', side_effect=OSError("Test error")):
                cache._load_file_cache()
                # Should not raise exception and cache should remain empty
                assert len(cache._memory_cache) == 0
    
    def test_load_file_cache_json_error_handling(self):
        """Test JSON decode error handling during cache loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "test_cache.json"
            
            cache = ExchangeRateCache.__new__(ExchangeRateCache)
            cache.cache_dir = cache_dir
            cache.cache_file = cache_file
            cache._memory_cache = {}
            
            with patch('json.load', side_effect=json.JSONDecodeError("Test error", "doc", 0)):
                cache._load_file_cache()
                # Should not raise exception and cache should remain empty
                assert len(cache._memory_cache) == 0
    
    def test_load_file_cache_key_error_handling(self):
        """Test KeyError handling during cache loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "test_cache.json"
            
            cache = ExchangeRateCache.__new__(ExchangeRateCache)
            cache.cache_dir = cache_dir
            cache.cache_file = cache_file
            cache._memory_cache = {}
            
            with patch('json.load', side_effect=KeyError("Test error")):
                cache._load_file_cache()
                # Should not raise exception and cache should remain empty
                assert len(cache._memory_cache) == 0
    
    def test_load_file_cache_corrupted_json(self):
        """Test loading corrupted JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "test_cache.json"
            
            # Create corrupted JSON file
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write('{"invalid": json}')
            
            cache = ExchangeRateCache.__new__(ExchangeRateCache)
            cache.cache_dir = cache_dir
            cache.cache_file = cache_file
            cache._memory_cache = {}
            
            cache._load_file_cache()
            
            # Should handle gracefully
            assert len(cache._memory_cache) == 0


class TestExchangeRateCacheSaveFileCache:
    """Test _save_file_cache method."""
    
    def test_save_file_cache_success(self):
        """Test successful cache file saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "test_cache.json"
            
            cache = ExchangeRateCache.__new__(ExchangeRateCache)
            cache.cache_dir = cache_dir
            cache.cache_file = cache_file
            cache._memory_cache = {
                ("USD", "GBP"): (0.79, datetime(2023, 1, 1, 12, 0, 0)),
                ("EUR", "USD"): (1.08, datetime(2023, 1, 1, 13, 0, 0, 123456))
            }
            
            cache._save_file_cache()
            
            # Verify file was created and contains correct data
            assert cache_file.exists()
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            expected_data = {
                "USD_GBP": [0.79, "2023-01-01T12:00:00"],
                "EUR_USD": [1.08, "2023-01-01T13:00:00.123456"]
            }
            assert saved_data == expected_data
    
    def test_save_file_cache_empty_cache(self):
        """Test saving empty cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "test_cache.json"
            
            cache = ExchangeRateCache.__new__(ExchangeRateCache)
            cache.cache_dir = cache_dir
            cache.cache_file = cache_file
            cache._memory_cache = {}
            
            cache._save_file_cache()
            
            # Verify file was created with empty object
            assert cache_file.exists()
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert saved_data == {}
    
    def test_save_file_cache_os_error(self):
        """Test handling of OS errors during save."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache_file = cache_dir / "test_cache.json"
            
            cache = ExchangeRateCache.__new__(ExchangeRateCache)
            cache.cache_dir = cache_dir
            cache.cache_file = cache_file
            cache._memory_cache = {("USD", "GBP"): (0.79, datetime.now())}
            
            with patch('builtins.open', side_effect=OSError("Permission denied")):
                # Should not raise exception
                cache._save_file_cache()
                
                # File should not exist due to error
                assert not cache_file.exists()


class TestExchangeRateCacheIsExpired:
    """Test _is_expired method."""
    
    @patch('random.randint')
    def test_is_expired_fresh_entry(self, mock_randint):
        """Test that fresh entries are not expired."""
        mock_randint.return_value = 0  # No jitter
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Recent timestamp
            recent_timestamp = datetime.now() - timedelta(minutes=30)
            
            assert not cache._is_expired(recent_timestamp)
    
    @patch('random.randint')
    def test_is_expired_old_entry(self, mock_randint):
        """Test that old entries are expired."""
        mock_randint.return_value = 0  # No jitter
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Old timestamp
            old_timestamp = datetime.now() - timedelta(hours=2)
            
            assert cache._is_expired(old_timestamp)
    
    @patch('random.randint')
    def test_is_expired_with_jitter(self, mock_randint):
        """Test expiration with jitter."""
        mock_randint.return_value = 15  # 15 minutes jitter
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Timestamp at exactly 1 hour should not be expired due to jitter
            boundary_timestamp = datetime.now() - timedelta(hours=1)
            
            assert not cache._is_expired(boundary_timestamp)
    
    @patch('random.randint')
    def test_is_expired_boundary_with_jitter(self, mock_randint):
        """Test expiration at boundary with maximum jitter."""
        mock_randint.return_value = 30  # Maximum 30 minutes jitter
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Timestamp beyond TTL + jitter should be expired
            expired_timestamp = datetime.now() - timedelta(hours=1, minutes=31)
            
            assert cache._is_expired(expired_timestamp)
    
    def test_is_expired_jitter_range(self):
        """Test that jitter is within expected range."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            timestamp = datetime.now() - timedelta(hours=1, minutes=10)
            
            # With 0 jitter: should be expired (10 min past TTL > 0 jitter)
            with patch('random.randint', return_value=0):
                assert cache._is_expired(timestamp)
                
            # With 15 jitter: should not be expired (10 min past TTL < 15 min jitter)
            with patch('random.randint', return_value=15):
                assert not cache._is_expired(timestamp)
                
            # With 30 jitter: should not be expired (10 min past TTL < 30 min jitter)
            with patch('random.randint', return_value=30):
                assert not cache._is_expired(timestamp)


class TestExchangeRateCacheGetRate:
    """Test get_rate method."""
    
    def test_get_rate_same_currency(self):
        """Test getting rate for same currency."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            result = cache.get_rate('USD', 'USD')
            
            assert result is not None
            rate, timestamp, is_stale = result
            assert rate == 1.0
            assert not is_stale
            assert isinstance(timestamp, datetime)
    
    def test_get_rate_case_insensitive(self):
        """Test that currency codes are case insensitive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Set rate with uppercase
            cache.set_rate('USD', 'GBP', 0.79)
            
            # Get with mixed case
            result = cache.get_rate('usd', 'gbp')
            
            assert result is not None
            rate, timestamp, is_stale = result
            assert rate == 0.79
    
    def test_get_rate_direct_lookup_fresh(self):
        """Test direct lookup of fresh rate."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Set fresh rate
            cache.set_rate('USD', 'GBP', 0.79)
            
            result = cache.get_rate('USD', 'GBP')
            
            assert result is not None
            rate, timestamp, is_stale = result
            assert rate == 0.79
            assert not is_stale
    
    @patch('random.randint', return_value=0)  # No jitter for predictable testing
    def test_get_rate_direct_lookup_stale(self, mock_randint):
        """Test direct lookup of stale rate."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Manually set stale entry
            old_timestamp = datetime.now() - timedelta(hours=2)
            cache._memory_cache[('USD', 'GBP')] = (0.79, old_timestamp)
            
            result = cache.get_rate('USD', 'GBP')
            
            assert result is not None
            rate, timestamp, is_stale = result
            assert rate == 0.79
            assert is_stale
            assert timestamp == old_timestamp
    
    def test_get_rate_reverse_lookup_fresh(self):
        """Test reverse lookup of fresh rate."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Set GBP to USD rate
            cache.set_rate('GBP', 'USD', 1.27)
            
            # Get USD to GBP (should return inverse)
            result = cache.get_rate('USD', 'GBP')
            
            assert result is not None
            rate, timestamp, is_stale = result
            assert abs(rate - (1.0 / 1.27)) < 0.000001  # Test with high precision
            assert not is_stale
    
    @patch('random.randint', return_value=0)  # No jitter
    def test_get_rate_reverse_lookup_stale(self, mock_randint):
        """Test reverse lookup of stale rate."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Manually set stale reverse entry
            old_timestamp = datetime.now() - timedelta(hours=2)
            cache._memory_cache[('GBP', 'USD')] = (1.27, old_timestamp)
            
            result = cache.get_rate('USD', 'GBP')
            
            assert result is not None
            rate, timestamp, is_stale = result
            assert abs(rate - (1.0 / 1.27)) < 0.000001
            assert is_stale
            assert timestamp == old_timestamp
    
    def test_get_rate_not_found(self):
        """Test getting rate that doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            result = cache.get_rate('USD', 'GBP')
            
            assert result is None
    
    def test_get_rate_direct_over_reverse(self):
        """Test that direct lookup takes precedence over reverse lookup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Set both direct and reverse rates
            cache.set_rate('USD', 'GBP', 0.79)
            cache.set_rate('GBP', 'USD', 1.25)  # Slightly different from 1/0.79
            
            result = cache.get_rate('USD', 'GBP')
            
            assert result is not None
            rate, timestamp, is_stale = result
            assert rate == 0.79  # Should use direct rate, not inverse of reverse


class TestExchangeRateCacheSetRate:
    """Test set_rate method."""
    
    def test_set_rate_basic(self):
        """Test basic rate setting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            cache.set_rate('USD', 'GBP', 0.79)
            
            assert ('USD', 'GBP') in cache._memory_cache
            rate, timestamp = cache._memory_cache[('USD', 'GBP')]
            assert rate == 0.79
            assert isinstance(timestamp, datetime)
            
            # Should also save to file
            assert cache.cache_file.exists()
    
    def test_set_rate_case_normalization(self):
        """Test that currency codes are normalized to uppercase."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            cache.set_rate('usd', 'gbp', 0.79)
            
            # Should be stored as uppercase
            assert ('USD', 'GBP') in cache._memory_cache
            assert ('usd', 'gbp') not in cache._memory_cache
    
    def test_set_rate_same_currency_ignored(self):
        """Test that setting rate for same currency is ignored."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            cache.set_rate('USD', 'USD', 1.5)  # Should be ignored
            
            assert len(cache._memory_cache) == 0
    
    def test_set_rate_overwrites_existing(self):
        """Test that setting rate overwrites existing entry."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Set initial rate
            cache.set_rate('USD', 'GBP', 0.79)
            initial_timestamp = cache._memory_cache[('USD', 'GBP')][1]
            
            # Set new rate
            cache.set_rate('USD', 'GBP', 0.81)
            new_rate, new_timestamp = cache._memory_cache[('USD', 'GBP')]
            
            assert new_rate == 0.81
            assert new_timestamp > initial_timestamp
    
    def test_set_rate_persists_to_file(self):
        """Test that rate setting persists to cache file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            cache.set_rate('USD', 'GBP', 0.79)
            
            # Load cache file directly
            with open(cache.cache_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert 'USD_GBP' in saved_data
            assert saved_data['USD_GBP'][0] == 0.79
    
    def test_set_rate_file_error_continues(self):
        """Test that file save errors don't prevent in-memory caching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Mock the file open to raise an OSError during save
            with patch('builtins.open', side_effect=OSError("Write error")):
                # Should not raise exception and should still cache in memory
                cache.set_rate('USD', 'GBP', 0.79)
                
                # Should still be cached in memory
                assert ('USD', 'GBP') in cache._memory_cache
                assert cache._memory_cache[('USD', 'GBP')][0] == 0.79
                
                # File should not exist due to error
                assert not cache.cache_file.exists()


class TestExchangeRateCacheClearExpired:
    """Test clear_expired method."""
    
    @patch('random.randint', return_value=0)  # No jitter
    def test_clear_expired_removes_old_entries(self, mock_randint):
        """Test that expired entries are removed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Add fresh entry
            fresh_timestamp = datetime.now() - timedelta(minutes=30)
            cache._memory_cache[('USD', 'GBP')] = (0.79, fresh_timestamp)
            
            # Add expired entry
            expired_timestamp = datetime.now() - timedelta(hours=2)
            cache._memory_cache[('EUR', 'USD')] = (1.08, expired_timestamp)
            
            removed_count = cache.clear_expired()
            
            assert removed_count == 1
            assert ('USD', 'GBP') in cache._memory_cache  # Fresh entry remains
            assert ('EUR', 'USD') not in cache._memory_cache  # Expired entry removed
    
    def test_clear_expired_no_expired_entries(self):
        """Test clearing expired when no entries are expired."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Add fresh entries
            cache.set_rate('USD', 'GBP', 0.79)
            cache.set_rate('EUR', 'USD', 1.08)
            
            removed_count = cache.clear_expired()
            
            assert removed_count == 0
            assert len(cache._memory_cache) == 2
    
    def test_clear_expired_empty_cache(self):
        """Test clearing expired from empty cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            removed_count = cache.clear_expired()
            
            assert removed_count == 0
            assert len(cache._memory_cache) == 0
    
    @patch('random.randint', return_value=0)  # No jitter
    def test_clear_expired_all_expired(self, mock_randint):
        """Test clearing when all entries are expired."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Add multiple expired entries
            expired_timestamp = datetime.now() - timedelta(hours=2)
            cache._memory_cache[('USD', 'GBP')] = (0.79, expired_timestamp)
            cache._memory_cache[('EUR', 'USD')] = (1.08, expired_timestamp)
            cache._memory_cache[('JPY', 'USD')] = (0.007, expired_timestamp)
            
            removed_count = cache.clear_expired()
            
            assert removed_count == 3
            assert len(cache._memory_cache) == 0
    
    def test_clear_expired_saves_to_file(self):
        """Test that clearing expired entries saves updated cache to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Mock _save_file_cache to verify it's called
            with patch.object(cache, '_save_file_cache') as mock_save:
                cache.clear_expired()
                mock_save.assert_called_once()


class TestExchangeRateCacheClearAll:
    """Test clear_all method."""
    
    def test_clear_all_removes_memory_cache(self):
        """Test that clear_all removes all entries from memory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Add some entries
            cache.set_rate('USD', 'GBP', 0.79)
            cache.set_rate('EUR', 'USD', 1.08)
            
            assert len(cache._memory_cache) == 2
            
            cache.clear_all()
            
            assert len(cache._memory_cache) == 0
    
    def test_clear_all_removes_cache_file(self):
        """Test that clear_all removes the cache file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Add entry to create cache file
            cache.set_rate('USD', 'GBP', 0.79)
            assert cache.cache_file.exists()
            
            cache.clear_all()
            
            assert not cache.cache_file.exists()
    
    def test_clear_all_nonexistent_file(self):
        """Test clear_all when cache file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Add to memory but don't save to file
            cache._memory_cache[('USD', 'GBP')] = (0.79, datetime.now())
            
            assert not cache.cache_file.exists()
            
            # Should not raise error
            cache.clear_all()
            
            assert len(cache._memory_cache) == 0
    
    def test_clear_all_file_deletion_error(self):
        """Test clear_all handles file deletion errors gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            cache.set_rate('USD', 'GBP', 0.79)
            
            with patch('pathlib.Path.unlink', side_effect=OSError("Permission denied")):
                # Should not raise exception
                cache.clear_all()
                
                # Memory should still be cleared
                assert len(cache._memory_cache) == 0


class TestExchangeRateCacheGetCacheStats:
    """Test get_cache_stats method."""
    
    def test_get_cache_stats_empty_cache(self):
        """Test cache stats for empty cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=2)
            
            stats = cache.get_cache_stats()
            
            assert stats['total_entries'] == 0
            assert stats['fresh_entries'] == 0
            assert stats['stale_entries'] == 0
            assert stats['cache_file_exists'] is False
            assert stats['ttl_hours'] == 2
    
    def test_get_cache_stats_with_fresh_entries(self):
        """Test cache stats with fresh entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Add fresh entries
            cache.set_rate('USD', 'GBP', 0.79)
            cache.set_rate('EUR', 'USD', 1.08)
            
            stats = cache.get_cache_stats()
            
            assert stats['total_entries'] == 2
            assert stats['fresh_entries'] == 2
            assert stats['stale_entries'] == 0
            assert stats['cache_file_exists'] is True
            assert stats['ttl_hours'] == 1
    
    @patch('random.randint', return_value=0)  # No jitter
    def test_get_cache_stats_with_stale_entries(self, mock_randint):
        """Test cache stats with stale entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Add fresh entry
            fresh_timestamp = datetime.now() - timedelta(minutes=30)
            cache._memory_cache[('USD', 'GBP')] = (0.79, fresh_timestamp)
            
            # Add stale entry
            stale_timestamp = datetime.now() - timedelta(hours=2)
            cache._memory_cache[('EUR', 'USD')] = (1.08, stale_timestamp)
            
            stats = cache.get_cache_stats()
            
            assert stats['total_entries'] == 2
            assert stats['fresh_entries'] == 1
            assert stats['stale_entries'] == 1
            assert stats['cache_file_exists'] is False  # Not saved in this test
            assert stats['ttl_hours'] == 1
    
    @patch('random.randint', return_value=0)  # No jitter
    def test_get_cache_stats_all_stale(self, mock_randint):
        """Test cache stats when all entries are stale."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Add only stale entries
            stale_timestamp = datetime.now() - timedelta(hours=2)
            cache._memory_cache[('USD', 'GBP')] = (0.79, stale_timestamp)
            cache._memory_cache[('EUR', 'USD')] = (1.08, stale_timestamp)
            cache._memory_cache[('JPY', 'USD')] = (0.007, stale_timestamp)
            
            stats = cache.get_cache_stats()
            
            assert stats['total_entries'] == 3
            assert stats['fresh_entries'] == 0
            assert stats['stale_entries'] == 3
    
    def test_get_cache_stats_with_existing_file(self):
        """Test cache stats when cache file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            
            # Create cache file manually
            cache_file = cache_dir / "exchange_rates_cache.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
            
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            stats = cache.get_cache_stats()
            
            assert stats['cache_file_exists'] is True


class TestExchangeRateCacheIntegration:
    """Integration tests for complete cache workflows."""
    
    def test_full_lifecycle_workflow(self):
        """Test complete cache lifecycle: init -> load -> set -> get -> clear."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            
            # Create initial cache
            cache1 = ExchangeRateCache(cache_dir, ttl_hours=1)
            cache1.set_rate('USD', 'GBP', 0.79)
            cache1.set_rate('EUR', 'USD', 1.08)
            
            # Create new cache instance (should load from file)
            cache2 = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Should have loaded existing data
            assert len(cache2._memory_cache) == 2
            
            result = cache2.get_rate('USD', 'GBP')
            assert result is not None
            assert result[0] == 0.79
            
            # Add more data
            cache2.set_rate('JPY', 'USD', 0.007)
            
            # Clear expired (should remove nothing since all are fresh)
            removed = cache2.clear_expired()
            assert removed == 0
            assert len(cache2._memory_cache) == 3
            
            # Get stats
            stats = cache2.get_cache_stats()
            assert stats['total_entries'] == 3
            assert stats['fresh_entries'] == 3
            
            # Clear all
            cache2.clear_all()
            assert len(cache2._memory_cache) == 0
            assert not cache2.cache_file.exists()
    
    def test_persistence_across_instances(self):
        """Test that data persists correctly across cache instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            
            # Create and populate first instance
            cache1 = ExchangeRateCache(cache_dir, ttl_hours=2)
            cache1.set_rate('USD', 'GBP', 0.79)
            cache1.set_rate('EUR', 'USD', 1.08)
            cache1.set_rate('JPY', 'USD', 0.007)
            
            # Create second instance
            cache2 = ExchangeRateCache(cache_dir, ttl_hours=2)
            
            # Should have all data from first instance
            assert len(cache2._memory_cache) == 3
            
            # Test all rates are accessible
            usd_gbp = cache2.get_rate('USD', 'GBP')
            eur_usd = cache2.get_rate('EUR', 'USD')
            jpy_usd = cache2.get_rate('JPY', 'USD')
            
            assert usd_gbp is not None and usd_gbp[0] == 0.79
            assert eur_usd is not None and eur_usd[0] == 1.08
            assert jpy_usd is not None and jpy_usd[0] == 0.007
    
    @patch('random.randint', return_value=0)  # No jitter
    def test_expiration_workflow(self, mock_randint):
        """Test complete expiration workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            cache = ExchangeRateCache(cache_dir, ttl_hours=1)
            
            # Add fresh entries
            fresh_time = datetime.now() - timedelta(minutes=30)
            cache._memory_cache[('USD', 'GBP')] = (0.79, fresh_time)
            
            # Add stale entries
            stale_time = datetime.now() - timedelta(hours=2)
            cache._memory_cache[('EUR', 'USD')] = (1.08, stale_time)
            cache._memory_cache[('JPY', 'USD')] = (0.007, stale_time)
            
            # Get fresh rate
            fresh_result = cache.get_rate('USD', 'GBP')
            assert fresh_result is not None
            assert not fresh_result[2]  # Not stale
            
            # Get stale rate
            stale_result = cache.get_rate('EUR', 'USD')
            assert stale_result is not None
            assert stale_result[2]  # Is stale
            
            # Check stats before cleanup
            stats = cache.get_cache_stats()
            assert stats['fresh_entries'] == 1
            assert stats['stale_entries'] == 2
            
            # Clear expired
            removed = cache.clear_expired()
            assert removed == 2
            assert len(cache._memory_cache) == 1
            
            # Only fresh entry should remain
            assert ('USD', 'GBP') in cache._memory_cache
            assert ('EUR', 'USD') not in cache._memory_cache
            assert ('JPY', 'USD') not in cache._memory_cache