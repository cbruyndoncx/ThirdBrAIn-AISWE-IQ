"""Cost calculation utilities."""

from __future__ import annotations

from ..core.result import Result, err, ok
from ..models.usage import RawUsageEntry, UsageTotals
from .fetcher import PricingFetcher


class CostCalculator:
    """Calculate costs for usage data."""

    def __init__(self, pricing_fetcher: PricingFetcher) -> None:
        """Initialize cost calculator with pricing fetcher."""
        self.pricing_fetcher = pricing_fetcher

    async def calculate_entry_cost(self, entry: RawUsageEntry, context: str = "") -> Result[float, Exception]:
        """Calculate cost for a single usage entry."""
        if entry.cost_usd is not None:
            return ok(entry.cost_usd)

        cost_result = await self.pricing_fetcher.calculate_cost_from_tokens(
            entry.input_tokens,
            entry.output_tokens,
            entry.cache_creation_tokens,
            entry.cache_read_tokens,
            entry.model_name,
            context,
        )

        if cost_result.is_err():
            return err(cost_result.error)

        return ok(cost_result.value)

    async def calculate_total_cost(self, entries: list[RawUsageEntry], context: str = "") -> Result[float, Exception]:
        """Calculate total cost for a list of entries."""
        total_cost = 0.0

        for entry in entries:
            cost_result = await self.calculate_entry_cost(entry, context)
            if cost_result.is_err():
                return err(cost_result.error)

            total_cost += cost_result.value

        return ok(total_cost)

    async def calculate_usage_totals(self, entries: list[RawUsageEntry], context: str = "") -> Result[UsageTotals, Exception]:
        """Calculate usage totals for a list of entries."""
        total_input = sum(entry.input_tokens for entry in entries)
        total_output = sum(entry.output_tokens for entry in entries)
        total_cache_creation = sum(entry.cache_creation_tokens for entry in entries)
        total_cache_read = sum(entry.cache_read_tokens for entry in entries)

        total_cost_result = await self.calculate_total_cost(entries, context)
        if total_cost_result.is_err():
            return err(total_cost_result.error)

        totals = UsageTotals(
            input_tokens=total_input,
            output_tokens=total_output,
            cache_creation_tokens=total_cache_creation,
            cache_read_tokens=total_cache_read,
            total_cost=total_cost_result.value,
        )

        return ok(totals)
