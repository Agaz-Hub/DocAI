@echo off
REM Production Startup Script for Windows
echo ====================================
echo Disease Prediction API - PRODUCTION
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "myenv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv myenv
)

REM Activate virtual environment
echo Activating virtual environment...
call myenv\Scripts\activate.bat

REM Install production dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install -r requirements-prod.txt

REM Set production environment
set ENVIRONMENT=production
set HOST=0.0.0.0
set PORT=8000

REM Start with Gunicorn (production-grade server)
echo.
echo ====================================
echo Starting in PRODUCTION mode...
echo Using Gunicorn for better performance
echo ====================================
echo.
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
