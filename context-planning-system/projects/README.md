# Projects Directory

This directory contains your project repositories and task files.

## Flexible Structure Options

The Context Planning System supports multiple organizational patterns. Choose what works best for you:

### Option 1: Simple Flat Structure

Perfect for personal projects or small teams:

```
projects/
├── my-app/
│   └── specs/
│       └── tasks.md
├── website/
│   └── specs/
│       └── tasks.md
└── side-project/
    └── specs/
        └── tasks.md
```

### Option 2: Organized by Organization

Good for managing work across multiple clients or organizations:

```
projects/
├── client-a/
│   └── project-x/
│       └── specs/
│           └── tasks.md
├── client-b/
│   └── project-y/
│       └── specs/
│           └── tasks.md
└── personal/
    └── hobby-project/
        └── specs/
            └── tasks.md
```

### Option 3: Direct Project Folders

Minimal structure for quick setup:

```
projects/
├── mobile-app/
│   └── tasks.md
├── backend-api/
│   └── tasks.md
└── frontend/
    └── tasks.md
```

**Note:** The scanner looks for `tasks.md` files, so you can place them at any depth.

## Creating Your First Project

### Quick Start

```bash
# Create a simple project structure
mkdir -p projects/my-project/specs
```

Create `projects/my-project/specs/tasks.md`:

```markdown
# My Project Tasks

## Setup

- [ ] T001 P1 Initialize project
- [ ] T002 P2 Configure environment
- [X] T003 P1 Create documentation

## Development

- [ ] T101 P1 Implement core feature
- [ ] T102 P2 Add tests
- [ ] T103 P3 Optimize performance
```

### Run Scanner

```bash
/ctx.scan
```

The scanner will find all `tasks.md` files and aggregate them into `state/backlog.yaml`.

## Task File Format

### Checkbox Syntax

- `- [ ]` = Open task
- `- [X]` or `- [x]` = Completed task

### Task Components

```markdown
- [ ] T101 P1 Task description
      ^^^^ ^^ ^^^^^^^^^^^^^^^
      |    |  └─ Description
      |    └─── Priority (P1/P2/P3)
      └──────── Task ID (optional)
```

### Example Task File

```markdown
# Feature Name

## Phase 1: Setup P1

- [ ] T001 P1 Setup development environment
- [ ] T002 P1 Configure CI/CD pipeline
- [X] T003 P1 Create initial documentation

## Phase 2: Implementation

### Backend P1

- [ ] T101 P1 Implement REST API
- [ ] T102 P1 Add authentication
- [ ] T103 P2 Add rate limiting

### Frontend P2

- [ ] T201 P2 Create UI components
- [ ] T202 P2 Implement state management
- [ ] T203 P3 Add animations

## Backlog P3

- [ ] T301 P3 Refactor old code
- [ ] T302 P3 Improve error messages
- [ ] T303 P3 Add more tests
```

## Priority Levels

- **P1**: High priority (critical, blockers, urgent)
- **P2**: Medium priority (normal development work)
- **P3**: Low priority (nice-to-have, tech debt, refactoring)

## Task IDs

- Pattern: `T` followed by numbers (e.g., `T1`, `T100`, `T999`)
- Optional but recommended for tracking
- Auto-generated hash ID if not provided

## Scanning Behavior

The scanner (`/ctx.scan`) will:

1. Recursively search for `tasks.md` files in this directory
2. Parse checkbox items and extract metadata
3. Detect priorities from task lines or heading context
4. Generate unique IDs for tasks without explicit IDs
5. Aggregate everything into `state/backlog.yaml`

## Additional Files

You can also organize tasks in checklists:

```
projects/
└── my-project/
    └── specs/
        ├── tasks.md
        └── checklists/
            ├── security-checklist.md
            ├── deployment-checklist.md
            └── review-checklist.md
```

Configure which files to scan in `BaseContext.yaml`:

```yaml
rules:
  include_open_tasks_from:
    - "tasks.md"
    - "checklists/*.md"
```

## Best Practices

1. **Keep tasks atomic**: One task = one clear action
2. **Use descriptive titles**: Help your future self understand context
3. **Set realistic priorities**: Not everything can be P1
4. **Update regularly**: Mark tasks as done when completed
5. **Review periodically**: Use `/ctx.weekly` to reflect on progress

## Examples

### Personal Projects

```
projects/
├── blog/
│   └── specs/
│       └── tasks.md           # Blog posts and improvements
├── portfolio/
│   └── specs/
│       └── tasks.md           # Portfolio updates
└── learning/
    └── specs/
        └── tasks.md           # Learning goals and exercises
```

### Work Projects

```
projects/
├── main-product/
│   └── specs/
│       ├── tasks.md           # General tasks
│       └── checklists/
│           ├── sprint-23.md   # Sprint-specific tasks
│           └── release.md     # Release checklist
└── side-service/
    └── specs/
        └── tasks.md
```

### Mixed Structure

```
projects/
├── work/
│   ├── project-a/
│   │   └── specs/tasks.md
│   └── project-b/
│       └── specs/tasks.md
├── personal/
│   ├── app/
│   │   └── specs/tasks.md
│   └── website/
│       └── specs/tasks.md
└── learning/
    └── tasks.md               # Directly in project folder
```

## Tips

- **Start simple**: Begin with one project, expand as needed
- **Experiment**: Try different structures to find what works
- **Stay flexible**: The system adapts to your organization
- **Use meaningful names**: Clear project/folder names help navigation
- **Document decisions**: Add comments in tasks.md to capture context

---

**Ready to get started?** Create your first project structure and run `/ctx.scan`!
