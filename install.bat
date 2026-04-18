@echo off
title KAIROS Dreamweaver - Installer
echo Checking Python installation...

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.9 or newer from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found. Starting KAIROS installer...
echo.
python install.py

if errorlevel 1 (
    echo.
    echo Installation encountered an error.
    pause
)