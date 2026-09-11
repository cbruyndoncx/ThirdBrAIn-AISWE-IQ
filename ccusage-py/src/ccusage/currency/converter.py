"""Main currency converter class that orchestrates all currency functionality."""

from enum import Enum
from pathlib import Path
from typing import Any

from ..core.exceptions import CcusageError
from ..core.result import Result, err, ok, unwrap
from .cache import ExchangeRateCache
from .detector import LocaleDetector, LocaleInfo
from .fetcher import ExchangeRateFetcher


class CurrencyMode(Enum):
    """Currency conversion modes."""
    AUTO = "auto"           # Auto-detect locale and convert
    USD_ONLY = "usd_only"   # Always display USD
    CUSTOM = "custom"       # Use specific currency


class CurrencyConverter:
    """
    Main currency converter that handles locale detection, exchange rates, and caching.
    """

    def __init__(self,
                 cache_dir: Path,
                 mode: CurrencyMode = CurrencyMode.AUTO,
                 custom_currency: str | None = None,
                 ttl_hours: int = 2):
        """
        Initialize the currency converter.

        Args:
            cache_dir: Directory for caching exchange rates
            mode: Currency conversion mode
            custom_currency: Custom currency code (used with CUSTOM mode)
            ttl_hours: Cache TTL in hours
        """
        self.mode = mode
        self.custom_currency = custom_currency
        self.ttl_hours = ttl_hours

        # Initialize components
        self.locale_detector = LocaleDetector()
        self.cache = ExchangeRateCache(cache_dir, ttl_hours)

        # Detected locale info (cached)
        self._locale_info: LocaleInfo | None = None

        # Warning flags
        self._shown_offline_warning = False
        self._shown_stale_warning = False

    def get_target_currency_info(self) -> tuple[str, str]:
        """
        Get the target currency code and symbol based on current mode.

        Returns:
            Tuple of (currency_code, currency_symbol)
        """
        if self.mode == CurrencyMode.USD_ONLY:
            return ("USD", "$")
        elif self.mode == CurrencyMode.CUSTOM and self.custom_currency:
            # For custom currency, we need to look up the symbol
            return self._get_currency_symbol(self.custom_currency)
        else:
            # AUTO mode - detect from locale
            if not self._locale_info:
                self._locale_info = self.locale_detector.detect_locale()
            return (self._locale_info.currency_code, self._locale_info.currency_symbol)

    def _get_currency_symbol(self, currency_code: str) -> tuple[str, str]:
        """Get currency symbol for a given currency code."""
        currency_symbols = {
            'USD': '$', 'GBP': '£', 'EUR': '€', 'JPY': '¥', 'CNY': '¥',
            'CAD': 'C$', 'AUD': 'A$', 'NZD': 'NZ$', 'CHF': 'CHF',
            'SEK': 'kr', 'NOK': 'kr', 'DKK': 'kr', 'PLN': 'zł',
            'CZK': 'Kč', 'HUF': 'Ft', 'RUB': '₽', 'INR': '₹',
            'BRL': 'R$', 'MXN': '$', 'KRW': '₩', 'ZAR': 'R',
            'SGD': 'S$', 'HKD': 'HK$'
        }

        symbol = currency_symbols.get(currency_code.upper(), currency_code.upper())
        return (currency_code.upper(), symbol)

    async def convert_amount(self, amount: float, from_currency: str = "USD") -> Result[float, str]:
        """
        Convert an amount from one currency to the target currency.

        Args:
            amount: Amount to convert
            from_currency: Source currency (defaults to USD)

        Returns:
            Result containing converted amount or error message
        """
        target_currency, _ = self.get_target_currency_info()

        if from_currency.upper() == target_currency.upper():
            return ok(amount)

        # Check cache first
        cached_rate = self.cache.get_rate(from_currency, target_currency)

        if cached_rate:
            rate, timestamp, is_stale = cached_rate

            if not is_stale:
                # Fresh cached rate
                return ok(amount * rate)
            else:
                # Stale rate - try to fetch fresh, but use stale as fallback
                fresh_result = await self._fetch_fresh_rate(from_currency, target_currency)

                if fresh_result.is_ok():
                    fresh_rate = unwrap(fresh_result)
                    self.cache.set_rate(from_currency, target_currency, fresh_rate)
                    return ok(amount * fresh_rate)
                else:
                    # Use stale rate as fallback
                    if not self._shown_stale_warning:
                        print(f"Warning: Using cached exchange rate from {timestamp.strftime('%Y-%m-%d %H:%M')}")
                        self._shown_stale_warning = True

                    return ok(amount * rate)

        # No cached rate - must fetch fresh
        fresh_result = await self._fetch_fresh_rate(from_currency, target_currency)

        if fresh_result.is_ok():
            rate = unwrap(fresh_result)
            self.cache.set_rate(from_currency, target_currency, rate)
            return ok(amount * rate)
        else:
            error_msg = fresh_result.error if hasattr(fresh_result, 'error') else str(fresh_result)
            return err(f"Failed to get exchange rate: {error_msg}")

    async def _fetch_fresh_rate(self, from_currency: str, to_currency: str) -> Result[float, str]:
        """Fetch a fresh exchange rate from the API."""
        try:
            async with ExchangeRateFetcher() as fetcher:
                return await fetcher.fetch_rate(from_currency, to_currency)
        except Exception as e:
            return err(f"Exchange rate fetch error: {e!s}")

    def format_amount(self, amount: float, include_currency_code: bool = False) -> str:
        """
        Format an amount with the appropriate currency symbol.

        Args:
            amount: Amount to format
            include_currency_code: Whether to include currency code in parentheses

        Returns:
            Formatted currency string
        """
        currency_code, currency_symbol = self.get_target_currency_info()

        # Format with appropriate precision
        if currency_code == "JPY" or currency_code == "KRW":
            # These currencies typically don't use decimal places
            formatted = f"{currency_symbol}{amount:,.0f}"
        else:
            formatted = f"{currency_symbol}{amount:,.2f}"

        if include_currency_code and currency_code != "USD":
            formatted += f" ({currency_code})"

        return formatted

    def get_currency_code(self) -> str:
        """Get the current target currency code."""
        currency_code, _ = self.get_target_currency_info()
        return currency_code

    def get_currency_symbol(self) -> str:
        """Get the current target currency symbol."""
        _, currency_symbol = self.get_target_currency_info()
        return currency_symbol

    def get_conversion_info(self) -> dict[str, Any]:
        """
        Get information about the current conversion settings.

        Returns:
            Dictionary with conversion configuration and status
        """
        currency_code, currency_symbol = self.get_target_currency_info()

        info = {
            'mode': self.mode.value,
            'target_currency': currency_code,
            'currency_symbol': currency_symbol,
            'cache_stats': self.cache.get_cache_stats(),
        }

        if self.mode == CurrencyMode.AUTO:
            if not self._locale_info:
                self._locale_info = self.locale_detector.detect_locale()

            info['detected_locale'] = {
                'language': self._locale_info.language,
                'country': self._locale_info.country,
                'locale_based': True
            }
        elif self.mode == CurrencyMode.CUSTOM:
            info['custom_currency'] = self.custom_currency

        return info

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Clean up any resources if needed
        pass


class CurrencyConversionError(CcusageError):
    """Exception for currency conversion errors."""
    pass
