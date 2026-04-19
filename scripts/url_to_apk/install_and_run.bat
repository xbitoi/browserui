@echo off
title URL to APK Converter - Setup
color 0A

echo ============================================
echo   URL to APK Converter - Installation
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python 3.10+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo [OK] Python found!
python --version
echo.

:: Check pip
echo [INFO] Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing pip...
    python -m ensurepip --upgrade
)

echo.
echo [INFO] Installing required packages...
echo.

:: Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install some packages!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo Starting URL to APK Converter...
echo.

:: Run the application
python main.py

pause
