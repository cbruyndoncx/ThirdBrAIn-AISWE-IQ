"""Session usage command implementation."""

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


def session_command(
    json_output: bool = False,
    since: str | None = None,
    until: str | None = None,
    order: SortOrder = SortOrder.DESC,
    breakdown: bool = False,
    offline: bool = False,
    graph: bool = False,
    currency: str | None = None,
) -> None:
    """Show usage report grouped by session."""
    import asyncio

    asyncio.run(_session_command_async(json_output, since, until, order, breakdown, offline, graph, currency))


async def _session_command_async(
    json_output: bool,
    since: str | None,
    until: str | None,
    order: SortOrder,
    breakdown: bool,
    offline: bool,
    graph: bool,
    currency: str | None,
) -> None:
    """Async implementation of session command."""
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
        processor = DataProcessor(CostMode.AUTO, offline)
        session_result = await processor.process_session_usage(
            entries, 
            _convert_date_format(since), 
            _convert_date_format(until), 
            order
        )

        if is_err(session_result):
            raise CcusageError(f"Failed to process data: {session_result.error}")

        session_data = unwrap(session_result)

        if json_output:
            # Output JSON format
            json_output_data = {
                "sessions": [
                    {
                        "session_id": data.session_id,
                        "project_path": data.project_path,
                        "input_tokens": data.input_tokens,
                        "output_tokens": data.output_tokens,
                        "cache_creation_tokens": data.cache_creation_tokens,
                        "cache_read_tokens": data.cache_read_tokens,
                        "total_tokens": data.total_tokens,
                        "total_cost": data.total_cost,
                        "last_activity": data.last_activity.isoformat(),
                        "versions": data.versions,
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
                    for data in session_data
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
                
                # Convert costs in session_data if not USD
                if currency_code != "USD":
                    converted_session_data = []
                    for session_usage in session_data:
                        # Convert main cost
                        cost_result = await converter.convert_amount(session_usage.total_cost)
                        converted_cost = unwrap(cost_result) if cost_result.is_ok() else session_usage.total_cost
                        
                        # Convert model breakdown costs
                        converted_breakdowns = []
                        for breakdown in session_usage.model_breakdowns:
                            breakdown_cost_result = await converter.convert_amount(breakdown.cost)
                            converted_breakdown_cost = unwrap(breakdown_cost_result) if breakdown_cost_result.is_ok() else breakdown.cost
                            
                            # Create new breakdown with converted cost
                            converted_breakdown = breakdown.model_copy(update={"cost": converted_breakdown_cost})
                            converted_breakdowns.append(converted_breakdown)
                        
                        # Create new session usage with converted cost and breakdowns
                        converted_session_usage = session_usage.model_copy(update={
                            "total_cost": converted_cost,
                            "model_breakdowns": converted_breakdowns
                        })
                        converted_session_data.append(converted_session_usage)
                    
                    session_data = converted_session_data
                
                # Format table output
                formatter = ResponsiveTableFormatter(console, currency_code, currency_symbol)
                table = formatter.format_session_table(session_data, breakdown)
                console.print(table)
                
                # Add graphs if requested
                if graph and session_data:
                    # Session activity chart
                    activity_chart = formatter.graph_generator.generate_session_activity_chart(
                        session_data,
                        max_width=min(80, formatter.terminal_width - 10),
                        title="📊 Session Activity"
                    )
                    console.print(activity_chart)
                    
                    # Cost comparison chart
                    cost_comparison = formatter.graph_generator.generate_cost_comparison_chart(
                        session_data,
                        max_width=min(80, formatter.terminal_width - 10),
                        title="📈 Cost Analysis"
                    )
                    console.print(cost_comparison)

            # Calculate and show totals from filtered data
            if session_data:
                filtered_total_tokens = sum(usage.total_tokens for usage in session_data)
                filtered_total_cost = sum(usage.total_cost for usage in session_data)
                
                # Determine labels based on filtering
                if since and until and since == until:
                    # Today view or specific date
                    from datetime import date
                    today_str = date.today().strftime("%Y-%m-%d")
                    if _convert_date_format(since) == today_str:
                        tokens_label = "Today Total Tokens"
                        cost_label = "Today Total Cost"
                    else:
                        tokens_label = "Day Total Tokens"
                        cost_label = "Day Total Cost"
                elif since or until:
                    # Date range filtering
                    tokens_label = "Filtered Total Tokens"
                    cost_label = "Filtered Total Cost"
                else:
                    # No filtering
                    tokens_label = "Total Tokens"
                    cost_label = "Total Cost"
                
                summary_panel = formatter.format_summary_panel(
                    filtered_total_tokens, filtered_total_cost, tokens_label, cost_label
                )
                console.print(summary_panel)

    except CcusageError:
        raise
    except Exception as e:
        raise CcusageError(f"Session command failed: {e}") from e
