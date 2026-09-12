# Daily Plan - {{date}}

**Generated:** {{timestamp}}

**Configuration:**
- Max tasks: {{daily_tasks_max}}
- Max projects: {{weekly_projects_max}}
- Tasks selected: {{task_count}}
- Projects involved: {{project_count}}

## Monthly Goals

{{#each monthly_goals}}
- {{this}}
{{/each}}

## Today's Tasks

{{#each tasks}}
### {{@index}}. [{{priority}}] {{task_id}} - {{project}}

**Task:** {{title}}

**Project Context:** [{{project}} analysis](../projects/{{project}}.md)

**File:** `{{file_path}}`

**Scope:** {{scope}}

{{#if project_overview}}
**Project Overview:**
- **Type:** {{project_overview.type}}
- **Tech Stack:** {{project_overview.stack}}
- **Key Features:** {{project_overview.features}}
- **CLI Commands:** {{project_overview.commands}}
- **Current State:** {{project_overview.state}}
{{/if}}

{{#if risks}}
**Risks & Considerations:**
{{#each risks}}
- {{this}}
{{/each}}
{{/if}}

{{#if todos}}
**TODO Before Starting:**
{{#each todos}}
- [ ] {{this}}
{{/each}}
{{/if}}

**Notes:** {{notes}}

- [ ] Completed

{{/each}}

## Notes

(Add your notes and observations here during the day)

## End of Day Summary

(To be filled with `/ctx.eod`)
