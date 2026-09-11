"""Daily usage command implementation."""

from __future__ import annotations

import json

from rich.console import Console

from ..core.exceptions import CcusageError
from ..core.result import is_err, is_ok, unwrap
from ..core.utils import get_claude_paths, validate_claude_paths
from ..data.loader import DataLoader
from ..data.processor import DataProcessor
from ..models.base import CostMode, SortOrder
from ..presentation.formatter import ResponsiveTableFormatter
from ..currency import CurrencyConverter, LocaleDetector
from ..currency.converter import CurrencyMode

console = Console()


def _convert_date_format(date_str: str | None) -> str | None:
    """Convert date from compact format (20250715) to ISO format (2025-07-15)."""
    if not date_str:
        return None
    
    # If already in ISO format, return as-is
    if "-" in date_str:
        return date_str
    
    # Convert from compact format (YYYYMMDD) to ISO format (YYYY-MM-DD)
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    
    return date_str


def daily_command(
    json_output: bool = False,
    since: str | None = None,
    until: str | None = None,
    mode: CostMode = CostMode.AUTO,
    order: SortOrder = SortOrder.DESC,
    breakdown: bool = False,
    offline: bool = False,
    graph: bool = False,
    currency: str | None = None,
) -> None:
    """Show usage report grouped by date."""
    import asyncio

    asyncio.run(_daily_command_async(json_output, since, until, mode, order, breakdown, offline, graph, currency))


async def _daily_command_async(
    json_output: bool,
    since: str | None,
    until: str | None,
    mode: CostMode,
    order: SortOrder,
    breakdown: bool,
    offline: bool,
    graph: bool,
    currency: str | None,
) -> None:
    """Async implementation of daily command."""
    try:
        # Suppress logging for JSON output
        if json_output:
            import logging
            logging.getLogger().setLevel(logging.ERROR)

        # Get Claude paths
        claude_paths = get_claude_paths()
        validate_claude_paths(claude_paths)

        # Load data
        loader = DataLoader(claude_paths)
        entries_result = await loader.load_raw_entries()

        if is_err(entries_result):
            raise CcusageError(f"Failed to load data: {entries_result.error}")

        entries = unwrap(entries_result)

        if not entries:
            if json_output:
                console.print_json("[]")
            else:
                console.print("[yellow]No Claude usage data found.[/yellow]")
            return

        # Process data
        processor = DataProcessor(mode, offline)
        daily_result = await processor.process_daily_usage(
            entries, 
            _convert_date_format(since), 
            _convert_date_format(until), 
            order
        )

        if is_err(daily_result):
            raise CcusageError(f"Failed to process data: {daily_result.error}")

        daily_data = unwrap(daily_result)

        if json_output:
            # Output JSON format
            json_output_data = {
                "daily": [
                    {
                        "date": data.date,
                        "input_tokens": data.input_tokens,
                        "output_tokens": data.output_tokens,
                        "cache_creation_tokens": data.cache_creation_tokens,
                        "cache_read_tokens": data.cache_read_tokens,
                        "total_tokens": data.total_tokens,
                        "total_cost": data.total_cost,
                        "models_used": data.models_used,
                        "model_breakdowns": [
                            {
                                "model_name": b.model_name,
                                "input_tokens": b.input_tokens,
                                "output_tokens": b.output_tokens,
                                "cache_creation_tokens": b.cache_creation_tokens,
                                "cache_read_tokens": b.cache_read_tokens,
                                "total_tokens": b.total_tokens,
                                "cost": b.cost,
                            }
                            for b in data.model_breakdowns
                        ],
                    }
                    for data in daily_data
                ],
            }
            console.print_json(json.dumps(json_output_data, indent=2))
        else:
            # Set up currency conversion
            currency_mode = CurrencyMode.AUTO
            target_currency = None
            
            if currency:
                currency_mode = CurrencyMode.CUSTOM
                target_currency = currency.upper()
            
            # Initialize currency converter
            cache_dir = claude_paths[0].parent / "currency_cache" 
            async with CurrencyConverter(cache_dir, currency_mode, target_currency) as converter:
                currency_code = converter.get_currency_code()
                currency_symbol = converter.get_currency_symbol()
                
                # Convert costs in daily_data if not USD
                if currency_code != "USD":
                    converted_daily_data = []
                    for daily_usage in daily_data:
                        # Convert main cost
                        cost_result = await converter.convert_amount(daily_usage.total_cost)
                        converted_cost = unwrap(cost_result) if cost_result.is_ok() else daily_usage.total_cost
                        
                        # Convert model breakdown costs
                        converted_breakdowns = []
                        for breakdown in daily_usage.model_breakdowns:
                            breakdown_cost_result = await converter.convert_amount(breakdown.cost)
                            converted_breakdown_cost = unwrap(breakdown_cost_result) if breakdown_cost_result.is_ok() else breakdown.cost
                            
                            # Create new breakdown with converted cost
                            converted_breakdown = breakdown.model_copy(update={"cost": converted_breakdown_cost})
                            converted_breakdowns.append(converted_breakdown)
                        
                        # Create new daily usage with converted cost and breakdowns
                        converted_daily_usage = daily_usage.model_copy(update={
                            "total_cost": converted_cost,
                            "model_breakdowns": converted_breakdowns
                        })
                        converted_daily_data.append(converted_daily_usage)
                    
                    daily_data = converted_daily_data
                
                # Format table output
                formatter = ResponsiveTableFormatter(console, currency_code, currency_symbol)
                table = formatter.format_daily_table(daily_data, breakdown)
                console.print(table)
                
                # Add graphs if requested
                if graph and daily_data:
                    # Cost bar chart
                    cost_chart = formatter.graph_generator.generate_cost_bar_chart(
                        daily_data, 
                        max_width=min(80, formatter.terminal_width - 10),
                        title="📊 Daily Cost Distribution"
                    )
                    console.print(cost_chart)
                    
                    # Cost trend sparkline
                    if len(daily_data) > 1:
                        sparkline = formatter.graph_generator.generate_sparkline(
                            daily_data,
                            max_width=min(60, formatter.terminal_width - 20),
                            title="📈 Cost Trend"
                        )
                        console.print(sparkline)

            # Calculate and show totals
            totals_result = await processor.calculate_totals(entries)
            if is_ok(totals_result):
                totals = unwrap(totals_result)
                summary_panel = formatter.format_summary_panel(
                    totals.total_tokens, totals.total_cost
                )
                console.print(summary_panel)

    except CcusageError:
        raise
    except Exception as e:
        raise CcusageError(f"Daily command failed: {e}") from e
