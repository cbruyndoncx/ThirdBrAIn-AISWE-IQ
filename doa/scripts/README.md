# Context Management Scripts

Three bash scripts for managing structured context log files with automatic rotation and efficient reading.

## Scripts

### `add-context`
Adds properly formatted entries to a context file with auto-generated metadata.

**Usage:**
```bash
add-context --agent AGENT --model MODEL [OPTIONS] [BODY_TEXT]
```

**Required Parameters:**
- `--agent AGENT` - Agent name and version (e.g., "CLI/1.0")
- `--model MODEL` - Model name and version (e.g., "gpt-4")

**Optional Parameters:**
- `--session SESSION` - Session identifier
- `--output FILE` - Output context file (default: `context.md`)
- `--file FILE` - Read body from file

**Body Input (priority order):**
1. Remaining arguments as body text (quoted)
2. `--file` to read from file
3. stdin if no body provided

**Auto-generated Fields:**
- `date` - ISO 8601 local date and time with offset
- `hash` - Base64 encoded SHA-256 hash of body text
- `startCommit` - Git hash of most recent commit (if in git repo)

**Examples:**
```bash
# Body as argument
add-context --agent "CLI/1.0" --model "gpt-4" "This is my context"

# Body from file
add-context --agent "CLI/1.0" --model "gpt-4" --file body.txt

# Body from stdin
cat body.txt | add-context --agent "CLI/1.0" --model "gpt-4"

# With session and custom output
add-context --agent "CLI/1.0" --model "gpt-4" --session "abc123" \
  --output my-context.md "Context text"
```

### `read-context`
Efficiently reads the last N entries from a context file without loading the entire file into memory.

**Usage:**
```bash
read-context [OPTIONS]
```

**Options:**
- `-n, --num N` - Number of entries to read (default: `1`)
- `-f, --file FILE` - Context file to read (default: `context.md`)
- `-h, --headers-only` - Show only entry headers (date, hash, agent, model)
- `--help` - Show help message

**Behavior:**
- Reads entries in chronological order (oldest to newest of the N selected)
- Uses single-pass AWK parsing for efficiency
- Memory usage: Only stores the requested N entries
- Performance: O(n) where n = total entries in file

**Examples:**
```bash
# Read last entry (default)
read-context

# Read last 3 entries
read-context -n 3

# Show only headers of last entry
read-context --headers-only

# Show headers of last 5 entries
read-context -n 5 --headers-only

# Read from different file
read-context -f project/archived-context.md -n 2

# Quick session start: see where you left off
read-context -n 2
```

**Use Cases:**
- Session resumption: Quickly see recent work without scrolling
- Debugging: Check what happened in last N interactions
- Auditing: Review recent context entries
- Integration: Parse headers programmatically for automation

### `rotate-context`
Rotates context files when they exceed a size limit, moving older entries to timestamped overflow files.

**Usage:**
```bash
rotate-context [OPTIONS]
```

**Options:**
- `--file FILE` - Context file to rotate (default: `context.md`)
- `--size BYTES` - Size limit in bytes (default: `1048576` = 1MB)
- `--keep N` - Number of recent entries to keep (default: `2`)

**Behavior:**
- Checks file size; if under limit, exits with code 1 (no rotation)
- If over limit and has more than `--keep` entries, creates overflow file
- Overflow filename: `<basename>-YYYY-MM-DDTHH_MM_SS±OFFSET.md`
- Original file is trimmed to keep only the last N entries
- Prints overflow filename to stdout on success (exit code 0)
- Returns exit code 2 on errors

**Examples:**
```bash
# Use defaults (context.md, 1MB, keep 2 entries)
rotate-context

# Custom file and limits
rotate-context --file mycontext.md --size 2097152 --keep 3

# Capture overflow filename
OVERFLOW=$(rotate-context --file context.md)
if [ $? -eq 0 ]; then
    echo "Created overflow: $OVERFLOW"
fi
```

## Entry Format

Each entry in the context file follows this structure:

```
---
date: 2026-01-25T13:44:33+0000
hash: KQjNYowLItHmgLl89cEJ4/5D+IMB3nkezcnIkaOTe2Q=
agent: CLI/1.0
model: gpt-4
session: abc123
startCommit: a1b2c3d4
---

Body text goes here.
Can contain multiple lines.
Any characters or whitespace.

EOF

```

**Notes:**
- Blank line required between entries
- `EOF` marker must be on its own line
- `session` and `startCommit` fields are optional
- Body text is hashed for integrity verification
- **Important:** The `EOF` marker is automatically added by `add-context` - do not include it in your body text

## Installation

```bash
chmod +x add-context read-context rotate-context
# Optionally move to PATH
sudo mv add-context read-context rotate-context /usr/local/bin/
```

## Workflow Example

```bash
# Start session: see where you left off
read-context -n 2

# Add entries throughout the day
add-context --agent "MyApp/1.0" --model "gpt-4" "Morning context"
add-context --agent "MyApp/1.0" --model "gpt-4" "Afternoon update"
add-context --agent "MyApp/1.0" --model "gpt-4" "Evening notes"

# Quick check: review recent work
read-context --headers-only -n 3

# Rotate when needed (manually or via cron)
rotate-context

# Or integrate rotation into your workflow
if rotate-context --size 500000 --keep 5; then
    echo "Rotated context to: $(rotate-context --size 500000 --keep 5)"
fi
```

## Integration Ideas

**Session start routine:**
```bash
# See recent work before starting
read-context -n 2
# or just headers for a quick overview
read-context --headers-only -n 5
```

**Manual rotation:**
```bash
# Check and rotate when needed
rotate-context || echo "No rotation needed"
```

**Automated rotation (cron):**
```bash
# Add to crontab to check daily
0 0 * * * /path/to/rotate-context --file /path/to/context.md
```

**Post-add hook:**
```bash
# Create wrapper script
add-context "$@" && rotate-context
```

**Parse recent entries programmatically:**
```bash
# Extract dates from last 10 entries
read-context -n 10 --headers-only | grep "^date:" | cut -d' ' -f2-

# Get agent used in last entry
read-context --headers-only | grep "^agent:" | cut -d' ' -f2-
```

## Dependencies

- bash
- openssl (for SHA-256 hashing)
- git (optional, for startCommit field)
- Standard Unix tools: awk, sed, grep, stat

## Platform Notes

**macOS vs Linux:**
The scripts handle platform differences in `stat` command automatically:
- macOS: `stat -f%z`
- Linux: `stat -c%s`

## Exit Codes

**add-context:**
- `0` - Success
- `1` - Invalid arguments or missing required parameters
- `2` - File errors

**read-context:**
- `0` - Success
- `1` - Invalid arguments or file not found

**rotate-context:**
- `0` - Rotation performed (overflow filename printed to stdout)
- `1` - No rotation needed (file under size limit or insufficient entries)
- `2` - Error (file not found, etc.)
