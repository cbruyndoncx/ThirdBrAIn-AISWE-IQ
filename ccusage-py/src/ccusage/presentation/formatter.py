"""Rich table formatter for ccusage-py."""

from __future__ import annotations

import locale
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..core.utils import get_terminal_width
from ..models.base import format_currency, format_model_name, format_number
from ..models.usage import DailyUsage, ModelBreakdown, MonthlyUsage, SessionUsage
from .graphs import ASCIIGraphGenerator


class ResponsiveTableFormatter:
    """Rich-based responsive table formatter."""

    def __init__(self, console: Console | None = None, currency_code: str = "USD", currency_symbol: str = "$") -> None:
        """Initialize formatter with console and currency settings."""
        self.terminal_width = get_terminal_width()
        self.console = console or Console(width=self.terminal_width)
        self.is_compact = self.terminal_width < 100
        self.graph_generator = ASCIIGraphGenerator(self.console, currency_code, currency_symbol)
        self.currency_code = currency_code
        self.currency_symbol = currency_symbol

    def format_daily_usage(self, daily_data, breakdown=False, show_graphs=False):
        """Compatibility method for tests - just returns table as string."""
        table = self.format_daily_table(daily_data, breakdown)
        with self.console.capture() as capture:
            self.console.print(table)
        return capture.get()

    def format_monthly_usage(self, monthly_data, breakdown=False, show_graphs=False):
        """Compatibility method for tests - just returns table as string."""
        table = self.format_monthly_table(monthly_data, breakdown)
        with self.console.capture() as capture:
            self.console.print(table)
        return capture.get()

    def format_session_usage(self, session_data, breakdown=False, show_graphs=False):
        """Compatibility method for tests - just returns table as string."""
        table = self.format_session_table(session_data, breakdown)
        with self.console.capture() as capture:
            self.console.print(table)
        return capture.get()

    def _format_datetime(self, dt) -> str:
        """Format datetime using system locale, converting to local time."""
        # Convert UTC to local time if timezone-aware
        local_dt = dt.astimezone() if dt.tzinfo is not None else dt

        try:
            # Try to use system locale
            locale.setlocale(locale.LC_TIME, "")
            return local_dt.strftime("%x %H:%M")
        except locale.Error:
            # Fallback to default format if locale setting fails
            return local_dt.strftime("%m/%d %H:%M")

    def format_daily_table(
        self,
        daily_data: list[DailyUsage],
        show_breakdown: bool = False,
        compact_threshold: int = 100,
    ) -> Table:
        """Format daily usage data as a Rich table."""
        # Determine if we should use compact mode
        compact_mode = self.terminal_width < compact_threshold

        if compact_mode:
            return self._create_compact_daily_table(daily_data, show_breakdown)
        else:
            return self._create_full_daily_table(daily_data, show_breakdown)

    def format_monthly_table(
        self,
        monthly_data: list[MonthlyUsage],
        show_breakdown: bool = False,
        compact_threshold: int = 100,
    ) -> Table:
        """Format monthly usage data as a Rich table."""
        # Determine if we should use compact mode
        compact_mode = self.terminal_width < compact_threshold

        if compact_mode:
            return self._create_compact_monthly_table(monthly_data, show_breakdown)
        else:
            return self._create_full_monthly_table(monthly_data, show_breakdown)

    def format_session_table(
        self,
        session_data: list[SessionUsage],
        show_breakdown: bool = False,
        compact_threshold: int = 100,
    ) -> Table:
        """Format session usage data as a Rich table."""
        # Determine if we should use compact mode
        compact_mode = self.terminal_width < compact_threshold

        if compact_mode:
            return self._create_compact_session_table(session_data, show_breakdown)
        else:
            return self._create_full_session_table(session_data, show_breakdown)

    def _create_full_daily_table(
        self, daily_data: list[DailyUsage], show_breakdown: bool
    ) -> Table:
        """Create full-width daily table."""
        table = Table(
            title="📅 Daily Usage",
            show_header=True,
            header_style="bold cyan",
            title_style="bold blue",
            expand=False,
            show_lines=show_breakdown,
        )

        # Add columns
        table.add_column("Date", style="cyan", no_wrap=True)
        table.add_column("Models", style="green")
        table.add_column("Input", justify="right", style="bright_blue")
        table.add_column("Output", justify="right", style="bright_green")
        table.add_column("Cache Create", justify="right", style="bright_yellow")
        table.add_column("Cache Read", justify="right", style="bright_magenta")
        table.add_column("Total Tokens", justify="right", style="bold white")
        table.add_column(f"Cost ({self.currency_code})", justify="right", style="bold green")

        # Add data rows
        for usage in daily_data:
            # Format models display
            models_display = self._format_models_multiline(usage.models_used)

            table.add_row(
                usage.date,
                models_display,
                format_number(usage.input_tokens),
                format_number(usage.output_tokens),
                format_number(usage.cache_creation_tokens),
                format_number(usage.cache_read_tokens),
                format_number(usage.total_tokens),
                format_currency(usage.total_cost, self.currency_code, self.currency_symbol),
            )

            # Add breakdown rows if requested
            if show_breakdown and usage.model_breakdowns:
                for breakdown in usage.model_breakdowns:
                    self._add_breakdown_row(table, breakdown)

        # Handle empty data
        if not daily_data:
            table.add_row(
                "No data found",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            )

        return table

    def _create_compact_daily_table(
        self, daily_data: list[DailyUsage], show_breakdown: bool
    ) -> Table:
        """Create compact daily table for narrow terminals."""
        table = Table(
            title="📅 Daily Usage (Compact)",
            show_header=True,
            header_style="bold cyan",
            title_style="bold blue",
            expand=False,
        )

        # Compact columns
        table.add_column("Date", style="cyan", no_wrap=True)
        table.add_column("Models", style="green")
        table.add_column("Input", justify="right", style="bright_blue")
        table.add_column("Output", justify="right", style="bright_green")
        table.add_column("Cost", justify="right", style="bold green")

        for usage in daily_data:
            models_display = ", ".join(
                format_model_name(model) for model in usage.models_used[:2]
            )
            if len(usage.models_used) > 2:
                models_display += "..."

            table.add_row(
                usage.date,
                models_display,
                format_number(usage.input_tokens),
                format_number(usage.output_tokens),
                format_currency(usage.total_cost, self.currency_code, self.currency_symbol),
            )

        # Handle empty data
        if not daily_data:
            table.add_row(
                "No data found",
                "",
                "",
                "",
                "",
            )

        return table

    def _create_full_monthly_table(
        self, monthly_data: list[MonthlyUsage], show_breakdown: bool
    ) -> Table:
        """Create full-width monthly table."""
        table = Table(
            title="📊 Monthly Usage",
            show_header=True,
            header_style="bold cyan",
            title_style="bold blue",
            expand=False,
            show_lines=show_breakdown,
        )

        # Add columns
        table.add_column("Month", style="cyan", no_wrap=True)
        table.add_column("Models", style="green")
        table.add_column("Input", justify="right", style="bright_blue")
        table.add_column("Output", justify="right", style="bright_green")
        table.add_column("Cache Create", justify="right", style="bright_yellow")
        table.add_column("Cache Read", justify="right", style="bright_magenta")
        table.add_column("Total Tokens", justify="right", style="bold white")
        table.add_column(f"Cost ({self.currency_code})", justify="right", style="bold green")

        # Add data rows
        for usage in monthly_data:
            # Format models display
            models_display = self._format_models_multiline(usage.models_used)

            table.add_row(
                usage.month,
                models_display,
                format_number(usage.input_tokens),
                format_number(usage.output_tokens),
                format_number(usage.cache_creation_tokens),
                format_number(usage.cache_read_tokens),
                format_number(usage.total_tokens),
                format_currency(usage.total_cost, self.currency_code, self.currency_symbol),
            )

            # Add breakdown rows if requested
            if show_breakdown and usage.model_breakdowns:
                for breakdown in usage.model_breakdowns:
                    self._add_breakdown_row(table, breakdown)

        # Handle empty data
        if not monthly_data:
            table.add_row(
                "No data found",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            )

        return table

    def _create_compact_monthly_table(
        self, monthly_data: list[MonthlyUsage], show_breakdown: bool
    ) -> Table:
        """Create compact monthly table for narrow terminals."""
        table = Table(
            title="📊 Monthly Usage (Compact)",
            show_header=True,
            header_style="bold cyan",
            title_style="bold blue",
            expand=False,
        )

        # Compact columns
        table.add_column("Month", style="cyan", no_wrap=True)
        table.add_column("Models", style="green")
        table.add_column("Input", justify="right", style="bright_blue")
        table.add_column("Output", justify="right", style="bright_green")
        table.add_column("Cost", justify="right", style="bold green")

        for usage in monthly_data:
            models_display = ", ".join(
                format_model_name(model) for model in usage.models_used[:2]
            )
            if len(usage.models_used) > 2:
                models_display += "..."

            table.add_row(
                usage.month,
                models_display,
                format_number(usage.input_tokens),
                format_number(usage.output_tokens),
                format_currency(usage.total_cost, self.currency_code, self.currency_symbol),
            )

        # Handle empty data
        if not monthly_data:
            table.add_row(
                "No data found",
                "",
                "",
                "",
                "",
            )

        return table

    def _create_full_session_table(
        self, session_data: list[SessionUsage], show_breakdown: bool
    ) -> Table:
        """Create full-width session table."""
        table = Table(
            title="💬 Sessions",
            show_header=True,
            header_style="bold cyan",
            title_style="bold blue",
            expand=False,
            show_lines=show_breakdown,
        )

        # Add columns
        table.add_column("Session ID", style="cyan", no_wrap=True)
        table.add_column("Project", style="magenta")
        table.add_column("Models", style="green")
        table.add_column("Input", justify="right", style="bright_blue")
        table.add_column("Output", justify="right", style="bright_green")
        table.add_column("Cache Create", justify="right", style="bright_yellow")
        table.add_column("Cache Read", justify="right", style="bright_magenta")
        table.add_column("Total Tokens", justify="right", style="bold white")
        table.add_column(f"Cost ({self.currency_code})", justify="right", style="bold green")
        table.add_column("Last Activity", style="dim", no_wrap=True)

        # Add data rows
        for usage in session_data:
            # Format models display
            models_display = self._format_models_compact(usage.models_used)

            # Format project path (show only last part)
            project_display = (
                usage.project_path.split("/")[-1] if usage.project_path else ""
            )

            table.add_row(
                usage.session_id,
                project_display,
                models_display,
                format_number(usage.input_tokens),
                format_number(usage.output_tokens),
                format_number(usage.cache_creation_tokens),
                format_number(usage.cache_read_tokens),
                format_number(usage.total_tokens),
                format_currency(usage.total_cost, self.currency_code, self.currency_symbol),
                self._format_datetime(usage.last_activity),
            )

            # Add breakdown rows if requested
            if show_breakdown and usage.model_breakdowns:
                for breakdown in usage.model_breakdowns:
                    self._add_session_breakdown_row(table, breakdown)

        # Handle empty data
        if not session_data:
            table.add_row(
                "No data found",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            )

        return table

    def _create_compact_session_table(
        self, session_data: list[SessionUsage], show_breakdown: bool
    ) -> Table:
        """Create compact session table for narrow terminals."""
        table = Table(
            title="💬 Sessions (Compact)",
            show_header=True,
            header_style="bold cyan",
            title_style="bold blue",
            expand=False,
        )

        # Compact columns
        table.add_column("Session", style="cyan", no_wrap=True)
        table.add_column("Project", style="magenta")
        table.add_column("Models", style="green")
        table.add_column("Tokens", justify="right", style="bold white")
        table.add_column("Cost", justify="right", style="bold green")

        for usage in session_data:
            models_display = ", ".join(
                format_model_name(model) for model in usage.models_used[:1]
            )
            if len(usage.models_used) > 1:
                models_display += "..."
            # Add ellipsis to model names in compact mode if they're longer than 7 chars
            if len(models_display) > 7:
                models_display = models_display + "..."

            project_display = (
                usage.project_path.split("/")[-1] if usage.project_path else ""
            )
            if len(project_display) > 10:
                project_display = project_display[:10] + "..."

            table.add_row(
                usage.session_id[:9] + "..."
                if len(usage.session_id) > 12
                else usage.session_id,
                project_display,
                models_display,
                format_number(usage.total_tokens),
                format_currency(usage.total_cost, self.currency_code, self.currency_symbol),
            )

        # Handle empty data
        if not session_data:
            table.add_row(
                "No data found",
                "",
                "",
                "",
                "",
            )

        return table

    def _format_models_multiline(self, models: list[str]) -> Text:
        """Format models as multiline text with bullet points."""
        if not models:
            return Text("")

        text = Text()
        for i, model in enumerate(models):
            if i > 0:
                text.append("\n")
            text.append(f"• {format_model_name(model)}", style="dim")

        return text

    def _format_models_compact(self, models: list[str]) -> str:
        """Format models as compact comma-separated string."""
        if not models:
            return ""

        formatted = [format_model_name(model) for model in models[:2]]
        result = ", ".join(formatted)
        if len(models) > 2:
            result += "..."
        return result

    def _add_breakdown_row(self, table: Table, breakdown: ModelBreakdown) -> None:
        """Add a model breakdown row to the table."""
        table.add_row(
            "",  # Empty date
            f"  └─ {format_model_name(breakdown.model_name)}",
            Text(format_number(breakdown.input_tokens), style="dim"),
            Text(format_number(breakdown.output_tokens), style="dim"),
            Text(format_number(breakdown.cache_creation_tokens), style="dim"),
            Text(format_number(breakdown.cache_read_tokens), style="dim"),
            Text(format_number(breakdown.total_tokens), style="dim"),
            Text(format_currency(breakdown.cost, self.currency_code, self.currency_symbol), style="dim"),
        )

    def _add_session_breakdown_row(
        self, table: Table, breakdown: ModelBreakdown
    ) -> None:
        """Add a model breakdown row to the session table."""
        table.add_row(
            "",  # Empty session ID
            "",  # Empty project
            f"  └─ {format_model_name(breakdown.model_name)}",
            Text(format_number(breakdown.input_tokens), style="dim"),
            Text(format_number(breakdown.output_tokens), style="dim"),
            Text(format_number(breakdown.cache_creation_tokens), style="dim"),
            Text(format_number(breakdown.cache_read_tokens), style="dim"),
            Text(format_number(breakdown.total_tokens), style="dim"),
            Text(format_currency(breakdown.cost, self.currency_code, self.currency_symbol), style="dim"),
            "",  # Empty last activity
        )

    def format_summary_panel(
        self,
        total_tokens: int,
        total_cost: float,
        tokens_label: str = "Total Tokens",
        cost_label: str = "Total Cost",
    ) -> Panel:
        """Create a summary panel with totals."""
        summary_text = Text()
        summary_text.append(f"{tokens_label}: ", style="bold")
        summary_text.append(f"{format_number(total_tokens)}", style="bold blue")
        summary_text.append(f"\n{cost_label}: ", style="bold")
        summary_text.append(f"{format_currency(total_cost, self.currency_code, self.currency_symbol)}", style="bold green")

        return Panel(
            Align.left(summary_text),
            title="📊 Summary",
            border_style="green",
            expand=False,
        )

    def format_compact_mode_notice(self) -> Panel:
        """Create a notice panel for compact mode."""
        notice = Text()
        notice.append("Running in Compact Mode\n", style="bold yellow")
        notice.append("Expand terminal width to see all metrics", style="dim")

        return Panel(
            Align.center(notice),
            title="i Notice",
            border_style="yellow",
        )

    def _truncate_string(self, text: str, max_length: int) -> str:
        """Truncate a string to specified length."""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def _format_cost(self, cost: float) -> str:
        """Format cost as currency string."""
        return format_currency(cost, self.currency_code, self.currency_symbol)

    def _format_tokens(self, tokens: int) -> str:
        """Format tokens with comma separators."""
        return format_number(tokens)

    def _create_compact_notice(self) -> str:
        """Create a notice panel for compact mode."""
        notice = self.format_compact_mode_notice()
        with self.console.capture() as capture:
            self.console.print(notice)
        return capture.get()

    def _create_summary_panel(self, total_tokens: int, total_cost: float) -> str:
        """Create a summary panel with totals."""
        panel = self.format_summary_panel(total_tokens, total_cost)
        with self.console.capture() as capture:
            self.console.print(panel)
        return capture.get()

    def _create_breakdown_section(self, breakdowns: list[ModelBreakdown]) -> str:
        """Create a breakdown section for model breakdowns."""
        if not breakdowns:
            return ""

        result = ["Model Breakdown"]
        for breakdown in breakdowns:
            result.append(f"  └─ {format_model_name(breakdown.model_name)}")
            result.append(f"     Input: {format_number(breakdown.input_tokens)}")
            result.append(f"     Output: {format_number(breakdown.output_tokens)}")
            result.append(f"     Cost: {format_currency(breakdown.cost, self.currency_code, self.currency_symbol)}")
            result.append("")

        return "\n".join(result)
