# Daily — {{date}} ({{weekday}})

## Перенос со вчера
{{#each carryover}}
- [ ] {{this.title}} ({{this.project}} • {{this.id}})
{{/each}}

## Фокус дня (≤{{daily_tasks_max}})
{{#each focus_tasks}}
- [ ] {{this.title}} ({{this.project}} • {{this.id}} • {{this.priority}})
{{/each}}

## Блокеры/риски
- ...

## EoD — итоги
**Сделано:**  
- ...

**Решения/инсайты:**  
- ...

**Перенос на завтра:**  
- ...
