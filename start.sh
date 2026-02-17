#!/bin/bash

# Look Creator - Quick Start Script

echo "🚀 Look Creator - Quick Start"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your ANTHROPIC_API_KEY"
    echo "   You can get your API key from: https://console.anthropic.com/"
    echo ""
    echo "   After adding your API key, run this script again."
    exit 1
fi

# Load environment variables
echo "🔐 Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_api_key_here" ]; then
    echo "❌ ANTHROPIC_API_KEY is not set in .env file"
    echo "   Please edit .env and add your API key"
    exit 1
fi

echo "✅ API key found"
echo ""
echo "🎉 Setup complete! Starting Streamlit app..."
echo "   The app will open in your browser at http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop the app"
echo ""

# Run Streamlit
streamlit run app.py
