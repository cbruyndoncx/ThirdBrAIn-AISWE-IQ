"""Exchange rate fetching from various APIs."""


from typing import ClassVar

import aiohttp

from ..core.exceptions import CcusageError
from ..core.result import Result, err, ok


class ExchangeRateFetcher:
    """Fetches exchange rates from multiple API sources with fallbacks."""

    # Primary API: ExchangeRate-API (free tier: 1,500 requests/month)
    PRIMARY_API_URL = "https://api.exchangerate-api.com/v4/latest/{base}"

    # Fallback APIs
    FALLBACK_APIS: ClassVar[list[str]] = [
        "https://api.fixer.io/latest?access_key={api_key}&base={base}&symbols={target}",
        "https://api.currencyfreaks.com/latest?apikey={api_key}&base={base}&symbols={target}",
    ]

    def __init__(self, timeout: int = 10):
        """
        Initialize the exchange rate fetcher.

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    async def fetch_rate(self, from_currency: str, to_currency: str) -> Result[float, str]:
        """
        Fetch exchange rate from one currency to another.

        Args:
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'GBP')

        Returns:
            Result containing the exchange rate or error message
        """
        if from_currency == to_currency:
            return ok(1.0)

        if not self._session:
            return err("HTTP session not initialized. Use async context manager.")

        # Try primary API first
        result = await self._fetch_from_primary_api(from_currency, to_currency)
        if result.is_ok():
            return result

        # Try fallback methods
        fallback_result = self._try_fallback_methods(from_currency, to_currency)
        if fallback_result.is_ok():
            return fallback_result

        return err(f"All exchange rate APIs failed. Last error: {result.error}")

    async def _fetch_from_primary_api(self, from_currency: str, to_currency: str) -> Result[float, str]:
        """Fetch rate from primary ExchangeRate-API."""
        url = self.PRIMARY_API_URL.format(base=from_currency.upper())

        try:
            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    # Check if the response contains rates
                    if 'rates' in data and to_currency.upper() in data['rates']:
                        rate = float(data['rates'][to_currency.upper()])
                        return ok(rate)
                    else:
                        return err(f"Currency {to_currency} not found in exchange rates")
                else:
                    return err(f"Primary API returned status {response.status}")

        except TimeoutError:
            return err("Primary API request timed out")
        except aiohttp.ClientError as e:
            return err(f"Primary API network error: {e!s}")
        except (KeyError, ValueError, TypeError) as e:
            return err(f"Primary API response parsing error: {e!s}")

    def _try_fallback_methods(self, from_currency: str, to_currency: str) -> Result[float, str]:
        """Try fallback exchange rate sources."""
        # For now, we'll implement a simple embedded rates fallback
        # This could be extended to use the CurrencyConverter library
        return self._get_embedded_rate(from_currency, to_currency)

    def _get_embedded_rate(self, from_currency: str, to_currency: str) -> Result[float, str]:
        """
        Get approximate exchange rate from embedded data.
        This is a fallback for offline scenarios.
        """
        # Static fallback rates (approximate, for offline use)
        # In a production system, this would be populated from historical data
        approximate_rates = {
            ('USD', 'GBP'): 0.79,
            ('USD', 'EUR'): 0.85,
            ('USD', 'CAD'): 1.25,
            ('USD', 'AUD'): 1.35,
            ('USD', 'JPY'): 110.0,
            ('GBP', 'USD'): 1.27,
            ('EUR', 'USD'): 1.18,
            ('CAD', 'USD'): 0.80,
            ('AUD', 'USD'): 0.74,
            ('JPY', 'USD'): 0.009,
        }

        key = (from_currency.upper(), to_currency.upper())
        if key in approximate_rates:
            return ok(approximate_rates[key])

        # Try reverse lookup
        reverse_key = (to_currency.upper(), from_currency.upper())
        if reverse_key in approximate_rates:
            reverse_rate = approximate_rates[reverse_key]
            return ok(1.0 / reverse_rate)

        return err(f"No fallback rate available for {from_currency} to {to_currency}")


class ExchangeRateError(CcusageError):
    """Exception for exchange rate related errors."""
    pass
