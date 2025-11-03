#!/bin/bash

# Azure App Service startup script
echo "Starting Disease Prediction API on Azure..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install gunicorn

# Start the application
echo "Starting Gunicorn server..."
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 600
