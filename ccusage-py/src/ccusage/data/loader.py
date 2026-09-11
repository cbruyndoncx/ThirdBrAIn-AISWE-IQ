"""Data loading utilities for JSONL files."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path

from pydantic import ValidationError

from ..core.constants import USAGE_DATA_GLOB_PATTERN
from ..core.exceptions import DataLoadError
from ..core.result import Err, Ok, Result, err, ok
from ..models.usage import RawUsageEntry


class DataLoader:
    """Async JSONL data loader with streaming support."""

    def __init__(self, claude_paths: list[Path]) -> None:
        """Initialize data loader with Claude paths."""
        self.claude_paths = claude_paths

    async def load_raw_entries(self) -> Result[list[RawUsageEntry], DataLoadError]:
        """Load all raw usage entries from JSONL files."""
        entries: list[RawUsageEntry] = []

        for claude_path in self.claude_paths:
            projects_path = claude_path / "projects"
            if not projects_path.exists():
                continue

            async for entry_result in self._stream_entries(projects_path):
                if isinstance(entry_result, Ok):
                    entries.append(entry_result.value)
                elif isinstance(entry_result, Err):
                    # Only print warnings for actual errors, not for missing usage data
                    if "No usage data found in entry" not in str(entry_result.error):
                        print(f"Warning: {entry_result.error}")

        return ok(entries)

    async def _stream_entries(self, projects_path: Path) -> AsyncIterator[Result[RawUsageEntry, DataLoadError]]:
        """Stream entries from all JSONL files."""
        jsonl_files = list(projects_path.rglob(USAGE_DATA_GLOB_PATTERN))

        for file_path in jsonl_files:
            async for line in self._read_jsonl_file(file_path):
                if isinstance(line, Ok):
                    yield self._parse_entry(line.value, file_path)
                elif isinstance(line, Err):
                    yield err(line.error)

    async def _read_jsonl_file(self, file_path: Path) -> AsyncIterator[Result[str, DataLoadError]]:
        """Read JSONL file line by line."""
        try:
            with file_path.open("r", encoding="utf-8") as f:
                for _line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    yield ok(line)
        except OSError as e:
            yield err(DataLoadError(f"Failed to read file {file_path}: {e}"))

    def _parse_entry(self, line: str, file_path: Path) -> Result[RawUsageEntry, DataLoadError]:
        """Parse a single JSONL line into a RawUsageEntry."""
        try:
            data = json.loads(line)

            # Transform the data to match our model
            transformed_data = self._transform_raw_data(data)
            
            # Skip entries without usage data (like user messages)
            if not transformed_data:
                return err(DataLoadError("No usage data found in entry"))

            entry = RawUsageEntry.model_validate(transformed_data)
            return ok(entry)
        except json.JSONDecodeError as e:
            return err(DataLoadError(f"Invalid JSON in {file_path}: {e}"))
        except ValidationError as e:
            return err(DataLoadError(f"Validation error in {file_path}: {e}"))
        except Exception as e:
            return err(DataLoadError(f"Failed to parse entry in {file_path}: {e}"))

    def _transform_raw_data(self, data: dict) -> dict:
        """Transform raw JSONL data to match our model structure."""
        # Extract data from actual Claude format
        message = data.get("message", {})
        usage = message.get("usage", {})
        
        # Skip entries without usage data (like user messages)
        if not usage:
            return {}
            
        transformed = {
            "timestamp": data.get("timestamp"),
            "session_id": data.get("sessionId"),
            "request_id": data.get("requestId"),
            "message_id": message.get("id"),
            "model_name": message.get("model"),
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "cache_creation_tokens": usage.get("cache_creation_input_tokens", 0),
            "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
            "cost_usd": data.get("cost_usd"),  # This may not be in the original data
            "project_path": data.get("cwd"),
            "version": data.get("version", "1.0.0"),
        }

        # Remove None values
        return {k: v for k, v in transformed.items() if v is not None}


class StreamingDataLoader:
    """Alternative streaming data loader for large datasets."""

    def __init__(self, claude_paths: list[Path]) -> None:
        """Initialize streaming data loader."""
        self.claude_paths = claude_paths

    async def stream_raw_entries(self) -> AsyncIterator[Result[RawUsageEntry, DataLoadError]]:
        """Stream raw usage entries one by one."""
        for claude_path in self.claude_paths:
            projects_path = claude_path / "projects"
            if not projects_path.exists():
                continue

            jsonl_files = list(projects_path.rglob(USAGE_DATA_GLOB_PATTERN))

            for file_path in jsonl_files:
                async for entry_result in self._stream_file_entries(file_path):
                    yield entry_result

    async def _stream_file_entries(self, file_path: Path) -> AsyncIterator[Result[RawUsageEntry, DataLoadError]]:
        """Stream entries from a single JSONL file."""
        try:
            with file_path.open("r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                        transformed_data = self._transform_raw_data(data)
                        entry = RawUsageEntry.model_validate(transformed_data)
                        yield ok(entry)
                    except json.JSONDecodeError as e:
                        yield err(DataLoadError(f"Invalid JSON in {file_path}:{line_num}: {e}"))
                    except ValidationError as e:
                        yield err(DataLoadError(f"Validation error in {file_path}:{line_num}: {e}"))
                    except Exception as e:
                        yield err(DataLoadError(f"Failed to parse entry in {file_path}:{line_num}: {e}"))
        except OSError as e:
            yield err(DataLoadError(f"Failed to read file {file_path}: {e}"))

    def _transform_raw_data(self, data: dict) -> dict:
        """Transform raw JSONL data to match our model structure."""
        # Same transformation logic as DataLoader
        transformed = {
            "timestamp": data.get("timestamp"),
            "session_id": data.get("sessionId") or data.get("session_id"),
            "request_id": data.get("requestId") or data.get("request_id"),
            "message_id": data.get("messageId") or data.get("message_id"),
            "model_name": data.get("modelName") or data.get("model_name") or data.get("model"),
            "input_tokens": data.get("inputTokens") or data.get("input_tokens") or 0,
            "output_tokens": data.get("outputTokens") or data.get("output_tokens") or 0,
            "cache_creation_tokens": data.get("cacheCreationTokens") or data.get("cache_creation_tokens") or 0,
            "cache_read_tokens": data.get("cacheReadTokens") or data.get("cache_read_tokens") or 0,
            "cost_usd": data.get("costUSD") or data.get("cost_usd"),
            "project_path": data.get("projectPath") or data.get("project_path"),
            "version": data.get("version") or "1.0.0",
        }

        # Remove None values
        return {k: v for k, v in transformed.items() if v is not None}
