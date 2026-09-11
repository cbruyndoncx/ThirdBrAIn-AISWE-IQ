"""Data processing utilities for usage analysis."""

from __future__ import annotations

from collections import defaultdict

from ..core.result import Result, err, ok
from ..models.base import CostMode, SortOrder
from ..models.usage import (
    DailyUsage,
    MonthlyUsage,
    RawUsageEntry,
    SessionUsage,
    UsageTotals,
)


class DataProcessor:
    """Process raw usage data into aggregated reports."""

    def __init__(
        self, cost_mode: CostMode = CostMode.AUTO, offline: bool = False
    ) -> None:
        """Initialize data processor with cost mode and offline flag."""
        self.cost_mode = cost_mode
        self.offline = offline

    async def process_daily_usage(
        self,
        entries: list[RawUsageEntry],
        since: str | None = None,
        until: str | None = None,
        order: SortOrder = SortOrder.DESC,
    ) -> Result[list[DailyUsage], Exception]:
        """Process entries into daily usage aggregates."""
        try:
            # Group entries by date
            daily_groups = defaultdict(list)
            for entry in entries:
                # Convert UTC timestamp to local time before extracting date
                local_timestamp = (
                    entry.timestamp.astimezone()
                    if entry.timestamp.tzinfo is not None
                    else entry.timestamp
                )
                date_str = local_timestamp.date().isoformat()
                if self._is_in_date_range(date_str, since, until):
                    daily_groups[date_str].append(entry)

            # Aggregate each day's data
            daily_usage = []
            for date_str, day_entries in daily_groups.items():
                usage = await self._aggregate_daily_entries(date_str, day_entries)
                daily_usage.append(usage)

            # Sort by date
            reverse = order == SortOrder.DESC
            daily_usage.sort(key=lambda x: x.date, reverse=reverse)

            return ok(daily_usage)

        except Exception as e:
            return err(e)

    async def process_monthly_usage(
        self,
        entries: list[RawUsageEntry],
        since: str | None = None,
        until: str | None = None,
        order: SortOrder = SortOrder.DESC,
    ) -> Result[list[MonthlyUsage], Exception]:
        """Process entries into monthly usage aggregates."""
        try:
            # Group entries by month
            monthly_groups = defaultdict(list)
            for entry in entries:
                # Convert UTC timestamp to local time before extracting month
                local_timestamp = (
                    entry.timestamp.astimezone()
                    if entry.timestamp.tzinfo is not None
                    else entry.timestamp
                )
                month_str = local_timestamp.strftime("%Y-%m")
                if self._is_in_month_range(month_str, since, until):
                    monthly_groups[month_str].append(entry)

            # Aggregate each month's data
            monthly_usage = []
            for month_str, month_entries in monthly_groups.items():
                usage = await self._aggregate_monthly_entries(month_str, month_entries)
                monthly_usage.append(usage)

            # Sort by month
            reverse = order == SortOrder.DESC
            monthly_usage.sort(key=lambda x: x.month, reverse=reverse)

            return ok(monthly_usage)

        except Exception as e:
            return err(e)

    async def process_session_usage(
        self,
        entries: list[RawUsageEntry],
        since: str | None = None,
        until: str | None = None,
        order: SortOrder = SortOrder.DESC,
    ) -> Result[list[SessionUsage], Exception]:
        """Process entries into session usage aggregates."""
        try:
            # Filter entries by date range if specified
            if since is not None or until is not None:
                filtered_entries = []
                for entry in entries:
                    # Convert UTC timestamp to local time before extracting date
                    local_timestamp = (
                        entry.timestamp.astimezone()
                        if entry.timestamp.tzinfo is not None
                        else entry.timestamp
                    )
                    date_str = local_timestamp.date().isoformat()
                    if self._is_in_date_range(date_str, since, until):
                        filtered_entries.append(entry)
                entries = filtered_entries

            # Group entries by session
            session_groups = defaultdict(list)
            for entry in entries:
                session_groups[entry.session_id].append(entry)

            # Aggregate each session's data
            session_usage = []
            for session_id, session_entries in session_groups.items():
                usage = await self._aggregate_session_entries(
                    session_id, session_entries
                )
                session_usage.append(usage)

            # Sort by last activity
            reverse = order == SortOrder.DESC
            session_usage.sort(key=lambda x: x.last_activity, reverse=reverse)

            return ok(session_usage)

        except Exception as e:
            return err(e)

    async def calculate_totals(
        self, entries: list[RawUsageEntry]
    ) -> Result[UsageTotals, Exception]:
        """Calculate total usage across all entries."""
        try:
            total_input = sum(entry.input_tokens for entry in entries)
            total_output = sum(entry.output_tokens for entry in entries)
            total_cache_creation = sum(entry.cache_creation_tokens for entry in entries)
            total_cache_read = sum(entry.cache_read_tokens for entry in entries)
            total_cost = await self._calculate_total_cost(entries)

            totals = UsageTotals(
                input_tokens=total_input,
                output_tokens=total_output,
                cache_creation_tokens=total_cache_creation,
                cache_read_tokens=total_cache_read,
                total_cost=total_cost,
            )

            return ok(totals)

        except Exception as e:
            return err(e)

    async def _aggregate_daily_entries(
        self, date_str: str, entries: list[RawUsageEntry]
    ) -> DailyUsage:
        """Aggregate entries for a single day."""
        total_input = sum(entry.input_tokens for entry in entries)
        total_output = sum(entry.output_tokens for entry in entries)
        total_cache_creation = sum(entry.cache_creation_tokens for entry in entries)
        total_cache_read = sum(entry.cache_read_tokens for entry in entries)

        models_used = list({entry.model_name for entry in entries})

        # Calculate total cost based on mode
        total_cost = await self._calculate_total_cost(entries)

        return DailyUsage(
            date=date_str,
            input_tokens=total_input,
            output_tokens=total_output,
            cache_creation_tokens=total_cache_creation,
            cache_read_tokens=total_cache_read,
            total_cost=total_cost,
            models_used=models_used,
            model_breakdowns=[],  # TODO: Implement model breakdowns
        )

    async def _aggregate_monthly_entries(
        self, month_str: str, entries: list[RawUsageEntry]
    ) -> MonthlyUsage:
        """Aggregate entries for a single month."""
        total_input = sum(entry.input_tokens for entry in entries)
        total_output = sum(entry.output_tokens for entry in entries)
        total_cache_creation = sum(entry.cache_creation_tokens for entry in entries)
        total_cache_read = sum(entry.cache_read_tokens for entry in entries)

        models_used = list({entry.model_name for entry in entries})

        # Calculate total cost based on mode
        total_cost = await self._calculate_total_cost(entries)

        return MonthlyUsage(
            month=month_str,
            input_tokens=total_input,
            output_tokens=total_output,
            cache_creation_tokens=total_cache_creation,
            cache_read_tokens=total_cache_read,
            total_cost=total_cost,
            models_used=models_used,
            model_breakdowns=[],  # TODO: Implement model breakdowns
        )

    async def _aggregate_session_entries(
        self, session_id: str, entries: list[RawUsageEntry]
    ) -> SessionUsage:
        """Aggregate entries for a single session."""
        total_input = sum(entry.input_tokens for entry in entries)
        total_output = sum(entry.output_tokens for entry in entries)
        total_cache_creation = sum(entry.cache_creation_tokens for entry in entries)
        total_cache_read = sum(entry.cache_read_tokens for entry in entries)

        models_used = list({entry.model_name for entry in entries})
        versions = list({entry.version for entry in entries})

        # Get last activity timestamp
        last_activity = max(entry.timestamp for entry in entries)

        # Get project path (should be same for all entries in session)
        project_path = entries[0].project_path if entries else ""

        # Calculate total cost based on mode
        total_cost = await self._calculate_total_cost(entries)

        return SessionUsage(
            session_id=session_id,
            project_path=project_path,
            input_tokens=total_input,
            output_tokens=total_output,
            cache_creation_tokens=total_cache_creation,
            cache_read_tokens=total_cache_read,
            total_cost=total_cost,
            last_activity=last_activity,
            versions=versions,
            models_used=models_used,
            model_breakdowns=[],  # TODO: Implement model breakdowns
        )

    async def _calculate_total_cost(self, entries: list[RawUsageEntry]) -> float:
        """Calculate total cost based on cost mode."""
        match self.cost_mode:
            case CostMode.DISPLAY:
                return sum(entry.cost_usd or 0.0 for entry in entries)
            case CostMode.CALCULATE:
                # Always calculate from tokens
                from ..pricing.calculator import CostCalculator
                from ..pricing.fetcher import PricingFetcher

                fetcher = PricingFetcher(offline=self.offline)
                calculator = CostCalculator(fetcher)

                # Create context based on the entries
                models = list(
                    set(entry.model_name for entry in entries if entry.model_name)
                )
                context = f"\nCalculating costs for {len(models)} model(s): {', '.join(models[:3])}"
                if len(models) > 3:
                    context = f"\nCalculating costs for {len(models)} model(s): {', '.join(models[:3])} and {len(models) - 3} more"

                total_cost_result = await calculator.calculate_total_cost(
                    entries, context
                )
                if total_cost_result.is_ok():
                    return total_cost_result.value
                return 0.0
            case CostMode.AUTO:
                # Use pre-calculated if available, otherwise calculate
                total_with_precalc = sum(entry.cost_usd or 0.0 for entry in entries)

                # For entries without cost_usd, calculate from tokens
                entries_without_cost = [e for e in entries if e.cost_usd is None]
                if entries_without_cost:
                    from ..pricing.calculator import CostCalculator
                    from ..pricing.fetcher import PricingFetcher

                    fetcher = PricingFetcher(offline=self.offline)
                    calculator = CostCalculator(fetcher)

                    # Create context for entries without pre-calculated costs
                    models = list(
                        set(
                            entry.model_name
                            for entry in entries_without_cost
                            if entry.model_name
                        )
                    )
                    context = f"\nAuto-calculating missing costs for {len(models)} model(s): {', '.join(models[:3])}"
                    if len(models) > 3:
                        context = f"\nAuto-calculating missing costs for {len(models)} model(s): {', '.join(models[:3])} and {len(models) - 3} more"

                    calculated_cost_result = await calculator.calculate_total_cost(
                        entries_without_cost, context
                    )
                    if calculated_cost_result.is_ok():
                        total_with_precalc += calculated_cost_result.value

                return total_with_precalc

    def _is_in_date_range(
        self, date_str: str, since: str | None, until: str | None
    ) -> bool:
        """Check if date is within specified range."""
        if since:
            # Handle both YYYYMMDD and YYYY-MM-DD formats
            if "-" in since:
                since_formatted = since
            else:
                since_formatted = f"{since[:4]}-{since[4:6]}-{since[6:8]}"
            if date_str < since_formatted:
                return False
        if until:
            # Handle both YYYYMMDD and YYYY-MM-DD formats
            if "-" in until:
                until_formatted = until
            else:
                until_formatted = f"{until[:4]}-{until[4:6]}-{until[6:8]}"
            if date_str > until_formatted:
                return False
        return True

    def _is_in_month_range(
        self, month_str: str, since: str | None, until: str | None
    ) -> bool:
        """Check if month is within specified range."""
        if since:
            # Convert YYYYMMDD to YYYY-MM for comparison
            since_month = f"{since[:4]}-{since[4:6]}"
            if month_str < since_month:
                return False
        if until:
            # Convert YYYYMMDD to YYYY-MM for comparison
            until_month = f"{until[:4]}-{until[4:6]}"
            if month_str > until_month:
                return False
        return True
