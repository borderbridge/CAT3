@echo off
REM CAT3 Start Script for Windows
REM Catalog of Astronomical Things

setlocal enabledelayedexpansion

echo 🚀 Starting CAT3...

REM Check for Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.
    exit /b 1
)

REM Check for venv and create if needed
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install/update requirements
if exist "requirements.txt" (
    echo 📥 Installing dependencies...
    pip install -q -r requirements.txt
)

REM Run CAT3
echo 🔭 Launching CAT3...
python mainwindow.py

pause
