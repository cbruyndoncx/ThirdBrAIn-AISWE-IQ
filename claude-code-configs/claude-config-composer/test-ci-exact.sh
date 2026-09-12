#!/bin/bash
set -e

echo "=== Testing in Node 18 environment (matching CI) ==="
echo ""

# Clean and reinstall to ensure fresh state
echo "Cleaning node_modules and dist..."
rm -rf node_modules dist package-lock.json

echo "Installing with npm ci (like CI does)..."
npm install

echo "Building..."
npm run build

echo "Running tests..."
npm test

echo ""
echo "Testing CLI list command..."
OUTPUT=$(node dist/cli-simple.js list)

# Check that all expected configs appear
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
echo "=== All tests passed! ==="
