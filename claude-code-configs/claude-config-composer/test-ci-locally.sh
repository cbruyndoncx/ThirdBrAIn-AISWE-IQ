#!/bin/bash
set -e

echo "=== Replicating CI Environment (Node 18.20.8) ==="

# Use Docker to run in exact CI environment
docker run --rm -v "$(pwd):/app" -w /app node:18.20.8 bash -c '
set -e
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

echo ""
echo "=== Installing dependencies ==="
npm ci

echo ""
echo "=== Building project ==="
npm run build

echo ""
echo "=== Running tests ==="
npm test

echo ""
echo "=== Testing CLI list command ==="
OUTPUT=$(node dist/cli-simple.js list)

# Check that all expected configs appear in list
if ! echo "$OUTPUT" | grep -q "Next.js 15"; then
  echo "❌ Next.js 15 not found in config list"
  exit 1
fi

if ! echo "$OUTPUT" | grep -q "shadcn/ui"; then
  echo "❌ shadcn/ui not found in config list"
  exit 1
fi

if ! echo "$OUTPUT" | grep -q "Tailwind CSS"; then
  echo "❌ Tailwind CSS not found in config list"
  exit 1
fi

if ! echo "$OUTPUT" | grep -q "Vercel AI SDK"; then
  echo "❌ Vercel AI SDK not found in config list"
  exit 1
fi

if ! echo "$OUTPUT" | grep -q "Drizzle ORM"; then
  echo "❌ Drizzle ORM not found in config list"
  exit 1
fi

echo "✅ CLI list command working correctly!"

echo ""
echo "=== All CI checks passed! ==="
'
