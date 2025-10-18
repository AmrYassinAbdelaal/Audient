#!/bin/bash

# Run Audient locally with uvicorn

set -e

echo "🚀 Starting Audient locally..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please update it with your API keys."
        exit 1
    else
        echo "❌ .env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created."
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set in .env file."
    exit 1
fi

echo "✅ Environment configured."
echo ""
echo "🌐 Starting server at http://localhost:${API_PORT:-8000}"
echo "📖 API docs available at http://localhost:${API_PORT:-8000}/docs"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

# Run the application
cd "$(dirname "$0")/.."
python -m uvicorn app.main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000} --reload
