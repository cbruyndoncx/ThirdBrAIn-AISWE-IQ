"""Base models and types for ccusage-py."""

from __future__ import annotations

import re
from enum import Enum
from typing import Annotated, NewType

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Branded types using NewType (Python 3.13 enhanced)
ModelName = NewType("ModelName", str)
SessionId = NewType("SessionId", str)
RequestId = NewType("RequestId", str)
MessageId = NewType("MessageId", str)
DailyDate = NewType("DailyDate", str)
MonthlyDate = NewType("MonthlyDate", str)
FilterDate = NewType("FilterDate", str)
ProjectPath = NewType("ProjectPath", str)
ISOTimestamp = NewType("ISOTimestamp", str)
Version = NewType("Version", str)


class CostMode(str, Enum):
    """Cost calculation modes."""

    AUTO = "auto"
    CALCULATE = "calculate"
    DISPLAY = "display"


class SortOrder(str, Enum):
    """Sort order options."""

    DESC = "desc"
    ASC = "asc"


class BaseUsageModel(BaseModel):
    """Base model for usage data with common configuration."""

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        extra="forbid",
    )


class DateString(BaseModel):
    """Validated date string in YYYY-MM-DD format."""

    value: str

    @field_validator("value")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date string format."""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class MonthString(BaseModel):
    """Validated month string in YYYY-MM format."""

    value: str

    @field_validator("value")
    @classmethod
    def validate_month_format(cls, v: str) -> str:
        """Validate month string format."""
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise ValueError("Month must be in YYYY-MM format")
        return v


class FilterDateString(BaseModel):
    """Validated filter date string in YYYYMMDD format."""

    value: str

    @field_validator("value")
    @classmethod
    def validate_filter_date_format(cls, v: str) -> str:
        """Validate filter date string format."""
        if not re.match(r"^\d{8}$", v):
            raise ValueError("Filter date must be in YYYYMMDD format")
        return v


class TimestampString(BaseModel):
    """Validated ISO timestamp string."""

    value: str

    @field_validator("value")
    @classmethod
    def validate_timestamp_format(cls, v: str) -> str:
        """Validate ISO timestamp format."""
        if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$", v):
            raise ValueError("Invalid ISO timestamp format")
        return v


class VersionString(BaseModel):
    """Validated version string."""

    value: str

    @field_validator("value")
    @classmethod
    def validate_version_format(cls, v: str) -> str:
        """Validate version string format."""
        if not re.match(r"^\d+\.\d+\.\d+", v):
            raise ValueError("Invalid version format")
        return v


# Type aliases for cleaner code
NonNegativeInt = Annotated[int, Field(ge=0)]
NonNegativeFloat = Annotated[float, Field(ge=0.0)]
PositiveFloat = Annotated[float, Field(gt=0.0)]
NonEmptyStr = Annotated[str, Field(min_length=1)]


def create_model_name(value: str) -> ModelName:
    """Create a validated ModelName."""
    if not value.strip():
        raise ValueError("Model name cannot be empty")
    return ModelName(value)


def create_session_id(value: str) -> SessionId:
    """Create a validated SessionId."""
    if not value.strip():
        raise ValueError("Session ID cannot be empty")
    return SessionId(value)


def create_request_id(value: str) -> RequestId:
    """Create a validated RequestId."""
    if not value.strip():
        raise ValueError("Request ID cannot be empty")
    return RequestId(value)


def create_message_id(value: str) -> MessageId:
    """Create a validated MessageId."""
    if not value.strip():
        raise ValueError("Message ID cannot be empty")
    return MessageId(value)


def create_daily_date(value: str) -> DailyDate:
    """Create a validated DailyDate."""
    DateString(value=value)  # Validate format
    return DailyDate(value)


def create_monthly_date(value: str) -> MonthlyDate:
    """Create a validated MonthlyDate."""
    MonthString(value=value)  # Validate format
    return MonthlyDate(value)


def create_filter_date(value: str) -> FilterDate:
    """Create a validated FilterDate."""
    FilterDateString(value=value)  # Validate format
    return FilterDate(value)


def create_project_path(value: str) -> ProjectPath:
    """Create a validated ProjectPath."""
    if not value.strip():
        raise ValueError("Project path cannot be empty")
    return ProjectPath(value)


def create_iso_timestamp(value: str) -> ISOTimestamp:
    """Create a validated ISOTimestamp."""
    TimestampString(value=value)  # Validate format
    return ISOTimestamp(value)


def create_version(value: str) -> Version:
    """Create a validated Version."""
    VersionString(value=value)  # Validate format
    return Version(value)


def format_model_name(model_name: str) -> str:
    """Format a model name to a shorter, more readable format."""
    # Extract model type from full model name
    # e.g., "claude-sonnet-4-20250514" -> "sonnet-4"
    # e.g., "claude-opus-4-20250514" -> "opus-4"
    match = re.match(r"claude-(\w+)-(\d+)-\d+", model_name)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    # Return original if pattern doesn't match
    return model_name


def format_number(num: int) -> str:
    """Format a number with locale-specific thousand separators."""
    return f"{num:,}"


def format_currency(amount: float, currency_code: str = "USD", currency_symbol: str = "$") -> str:
    """
    Format a number as currency with appropriate symbol and decimal places.
    
    Args:
        amount: The amount to format
        currency_code: Currency code (e.g., 'USD', 'GBP', 'EUR')
        currency_symbol: Currency symbol (e.g., '$', '£', '€')
    
    Returns:
        Formatted currency string
    """
    # Some currencies don't typically use decimal places
    if currency_code.upper() in ("JPY", "KRW", "VND", "IDR"):
        return f"{currency_symbol}{amount:,.0f}"
    else:
        return f"{currency_symbol}{amount:,.2f}"
