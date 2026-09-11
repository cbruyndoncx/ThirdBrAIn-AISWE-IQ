"""Constants for ccusage-py."""

from __future__ import annotations

from pathlib import Path

from platformdirs import user_config_dir

# User's home directory
USER_HOME_DIR = Path.home()

# XDG config directory
XDG_CONFIG_DIR = Path(user_config_dir())

# Default Claude data directory paths
DEFAULT_CLAUDE_CODE_PATH = ".claude"
DEFAULT_CLAUDE_CONFIG_PATH = XDG_CONFIG_DIR / "claude"

# Environment variable for specifying Claude data directories
CLAUDE_CONFIG_DIR_ENV = "CLAUDE_CONFIG_DIR"

# Claude projects directory name
CLAUDE_PROJECTS_DIR_NAME = "projects"

# JSONL file pattern for usage data
USAGE_DATA_GLOB_PATTERN = "**/*.jsonl"

# LiteLLM pricing URL
LITELLM_PRICING_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)

# Default values for various operations
DEFAULT_RECENT_DAYS = 3
DEFAULT_REFRESH_INTERVAL_SECONDS = 1
MIN_REFRESH_INTERVAL_SECONDS = 1
MAX_REFRESH_INTERVAL_SECONDS = 60
MIN_RENDER_INTERVAL_MS = 16

# Display thresholds
BLOCKS_WARNING_THRESHOLD = 0.8
BLOCKS_COMPACT_WIDTH_THRESHOLD = 120
BLOCKS_DEFAULT_TERMINAL_WIDTH = 120

# Cost calculation thresholds
DEBUG_MATCH_THRESHOLD_PERCENT = 0.1

# Burn rate thresholds (tokens per minute)
BURN_RATE_THRESHOLDS = {
    "HIGH": 1000,
    "MODERATE": 500,
}
