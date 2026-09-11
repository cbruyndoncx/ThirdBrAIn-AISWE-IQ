#!/bin/bash
set -e

DEMO_DIR="$(dirname "$0")/../demo-project"

mkdir -p "$DEMO_DIR/.claude/skills/vercel-react-best-practices"
mkdir -p "$DEMO_DIR/.claude/skills/remotion-best-practices"
mkdir -p "$DEMO_DIR/.claude/skills/frontend-design"
mkdir -p "$DEMO_DIR/.claude/skills/karpathy-guidelines"

echo "Downloading vercel-react-best-practices..."
curl -sS -o "$DEMO_DIR/.claude/skills/vercel-react-best-practices/SKILL.md" \
  https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/react-best-practices/SKILL.md

echo "Downloading remotion-best-practices..."
curl -sS -o "$DEMO_DIR/.claude/skills/remotion-best-practices/SKILL.md" \
  https://raw.githubusercontent.com/remotion-dev/skills/main/skills/remotion/SKILL.md

echo "Downloading frontend-design..."
curl -sS -o "$DEMO_DIR/.claude/skills/frontend-design/SKILL.md" \
  https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md

echo "Downloading karpathy-guidelines..."
curl -sS -o "$DEMO_DIR/.claude/skills/karpathy-guidelines/SKILL.md" \
  https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/skills/karpathy-guidelines/SKILL.md

echo "Done! Downloaded 4 skills to $DEMO_DIR/.claude/skills/"
