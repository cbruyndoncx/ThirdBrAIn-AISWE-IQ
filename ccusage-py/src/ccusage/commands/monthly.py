"""Monthly usage command implementation."""

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


def monthly_command(
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
    """Show usage report grouped by month."""
    import asyncio

    asyncio.run(_monthly_command_async(json_output, since, until, mode, order, breakdown, offline, graph, currency))


async def _monthly_command_async(
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
    """Async implementation of monthly command."""
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
        monthly_result = await processor.process_monthly_usage(entries, since, until, order)

        if is_err(monthly_result):
            raise CcusageError(f"Failed to process data: {monthly_result.error}")

        monthly_data = unwrap(monthly_result)

        if json_output:
            # Output JSON format
            json_output_data = {
                "monthly": [
                    {
                        "month": data.month,
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
                    for data in monthly_data
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
                
                # Convert costs in monthly_data if not USD
                if currency_code != "USD":
                    converted_monthly_data = []
                    for monthly_usage in monthly_data:
                        # Convert main cost
                        cost_result = await converter.convert_amount(monthly_usage.total_cost)
                        converted_cost = unwrap(cost_result) if cost_result.is_ok() else monthly_usage.total_cost
                        
                        # Convert model breakdown costs
                        converted_breakdowns = []
                        for breakdown in monthly_usage.model_breakdowns:
                            breakdown_cost_result = await converter.convert_amount(breakdown.cost)
                            converted_breakdown_cost = unwrap(breakdown_cost_result) if breakdown_cost_result.is_ok() else breakdown.cost
                            
                            # Create new breakdown with converted cost
                            converted_breakdown = breakdown.model_copy(update={"cost": converted_breakdown_cost})
                            converted_breakdowns.append(converted_breakdown)
                        
                        # Create new monthly usage with converted cost and breakdowns
                        converted_monthly_usage = monthly_usage.model_copy(update={
                            "total_cost": converted_cost,
                            "model_breakdowns": converted_breakdowns
                        })
                        converted_monthly_data.append(converted_monthly_usage)
                    
                    monthly_data = converted_monthly_data
                
                # Format table output
                formatter = ResponsiveTableFormatter(console, currency_code, currency_symbol)
                table = formatter.format_monthly_table(monthly_data, breakdown)
                console.print(table)
                
                # Add graphs if requested
                if graph and monthly_data:
                    # Cost bar chart
                    cost_chart = formatter.graph_generator.generate_cost_bar_chart(
                        monthly_data, 
                        max_width=min(80, formatter.terminal_width - 10),
                        title="📊 Monthly Cost Distribution"
                    )
                    console.print(cost_chart)
                    
                    # Cost trend sparkline
                    if len(monthly_data) > 1:
                        sparkline = formatter.graph_generator.generate_sparkline(
                            monthly_data,
                            max_width=min(60, formatter.terminal_width - 20),
                            title="📈 Monthly Cost Trend"
                        )
                        console.print(sparkline)

            # Calculate and show totals from filtered data
            if monthly_data:
                filtered_total_tokens = sum(usage.total_tokens for usage in monthly_data)
                filtered_total_cost = sum(usage.total_cost for usage in monthly_data)
                
                # Use monthly-specific labels
                tokens_label = "Monthly Total Tokens"
                cost_label = "Monthly Total Cost"
                
                summary_panel = formatter.format_summary_panel(
                    filtered_total_tokens, filtered_total_cost, tokens_label, cost_label
                )
                console.print(summary_panel)

    except CcusageError:
        raise
    except Exception as e:
        raise CcusageError(f"Monthly command failed: {e}") from e
