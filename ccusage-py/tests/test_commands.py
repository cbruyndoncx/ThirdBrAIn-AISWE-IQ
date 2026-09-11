"""Tests for CLI commands and coverage."""

from __future__ import annotations

import warnings
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from typer.testing import CliRunner

from ccusage.commands.daily import (
    _convert_date_format,
    _daily_command_async,
    daily_command,
)
from ccusage.commands.monthly import _monthly_command_async, monthly_command
from ccusage.commands.session import (
    _convert_date_format as session_convert_date_format,
)
from ccusage.commands.session import (
    _session_command_async,
    session_command,
)
from ccusage.core.exceptions import CcusageError, ConfigurationError
from ccusage.core.result import Err, Ok
from ccusage.models.base import CostMode, SortOrder
from ccusage.models.usage import (
    DailyUsage,
    ModelBreakdown,
    MonthlyUsage,
    RawUsageEntry,
    SessionUsage,
    UsageTotals,
)


@pytest.fixture
def sample_raw_entries():
    """Sample raw usage entries."""
    return [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            request_id="req-1",
            message_id="msg-1",
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            cost_usd=0.01,
            project_path="/project1",
            version="1.0.43",
        )
    ]


@pytest.fixture
def sample_daily_usage():
    """Sample daily usage data."""
    return [
        DailyUsage(
            date="2025-07-15",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            total_cost=0.01,
            models_used=["claude-sonnet-4-20250514"],
            model_breakdowns=[
                ModelBreakdown(
                    model_name="claude-sonnet-4-20250514",
                    input_tokens=100,
                    output_tokens=50,
                    cache_creation_tokens=25,
                    cache_read_tokens=10,
                    cost=0.01,
                ),
            ],
        ),
        DailyUsage(
            date="2025-07-16",
            input_tokens=200,
            output_tokens=100,
            cache_creation_tokens=50,
            cache_read_tokens=20,
            total_cost=0.02,
            models_used=["claude-sonnet-4-20250514"],
            model_breakdowns=[],
        ),
    ]


@pytest.fixture
def sample_monthly_usage():
    """Sample monthly usage data."""
    return [
        MonthlyUsage(
            month="2025-07",
            input_tokens=300,
            output_tokens=150,
            cache_creation_tokens=75,
            cache_read_tokens=30,
            total_cost=0.03,
            models_used=["claude-sonnet-4-20250514"],
            model_breakdowns=[],
        ),
    ]


@pytest.fixture
def sample_session_usage():
    """Sample session usage data."""
    return [
        SessionUsage(
            session_id="session-1",
            project_path="/project1",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            total_cost=0.01,
            last_activity=datetime(2025, 7, 15, 10, 0, 0),
            versions=["1.0.43"],
            models_used=["claude-sonnet-4-20250514"],
            model_breakdowns=[],
        ),
    ]


@pytest.fixture
def sample_totals():
    """Sample usage totals."""
    return UsageTotals(
        input_tokens=300,
        output_tokens=150,
        cache_creation_tokens=75,
        cache_read_tokens=30,
        total_cost=0.03,
    )


class TestDailyCommand:
    """Test the daily command."""

    @patch("ccusage.commands.daily.get_claude_paths")
    @patch("ccusage.commands.daily.validate_claude_paths")
    @patch("ccusage.commands.daily.DataLoader")
    @patch("ccusage.commands.daily.DataProcessor")
    @patch("ccusage.commands.daily.ResponsiveTableFormatter")
    @patch("ccusage.commands.daily.CurrencyConverter")
    @patch("ccusage.commands.daily.console")
    def test_daily_command_success(
        self,
        mock_console,
        mock_currency_converter,
        mock_formatter_class,
        mock_processor_class,
        mock_loader_class,
        mock_validate,
        mock_get_paths,
        sample_daily_usage,
    ):
        """Test daily command success."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_daily_usage = AsyncMock(
            return_value=Ok(sample_daily_usage)
        )
        mock_processor.calculate_totals = AsyncMock(
            return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
        )
        mock_processor_class.return_value = mock_processor

        mock_formatter = Mock()
        mock_formatter.format_daily_table = Mock(return_value="table_output")
        mock_formatter.format_summary_panel = Mock(return_value="summary_output")
        mock_formatter_class.return_value = mock_formatter

        # Setup currency converter mock
        mock_converter_instance = AsyncMock()
        mock_converter_instance.__aenter__ = AsyncMock(
            return_value=mock_converter_instance
        )
        mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
        mock_converter_instance.get_currency_code = Mock(return_value="USD")
        mock_converter_instance.get_currency_symbol = Mock(return_value="$")
        mock_currency_converter.return_value = mock_converter_instance

        daily_command(
            False, None, None, CostMode.AUTO, SortOrder.DESC, False, False, False
        )

        mock_get_paths.assert_called_once()

    def test_daily_command_wrapper(self):
        """Test daily_command wrapper function."""
        with patch("asyncio.run") as mock_asyncio_run:
            daily_command(
                json_output=True,
                since="2025-07-15",
                until="2025-07-16",
                mode=CostMode.CALCULATE,
                order=SortOrder.ASC,
                breakdown=True,
                offline=True,
                graph=True,
            )

            mock_asyncio_run.assert_called_once()
            args, kwargs = mock_asyncio_run.call_args
            assert len(args) == 1

    @pytest.mark.asyncio
    async def test_daily_command_async_success(self, sample_daily_usage, sample_totals):
        """Test successful daily command execution."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            with (
                patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
                patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
                patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
                patch("ccusage.commands.daily.DataProcessor") as mock_processor_class,
                patch(
                    "ccusage.commands.daily.ResponsiveTableFormatter"
                ) as mock_formatter_class,
                patch(
                    "ccusage.commands.daily.CurrencyConverter"
                ) as mock_currency_converter,
                patch("ccusage.commands.daily.console") as mock_console,
            ):
                # Setup mocks
                mock_get_paths.return_value = [Path("/path/to/claude")]
                mock_validate.return_value = None

                mock_loader = Mock()
                mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
                mock_loader_class.return_value = mock_loader

                mock_processor = Mock()
                mock_processor.process_daily_usage = AsyncMock(
                    return_value=Ok(sample_daily_usage)
                )
                mock_processor.calculate_totals = AsyncMock(
                    return_value=Ok(sample_totals)
                )
                mock_processor_class.return_value = mock_processor

                mock_formatter = Mock()
                mock_formatter.format_daily_table = Mock(return_value="mock_table")
                mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
                mock_formatter.terminal_width = 120
                mock_formatter.graph_generator = Mock()
                mock_formatter.graph_generator.generate_cost_bar_chart = Mock(
                    return_value="mock_chart"
                )
                mock_formatter.graph_generator.generate_sparkline = Mock(
                    return_value="mock_sparkline"
                )
                mock_formatter_class.return_value = mock_formatter

                # Setup currency converter mock
                mock_converter_instance = AsyncMock()
                mock_converter_instance.__aenter__ = AsyncMock(
                    return_value=mock_converter_instance
                )
                mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
                mock_converter_instance.get_currency_code = Mock(return_value="USD")
                mock_converter_instance.get_currency_symbol = Mock(return_value="$")
                mock_currency_converter.return_value = mock_converter_instance

                # Test successful execution
                await _daily_command_async(
                    json_output=False,
                    since="2025-07-15",
                    until="2025-07-16",
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=True,
                    currency=None,
                )

                # Verify calls
                mock_get_paths.assert_called_once()
                mock_validate.assert_called_once()
                mock_loader.load_raw_entries.assert_called_once()
                assert mock_processor.process_daily_usage.called
                assert mock_processor.calculate_totals.called
                assert mock_formatter.format_daily_table.called
                assert mock_formatter.format_summary_panel.called
                assert mock_console.print.called

                # Clean up AsyncMock objects to avoid warnings
                mock_loader.load_raw_entries.reset_mock()
                mock_processor.process_daily_usage.reset_mock()
                mock_processor.calculate_totals.reset_mock()

    @pytest.mark.asyncio
    async def test_daily_command_async_json_output(self, sample_daily_usage):
        """Test daily command with JSON output."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.DataProcessor") as mock_processor_class,
            patch("ccusage.commands.daily.console") as mock_console,
            patch("logging.getLogger") as mock_get_logger,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_daily_usage = AsyncMock(
                return_value=Ok(sample_daily_usage)
            )
            mock_processor_class.return_value = mock_processor

            # Test JSON output
            await _daily_command_async(
                json_output=True,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify logging suppression
            mock_get_logger.assert_called_once()
            mock_get_logger().setLevel.assert_called_once()

            # Verify JSON output
            mock_console.print_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_daily_command_async_no_data(self):
        """Test daily command when no data is found."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            # Test no data (empty entries)
            await _daily_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify no data message
            mock_console.print.assert_called_with(
                "[yellow]No Claude usage data found.[/yellow]"
            )

    @patch("ccusage.commands.daily.get_claude_paths")
    @patch("ccusage.commands.daily.validate_claude_paths")
    @patch("ccusage.commands.daily.DataLoader")
    def test_daily_command_configuration_error(
        self, mock_loader_class, mock_validate, mock_get_paths
    ):
        """Test daily command configuration error."""
        mock_get_paths.side_effect = ConfigurationError("Config error")

        with pytest.raises(ConfigurationError):
            daily_command(
                False, None, None, CostMode.AUTO, SortOrder.DESC, False, False, False
            )

    @patch("ccusage.commands.daily.get_claude_paths")
    @patch("ccusage.commands.daily.validate_claude_paths")
    @patch("ccusage.commands.daily.DataLoader")
    def test_daily_command_data_load_error(
        self, mock_loader_class, mock_validate, mock_get_paths
    ):
        """Test daily command data load error."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Err("Load error"))
        mock_loader_class.return_value = mock_loader

        with pytest.raises(CcusageError, match="Failed to load data: Load error"):
            daily_command(
                False, None, None, CostMode.AUTO, SortOrder.DESC, False, False, False
            )

    @patch("ccusage.commands.daily.get_claude_paths")
    @patch("ccusage.commands.daily.validate_claude_paths")
    @patch("ccusage.commands.daily.DataLoader")
    @patch("ccusage.commands.daily.DataProcessor")
    def test_daily_command_processing_error(
        self, mock_processor_class, mock_loader_class, mock_validate, mock_get_paths
    ):
        """Test daily command processing error."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_daily_usage = AsyncMock(
            return_value=Err("Processing error")
        )
        mock_processor_class.return_value = mock_processor

        with pytest.raises(
            CcusageError, match="Failed to process data: Processing error"
        ):
            daily_command(
                False, None, None, CostMode.AUTO, SortOrder.DESC, False, False, False
            )

    @patch("ccusage.commands.daily.get_claude_paths")
    @patch("ccusage.commands.daily.validate_claude_paths")
    @patch("ccusage.commands.daily.DataLoader")
    @patch("ccusage.commands.daily.DataProcessor")
    @patch("ccusage.commands.daily.ResponsiveTableFormatter")
    @patch("ccusage.commands.daily.console")
    def test_daily_command_json_output(
        self,
        mock_console,
        mock_formatter_class,
        mock_processor_class,
        mock_loader_class,
        mock_validate,
        mock_get_paths,
        sample_daily_usage,
    ):
        """Test daily command JSON output."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_daily_usage = AsyncMock(
            return_value=Ok(sample_daily_usage)
        )
        mock_processor.calculate_totals = AsyncMock(
            return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
        )
        mock_processor_class.return_value = mock_processor

        with patch("logging.getLogger"):
            daily_command(
                True, None, None, CostMode.AUTO, SortOrder.DESC, False, False, False
            )

        mock_console.print_json.assert_called_once()

    @patch("ccusage.commands.daily.get_claude_paths")
    @patch("ccusage.commands.daily.validate_claude_paths")
    @patch("ccusage.commands.daily.DataLoader")
    @patch("ccusage.commands.daily.DataProcessor")
    @patch("ccusage.commands.daily.ResponsiveTableFormatter")
    @patch("ccusage.commands.daily.CurrencyConverter")
    @patch("ccusage.commands.daily.console")
    def test_daily_command_with_options(
        self,
        mock_console,
        mock_currency_converter,
        mock_formatter_class,
        mock_processor_class,
        mock_loader_class,
        mock_validate,
        mock_get_paths,
        sample_daily_usage,
    ):
        """Test daily command with various options."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_daily_usage = AsyncMock(
            return_value=Ok(sample_daily_usage)
        )
        mock_processor.calculate_totals = AsyncMock(
            return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
        )
        mock_processor_class.return_value = mock_processor

        mock_formatter = Mock()
        mock_formatter.format_daily_table = Mock(return_value="table_output")
        mock_formatter.format_summary_panel = Mock(return_value="summary_output")
        mock_formatter_class.return_value = mock_formatter

        # Setup currency converter mock
        mock_converter_instance = AsyncMock()
        mock_converter_instance.__aenter__ = AsyncMock(
            return_value=mock_converter_instance
        )
        mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
        mock_converter_instance.get_currency_code = Mock(return_value="USD")
        mock_converter_instance.get_currency_symbol = Mock(return_value="$")
        mock_currency_converter.return_value = mock_converter_instance

        daily_command(
            False,
            "2025-07-15",
            "2025-07-16",
            CostMode.CALCULATE,
            SortOrder.ASC,
            True,
            True,
            False,
        )

        # Verify processor was called with correct parameters
        mock_processor.process_daily_usage.assert_called_once()

    def test_daily_command_no_data_found_json(self):
        """Test daily command when no data found with JSON output."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.console") as mock_console,
            patch("logging.getLogger"),
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            daily_command(
                True, None, None, CostMode.AUTO, SortOrder.DESC, False, False, False
            )

            mock_console.print_json.assert_called_with("[]")

    def test_daily_command_no_data_found_table(self):
        """Test daily command when no data found with table output."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.console") as mock_console,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            daily_command(
                False, None, None, CostMode.AUTO, SortOrder.DESC, False, False, False
            )

            mock_console.print.assert_called_with(
                "[yellow]No Claude usage data found.[/yellow]"
            )

    def test_daily_command_totals_calculation_error(self, sample_daily_usage):
        """Test daily command when totals calculation fails."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.daily.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.daily.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.daily.console") as mock_console,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_daily_usage = AsyncMock(
                return_value=Ok(sample_daily_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Err("Totals error")
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_daily_table = Mock(return_value="table_output")
            mock_formatter.format_summary_panel = Mock(return_value="summary_output")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(return_value="USD")
            mock_converter_instance.get_currency_symbol = Mock(return_value="$")
            mock_currency_converter.return_value = mock_converter_instance

            daily_command(
                False, None, None, CostMode.AUTO, SortOrder.DESC, False, False, False
            )

            # Should still format the table
            mock_formatter.format_daily_table.assert_called_once()

    def test_daily_command_generic_exception(self):
        """Test daily command generic exception handling."""
        with patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths:
            mock_get_paths.side_effect = Exception("Generic error")

            with pytest.raises(
                CcusageError, match="Daily command failed: Generic error"
            ):
                daily_command(
                    False,
                    None,
                    None,
                    CostMode.AUTO,
                    SortOrder.DESC,
                    False,
                    False,
                    False,
                )

    def test_daily_command_with_graph_flag(self, sample_daily_usage, sample_totals):
        """Test daily command with graph flag enabled."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.daily.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.daily.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.daily.console") as mock_console,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_daily_usage = AsyncMock(
                return_value=Ok(sample_daily_usage)
            )
            mock_processor.calculate_totals = AsyncMock(return_value=Ok(sample_totals))
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_daily_table = Mock(return_value="table_output")
            mock_formatter.format_summary_panel = Mock(return_value="summary_output")
            mock_formatter.terminal_width = 120  # Wide enough for graphs
            mock_formatter.graph_generator = Mock()
            mock_formatter.graph_generator.generate_cost_bar_chart = Mock(
                return_value="mock_chart"
            )
            mock_formatter.graph_generator.generate_sparkline = Mock(
                return_value="mock_sparkline"
            )
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(return_value="USD")
            mock_converter_instance.get_currency_symbol = Mock(return_value="$")
            mock_currency_converter.return_value = mock_converter_instance

            daily_command(
                False, None, None, CostMode.AUTO, SortOrder.DESC, False, False, True
            )

            # Verify graph generation was called
            mock_formatter.graph_generator.generate_cost_bar_chart.assert_called_once()
            mock_formatter.graph_generator.generate_sparkline.assert_called_once()

    @pytest.mark.asyncio
    async def test_daily_command_async_data_load_error(self):
        """Test daily command when data loading fails."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Err("Load error"))
            mock_loader_class.return_value = mock_loader

            # Test data load error
            with pytest.raises(CcusageError, match="Failed to load data: Load error"):
                await _daily_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_daily_command_async_processing_error(self):
        """Test daily command when data processing fails."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.DataProcessor") as mock_processor_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_daily_usage = AsyncMock(
                return_value=Err("Processing error")
            )
            mock_processor_class.return_value = mock_processor

            # Test processing error
            with pytest.raises(
                CcusageError, match="Failed to process data: Processing error"
            ):
                await _daily_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_daily_command_async_generic_exception(self):
        """Test daily command when generic exception occurs."""
        with patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths:
            # Setup mocks to raise generic exception
            mock_get_paths.side_effect = ValueError("Generic error")

            # Test generic exception
            with pytest.raises(
                CcusageError, match="Daily command failed: Generic error"
            ):
                await _daily_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_daily_command_async_ccusage_error_passthrough(self):
        """Test daily command when CcusageError is raised (should pass through)."""
        with patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths:
            # Setup mocks to raise CcusageError
            mock_get_paths.side_effect = CcusageError("Direct error")

            # Test CcusageError passthrough
            with pytest.raises(CcusageError, match="Direct error"):
                await _daily_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_daily_command_async_graphs_single_item(self, sample_totals):
        """Test daily command with graphs when only single data item (no sparkline)."""
        single_daily_usage = [
            DailyUsage(
                date="2025-07-15",
                input_tokens=100,
                output_tokens=50,
                cache_creation_tokens=25,
                cache_read_tokens=10,
                total_cost=0.01,
                models_used=["claude-sonnet-4-20250514"],
                model_breakdowns=[],
            ),
        ]

        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.daily.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.daily.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.daily.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_daily_usage = AsyncMock(
                return_value=Ok(single_daily_usage)
            )
            mock_processor.calculate_totals = AsyncMock(return_value=Ok(sample_totals))
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_daily_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter.terminal_width = 120
            mock_formatter.graph_generator = Mock()
            mock_formatter.graph_generator.generate_cost_bar_chart = Mock(
                return_value="mock_chart"
            )
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(return_value="USD")
            mock_converter_instance.get_currency_symbol = Mock(return_value="$")
            mock_currency_converter.return_value = mock_converter_instance

            # Test with graphs and single item (no sparkline)
            await _daily_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=True,
                currency=None,
            )

            # Verify cost chart was generated but not sparkline
            mock_formatter.graph_generator.generate_cost_bar_chart.assert_called_once()
            mock_formatter.graph_generator.generate_sparkline.assert_not_called()

    @pytest.mark.asyncio
    async def test_daily_command_async_totals_error(self, sample_daily_usage):
        """Test daily command when totals calculation fails."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.daily.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.daily.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.daily.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_daily_usage = AsyncMock(
                return_value=Ok(sample_daily_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Err("Totals error")
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_daily_table = Mock(return_value="mock_table")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(return_value="USD")
            mock_converter_instance.get_currency_symbol = Mock(return_value="$")
            mock_currency_converter.return_value = mock_converter_instance

            # Test totals error (should not raise, just skip totals)
            await _daily_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify table was still formatted
            mock_formatter.format_daily_table.assert_called_once()
            # Summary should not be called
            mock_formatter.format_summary_panel.assert_not_called()

    @pytest.mark.asyncio
    async def test_daily_command_async_no_data_json(self):
        """Test daily command when no data is found with JSON output."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.console") as mock_console,
            patch("logging.getLogger") as mock_get_logger,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            # Test no data with JSON output
            await _daily_command_async(
                json_output=True,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify JSON output for no data
            mock_console.print_json.assert_called_with("[]")

    def test_convert_date_format(self):
        """Test date format conversion function."""
        # Test None input
        assert _convert_date_format(None) is None

        # Test empty string
        assert _convert_date_format("") is None

        # Test already ISO format
        assert _convert_date_format("2025-07-15") == "2025-07-15"

        # Test compact format conversion
        assert _convert_date_format("20250715") == "2025-07-15"

        # Test invalid format (not 8 chars)
        assert _convert_date_format("2025715") == "2025715"

        # Test with dash but different format
        assert _convert_date_format("2025-7-15") == "2025-7-15"

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_daily_command_async_custom_currency(
        self, sample_daily_usage, sample_totals
    ):
        """Test daily command with custom currency conversion."""
        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.daily.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.daily.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.daily.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_daily_usage = AsyncMock(
                return_value=Ok(sample_daily_usage)
            )
            mock_processor.calculate_totals = AsyncMock(return_value=Ok(sample_totals))
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_daily_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(return_value="EUR")
            mock_converter_instance.get_currency_symbol = Mock(return_value="€")
            mock_currency_converter.return_value = mock_converter_instance

            # Test with custom currency (EUR)
            await _daily_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency="eur",
            )

            # Verify CurrencyConverter was called with correct parameters
            mock_currency_converter.assert_called_once()
            args = mock_currency_converter.call_args[0]
            kwargs = mock_currency_converter.call_args[1]

            # Should be called with CUSTOM mode and EUR as target currency
            from ccusage.currency.converter import CurrencyMode

            assert (
                kwargs.get("currency_mode") == CurrencyMode.CUSTOM
                or args[1] == CurrencyMode.CUSTOM
            )
            assert kwargs.get("target_currency") == "EUR" or args[2] == "EUR"

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_daily_command_async_currency_conversion_non_usd(self, sample_totals):
        """Test daily command with currency conversion for non-USD currency."""
        from ccusage.core.result import Ok
        from ccusage.models.usage import DailyUsage, ModelBreakdown

        # Create sample data with model breakdowns for conversion testing
        sample_breakdown = ModelBreakdown(
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            cost=0.05,
        )

        sample_daily_with_breakdown = [
            DailyUsage(
                date="2025-07-15",
                input_tokens=100,
                output_tokens=50,
                cache_creation_tokens=25,
                cache_read_tokens=10,
                total_cost=0.10,
                models_used=["claude-sonnet-4-20250514"],
                model_breakdowns=[sample_breakdown],
            ),
        ]

        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.daily.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.daily.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.daily.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_daily_usage = AsyncMock(
                return_value=Ok(sample_daily_with_breakdown)
            )
            mock_processor.calculate_totals = AsyncMock(return_value=Ok(sample_totals))
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_daily_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock for EUR (non-USD)
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(
                return_value="EUR"
            )  # Non-USD currency
            mock_converter_instance.get_currency_symbol = Mock(return_value="€")

            # Mock convert_amount to return converted values
            mock_converter_instance.convert_amount = AsyncMock(
                return_value=Ok(0.092)
            )  # Converted main cost
            mock_currency_converter.return_value = mock_converter_instance

            # Test with EUR currency (will trigger conversion logic)
            await _daily_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency="eur",
            )

            # Verify currency conversion was called
            # Should be called twice: once for main cost, once for breakdown cost
            assert mock_converter_instance.convert_amount.call_count == 2

            # Verify the calls were for the right amounts
            call_args_list = mock_converter_instance.convert_amount.call_args_list
            assert call_args_list[0][0][0] == 0.10  # Main cost conversion
            assert call_args_list[1][0][0] == 0.05  # Breakdown cost conversion

            # Verify table formatting was called
            mock_formatter.format_daily_table.assert_called_once()
            mock_formatter.format_summary_panel.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_daily_command_async_currency_conversion_failed(self, sample_totals):
        """Test daily command when currency conversion fails (fallback to original cost)."""
        from ccusage.core.result import Err, Ok
        from ccusage.models.usage import DailyUsage, ModelBreakdown

        # Create sample data with model breakdowns
        sample_breakdown = ModelBreakdown(
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            cost=0.05,
        )

        sample_daily_with_breakdown = [
            DailyUsage(
                date="2025-07-15",
                input_tokens=100,
                output_tokens=50,
                cache_creation_tokens=25,
                cache_read_tokens=10,
                total_cost=0.10,
                models_used=["claude-sonnet-4-20250514"],
                model_breakdowns=[sample_breakdown],
            ),
        ]

        with (
            patch("ccusage.commands.daily.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.daily.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.daily.DataLoader") as mock_loader_class,
            patch("ccusage.commands.daily.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.daily.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.daily.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.daily.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_daily_usage = AsyncMock(
                return_value=Ok(sample_daily_with_breakdown)
            )
            mock_processor.calculate_totals = AsyncMock(return_value=Ok(sample_totals))
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_daily_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock for EUR (non-USD) with conversion failures
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(
                return_value="EUR"
            )  # Non-USD currency
            mock_converter_instance.get_currency_symbol = Mock(return_value="€")

            # Mock convert_amount to return error (conversion fails)
            mock_converter_instance.convert_amount = AsyncMock(
                return_value=Err("Conversion failed")
            )
            mock_currency_converter.return_value = mock_converter_instance

            # Test with EUR currency (will trigger conversion logic that fails)
            await _daily_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency="eur",
            )

            # Verify currency conversion was attempted
            assert mock_converter_instance.convert_amount.call_count == 2

            # Verify table formatting was still called (with original costs as fallback)
            mock_formatter.format_daily_table.assert_called_once()
            mock_formatter.format_summary_panel.assert_called_once()


class TestMonthlyCommand:
    """Test the monthly command."""

    def test_monthly_command_wrapper(self):
        """Test monthly_command wrapper function."""
        with patch("asyncio.run") as mock_asyncio_run:
            monthly_command(
                json_output=True,
                since="2025-07",
                until="2025-08",
                mode=CostMode.CALCULATE,
                order=SortOrder.ASC,
                breakdown=True,
                offline=True,
                graph=True,
            )

            mock_asyncio_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_monthly_command_async_success(self, sample_monthly_usage):
        """Test successful monthly command execution."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            with (
                patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
                patch(
                    "ccusage.commands.monthly.validate_claude_paths"
                ) as mock_validate,
                patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
                patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
                patch(
                    "ccusage.commands.monthly.ResponsiveTableFormatter"
                ) as mock_formatter_class,
                patch("ccusage.commands.monthly.console") as mock_console,
                patch(
                    "ccusage.commands.monthly.CurrencyConverter"
                ) as mock_currency_converter_class,
            ):
                # Setup mocks
                mock_get_paths.return_value = [Path("/path/to/claude")]
                mock_validate.return_value = None

                mock_loader = Mock()
                mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
                mock_loader_class.return_value = mock_loader

                mock_processor = Mock()
                mock_processor.process_monthly_usage = AsyncMock(
                    return_value=Ok(sample_monthly_usage)
                )
                mock_processor.calculate_totals = AsyncMock(
                    return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
                )
                mock_processor_class.return_value = mock_processor

                mock_formatter = Mock()
                mock_formatter.format_monthly_table = Mock(return_value="mock_table")
                mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
                mock_formatter.terminal_width = 120
                mock_formatter.graph_generator = Mock()
                mock_formatter.graph_generator.generate_cost_bar_chart = Mock(
                    return_value="mock_chart"
                )
                mock_formatter.graph_generator.generate_sparkline = Mock(
                    return_value="mock_sparkline"
                )
                mock_formatter_class.return_value = mock_formatter

                # Setup currency converter mock
                mock_currency_converter = Mock()
                mock_currency_converter.__aenter__ = AsyncMock(
                    return_value=mock_currency_converter
                )
                mock_currency_converter.__aexit__ = AsyncMock(return_value=None)
                mock_currency_converter.get_currency_code = Mock(return_value="USD")
                mock_currency_converter.get_currency_symbol = Mock(return_value="$")
                mock_currency_converter_class.return_value = mock_currency_converter

                # Test successful execution
                await _monthly_command_async(
                    json_output=False,
                    since="2025-07",
                    until="2025-08",
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=True,
                    currency=None,
                )

                # Verify calls
                mock_get_paths.assert_called_once()
                mock_validate.assert_called_once()
                mock_loader.load_raw_entries.assert_called_once()
                mock_processor.process_monthly_usage.assert_called_once()
                mock_formatter.format_monthly_table.assert_called_once()
                mock_formatter.format_summary_panel.assert_called_once()
                mock_console.print.assert_called()

    @pytest.mark.asyncio
    async def test_monthly_command_async_json_output(self, sample_monthly_usage):
        """Test monthly command with JSON output."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            with (
                patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
                patch(
                    "ccusage.commands.monthly.validate_claude_paths"
                ) as mock_validate,
                patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
                patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
                patch("ccusage.commands.monthly.console") as mock_console,
                patch("logging.getLogger") as mock_get_logger,
            ):
                # Setup mocks
                mock_get_paths.return_value = [Path("/path/to/claude")]
                mock_validate.return_value = None

                mock_loader = Mock()
                mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
                mock_loader_class.return_value = mock_loader

                mock_processor = Mock()
                mock_processor.process_monthly_usage = AsyncMock(
                    return_value=Ok(sample_monthly_usage)
                )
                mock_processor_class.return_value = mock_processor

                # Test JSON output
                await _monthly_command_async(
                    json_output=True,
                    since=None,
                    until=None,
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

                # Verify logging suppression
                mock_get_logger.assert_called_once()
                mock_get_logger().setLevel.assert_called_once()

                # Verify JSON output
                mock_console.print_json.assert_called_once()

                # Clean up AsyncMock objects to avoid warnings
                mock_loader.load_raw_entries.reset_mock()
                mock_processor.process_monthly_usage.reset_mock()

    @pytest.mark.asyncio
    async def test_monthly_command_async_no_data(self):
        """Test monthly command when no data is found."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            # Test no data
            await _monthly_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify no data message
            mock_console.print.assert_called_with(
                "[yellow]No Claude usage data found.[/yellow]"
            )

    @patch("ccusage.commands.monthly.get_claude_paths")
    @patch("ccusage.commands.monthly.validate_claude_paths")
    @patch("ccusage.commands.monthly.DataLoader")
    def test_monthly_command_success(
        self, mock_loader_class, mock_validate, mock_get_paths, sample_monthly_usage
    ):
        """Test monthly command success."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        with (
            patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.monthly.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.monthly.console") as mock_console,
            patch(
                "ccusage.commands.monthly.CurrencyConverter"
            ) as mock_currency_converter_class,
        ):
            mock_processor = Mock()
            mock_processor.process_monthly_usage = AsyncMock(
                return_value=Ok(sample_monthly_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_monthly_table = Mock(return_value="table_output")
            mock_formatter.format_summary_panel = Mock(return_value="summary_output")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_currency_converter = Mock()
            mock_currency_converter.__aenter__ = AsyncMock(
                return_value=mock_currency_converter
            )
            mock_currency_converter.__aexit__ = AsyncMock(return_value=None)
            mock_currency_converter.get_currency_code = Mock(return_value="USD")
            mock_currency_converter.get_currency_symbol = Mock(return_value="$")

            # Mock convert_amount to return Ok Result with same amount (USD = no conversion)
            def create_result_ok(amount):
                from ccusage.core.result import Ok

                return Ok(amount)

            mock_currency_converter.convert_amount = AsyncMock(
                side_effect=create_result_ok
            )
            mock_currency_converter_class.return_value = mock_currency_converter

            monthly_command(
                False,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                False,
                None,
            )

            mock_get_paths.assert_called_once()

    @patch("ccusage.commands.monthly.get_claude_paths")
    @patch("ccusage.commands.monthly.validate_claude_paths")
    @patch("ccusage.commands.monthly.DataLoader")
    @patch("ccusage.commands.monthly.DataProcessor")
    @patch("ccusage.commands.monthly.ResponsiveTableFormatter")
    @patch("ccusage.commands.monthly.console")
    def test_monthly_command_json_output(
        self,
        mock_console,
        mock_formatter_class,
        mock_processor_class,
        mock_loader_class,
        mock_validate,
        mock_get_paths,
        sample_monthly_usage,
    ):
        """Test monthly command JSON output."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_monthly_usage = AsyncMock(
            return_value=Ok(sample_monthly_usage)
        )
        mock_processor.calculate_totals = AsyncMock(
            return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
        )
        mock_processor_class.return_value = mock_processor

        with patch("logging.getLogger"):
            monthly_command(
                True,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                False,
                None,
            )

        mock_console.print_json.assert_called_once()

    @patch("ccusage.commands.monthly.get_claude_paths")
    @patch("ccusage.commands.monthly.validate_claude_paths")
    @patch("ccusage.commands.monthly.DataLoader")
    def test_monthly_command_configuration_error(
        self, mock_loader_class, mock_validate, mock_get_paths
    ):
        """Test monthly command configuration error."""
        mock_get_paths.side_effect = ConfigurationError("Config error")

        with pytest.raises(ConfigurationError):
            monthly_command(
                False,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                False,
                None,
            )

    @patch("ccusage.commands.monthly.get_claude_paths")
    @patch("ccusage.commands.monthly.validate_claude_paths")
    @patch("ccusage.commands.monthly.DataLoader")
    def test_monthly_command_data_load_error(
        self, mock_loader_class, mock_validate, mock_get_paths
    ):
        """Test monthly command data load error."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Err("Load error"))
        mock_loader_class.return_value = mock_loader

        with pytest.raises(CcusageError, match="Failed to load data: Load error"):
            monthly_command(
                False,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                False,
                None,
            )

    @patch("ccusage.commands.monthly.get_claude_paths")
    @patch("ccusage.commands.monthly.validate_claude_paths")
    @patch("ccusage.commands.monthly.DataLoader")
    @patch("ccusage.commands.monthly.DataProcessor")
    def test_monthly_command_processing_error(
        self, mock_processor_class, mock_loader_class, mock_validate, mock_get_paths
    ):
        """Test monthly command processing error."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_monthly_usage = AsyncMock(
            return_value=Err("Processing error")
        )
        mock_processor.calculate_totals = AsyncMock(
            return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
        )
        mock_processor_class.return_value = mock_processor

        with pytest.raises(
            CcusageError, match="Failed to process data: Processing error"
        ):
            monthly_command(
                False,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                False,
                None,
            )

    def test_monthly_command_no_data_found_json(self):
        """Test monthly command when no data found with JSON output."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.console") as mock_console,
            patch("logging.getLogger"),
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            monthly_command(
                True,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                False,
                None,
            )

            mock_console.print_json.assert_called_with("[]")

    def test_monthly_command_no_data_found_table(self):
        """Test monthly command when no data found with table output."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.console") as mock_console,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            monthly_command(
                False,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                False,
                None,
            )

            mock_console.print.assert_called_with(
                "[yellow]No Claude usage data found.[/yellow]"
            )

    def test_monthly_command_totals_calculation_error(self, sample_monthly_usage):
        """Test monthly command when totals calculation fails."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.monthly.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.monthly.console") as mock_console,
            patch(
                "ccusage.commands.monthly.CurrencyConverter"
            ) as mock_currency_converter_class,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_monthly_usage = AsyncMock(
                return_value=Ok(sample_monthly_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Err("Totals error")
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_monthly_table = Mock(return_value="table_output")
            mock_formatter.format_summary_panel = Mock(return_value="summary_output")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_currency_converter = Mock()
            mock_currency_converter.__aenter__ = AsyncMock(
                return_value=mock_currency_converter
            )
            mock_currency_converter.__aexit__ = AsyncMock(return_value=None)
            mock_currency_converter.get_currency_code = Mock(return_value="USD")
            mock_currency_converter.get_currency_symbol = Mock(return_value="$")

            # Mock convert_amount to return Ok Result with same amount (USD = no conversion)
            def create_result_ok(amount):
                from ccusage.core.result import Ok

                return Ok(amount)

            mock_currency_converter.convert_amount = AsyncMock(
                side_effect=create_result_ok
            )
            mock_currency_converter_class.return_value = mock_currency_converter

            monthly_command(
                False,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                False,
                None,
            )

            # Should still format the table
            mock_formatter.format_monthly_table.assert_called_once()

    def test_monthly_command_with_offline_flag(self, sample_monthly_usage):
        """Test monthly command with offline flag."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.monthly.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.monthly.console") as mock_console,
            patch(
                "ccusage.commands.monthly.CurrencyConverter"
            ) as mock_currency_converter_class,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_monthly_usage = AsyncMock(
                return_value=Ok(sample_monthly_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_monthly_table = Mock(return_value="table_output")
            mock_formatter.format_summary_panel = Mock(return_value="summary_output")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_currency_converter = Mock()
            mock_currency_converter.__aenter__ = AsyncMock(
                return_value=mock_currency_converter
            )
            mock_currency_converter.__aexit__ = AsyncMock(return_value=None)
            mock_currency_converter.get_currency_code = Mock(return_value="USD")
            mock_currency_converter.get_currency_symbol = Mock(return_value="$")

            # Mock convert_amount to return Ok Result with same amount (USD = no conversion)
            def create_result_ok(amount):
                from ccusage.core.result import Ok

                return Ok(amount)

            mock_currency_converter.convert_amount = AsyncMock(
                side_effect=create_result_ok
            )
            mock_currency_converter_class.return_value = mock_currency_converter

            monthly_command(
                False,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                True,
                False,
                None,
            )

            # Verify processor was called with offline flag
            mock_processor_class.assert_called_with(CostMode.AUTO, True)

    def test_monthly_command_empty_data_no_totals(self):
        """Test monthly command with empty data (no totals calculation)."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.monthly.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.monthly.console") as mock_console,
            patch(
                "ccusage.commands.monthly.CurrencyConverter"
            ) as mock_currency_converter_class,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_monthly_usage = AsyncMock(
                return_value=Ok([])
            )  # Empty monthly usage
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_monthly_table = Mock(return_value="table_output")
            mock_formatter.format_summary_panel = Mock(return_value="summary_output")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_currency_converter = Mock()
            mock_currency_converter.__aenter__ = AsyncMock(
                return_value=mock_currency_converter
            )
            mock_currency_converter.__aexit__ = AsyncMock(return_value=None)
            mock_currency_converter.get_currency_code = Mock(return_value="USD")
            mock_currency_converter.get_currency_symbol = Mock(return_value="$")

            # Mock convert_amount to return Ok Result with same amount (USD = no conversion)
            def create_result_ok(amount):
                from ccusage.core.result import Ok

                return Ok(amount)

            mock_currency_converter.convert_amount = AsyncMock(
                side_effect=create_result_ok
            )
            mock_currency_converter_class.return_value = mock_currency_converter

            monthly_command(
                False,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                False,
                None,
            )

            # Should format table but not call calculate_totals
            mock_formatter.format_monthly_table.assert_called_once()
            mock_processor.calculate_totals.assert_not_called()

    def test_monthly_command_with_graph_flag(self, sample_totals):
        """Test monthly command with graph flag enabled."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.monthly.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.monthly.console") as mock_console,
            patch(
                "ccusage.commands.monthly.CurrencyConverter"
            ) as mock_currency_converter_class,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            # Create multiple monthly usage entries to trigger sparkline
            multiple_monthly_usage = [
                MonthlyUsage(
                    month="2025-07",
                    input_tokens=300,
                    output_tokens=150,
                    cache_creation_tokens=75,
                    cache_read_tokens=30,
                    total_cost=0.03,
                    models_used=["claude-sonnet-4-20250514"],
                    model_breakdowns=[],
                ),
                MonthlyUsage(
                    month="2025-06",
                    input_tokens=200,
                    output_tokens=100,
                    cache_creation_tokens=50,
                    cache_read_tokens=20,
                    total_cost=0.02,
                    models_used=["claude-sonnet-4-20250514"],
                    model_breakdowns=[],
                ),
            ]

            mock_processor = Mock()
            mock_processor.process_monthly_usage = AsyncMock(
                return_value=Ok(multiple_monthly_usage)
            )
            mock_processor.calculate_totals = AsyncMock(return_value=Ok(sample_totals))
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_monthly_table = Mock(return_value="table_output")
            mock_formatter.format_summary_panel = Mock(return_value="summary_output")
            mock_formatter.terminal_width = 120  # Wide enough for graphs
            mock_formatter.graph_generator = Mock()
            mock_formatter.graph_generator.generate_cost_bar_chart = Mock(
                return_value="mock_chart"
            )
            mock_formatter.graph_generator.generate_sparkline = Mock(
                return_value="mock_sparkline"
            )
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_currency_converter = Mock()
            mock_currency_converter.__aenter__ = AsyncMock(
                return_value=mock_currency_converter
            )
            mock_currency_converter.__aexit__ = AsyncMock(return_value=None)
            mock_currency_converter.get_currency_code = Mock(return_value="USD")
            mock_currency_converter.get_currency_symbol = Mock(return_value="$")

            # Mock convert_amount to return Ok Result with same amount (USD = no conversion)
            def create_result_ok(amount):
                from ccusage.core.result import Ok

                return Ok(amount)

            mock_currency_converter.convert_amount = AsyncMock(
                side_effect=create_result_ok
            )
            mock_currency_converter_class.return_value = mock_currency_converter

            monthly_command(
                False,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                True,
                None,
            )

            # Verify graph generation was called
            mock_formatter.graph_generator.generate_cost_bar_chart.assert_called_once()
            mock_formatter.graph_generator.generate_sparkline.assert_called_once()

    @pytest.mark.asyncio
    async def test_monthly_command_async_data_load_error(self):
        """Test monthly command when data loading fails."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Err("Load error"))
            mock_loader_class.return_value = mock_loader

            # Test data load error
            with pytest.raises(CcusageError, match="Failed to load data: Load error"):
                await _monthly_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_monthly_command_async_processing_error(self):
        """Test monthly command when data processing fails."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_monthly_usage = AsyncMock(
                return_value=Err("Processing error")
            )
            mock_processor_class.return_value = mock_processor

            # Test processing error
            with pytest.raises(
                CcusageError, match="Failed to process data: Processing error"
            ):
                await _monthly_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_monthly_command_async_generic_exception(self):
        """Test monthly command when generic exception occurs."""
        with patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths:
            # Setup mocks to raise generic exception
            mock_get_paths.side_effect = ValueError("Generic error")

            # Test generic exception
            with pytest.raises(
                CcusageError, match="Monthly command failed: Generic error"
            ):
                await _monthly_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_monthly_command_async_ccusage_error_passthrough(self):
        """Test monthly command when CcusageError is raised (should pass through)."""
        with patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths:
            # Setup mocks to raise CcusageError
            mock_get_paths.side_effect = CcusageError("Direct error")

            # Test CcusageError passthrough
            with pytest.raises(CcusageError, match="Direct error"):
                await _monthly_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    mode=CostMode.AUTO,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_monthly_command_async_no_monthly_data(self):
        """Test monthly command when no monthly data after processing."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.monthly.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.monthly.console") as mock_console,
            patch(
                "ccusage.commands.monthly.CurrencyConverter"
            ) as mock_currency_converter_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_monthly_usage = AsyncMock(
                return_value=Ok([])
            )  # Empty monthly data
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_monthly_table = Mock(return_value="mock_table")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_currency_converter = Mock()
            mock_currency_converter.__aenter__ = AsyncMock(
                return_value=mock_currency_converter
            )
            mock_currency_converter.__aexit__ = AsyncMock(return_value=None)
            mock_currency_converter.get_currency_code = Mock(return_value="USD")
            mock_currency_converter.get_currency_symbol = Mock(return_value="$")

            # Mock convert_amount to return Ok Result with same amount (USD = no conversion)
            def create_result_ok(amount):
                from ccusage.core.result import Ok

                return Ok(amount)

            mock_currency_converter.convert_amount = AsyncMock(
                side_effect=create_result_ok
            )
            mock_currency_converter_class.return_value = mock_currency_converter

            # Test no monthly data after processing
            await _monthly_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify table was formatted but no summary
            mock_formatter.format_monthly_table.assert_called_once()
            mock_formatter.format_summary_panel.assert_not_called()

    @pytest.mark.asyncio
    async def test_monthly_command_async_no_data_json(self):
        """Test monthly command when no data is found with JSON output."""
        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.console") as mock_console,
            patch("logging.getLogger") as mock_get_logger,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            # Test no data with JSON output
            await _monthly_command_async(
                json_output=True,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify JSON output for no data
            mock_console.print_json.assert_called_with("[]")

    @pytest.mark.asyncio
    async def test_monthly_command_async_sparkline_multiple_items(self):
        """Test monthly command with multiple monthly data items to trigger sparkline generation."""
        # Create sample data with multiple items
        multiple_monthly_usage = [
            MonthlyUsage(
                month="2025-06",
                input_tokens=100,
                output_tokens=50,
                cache_creation_tokens=25,
                cache_read_tokens=10,
                total_cost=0.01,
                models_used=["claude-sonnet-4-20250514"],
                model_breakdowns=[],
            ),
            MonthlyUsage(
                month="2025-07",
                input_tokens=200,
                output_tokens=100,
                cache_creation_tokens=50,
                cache_read_tokens=20,
                total_cost=0.02,
                models_used=["claude-sonnet-4-20250514"],
                model_breakdowns=[],
            ),
        ]

        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.monthly.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.monthly.console") as mock_console,
            patch(
                "ccusage.commands.monthly.CurrencyConverter"
            ) as mock_currency_converter_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_monthly_usage = AsyncMock(
                return_value=Ok(multiple_monthly_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_monthly_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter.terminal_width = 120
            mock_formatter.graph_generator = Mock()
            mock_formatter.graph_generator.generate_cost_bar_chart = Mock(
                return_value="mock_chart"
            )
            mock_formatter.graph_generator.generate_sparkline = Mock(
                return_value="mock_sparkline"
            )
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock
            mock_currency_converter = Mock()
            mock_currency_converter.__aenter__ = AsyncMock(
                return_value=mock_currency_converter
            )
            mock_currency_converter.__aexit__ = AsyncMock(return_value=None)
            mock_currency_converter.get_currency_code = Mock(return_value="USD")
            mock_currency_converter.get_currency_symbol = Mock(return_value="$")

            # Mock convert_amount to return Ok Result with same amount (USD = no conversion)
            def create_result_ok(amount):
                from ccusage.core.result import Ok

                return Ok(amount)

            mock_currency_converter.convert_amount = AsyncMock(
                side_effect=create_result_ok
            )
            mock_currency_converter_class.return_value = mock_currency_converter

            # Test with graphs enabled and multiple items
            await _monthly_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=True,
                currency=None,
            )

            # Verify sparkline generation was called
            mock_formatter.graph_generator.generate_sparkline.assert_called_once()

            # Verify the sparkline call parameters
            sparkline_call_args = (
                mock_formatter.graph_generator.generate_sparkline.call_args
            )
            assert (
                sparkline_call_args[0][0] == multiple_monthly_usage
            )  # First positional arg should be the data
            assert "Monthly Cost Trend" in str(
                sparkline_call_args
            )  # Should contain the title

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_monthly_command_async_currency_conversion_success(
        self, sample_totals
    ):
        """Test monthly command with successful currency conversion (covers lines 122-123, 142-147)."""
        from ccusage.core.result import Ok
        from ccusage.models.usage import ModelBreakdown, MonthlyUsage

        # Create sample data with model breakdowns
        sample_breakdown = ModelBreakdown(
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            cost=0.05,
        )

        sample_monthly_with_breakdown = [
            MonthlyUsage(
                month="2025-07",
                input_tokens=100,
                output_tokens=50,
                cache_creation_tokens=25,
                cache_read_tokens=10,
                total_cost=0.10,
                models_used=["claude-sonnet-4-20250514"],
                model_breakdowns=[sample_breakdown],
            ),
        ]

        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.monthly.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.monthly.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.monthly.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_monthly_usage = AsyncMock(
                return_value=Ok(sample_monthly_with_breakdown)
            )
            mock_processor.calculate_totals = AsyncMock(return_value=Ok(sample_totals))
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_monthly_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock for EUR (non-USD)
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(
                return_value="EUR"
            )  # Non-USD currency
            mock_converter_instance.get_currency_symbol = Mock(return_value="€")

            # Mock convert_amount to return converted values
            mock_converter_instance.convert_amount = AsyncMock(
                return_value=Ok(0.092)
            )  # Converted cost
            mock_currency_converter.return_value = mock_converter_instance

            # Test with EUR currency (will trigger conversion logic)
            await _monthly_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency="eur",
            )

            # Verify currency conversion was called
            # Should be called twice: once for main cost, once for breakdown cost
            assert mock_converter_instance.convert_amount.call_count == 2

            # Verify the calls were for the right amounts
            call_args_list = mock_converter_instance.convert_amount.call_args_list
            assert call_args_list[0][0][0] == 0.10  # Main cost conversion
            assert call_args_list[1][0][0] == 0.05  # Breakdown cost conversion

            # Verify table formatting was called
            mock_formatter.format_monthly_table.assert_called_once()
            mock_formatter.format_summary_panel.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_monthly_command_async_currency_conversion_failed(
        self, sample_totals
    ):
        """Test monthly command when currency conversion fails (fallback to original cost)."""
        from ccusage.core.result import Err, Ok
        from ccusage.models.usage import ModelBreakdown, MonthlyUsage

        # Create sample data with model breakdowns
        sample_breakdown = ModelBreakdown(
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            cost=0.05,
        )

        sample_monthly_with_breakdown = [
            MonthlyUsage(
                month="2025-07",
                input_tokens=100,
                output_tokens=50,
                cache_creation_tokens=25,
                cache_read_tokens=10,
                total_cost=0.10,
                models_used=["claude-sonnet-4-20250514"],
                model_breakdowns=[sample_breakdown],
            ),
        ]

        with (
            patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.monthly.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.monthly.DataLoader") as mock_loader_class,
            patch("ccusage.commands.monthly.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.monthly.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.monthly.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.monthly.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_monthly_usage = AsyncMock(
                return_value=Ok(sample_monthly_with_breakdown)
            )
            mock_processor.calculate_totals = AsyncMock(return_value=Ok(sample_totals))
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_monthly_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock for EUR (non-USD) with conversion failures
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(
                return_value="EUR"
            )  # Non-USD currency
            mock_converter_instance.get_currency_symbol = Mock(return_value="€")

            # Mock convert_amount to return error (conversion fails)
            mock_converter_instance.convert_amount = AsyncMock(
                return_value=Err("Conversion failed")
            )
            mock_currency_converter.return_value = mock_converter_instance

            # Test with EUR currency (will trigger conversion logic that fails)
            await _monthly_command_async(
                json_output=False,
                since=None,
                until=None,
                mode=CostMode.AUTO,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency="eur",
            )

            # Verify currency conversion was attempted
            assert mock_converter_instance.convert_amount.call_count == 2

            # Verify table formatting was still called (with original costs as fallback)
            mock_formatter.format_monthly_table.assert_called_once()
            mock_formatter.format_summary_panel.assert_called_once()


class TestSessionCommand:
    """Test the session command."""

    def test_session_command_wrapper(self):
        """Test session_command wrapper function."""
        with patch("asyncio.run") as mock_asyncio_run:
            session_command(
                json_output=True,
                since="2025-07-15",
                until="2025-07-16",
                order=SortOrder.ASC,
                breakdown=True,
                offline=True,
                graph=True,
                currency=None,
            )

            mock_asyncio_run.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_session_command_async_success(self, sample_session_usage):
        """Test successful session command execution."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.session.console") as mock_console,
            patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
            warnings.catch_warnings(),
        ):
            warnings.simplefilter("ignore", RuntimeWarning)

            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(sample_session_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )

            # Ensure any other async methods that might exist don't create unawaited coroutines
            mock_processor.process_daily_usage = AsyncMock()
            mock_processor.process_monthly_usage = AsyncMock()

            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter.terminal_width = 120
            mock_formatter.graph_generator = Mock()
            mock_formatter.graph_generator.generate_session_activity_chart = Mock(
                return_value="mock_activity"
            )
            mock_formatter.graph_generator.generate_cost_comparison_chart = Mock(
                return_value="mock_comparison"
            )
            mock_formatter_class.return_value = mock_formatter

            # Mock currency converter
            mock_converter = Mock()
            mock_converter.get_currency_code = Mock(return_value="USD")
            mock_converter.get_currency_symbol = Mock(return_value="$")
            mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
            mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
            mock_converter.__aexit__ = AsyncMock(return_value=None)
            mock_converter_class.return_value = mock_converter

            # Test successful execution
            await _session_command_async(
                json_output=False,
                since="2025-07-15",
                until="2025-07-16",
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=True,
                currency=None,
            )

            # Verify calls
            mock_get_paths.assert_called_once()
            mock_validate.assert_called_once()
            mock_loader.load_raw_entries.assert_called_once()
            mock_processor.process_session_usage.assert_called_once()
            mock_formatter.format_session_table.assert_called_once()
            mock_formatter.format_summary_panel.assert_called_once()
            mock_console.print.assert_called()

    @pytest.mark.asyncio
    async def test_session_command_async_json_output(self, sample_session_usage):
        """Test session command with JSON output."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            with (
                patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
                patch(
                    "ccusage.commands.session.validate_claude_paths"
                ) as mock_validate,
                patch("ccusage.commands.session.DataLoader") as mock_loader_class,
                patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
                patch("ccusage.commands.session.console") as mock_console,
                patch("logging.getLogger") as mock_get_logger,
            ):
                # Setup mocks
                mock_get_paths.return_value = [Path("/path/to/claude")]
                mock_validate.return_value = None

                mock_loader = Mock()
                mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
                mock_loader_class.return_value = mock_loader

                mock_processor = Mock()
                mock_processor.process_session_usage = AsyncMock(
                    return_value=Ok(sample_session_usage)
                )
                mock_processor_class.return_value = mock_processor

                # Test JSON output
                await _session_command_async(
                    json_output=True,
                    since=None,
                    until=None,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

                # Verify logging suppression
                mock_get_logger.assert_called_once()
                mock_get_logger().setLevel.assert_called_once()

                # Verify JSON output
                mock_console.print_json.assert_called_once()

                # Clean up AsyncMock objects to avoid warnings
                mock_loader.load_raw_entries.reset_mock()
                mock_processor.process_session_usage.reset_mock()

    @pytest.mark.asyncio
    async def test_session_command_async_no_data(self):
        """Test session command when no data is found."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            # Test no data
            await _session_command_async(
                json_output=False,
                since=None,
                until=None,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify no data message
            mock_console.print.assert_called_with(
                "[yellow]No Claude usage data found.[/yellow]"
            )

    @patch("ccusage.commands.session.get_claude_paths")
    @patch("ccusage.commands.session.validate_claude_paths")
    @patch("ccusage.commands.session.DataLoader")
    def test_session_command_success(
        self, mock_loader_class, mock_validate, mock_get_paths, sample_session_usage
    ):
        """Test session command success."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        with (
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.session.console") as mock_console,
            patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
        ):
            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(sample_session_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="table_output")
            mock_formatter.format_summary_panel = Mock(return_value="summary_output")
            mock_formatter_class.return_value = mock_formatter

            # Mock currency converter
            mock_converter = Mock()
            mock_converter.get_currency_code = Mock(return_value="USD")
            mock_converter.get_currency_symbol = Mock(return_value="$")
            mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
            mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
            mock_converter.__aexit__ = AsyncMock(return_value=None)
            mock_converter_class.return_value = mock_converter

            session_command(
                False, None, None, SortOrder.DESC, False, False, False, None
            )

            mock_get_paths.assert_called_once()

    @patch("ccusage.commands.session.get_claude_paths")
    @patch("ccusage.commands.session.validate_claude_paths")
    @patch("ccusage.commands.session.DataLoader")
    @patch("ccusage.commands.session.DataProcessor")
    @patch("ccusage.commands.session.ResponsiveTableFormatter")
    @patch("ccusage.commands.session.console")
    def test_session_command_json_output(
        self,
        mock_console,
        mock_formatter_class,
        mock_processor_class,
        mock_loader_class,
        mock_validate,
        mock_get_paths,
        sample_session_usage,
    ):
        """Test session command JSON output."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_session_usage = AsyncMock(
            return_value=Ok(sample_session_usage)
        )
        mock_processor.calculate_totals = AsyncMock(
            return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
        )
        mock_processor_class.return_value = mock_processor

        with patch("logging.getLogger"):
            session_command(True, None, None, SortOrder.DESC, False, False, False, None)

        mock_console.print_json.assert_called_once()

    @patch("ccusage.commands.session.get_claude_paths")
    @patch("ccusage.commands.session.validate_claude_paths")
    @patch("ccusage.commands.session.DataLoader")
    def test_session_command_configuration_error(
        self, mock_loader_class, mock_validate, mock_get_paths
    ):
        """Test session command configuration error."""
        mock_get_paths.side_effect = ConfigurationError("Config error")

        with pytest.raises(ConfigurationError):
            session_command(
                False, None, None, SortOrder.DESC, False, False, False, None
            )

    @patch("ccusage.commands.session.get_claude_paths")
    @patch("ccusage.commands.session.validate_claude_paths")
    @patch("ccusage.commands.session.DataLoader")
    def test_session_command_data_load_error(
        self, mock_loader_class, mock_validate, mock_get_paths
    ):
        """Test session command data load error."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Err("Load error"))
        mock_loader_class.return_value = mock_loader

        with pytest.raises(CcusageError, match="Failed to load data: Load error"):
            session_command(
                False, None, None, SortOrder.DESC, False, False, False, None
            )

    @patch("ccusage.commands.session.get_claude_paths")
    @patch("ccusage.commands.session.validate_claude_paths")
    @patch("ccusage.commands.session.DataLoader")
    @patch("ccusage.commands.session.DataProcessor")
    def test_session_command_processing_error(
        self, mock_processor_class, mock_loader_class, mock_validate, mock_get_paths
    ):
        """Test session command processing error."""
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_session_usage = AsyncMock(
            return_value=Err("Processing error")
        )
        mock_processor.calculate_totals = AsyncMock(
            return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
        )
        mock_processor_class.return_value = mock_processor

        with pytest.raises(
            CcusageError, match="Failed to process data: Processing error"
        ):
            session_command(
                False, None, None, SortOrder.DESC, False, False, False, None
            )

    def test_session_command_no_data_found_json(self):
        """Test session command when no data found with JSON output."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.console") as mock_console,
            patch("logging.getLogger"),
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            session_command(True, None, None, SortOrder.DESC, False, False, False, None)

            mock_console.print_json.assert_called_with("[]")

    def test_session_command_no_data_found_table(self):
        """Test session command when no data found with table output."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.console") as mock_console,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([]))
            mock_loader_class.return_value = mock_loader

            session_command(
                False, None, None, SortOrder.DESC, False, False, False, None
            )

            mock_console.print.assert_called_with(
                "[yellow]No Claude usage data found.[/yellow]"
            )

    def test_session_command_totals_calculation_error(self, sample_session_usage):
        """Test session command when totals calculation fails."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.session.console") as mock_console,
            patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(sample_session_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Err("Totals error")
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="table_output")
            mock_formatter.format_summary_panel = Mock(return_value="summary_output")
            mock_formatter_class.return_value = mock_formatter

            # Mock currency converter
            mock_converter = Mock()
            mock_converter.get_currency_code = Mock(return_value="USD")
            mock_converter.get_currency_symbol = Mock(return_value="$")
            mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
            mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
            mock_converter.__aexit__ = AsyncMock(return_value=None)
            mock_converter_class.return_value = mock_converter

            session_command(
                False, None, None, SortOrder.DESC, False, False, False, None
            )

            # Should still format the table
            mock_formatter.format_session_table.assert_called_once()

    def test_session_command_with_offline_flag(self, sample_session_usage):
        """Test session command with offline flag."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.session.console") as mock_console,
            patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
        ):
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(sample_session_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="table_output")
            mock_formatter.format_summary_panel = Mock(return_value="summary_output")
            mock_formatter_class.return_value = mock_formatter

            # Mock currency converter
            mock_converter = Mock()
            mock_converter.get_currency_code = Mock(return_value="USD")
            mock_converter.get_currency_symbol = Mock(return_value="$")
            mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
            mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
            mock_converter.__aexit__ = AsyncMock(return_value=None)
            mock_converter_class.return_value = mock_converter

            session_command(False, None, None, SortOrder.DESC, False, True, False, None)

            # Verify processor was called with offline flag
            mock_processor_class.assert_called_with(CostMode.AUTO, True)

    @pytest.mark.asyncio
    async def test_session_command_async_data_load_error(self):
        """Test session command when data loading fails."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Err("Load error"))
            mock_loader_class.return_value = mock_loader

            # Test data load error
            with pytest.raises(CcusageError, match="Failed to load data: Load error"):
                await _session_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_session_command_async_processing_error(self):
        """Test session command when data processing fails."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Err("Processing error")
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            # Test processing error
            with pytest.raises(
                CcusageError, match="Failed to process data: Processing error"
            ):
                await _session_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_session_command_async_generic_exception(self):
        """Test session command when generic exception occurs."""
        with patch("ccusage.commands.session.get_claude_paths") as mock_get_paths:
            # Setup mocks to raise generic exception
            mock_get_paths.side_effect = ValueError("Generic error")

            # Test generic exception
            with pytest.raises(
                CcusageError, match="Session command failed: Generic error"
            ):
                await _session_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_session_command_async_ccusage_error_passthrough(self):
        """Test session command when CcusageError is raised (should pass through)."""
        with patch("ccusage.commands.session.get_claude_paths") as mock_get_paths:
            # Setup mocks to raise CcusageError
            mock_get_paths.side_effect = CcusageError("Direct error")

            # Test CcusageError passthrough
            with pytest.raises(CcusageError, match="Direct error"):
                await _session_command_async(
                    json_output=False,
                    since=None,
                    until=None,
                    order=SortOrder.DESC,
                    breakdown=False,
                    offline=False,
                    graph=False,
                    currency=None,
                )

    @pytest.mark.asyncio
    async def test_session_command_async_today_label_test(self, sample_session_usage):
        """Test session command with today label detection."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.session.console") as mock_console,
            patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
            patch("datetime.date") as mock_date_module,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(sample_session_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Mock currency converter
            mock_converter = Mock()
            mock_converter.get_currency_code = Mock(return_value="USD")
            mock_converter.get_currency_symbol = Mock(return_value="$")
            mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
            mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
            mock_converter.__aexit__ = AsyncMock(return_value=None)
            mock_converter_class.return_value = mock_converter

            # Mock today's date
            mock_date_module.today.return_value.strftime.return_value = "2025-07-15"

            # Test with today's date
            await _session_command_async(
                json_output=False,
                since="2025-07-15",
                until="2025-07-15",
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify summary panel was called with today labels
            mock_formatter.format_summary_panel.assert_called_once()
            args, kwargs = mock_formatter.format_summary_panel.call_args
            # Check if any of the arguments contains "Today"
            all_args = list(args) + list(kwargs.values())
            assert any("Today" in str(arg) for arg in all_args)

    @pytest.mark.asyncio
    async def test_session_command_async_specific_date_not_today(
        self, sample_session_usage
    ):
        """Test session command with specific date that's not today."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.session.console") as mock_console,
            patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
            patch("datetime.date") as mock_date_module,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(sample_session_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Mock currency converter
            mock_converter = Mock()
            mock_converter.get_currency_code = Mock(return_value="USD")
            mock_converter.get_currency_symbol = Mock(return_value="$")
            mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
            mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
            mock_converter.__aexit__ = AsyncMock(return_value=None)
            mock_converter_class.return_value = mock_converter

            # Mock today's date (different from filter date)
            mock_date_module.today.return_value.strftime.return_value = "2025-07-16"

            # Test with specific date that's not today
            await _session_command_async(
                json_output=False,
                since="2025-07-15",
                until="2025-07-15",
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify summary panel was called with day labels
            mock_formatter.format_summary_panel.assert_called_once()
            args, kwargs = mock_formatter.format_summary_panel.call_args
            # Check if any of the arguments contains "Day"
            all_args = list(args) + list(kwargs.values())
            assert any("Day" in str(arg) for arg in all_args)

    @pytest.mark.asyncio
    async def test_session_command_async_date_range_filtering(
        self, sample_session_usage
    ):
        """Test session command with date range filtering."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.session.console") as mock_console,
            patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(sample_session_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Mock currency converter
            mock_converter = Mock()
            mock_converter.get_currency_code = Mock(return_value="USD")
            mock_converter.get_currency_symbol = Mock(return_value="$")
            mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
            mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
            mock_converter.__aexit__ = AsyncMock(return_value=None)
            mock_converter_class.return_value = mock_converter

            # Test with date range
            await _session_command_async(
                json_output=False,
                since="2025-07-15",
                until="2025-07-20",
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify summary panel was called with filtered labels
            mock_formatter.format_summary_panel.assert_called_once()
            args, kwargs = mock_formatter.format_summary_panel.call_args
            # Check if any of the arguments contains "Filtered"
            all_args = list(args) + list(kwargs.values())
            assert any("Filtered" in str(arg) for arg in all_args)

    @pytest.mark.asyncio
    async def test_session_command_async_no_filtering(self, sample_session_usage):
        """Test session command with no filtering."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.session.console") as mock_console,
            patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(sample_session_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Mock currency converter
            mock_converter = Mock()
            mock_converter.get_currency_code = Mock(return_value="USD")
            mock_converter.get_currency_symbol = Mock(return_value="$")
            mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
            mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
            mock_converter.__aexit__ = AsyncMock(return_value=None)
            mock_converter_class.return_value = mock_converter

            # Test with no filtering
            await _session_command_async(
                json_output=False,
                since=None,
                until=None,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify summary panel was called with total labels
            mock_formatter.format_summary_panel.assert_called_once()
            args, kwargs = mock_formatter.format_summary_panel.call_args
            # Check if any of the arguments contains "Total"
            all_args = list(args) + list(kwargs.values())
            assert any("Total" in str(arg) for arg in all_args)

    @pytest.mark.asyncio
    async def test_session_command_async_no_session_data(self):
        """Test session command when no session data after processing."""
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch("ccusage.commands.session.console") as mock_console,
            patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok([])
            )  # Empty session data
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="mock_table")
            mock_formatter_class.return_value = mock_formatter

            # Mock currency converter
            mock_converter = Mock()
            mock_converter.get_currency_code = Mock(return_value="USD")
            mock_converter.get_currency_symbol = Mock(return_value="$")
            mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
            mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
            mock_converter.__aexit__ = AsyncMock(return_value=None)
            mock_converter_class.return_value = mock_converter

            # Test no session data after processing
            await _session_command_async(
                json_output=False,
                since=None,
                until=None,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency=None,
            )

            # Verify table was formatted but no summary
            mock_formatter.format_session_table.assert_called_once()
            mock_formatter.format_summary_panel.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_session_command_async_custom_currency(self):
        """Test session command with custom currency conversion."""
        # Create test data with proper structure
        test_session_usage = [
            SessionUsage(
                session_id="test_session_1",
                project_path="/test/project",
                input_tokens=100,
                output_tokens=50,
                cache_creation_tokens=25,
                cache_read_tokens=10,
                total_cost=0.10,
                last_activity=datetime(2025, 7, 15, 10, 0, 0),
                versions=["1.0.43"],
                models_used=["claude-sonnet-4-20250514"],
                model_breakdowns=[],
            ),
        ]
        
        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.session.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.session.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(test_session_usage)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock for USD (no conversion needed)
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(return_value="USD")
            mock_converter_instance.get_currency_symbol = Mock(return_value="$")
            mock_currency_converter.return_value = mock_converter_instance

            # Test with custom currency (USD) - this covers lines 144-145
            await _session_command_async(
                json_output=False,
                since=None,
                until=None,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency="usd",
            )

            # Verify CurrencyConverter was called with correct parameters
            mock_currency_converter.assert_called_once()
            args = mock_currency_converter.call_args[0]
            kwargs = mock_currency_converter.call_args[1]

            # Should be called with CUSTOM mode and USD as target currency
            from ccusage.currency.converter import CurrencyMode

            assert (
                kwargs.get("currency_mode") == CurrencyMode.CUSTOM
                or args[1] == CurrencyMode.CUSTOM
            )
            assert kwargs.get("target_currency") == "USD" or args[2] == "USD"

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_session_command_async_currency_conversion_non_usd(self):
        """Test session command with currency conversion for non-USD currency."""
        from ccusage.core.result import Ok
        from ccusage.models.usage import SessionUsage, ModelBreakdown

        # Create sample data with model breakdowns for conversion testing
        sample_breakdown = ModelBreakdown(
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            cost=0.05,
        )

        sample_session_with_breakdown = [
            SessionUsage(
                session_id="test_session_1",
                project_path="/test/project",
                input_tokens=100,
                output_tokens=50,
                cache_creation_tokens=25,
                cache_read_tokens=10,
                total_cost=0.10,
                last_activity=datetime(2025, 7, 15, 10, 0, 0),
                versions=["1.0.43"],
                models_used=["claude-sonnet-4-20250514"],
                model_breakdowns=[sample_breakdown],
            ),
        ]

        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.session.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.session.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(sample_session_with_breakdown)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock for EUR (non-USD)
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(
                return_value="EUR"
            )  # Non-USD currency
            mock_converter_instance.get_currency_symbol = Mock(return_value="€")

            # Mock convert_amount to return converted values
            mock_converter_instance.convert_amount = AsyncMock(
                return_value=Ok(0.092)
            )  # Converted cost
            mock_currency_converter.return_value = mock_converter_instance

            # Test with EUR currency (will trigger conversion logic) - this covers lines 155-178
            await _session_command_async(
                json_output=False,
                since=None,
                until=None,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency="eur",
            )

            # Verify currency conversion was called
            # Should be called twice: once for main cost, once for breakdown cost
            assert mock_converter_instance.convert_amount.call_count == 2

            # Verify the calls were for the right amounts
            call_args_list = mock_converter_instance.convert_amount.call_args_list
            assert call_args_list[0][0][0] == 0.10  # Main cost conversion
            assert call_args_list[1][0][0] == 0.05  # Breakdown cost conversion

            # Verify table formatting was called
            mock_formatter.format_session_table.assert_called_once()
            mock_formatter.format_summary_panel.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    async def test_session_command_async_currency_conversion_failed(self):
        """Test session command when currency conversion fails (fallback to original cost)."""
        from ccusage.core.result import Err, Ok
        from ccusage.models.usage import SessionUsage, ModelBreakdown

        # Create sample data with model breakdowns
        sample_breakdown = ModelBreakdown(
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            cost=0.05,
        )

        sample_session_with_breakdown = [
            SessionUsage(
                session_id="test_session_1",
                project_path="/test/project",
                input_tokens=100,
                output_tokens=50,
                cache_creation_tokens=25,
                cache_read_tokens=10,
                total_cost=0.10,
                last_activity=datetime(2025, 7, 15, 10, 0, 0),
                versions=["1.0.43"],
                models_used=["claude-sonnet-4-20250514"],
                model_breakdowns=[sample_breakdown],
            ),
        ]

        with (
            patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
            patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
            patch("ccusage.commands.session.DataLoader") as mock_loader_class,
            patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
            patch(
                "ccusage.commands.session.ResponsiveTableFormatter"
            ) as mock_formatter_class,
            patch(
                "ccusage.commands.session.CurrencyConverter"
            ) as mock_currency_converter,
            patch("ccusage.commands.session.console") as mock_console,
        ):
            # Setup mocks
            mock_get_paths.return_value = [Path("/path/to/claude")]
            mock_validate.return_value = None

            mock_loader = Mock()
            mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
            mock_loader_class.return_value = mock_loader

            mock_processor = Mock()
            mock_processor.process_session_usage = AsyncMock(
                return_value=Ok(sample_session_with_breakdown)
            )
            mock_processor.calculate_totals = AsyncMock(
                return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
            )
            mock_processor_class.return_value = mock_processor

            mock_formatter = Mock()
            mock_formatter.format_session_table = Mock(return_value="mock_table")
            mock_formatter.format_summary_panel = Mock(return_value="mock_summary")
            mock_formatter_class.return_value = mock_formatter

            # Setup currency converter mock for EUR (non-USD) with conversion failures
            mock_converter_instance = AsyncMock()
            mock_converter_instance.__aenter__ = AsyncMock(
                return_value=mock_converter_instance
            )
            mock_converter_instance.__aexit__ = AsyncMock(return_value=None)
            mock_converter_instance.get_currency_code = Mock(
                return_value="EUR"
            )  # Non-USD currency
            mock_converter_instance.get_currency_symbol = Mock(return_value="€")

            # Mock convert_amount to return error (conversion fails)
            mock_converter_instance.convert_amount = AsyncMock(
                return_value=Err("Conversion failed")
            )
            mock_currency_converter.return_value = mock_converter_instance

            # Test with EUR currency (will trigger conversion logic that fails)
            await _session_command_async(
                json_output=False,
                since=None,
                until=None,
                order=SortOrder.DESC,
                breakdown=False,
                offline=False,
                graph=False,
                currency="eur",
            )

            # Verify currency conversion was attempted
            assert mock_converter_instance.convert_amount.call_count == 2

            # Verify table formatting was still called (with original costs as fallback)
            mock_formatter.format_session_table.assert_called_once()
            mock_formatter.format_summary_panel.assert_called_once()

    def test_session_convert_date_format(self):
        """Test session command date format conversion."""
        # Test None input
        assert session_convert_date_format(None) is None

        # Test empty string
        assert session_convert_date_format("") is None

        # Test already ISO format
        assert session_convert_date_format("2025-07-15") == "2025-07-15"

        # Test compact format conversion
        assert session_convert_date_format("20250715") == "2025-07-15"

        # Test invalid format (not 8 chars)
        assert session_convert_date_format("2025715") == "2025715"

        # Test with dash but different format
        assert session_convert_date_format("2025-7-15") == "2025-7-15"


def test_date_format_conversion():
    """Test date format conversion."""
    # Test daily command date conversion
    assert _convert_date_format("20250715") == "2025-07-15"
    assert _convert_date_format("2025-07-15") == "2025-07-15"
    assert _convert_date_format(None) is None


def test_session_date_format_conversion():
    """Test session command date format conversion."""
    # Test session command date conversion
    assert session_convert_date_format("20250715") == "2025-07-15"
    assert session_convert_date_format("2025-07-15") == "2025-07-15"
    assert session_convert_date_format(None) is None


def test_monthly_command_generic_exception(
    sample_monthly_usage,
):
    """Test monthly command generic exception."""
    with patch("ccusage.commands.monthly.get_claude_paths") as mock_get_paths:
        mock_get_paths.side_effect = Exception("Generic error")

        with pytest.raises(CcusageError, match="Monthly command failed: Generic error"):
            monthly_command(
                False,
                None,
                None,
                CostMode.AUTO,
                SortOrder.DESC,
                False,
                False,
                False,
                None,
            )


def test_session_command_generic_exception(
    sample_session_usage,
):
    """Test session command generic exception."""
    with patch("ccusage.commands.session.get_claude_paths") as mock_get_paths:
        mock_get_paths.side_effect = Exception("Generic error")

        with pytest.raises(CcusageError, match="Session command failed: Generic error"):
            session_command(
                False, None, None, SortOrder.DESC, False, False, False, None
            )


def test_session_command_with_date_filtering(
    sample_session_usage,
):
    """Test session command with date filtering."""
    with (
        patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
        patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
        patch("ccusage.commands.session.DataLoader") as mock_loader_class,
        patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
        patch(
            "ccusage.commands.session.ResponsiveTableFormatter"
        ) as mock_formatter_class,
        patch("ccusage.commands.session.console") as mock_console,
        patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
    ):
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_session_usage = AsyncMock(
            return_value=Ok(sample_session_usage)
        )
        mock_processor.calculate_totals = AsyncMock(
            return_value=Ok(Mock(total_tokens=1000, total_cost=0.15))
        )
        mock_processor_class.return_value = mock_processor

        mock_formatter = Mock()
        mock_formatter.format_session_table = Mock(return_value="table_output")
        mock_formatter.format_summary_panel = Mock(return_value="summary_output")
        mock_formatter_class.return_value = mock_formatter

        # Mock currency converter
        mock_converter = Mock()
        mock_converter.get_currency_code = Mock(return_value="USD")
        mock_converter.get_currency_symbol = Mock(return_value="$")
        mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
        mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
        mock_converter.__aexit__ = AsyncMock(return_value=None)
        mock_converter_class.return_value = mock_converter

        session_command(
            False, "2025-07-15", "2025-07-16", SortOrder.DESC, False, False, False, None
        )

        # Should call processor with date filtering
        mock_processor.process_session_usage.assert_called_once()


def test_session_command_today_label_test(sample_session_usage, sample_totals):
    """Test session command with today labels."""
    with (
        patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
        patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
        patch("ccusage.commands.session.DataLoader") as mock_loader_class,
        patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
        patch(
            "ccusage.commands.session.ResponsiveTableFormatter"
        ) as mock_formatter_class,
        patch("ccusage.commands.session.console") as mock_console,
        patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
        patch("datetime.date") as mock_date_module,
    ):
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_session_usage = AsyncMock(
            return_value=Ok(sample_session_usage)
        )
        mock_processor.calculate_totals = AsyncMock(return_value=Ok(sample_totals))
        mock_processor_class.return_value = mock_processor

        mock_formatter = Mock()
        mock_formatter.format_session_table = Mock(return_value="table_output")
        mock_formatter.format_summary_panel = Mock(return_value="summary_output")
        mock_formatter_class.return_value = mock_formatter

        # Mock currency converter
        mock_converter = Mock()
        mock_converter.get_currency_code = Mock(return_value="USD")
        mock_converter.get_currency_symbol = Mock(return_value="$")
        mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
        mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
        mock_converter.__aexit__ = AsyncMock(return_value=None)
        mock_converter_class.return_value = mock_converter

        # Mock today's date
        mock_date_module.today.return_value.strftime.return_value = "2025-07-15"

        session_command(
            False, "2025-07-15", "2025-07-15", SortOrder.DESC, False, False, False, None
        )

        # Should format with today labels
        mock_formatter.format_session_table.assert_called_once()


def test_session_command_specific_date_not_today(sample_session_usage, sample_totals):
    """Test session command with specific date not today."""
    with (
        patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
        patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
        patch("ccusage.commands.session.DataLoader") as mock_loader_class,
        patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
        patch(
            "ccusage.commands.session.ResponsiveTableFormatter"
        ) as mock_formatter_class,
        patch("ccusage.commands.session.console") as mock_console,
        patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
        patch("datetime.date") as mock_date_module,
    ):
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_session_usage = AsyncMock(
            return_value=Ok(sample_session_usage)
        )
        mock_processor.calculate_totals = AsyncMock(return_value=Ok(sample_totals))
        mock_processor_class.return_value = mock_processor

        mock_formatter = Mock()
        mock_formatter.format_session_table = Mock(return_value="table_output")
        mock_formatter.format_summary_panel = Mock(return_value="summary_output")
        mock_formatter_class.return_value = mock_formatter

        # Mock currency converter
        mock_converter = Mock()
        mock_converter.get_currency_code = Mock(return_value="USD")
        mock_converter.get_currency_symbol = Mock(return_value="$")
        mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
        mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
        mock_converter.__aexit__ = AsyncMock(return_value=None)
        mock_converter_class.return_value = mock_converter

        # Mock today's date (different from filter date)
        mock_date_module.today.return_value.strftime.return_value = "2025-07-16"

        session_command(
            False, "2025-07-15", "2025-07-15", SortOrder.DESC, False, False, False, None
        )

        # Should format with day labels
        mock_formatter.format_session_table.assert_called_once()


def test_session_command_empty_session_data_no_totals(runner=CliRunner()):
    """Test session command with empty session data."""
    with (
        patch("ccusage.commands.session.get_claude_paths") as mock_get_paths,
        patch("ccusage.commands.session.validate_claude_paths") as mock_validate,
        patch("ccusage.commands.session.DataLoader") as mock_loader_class,
        patch("ccusage.commands.session.DataProcessor") as mock_processor_class,
        patch(
            "ccusage.commands.session.ResponsiveTableFormatter"
        ) as mock_formatter_class,
        patch("ccusage.commands.session.console") as mock_console,
        patch("ccusage.commands.session.CurrencyConverter") as mock_converter_class,
    ):
        mock_get_paths.return_value = [Path("/path/to/claude")]
        mock_validate.return_value = None

        mock_loader = Mock()
        mock_loader.load_raw_entries = AsyncMock(return_value=Ok([Mock()]))
        mock_loader_class.return_value = mock_loader

        mock_processor = Mock()
        mock_processor.process_session_usage = AsyncMock(
            return_value=Ok([])
        )  # Empty session data
        mock_processor_class.return_value = mock_processor

        mock_formatter = Mock()
        mock_formatter.format_session_table = Mock(return_value="table_output")
        mock_formatter.format_summary_panel = Mock(return_value="summary_output")
        mock_formatter_class.return_value = mock_formatter

        # Mock currency converter
        mock_converter = Mock()
        mock_converter.get_currency_code = Mock(return_value="USD")
        mock_converter.get_currency_symbol = Mock(return_value="$")
        mock_converter.convert_amount = AsyncMock(return_value=Ok(0.15))
        mock_converter.__aenter__ = AsyncMock(return_value=mock_converter)
        mock_converter.__aexit__ = AsyncMock(return_value=None)
        mock_converter_class.return_value = mock_converter

        session_command(False, None, None, SortOrder.DESC, False, False, False, None)

        # Should format table but not call calculate_totals
        mock_formatter.format_session_table.assert_called_once()
        mock_processor.calculate_totals.assert_not_called()


class TestCommandsInit:
    """Test commands __init__.py module."""

    def test_commands_init_imports(self):
        """Test that commands __init__.py can be imported."""
        import ccusage.commands

        # Verify __all__ is defined
        assert hasattr(ccusage.commands, "__all__")
        assert ccusage.commands.__all__ == []
