"""Comprehensive tests for currency detector functionality."""

import pytest
import locale
from unittest.mock import patch, Mock
from dataclasses import FrozenInstanceError

from ccusage.currency.detector import LocaleDetector, LocaleInfo


class TestLocaleInfo:
    """Tests for LocaleInfo dataclass."""
    
    def test_locale_info_creation(self):
        """Test creating LocaleInfo instances."""
        locale_info = LocaleInfo(
            language='en',
            country='US',
            currency_code='USD',
            currency_symbol='$'
        )
        
        assert locale_info.language == 'en'
        assert locale_info.country == 'US'
        assert locale_info.currency_code == 'USD'
        assert locale_info.currency_symbol == '$'
    
    def test_locale_info_none_country(self):
        """Test LocaleInfo with None country."""
        locale_info = LocaleInfo(
            language='en',
            country=None,
            currency_code='USD',
            currency_symbol='$'
        )
        
        assert locale_info.language == 'en'
        assert locale_info.country is None
        assert locale_info.currency_code == 'USD'
        assert locale_info.currency_symbol == '$'
    
    def test_locale_info_mutable(self):
        """Test that LocaleInfo is mutable (not frozen)."""
        locale_info = LocaleInfo(
            language='en',
            country='US',
            currency_code='USD',
            currency_symbol='$'
        )
        
        # LocaleInfo is not frozen, so this should work
        locale_info.language = 'fr'
        assert locale_info.language == 'fr'
    
    def test_locale_info_equality(self):
        """Test LocaleInfo equality comparison."""
        locale_info1 = LocaleInfo('en', 'US', 'USD', '$')
        locale_info2 = LocaleInfo('en', 'US', 'USD', '$')
        locale_info3 = LocaleInfo('en', 'GB', 'GBP', '£')
        
        assert locale_info1 == locale_info2
        assert locale_info1 != locale_info3
    
    def test_locale_info_repr(self):
        """Test LocaleInfo string representation."""
        locale_info = LocaleInfo('en', 'US', 'USD', '$')
        repr_str = repr(locale_info)
        
        assert 'LocaleInfo' in repr_str
        assert 'language=\'en\'' in repr_str
        assert 'country=\'US\'' in repr_str
        assert 'currency_code=\'USD\'' in repr_str
        assert 'currency_symbol=\'$\'' in repr_str


class TestLocaleDetector:
    """Comprehensive tests for LocaleDetector class."""
    
    def test_country_currency_map_completeness(self):
        """Test that COUNTRY_CURRENCY_MAP contains expected entries."""
        detector = LocaleDetector()
        
        # Test that the map is a class variable
        assert hasattr(LocaleDetector, 'COUNTRY_CURRENCY_MAP')
        assert isinstance(LocaleDetector.COUNTRY_CURRENCY_MAP, dict)
        
        # Test some key entries
        expected_mappings = {
            'GB': ('GBP', '£'),
            'US': ('USD', '$'),
            'DE': ('EUR', '€'),
            'FR': ('EUR', '€'),
            'JP': ('JPY', '¥'),
            'CN': ('CNY', '¥'),
            'IN': ('INR', '₹'),
            'CA': ('CAD', 'C$'),
            'AU': ('AUD', 'A$'),
            'SG': ('SGD', 'S$'),
            'HK': ('HKD', 'HK$'),
            'CH': ('CHF', 'CHF'),
            'SE': ('SEK', 'kr'),
            'NO': ('NOK', 'kr'),
            'DK': ('DKK', 'kr'),
        }
        
        for country, expected in expected_mappings.items():
            assert country in detector.COUNTRY_CURRENCY_MAP
            assert detector.COUNTRY_CURRENCY_MAP[country] == expected
    
    @pytest.mark.parametrize("locale_str,expected_language,expected_country,expected_currency,expected_symbol", [
        ('en_US', 'en', 'US', 'USD', '$'),
        ('en_GB', 'en', 'GB', 'GBP', '£'),
        ('de_DE', 'de', 'DE', 'EUR', '€'),
        ('fr_FR', 'fr', 'FR', 'EUR', '€'),
        ('ja_JP', 'ja', 'JP', 'JPY', '¥'),
        ('zh_CN', 'zh', 'CN', 'CNY', '¥'),
        ('hi_IN', 'hi', 'IN', 'INR', '₹'),
        ('pt_BR', 'pt', 'BR', 'BRL', 'R$'),
        ('ko_KR', 'ko', 'KR', 'KRW', '₩'),
        ('sv_SE', 'sv', 'SE', 'SEK', 'kr'),
        ('nb_NO', 'nb', 'NO', 'NOK', 'kr'),
        ('da_DK', 'da', 'DK', 'DKK', 'kr'),
        ('pl_PL', 'pl', 'PL', 'PLN', 'zł'),
        ('cs_CZ', 'cs', 'CZ', 'CZK', 'Kč'),
        ('hu_HU', 'hu', 'HU', 'HUF', 'Ft'),
        ('ru_RU', 'ru', 'RU', 'RUB', '₽'),
        ('af_ZA', 'af', 'ZA', 'ZAR', 'R'),
    ])
    def test_detect_locale_known_countries(self, locale_str, expected_language, expected_country, expected_currency, expected_symbol):
        """Test locale detection for known countries."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', return_value=(locale_str, 'UTF-8')):
            locale_info = detector.detect_locale()
            
            assert locale_info.language == expected_language
            assert locale_info.country == expected_country
            assert locale_info.currency_code == expected_currency
            assert locale_info.currency_symbol == expected_symbol
    
    def test_detect_locale_unknown_country(self):
        """Test locale detection with unknown country code."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', return_value=('en_XX', 'UTF-8')):
            locale_info = detector.detect_locale()
            
            # Should fall back to USD
            assert locale_info.language == 'en'
            assert locale_info.country is None
            assert locale_info.currency_code == 'USD'
            assert locale_info.currency_symbol == '$'
    
    def test_detect_locale_no_underscore(self):
        """Test locale detection with locale string without underscore."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', return_value=('en', 'UTF-8')):
            locale_info = detector.detect_locale()
            
            # Should fall back to USD
            assert locale_info.language == 'en'
            assert locale_info.country is None
            assert locale_info.currency_code == 'USD'
            assert locale_info.currency_symbol == '$'
    
    def test_detect_locale_complex_locale_string(self):
        """Test locale detection with complex locale string (multiple underscores)."""
        detector = LocaleDetector()
        
        # Some systems return locale like 'en_US_POSIX' or 'en_GB_UTF8'
        # The code splits on '_' with maxsplit=1, so 'en_US_POSIX' -> language='en', country='US_POSIX'
        # Since 'US_POSIX' is not in the currency map, it should fall back to USD
        with patch('locale.getlocale', return_value=('en_US_POSIX', 'UTF-8')):
            locale_info = detector.detect_locale()
            
            assert locale_info.language == 'en'
            assert locale_info.country is None
            assert locale_info.currency_code == 'USD'
            assert locale_info.currency_symbol == '$'
    
    def test_detect_locale_none_returned(self):
        """Test locale detection when getlocale returns None."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', return_value=(None, None)):
            locale_info = detector.detect_locale()
            
            # Should fall back to USD
            assert locale_info.language == 'en'
            assert locale_info.country is None
            assert locale_info.currency_code == 'USD'
            assert locale_info.currency_symbol == '$'
    
    def test_detect_locale_empty_string_returned(self):
        """Test locale detection when getlocale returns empty string."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', return_value=('', 'UTF-8')):
            locale_info = detector.detect_locale()
            
            # Should fall back to USD
            assert locale_info.language == 'en'
            assert locale_info.country is None
            assert locale_info.currency_code == 'USD'
            assert locale_info.currency_symbol == '$'
    
    def test_detect_locale_locale_error(self):
        """Test locale detection when getlocale raises locale.Error."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', side_effect=locale.Error("Locale error")):
            locale_info = detector.detect_locale()
            
            # Should fall back to USD
            assert locale_info.language == 'en'
            assert locale_info.country is None
            assert locale_info.currency_code == 'USD'
            assert locale_info.currency_symbol == '$'
    
    def test_detect_locale_value_error(self):
        """Test locale detection when getlocale raises ValueError."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', side_effect=ValueError("Value error")):
            locale_info = detector.detect_locale()
            
            # Should fall back to USD
            assert locale_info.language == 'en'
            assert locale_info.country is None
            assert locale_info.currency_code == 'USD'
            assert locale_info.currency_symbol == '$'
    
    def test_detect_locale_unexpected_exception(self):
        """Test locale detection when getlocale raises unexpected exception."""
        detector = LocaleDetector()
        
        with patch('locale.getlocale', side_effect=RuntimeError("Unexpected error")):
            # Should not catch RuntimeError, so it should propagate
            with pytest.raises(RuntimeError, match="Unexpected error"):
                detector.detect_locale()
    
    def test_detect_locale_malformed_locale_string(self):
        """Test locale detection with malformed locale strings."""
        detector = LocaleDetector()
        
        # Test with locale that would cause split issues if not handled properly
        # '_GB' splits to language='', country='GB', so GB should be found in currency map
        with patch('locale.getlocale', return_value=('_GB', 'UTF-8')):
            locale_info = detector.detect_locale()
            
            # The empty language gets split to '', and GB is found in currency map
            assert locale_info.language == ''
            assert locale_info.country == 'GB'
            assert locale_info.currency_code == 'GBP'
            assert locale_info.currency_symbol == '£'
    
    @pytest.mark.parametrize("locale_str,expected_currency,expected_symbol", [
        ('en_GB', 'GBP', '£'),
        ('fr_FR', 'EUR', '€'),
        ('de_DE', 'EUR', '€'),
        ('es_ES', 'EUR', '€'),
        ('it_IT', 'EUR', '€'),
        ('nl_NL', 'EUR', '€'),
        ('ja_JP', 'JPY', '¥'),
        ('zh_CN', 'CNY', '¥'),
        ('invalid', 'USD', '$'),
        ('en', 'USD', '$'),
        ('', 'USD', '$'),
        ('en_XX', 'USD', '$'),  # Unknown country
        ('_GB', 'GBP', '£'),    # Malformed locale but GB is found
    ])
    def test_get_currency_for_locale(self, locale_str, expected_currency, expected_symbol):
        """Test get_currency_for_locale method with various locale strings."""
        detector = LocaleDetector()
        
        currency_code, currency_symbol = detector.get_currency_for_locale(locale_str)
        
        assert currency_code == expected_currency
        assert currency_symbol == expected_symbol
    
    def test_get_currency_for_locale_complex_locale(self):
        """Test get_currency_for_locale with complex locale strings."""
        detector = LocaleDetector()
        
        # Test with locale like 'en_US_POSIX' - splits to 'en', 'US_POSIX'
        # Since 'US_POSIX' is not in the map, it falls back to USD
        currency_code, currency_symbol = detector.get_currency_for_locale('en_US_POSIX')
        assert currency_code == 'USD'
        assert currency_symbol == '$'
        
        # Test with locale like 'de_DE_UTF8' - splits to 'de', 'DE_UTF8'  
        # Since 'DE_UTF8' is not in the map, it falls back to USD
        currency_code, currency_symbol = detector.get_currency_for_locale('de_DE_UTF8')
        assert currency_code == 'USD'
        assert currency_symbol == '$'
    
    def test_get_currency_for_locale_no_underscore(self):
        """Test get_currency_for_locale without underscore separator."""
        detector = LocaleDetector()
        
        currency_code, currency_symbol = detector.get_currency_for_locale('en')
        assert currency_code == 'USD'
        assert currency_symbol == '$'
    
    def test_get_currency_for_locale_empty_string(self):
        """Test get_currency_for_locale with empty string."""
        detector = LocaleDetector()
        
        currency_code, currency_symbol = detector.get_currency_for_locale('')
        assert currency_code == 'USD'
        assert currency_symbol == '$'
    
    def test_multiple_detector_instances(self):
        """Test that multiple detector instances work independently."""
        detector1 = LocaleDetector()
        detector2 = LocaleDetector()
        
        # Both should have access to the same class-level currency map
        assert detector1.COUNTRY_CURRENCY_MAP is detector2.COUNTRY_CURRENCY_MAP
        
        # But should work independently
        with patch('locale.getlocale', return_value=('en_GB', 'UTF-8')):
            locale_info1 = detector1.detect_locale()
            locale_info2 = detector2.detect_locale()
            
            assert locale_info1 == locale_info2
            assert locale_info1.currency_code == 'GBP'
    
    def test_currency_map_immutability(self):
        """Test that the currency map reference can't be accidentally modified."""
        detector = LocaleDetector()
        original_map = detector.COUNTRY_CURRENCY_MAP
        
        # This should be the same object reference
        assert detector.COUNTRY_CURRENCY_MAP is LocaleDetector.COUNTRY_CURRENCY_MAP
        assert original_map is LocaleDetector.COUNTRY_CURRENCY_MAP
    
    def test_all_euro_countries(self):
        """Test that all expected Euro countries are mapped correctly."""
        detector = LocaleDetector()
        euro_countries = ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT']
        
        for country in euro_countries:
            assert country in detector.COUNTRY_CURRENCY_MAP
            currency_code, currency_symbol = detector.COUNTRY_CURRENCY_MAP[country]
            assert currency_code == 'EUR'
            assert currency_symbol == '€'
    
    def test_unique_currency_symbols(self):
        """Test that currency symbols are as expected for uniqueness testing."""
        detector = LocaleDetector()
        
        # Some currencies share symbols (like $ and ¥), but let's verify the specific ones
        symbol_to_codes = {}
        for country, (code, symbol) in detector.COUNTRY_CURRENCY_MAP.items():
            if symbol not in symbol_to_codes:
                symbol_to_codes[symbol] = []
            symbol_to_codes[symbol].append(code)
        
        # USD and MXN both use '$'
        assert 'USD' in symbol_to_codes['$']
        assert 'MXN' in symbol_to_codes['$']
        
        # JPY and CNY both use '¥'
        assert 'JPY' in symbol_to_codes['¥']
        assert 'CNY' in symbol_to_codes['¥']
        
        # SEK, NOK, DKK all use 'kr'
        assert 'SEK' in symbol_to_codes['kr']
        assert 'NOK' in symbol_to_codes['kr']
        assert 'DKK' in symbol_to_codes['kr']
    
    @pytest.mark.parametrize("country_code", [
        'GB', 'US', 'CA', 'AU', 'NZ', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT',
        'JP', 'CN', 'IN', 'BR', 'MX', 'KR', 'CH', 'SE', 'NO', 'DK', 'PL', 'CZ',
        'HU', 'RU', 'ZA', 'SG', 'HK'
    ])
    def test_all_supported_countries_in_map(self, country_code):
        """Test that all expected country codes are in the currency map."""
        detector = LocaleDetector()
        
        assert country_code in detector.COUNTRY_CURRENCY_MAP
        currency_code, currency_symbol = detector.COUNTRY_CURRENCY_MAP[country_code]
        
        # Ensure both values are non-empty strings
        assert isinstance(currency_code, str)
        assert isinstance(currency_symbol, str)
        assert len(currency_code) > 0
        assert len(currency_symbol) > 0
        
        # Currency codes should be uppercase and 3 characters (mostly)
        assert currency_code.isupper()
        assert len(currency_code) == 3