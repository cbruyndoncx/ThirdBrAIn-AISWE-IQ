"""Integration tests for cost calculation functionality."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import json

import pytest

from ccusage.data.processor import DataProcessor
from ccusage.models.usage import RawUsageEntry, ModelPricing
from ccusage.models.base import CostMode
from ccusage.core.result import ok, err


@pytest.fixture
def sample_entries_mixed_costs():
    """Sample entries with mixed cost_usd values."""
    return [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            request_id="req-1",
            message_id="msg-1",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=100,
            cache_read_tokens=50,
            cost_usd=None,  # No pre-calculated cost
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 14, 0, 0),
            session_id="session-1",
            request_id="req-2",
            message_id="msg-2",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=2000,
            output_tokens=1000,
            cache_creation_tokens=0,
            cache_read_tokens=200,
            cost_usd=0.05,  # Has pre-calculated cost
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 16, 10, 0, 0),
            session_id="session-2",
            request_id="req-3",
            message_id="msg-3",
            model_name="claude-3-opus-20240229",
            input_tokens=500,
            output_tokens=250,
            cache_creation_tokens=50,
            cache_read_tokens=25,
            cost_usd=None,  # No pre-calculated cost
            project_path="/project2",
            version="1.0.43",
        ),
    ]


@pytest.fixture
def mock_pricing_data():
    """Mock pricing data."""
    return {
        "claude-3-5-sonnet-20241022": ModelPricing(
            max_tokens=4096,
            max_input_tokens=200000,
            max_output_tokens=4096,
            input_cost_per_token=0.000003,
            output_cost_per_token=0.000015,
            cache_creation_input_token_cost=0.000003,
            cache_read_input_token_cost=0.0000003,
            litellm_provider="anthropic",
            mode="chat",
        ),
        "claude-3-opus-20240229": ModelPricing(
            max_tokens=4096,
            max_input_tokens=200000,
            max_output_tokens=4096,
            input_cost_per_token=0.000015,
            output_cost_per_token=0.000075,
            cache_creation_input_token_cost=0.000015,
            cache_read_input_token_cost=0.0000015,
            litellm_provider="anthropic",
            mode="chat",
        ),
    }


@pytest.mark.asyncio
async def test_integration_cost_calculation_auto_mode(sample_entries_mixed_costs, mock_pricing_data):
    """Test integration of cost calculation in AUTO mode with mixed pre-calculated and calculated costs."""
    processor = DataProcessor(cost_mode=CostMode.AUTO, offline=False)
    
    # Mock the pricing fetcher
    with patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock fetch_pricing_data to return our mock data
        mock_fetcher.fetch_pricing_data.return_value = ok(mock_pricing_data)
        
        # Mock get_model_pricing to return appropriate pricing
        def mock_get_model_pricing(model_name, pricing_data):
            if model_name in pricing_data:
                return ok(pricing_data[model_name])
            return ok(None)
        
        mock_fetcher.get_model_pricing.side_effect = mock_get_model_pricing
        
        # Mock calculate_cost_from_tokens to return calculated costs
        async def mock_calculate_cost_from_tokens(input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, model_name, context=""):
            pricing = mock_pricing_data.get(model_name)
            if pricing:
                cost = (
                    input_tokens * pricing.input_cost_per_token +
                    output_tokens * pricing.output_cost_per_token +
                    cache_creation_tokens * pricing.cache_creation_input_token_cost +
                    cache_read_tokens * pricing.cache_read_input_token_cost
                )
                return ok(cost)
            return ok(0.0)
        
        mock_fetcher.calculate_cost_from_tokens = mock_calculate_cost_from_tokens
        
        # Process daily usage
        result = await processor.process_daily_usage(sample_entries_mixed_costs)
        
        assert result.is_ok()
        daily_usage = result.value
        
        # Should have 2 days
        assert len(daily_usage) == 2
        
        # Check July 15 - has 1 entry with pre-calculated cost and 1 without
        july_15 = next(d for d in daily_usage if d.date == "2025-07-15")
        # Should have pre-calculated cost (0.05) plus calculated cost for first entry
        assert july_15.total_cost > 0.05  # Greater than just pre-calculated cost
        assert july_15.total_cost < 0.1   # Reasonable upper bound
        
        # Check July 16 - has 1 entry without pre-calculated cost
        july_16 = next(d for d in daily_usage if d.date == "2025-07-16")
        # Should have calculated cost only (no pre-calculated cost)
        assert july_16.total_cost > 0.0   # Has calculated cost
        assert july_16.total_cost < 0.1   # Reasonable upper bound


@pytest.mark.asyncio
async def test_integration_cost_calculation_calculate_mode(sample_entries_mixed_costs, mock_pricing_data):
    """Test integration of cost calculation in CALCULATE mode - should ignore pre-calculated costs."""
    processor = DataProcessor(cost_mode=CostMode.CALCULATE, offline=False)
    
    # Mock the pricing fetcher
    with patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock fetch_pricing_data to return our mock data
        mock_fetcher.fetch_pricing_data.return_value = ok(mock_pricing_data)
        
        # Mock get_model_pricing to return appropriate pricing
        def mock_get_model_pricing(model_name, pricing_data):
            if model_name in pricing_data:
                return ok(pricing_data[model_name])
            return ok(None)
        
        mock_fetcher.get_model_pricing.side_effect = mock_get_model_pricing
        
        # Mock calculate_cost_from_tokens to return calculated costs
        async def mock_calculate_cost_from_tokens(input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, model_name, context=""):
            pricing = mock_pricing_data.get(model_name)
            if pricing:
                cost = (
                    input_tokens * pricing.input_cost_per_token +
                    output_tokens * pricing.output_cost_per_token +
                    cache_creation_tokens * pricing.cache_creation_input_token_cost +
                    cache_read_tokens * pricing.cache_read_input_token_cost
                )
                return ok(cost)
            return ok(0.0)
        
        mock_fetcher.calculate_cost_from_tokens = mock_calculate_cost_from_tokens
        
        # Process daily usage
        result = await processor.process_daily_usage(sample_entries_mixed_costs)
        
        assert result.is_ok()
        daily_usage = result.value
        
        # Should have 2 days
        assert len(daily_usage) == 2
        
        # Check July 15 - both entries should be calculated (ignore pre-calculated 0.05)
        july_15 = next(d for d in daily_usage if d.date == "2025-07-15")
        # Should have calculated costs for both entries
        assert july_15.total_cost > 0.01   # Has meaningful calculated cost
        assert july_15.total_cost < 0.1    # Reasonable upper bound
        
        # Check July 16 - should be calculated
        july_16 = next(d for d in daily_usage if d.date == "2025-07-16")
        # Should have calculated cost
        assert july_16.total_cost > 0.01   # Has meaningful calculated cost
        assert july_16.total_cost < 0.1    # Reasonable upper bound


@pytest.mark.asyncio
async def test_integration_cost_calculation_display_mode(sample_entries_mixed_costs):
    """Test integration of cost calculation in DISPLAY mode - should only use pre-calculated costs."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY, offline=False)
    
    # Process daily usage
    result = await processor.process_daily_usage(sample_entries_mixed_costs)
    
    assert result.is_ok()
    daily_usage = result.value
    
    # Should have 2 days
    assert len(daily_usage) == 2
    
    # Check July 15 - only entry with pre-calculated cost contributes
    july_15 = next(d for d in daily_usage if d.date == "2025-07-15")
    assert july_15.total_cost == 0.05  # Only the pre-calculated cost
    
    # Check July 16 - no pre-calculated cost
    july_16 = next(d for d in daily_usage if d.date == "2025-07-16")
    assert july_16.total_cost == 0.0  # No pre-calculated cost available


@pytest.mark.asyncio
async def test_integration_cost_calculation_offline_mode_with_cache(sample_entries_mixed_costs):
    """Test integration of cost calculation in offline mode with cached pricing data."""
    processor = DataProcessor(cost_mode=CostMode.CALCULATE, offline=True)
    
    # Mock the pricing fetcher to simulate cached data
    with patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock _load_offline_pricing to return cached data
        mock_pricing_data = {
            "claude-3-5-sonnet-20241022": ModelPricing(
                max_tokens=4096,
                max_input_tokens=200000,
                max_output_tokens=4096,
                input_cost_per_token=0.000003,
                output_cost_per_token=0.000015,
                cache_creation_input_token_cost=0.000003,
                cache_read_input_token_cost=0.0000003,
                litellm_provider="anthropic",
                mode="chat",
            ),
        }
        mock_fetcher.fetch_pricing_data.return_value = ok(mock_pricing_data)
        
        # Mock get_model_pricing to return appropriate pricing
        def mock_get_model_pricing(model_name, pricing_data):
            if model_name in pricing_data:
                return ok(pricing_data[model_name])
            return ok(None)
        
        mock_fetcher.get_model_pricing.side_effect = mock_get_model_pricing
        
        # Mock calculate_cost_from_tokens
        async def mock_calculate_cost_from_tokens(input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, model_name, context=""):
            if model_name == "claude-3-5-sonnet-20241022":
                pricing = mock_pricing_data[model_name]
                cost = (
                    input_tokens * pricing.input_cost_per_token +
                    output_tokens * pricing.output_cost_per_token +
                    cache_creation_tokens * pricing.cache_creation_input_token_cost +
                    cache_read_tokens * pricing.cache_read_input_token_cost
                )
                return ok(cost)
            return ok(0.0)  # Unknown model
        
        mock_fetcher.calculate_cost_from_tokens = mock_calculate_cost_from_tokens
        
        # Process daily usage
        result = await processor.process_daily_usage(sample_entries_mixed_costs)
        
        assert result.is_ok()
        daily_usage = result.value
        
        # Should have 2 days
        assert len(daily_usage) == 2
        
        # Check July 15 - both entries should be calculated
        july_15 = next(d for d in daily_usage if d.date == "2025-07-15")
        # Should have calculated costs for both entries
        assert july_15.total_cost > 0.01   # Has meaningful calculated cost
        assert july_15.total_cost < 0.1    # Reasonable upper bound
        
        # Check July 16 - opus model not in cache, should return 0.0
        july_16 = next(d for d in daily_usage if d.date == "2025-07-16")
        assert july_16.total_cost == 0.0  # Model not in cache
        
        # Verify offline mode was used
        mock_fetcher_class.assert_called_with(offline=True)


@pytest.mark.asyncio
async def test_integration_cost_calculation_error_handling(sample_entries_mixed_costs):
    """Test integration of cost calculation with error handling."""
    processor = DataProcessor(cost_mode=CostMode.CALCULATE, offline=False)
    
    # Mock the pricing fetcher to return an error
    with patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock fetch_pricing_data to return an error
        mock_fetcher.fetch_pricing_data.return_value = err(Exception("Network error"))
        
        # Mock calculate_cost_from_tokens to also return an error
        async def mock_calculate_cost_from_tokens(input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, model_name, context=""):
            return err(Exception("Pricing calculation failed"))
        
        mock_fetcher.calculate_cost_from_tokens = mock_calculate_cost_from_tokens
        
        # Process daily usage
        result = await processor.process_daily_usage(sample_entries_mixed_costs)
        
        assert result.is_ok()
        daily_usage = result.value
        
        # Should have 2 days
        assert len(daily_usage) == 2
        
        # All costs should be 0.0 due to pricing errors
        for day in daily_usage:
            assert day.total_cost == 0.0


@pytest.mark.asyncio
async def test_integration_totals_calculation(sample_entries_mixed_costs, mock_pricing_data):
    """Test integration of totals calculation with cost calculation."""
    processor = DataProcessor(cost_mode=CostMode.AUTO, offline=False)
    
    # Mock the pricing fetcher
    with patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock fetch_pricing_data to return our mock data
        mock_fetcher.fetch_pricing_data.return_value = ok(mock_pricing_data)
        
        # Mock get_model_pricing to return appropriate pricing
        def mock_get_model_pricing(model_name, pricing_data):
            if model_name in pricing_data:
                return ok(pricing_data[model_name])
            return ok(None)
        
        mock_fetcher.get_model_pricing.side_effect = mock_get_model_pricing
        
        # Mock calculate_cost_from_tokens to return calculated costs
        async def mock_calculate_cost_from_tokens(input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, model_name, context=""):
            pricing = mock_pricing_data.get(model_name)
            if pricing:
                cost = (
                    input_tokens * pricing.input_cost_per_token +
                    output_tokens * pricing.output_cost_per_token +
                    cache_creation_tokens * pricing.cache_creation_input_token_cost +
                    cache_read_tokens * pricing.cache_read_input_token_cost
                )
                return ok(cost)
            return ok(0.0)
        
        mock_fetcher.calculate_cost_from_tokens = mock_calculate_cost_from_tokens
        
        # Calculate totals
        result = await processor.calculate_totals(sample_entries_mixed_costs)
        
        assert result.is_ok()
        totals = result.value
        
        # Check token totals
        assert totals.input_tokens == 3500  # 1000 + 2000 + 500
        assert totals.output_tokens == 1750  # 500 + 1000 + 250
        assert totals.cache_creation_tokens == 150  # 100 + 0 + 50
        assert totals.cache_read_tokens == 275  # 50 + 200 + 25
        
        # Check total cost (pre-calculated + calculated)
        # Should have pre-calculated cost (0.05) plus calculated costs for entries without cost_usd
        assert totals.total_cost > 0.05    # Greater than just pre-calculated cost
        assert totals.total_cost < 0.15    # Reasonable upper bound


if __name__ == "__main__":
    pytest.main([__file__])