"""Exchange rate caching with memory and file persistence."""

import contextlib
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class ExchangeRateCache:
    """Two-tier caching system for exchange rates with memory and file persistence."""

    def __init__(self, cache_dir: Path, ttl_hours: int = 2):
        """
        Initialize the exchange rate cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cached rates in hours
        """
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        self.cache_file = cache_dir / "exchange_rates_cache.json"

        # In-memory cache: {(from, to): (rate, timestamp)}
        self._memory_cache: dict[tuple[str, str], tuple[float, datetime]] = {}

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load existing cache from file
        self._load_file_cache()

    def _load_file_cache(self) -> None:
        """Load cached exchange rates from file into memory."""
        if not self.cache_file.exists():
            return

        try:
            with open(self.cache_file, encoding='utf-8') as f:
                file_cache = json.load(f)

            # Convert string timestamps back to datetime objects
            for key_str, (rate, timestamp_str) in file_cache.items():
                try:
                    # Parse key: "USD_GBP" -> ("USD", "GBP")
                    from_currency, to_currency = key_str.split('_', 1)
                    key = (from_currency, to_currency)

                    # Parse timestamp
                    timestamp = datetime.fromisoformat(timestamp_str)

                    self._memory_cache[key] = (rate, timestamp)

                except (ValueError, KeyError):
                    # Skip invalid cache entries
                    continue

        except (OSError, json.JSONDecodeError, KeyError):
            # If cache file is corrupted, start fresh
            pass

    def _save_file_cache(self) -> None:
        """Save current memory cache to file."""
        try:
            # Convert to JSON-serializable format
            file_cache = {}
            for (from_currency, to_currency), (rate, timestamp) in self._memory_cache.items():
                key_str = f"{from_currency}_{to_currency}"
                file_cache[key_str] = (rate, timestamp.isoformat())

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(file_cache, f, indent=2)

        except OSError:
            # Ignore file write errors - cache can still work in memory
            pass

    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if a cached entry is expired."""
        age = datetime.now() - timestamp

        # Add some jitter to prevent thundering herd
        jitter_minutes = random.randint(0, 30)
        effective_ttl = timedelta(hours=self.ttl_hours, minutes=jitter_minutes)

        return age > effective_ttl

    def get_rate(self, from_currency: str, to_currency: str) -> tuple[float, datetime, bool] | None:
        """
        Get cached exchange rate if available and not expired.

        Args:
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Tuple of (rate, timestamp, is_stale) if found, None otherwise.
            is_stale indicates if the rate is expired but still available.
        """
        if from_currency == to_currency:
            return (1.0, datetime.now(), False)

        key = (from_currency.upper(), to_currency.upper())

        if key in self._memory_cache:
            rate, timestamp = self._memory_cache[key]
            is_stale = self._is_expired(timestamp)

            # Return even if stale for fallback scenarios
            return (rate, timestamp, is_stale)

        # Try reverse lookup
        reverse_key = (to_currency.upper(), from_currency.upper())
        if reverse_key in self._memory_cache:
            rate, timestamp = self._memory_cache[reverse_key]
            is_stale = self._is_expired(timestamp)

            # Return inverse rate
            return (1.0 / rate, timestamp, is_stale)

        return None

    def set_rate(self, from_currency: str, to_currency: str, rate: float) -> None:
        """
        Cache an exchange rate.

        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            rate: Exchange rate value
        """
        if from_currency == to_currency:
            return

        key = (from_currency.upper(), to_currency.upper())
        timestamp = datetime.now()

        self._memory_cache[key] = (rate, timestamp)

        # Persist to file asynchronously
        self._save_file_cache()

    def clear_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        expired_keys = []

        for key, (_rate, timestamp) in self._memory_cache.items():
            if self._is_expired(timestamp):
                expired_keys.append(key)

        for key in expired_keys:
            del self._memory_cache[key]

        # Save updated cache
        self._save_file_cache()

        return len(expired_keys)

    def clear_all(self) -> None:
        """Clear all cached entries."""
        self._memory_cache.clear()

        # Remove cache file
        if self.cache_file.exists():
            with contextlib.suppress(OSError):
                self.cache_file.unlink()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        datetime.now()
        fresh_count = 0
        stale_count = 0

        for _, (_rate, timestamp) in self._memory_cache.items():
            if self._is_expired(timestamp):
                stale_count += 1
            else:
                fresh_count += 1

        return {
            'total_entries': len(self._memory_cache),
            'fresh_entries': fresh_count,
            'stale_entries': stale_count,
            'cache_file_exists': self.cache_file.exists(),
            'ttl_hours': self.ttl_hours,
        }
