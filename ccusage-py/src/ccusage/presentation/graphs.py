"""ASCII graph visualization for ccusage-py."""

from __future__ import annotations

import math
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..models.usage import DailyUsage, MonthlyUsage, SessionUsage
from ..models.base import format_currency


class ASCIIGraphGenerator:
    """Generator for ASCII character graphs."""

    def __init__(
        self, 
        console: Console | None = None,
        currency_code: str = "USD",
        currency_symbol: str = "$"
    ) -> None:
        """Initialize graph generator with console and currency formatting."""
        self.console = console or Console()
        self.terminal_width = self.console.size.width
        self.currency_code = currency_code
        self.currency_symbol = currency_symbol

    def generate_cost_bar_chart(
        self,
        usage_data: list[DailyUsage | MonthlyUsage | SessionUsage],
        max_width: int = 60,
        title: str = "Cost Distribution",
    ) -> Panel:
        """Generate horizontal bar chart for cost data."""
        if not usage_data:
            return Panel(
                Text("No data available for graph", style="dim"),
                title=title,
                border_style="blue",
            )

        # Extract costs and labels
        costs = [usage.total_cost for usage in usage_data]
        max_cost = max(costs) if costs else 0
        
        if max_cost == 0:
            return Panel(
                Text("No cost data available", style="dim"),
                title=title,
                border_style="blue",
            )

        # Create labels based on data type
        labels = []
        for usage in usage_data:
            if hasattr(usage, 'date'):
                labels.append(usage.date)
            elif hasattr(usage, 'month'):
                labels.append(usage.month)
            elif hasattr(usage, 'session_id'):
                labels.append(usage.session_id[:8] + "...")
            else:
                labels.append("Unknown")

        # Calculate available width for bars
        max_label_width = max(len(label) for label in labels) if labels else 0
        cost_width = 8  # Width for cost display (e.g. "$0.45" or "£0.45")
        bar_width = max_width - max_label_width - cost_width - 4  # 4 for spacing

        if bar_width < 10:
            bar_width = 10

        # Generate bars
        graph_text = Text()
        for i, (cost, label) in enumerate(zip(costs, labels)):
            if i > 0:
                graph_text.append("\n")
            
            # Calculate bar length
            bar_length = int((cost / max_cost) * bar_width) if max_cost > 0 else 0
            bar = "█" * bar_length + "░" * (bar_width - bar_length)
            
            # Format the line
            graph_text.append(f"{label:<{max_label_width}} ", style="cyan")
            graph_text.append(bar, style="blue")
            graph_text.append(f" {format_currency(cost, self.currency_code, self.currency_symbol)}", style="green")

        return Panel(
            graph_text,
            title=title,
            border_style="blue",
            expand=False,
        )

    def generate_sparkline(
        self,
        usage_data: list[DailyUsage | MonthlyUsage | SessionUsage],
        max_width: int = 50,
        title: str = "Cost Trend",
    ) -> Panel:
        """Generate sparkline for cost trend."""
        if not usage_data:
            return Panel(
                Text("No data available for sparkline", style="dim"),
                title=title,
                border_style="green",
            )

        costs = [usage.total_cost for usage in usage_data]
        if not costs or max(costs) == 0:
            return Panel(
                Text("No cost data available", style="dim"),
                title=title,
                border_style="green",
            )

        # Sparkline characters (from lowest to highest)
        spark_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        
        # Normalize costs to sparkline range
        min_cost = min(costs)
        max_cost = max(costs)
        cost_range = max_cost - min_cost
        
        if cost_range == 0:
            # All costs are the same
            sparkline = spark_chars[4] * len(costs)  # Use middle character
        else:
            sparkline = ""
            for cost in costs:
                normalized = (cost - min_cost) / cost_range
                char_index = min(int(normalized * len(spark_chars)), len(spark_chars) - 1)
                sparkline += spark_chars[char_index]

        # Truncate if too long
        if len(sparkline) > max_width:
            sparkline = sparkline[:max_width-3] + "..."

        spark_text = Text()
        spark_text.append(sparkline, style="bright_blue")
        spark_text.append(f"\nRange: {format_currency(min_cost, self.currency_code, self.currency_symbol)} - {format_currency(max_cost, self.currency_code, self.currency_symbol)}", style="dim")

        return Panel(
            spark_text,
            title=title,
            border_style="green",
            expand=False,
        )

    def generate_token_usage_chart(
        self,
        usage_data: list[DailyUsage | MonthlyUsage | SessionUsage],
        max_width: int = 60,
        title: str = "Token Usage",
    ) -> Panel:
        """Generate stacked bar chart for token usage (input/output)."""
        if not usage_data:
            return Panel(
                Text("No data available for token chart", style="dim"),
                title=title,
                border_style="yellow",
            )

        # Extract token data
        input_tokens = [usage.input_tokens for usage in usage_data]
        output_tokens = [usage.output_tokens for usage in usage_data]
        max_tokens = max(
            usage.total_tokens for usage in usage_data
        ) if usage_data else 0

        if max_tokens == 0:
            return Panel(
                Text("No token data available", style="dim"),
                title=title,
                border_style="yellow",
            )

        # Create labels based on data type
        labels = []
        for usage in usage_data:
            if hasattr(usage, 'date'):
                labels.append(usage.date)
            elif hasattr(usage, 'month'):
                labels.append(usage.month)
            elif hasattr(usage, 'session_id'):
                labels.append(usage.session_id[:8] + "...")
            else:
                labels.append("Unknown")

        # Calculate available width for bars
        max_label_width = max(len(label) for label in labels) if labels else 0
        tokens_width = 10  # Width for token count display
        bar_width = max_width - max_label_width - tokens_width - 4  # 4 for spacing

        if bar_width < 10:
            bar_width = 10

        # Generate stacked bars
        graph_text = Text()
        for i, (inp, out, label) in enumerate(zip(input_tokens, output_tokens, labels)):
            if i > 0:
                graph_text.append("\n")
            
            total = inp + out
            
            # Calculate bar segments
            input_length = int((inp / max_tokens) * bar_width) if max_tokens > 0 else 0
            output_length = int((out / max_tokens) * bar_width) if max_tokens > 0 else 0
            
            # Ensure we don't exceed bar width
            if input_length + output_length > bar_width:
                ratio = bar_width / (input_length + output_length)
                input_length = int(input_length * ratio)
                output_length = int(output_length * ratio)
            
            remaining = bar_width - input_length - output_length
            
            # Format the line
            graph_text.append(f"{label:<{max_label_width}} ", style="cyan")
            graph_text.append("█" * input_length, style="bright_blue")
            graph_text.append("█" * output_length, style="bright_green")
            graph_text.append("░" * remaining, style="dim")
            graph_text.append(f" {total:,}", style="white")

        # Add legend
        graph_text.append("\n\nLegend: ")
        graph_text.append("█", style="bright_blue")
        graph_text.append(" Input  ", style="bright_blue")
        graph_text.append("█", style="bright_green")
        graph_text.append(" Output", style="bright_green")

        return Panel(
            graph_text,
            title=title,
            border_style="yellow",
            expand=False,
        )

    def generate_session_activity_chart(
        self,
        session_data: list[SessionUsage],
        max_width: int = 60,
        title: str = "Session Activity",
    ) -> Panel:
        """Generate chart showing session activity over time.
        
        Note: This chart shows the count of sessions that were already filtered 
        by date at the entry level in the session command, so the session count 
        matches the logic used by 'ccusage-py s'.
        """
        if not session_data:
            return Panel(
                Text("No session data available", style="dim"),
                title=title,
                border_style="magenta",
            )

        # Group sessions by the date of their last activity
        # Convert to local time before extracting date to match processor logic
        from collections import defaultdict
        daily_sessions: dict[str, int] = defaultdict(int)
        
        for session in session_data:
            # Convert UTC timestamp to local time before extracting date
            # This matches the timezone conversion in processor.py lines 117-121
            local_timestamp = (
                session.last_activity.astimezone()
                if session.last_activity.tzinfo is not None
                else session.last_activity
            )
            date_str = local_timestamp.date().isoformat()
            daily_sessions[date_str] += 1

        # Convert to sorted list
        dates = sorted(daily_sessions.keys())
        counts = [daily_sessions[date] for date in dates]
        
        if not counts:
            return Panel(
                Text("No activity data available", style="dim"),
                title=title,
                border_style="magenta",
            )

        max_count = max(counts)
        
        # Generate activity chart
        graph_text = Text()
        for i, (date, count) in enumerate(zip(dates, counts)):
            if i > 0:
                graph_text.append("\n")
            
            # Calculate bar length
            bar_length = int((count / max_count) * (max_width - 15)) if max_count > 0 else 0
            bar = "█" * bar_length
            
            # Format the line
            graph_text.append(f"{date} ", style="cyan")
            graph_text.append(bar, style="magenta")
            graph_text.append(f" {count}", style="white")

        return Panel(
            graph_text,
            title=title,
            border_style="magenta",
            expand=False,
        )

    def generate_cost_comparison_chart(
        self,
        usage_data: list[DailyUsage | MonthlyUsage | SessionUsage],
        max_width: int = 60,
        title: str = "Cost Comparison",
    ) -> Panel:
        """Generate comparative chart showing relative costs."""
        if not usage_data:
            return Panel(
                Text("No data available for comparison", style="dim"),
                title=title,
                border_style="red",
            )

        costs = [usage.total_cost for usage in usage_data]
        if not costs or max(costs) == 0:
            return Panel(
                Text("No cost data available", style="dim"),
                title=title,
                border_style="red",
            )

        # Calculate statistics
        total_cost = sum(costs)
        avg_cost = total_cost / len(costs)
        min_cost = min(costs)
        max_cost = max(costs)

        # Generate comparison bars
        graph_text = Text()
        
        # Show distribution
        above_avg = sum(1 for cost in costs if cost > avg_cost)
        below_avg = len(costs) - above_avg
        
        bar_width = max_width - 30
        above_bar = int((above_avg / len(costs)) * bar_width)
        below_bar = bar_width - above_bar
        
        graph_text.append("Above Average: ", style="bold")
        graph_text.append("█" * above_bar, style="red")
        graph_text.append(f" {above_avg}/{len(costs)}\n", style="white")
        
        graph_text.append("Below Average: ", style="bold")
        graph_text.append("█" * below_bar, style="green")
        graph_text.append(f" {below_avg}/{len(costs)}\n\n", style="white")
        
        # Show statistics
        graph_text.append(f"Average: {format_currency(avg_cost, self.currency_code, self.currency_symbol)}\n", style="yellow")
        graph_text.append(f"Range: {format_currency(min_cost, self.currency_code, self.currency_symbol)} - {format_currency(max_cost, self.currency_code, self.currency_symbol)}\n", style="cyan")
        graph_text.append(f"Total: {format_currency(total_cost, self.currency_code, self.currency_symbol)}", style="bold green")

        return Panel(
            graph_text,
            title=title,
            border_style="red",
            expand=False,
        )