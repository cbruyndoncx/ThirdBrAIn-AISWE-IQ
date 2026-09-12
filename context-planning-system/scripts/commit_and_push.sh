#!/usr/bin/env bash
set -euo pipefail
msg="${1:-chore(context): update}"
git add -A
git commit -m "$msg" || echo "[i] nothing to commit"
git push origin main
