"""Main CLI application for ccusage-py."""

from __future__ import annotations

import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.traceback import install

from .commands.daily import daily_command
from .commands.monthly import monthly_command
from .commands.session import session_command
from .core.exceptions import CcusageError
from .models.base import CostMode, SortOrder

# Install rich traceback handler
install(show_locals=True)

console = Console()

app = typer.Typer(
    name="ccusage-py",
    help="🔍 Python implementation of ccusage - Analyze your Claude Code token usage and costs",
    rich_markup_mode="rich",
    no_args_is_help=False,
    add_completion=False,
)

# Type aliases for cleaner signatures
JsonFlag = Annotated[bool, typer.Option("--json", help="Output in JSON format")]
SinceDate = Annotated[str | None, typer.Option("--since", help="Start date (YYYYMMDD)")]
UntilDate = Annotated[str | None, typer.Option("--until", help="End date (YYYYMMDD)")]
CostModeOption = Annotated[CostMode, typer.Option("--mode", help="Cost calculation mode")]
SortOrderOption = Annotated[SortOrder, typer.Option("--order", help="Sort order")]
BreakdownFlag = Annotated[bool, typer.Option("--breakdown", help="Show per-model breakdown")]
OfflineFlag = Annotated[bool, typer.Option("--offline", help="Use offline pricing data")]
GraphFlag = Annotated[bool, typer.Option("--graph", "-g", help="Show ASCII graphs for cost visualization")]
CurrencyOption = Annotated[str | None, typer.Option("--currency", help="Currency code for display (e.g., GBP, EUR). Defaults to auto-detection.")]


@app.command("daily")
def daily(
    json_output: JsonFlag = False,
    since: SinceDate = None,
    until: UntilDate = None,
    mode: CostModeOption = CostMode.AUTO,
    order: SortOrderOption = SortOrder.DESC,
    breakdown: BreakdownFlag = False,
    offline: OfflineFlag = False,
    graph: GraphFlag = False,
    currency: CurrencyOption = None,
) -> None:
    """📅 Show daily usage report."""
    daily_command(json_output, since, until, mode, order, breakdown, offline, graph, currency)


@app.command("d")
def daily_alias(
    json_output: JsonFlag = False,
    since: SinceDate = None,
    until: UntilDate = None,
    mode: CostModeOption = CostMode.AUTO,
    order: SortOrderOption = SortOrder.DESC,
    breakdown: BreakdownFlag = False,
    offline: OfflineFlag = False,
    graph: GraphFlag = False,
    currency: CurrencyOption = None,
) -> None:
    """📅 Show daily usage report."""
    daily_command(json_output, since, until, mode, order, breakdown, offline, graph, currency)


@app.command("monthly")
def monthly(
    json_output: JsonFlag = False,
    since: SinceDate = None,
    until: UntilDate = None,
    mode: CostModeOption = CostMode.AUTO,
    order: SortOrderOption = SortOrder.DESC,
    breakdown: BreakdownFlag = False,
    offline: OfflineFlag = False,
    graph: GraphFlag = False,
    currency: CurrencyOption = None,
) -> None:
    """📊 Show monthly usage report."""
    monthly_command(json_output, since, until, mode, order, breakdown, offline, graph, currency)


@app.command("m")
def monthly_alias(
    json_output: JsonFlag = False,
    since: SinceDate = None,
    until: UntilDate = None,
    mode: CostModeOption = CostMode.AUTO,
    order: SortOrderOption = SortOrder.DESC,
    breakdown: BreakdownFlag = False,
    offline: OfflineFlag = False,
    graph: GraphFlag = False,
    currency: CurrencyOption = None,
) -> None:
    """📊 Show monthly usage report."""
    monthly_command(json_output, since, until, mode, order, breakdown, offline, graph, currency)


@app.command("session")
def session(
    json_output: JsonFlag = False,
    since: SinceDate = None,
    until: UntilDate = None,
    order: SortOrderOption = SortOrder.DESC,
    breakdown: BreakdownFlag = False,
    offline: OfflineFlag = False,
    graph: GraphFlag = False,
    currency: CurrencyOption = None,
) -> None:
    """💬 Show session usage report."""
    session_command(json_output, since, until, order, breakdown, offline, graph, currency)


@app.command("s")
def session_alias(
    json_output: JsonFlag = False,
    since: SinceDate = None,
    until: UntilDate = None,
    order: SortOrderOption = SortOrder.DESC,
    breakdown: BreakdownFlag = False,
    offline: OfflineFlag = False,
    graph: GraphFlag = False,
    currency: CurrencyOption = None,
) -> None:
    """💬 Show session usage report."""
    session_command(json_output, since, until, order, breakdown, offline, graph, currency)


@app.command("sessions")
def sessions_alias(
    json_output: JsonFlag = False,
    since: SinceDate = None,
    until: UntilDate = None,
    order: SortOrderOption = SortOrder.DESC,
    breakdown: BreakdownFlag = False,
    offline: OfflineFlag = False,
    graph: GraphFlag = False,
    currency: CurrencyOption = None,
) -> None:
    """💬 Show session usage report."""
    session_command(json_output, since, until, order, breakdown, offline, graph, currency)


@app.command("today")
def today(
    json_output: JsonFlag = False,
    order: SortOrderOption = SortOrder.DESC,
    breakdown: BreakdownFlag = False,
    offline: OfflineFlag = False,
    graph: GraphFlag = False,
    currency: CurrencyOption = None,
) -> None:
    """🕐 Show today's session usage report."""
    from datetime import date
    today_str = date.today().strftime("%Y%m%d")
    session_command(json_output, today_str, today_str, order, breakdown, offline, graph, currency)


@app.command("t")
def today_alias(
    json_output: JsonFlag = False,
    order: SortOrderOption = SortOrder.DESC,
    breakdown: BreakdownFlag = False,
    offline: OfflineFlag = False,
    graph: GraphFlag = False,
    currency: CurrencyOption = None,
) -> None:
    """🕐 Show today's session usage report."""
    from datetime import date
    today_str = date.today().strftime("%Y%m%d")
    session_command(json_output, today_str, today_str, order, breakdown, offline, graph, currency)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[bool, typer.Option("--version", help="Show version")] = False,
) -> None:
    """Main callback - default to today command if no subcommand specified."""
    if version:
        from . import __version__
        console.print(f"ccusage-py version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        # Default to today command
        today()


def cli_main() -> None:
    """Entry point for CLI."""
    try:
        app()
    except CcusageError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
