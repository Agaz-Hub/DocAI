@echo off
echo ====================================
echo Disease Prediction API - Startup
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

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
)

REM Start the server
echo.
echo ====================================
echo Starting Disease Prediction API...
echo ====================================
echo.
python main.py
