---
description: Update BaseContext.yaml configuration
---

# Update Configuration

Make targeted updates to `BaseContext.yaml` configuration file.

## What this does

Updates planning parameters and goals in the main configuration file.

## Usage

Edit `BaseContext.yaml` directly or provide specific updates:

```bash
vi BaseContext.yaml
```

## Configuration Sections

### 1. WIP Limits

```yaml
wip_limits:
  daily_tasks_max: 5      # Max tasks per day
  weekly_projects_max: 3  # Max concurrent projects
```

**When to update:**
- You consistently under/over-commit
- Team size changes
- Working style changes

### 2. Monthly Goals

```yaml
goals:
  month:
    - "Goal 1"
    - "Goal 2"
    - "Goal 3"
```

**When to update:**
- At the start of each month
- When priorities change
- After completing major milestones

### 3. Cadence

```yaml
cadence:
  weekly_review_day: "Monday"
  monthly_cycle: "next-30-days"
```

### 4. Prioritization

```yaml
prioritization:
  order: ["P1", "P2", "P3"]
  tie_breakers:
    - "unblocker_first"
    - "short_first"
```

## After Updating

1. **Validate YAML:**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('BaseContext.yaml'))"
   ```

2. **Commit changes:**
   ```bash
   git add BaseContext.yaml
   git commit -m "config: update [what you changed]"
   git push
   ```

3. **Re-plan if needed:**
   If you changed WIP limits or priorities, regenerate today's plan:
   ```bash
   /ctx.daily
   ```

## Examples

**Increase daily task limit:**
```yaml
wip_limits:
  daily_tasks_max: 7  # was 5
```

**Update monthly goals:**
```yaml
goals:
  month:
    - "Launch MVP version 1.0"
    - "Reach 1000 users"
    - "Complete security audit"
```

## See Also

- Full reference: `skills/ctx-planning/references/configuration.md`
- Example config: `BaseContext.yaml`
