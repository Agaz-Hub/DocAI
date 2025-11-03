#!/bin/bash
# Production Startup Script for Linux/Mac

echo "===================================="
echo "Disease Prediction API - PRODUCTION"
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

# Install production dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-prod.txt

# Set production environment
export ENVIRONMENT=production
export HOST=0.0.0.0
export PORT=8000

# Start with Gunicorn (production-grade server)
echo ""
echo "===================================="
echo "Starting in PRODUCTION mode..."
echo "Using Gunicorn for better performance"
echo "===================================="
echo ""
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
