#!/bin/bash

# Run tests for the Secure Enterprise Knowledge Hub API
# Usage: ./test.sh

echo "🧪 Running tests for Secure Enterprise Knowledge Hub API..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    # Try Windows path first (Git Bash on Windows)
    if [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    # Fall back to Unix path (Linux/Mac)
    elif [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
fi

# Set test environment variables
export API_KEY="test-api-key-12345"
export ENVIRONMENT="test"

# Add current directory to PYTHONPATH so tests can find the app module
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run pytest with coverage
echo "📊 Running tests with coverage..."
pytest tests/ -v --cov=app --cov=observability --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Tests complete!"
echo "📈 Coverage report generated in htmlcov/index.html"