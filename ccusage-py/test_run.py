#!/usr/bin/env python3
"""Test script to verify ccusage-py implementation."""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console

from ccusage.core.result import is_ok
from ccusage.models.base import format_currency, format_model_name, format_number
from ccusage.models.usage import DailyUsage
from ccusage.presentation.formatter import ResponsiveTableFormatter
from ccusage.pricing.fetcher import PricingFetcher


async def test_pricing_fetcher():
    """Test pricing fetcher."""
    console = Console()
    console.print("[bold blue]Testing PricingFetcher...[/bold blue]")

    # Test offline mode
    fetcher = PricingFetcher(offline=True)
    pricing_result = fetcher.fetch_pricing_data()

    if is_ok(pricing_result):
        pricing = pricing_result.value
        console.print(f"✅ Loaded {len(pricing)} offline pricing models")

        # Test specific model pricing
        model_result = fetcher.get_model_pricing("claude-sonnet-4-20250514", pricing)
        if is_ok(model_result) and model_result.value:
            console.print("✅ Found Claude Sonnet 4 pricing")
        else:
            console.print("❌ Could not find Claude Sonnet 4 pricing")
    else:
        console.print(f"❌ Failed to load pricing: {pricing_result.error}")


def test_table_formatting():
    """Test table formatting."""
    console = Console()
    console.print("[bold blue]Testing Table Formatting...[/bold blue]")

    # Create sample data
    sample_data = [
        DailyUsage(
            date="2024-01-01",
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=100,
            cache_read_tokens=50,
            total_cost=0.15,
            models_used=["claude-sonnet-4-20250514", "claude-opus-4-20250514"],
            model_breakdowns=[],
        ),
        DailyUsage(
            date="2024-01-02",
            input_tokens=800,
            output_tokens=400,
            cache_creation_tokens=80,
            cache_read_tokens=40,
            total_cost=0.12,
            models_used=["claude-sonnet-4-20250514"],
            model_breakdowns=[],
        ),
    ]

    formatter = ResponsiveTableFormatter(console)
    table = formatter.format_daily_table(sample_data)
    console.print(table)

    # Test summary panel
    summary = formatter.format_summary_panel(3970, 0.27)
    console.print(summary)

    console.print("✅ Table formatting test completed")


def test_model_utilities():
    """Test model utilities."""
    console = Console()
    console.print("[bold blue]Testing Model Utilities...[/bold blue]")

    # Test model name formatting
    test_cases = [
        ("claude-sonnet-4-20250514", "sonnet-4"),
        ("claude-opus-4-20250514", "opus-4"),
        ("custom-model", "custom-model"),
    ]

    for input_name, expected in test_cases:
        result = format_model_name(input_name)
        if result == expected:
            console.print(f"✅ {input_name} -> {result}")
        else:
            console.print(f"❌ {input_name} -> {result} (expected {expected})")

    # Test number formatting
    assert format_number(1000) == "1,000"
    assert format_number(1000000) == "1,000,000"
    console.print("✅ Number formatting works")

    # Test currency formatting
    assert format_currency(1.23) == "$1.23"
    assert format_currency(0.001) == "$0.00"
    console.print("✅ Currency formatting works")


async def main():
    """Run all tests."""
    console = Console()
    console.print("[bold green]🔍 ccusage-py Test Suite[/bold green]")
    console.print()

    # Test model utilities
    test_model_utilities()
    console.print()

    # Test pricing fetcher
    await test_pricing_fetcher()
    console.print()

    # Test table formatting
    test_table_formatting()
    console.print()

    console.print("[bold green]✅ All tests completed![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
