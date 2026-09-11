"""Utility functions for ccusage-py."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .constants import (
    CLAUDE_CONFIG_DIR_ENV,
    CLAUDE_PROJECTS_DIR_NAME,
    DEFAULT_CLAUDE_CODE_PATH,
    DEFAULT_CLAUDE_CONFIG_PATH,
    USER_HOME_DIR,
)
from .exceptions import ConfigurationError


def get_claude_paths() -> list[Path]:
    """Get all Claude data directories to search for usage data.

    Supports multiple paths: environment variable (comma-separated),
    new default, and old default.

    Returns:
        Array of valid Claude data directory paths
    """
    paths: list[Path] = []
    normalized_paths: set[Path] = set()

    # Check environment variable first (supports comma-separated paths)
    env_paths = os.environ.get(CLAUDE_CONFIG_DIR_ENV, "").strip()
    if env_paths:
        env_path_list = [p.strip() for p in env_paths.split(",") if p.strip()]
        for env_path in env_path_list:
            normalized_path = Path(env_path).resolve()
            if normalized_path.is_dir():
                projects_path = normalized_path / CLAUDE_PROJECTS_DIR_NAME
                if projects_path.is_dir() and normalized_path not in normalized_paths:
                        normalized_paths.add(normalized_path)
                        paths.append(normalized_path)

    # Add default paths if they exist
    default_paths = [
        DEFAULT_CLAUDE_CONFIG_PATH,  # New default: XDG config directory
        USER_HOME_DIR / DEFAULT_CLAUDE_CODE_PATH,  # Old default: ~/.claude
    ]

    for default_path in default_paths:
        normalized_path = default_path.resolve()
        if normalized_path.is_dir():
            projects_path = normalized_path / CLAUDE_PROJECTS_DIR_NAME
            if projects_path.is_dir() and normalized_path not in normalized_paths:
                    normalized_paths.add(normalized_path)
                    paths.append(normalized_path)

    return paths


def validate_claude_paths(paths: list[Path]) -> None:
    """Validate that Claude paths exist and are accessible.

    Args:
        paths: List of Claude data directory paths

    Raises:
        ConfigurationError: If no valid paths are found
    """
    if not paths:
        raise ConfigurationError(
            "No Claude data directories found. "
            f"Expected directories at {DEFAULT_CLAUDE_CONFIG_PATH} "
            f"or {USER_HOME_DIR / DEFAULT_CLAUDE_CODE_PATH}. "
            f"You can also set {CLAUDE_CONFIG_DIR_ENV} environment variable."
        )

    # Check that at least one path has projects directory
    valid_paths = []
    for path in paths:
        projects_path = path / CLAUDE_PROJECTS_DIR_NAME
        if projects_path.is_dir():
            valid_paths.append(path)

    if not valid_paths:
        raise ConfigurationError(
            f"No valid Claude projects directories found in: {', '.join(str(p) for p in paths)}"
        )


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float with default fallback."""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int with default fallback."""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def format_date_compact(date_str: str) -> str:
    """Format date string for compact display."""
    # Convert YYYY-MM-DD to MM/DD format
    try:
        year, month, day = date_str.split("-")
        return f"{month}/{day}"
    except ValueError:
        return date_str  # Return original if parsing fails


def is_date_string(text: str) -> bool:
    """Check if string matches YYYY-MM-DD date format."""
    import re
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", text))


def get_terminal_width() -> int:
    """Get terminal width with fallback."""
    try:
        # Try environment variable first
        if columns := os.environ.get("COLUMNS"):
            return int(columns)

        # Try getting from stdout
        import shutil
        width = shutil.get_terminal_size().columns
        return width
    except (ValueError, OSError):
        return 120  # Default fallback
