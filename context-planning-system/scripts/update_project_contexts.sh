#!/usr/bin/env bash
# Universal script to update project contexts
# Called by git hooks: post-commit, post-merge, post-checkout

set -e

HOOK_NAME="${1:-manual}"
CONTEXT_ROOT="$(git rev-parse --show-toplevel)"
cd "$CONTEXT_ROOT"

echo "🔄 [$HOOK_NAME] Updating project contexts..."

# Detect changes based on hook type
case "$HOOK_NAME" in
    "post-merge")
        # After git pull - compare with previous HEAD
        CHANGED_FILES=$(git diff --name-only HEAD@{1} HEAD 2>/dev/null || echo "")
        ;;
    "post-commit")
        # After commit - compare with previous commit
        CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || echo "")
        ;;
    "post-checkout")
        # After checkout - compare with previous branch
        CHANGED_FILES=$(git diff --name-only $2 $3 2>/dev/null || echo "")
        ;;
    "manual")
        # Manual run - analyze all projects
        CHANGED_FILES=$(find projects -type f | head -1)  # Force update
        ;;
esac

# Extract changed projects (org/repo)
CHANGED_PROJECTS=$(echo "$CHANGED_FILES" | grep "^projects/" | cut -d/ -f2-3 | sort -u || true)

# Find all current projects
ALL_PROJECTS=$(find projects -mindepth 2 -maxdepth 2 -type d | sed 's|^projects/||' | sort)

# Create reports directory
mkdir -p reports/projects

# Track if any changes were made
UPDATED=0
DELETED=0

# Handle changed/added projects
if [ -n "$CHANGED_PROJECTS" ]; then
    echo "📋 Detected changes in projects:"
    while IFS= read -r project; do
        if [ -d "projects/$project" ]; then
            echo "  📊 Analyzing: $project"
            python3 skills/ctx-collector/scripts/analyze_project.py \
                "projects/$project" \
                --output "reports/projects/$(basename $project).md" \
                2>/dev/null && UPDATED=$((UPDATED + 1)) || echo "  ⚠️  Failed"
        fi
    done <<< "$CHANGED_PROJECTS"
fi

# Handle deleted projects
for report in reports/projects/*.md; do
    [ -f "$report" ] || continue
    [ "$report" = "reports/projects/INDEX.md" ] && continue

    PROJECT_NAME=$(basename "$report" .md)

    # Check if project still exists
    PROJECT_FOUND=0
    while IFS= read -r project; do
        if [ "$(basename $project)" = "$PROJECT_NAME" ]; then
            PROJECT_FOUND=1
            break
        fi
    done <<< "$ALL_PROJECTS"

    if [ $PROJECT_FOUND -eq 0 ]; then
        echo "  🗑️  Removing: $PROJECT_NAME (project deleted)"
        rm -f "reports/projects/$PROJECT_NAME.md"
        rm -f "reports/projects/$PROJECT_NAME.json"
        DELETED=$((DELETED + 1))
    fi
done

# Regenerate index if there were changes
if [ $UPDATED -gt 0 ] || [ $DELETED -gt 0 ]; then
    echo "📝 Regenerating project index..."
    python3 << 'PYEOF'
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict

reports_dir = Path("reports/projects")
index_lines = [
    "# Project Context Index",
    "",
    f"**Generated:** {datetime.now().isoformat()}",
    f"**Total Projects:** {len(list(reports_dir.glob('*.json')))}",
    "",
    "## Quick Links",
    ""
]

# Group by organization
projects_by_org = defaultdict(list)

for json_file in sorted(reports_dir.glob("*.json")):
    try:
        with open(json_file) as f:
            data = json.load(f)
            org = data.get("organization", "unknown")
            projects_by_org[org].append(data)
    except:
        continue

# Generate index by organization
for org in sorted(projects_by_org.keys()):
    if org == "unknown":
        continue

    index_lines.append(f"### {org}")
    index_lines.append("")

    for project in sorted(projects_by_org[org], key=lambda p: p["name"]):
        name = project["name"]
        desc = project.get("overview", {}).get("description", "No description")[:100]
        index_lines.append(f"#### [{name}](projects/{name}.md)")
        index_lines.append(f"**Description:** {desc}")
        index_lines.append("")

# Write index
with open("reports/projects/INDEX.md", "w") as f:
    f.write("\n".join(index_lines))
PYEOF

    echo "✅ Updated: $UPDATED | Deleted: $DELETED"
else
    echo "✅ No project changes detected"
fi
