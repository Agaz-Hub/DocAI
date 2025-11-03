#!/bin/bash

echo "===================================="
echo "Disease Prediction API - Startup"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "myenv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv myenv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source myenv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

# Start the server
echo ""
echo "===================================="
echo "Starting Disease Prediction API..."
echo "===================================="
echo ""
python main.py
