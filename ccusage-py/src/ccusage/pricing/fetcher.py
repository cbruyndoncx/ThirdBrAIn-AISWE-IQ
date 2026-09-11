"""Pricing fetcher for LiteLLM model costs."""

from __future__ import annotations

import json
from pathlib import Path

import requests
from pydantic import ValidationError

from ..core.constants import LITELLM_PRICING_URL
from ..core.exceptions import NetworkError, PricingError
from ..core.result import Result, err, ok
from ..models.usage import ModelPricing


class PricingFetcher:
    """Fetches and caches model pricing information from LiteLLM."""
    
    # Class-level cache shared across all instances
    _shared_pricing_cache: dict[str, ModelPricing] | None = None
    _cache_message_shown: bool = False

    def __init__(self, offline: bool = False) -> None:
        """Initialize pricing fetcher."""
        self.offline = offline
        self.base_url = LITELLM_PRICING_URL
        self.timeout = 30
        self.cache_file = Path("litellm_pricing_cache.json")

    def fetch_pricing_data(self, context: str = "") -> Result[dict[str, ModelPricing], PricingError]:
        """Fetch all available model pricing data."""
        if PricingFetcher._shared_pricing_cache is not None:
            # Only show cache message once
            if not PricingFetcher._cache_message_shown:
                print("Using cached pricing data for cost calculations.\n")
                PricingFetcher._cache_message_shown = True
            return ok(PricingFetcher._shared_pricing_cache)

        if self.offline:
            return self._load_offline_pricing(context)

        try:
            if context:
                print(f"{context}: Fetching pricing data from LiteLLM.")
            else:
                print("Fetching pricing data from LiteLLM.")
            response = requests.get(self.base_url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            pricing_dict = {}

            for model_name, model_data in data.items():
                if isinstance(model_data, dict):
                    try:
                        pricing = ModelPricing.model_validate(model_data)
                        pricing_dict[model_name] = pricing
                    except ValidationError:
                        # Skip models that don't match our schema
                        continue

            PricingFetcher._shared_pricing_cache = pricing_dict
            self._save_to_cache(pricing_dict)
            return ok(pricing_dict)

        except requests.RequestException as e:
            return err(NetworkError(f"Failed to fetch pricing data: {e}"))
        except json.JSONDecodeError as e:
            return err(PricingError(f"Failed to parse pricing data: {e}"))
        except Exception as e:
            return err(PricingError(f"Unexpected error fetching pricing: {e}"))

    def get_pricing_data(self, offline: bool = False, context: str = "") -> Result[dict[str, ModelPricing], PricingError]:
        """Get pricing data either online or offline."""
        if offline:
            return self._load_offline_pricing(context)
        else:
            return self.fetch_pricing_data(context)

    def get_model_pricing(self, model_name: str, pricing_data: dict[str, ModelPricing]) -> Result[ModelPricing | None, PricingError]:
        """Get pricing information for a specific model."""
        # Direct match
        if model_name in pricing_data:
            return ok(pricing_data[model_name])

        # Try with provider prefix variations
        variations = [
            model_name,
            f"anthropic/{model_name}",
            f"claude-3-5-{model_name}",
            f"claude-3-{model_name}",
            f"claude-{model_name}",
        ]

        for variant in variations:
            if variant in pricing_data:
                return ok(pricing_data[variant])

        # Try partial matches
        lower_model = model_name.lower()
        for key, value in pricing_data.items():
            if (
                key.lower() in lower_model
                or lower_model in key.lower()
            ):
                return ok(value)

        return ok(None)

    async def calculate_cost_from_tokens(
        self,
        input_tokens: int,
        output_tokens: int,
        cache_creation_tokens: int = 0,
        cache_read_tokens: int = 0,
        model_name: str = "",
        context: str = "",
    ) -> Result[float, PricingError]:
        """Calculate cost from token usage and model name."""
        if not model_name:
            return ok(0.0)

        pricing_result = self.fetch_pricing_data(context)
        if pricing_result.is_err():
            return err(pricing_result.error)

        pricing_data = pricing_result.value
        model_pricing_result = self.get_model_pricing(model_name, pricing_data)
        if model_pricing_result.is_err():
            return err(model_pricing_result.error)

        pricing = model_pricing_result.value
        if pricing is None:
            return ok(0.0)

        cost = self._calculate_cost_from_pricing(
            input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, pricing
        )

        return ok(cost)

    def _calculate_cost_from_pricing(
        self,
        input_tokens: int,
        output_tokens: int,
        cache_creation_tokens: int,
        cache_read_tokens: int,
        pricing: ModelPricing,
    ) -> float:
        """Calculate cost from token usage and pricing information."""
        cost = 0.0

        # Input tokens cost
        if pricing.input_cost_per_token is not None:
            cost += input_tokens * pricing.input_cost_per_token

        # Output tokens cost
        if pricing.output_cost_per_token is not None:
            cost += output_tokens * pricing.output_cost_per_token

        # Cache creation tokens cost
        if (
            cache_creation_tokens > 0
            and pricing.cache_creation_input_token_cost is not None
        ):
            cost += cache_creation_tokens * pricing.cache_creation_input_token_cost

        # Cache read tokens cost
        if (
            cache_read_tokens > 0
            and pricing.cache_read_input_token_cost is not None
        ):
            cost += cache_read_tokens * pricing.cache_read_input_token_cost

        return cost

    def _load_offline_pricing(self, context: str = "") -> Result[dict[str, ModelPricing], PricingError]:
        """Load pre-cached pricing data for offline mode."""
        if self.cache_file.exists():
            if not PricingFetcher._cache_message_shown:
                print("Using cached pricing data for cost calculations.\n")
                PricingFetcher._cache_message_shown = True
            try:
                data = json.loads(self.cache_file.read_text())
                pricing_dict = {}
                for model_name, model_data in data.items():
                    if isinstance(model_data, dict):
                        try:
                            pricing = ModelPricing.model_validate(model_data)
                            pricing_dict[model_name] = pricing
                        except ValidationError:
                            continue
                PricingFetcher._shared_pricing_cache = pricing_dict
                return ok(pricing_dict)
            except (json.JSONDecodeError, Exception) as e:
                return err(PricingError(f"Failed to parse cached pricing data: {e}"))
        else:
            return err(PricingError("No cached pricing data found for offline mode"))

    def _save_to_cache(self, pricing_data: dict[str, ModelPricing]) -> None:
        """Save pricing data to cache file."""
        try:
            # Convert ModelPricing objects to dict for JSON serialization
            json_data = {}
            for model_name, pricing in pricing_data.items():
                json_data[model_name] = pricing.model_dump()
            
            self.cache_file.write_text(json.dumps(json_data, indent=2))
        except Exception:
            # Silently ignore cache save errors
            pass

    def clear_cache(self) -> None:
        """Clear the pricing cache."""
        PricingFetcher._shared_pricing_cache = None
        PricingFetcher._cache_message_shown = False
