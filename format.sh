#!/bin/bash

# Format and lint code before committing
# Usage: ./format.sh

echo "🎨 Formatting code with Black..."
black app/ observability/ tests/

echo ""
echo "🔍 Linting with Ruff..."
ruff check --fix app/ observability/ tests/

echo ""
echo "✨ Organizing imports..."
ruff check --select I --fix app/ observability/ tests/

echo ""
echo "✅ Code formatting complete!"
echo ""
echo "Run './test.sh' to verify tests still pass"