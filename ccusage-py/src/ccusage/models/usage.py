"""Usage data models for ccusage-py."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, computed_field

from .base import (
    BaseUsageModel,
    DailyDate,
    MessageId,
    ModelName,
    MonthlyDate,
    NonNegativeFloat,
    NonNegativeInt,
    ProjectPath,
    RequestId,
    SessionId,
    Version,
)


class TokenCounts(BaseModel):
    """Token counts for various token types."""

    input_tokens: NonNegativeInt
    output_tokens: NonNegativeInt
    cache_creation_tokens: NonNegativeInt = Field(default=0)
    cache_read_tokens: NonNegativeInt = Field(default=0)

    @computed_field
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens across all types."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
        )


class RawUsageEntry(BaseUsageModel):
    """Raw usage entry from JSONL files."""

    timestamp: datetime
    session_id: SessionId
    request_id: RequestId | None = None
    message_id: MessageId
    model_name: ModelName
    input_tokens: NonNegativeInt
    output_tokens: NonNegativeInt
    cache_creation_tokens: NonNegativeInt = Field(default=0)
    cache_read_tokens: NonNegativeInt = Field(default=0)
    cost_usd: NonNegativeFloat | None = None
    project_path: ProjectPath
    version: Version

    @computed_field
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
        )


class ModelPricing(BaseModel):
    """Model pricing information from LiteLLM."""

    input_cost_per_token: float | None = None
    output_cost_per_token: float | None = None
    cache_creation_input_token_cost: float | None = None
    cache_read_input_token_cost: float | None = None
    max_tokens: int | None = None
    max_input_tokens: int | None = None
    max_output_tokens: int | None = None
    litellm_provider: str | None = None
    mode: str | None = None
    supports_function_calling: bool | None = None
    supports_parallel_function_calling: bool | None = None
    supports_vision: bool | None = None


class ModelBreakdown(BaseUsageModel):
    """Model-specific breakdown of usage and cost."""

    model_name: ModelName
    input_tokens: NonNegativeInt
    output_tokens: NonNegativeInt
    cache_creation_tokens: NonNegativeInt = Field(default=0)
    cache_read_tokens: NonNegativeInt = Field(default=0)
    cost: NonNegativeFloat

    @computed_field
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens for this model."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
        )


class DailyUsage(BaseUsageModel):
    """Daily usage aggregation."""

    date: DailyDate
    input_tokens: NonNegativeInt
    output_tokens: NonNegativeInt
    cache_creation_tokens: NonNegativeInt = Field(default=0)
    cache_read_tokens: NonNegativeInt = Field(default=0)
    total_cost: NonNegativeFloat
    models_used: list[ModelName]
    model_breakdowns: list[ModelBreakdown] = Field(default_factory=list)

    @computed_field
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens for the day."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
        )


class MonthlyUsage(BaseUsageModel):
    """Monthly usage aggregation."""

    month: MonthlyDate
    input_tokens: NonNegativeInt
    output_tokens: NonNegativeInt
    cache_creation_tokens: NonNegativeInt = Field(default=0)
    cache_read_tokens: NonNegativeInt = Field(default=0)
    total_cost: NonNegativeFloat
    models_used: list[ModelName]
    model_breakdowns: list[ModelBreakdown] = Field(default_factory=list)

    @computed_field
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens for the month."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
        )


class SessionUsage(BaseUsageModel):
    """Session usage aggregation."""

    session_id: SessionId
    project_path: ProjectPath
    input_tokens: NonNegativeInt
    output_tokens: NonNegativeInt
    cache_creation_tokens: NonNegativeInt = Field(default=0)
    cache_read_tokens: NonNegativeInt = Field(default=0)
    total_cost: NonNegativeFloat
    last_activity: datetime
    versions: list[Version]
    models_used: list[ModelName]
    model_breakdowns: list[ModelBreakdown] = Field(default_factory=list)

    @computed_field
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens for the session."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
        )


class UsageTotals(BaseModel):
    """Aggregated usage totals."""

    input_tokens: NonNegativeInt
    output_tokens: NonNegativeInt
    cache_creation_tokens: NonNegativeInt = Field(default=0)
    cache_read_tokens: NonNegativeInt = Field(default=0)
    total_cost: NonNegativeFloat

    @computed_field
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens across all usage."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
        )
