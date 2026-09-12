# BaseContext.yaml Configuration Reference

Complete reference for configuring the context planning system.

## Configuration Structure

```yaml
version: 0.2                    # Configuration schema version
timezone: "Europe/Moscow"       # IANA timezone for date/time operations

cadence:
  weekly_review_day: "Monday"   # Day of week for weekly reviews
  monthly_cycle: "next-30-days" # Planning horizon

wip_limits:
  daily_tasks_max: 5            # Maximum tasks per day
  weekly_projects_max: 3        # Maximum concurrent projects

prioritization:
  order: ["P1", "P2", "P3"]     # Priority levels (high to low)
  tie_breakers:                 # Rules for same-priority tasks
    - "unblocker_first"         # Prioritize unblocking tasks
    - "short_first"             # Favor quick wins

goals:
  month:                        # Current month's objectives
    - "Launch MVP for project X"
    - "Complete security audit"

rules:
  include_open_tasks_from:      # Files to scan for tasks
    - "tasks.md"
    - "checklists/*.md"
  task_id_pattern: "T\\d+"      # Regex for task IDs
  priority_patterns: ["P1", "P2", "P3"]  # Valid priority markers
```

## Configuration Fields

### Top-Level Fields

#### `version` (string, required)

Configuration schema version. Current version: `0.2`

- **Type**: String
- **Example**: `"0.2"`
- **Purpose**: Enables forward compatibility and migration warnings

#### `timezone` (string, required)

IANA timezone identifier for date/time operations.

- **Type**: String (IANA timezone name)
- **Example**: `"America/New_York"`, `"Europe/London"`, `"Asia/Tokyo"`
- **Purpose**: Ensures consistent date calculations across time zones
- **Default**: System timezone if not specified

### `cadence` Section

Controls the rhythm of planning activities.

#### `weekly_review_day` (string)

Day of the week for weekly review generation.

- **Type**: String (day name)
- **Valid values**: `"Monday"`, `"Tuesday"`, ..., `"Sunday"`
- **Default**: `"Monday"`
- **Example**: `"Friday"` (for end-of-week reviews)

#### `monthly_cycle` (string)

Monthly planning cycle mode.

- **Type**: String
- **Valid values**:
  - `"next-30-days"`: Rolling 30-day window
  - `"calendar-month"`: Align with calendar months
- **Default**: `"next-30-days"`
- **Purpose**: Determines how monthly goals and reviews are scoped

### `wip_limits` Section

Work-in-progress limits to maintain focus and prevent overcommitment.

#### `daily_tasks_max` (integer)

Maximum number of tasks to plan per day.

- **Type**: Integer
- **Range**: 1-10 (recommended: 3-5)
- **Default**: `5`
- **Rationale**:
  - Too few (1-2): May underutilize capacity
  - Just right (3-5): Realistic completion rate
  - Too many (6+): Likely to have carryover, reduces focus

#### `weekly_projects_max` (integer)

Maximum number of distinct projects to work on per week.

- **Type**: Integer
- **Range**: 1-5 (recommended: 2-3)
- **Default**: `3`
- **Rationale**:
  - Single project (1): Maximum focus, but risky if blocked
  - Balanced (2-3): Good focus with flexibility
  - Too many (4+): Excessive context switching

### `prioritization` Section

Rules for task priority and selection.

#### `order` (array of strings)

Priority levels from highest to lowest.

- **Type**: Array of strings
- **Default**: `["P1", "P2", "P3"]`
- **Customization**: Can add P0 for emergencies or P4 for backlog
- **Example**:
  ```yaml
  order: ["P0", "P1", "P2", "P3", "P4"]
  ```

**Priority Level Meanings:**

- **P1**: High priority
  - Critical bugs or blockers
  - Urgent customer-facing issues
  - Hard deadlines (< 48 hours)
  - Dependencies blocking other work

- **P2**: Medium priority
  - Regular feature work
  - Planned improvements
  - Non-critical bugs
  - Standard development tasks

- **P3**: Low priority
  - Nice-to-have features
  - Technical debt
  - Refactoring
  - Documentation updates

#### `tie_breakers` (array of strings)

Ordered list of rules to break ties between same-priority tasks.

- **Type**: Array of strings
- **Default**: `["unblocker_first", "short_first"]`
- **Available tie-breakers**:

**`unblocker_first`**: Prioritize tasks that unblock other work
```yaml
# Example: These tasks would be selected first among P2s
- [ ] T101 P2 Unblock API deployment (needed for frontend)
- [ ] T102 P2 Complete auth prerequisite
```

**`short_first`**: Favor quick wins over long tasks
```yaml
# Example: Short tasks selected before long ones
- [ ] T201 P2 Fix typo in error message (short)
- [ ] T202 P2 Refactor entire authentication module (long)
```

**`least_recent_project`**: Rotate focus across projects
```yaml
# If worked on project-A yesterday, prioritize project-B today
```

**`oldest_first`**: Select tasks by creation date (oldest first)
```yaml
# Prevents old tasks from being perpetually deprioritized
```

**Custom tie-breaker order example:**
```yaml
tie_breakers:
  - "unblocker_first"        # 1st: Unblock others
  - "short_first"            # 2nd: Quick wins
  - "least_recent_project"   # 3rd: Rotate projects
  - "oldest_first"           # 4th: Age-based
```

### `goals` Section

High-level objectives for planning alignment.

#### `month` (array of strings)

Current month's goals.

- **Type**: Array of strings (free-form goal descriptions)
- **Purpose**: Align daily/weekly tasks with strategic objectives
- **Best practices**:
  - Keep goals measurable and specific
  - Limit to 3-5 goals per month
  - Use action verbs (Launch, Complete, Implement, etc.)
  - Include success criteria when possible

**Good goal examples:**
```yaml
goals:
  month:
    - "Launch MVP for trading dashboard (min 3 users)"
    - "Complete security audit for authentication module"
    - "Implement CI/CD pipeline (< 10 min build time)"
    - "Reduce technical debt by 20% (measured by code complexity)"
```

**Avoid vague goals:**
```yaml
# Bad: Too vague, not measurable
goals:
  month:
    - "Work on project X"
    - "Improve code quality"
    - "Learn new technology"
```

#### `quarter` (array of strings, optional)

Quarterly goals for longer-term planning.

```yaml
goals:
  quarter:
    - "Ship 3 major features"
    - "Grow user base to 1000 active users"
    - "Establish community forum"
```

### `rules` Section

Low-level parsing and validation rules.

#### `include_open_tasks_from` (array of strings)

File patterns to scan for tasks.

- **Type**: Array of glob patterns
- **Default**: `["tasks.md", "checklists/*.md"]`
- **Purpose**: Define which files contain actionable tasks
- **Examples**:
  ```yaml
  # Scan only tasks.md files
  include_open_tasks_from:
    - "tasks.md"

  # Include checklists and TODOs
  include_open_tasks_from:
    - "tasks.md"
    - "checklists/**/*.md"
    - "TODO.md"
  ```

#### `task_id_pattern` (string)

Regular expression for task ID format.

- **Type**: String (regex pattern)
- **Default**: `"T\\d+"`
- **Purpose**: Standardize task identification
- **Examples**:
  ```yaml
  # Standard: T1, T100, T999
  task_id_pattern: "T\\d+"

  # With project prefix: PROJ-T101
  task_id_pattern: "[A-Z]+-T\\d+"

  # Alphanumeric: TASK-A1B2
  task_id_pattern: "TASK-[A-Z0-9]+"
  ```

#### `priority_patterns` (array of strings)

Valid priority markers.

- **Type**: Array of strings (regex patterns)
- **Default**: `["P1", "P2", "P3"]`
- **Purpose**: Validate priority markers in tasks
- **Custom priority example**:
  ```yaml
  # Add P0 for critical emergencies
  priority_patterns: ["P0", "P1", "P2", "P3"]
  ```

## Configuration Examples

### Minimal Configuration

```yaml
version: 0.2
wip_limits:
  daily_tasks_max: 5
  weekly_projects_max: 3
goals:
  month:
    - "Launch MVP"
```

### Full-Featured Configuration

```yaml
version: 0.2
timezone: "America/Los_Angeles"

cadence:
  weekly_review_day: "Friday"
  monthly_cycle: "calendar-month"

wip_limits:
  daily_tasks_max: 4
  weekly_projects_max: 2

prioritization:
  order: ["P0", "P1", "P2", "P3", "P4"]
  tie_breakers:
    - "unblocker_first"
    - "short_first"
    - "least_recent_project"
    - "oldest_first"

goals:
  month:
    - "Launch trading bot MVP (target: 10 test users)"
    - "Complete security audit (pass all OWASP checks)"
    - "Implement real-time dashboard (< 1s latency)"
  quarter:
    - "Reach 100 active users"
    - "Establish partnership with 2 exchanges"
    - "Open-source core modules"

rules:
  include_open_tasks_from:
    - "tasks.md"
    - "checklists/**/*.md"
    - "ROADMAP.md"
  task_id_pattern: "[A-Z]+-T\\d+"
  priority_patterns: ["P0", "P1", "P2", "P3", "P4"]
```

### Configuration for Solo Developer

```yaml
version: 0.2
timezone: "Europe/Berlin"

wip_limits:
  daily_tasks_max: 3    # Conservative for solo work
  weekly_projects_max: 1  # Single focus

prioritization:
  order: ["P1", "P2", "P3"]
  tie_breakers:
    - "short_first"     # Momentum through quick wins

goals:
  month:
    - "Ship v1.0 of side project"
```

### Configuration for Team Lead

```yaml
version: 0.2
timezone: "America/New_York"

wip_limits:
  daily_tasks_max: 6    # More capacity, includes reviews
  weekly_projects_max: 4  # Overseeing multiple projects

prioritization:
  order: ["P1", "P2", "P3"]
  tie_breakers:
    - "unblocker_first"  # Unblock team first
    - "least_recent_project"  # Ensure all projects progress

goals:
  month:
    - "Unblock 3 critical team dependencies"
    - "Complete Q4 planning and resource allocation"
    - "Ship 2 major features across projects"
```

## Updating Configuration

### Manual Updates

Edit `BaseContext.yaml` directly:

```bash
# Open in your editor
code BaseContext.yaml

# Validate syntax (requires PyYAML)
python3 -c "import yaml; yaml.safe_load(open('BaseContext.yaml'))"
```

### Using `/ctx.update` Command

Request updates through the planning skill:

```
/ctx.update increase daily tasks to 6
/ctx.update add quarterly goal "Reach 1000 users"
/ctx.update change weekly review day to Friday
```

The skill will:
1. Parse your request
2. Update `BaseContext.yaml`
3. Validate syntax
4. Optionally regenerate current plans

## Troubleshooting

### Common Configuration Errors

**Invalid YAML syntax:**
```yaml
# Wrong: Missing quotes around special characters
timezone: Europe/Moscow

# Correct:
timezone: "Europe/Moscow"
```

**Invalid priority order:**
```yaml
# Wrong: Priorities not in high-to-low order
prioritization:
  order: ["P3", "P1", "P2"]

# Correct:
prioritization:
  order: ["P1", "P2", "P3"]
```

**Missing required fields:**
```yaml
# Wrong: Missing wip_limits
version: 0.2
goals:
  month: []

# Correct:
version: 0.2
wip_limits:
  daily_tasks_max: 5
  weekly_projects_max: 3
goals:
  month: []
```

### Validation Script

Create a simple validator:

```python
#!/usr/bin/env python3
import yaml
import sys

required_fields = ["version", "wip_limits", "goals"]

try:
    with open("BaseContext.yaml") as f:
        config = yaml.safe_load(f)

    for field in required_fields:
        if field not in config:
            print(f"Error: Missing required field '{field}'")
            sys.exit(1)

    print("✓ Configuration is valid")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
```
