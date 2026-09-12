# Context Planning Workflows Reference

Detailed workflow specifications for the ctx-planning skill.

## Daily Planning Workflow Details

### Step 1: Configuration Loading

Load and validate `BaseContext.yaml`:

```yaml
wip_limits:
  daily_tasks_max: 5      # Hard limit on tasks per day
  weekly_projects_max: 3  # Soft limit on project diversity

prioritization:
  order: ["P1", "P2", "P3"]
  tie_breakers:
    - "unblocker_first"   # Tasks that unblock others
    - "short_first"       # Quick wins over long tasks
    - "least_recent_project"  # Rotate focus
    - "oldest_first"      # Oldest tasks first

goals:
  month:
    - "Launch MVP for project X"
    - "Complete security audit"
```

### Step 2: State Loading

Load backlog and carryover with validation:

**`state/backlog.yaml` structure:**
```yaml
generated_at: "2025-10-22T09:00:00+00:00"
items:
  - uid: "my-project#T101"
    project: "my-project"
    file: "projects/my-project/specs/feature/tasks.md"
    line: 42
    id: "T101"
    title: "Implement user authentication"
    priority: "P1"
    status: "open"
    scope:
      section: "Security"
      subsection: "Authentication"
```

**`state/carryover.yaml` structure:**
```yaml
date: "2025-10-21"
items:
  - uid: "my-project#T101"
    title: "Complete authentication tests"
    project: "my-project"
    priority: "P1"
    reason: "blocked_by_external"
    original_date: "2025-10-20"
```

### Step 3: Task Selection Algorithm

Pseudocode for task selection:

```python
def select_daily_tasks(backlog, carryover, config):
    selected = []
    projects_used = set()

    # 1. Add all carryover tasks first (high priority)
    for task in carryover.items:
        if len(selected) < config.daily_tasks_max:
            selected.append(task)
            projects_used.add(task.project)

    # 2. Fill remaining slots from backlog
    remaining_slots = config.daily_tasks_max - len(selected)

    # Sort backlog by priority order
    open_tasks = [t for t in backlog.items if t.status == "open"]

    for priority in config.prioritization.order:
        candidates = [t for t in open_tasks if t.priority == priority]

        # Apply tie-breakers
        candidates = apply_tie_breakers(candidates, config.tie_breakers)

        for task in candidates:
            if len(selected) >= config.daily_tasks_max:
                break

            # Check project diversity limit
            if task.project not in projects_used:
                if len(projects_used) >= config.weekly_projects_max:
                    # Only add from already-used projects
                    continue

            selected.append(task)
            projects_used.add(task.project)

    return selected
```

### Step 4: Tie-Breaker Implementation

**`unblocker_first`**: Detect tasks that unblock others

```python
def is_unblocker(task):
    """Check if task title contains unblocking keywords."""
    keywords = ["unblock", "prerequisite", "dependency", "blocker", "blocks"]
    return any(kw in task.title.lower() for kw in keywords)

def sort_by_unblocker(tasks):
    """Sort tasks with unblockers first."""
    unblockers = [t for t in tasks if is_unblocker(t)]
    others = [t for t in tasks if not is_unblocker(t)]
    return unblockers + others
```

**`short_first`**: Estimate task duration from title/scope

```python
def estimate_duration(task):
    """Estimate task duration category based on title."""
    short_indicators = ["fix", "update", "adjust", "tweak", "minor"]
    long_indicators = ["implement", "design", "architecture", "refactor", "migrate"]

    title_lower = task.title.lower()

    if any(ind in title_lower for ind in short_indicators):
        return 1  # Short task
    elif any(ind in title_lower for ind in long_indicators):
        return 3  # Long task
    else:
        return 2  # Medium task

def sort_by_duration(tasks):
    """Sort tasks by estimated duration (short first)."""
    return sorted(tasks, key=estimate_duration)
```

**`least_recent_project`**: Rotate focus across projects

```python
def sort_by_project_rotation(tasks, recent_projects):
    """Prioritize projects not recently worked on."""
    def project_priority(task):
        if task.project not in recent_projects:
            return 0  # Highest priority
        return recent_projects.index(task.project) + 1

    return sorted(tasks, key=project_priority)
```

### Step 5: Report Generation

Template variable mapping:

```python
def prepare_template_vars(selected_tasks, carryover, config):
    return {
        "date": datetime.date.today().isoformat(),
        "weekday": datetime.date.today().strftime("%A"),
        "daily_tasks_max": config.wip_limits.daily_tasks_max,
        "carryover": [
            {
                "title": task.title,
                "project": task.project,
                "id": task.id or "no-id",
            }
            for task in carryover.items
        ],
        "focus_tasks": [
            {
                "title": task.title,
                "project": task.project,
                "id": task.id or "no-id",
                "priority": task.priority,
            }
            for task in selected_tasks
        ]
    }
```

## End-of-Day Workflow Details

### EoD Report Structure

Update the daily report with completed sections:

```markdown
## EoD — Summary

**Completed:**
- [X] T101 Implement user authentication (my-project)
- [X] T250 Fix login button styling (my-project2)
- [ ] T251 Add password reset flow (my-project) ← Incomplete

**Decisions/Insights:**
- Decided to use OAuth2 instead of custom auth for better security
- Found performance bottleneck in session management (needs optimization)
- Team agreed to defer mobile app until web version is stable

**Carry to Tomorrow:**
- [ ] T251 Add password reset flow (blocked by external API access)
- [ ] T252 Write integration tests (needs more time)
```

### Carryover Generation Logic

```python
def generate_carryover(daily_report, date):
    """Extract incomplete tasks from daily report."""
    carryover = {
        "date": date,
        "items": []
    }

    # Parse "Carry to Tomorrow" section
    carry_section = extract_section(daily_report, "Carry to Tomorrow")

    for line in carry_section:
        if line.strip().startswith("- [ ]"):
            task_info = parse_checkbox_line(line)

            # Determine carryover reason
            reason = "needs_more_time"  # Default
            if "blocked" in line.lower():
                reason = "blocked_by_external"
            elif "deprioritized" in line.lower():
                reason = "deprioritized"

            carryover["items"].append({
                "uid": task_info.uid,
                "title": task_info.title,
                "project": task_info.project,
                "priority": task_info.priority,
                "reason": reason,
                "original_date": date
            })

    return carryover
```

## Weekly Review Workflow Details

### Achievement Aggregation

```python
def aggregate_achievements(daily_reports):
    """Aggregate completed tasks by project."""
    achievements = {}

    for report in daily_reports:
        completed = extract_completed_tasks(report)

        for task in completed:
            project = task.project
            if project not in achievements:
                achievements[project] = {
                    "tasks_completed": 0,
                    "milestones": [],
                    "notable_tasks": []
                }

            achievements[project]["tasks_completed"] += 1

            # Identify milestones (P1 tasks or tasks with "milestone" keyword)
            if task.priority == "P1" or "milestone" in task.title.lower():
                achievements[project]["milestones"].append(task.title)

            # Track notable achievements
            if task.priority in ["P1", "P2"]:
                achievements[project]["notable_tasks"].append(task.title)

    return achievements
```

### Goal Progress Assessment

```python
def assess_goal_progress(achievements, monthly_goals, backlog):
    """Assess progress toward monthly goals."""
    goal_progress = []

    for goal in monthly_goals:
        # Extract keywords from goal
        keywords = extract_goal_keywords(goal)

        # Find related tasks (completed + remaining)
        related_completed = find_related_tasks(achievements, keywords)
        related_open = find_related_tasks(backlog, keywords, status="open")

        total = len(related_completed) + len(related_open)
        if total > 0:
            progress_pct = len(related_completed) / total * 100
        else:
            progress_pct = 0

        # Assess status
        if progress_pct >= 80:
            status = "ahead of schedule"
        elif progress_pct >= 60:
            status = "on track"
        elif progress_pct >= 40:
            status = "at risk"
        else:
            status = "behind schedule"

        goal_progress.append({
            "goal": goal,
            "progress": f"{progress_pct:.0f}% complete ({status})",
            "completed": len(related_completed),
            "remaining": len(related_open)
        })

    return goal_progress
```

## Error Handling and Validation

### Common Validation Checks

```python
def validate_backlog(backlog):
    """Validate backlog structure."""
    required_fields = ["uid", "project", "title", "priority", "status"]

    for item in backlog.get("items", []):
        for field in required_fields:
            if field not in item:
                raise ValueError(f"Missing required field '{field}' in task {item.get('uid', 'unknown')}")

        if item["priority"] not in ["P1", "P2", "P3"]:
            raise ValueError(f"Invalid priority '{item['priority']}' for task {item['uid']}")

        if item["status"] not in ["open", "done"]:
            raise ValueError(f"Invalid status '{item['status']}' for task {item['uid']}")

def validate_config(config):
    """Validate BaseContext.yaml configuration."""
    if config.get("wip_limits", {}).get("daily_tasks_max", 0) < 1:
        raise ValueError("daily_tasks_max must be at least 1")

    if config.get("wip_limits", {}).get("weekly_projects_max", 0) < 1:
        raise ValueError("weekly_projects_max must be at least 1")

    priority_order = config.get("prioritization", {}).get("order", [])
    if not all(p in ["P1", "P2", "P3"] for p in priority_order):
        raise ValueError("Invalid priority order in configuration")
```

## Best Practices

### Daily Planning
- Run `/ctx.scan` before `/ctx.daily` to ensure backlog is current
- Review carryover tasks and update reasons if needed
- Check for blockers early in the day
- Update task priorities if circumstances change

### End-of-Day
- Be honest about incomplete tasks (don't mark as done if not finished)
- Document decisions and insights while fresh in memory
- Identify root causes of carryover (blocked vs. needs more time)
- Update task files to reflect actual progress

### Weekly Review
- Review weekly reports on the configured review day (default: Monday)
- Look for patterns in carryover reasons (recurring blockers?)
- Adjust WIP limits if consistently over/under capacity
- Realign priorities if goals are at risk

### Monthly Review
- Use monthly reviews to set next month's goals
- Identify systemic issues (tooling, process, dependencies)
- Celebrate wins and completed milestones
- Archive completed projects or phases
