"""Tests for data processor functionality."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ccusage.data.processor import DataProcessor
from ccusage.models.usage import RawUsageEntry
from ccusage.models.base import CostMode, SortOrder


@pytest.fixture
def sample_entries():
    """Create sample usage entries for testing."""
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
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 14, 0, 0),
            session_id="session-1",
            request_id="req-2",
            message_id="msg-2",
            model_name="claude-sonnet-4-20250514",
            input_tokens=200,
            output_tokens=100,
            cache_creation_tokens=0,
            cache_read_tokens=50,
            cost_usd=0.02,
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 16, 10, 0, 0),
            session_id="session-2",
            request_id="req-3",
            message_id="msg-3",
            model_name="claude-opus-4-20250514",
            input_tokens=150,
            output_tokens=75,
            cache_creation_tokens=10,
            cache_read_tokens=20,
            cost_usd=0.03,
            project_path="/project2",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 6, 15, 10, 0, 0),  # Different month
            session_id="session-3",
            request_id=None,  # Test optional field
            message_id="msg-4",
            model_name="claude-sonnet-4-20250514",
            input_tokens=300,
            output_tokens=150,
            cache_creation_tokens=0,
            cache_read_tokens=0,
            cost_usd=0.04,
            project_path="/project3",
            version="1.0.43",
        ),
    ]


@pytest.fixture
def processor():
    """Create a DataProcessor instance."""
    yield DataProcessor(cost_mode=CostMode.DISPLAY, offline=False)


@pytest.fixture
def processor_offline():
    """Create a DataProcessor instance with offline mode."""
    yield DataProcessor(cost_mode=CostMode.DISPLAY, offline=True)


@pytest.mark.asyncio
async def test_process_daily_usage(processor, sample_entries):
    """Test processing daily usage data."""
    result = await processor.process_daily_usage(
        sample_entries,
        since=None,
        until=None,
        order=SortOrder.DESC
    )
    
    assert result.is_ok()
    daily_usage = result.value
    
    # Should have 3 days (2 in July, 1 in June)
    assert len(daily_usage) == 3
    
    # Check July 15 (2 entries)
    july_15 = next(d for d in daily_usage if d.date == "2025-07-15")
    assert july_15.input_tokens == 300  # 100 + 200
    assert july_15.output_tokens == 150  # 50 + 100
    assert july_15.cache_creation_tokens == 25  # 25 + 0
    assert july_15.cache_read_tokens == 60  # 10 + 50
    assert july_15.total_tokens == 535
    assert july_15.total_cost == 0.03  # 0.01 + 0.02
    assert "claude-sonnet-4-20250514" in july_15.models_used
    
    # Check July 16 (1 entry)
    july_16 = next(d for d in daily_usage if d.date == "2025-07-16")
    assert july_16.input_tokens == 150
    assert july_16.output_tokens == 75
    assert july_16.total_tokens == 255
    assert july_16.total_cost == 0.03
    assert "claude-opus-4-20250514" in july_16.models_used


@pytest.mark.asyncio
async def test_process_daily_usage_with_date_filters(processor, sample_entries):
    """Test processing daily usage with date filters."""
    result = await processor.process_daily_usage(
        sample_entries,
        since="2025-07-15",
        until="2025-07-15",
        order=SortOrder.ASC
    )
    
    assert result.is_ok()
    daily_usage = result.value
    
    # Should only have July 15
    assert len(daily_usage) == 1
    assert daily_usage[0].date == "2025-07-15"


@pytest.mark.asyncio
async def test_process_monthly_usage(processor, sample_entries):
    """Test processing monthly usage data."""
    result = await processor.process_monthly_usage(
        sample_entries,
        since=None,
        until=None,
        order=SortOrder.DESC
    )
    
    assert result.is_ok()
    monthly_usage = result.value
    
    # Should have 2 months
    assert len(monthly_usage) == 2
    
    # Check July 2025
    july_2025 = next(m for m in monthly_usage if m.month == "2025-07")
    assert july_2025.input_tokens == 450  # 100 + 200 + 150
    assert july_2025.output_tokens == 225  # 50 + 100 + 75
    assert july_2025.total_tokens == 790
    assert july_2025.total_cost == 0.06  # 0.01 + 0.02 + 0.03
    assert len(july_2025.models_used) == 2  # sonnet-4 and opus-4


@pytest.mark.asyncio
async def test_process_session_usage(processor, sample_entries):
    """Test processing session usage data."""
    result = await processor.process_session_usage(
        sample_entries,
        order=SortOrder.DESC
    )
    
    assert result.is_ok()
    session_usage = result.value
    
    # Should have 3 sessions
    assert len(session_usage) == 3
    
    # Check session-1 (2 entries)
    session_1 = next(s for s in session_usage if s.session_id == "session-1")
    assert session_1.input_tokens == 300  # 100 + 200
    assert session_1.output_tokens == 150  # 50 + 100
    assert session_1.total_tokens == 535
    assert session_1.total_cost == 0.03  # 0.01 + 0.02
    assert session_1.project_path == "/project1"
    assert "claude-sonnet-4-20250514" in session_1.models_used
    assert "1.0.43" in session_1.versions


@pytest.mark.asyncio
async def test_calculate_total_cost_display_mode(sample_entries):
    """Test cost calculation in display mode."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    cost = await processor._calculate_total_cost(sample_entries)
    
    # Should sum up the cost_usd values
    assert cost == 0.10  # 0.01 + 0.02 + 0.03 + 0.04


@pytest.mark.asyncio
async def test_calculate_total_cost_calculate_mode(sample_entries):
    """Test cost calculation in calculate mode."""
    processor = DataProcessor(cost_mode=CostMode.CALCULATE, offline=True)
    
    cost = await processor._calculate_total_cost(sample_entries)
    
    # Should return calculated cost (not 0.0 since we actually have pricing data now)
    # The exact cost depends on the pricing data and tokens, so we just verify it's positive
    assert cost > 0.0


@pytest.mark.asyncio
async def test_aggregate_daily_usage(processor, sample_entries):
    """Test aggregating entries for a single day."""
    # Filter entries for July 15
    july_15_entries = [e for e in sample_entries if e.timestamp.date().isoformat() == "2025-07-15"]
    
    daily_usage = await processor._aggregate_daily_entries("2025-07-15", july_15_entries)
    
    assert daily_usage.date == "2025-07-15"
    assert daily_usage.input_tokens == 300
    assert daily_usage.output_tokens == 150
    assert daily_usage.cache_creation_tokens == 25
    assert daily_usage.cache_read_tokens == 60
    assert daily_usage.total_tokens == 535
    assert daily_usage.total_cost == 0.03
    assert "claude-sonnet-4-20250514" in daily_usage.models_used


@pytest.mark.asyncio
async def test_aggregate_monthly_usage(processor, sample_entries):
    """Test aggregating entries for a single month."""
    # Filter entries for July 2025
    july_entries = [e for e in sample_entries if e.timestamp.strftime("%Y-%m") == "2025-07"]
    
    monthly_usage = await processor._aggregate_monthly_entries("2025-07", july_entries)
    
    assert monthly_usage.month == "2025-07"
    assert monthly_usage.input_tokens == 450
    assert monthly_usage.output_tokens == 225
    assert monthly_usage.total_tokens == 790
    assert monthly_usage.total_cost == 0.06
    assert len(monthly_usage.models_used) == 2


@pytest.mark.asyncio
async def test_aggregate_session_usage(processor, sample_entries):
    """Test aggregating entries for a single session."""
    # Filter entries for session-1
    session_1_entries = [e for e in sample_entries if e.session_id == "session-1"]
    
    session_usage = await processor._aggregate_session_entries("session-1", session_1_entries)
    
    assert session_usage.session_id == "session-1"
    assert session_usage.input_tokens == 300
    assert session_usage.output_tokens == 150
    assert session_usage.total_tokens == 535
    assert session_usage.total_cost == 0.03
    assert session_usage.project_path == "/project1"
    assert "claude-sonnet-4-20250514" in session_usage.models_used
    assert "1.0.43" in session_usage.versions


@pytest.mark.asyncio
async def test_process_empty_entries(processor):
    """Test processing empty entries list."""
    result = await processor.process_daily_usage(
        [],
        since=None,
        until=None,
        order=SortOrder.DESC
    )
    
    assert result.is_ok()
    assert len(result.value) == 0


@pytest.mark.asyncio
async def test_date_filtering():
    """Test date filtering logic."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    # Test _is_in_date_range method
    assert processor._is_in_date_range("2025-07-15", None, None) is True
    assert processor._is_in_date_range("2025-07-15", "2025-07-01", None) is True
    assert processor._is_in_date_range("2025-07-15", "2025-07-01", "2025-07-31") is True
    assert processor._is_in_date_range("2025-07-15", "2025-07-16", None) is False
    assert processor._is_in_date_range("2025-07-15", None, "2025-07-14") is False


def test_processor_initialization():
    """Test DataProcessor initialization."""
    processor = DataProcessor(cost_mode=CostMode.AUTO)
    
    assert processor.cost_mode == CostMode.AUTO
    assert processor.offline is False


def test_processor_initialization_with_offline():
    """Test DataProcessor initialization with offline flag."""
    processor = DataProcessor(cost_mode=CostMode.AUTO, offline=True)
    
    assert processor.cost_mode == CostMode.AUTO
    assert processor.offline is True


@pytest.mark.asyncio
async def test_process_daily_usage_exception():
    """Test daily usage processing with exception."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    # Create entries that will cause an error during processing
    # We'll patch the aggregation method to raise an exception
    original_aggregate = processor._aggregate_daily_entries
    
    async def mock_aggregate_daily_entries(date_str, entries):
        raise ValueError("Test exception in daily aggregation")
    
    processor._aggregate_daily_entries = mock_aggregate_daily_entries
    
    entries = [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            message_id="msg-1",
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            project_path="/project1",
            version="1.0.43",
        )
    ]
    
    result = await processor.process_daily_usage(entries)
    
    assert result.is_err()
    assert "Test exception in daily aggregation" in str(result.error)


@pytest.mark.asyncio
async def test_process_monthly_usage_exception():
    """Test monthly usage processing with exception."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    # Patch the aggregation method to raise an exception
    original_aggregate = processor._aggregate_monthly_entries
    
    async def mock_aggregate_monthly_entries(month_str, entries):
        raise ValueError("Test exception in monthly aggregation")
    
    processor._aggregate_monthly_entries = mock_aggregate_monthly_entries
    
    entries = [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            message_id="msg-1",
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            project_path="/project1",
            version="1.0.43",
        )
    ]
    
    result = await processor.process_monthly_usage(entries)
    
    assert result.is_err()
    assert "Test exception in monthly aggregation" in str(result.error)


@pytest.mark.asyncio
async def test_process_session_usage_exception():
    """Test session usage processing with exception."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    # Patch the aggregation method to raise an exception
    original_aggregate = processor._aggregate_session_entries
    
    async def mock_aggregate_session_entries(session_id, entries):
        raise ValueError("Test exception in session aggregation")
    
    processor._aggregate_session_entries = mock_aggregate_session_entries
    
    entries = [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            message_id="msg-1",
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            project_path="/project1",
            version="1.0.43",
        )
    ]
    
    result = await processor.process_session_usage(entries)
    
    assert result.is_err()
    assert "Test exception in session aggregation" in str(result.error)


@pytest.mark.asyncio
async def test_calculate_totals_success(sample_entries):
    """Test totals calculation success."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    result = await processor.calculate_totals(sample_entries)
    
    assert result.is_ok()
    totals = result.value
    assert totals.input_tokens == 750  # 100 + 200 + 150 + 300
    assert totals.output_tokens == 375  # 50 + 100 + 75 + 150
    assert totals.cache_creation_tokens == 35  # 25 + 0 + 10 + 0
    assert totals.cache_read_tokens == 80  # 10 + 50 + 20 + 0
    assert totals.total_cost == 0.10  # 0.01 + 0.02 + 0.03 + 0.04


@pytest.mark.asyncio
async def test_calculate_totals_exception():
    """Test totals calculation with exception."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    # Patch the cost calculation method to raise an exception
    original_calculate_cost = processor._calculate_total_cost
    
    async def mock_calculate_total_cost(entries):
        raise ValueError("Test exception in cost calculation")
    
    processor._calculate_total_cost = mock_calculate_total_cost
    
    entries = [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            message_id="msg-1",
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            project_path="/project1",
            version="1.0.43",
        )
    ]
    
    result = await processor.calculate_totals(entries)
    
    assert result.is_err()
    assert "Test exception in cost calculation" in str(result.error)


@pytest.mark.asyncio
async def test_calculate_total_cost_auto_mode(sample_entries):
    """Test cost calculation in auto mode."""
    processor = DataProcessor(cost_mode=CostMode.AUTO)
    
    cost = await processor._calculate_total_cost(sample_entries)
    
    # Should sum up the cost_usd values (same as display mode)
    assert cost == 0.10  # 0.01 + 0.02 + 0.03 + 0.04


@pytest.mark.asyncio
async def test_calculate_total_cost_auto_mode_with_none_values():
    """Test cost calculation in auto mode with None cost values."""
    processor = DataProcessor(cost_mode=CostMode.AUTO)
    
    # Create entries with some None cost_usd values
    entries = [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            message_id="msg-1",
            model_name="claude-sonnet-4-20250514",
            input_tokens=100,
            output_tokens=50,
            cost_usd=None,  # None value
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 14, 0, 0),
            session_id="session-2",
            message_id="msg-2",
            model_name="claude-sonnet-4-20250514",
            input_tokens=200,
            output_tokens=100,
            cost_usd=0.02,  # Has value
            project_path="/project2",
            version="1.0.43",
        ),
    ]
    
    cost = await processor._calculate_total_cost(entries)
    
    # Should handle None values correctly - the entry with None cost_usd gets calculated
    # The result should be the pre-calculated 0.02 plus the calculated cost for the None entry
    assert cost > 0.02  # Should be greater than just the pre-calculated cost


@pytest.mark.asyncio
async def test_calculate_total_cost_auto_mode_empty_entries():
    """Test cost calculation in auto mode with empty entries list."""
    processor = DataProcessor(cost_mode=CostMode.AUTO)
    
    cost = await processor._calculate_total_cost([])
    
    # Should return 0.0 for empty list
    assert cost == 0.0


def test_date_range_compact_format():
    """Test date range filtering with compact format dates."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    # Test with compact format (YYYYMMDD)
    assert processor._is_in_date_range("2025-07-15", "20250701", "20250731") is True
    assert processor._is_in_date_range("2025-07-15", "20250716", None) is False
    assert processor._is_in_date_range("2025-07-15", None, "20250714") is False
    
    # Test with mixed formats
    assert processor._is_in_date_range("2025-07-15", "2025-07-01", "20250731") is True


def test_month_range_filtering():
    """Test month range filtering logic."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    # Test _is_in_month_range method
    assert processor._is_in_month_range("2025-07", "20250601", "20250801") is True
    assert processor._is_in_month_range("2025-07", "20250801", None) is False
    assert processor._is_in_month_range("2025-07", None, "20250601") is False
    
    # Test edge cases
    assert processor._is_in_month_range("2025-07", "20250701", "20250731") is True
    assert processor._is_in_month_range("2025-06", "20250701", "20250731") is False


@pytest.mark.asyncio
async def test_process_monthly_usage_with_month_filters(sample_entries):
    """Test monthly processing with month date filters."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    result = await processor.process_monthly_usage(
        sample_entries,
        since="20250701",  # Compact format  
        until="20250731",  # Compact format
        order=SortOrder.ASC
    )
    
    assert result.is_ok()
    monthly_usage = result.value
    
    # Should only have July 2025 (exclude June entry)
    assert len(monthly_usage) == 1
    assert monthly_usage[0].month == "2025-07"


@pytest.mark.asyncio 
async def test_process_monthly_usage_no_entries_in_range(sample_entries):
    """Test monthly processing with no entries in date range."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY)
    
    result = await processor.process_monthly_usage(
        sample_entries,
        since="20250801",  # After all entries
        until="20250831",  # After all entries
        order=SortOrder.DESC
    )
    
    assert result.is_ok()
    monthly_usage = result.value
    
    # Should have no entries
    assert len(monthly_usage) == 0


@pytest.fixture
def entries_with_mixed_costs():
    """Create sample entries with mixed cost_usd values (some None, some not)."""
    return [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            request_id="req-1",
            message_id="msg-1",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            cost_usd=None,  # No pre-calculated cost
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 14, 0, 0),
            session_id="session-1",
            request_id="req-2",
            message_id="msg-2",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=200,
            output_tokens=100,
            cache_creation_tokens=0,
            cache_read_tokens=50,
            cost_usd=0.02,  # Has pre-calculated cost
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 16, 10, 0, 0),
            session_id="session-2",
            request_id="req-3",
            message_id="msg-3",
            model_name="claude-3-opus-20240229",
            input_tokens=150,
            output_tokens=75,
            cache_creation_tokens=10,
            cache_read_tokens=20,
            cost_usd=None,  # No pre-calculated cost
            project_path="/project2",
            version="1.0.43",
        ),
    ]


@pytest.mark.asyncio
async def test_calculate_total_cost_calculate_mode_with_real_pricing():
    """Test cost calculation in calculate mode with mock pricing data."""
    from unittest.mock import AsyncMock, MagicMock
    from ccusage.pricing.calculator import CostCalculator
    from ccusage.pricing.fetcher import PricingFetcher
    
    processor = DataProcessor(cost_mode=CostMode.CALCULATE, offline=True)
    
    # Mock the pricing fetcher and calculator
    with pytest.importorskip("unittest.mock").patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        with pytest.importorskip("unittest.mock").patch("ccusage.pricing.calculator.CostCalculator") as mock_calculator_class:
            # Set up mocks
            mock_fetcher = MagicMock()
            mock_calculator = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_calculator_class.return_value = mock_calculator
            
            # Mock the calculate_total_cost method to return a successful result
            from ccusage.core.result import ok
            mock_calculator.calculate_total_cost = AsyncMock(return_value=ok(0.05))
            
            entries = [
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 10, 0, 0),
                    session_id="session-1",
                    message_id="msg-1",
                    model_name="claude-3-5-sonnet-20241022",
                    input_tokens=100,
                    output_tokens=50,
                    cost_usd=0.01,  # This should be ignored in CALCULATE mode
                    project_path="/project1",
                    version="1.0.43",
                ),
            ]
            
            cost = await processor._calculate_total_cost(entries)
            
            # Should use calculated cost, not pre-calculated
            assert cost == 0.05
            mock_fetcher_class.assert_called_once_with(offline=True)
            mock_calculator_class.assert_called_once_with(mock_fetcher)
            mock_calculator.calculate_total_cost.assert_called_once_with(entries, "\nCalculating costs for 1 model(s): claude-3-5-sonnet-20241022")


@pytest.mark.asyncio
async def test_calculate_total_cost_calculate_mode_with_error():
    """Test cost calculation in calculate mode when pricing calculation fails."""
    from unittest.mock import AsyncMock, MagicMock
    
    processor = DataProcessor(cost_mode=CostMode.CALCULATE, offline=True)
    
    # Mock the pricing fetcher and calculator
    with pytest.importorskip("unittest.mock").patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        with pytest.importorskip("unittest.mock").patch("ccusage.pricing.calculator.CostCalculator") as mock_calculator_class:
            # Set up mocks
            mock_fetcher = MagicMock()
            mock_calculator = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_calculator_class.return_value = mock_calculator
            
            # Mock the calculate_total_cost method to return an error
            from ccusage.core.result import err
            mock_calculator.calculate_total_cost = AsyncMock(return_value=err(Exception("Pricing error")))
            
            entries = [
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 10, 0, 0),
                    session_id="session-1",
                    message_id="msg-1",
                    model_name="claude-3-5-sonnet-20241022",
                    input_tokens=100,
                    output_tokens=50,
                    project_path="/project1",
                    version="1.0.43",
                ),
            ]
            
            cost = await processor._calculate_total_cost(entries)
            
            # Should return 0.0 when calculation fails
            assert cost == 0.0


@pytest.mark.asyncio
async def test_calculate_total_cost_auto_mode_with_mixed_costs():
    """Test cost calculation in auto mode with mixed cost_usd values."""
    from unittest.mock import AsyncMock, MagicMock
    
    processor = DataProcessor(cost_mode=CostMode.AUTO, offline=True)
    
    # Mock the pricing fetcher and calculator
    with pytest.importorskip("unittest.mock").patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        with pytest.importorskip("unittest.mock").patch("ccusage.pricing.calculator.CostCalculator") as mock_calculator_class:
            # Set up mocks
            mock_fetcher = MagicMock()
            mock_calculator = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_calculator_class.return_value = mock_calculator
            
            # Mock the calculate_total_cost method to return a successful result
            from ccusage.core.result import ok
            mock_calculator.calculate_total_cost = AsyncMock(return_value=ok(0.03))
            
            entries = [
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 10, 0, 0),
                    session_id="session-1",
                    message_id="msg-1",
                    model_name="claude-3-5-sonnet-20241022",
                    input_tokens=100,
                    output_tokens=50,
                    cost_usd=0.01,  # Has pre-calculated cost
                    project_path="/project1",
                    version="1.0.43",
                ),
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 14, 0, 0),
                    session_id="session-1",
                    message_id="msg-2",
                    model_name="claude-3-5-sonnet-20241022",
                    input_tokens=200,
                    output_tokens=100,
                    cost_usd=None,  # No pre-calculated cost
                    project_path="/project1",
                    version="1.0.43",
                ),
            ]
            
            cost = await processor._calculate_total_cost(entries)
            
            # Should use pre-calculated cost (0.01) plus calculated cost (0.03)
            assert cost == 0.04
            
            # Should only call calculator for entry without cost_usd
            mock_calculator.calculate_total_cost.assert_called_once()
            called_entries = mock_calculator.calculate_total_cost.call_args[0][0]
            assert len(called_entries) == 1
            assert called_entries[0].cost_usd is None


@pytest.mark.asyncio
async def test_calculate_total_cost_auto_mode_calculation_error():
    """Test cost calculation in auto mode when calculation fails for some entries."""
    from unittest.mock import AsyncMock, MagicMock
    
    processor = DataProcessor(cost_mode=CostMode.AUTO, offline=True)
    
    # Mock the pricing fetcher and calculator
    with pytest.importorskip("unittest.mock").patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        with pytest.importorskip("unittest.mock").patch("ccusage.pricing.calculator.CostCalculator") as mock_calculator_class:
            # Set up mocks
            mock_fetcher = MagicMock()
            mock_calculator = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_calculator_class.return_value = mock_calculator
            
            # Mock the calculate_total_cost method to return an error
            from ccusage.core.result import err
            mock_calculator.calculate_total_cost = AsyncMock(return_value=err(Exception("Pricing error")))
            
            entries = [
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 10, 0, 0),
                    session_id="session-1",
                    message_id="msg-1",
                    model_name="claude-3-5-sonnet-20241022",
                    input_tokens=100,
                    output_tokens=50,
                    cost_usd=0.01,  # Has pre-calculated cost
                    project_path="/project1",
                    version="1.0.43",
                ),
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 14, 0, 0),
                    session_id="session-1",
                    message_id="msg-2",
                    model_name="claude-3-5-sonnet-20241022",
                    input_tokens=200,
                    output_tokens=100,
                    cost_usd=None,  # No pre-calculated cost
                    project_path="/project1",
                    version="1.0.43",
                ),
            ]
            
            cost = await processor._calculate_total_cost(entries)
            
            # Should only use pre-calculated cost when calculation fails
            assert cost == 0.01


@pytest.mark.asyncio
async def test_calculate_total_cost_auto_mode_all_precalculated():
    """Test cost calculation in auto mode when all entries have pre-calculated costs."""
    processor = DataProcessor(cost_mode=CostMode.AUTO, offline=True)
    
    entries = [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            message_id="msg-1",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 14, 0, 0),
            session_id="session-1",
            message_id="msg-2",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=200,
            output_tokens=100,
            cost_usd=0.02,
            project_path="/project1",
            version="1.0.43",
        ),
    ]
    
    cost = await processor._calculate_total_cost(entries)
    
    # Should just sum pre-calculated costs without calling calculator
    assert cost == 0.03


@pytest.mark.asyncio
async def test_process_session_usage_with_date_filtering():
    """Test session processing with date filtering."""
    processor = DataProcessor(cost_mode=CostMode.DISPLAY, offline=True)
    
    entries = [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 14, 10, 0, 0),  # Before range
            session_id="session-1",
            message_id="msg-1",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),  # In range
            session_id="session-1",
            message_id="msg-2",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=200,
            output_tokens=100,
            cost_usd=0.02,
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 16, 10, 0, 0),  # After range
            session_id="session-1",
            message_id="msg-3",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=300,
            output_tokens=150,
            cost_usd=0.03,
            project_path="/project1",
            version="1.0.43",
        ),
    ]
    
    result = await processor.process_session_usage(entries, since="2025-07-15", until="2025-07-15")
    
    assert result.is_ok()
    session_data = result.value
    
    # Should only include the entry from 2025-07-15
    assert len(session_data) == 1
    assert session_data[0].input_tokens == 200
    assert session_data[0].output_tokens == 100
    assert session_data[0].total_cost == 0.02


def test_date_format_conversion_edge_cases():
    """Test date format conversion with edge cases."""
    processor = DataProcessor()
    
    # Test valid YYYYMMDD format
    assert processor._is_in_date_range("2025-01-15", "20250101", "20250131")
    
    # Test valid YYYY-MM-DD format
    assert processor._is_in_date_range("2025-01-15", "2025-01-01", "2025-01-31")
    
    # Test boundary conditions
    assert processor._is_in_date_range("2025-01-01", "20250101", "20250131")
    assert processor._is_in_date_range("2025-01-31", "20250101", "20250131")
    
    # Test dates outside range
    assert not processor._is_in_date_range("2024-12-31", "20250101", "20250131")
    assert not processor._is_in_date_range("2025-02-01", "20250101", "20250131")


def test_month_format_conversion_edge_cases():
    """Test month format conversion with edge cases."""
    processor = DataProcessor()
    
    # Test valid month range
    assert processor._is_in_month_range("2025-01", "20250101", "20250228")
    assert processor._is_in_month_range("2025-02", "20250101", "20250228")
    
    # Test boundary conditions
    assert processor._is_in_month_range("2025-01", "20250101", "20250131")
    assert not processor._is_in_month_range("2024-12", "20250101", "20250131")
    assert not processor._is_in_month_range("2025-02", "20250101", "20250131")


@pytest.mark.asyncio
async def test_session_aggregation_with_empty_entries():
    """Test session aggregation with empty entries list."""
    processor = DataProcessor()
    
    entries = []
    
    result = await processor.process_session_usage(entries)
    
    assert result.is_ok()
    session_data = result.value
    assert len(session_data) == 0


@pytest.mark.asyncio
async def test_session_aggregation_with_different_project_paths():
    """Test session aggregation with entries having different project paths."""
    processor = DataProcessor()
    
    entries = [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            message_id="msg-1",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=100,
            output_tokens=50,
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 11, 0, 0),
            session_id="session-1",
            message_id="msg-2",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=200,
            output_tokens=100,
            project_path="/project2",  # Different project path
            version="1.0.43",
        ),
    ]
    
    result = await processor.process_session_usage(entries)
    
    assert result.is_ok()
    session_data = result.value
    assert len(session_data) == 1
    # Should use the first entry's project path
    assert session_data[0].project_path == "/project1"


@pytest.mark.asyncio
async def test_session_aggregation_with_multiple_versions():
    """Test session aggregation with multiple versions."""
    processor = DataProcessor()
    
    entries = [
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 10, 0, 0),
            session_id="session-1",
            message_id="msg-1",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=100,
            output_tokens=50,
            project_path="/project1",
            version="1.0.43",
        ),
        RawUsageEntry(
            timestamp=datetime(2025, 7, 15, 11, 0, 0),
            session_id="session-1",
            message_id="msg-2",
            model_name="claude-3-5-sonnet-20241022",
            input_tokens=200,
            output_tokens=100,
            project_path="/project1",
            version="1.0.44",  # Different version
        ),
    ]
    
    result = await processor.process_session_usage(entries)
    
    assert result.is_ok()
    session_data = result.value
    assert len(session_data) == 1
    # Should include both versions
    assert sorted(session_data[0].versions) == ["1.0.43", "1.0.44"]


@pytest.mark.asyncio
async def test_cost_calculation_context_generation():
    """Test context generation for cost calculation."""
    from unittest.mock import AsyncMock, MagicMock
    
    processor = DataProcessor(cost_mode=CostMode.CALCULATE, offline=True)
    
    # Mock the pricing fetcher and calculator
    with pytest.importorskip("unittest.mock").patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        with pytest.importorskip("unittest.mock").patch("ccusage.pricing.calculator.CostCalculator") as mock_calculator_class:
            # Set up mocks
            mock_fetcher = MagicMock()
            mock_calculator = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_calculator_class.return_value = mock_calculator
            
            # Mock the calculate_total_cost method
            from ccusage.core.result import ok
            mock_calculator.calculate_total_cost = AsyncMock(return_value=ok(0.05))
            
            # Test with exactly 3 models
            entries = [
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 10, 0, 0),
                    session_id="session-1",
                    message_id="msg-1",
                    model_name="claude-3-5-sonnet-20241022",
                    input_tokens=100,
                    output_tokens=50,
                    project_path="/project1",
                    version="1.0.43",
                ),
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 11, 0, 0),
                    session_id="session-1",
                    message_id="msg-2",
                    model_name="claude-3-opus-20240229",
                    input_tokens=200,
                    output_tokens=100,
                    project_path="/project1",
                    version="1.0.43",
                ),
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 12, 0, 0),
                    session_id="session-1",
                    message_id="msg-3",
                    model_name="claude-3-haiku-20240307",
                    input_tokens=300,
                    output_tokens=150,
                    project_path="/project1",
                    version="1.0.43",
                ),
            ]
            
            cost = await processor._calculate_total_cost(entries)
            
            # Check that calculate_total_cost was called with proper context
            mock_calculator.calculate_total_cost.assert_called_once()
            call_args = mock_calculator.calculate_total_cost.call_args
            context = call_args[0][1]  # Second positional argument
            
            assert "Calculating costs for 3 model(s):" in context
            assert "claude-3-5-sonnet-20241022" in context
            assert "claude-3-opus-20240229" in context
            assert "claude-3-haiku-20240307" in context


@pytest.mark.asyncio
async def test_cost_calculation_context_generation_many_models():
    """Test context generation for cost calculation with many models."""
    from unittest.mock import AsyncMock, MagicMock
    
    processor = DataProcessor(cost_mode=CostMode.CALCULATE, offline=True)
    
    # Mock the pricing fetcher and calculator
    with pytest.importorskip("unittest.mock").patch("ccusage.pricing.fetcher.PricingFetcher") as mock_fetcher_class:
        with pytest.importorskip("unittest.mock").patch("ccusage.pricing.calculator.CostCalculator") as mock_calculator_class:
            # Set up mocks
            mock_fetcher = MagicMock()
            mock_calculator = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_calculator_class.return_value = mock_calculator
            
            # Mock the calculate_total_cost method
            from ccusage.core.result import ok
            mock_calculator.calculate_total_cost = AsyncMock(return_value=ok(0.05))
            
            # Test with more than 3 models
            entries = [
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 10, 0, 0),
                    session_id="session-1",
                    message_id="msg-1",
                    model_name="claude-3-5-sonnet-20241022",
                    input_tokens=100,
                    output_tokens=50,
                    project_path="/project1",
                    version="1.0.43",
                ),
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 11, 0, 0),
                    session_id="session-1",
                    message_id="msg-2",
                    model_name="claude-3-opus-20240229",
                    input_tokens=200,
                    output_tokens=100,
                    project_path="/project1",
                    version="1.0.43",
                ),
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 12, 0, 0),
                    session_id="session-1",
                    message_id="msg-3",
                    model_name="claude-3-haiku-20240307",
                    input_tokens=300,
                    output_tokens=150,
                    project_path="/project1",
                    version="1.0.43",
                ),
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 13, 0, 0),
                    session_id="session-1",
                    message_id="msg-4",
                    model_name="claude-instant-1.2",
                    input_tokens=400,
                    output_tokens=200,
                    project_path="/project1",
                    version="1.0.43",
                ),
                RawUsageEntry(
                    timestamp=datetime(2025, 7, 15, 14, 0, 0),
                    session_id="session-1",
                    message_id="msg-5",
                    model_name="claude-2.1",
                    input_tokens=500,
                    output_tokens=250,
                    project_path="/project1",
                    version="1.0.43",
                ),
            ]
            
            cost = await processor._calculate_total_cost(entries)
            
            # Check that calculate_total_cost was called with proper context
            mock_calculator.calculate_total_cost.assert_called_once()
            call_args = mock_calculator.calculate_total_cost.call_args
            context = call_args[0][1]  # Second positional argument
            
            assert "Calculating costs for 5 model(s):" in context
            assert "and 2 more" in context


if __name__ == "__main__":
    pytest.main([__file__])