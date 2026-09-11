"""Basic tests for ccusage-py."""

from __future__ import annotations

from datetime import datetime

import pytest

from ccusage.core.result import err, is_err, is_ok, ok
from ccusage.models.base import (
    CostMode,
    SortOrder,
    format_model_name,
)
from ccusage.models.usage import DailyUsage, RawUsageEntry, TokenCounts


def test_result_pattern():
    """Test Result pattern implementation."""
    # Test Ok result
    ok_result = ok(42)
    assert is_ok(ok_result)
    assert not is_err(ok_result)
    assert ok_result.value == 42

    # Test Err result
    err_result = err(ValueError("test error"))
    assert is_err(err_result)
    assert not is_ok(err_result)
    assert isinstance(err_result.error, ValueError)


def test_enums():
    """Test enum definitions."""
    assert CostMode.AUTO == "auto"
    assert CostMode.CALCULATE == "calculate"
    assert CostMode.DISPLAY == "display"

    assert SortOrder.DESC == "desc"
    assert SortOrder.ASC == "asc"


def test_model_name_formatting():
    """Test model name formatting."""
    assert format_model_name("claude-sonnet-4-20250514") == "sonnet-4"
    assert format_model_name("claude-opus-4-20250514") == "opus-4"
    assert format_model_name("custom-model") == "custom-model"


def test_token_counts():
    """Test token counts model."""
    tokens = TokenCounts(
        input_tokens=100,
        output_tokens=50,
        cache_creation_tokens=25,
        cache_read_tokens=10,
    )

    assert tokens.total_tokens == 185
    assert tokens.input_tokens == 100
    assert tokens.output_tokens == 50


def test_raw_usage_entry():
    """Test raw usage entry model."""
    entry = RawUsageEntry(
        timestamp=datetime.now(),
        session_id="test-session",
        request_id="test-request",
        message_id="test-message",
        model_name="claude-sonnet-4-20250514",
        input_tokens=100,
        output_tokens=50,
        cache_creation_tokens=25,
        cache_read_tokens=10,
        cost_usd=0.01,
        project_path="/test/project",
        version="1.0.0",
    )

    assert entry.total_tokens == 185
    assert entry.model_name == "claude-sonnet-4-20250514"
    assert entry.cost_usd == 0.01


def test_raw_usage_entry_optional_request_id():
    """Test raw usage entry model with optional request_id."""
    entry = RawUsageEntry(
        timestamp=datetime.now(),
        session_id="test-session",
        request_id=None,  # Test optional field
        message_id="test-message",
        model_name="claude-sonnet-4-20250514",
        input_tokens=100,
        output_tokens=50,
        cache_creation_tokens=25,
        cache_read_tokens=10,
        cost_usd=0.01,
        project_path="/test/project",
        version="1.0.0",
    )

    assert entry.total_tokens == 185
    assert entry.request_id is None


def test_daily_usage():
    """Test daily usage model."""
    usage = DailyUsage(
        date="2024-01-01",
        input_tokens=1000,
        output_tokens=500,
        cache_creation_tokens=100,
        cache_read_tokens=50,
        total_cost=0.15,
        models_used=["claude-sonnet-4-20250514"],
        model_breakdowns=[],
    )

    assert usage.total_tokens == 1650
    assert usage.date == "2024-01-01"
    assert usage.total_cost == 0.15


if __name__ == "__main__":
    pytest.main([__file__])
