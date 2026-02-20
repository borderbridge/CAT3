#!/bin/bash

# CAT3 Start Script for Linux
# Catalog of Astronomical Things

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting CAT3..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

# Check for venv and create if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install/update requirements
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies..."
    pip install -q -r requirements.txt
fi

# Run CAT3
echo "🔭 Launching CAT3..."
python3 mainwindow.py
