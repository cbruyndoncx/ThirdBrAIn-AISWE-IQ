# Автоматическое обновление контекста проектов

Система автоматически обновляет контекстные отчеты проектов при любых изменениях.

## 🚀 Возможности

### ✅ Автоматические сценарии

| Действие | Что происходит | Когда |
|----------|----------------|-------|
| **Добавление проекта** | Создается новый отчет `reports/projects/<name>.md` | При `git commit` |
| **Обновление проекта** | Пересоздается отчет для измененного проекта | При `git commit` |
| **Удаление проекта** | Удаляются отчеты `.md` и `.json` | При `git commit` |
| **Git pull** | Обновляются контексты измененных проектов | После получения изменений |
| **Смена ветки** | Обновляются контексты при переключении веток | При `git checkout` |

### 🔄 Git Hooks

Система использует следующие git hooks:

```bash
.git/hooks/
├── post-commit    # После локального коммита
├── post-merge     # После git pull/merge
└── post-checkout  # После смены ветки
```

Все hooks вызывают единый скрипт:
```bash
scripts/update_project_contexts.sh
```

## 📦 Установка

На новой машине или после клонирования репозитория:

```bash
cd ~/context
bash scripts/install_hooks.sh
```

Вывод:
```
🔧 Installing git hooks...
  ✅ Installed: post-commit
  ✅ Installed: post-merge
  ✅ Installed: post-checkout

✅ Git hooks installed successfully!

Hooks will now run automatically on:
  - git commit   (updates changed projects)
  - git pull     (updates changed projects)
  - git checkout (updates when switching branches)
```

## 📝 Примеры использования

### Пример 1: Добавление нового проекта

```bash
# Создаем новый проект
mkdir -p projects/forgequant/new-strategy
echo "# New Strategy" > projects/forgequant/new-strategy/README.md

# Коммитим
git add projects/forgequant/new-strategy
git commit -m "add: new trading strategy"
```

**Результат:**
```
🔄 [post-commit] Updating project contexts...
📋 Detected changes in projects:
  📊 Analyzing: forgequant/new-strategy
📝 Regenerating project index...
✅ Updated: 1 | Deleted: 0
```

**Созданные файлы:**
- `reports/projects/new-strategy.md`
- `reports/projects/new-strategy.json`
- Обновлен `reports/projects/INDEX.md`

### Пример 2: Обновление проекта

```bash
# Меняем README
echo "## New Section" >> projects/forgequant/nt-playground/README.md

# Коммитим
git add projects/forgequant/nt-playground/README.md
git commit -m "docs: update nt-playground readme"
```

**Результат:**
```
🔄 [post-commit] Updating project contexts...
📋 Detected changes in projects:
  📊 Analyzing: forgequant/nt-playground
✅ Updated: 1 | Deleted: 0
```

### Пример 3: Удаление проекта

```bash
# Удаляем устаревший проект
git rm -rf projects/forgequant/old-project
git commit -m "remove: obsolete project"
```

**Результат:**
```
🔄 [post-commit] Updating project contexts...
  🗑️  Removing: old-project (project deleted)
📝 Regenerating project index...
✅ Updated: 0 | Deleted: 1
```

### Пример 4: Получение изменений (git pull)

```bash
git pull
```

**Результат:**
```
Updating a8a1aad..945af66
Fast-forward
 projects/forgequant/ai-trader/README.md | 5 +++++
 1 file changed, 5 insertions(+)

🔄 [post-merge] Updating project contexts...
📋 Detected changes in projects:
  📊 Analyzing: forgequant/ai-trader
✅ Updated: 1 | Deleted: 0
```

### Пример 5: Ручное обновление

Если нужно пересоздать все отчеты:

```bash
bash scripts/update_project_contexts.sh manual
```

## 🔍 Что анализируется

При обновлении контекста проекта извлекается:

- **Overview**: Название и описание из README/pyproject.toml
- **Stack**: Языки программирования и фреймворки
- **Structure**: Директории и ключевые файлы
- **Entry Points**: CLI, main модули
- **Specs**: Спецификации (Speckit/context-planning)
- **Tests**: Тестовый фреймворк и покрытие
- **Documentation**: Документация (MD, RST файлы)

## 🛠️ Ручное управление

### Обновить один проект

```bash
python3 .claude/skills/ctx-collector/scripts/analyze_project.py \
  projects/forgequant/nt-playground \
  --output reports/projects/nt-playground.md
```

### Обновить все проекты

```bash
for project in projects/*/*; do
  [ -d "$project" ] || continue
  name=$(basename "$project")
  python3 .claude/skills/ctx-collector/scripts/analyze_project.py \
    "$project" \
    --output "reports/projects/$name.md"
done
```

### Пересоздать индекс

```bash
python3 << 'EOF'
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict

reports_dir = Path("reports/projects")
# ... (код генерации индекса)
EOF
```

## 📊 Структура отчетов

```
reports/projects/
├── INDEX.md                    # Главный индекс
├── nt-playground.md           # Markdown отчет
├── nt-playground.json         # JSON данные
├── ai-trader.md
├── ai-trader.json
└── ... (26 проектов × 2 файла)
```

## 🔧 Troubleshooting

### Hook не срабатывает

```bash
# Проверить, что hooks установлены
ls -la .git/hooks/post-*

# Переустановить hooks
bash scripts/install_hooks.sh
```

### Отчет не обновился

```bash
# Ручное обновление
bash scripts/update_project_contexts.sh manual

# Проверить логи
git log -1 --stat
```

### Ошибка при анализе проекта

```bash
# Запустить анализ вручную с выводом ошибок
python3 .claude/skills/ctx-collector/scripts/analyze_project.py \
  projects/forgequant/problem-project \
  --output reports/projects/problem-project.md
```

## 💡 Best Practices

1. **Коммитьте часто** - контексты обновляются автоматически
2. **Добавляйте README** - описания проекта попадут в отчет
3. **Используйте pyproject.toml** - зависимости будут извлечены
4. **Документируйте структуру** - облегчит навигацию

## 🔗 Связанные команды

- `/ctx.scan` - сканирование задач
- `/ctx.daily` - создание дневного плана
- `/ctx.analyze <project>` - анализ конкретного проекта
