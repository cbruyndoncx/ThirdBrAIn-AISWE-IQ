![ccusage-py daily](./assets/ccusage-py-daily.png?v=3 "ccusage-py daily")
└─ `ccusage-py daily`  

![ccusage-py sessions](./assets/ccusage-py-sessions.png?v=3 "ccusage-py sessions")
└─ `ccusage-py sessions`

![ccusage-py daily --graph](./assets/ccusage-py-daily-graph.png?v=3 "ccusage-py daily --graph")
└─ `ccusage-py daily --graph`  

![ccusage-py sessions --graph](./assets/ccusage-py-sessions-graph.png?v=3 "ccusage-py sessions --graph")
└─ `ccusage-py sessions --graph`

ccusage-py-daily-graph.png
ccusage-py-daily.png
ccusage-py-sessions-graph.png
ccusage-py-sessions.png

All code in this project, including tests and this README below the test coverage, was created using Claude Code. For me, this was a practical exercise beyond my daily use of Claude Code (mostly simple Python scripts).

The first prompt was:
> You are a master level TypeScript and Python programmer.
> Your tasks are:
> - Analyse the content of the repository in the ccusage-ts directory.
> - Give an overview of the code functionality.
> - Plan implementing the same functionality in Python. You can use any library necessary to achieve that. For nice presentation I suggest using the "rich" library.

After the second prompt (fixed JSON parsing) the code was fully working. The rest of the coding were small fixes and improvements, and the tests - `ccusage-py` has 99% tests coverage:
```
======================================================================= tests coverage =======================================================================
______________________________________________________ coverage: platform darwin, python 3.13.5-final-0 ______________________________________________________

Name                                    Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------------
src/ccusage/__init__.py                     6      0      0      0   100%
src/ccusage/commands/__init__.py            2      0      0      0   100%
src/ccusage/commands/daily.py              90      0     32      0   100%
src/ccusage/commands/monthly.py            84      0     26      0   100%
src/ccusage/commands/session.py           102      0     36      0   100%
src/ccusage/core/__init__.py                2      0      0      0   100%
src/ccusage/core/constants.py              21      0      0      0   100%
src/ccusage/core/exceptions.py             17      0      0      0   100%
src/ccusage/core/result.py                134      0     40      8    95%   86->exit, 95->exit, 104->exit, 113->exit, 122->exit, 131->exit, 159->155, 172->168
src/ccusage/core/utils.py                  66      0     24      0   100%
src/ccusage/currency/__init__.py            4      0      0      0   100%
src/ccusage/currency/cache.py              89      0     26      0   100%
src/ccusage/currency/converter.py          95      0     28      0   100%
src/ccusage/currency/detector.py           31      0     10      0   100%
src/ccusage/currency/fetcher.py            59      2     18      1    96%   133-134
src/ccusage/data/__init__.py                2      0      0      0   100%
src/ccusage/data/loader.py                 99      0     40      2    99%   36->33, 51->48
src/ccusage/data/processor.py             160      1     58      2    99%   284->exit, 307
src/ccusage/main.py                        75      0      4      0   100%
src/ccusage/models/__init__.py              4      0      0      0   100%
src/ccusage/models/base.py                114      0     24      0   100%
src/ccusage/models/usage.py               106      0      0      0   100%
src/ccusage/presentation/__init__.py        2      0      0      0   100%
src/ccusage/presentation/formatter.py     228      0     68      0   100%
src/ccusage/presentation/graphs.py        163      3     62      1    98%   215-217
src/ccusage/pricing/__init__.py             2      0      0      0   100%
src/ccusage/pricing/calculator.py          32      0     10      0   100%
src/ccusage/pricing/fetcher.py            122      0     50      0   100%
-----------------------------------------------------------------------------------
TOTAL                                    1911      6    556     14    99%
Coverage HTML written to dir htmlcov
==================================================================== 706 passed in 3.12s =====================================================================
```

***

# ccusage-py

**Python implementation of ccusage** - Analyze your Claude Code token usage and costs from local JSONL files.

This project is inspired by and provides feature parity with the original [ccusage](https://github.com/ryoppippi/ccusage) TypeScript implementation, reimagined for Python developers.

## Features

- 📊 **Daily Reports**: View token usage and costs aggregated by date.
- 📅 **Monthly Reports**: View token usage and costs aggregated by month.
- 💬 **Session Reports**: View usage grouped by conversation sessions.
- 🕐 **Today View**: Quick access to today's session activity (default).
- 🎯 **Command Aliases**: Short aliases for faster access (`d`, `m`, `s`, `t`).
- 📅 **Date Filtering**: Filter sessions by date range with `--since` and `--until`.
- 🏷️ **Context-Aware Summaries**: Smart summary labels based on view type.
- 🎨 **Rich Terminal Output**: Beautiful tables with responsive formatting.
- 📱 **Compact Mode**: Automatic adaptation to narrow terminals.
- 📄 **JSON Output**: Export data in structured JSON format.
- 💰 **Multi-Currency Support**: Display costs in your local currency or specify with `--currency`.
- 🌍 **Automatic Currency Detection**: Uses system locale to determine preferred currency.
- 💱 **Real-Time Exchange Rates**: Live currency conversion with smart caching.
- 🗄️ **Cache Token Support**: Tracks cache creation and read tokens separately.
- 🔌 **Offline Mode**: Use pre-cached pricing data without network connectivity.
- 📊 **ASCII Graph Visualization**: Visual cost charts with the `--graph` flag.
- 🐍 **Modern Python**: Built with Python 3.13+ and modern best practices.

## Installation

### Quick Start

```bash
# Using uv (recommended)
uv run ccusage-py

# Or install globally
uv tool install ccusage-py
ccusage-py
```

### From Source

```bash
git clone https://github.com/m6k/ccusage-py.git
cd ccusage-py
uv sync
uv run ccusage-py
```

## Usage

> **New in latest version**: Command aliases, today view as default, date filtering for sessions, and context-aware summary labels!

```bash
# Basic usage
ccusage-py          # Show today's sessions (default).
ccusage-py daily    # Daily token usage and costs.
ccusage-py monthly  # Monthly aggregated report.
ccusage-py session  # Usage by conversation session.

# Command aliases (faster access)
ccusage-py d        # Daily report.
ccusage-py m        # Monthly report.
ccusage-py s        # Session report.
ccusage-py sessions # Session report (alternative).
ccusage-py t        # Today's sessions.
ccusage-py today    # Today's sessions (alternative).

# Date filtering (sessions only)
ccusage-py s --since 20250101 --until 20250131  # Sessions in date range.
ccusage-py session --since 20250115             # Sessions from specific date.
ccusage-py t                                     # Today's sessions (automatic).

# With options
ccusage-py daily --since 20250101 --until 20250131
ccusage-py daily --json  # JSON output.
ccusage-py daily --breakdown  # Per-model cost breakdown.
ccusage-py daily --graph  # Show ASCII cost visualization charts.
ccusage-py daily --currency EUR  # Display costs in Euros.
ccusage-py daily --mode calculate --order asc  # Cost calculation mode and sort order.
ccusage-py monthly --offline  # Use offline pricing data.
ccusage-py session --breakdown --json  # Session report with model breakdown in JSON format.
ccusage-py session --currency GBP --graph  # UK pounds with graphs.

# Additional options
ccusage-py --version  # Show version information.
```

## CLI Options

### Commands
- `today` (default) - Show today's session usage report.
- `daily` - Show daily usage report.
- `monthly` - Show monthly aggregated report.
- `session` - Show usage by conversation session.

### Command Aliases
- `t`, `today` - Today's sessions (default).
- `d` - Daily report.
- `m` - Monthly report.
- `s`, `sessions` - Session report.

### Common Options
- `--json` - Output in JSON format instead of formatted tables.
- `--breakdown` - Show per-model cost breakdown.
- `--graph, -g` - Show ASCII graphs for cost visualization.
- `--currency CODE` - Display costs in specified currency (e.g., EUR, GBP, JPY).
- `--offline` - Use cached pricing data without network connectivity.
- `--order {desc,asc}` - Sort order (desc=newest first, asc=oldest first).

### Date Range Options
Available for: `daily`, `monthly`, `session`
- `--since YYYYMMDD` - Start date (e.g., 20250101).
- `--until YYYYMMDD` - End date (e.g., 20250131).

**Note**: Session date filtering shows only sessions with activity in the specified date range.

### Cost Calculation Modes (daily/monthly only)
- `--mode {auto,calculate,display}` - Cost calculation method:
  - `auto` (default) - Automatically choose best method.
  - `calculate` - Calculate from token usage using current pricing.
  - `display` - Use costs recorded in usage data.

### Graph Visualization Options
- `--graph, -g` - Enable ASCII graph visualization for cost data:
  - **Daily reports**: Cost distribution bar charts and trend sparklines.
  - **Monthly reports**: Monthly cost comparison charts and trend analysis.
  - **Session reports**: Session activity charts and cost comparison visualizations.
  - **Responsive design** that adapts to terminal width with Unicode block characters.

### Global Options
- `--version` - Show version information.

## Data Sources

The tool automatically searches for Claude usage data in:
1. Custom path via `CLAUDE_CONFIG_DIR` environment variable.
2. `~/.config/claude/projects/` (XDG config directory).
3. `~/.claude/projects/` (legacy location).

## Requirements

- Python 3.13+.
- Claude Code usage data in one of the supported locations above.

## Environment Configuration

### Environment Variables
- `CLAUDE_CONFIG_DIR` - Override default data directory paths (supports comma-separated multiple paths).
- `COLUMNS` - Override terminal width detection.

### Output Features
- **Responsive Design**: Automatically adapts to terminal width.
- **Rich Formatting**: Beautiful tables with colors and syntax highlighting.
- **JSON Export**: Structured data export for further processing.
- **Model Breakdown**: Per-model usage and cost analysis.
- **Cache Token Tracking**: Separate tracking of cache creation and read tokens.
- **Context-Aware Summaries**: Summary labels adapt based on view type:
  - **"Today Total"** for today's sessions.
  - **"Monthly Total"** for monthly reports.
  - **"Filtered Total"** for date-range filtered sessions.
  - **"Total"** for unfiltered views.

## Architecture

ccusage-py follows a layered architecture with modern Python patterns and practices:

### Core Architectural Patterns

**Result Pattern for Error Handling**
- `src/ccusage/core/result.py` implements a Rust-inspired Result type with `Ok[T]` and `Err[E]` variants.
- All data processing operations return `Result` types instead of raising exceptions.
- Use helper functions: `ok()`, `err()`, `is_ok()`, `is_err()`, `unwrap()`.

**Async/Await Data Processing**
- All data loading and processing operations are async for performance with large datasets.
- `DataLoader.load_raw_entries()` and `DataProcessor.process_*_usage()` methods are async.
- Commands use `asyncio.run()` to bridge sync CLI interface with async internals.

**Functional Programming Approach**
- Immutable data models with Pydantic v2.
- Pure functions for data transformations.
- Composition over inheritance for component design.

### Technology Stack

- **Async/await**: Efficient I/O operations for large datasets.
- **LiteLLM Integration**: Real-time pricing data with offline caching.
- **Pydantic v2**: Data validation and type safety with immutable models.
- **Result Pattern**: Functional error handling inspired by Rust.
- **Rich**: Beautiful terminal output with responsive tables and ASCII graphs.
- **Typer**: Type-safe CLI with automatic help generation and command aliases.
- **aiohttp**: Async HTTP client for external API calls.
- **uv**: Modern Python package management and virtual environment handling.

### Layered Architecture

```
CLI Commands (main.py, commands/) 
    ↓
Currency Conversion (currency/)
    ↓
Data Processing (data/processor.py)
    ↓  
Data Loading (data/loader.py)
    ↓
Models & Validation (models/)
    ↓
Core Utilities (core/)
```

### Key Components

**Data Flow Pipeline**
1. **DataLoader** (`data/loader.py`): Loads raw JSONL files from Claude usage directories.
2. **DataProcessor** (`data/processor.py`): Aggregates raw entries into daily/monthly/session views.
3. **CurrencyConverter** (`currency/converter.py`): Handles multi-currency cost conversion.
4. **ResponsiveTableFormatter** (`presentation/formatter.py`): Formats data for terminal output.
5. **PricingFetcher** (`pricing/fetcher.py`): Fetches real-time pricing data from LiteLLM API.

**Model Hierarchy**
- `RawUsageEntry`: Raw data from JSONL files (timestamp, tokens, costs, session info).
- `DailyUsage`, `MonthlyUsage`, `SessionUsage`: Aggregated views with computed fields.
- `ModelBreakdown`: Per-model usage and cost breakdown with currency conversion support.
- `UsageTotals`: Summary statistics with multi-currency display.

**CLI Architecture**
- **Typer-based**: Type-safe CLI with automatic help generation.
- **Command Aliases**: Short aliases (d, m, s, t) for common operations.
- **Rich Integration**: Beautiful terminal output with responsive tables and ASCII graphs.
- **Currency Support**: Automatic locale detection and manual currency override.

### Currency Conversion System

**Multi-Currency Architecture**
- `CurrencyConverter`: Main conversion orchestrator with async context manager.
- `ExchangeRateFetcher`: Fetches live rates from exchangerate-api.com.
- `ExchangeRateCache`: Two-tier caching (memory + file) with TTL and jitter.
- `LocaleDetector`: Automatic currency detection from system locale.

**Conversion Modes**
- `AUTO`: Uses system locale to determine target currency.
- `CUSTOM`: Uses user-specified currency code.
- Fallback to USD if conversion fails or is unavailable.

**Caching Strategy**
- In-memory cache for performance within session.
- File-based persistence across application runs.
- TTL-based expiration (2 hours) with random jitter to prevent thundering herd.
- Graceful degradation to stale rates when fresh data unavailable.

### Data Sources and Configuration

**Data Discovery Priority**
1. `CLAUDE_CONFIG_DIR` environment variable (supports comma-separated multiple paths).
2. `~/.config/claude/projects/` (XDG standard).
3. `~/.claude/projects/` (legacy location).

**Cost Calculation Modes**
- `AUTO`: Intelligently chooses between display and calculate modes.
- `CALCULATE`: Uses LiteLLM pricing API for real-time cost calculation.
- `DISPLAY`: Uses pre-recorded costs from usage data.

**Currency Configuration**
- Automatic detection via system locale (LC_MONETARY).
- Manual override with `--currency` flag.
- Cache directory: `{claude_config}/currency_cache/`.

### Performance Optimizations

**Caching Layers**
- LiteLLM pricing data cached in memory across instances.
- File-based pricing cache (`litellm_pricing_cache.json`) for offline usage.
- Exchange rate caching with configurable TTL and persistence.
- Async I/O for processing large JSONL files efficiently.

**Memory Management**
- Streaming JSONL processing for large datasets.
- Generator-based data processing to minimize memory footprint.
- Lazy loading of pricing and exchange rate data.

## Project Structure

```
ccusage-py/
├── src/ccusage/
│   ├── main.py              # CLI entry point.
│   ├── models/              # Pydantic data models.
│   ├── core/                # Core utilities and patterns.
│   ├── data/                # Data loading and processing.
│   ├── currency/            # Multi-currency conversion system.
│   │   ├── cache.py         # Exchange rate caching.
│   │   ├── converter.py     # Currency conversion orchestrator.
│   │   ├── detector.py      # Locale-based currency detection.
│   │   └── fetcher.py       # Exchange rate API client.
│   ├── pricing/             # LiteLLM integration.
│   ├── presentation/        # Rich table formatting and graphs.
│   └── commands/            # CLI command implementations.
├── tests/                   # Comprehensive test suite (99% coverage).
└── pyproject.toml           # Project configuration.
```

## Development

```bash
# Setup development environment:
uv sync --dev

# Run tests:
uv run pytest

# Format code:
uv run ruff format

# Type checking:
uv run mypy src/

# Run linting:
uv run ruff check
```

## Inspiration

This project is inspired by the excellent [ccusage](https://github.com/ryoppippi/ccusage) TypeScript implementation by [@ryoppippi](https://github.com/ryoppippi). The Python version aims to provide the same functionality while leveraging Python's ecosystem and modern development practices.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
