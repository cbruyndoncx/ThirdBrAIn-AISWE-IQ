"""Comprehensive tests for model validation and functionality."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ccusage.models.base import (
    DateString,
    MonthString,
    FilterDateString,
    TimestampString,
    VersionString,
    create_model_name,
    create_session_id,
    create_request_id,
    create_message_id,
    create_daily_date,
    create_monthly_date,
    create_filter_date,
    create_project_path,
    create_iso_timestamp,
    create_version,
    format_model_name,
    format_number,
    format_currency,
)
from ccusage.models.usage import UsageTotals


class TestDateString:
    """Test DateString validation."""
    
    def test_valid_date_string(self):
        """Test valid date string format."""
        date_str = DateString(value="2025-07-15")
        assert date_str.value == "2025-07-15"
    
    def test_invalid_date_string_format(self):
        """Test invalid date string format."""
        with pytest.raises(ValidationError, match="Date must be in YYYY-MM-DD format"):
            DateString(value="2025-7-15")  # Single digit month
        
        with pytest.raises(ValidationError, match="Date must be in YYYY-MM-DD format"):
            DateString(value="25-07-15")  # Two digit year
            
        with pytest.raises(ValidationError, match="Date must be in YYYY-MM-DD format"):
            DateString(value="2025/07/15")  # Wrong separator


class TestMonthString:
    """Test MonthString validation."""
    
    def test_valid_month_string(self):
        """Test valid month string format."""
        month_str = MonthString(value="2025-07")
        assert month_str.value == "2025-07"
    
    def test_invalid_month_string_format(self):
        """Test invalid month string format."""
        with pytest.raises(ValidationError, match="Month must be in YYYY-MM format"):
            MonthString(value="2025-7")  # Single digit month
        
        with pytest.raises(ValidationError, match="Month must be in YYYY-MM format"):
            MonthString(value="25-07")  # Two digit year
            
        with pytest.raises(ValidationError, match="Month must be in YYYY-MM format"):
            MonthString(value="2025/07")  # Wrong separator


class TestFilterDateString:
    """Test FilterDateString validation."""
    
    def test_valid_filter_date_string(self):
        """Test valid filter date string format."""
        filter_date = FilterDateString(value="20250715")
        assert filter_date.value == "20250715"
    
    def test_invalid_filter_date_string_format(self):
        """Test invalid filter date string format."""
        with pytest.raises(ValidationError, match="Filter date must be in YYYYMMDD format"):
            FilterDateString(value="2025071")  # Too short
        
        with pytest.raises(ValidationError, match="Filter date must be in YYYYMMDD format"):
            FilterDateString(value="202507155")  # Too long
            
        with pytest.raises(ValidationError, match="Filter date must be in YYYYMMDD format"):
            FilterDateString(value="2025-07-15")  # With separators


class TestTimestampString:
    """Test TimestampString validation."""
    
    def test_valid_timestamp_string(self):
        """Test valid timestamp string format."""
        timestamp = TimestampString(value="2025-07-15T10:30:45Z")
        assert timestamp.value == "2025-07-15T10:30:45Z"
        
        # With milliseconds
        timestamp_ms = TimestampString(value="2025-07-15T10:30:45.123Z")
        assert timestamp_ms.value == "2025-07-15T10:30:45.123Z"
    
    def test_invalid_timestamp_string_format(self):
        """Test invalid timestamp string format."""
        with pytest.raises(ValidationError, match="Invalid ISO timestamp format"):
            TimestampString(value="2025-07-15 10:30:45")  # Missing T and Z
        
        with pytest.raises(ValidationError, match="Invalid ISO timestamp format"):
            TimestampString(value="2025-07-15T10:30:45")  # Missing Z
            
        with pytest.raises(ValidationError, match="Invalid ISO timestamp format"):
            TimestampString(value="2025-7-15T10:30:45Z")  # Single digit month


class TestVersionString:
    """Test VersionString validation."""
    
    def test_valid_version_string(self):
        """Test valid version string format."""
        version = VersionString(value="1.0.0")
        assert version.value == "1.0.0"
        
        # With additional info
        version_beta = VersionString(value="1.0.0-beta.1")
        assert version_beta.value == "1.0.0-beta.1"
    
    def test_invalid_version_string_format(self):
        """Test invalid version string format."""
        with pytest.raises(ValidationError, match="Invalid version format"):
            VersionString(value="1.0")  # Missing patch version
        
        with pytest.raises(ValidationError, match="Invalid version format"):
            VersionString(value="v1.0.0")  # With v prefix
            
        with pytest.raises(ValidationError, match="Invalid version format"):
            VersionString(value="invalid")  # Not a version at all


class TestCreateFunctions:
    """Test create_* validation functions."""
    
    def test_create_model_name_valid(self):
        """Test valid model name creation."""
        model_name = create_model_name("claude-sonnet-4")
        assert model_name == "claude-sonnet-4"
    
    def test_create_model_name_invalid(self):
        """Test invalid model name creation."""
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            create_model_name("")
        
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            create_model_name("   ")  # Whitespace only
    
    def test_create_session_id_valid(self):
        """Test valid session ID creation."""
        session_id = create_session_id("session-123")
        assert session_id == "session-123"
    
    def test_create_session_id_invalid(self):
        """Test invalid session ID creation."""
        with pytest.raises(ValueError, match="Session ID cannot be empty"):
            create_session_id("")
        
        with pytest.raises(ValueError, match="Session ID cannot be empty"):
            create_session_id("   ")  # Whitespace only
    
    def test_create_request_id_valid(self):
        """Test valid request ID creation."""
        request_id = create_request_id("req-123")
        assert request_id == "req-123"
    
    def test_create_request_id_invalid(self):
        """Test invalid request ID creation."""
        with pytest.raises(ValueError, match="Request ID cannot be empty"):
            create_request_id("")
        
        with pytest.raises(ValueError, match="Request ID cannot be empty"):
            create_request_id("   ")  # Whitespace only
    
    def test_create_message_id_valid(self):
        """Test valid message ID creation."""
        message_id = create_message_id("msg-123")
        assert message_id == "msg-123"
    
    def test_create_message_id_invalid(self):
        """Test invalid message ID creation."""
        with pytest.raises(ValueError, match="Message ID cannot be empty"):
            create_message_id("")
        
        with pytest.raises(ValueError, match="Message ID cannot be empty"):
            create_message_id("   ")  # Whitespace only
    
    def test_create_daily_date_valid(self):
        """Test valid daily date creation."""
        daily_date = create_daily_date("2025-07-15")
        assert daily_date == "2025-07-15"
    
    def test_create_daily_date_invalid(self):
        """Test invalid daily date creation."""
        with pytest.raises(ValidationError, match="Date must be in YYYY-MM-DD format"):
            create_daily_date("2025-7-15")
    
    def test_create_monthly_date_valid(self):
        """Test valid monthly date creation."""
        monthly_date = create_monthly_date("2025-07")
        assert monthly_date == "2025-07"
    
    def test_create_monthly_date_invalid(self):
        """Test invalid monthly date creation."""
        with pytest.raises(ValidationError, match="Month must be in YYYY-MM format"):
            create_monthly_date("2025-7")
    
    def test_create_filter_date_valid(self):
        """Test valid filter date creation."""
        filter_date = create_filter_date("20250715")
        assert filter_date == "20250715"
    
    def test_create_filter_date_invalid(self):
        """Test invalid filter date creation."""
        with pytest.raises(ValidationError, match="Filter date must be in YYYYMMDD format"):
            create_filter_date("2025-07-15")
    
    def test_create_project_path_valid(self):
        """Test valid project path creation."""
        project_path = create_project_path("/path/to/project")
        assert project_path == "/path/to/project"
    
    def test_create_project_path_invalid(self):
        """Test invalid project path creation."""
        with pytest.raises(ValueError, match="Project path cannot be empty"):
            create_project_path("")
        
        with pytest.raises(ValueError, match="Project path cannot be empty"):
            create_project_path("   ")  # Whitespace only
    
    def test_create_iso_timestamp_valid(self):
        """Test valid ISO timestamp creation."""
        timestamp = create_iso_timestamp("2025-07-15T10:30:45Z")
        assert timestamp == "2025-07-15T10:30:45Z"
    
    def test_create_iso_timestamp_invalid(self):
        """Test invalid ISO timestamp creation."""
        with pytest.raises(ValidationError, match="Invalid ISO timestamp format"):
            create_iso_timestamp("2025-07-15 10:30:45")
    
    def test_create_version_valid(self):
        """Test valid version creation."""
        version = create_version("1.0.43")
        assert version == "1.0.43"
    
    def test_create_version_invalid(self):
        """Test invalid version creation."""
        with pytest.raises(ValidationError, match="Invalid version format"):
            create_version("1.0")


class TestFormatFunctions:
    """Test formatting functions."""
    
    def test_format_model_name_claude_models(self):
        """Test format_model_name with Claude models."""
        assert format_model_name("claude-sonnet-4-20250514") == "sonnet-4"
        assert format_model_name("claude-opus-4-20250514") == "opus-4"
        assert format_model_name("claude-haiku-3-20240307") == "haiku-3"
    
    def test_format_model_name_non_matching(self):
        """Test format_model_name with non-matching patterns."""
        assert format_model_name("custom-model") == "custom-model"
        assert format_model_name("gpt-4") == "gpt-4"
        assert format_model_name("") == ""
    
    def test_format_number(self):
        """Test number formatting with thousand separators."""
        assert format_number(1000) == "1,000"
        assert format_number(1234567) == "1,234,567"
        assert format_number(0) == "0"
        assert format_number(123) == "123"
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(1.23) == "$1.23"
        assert format_currency(0.0) == "$0.00"
        assert format_currency(1234.567) == "$1,234.57"
        assert format_currency(0.1) == "$0.10"


class TestUsageTotals:
    """Test UsageTotals model to cover missing line 199."""
    
    def test_usage_totals_total_tokens_property(self):
        """Test the total_tokens computed property."""
        totals = UsageTotals(
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            total_cost=0.05,
        )
        
        # This should trigger line 199 in the total_tokens property
        assert totals.total_tokens == 185  # 100 + 50 + 25 + 10
    
    def test_usage_totals_with_zeros(self):
        """Test UsageTotals with zero values."""
        totals = UsageTotals(
            input_tokens=0,
            output_tokens=0,
            cache_creation_tokens=0,
            cache_read_tokens=0,
            total_cost=0.0,
        )
        
        assert totals.total_tokens == 0


class TestUsageModels:
    """Test all usage models to cover missing computed properties."""
    
    def test_token_counts_total_tokens(self):
        """Test TokenCounts total_tokens property."""
        from ccusage.models.usage import TokenCounts
        
        tokens = TokenCounts(
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
        )
        
        assert tokens.total_tokens == 185  # 100 + 50 + 25 + 10
    
    def test_raw_usage_entry_total_tokens(self):
        """Test RawUsageEntry total_tokens property."""
        from ccusage.models.usage import RawUsageEntry
        from datetime import datetime
        
        entry = RawUsageEntry(
            timestamp=datetime.now(),
            session_id="test-session",
            message_id="test-message",
            model_name="claude-sonnet-4",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            project_path="/test/path",
            version="1.0.0",
        )
        
        assert entry.total_tokens == 185  # 100 + 50 + 25 + 10
    
    def test_model_breakdown_total_tokens(self):
        """Test ModelBreakdown total_tokens property."""
        from ccusage.models.usage import ModelBreakdown
        
        breakdown = ModelBreakdown(
            model_name="claude-sonnet-4",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            cost=0.05,
        )
        
        assert breakdown.total_tokens == 185  # 100 + 50 + 25 + 10
    
    def test_daily_usage_total_tokens(self):
        """Test DailyUsage total_tokens property."""
        from ccusage.models.usage import DailyUsage
        
        daily = DailyUsage(
            date="2025-07-15",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            total_cost=0.05,
            models_used=["claude-sonnet-4"],
        )
        
        assert daily.total_tokens == 185  # 100 + 50 + 25 + 10
    
    def test_monthly_usage_total_tokens(self):
        """Test MonthlyUsage total_tokens property."""
        from ccusage.models.usage import MonthlyUsage
        
        monthly = MonthlyUsage(
            month="2025-07",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            total_cost=0.05,
            models_used=["claude-sonnet-4"],
        )
        
        assert monthly.total_tokens == 185  # 100 + 50 + 25 + 10
    
    def test_session_usage_total_tokens(self):
        """Test SessionUsage total_tokens property."""
        from ccusage.models.usage import SessionUsage
        from datetime import datetime
        
        session = SessionUsage(
            session_id="test-session",
            project_path="/test/path",
            input_tokens=100,
            output_tokens=50,
            cache_creation_tokens=25,
            cache_read_tokens=10,
            total_cost=0.05,
            last_activity=datetime.now(),
            versions=["1.0.0"],
            models_used=["claude-sonnet-4"],
        )
        
        assert session.total_tokens == 185  # 100 + 50 + 25 + 10


if __name__ == "__main__":
    pytest.main([__file__])