"""Tests for pricing functionality."""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest
import requests

from ccusage.pricing.fetcher import PricingFetcher
from ccusage.pricing.calculator import CostCalculator
from ccusage.models.usage import RawUsageEntry, ModelPricing, UsageTotals
from ccusage.core.exceptions import NetworkError, PricingError
from ccusage.core.result import Ok, Err
from datetime import datetime


@pytest.fixture
def sample_pricing_data():
    """Sample pricing data from LiteLLM."""
    return {
        "claude-sonnet-4-20250514": {
            "max_tokens": 4096,
            "max_input_tokens": 200000,
            "max_output_tokens": 4096,
            "input_cost_per_token": 0.000003,
            "output_cost_per_token": 0.000015,
            "litellm_provider": "anthropic",
            "mode": "chat",
            "supports_function_calling": True,
            "supports_parallel_function_calling": True,
            "supports_vision": True
        },
        "claude-opus-4-20250514": {
            "max_tokens": 4096,
            "max_input_tokens": 200000,
            "max_output_tokens": 4096,
            "input_cost_per_token": 0.000015,
            "output_cost_per_token": 0.000075,
            "litellm_provider": "anthropic",
            "mode": "chat",
            "supports_function_calling": True,
            "supports_parallel_function_calling": True,
            "supports_vision": True
        }
    }


@pytest.fixture
def sample_usage_entry():
    """Sample usage entry for testing."""
    return RawUsageEntry(
        timestamp=datetime(2025, 7, 15, 10, 0, 0),
        session_id="session-1",
        request_id="req-1",
        message_id="msg-1",
        model_name="claude-sonnet-4-20250514",
        input_tokens=1000,
        output_tokens=500,
        cache_creation_tokens=100,
        cache_read_tokens=50,
        cost_usd=None,
        project_path="/project1",
        version="1.0.43",
    )


class TestPricingFetcher:
    """Test the PricingFetcher class."""
    
    def setup_method(self):
        """Clear cache before each test."""
        PricingFetcher._shared_pricing_cache = None
        PricingFetcher._cache_message_shown = False
    
    def test_init(self):
        """Test PricingFetcher initialization."""
        fetcher = PricingFetcher()
        assert fetcher.base_url == "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"
        assert fetcher.timeout == 30
        assert fetcher.cache_file.name == "litellm_pricing_cache.json"
    
    @patch('requests.get')
    def test_fetch_pricing_data_success(self, mock_get, sample_pricing_data):
        """Test successful pricing data fetch."""
        mock_response = Mock()
        mock_response.json.return_value = sample_pricing_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        fetcher = PricingFetcher()
        result = fetcher.fetch_pricing_data()
        
        assert isinstance(result, Ok)
        pricing_data = result.value
        assert "claude-sonnet-4-20250514" in pricing_data
        assert pricing_data["claude-sonnet-4-20250514"].input_cost_per_token == 0.000003
        
        mock_get.assert_called_once_with(fetcher.base_url, timeout=30)
    
    @patch('requests.get')
    def test_fetch_pricing_data_network_error(self, mock_get):
        """Test network error during pricing data fetch."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        fetcher = PricingFetcher()
        result = fetcher.fetch_pricing_data()
        
        assert isinstance(result, Err)
        assert isinstance(result.error, NetworkError)
        assert "Network error" in str(result.error)
    
    @patch('requests.get')
    def test_fetch_pricing_data_json_error(self, mock_get):
        """Test JSON parsing error during pricing data fetch."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        fetcher = PricingFetcher()
        result = fetcher.fetch_pricing_data()
        
        assert isinstance(result, Err)
        assert isinstance(result.error, PricingError)
        assert "Invalid JSON" in str(result.error)
    
    @patch('requests.get')
    def test_get_pricing_data_online_success(self, mock_get, sample_pricing_data):
        """Test getting pricing data online successfully."""
        mock_response = Mock()
        mock_response.json.return_value = sample_pricing_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        fetcher = PricingFetcher()
        result = fetcher.get_pricing_data(offline=False)
        
        assert isinstance(result, Ok)
        pricing_data = result.value
        assert "claude-sonnet-4-20250514" in pricing_data
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_get_pricing_data_offline_success(self, mock_read_text, mock_exists, sample_pricing_data):
        """Test getting pricing data offline successfully."""
        mock_exists.return_value = True
        mock_read_text.return_value = json.dumps(sample_pricing_data)
        
        fetcher = PricingFetcher()
        result = fetcher.get_pricing_data(offline=True)
        
        assert isinstance(result, Ok)
        pricing_data = result.value
        assert "claude-sonnet-4-20250514" in pricing_data
    
    @patch('pathlib.Path.exists')
    def test_get_pricing_data_offline_no_cache(self, mock_exists):
        """Test getting pricing data offline with no cache file."""
        mock_exists.return_value = False
        
        fetcher = PricingFetcher()
        result = fetcher.get_pricing_data(offline=True)
        
        assert isinstance(result, Err)
        assert isinstance(result.error, PricingError)
        assert "No cached pricing data found" in str(result.error)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_get_pricing_data_offline_invalid_json(self, mock_read_text, mock_exists):
        """Test getting pricing data offline with invalid JSON."""
        mock_exists.return_value = True
        mock_read_text.return_value = "invalid json"
        
        fetcher = PricingFetcher()
        result = fetcher.get_pricing_data(offline=True)
        
        assert isinstance(result, Err)
        assert isinstance(result.error, PricingError)
        assert "Failed to parse cached pricing data" in str(result.error)
    
    def test_get_model_pricing_success(self, sample_pricing_data):
        """Test getting pricing for a specific model."""
        fetcher = PricingFetcher()
        pricing_data = {
            model: ModelPricing(**data) for model, data in sample_pricing_data.items()
        }
        
        result = fetcher.get_model_pricing("claude-sonnet-4-20250514", pricing_data)
        
        assert isinstance(result, Ok)
        model_pricing = result.value
        assert model_pricing is not None
        assert model_pricing.input_cost_per_token == 0.000003
    
    def test_get_model_pricing_not_found(self):
        """Test getting pricing for a non-existent model."""
        fetcher = PricingFetcher()
        pricing_data = {}
        
        result = fetcher.get_model_pricing("non-existent-model", pricing_data)
        
        assert isinstance(result, Ok)
        assert result.value is None
    
    @patch('pathlib.Path.write_text')
    def test_save_to_cache(self, mock_write_text, sample_pricing_data):
        """Test saving pricing data to cache."""
        fetcher = PricingFetcher()
        pricing_data = {
            model: ModelPricing(**data) for model, data in sample_pricing_data.items()
        }
        
        fetcher._save_to_cache(pricing_data)
        
        mock_write_text.assert_called_once()
        # Verify JSON was written
        written_data = mock_write_text.call_args[0][0]
        parsed_data = json.loads(written_data)
        assert "claude-sonnet-4-20250514" in parsed_data
    
    @patch('pathlib.Path.write_text')
    def test_save_to_cache_exception(self, mock_write_text, sample_pricing_data):
        """Test saving pricing data to cache with exception."""
        mock_write_text.side_effect = Exception("Write error")
        fetcher = PricingFetcher()
        pricing_data = {
            model: ModelPricing(**data) for model, data in sample_pricing_data.items()
        }
        
        # Should not raise exception, just silently ignore
        fetcher._save_to_cache(pricing_data)
        
        mock_write_text.assert_called_once()
    
    def test_clear_cache(self):
        """Test clearing the pricing cache."""
        fetcher = PricingFetcher()
        PricingFetcher._shared_pricing_cache = {"test": "data"}
        
        fetcher.clear_cache()
        
        assert PricingFetcher._shared_pricing_cache is None
    
    def test_fetch_pricing_data_with_cache(self, sample_pricing_data):
        """Test fetching pricing data when cache exists."""
        fetcher = PricingFetcher()
        cached_data = {
            model: ModelPricing(**data) for model, data in sample_pricing_data.items()
        }
        PricingFetcher._shared_pricing_cache = cached_data
        
        result = fetcher.fetch_pricing_data()
        
        assert isinstance(result, Ok)
        assert result.value == cached_data
        
        # Clean up
        PricingFetcher._shared_pricing_cache = None
    
    def test_init_offline(self):
        """Test PricingFetcher initialization in offline mode."""
        fetcher = PricingFetcher(offline=True)
        assert fetcher.offline is True
    
    @patch('pathlib.Path.exists')
    def test_fetch_pricing_data_offline_mode(self, mock_exists):
        """Test fetching pricing data in offline mode."""
        mock_exists.return_value = False
        
        fetcher = PricingFetcher(offline=True)
        result = fetcher.fetch_pricing_data()
        
        assert isinstance(result, Err)
        assert isinstance(result.error, PricingError)
        assert "No cached pricing data found" in str(result.error)
    
    @patch('requests.get')
    def test_fetch_pricing_data_validation_error(self, mock_get):
        """Test fetching pricing data with validation error."""
        # Mock invalid model data that will cause validation error
        mock_response = Mock()
        mock_response.json.return_value = {
            "invalid-model": {
                "input_cost_per_token": "invalid_string_value"  # This should cause validation error
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        fetcher = PricingFetcher()
        result = fetcher.fetch_pricing_data()
        
        # Should succeed but skip invalid models
        assert isinstance(result, Ok)
        assert "invalid-model" not in result.value
    
    @patch('requests.get')
    def test_fetch_pricing_data_generic_exception(self, mock_get):
        """Test fetching pricing data with generic exception."""
        mock_get.side_effect = Exception("Unexpected error")
        
        fetcher = PricingFetcher()
        result = fetcher.fetch_pricing_data()
        
        assert isinstance(result, Err)
        assert isinstance(result.error, PricingError)
        assert "Unexpected error" in str(result.error)
    
    @patch('requests.get')
    def test_fetch_pricing_data_non_dict_model(self, mock_get):
        """Test fetching pricing data with non-dict model entry."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "valid-model": {
                "input_cost_per_token": 0.000003,
                "output_cost_per_token": 0.000015
            },
            "invalid-model": "not a dict"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        fetcher = PricingFetcher()
        result = fetcher.fetch_pricing_data()
        
        assert isinstance(result, Ok)
        assert "valid-model" in result.value
        assert "invalid-model" not in result.value
    
    def test_get_model_pricing_variations(self, sample_pricing_data):
        """Test getting pricing with various model name variations."""
        fetcher = PricingFetcher()
        pricing_data = {
            "anthropic/claude-sonnet-4": ModelPricing(**sample_pricing_data["claude-sonnet-4-20250514"])
        }
        
        # Test with provider prefix variation
        result = fetcher.get_model_pricing("claude-sonnet-4", pricing_data)
        assert isinstance(result, Ok)
        assert result.value is not None
    
    def test_get_model_pricing_partial_match(self, sample_pricing_data):
        """Test getting pricing with partial model name match."""
        fetcher = PricingFetcher()
        pricing_data = {
            "claude-sonnet-4-20250514": ModelPricing(**sample_pricing_data["claude-sonnet-4-20250514"])
        }
        
        # Test partial match
        result = fetcher.get_model_pricing("sonnet-4", pricing_data)
        assert isinstance(result, Ok)
        assert result.value is not None
    
    @pytest.mark.asyncio
    async def test_calculate_cost_from_tokens_success(self, sample_pricing_data):
        """Test calculating cost from tokens successfully."""
        with patch.object(PricingFetcher, 'fetch_pricing_data') as mock_fetch:
            mock_fetch.return_value = Ok({
                "claude-sonnet-4-20250514": ModelPricing(**sample_pricing_data["claude-sonnet-4-20250514"])
            })
            
            fetcher = PricingFetcher()
            result = await fetcher.calculate_cost_from_tokens(
                input_tokens=1000,
                output_tokens=500,
                cache_creation_tokens=100,
                cache_read_tokens=50,
                model_name="claude-sonnet-4-20250514"
            )
            
            assert isinstance(result, Ok)
            expected_cost = (1000 * 0.000003) + (500 * 0.000015)
            assert result.value == expected_cost
    
    @pytest.mark.asyncio
    async def test_calculate_cost_from_tokens_empty_model(self):
        """Test calculating cost from tokens with empty model name."""
        fetcher = PricingFetcher()
        result = await fetcher.calculate_cost_from_tokens(
            input_tokens=1000,
            output_tokens=500,
            model_name=""
        )
        
        assert isinstance(result, Ok)
        assert result.value == 0.0
    
    @pytest.mark.asyncio
    async def test_calculate_cost_from_tokens_fetch_error(self):
        """Test calculating cost from tokens with fetch error."""
        with patch.object(PricingFetcher, 'fetch_pricing_data') as mock_fetch:
            mock_fetch.return_value = Err(PricingError("Fetch failed"))
            
            fetcher = PricingFetcher()
            result = await fetcher.calculate_cost_from_tokens(
                input_tokens=1000,
                output_tokens=500,
                model_name="claude-sonnet-4-20250514"
            )
            
            assert isinstance(result, Err)
            assert "Fetch failed" in str(result.error)
    
    @pytest.mark.asyncio
    async def test_calculate_cost_from_tokens_model_not_found(self, sample_pricing_data):
        """Test calculating cost from tokens with model not found."""
        with patch.object(PricingFetcher, 'fetch_pricing_data') as mock_fetch:
            mock_fetch.return_value = Ok({
                "claude-sonnet-4-20250514": ModelPricing(**sample_pricing_data["claude-sonnet-4-20250514"])
            })
            
            fetcher = PricingFetcher()
            result = await fetcher.calculate_cost_from_tokens(
                input_tokens=1000,
                output_tokens=500,
                model_name="non-existent-model"
            )
            
            assert isinstance(result, Ok)
            assert result.value == 0.0
    
    @pytest.mark.asyncio
    async def test_calculate_cost_from_tokens_get_pricing_error(self, sample_pricing_data):
        """Test calculating cost from tokens with get_model_pricing error."""
        with patch.object(PricingFetcher, 'fetch_pricing_data') as mock_fetch, \
             patch.object(PricingFetcher, 'get_model_pricing') as mock_get_pricing:
            
            mock_fetch.return_value = Ok({})
            mock_get_pricing.return_value = Err(PricingError("Get pricing failed"))
            
            fetcher = PricingFetcher()
            result = await fetcher.calculate_cost_from_tokens(
                input_tokens=1000,
                output_tokens=500,
                model_name="claude-sonnet-4-20250514"
            )
            
            assert isinstance(result, Err)
            assert "Get pricing failed" in str(result.error)
    
    def test_calculate_cost_from_pricing_with_cache_costs(self):
        """Test calculating cost from pricing with cache costs."""
        fetcher = PricingFetcher()
        pricing = ModelPricing(
            max_tokens=4096,
            max_input_tokens=200000,
            max_output_tokens=4096,
            input_cost_per_token=0.000003,
            output_cost_per_token=0.000015,
            cache_creation_input_token_cost=0.000002,
            cache_read_input_token_cost=0.000001,
            litellm_provider="anthropic",
            mode="chat",
            supports_function_calling=True
        )
        
        cost = fetcher._calculate_cost_from_pricing(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=100,
            cache_read_tokens=50,
            pricing=pricing
        )
        
        expected_cost = (1000 * 0.000003) + (500 * 0.000015) + (100 * 0.000002) + (50 * 0.000001)
        assert cost == expected_cost
    
    def test_calculate_cost_from_pricing_none_costs(self):
        """Test calculating cost from pricing with None costs."""
        fetcher = PricingFetcher()
        pricing = ModelPricing(
            max_tokens=4096,
            max_input_tokens=200000,
            max_output_tokens=4096,
            input_cost_per_token=None,
            output_cost_per_token=None,
            cache_creation_input_token_cost=None,
            cache_read_input_token_cost=None,
            litellm_provider="anthropic",
            mode="chat",
            supports_function_calling=True
        )
        
        cost = fetcher._calculate_cost_from_pricing(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=100,
            cache_read_tokens=50,
            pricing=pricing
        )
        
        assert cost == 0.0
    
    def test_calculate_cost_from_pricing_zero_cache_tokens(self):
        """Test calculating cost from pricing with zero cache tokens."""
        fetcher = PricingFetcher()
        pricing = ModelPricing(
            max_tokens=4096,
            max_input_tokens=200000,
            max_output_tokens=4096,
            input_cost_per_token=0.000003,
            output_cost_per_token=0.000015,
            cache_creation_input_token_cost=0.000002,
            cache_read_input_token_cost=0.000001,
            litellm_provider="anthropic",
            mode="chat",
            supports_function_calling=True
        )
        
        cost = fetcher._calculate_cost_from_pricing(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=0,
            cache_read_tokens=0,
            pricing=pricing
        )
        
        expected_cost = (1000 * 0.000003) + (500 * 0.000015)
        assert cost == expected_cost
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_offline_pricing_validation_error(self, mock_read_text, mock_exists):
        """Test loading offline pricing with validation error."""
        mock_exists.return_value = True
        mock_read_text.return_value = json.dumps({
            "invalid-model": {
                "input_cost_per_token": "invalid_string_value"  # This should cause validation error
            }
        })
        
        fetcher = PricingFetcher()
        result = fetcher._load_offline_pricing()
        
        # Should succeed but skip invalid models
        assert isinstance(result, Ok)
        assert "invalid-model" not in result.value
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_offline_pricing_generic_exception(self, mock_read_text, mock_exists):
        """Test loading offline pricing with generic exception."""
        mock_exists.return_value = True
        mock_read_text.side_effect = Exception("Read error")
        
        fetcher = PricingFetcher()
        result = fetcher._load_offline_pricing()
        
        assert isinstance(result, Err)
        assert isinstance(result.error, PricingError)
        assert "Read error" in str(result.error)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_offline_pricing_non_dict_model(self, mock_read_text, mock_exists):
        """Test loading offline pricing with non-dict model entry."""
        mock_exists.return_value = True
        mock_read_text.return_value = json.dumps({
            "valid-model": {
                "input_cost_per_token": 0.000003,
                "output_cost_per_token": 0.000015
            },
            "invalid-model": "not a dict"
        })
        
        fetcher = PricingFetcher()
        result = fetcher._load_offline_pricing()
        
        assert isinstance(result, Ok)
        assert "valid-model" in result.value
        assert "invalid-model" not in result.value
    
    @patch('builtins.print')
    def test_fetch_pricing_data_with_context(self, mock_print, sample_pricing_data):
        """Test fetching pricing data with context parameter."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = sample_pricing_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            fetcher = PricingFetcher()
            result = fetcher.fetch_pricing_data("Test context")
            
            assert isinstance(result, Ok)
            mock_print.assert_called_with("Test context: Fetching pricing data from LiteLLM.")
    
    @patch('builtins.print')
    def test_fetch_pricing_data_without_context(self, mock_print, sample_pricing_data):
        """Test fetching pricing data without context parameter."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = sample_pricing_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            fetcher = PricingFetcher()
            result = fetcher.fetch_pricing_data()
            
            assert isinstance(result, Ok)
            mock_print.assert_called_with("Fetching pricing data from LiteLLM.")
    
    @patch('builtins.print')
    def test_cache_message_shown_once(self, mock_print, sample_pricing_data):
        """Test that cache message is only shown once."""
        cached_data = {
            model: ModelPricing(**data) for model, data in sample_pricing_data.items()
        }
        PricingFetcher._shared_pricing_cache = cached_data
        
        fetcher1 = PricingFetcher()
        fetcher2 = PricingFetcher()
        
        # First call should show message
        result1 = fetcher1.fetch_pricing_data()
        assert isinstance(result1, Ok)
        
        # Second call should not show message
        result2 = fetcher2.fetch_pricing_data()
        assert isinstance(result2, Ok)
        
        # Should only be called once
        mock_print.assert_called_once_with("Using cached pricing data for cost calculations.\n")
    
    def test_get_model_pricing_exact_match(self, sample_pricing_data):
        """Test getting pricing with exact model name match."""
        fetcher = PricingFetcher()
        pricing_data = {
            model: ModelPricing(**data) for model, data in sample_pricing_data.items()
        }
        
        result = fetcher.get_model_pricing("claude-sonnet-4-20250514", pricing_data)
        assert isinstance(result, Ok)
        assert result.value is not None
        assert result.value == pricing_data["claude-sonnet-4-20250514"]
    
    def test_get_model_pricing_all_variations(self, sample_pricing_data):
        """Test getting pricing with all model name variations."""
        fetcher = PricingFetcher()
        pricing_data = {
            "anthropic/claude-sonnet": ModelPricing(**sample_pricing_data["claude-sonnet-4-20250514"])
        }
        
        # Test each variation pattern
        variations = [
            "claude-sonnet",
            "anthropic/claude-sonnet", 
            "claude-3-5-claude-sonnet",
            "claude-3-claude-sonnet",
            "claude-claude-sonnet",
        ]
        
        for variation in variations:
            result = fetcher.get_model_pricing(variation, pricing_data)
            assert isinstance(result, Ok)
            # Should find the match for the anthropic/ variant
            if variation == "anthropic/claude-sonnet":
                assert result.value is not None
    
    def test_get_model_pricing_empty_model_name(self, sample_pricing_data):
        """Test getting pricing with empty model name."""
        fetcher = PricingFetcher()
        pricing_data = {
            model: ModelPricing(**data) for model, data in sample_pricing_data.items()
        }
        
        result = fetcher.get_model_pricing("", pricing_data)
        assert isinstance(result, Ok)
        # Empty string matches the first key due to partial matching logic
        assert result.value is not None
    
    @pytest.mark.asyncio
    async def test_calculate_cost_from_tokens_with_context(self, sample_pricing_data):
        """Test calculating cost from tokens with context parameter."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = sample_pricing_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            fetcher = PricingFetcher()
            result = await fetcher.calculate_cost_from_tokens(
                input_tokens=1000,
                output_tokens=500,
                model_name="claude-sonnet-4-20250514",
                context="Test context"
            )
            
            assert isinstance(result, Ok)
            assert result.value > 0
    
    @patch('builtins.print')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_offline_pricing_cache_message_already_shown(self, mock_read_text, mock_exists, mock_print, sample_pricing_data):
        """Test loading offline pricing when cache message already shown."""
        mock_exists.return_value = True
        mock_read_text.return_value = json.dumps(sample_pricing_data)
        
        # Set cache message as already shown
        PricingFetcher._cache_message_shown = True
        
        fetcher = PricingFetcher()
        result = fetcher._load_offline_pricing()
        
        assert isinstance(result, Ok)
        # Should not print message since it was already shown
        mock_print.assert_not_called()


class TestCostCalculator:
    """Test the CostCalculator class."""
    
    def test_init(self):
        """Test CostCalculator initialization."""
        fetcher = PricingFetcher()
        calculator = CostCalculator(fetcher)
        assert calculator.pricing_fetcher is fetcher
    
    @patch.object(PricingFetcher, 'calculate_cost_from_tokens')
    @pytest.mark.asyncio
    async def test_calculate_entry_cost_success(self, mock_calculate_cost, sample_usage_entry):
        """Test successful entry cost calculation."""
        # Mock the pricing fetcher method
        mock_calculate_cost.return_value = Ok(0.0105)
        
        fetcher = PricingFetcher()
        calculator = CostCalculator(fetcher)
        
        # Use entry with cost_usd=None to force calculation
        # sample_usage_entry already has cost_usd=None from fixture
        
        result = await calculator.calculate_entry_cost(sample_usage_entry)
        
        assert isinstance(result, Ok)
        cost = result.value
        assert cost == 0.0105
    
    @pytest.mark.asyncio
    async def test_calculate_entry_cost_with_existing_cost(self, sample_usage_entry):
        """Test entry cost calculation with existing cost_usd."""
        # Create entry with existing cost
        entry_with_cost = sample_usage_entry.model_copy(update={"cost_usd": 0.05})
        
        fetcher = PricingFetcher()
        calculator = CostCalculator(fetcher)
        
        result = await calculator.calculate_entry_cost(entry_with_cost)
        
        assert isinstance(result, Ok)
        assert result.value == 0.05
    
    @patch.object(PricingFetcher, 'calculate_cost_from_tokens')
    @pytest.mark.asyncio
    async def test_calculate_entry_cost_error(self, mock_calculate_cost, sample_usage_entry):
        """Test entry cost calculation with error."""
        mock_calculate_cost.return_value = Err(Exception("Calculation failed"))
        
        fetcher = PricingFetcher()
        calculator = CostCalculator(fetcher)
        
        # Use entry with cost_usd=None to force calculation
        # sample_usage_entry already has cost_usd=None from fixture
        
        result = await calculator.calculate_entry_cost(sample_usage_entry)
        
        assert isinstance(result, Err)
        assert "Calculation failed" in str(result.error)
    
    @patch.object(CostCalculator, 'calculate_entry_cost')
    @pytest.mark.asyncio
    async def test_calculate_total_cost_success(self, mock_calculate_entry, sample_usage_entry):
        """Test calculating total cost for multiple entries."""
        mock_calculate_entry.return_value = Ok(0.01)
        
        fetcher = PricingFetcher()
        calculator = CostCalculator(fetcher)
        
        entries = [sample_usage_entry, sample_usage_entry]
        result = await calculator.calculate_total_cost(entries)
        
        assert isinstance(result, Ok)
        assert result.value == 0.02  # 2 * 0.01
    
    @patch.object(CostCalculator, 'calculate_entry_cost')
    @pytest.mark.asyncio
    async def test_calculate_total_cost_with_error(self, mock_calculate_entry, sample_usage_entry):
        """Test calculating total cost with error."""
        mock_calculate_entry.return_value = Err(Exception("Entry error"))
        
        fetcher = PricingFetcher()
        calculator = CostCalculator(fetcher)
        
        entries = [sample_usage_entry]
        result = await calculator.calculate_total_cost(entries)
        
        assert isinstance(result, Err)
        assert "Entry error" in str(result.error)
    
    @pytest.mark.asyncio
    async def test_calculate_total_cost_empty_entries(self):
        """Test calculating total cost with empty entries."""
        fetcher = PricingFetcher()
        calculator = CostCalculator(fetcher)
        
        result = await calculator.calculate_total_cost([])
        
        assert isinstance(result, Ok)
        assert result.value == 0.0
    
    @patch.object(CostCalculator, 'calculate_total_cost')
    @pytest.mark.asyncio
    async def test_calculate_usage_totals_success(self, mock_total_cost, sample_usage_entry):
        """Test calculating usage totals."""
        mock_total_cost.return_value = Ok(0.05)
        
        fetcher = PricingFetcher()
        calculator = CostCalculator(fetcher)
        
        entries = [sample_usage_entry]
        result = await calculator.calculate_usage_totals(entries)
        
        assert isinstance(result, Ok)
        totals = result.value
        assert totals.input_tokens == 1000
        assert totals.output_tokens == 500
        assert totals.cache_creation_tokens == 100
        assert totals.cache_read_tokens == 50
        assert totals.total_cost == 0.05
    
    @patch.object(CostCalculator, 'calculate_total_cost')
    @pytest.mark.asyncio
    async def test_calculate_usage_totals_error(self, mock_total_cost, sample_usage_entry):
        """Test calculating usage totals with error."""
        mock_total_cost.return_value = Err(Exception("Total cost error"))
        
        fetcher = PricingFetcher()
        calculator = CostCalculator(fetcher)
        
        entries = [sample_usage_entry]
        result = await calculator.calculate_usage_totals(entries)
        
        assert isinstance(result, Err)
        assert "Total cost error" in str(result.error)


def test_model_pricing_model():
    """Test ModelPricing model."""
    pricing = ModelPricing(
        max_tokens=4096,
        max_input_tokens=200000,
        max_output_tokens=4096,
        input_cost_per_token=0.000003,
        output_cost_per_token=0.000015,
        litellm_provider="anthropic",
        mode="chat",
        supports_function_calling=True,
        supports_parallel_function_calling=True,
        supports_vision=True
    )
    
    assert pricing.max_tokens == 4096
    assert pricing.input_cost_per_token == 0.000003
    assert pricing.output_cost_per_token == 0.000015
    assert pricing.litellm_provider == "anthropic"
    assert pricing.supports_function_calling is True


if __name__ == "__main__":
    pytest.main([__file__])