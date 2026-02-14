#!/bin/bash

# Run tests for the Secure Enterprise Knowledge Hub API
# Usage: ./test.sh

echo "🧪 Running tests for Secure Enterprise Knowledge Hub API..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set test environment variables
export API_KEY="test-api-key-12345"
export ENVIRONMENT="test"

# Run pytest with coverage
echo "📊 Running tests with coverage..."
pytest tests/ -v --cov=app --cov=observability --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Tests complete!"
echo "📈 Coverage report generated in htmlcov/index.html"