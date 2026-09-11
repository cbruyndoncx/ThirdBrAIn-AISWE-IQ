"""Locale detection and currency mapping."""

import locale
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class LocaleInfo:
    """Information about the detected locale."""
    language: str
    country: str | None
    currency_code: str
    currency_symbol: str


class LocaleDetector:
    """Detects system locale and maps to appropriate currency."""

    # Mapping of country codes to currency information
    COUNTRY_CURRENCY_MAP: ClassVar[dict[str, tuple[str, str]]] = {
        'GB': ('GBP', '£'),
        'US': ('USD', '$'),
        'CA': ('CAD', 'C$'),
        'AU': ('AUD', 'A$'),
        'NZ': ('NZD', 'NZ$'),
        'DE': ('EUR', '€'),
        'FR': ('EUR', '€'),
        'IT': ('EUR', '€'),
        'ES': ('EUR', '€'),
        'NL': ('EUR', '€'),
        'BE': ('EUR', '€'),
        'AT': ('EUR', '€'),
        'JP': ('JPY', '¥'),
        'CN': ('CNY', '¥'),
        'IN': ('INR', '₹'),
        'BR': ('BRL', 'R$'),
        'MX': ('MXN', '$'),
        'KR': ('KRW', '₩'),
        'CH': ('CHF', 'CHF'),
        'SE': ('SEK', 'kr'),
        'NO': ('NOK', 'kr'),
        'DK': ('DKK', 'kr'),
        'PL': ('PLN', 'zł'),
        'CZ': ('CZK', 'Kč'),
        'HU': ('HUF', 'Ft'),
        'RU': ('RUB', '₽'),
        'ZA': ('ZAR', 'R'),
        'SG': ('SGD', 'S$'),
        'HK': ('HKD', 'HK$'),
    }

    def detect_locale(self) -> LocaleInfo:
        """
        Detect the system locale and return currency information.

        Returns:
            LocaleInfo with detected locale and currency details.
            Falls back to USD if detection fails or country is unsupported.
        """
        try:
            # Get system locale using the recommended approach
            # getlocale() returns (language, encoding) similar to getdefaultlocale()
            # but requires a category parameter. We use LC_CTYPE for character classification.
            current_locale = locale.getlocale(locale.LC_CTYPE)

            if current_locale and current_locale[0]:
                locale_code = current_locale[0]

                # Parse locale (e.g., 'en_GB', 'en_US', 'de_DE')
                if '_' in locale_code:
                    language, country = locale_code.split('_', 1)

                    # Look up currency for this country
                    if country in self.COUNTRY_CURRENCY_MAP:
                        currency_code, currency_symbol = self.COUNTRY_CURRENCY_MAP[country]
                        return LocaleInfo(
                            language=language,
                            country=country,
                            currency_code=currency_code,
                            currency_symbol=currency_symbol
                        )

                # Extract just the language part
                language = locale_code.split('_')[0]

        except (locale.Error, ValueError):
            # Locale detection failed
            pass

        # Default fallback to USD
        return LocaleInfo(
            language='en',
            country=None,
            currency_code='USD',
            currency_symbol='$'
        )

    def get_currency_for_locale(self, locale_code: str) -> tuple[str, str]:
        """
        Get currency code and symbol for a specific locale.

        Args:
            locale_code: Locale string like 'en_GB' or 'de_DE'

        Returns:
            Tuple of (currency_code, currency_symbol)
        """
        if '_' in locale_code:
            _, country = locale_code.split('_', 1)
            if country in self.COUNTRY_CURRENCY_MAP:
                return self.COUNTRY_CURRENCY_MAP[country]

        # Default to USD
        return ('USD', '$')
