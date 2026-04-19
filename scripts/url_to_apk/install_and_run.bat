@echo off
chcp 65001 >nul 2>&1
title URL to APK Converter v2.0
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║               URL to APK Converter v2.0.0                        ║
echo ║                                                                  ║
echo ║         Convert any website to Android APK                       ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Check for Python
echo [STEP 1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════╗
    echo ║  ERROR: Python is not installed!                                 ║
    echo ╠══════════════════════════════════════════════════════════════════╣
    echo ║                                                                  ║
    echo ║  Please install Python from:                                     ║
    echo ║  https://www.python.org/downloads/                               ║
    echo ║                                                                  ║
    echo ║  IMPORTANT: Check "Add Python to PATH" during installation!     ║
    echo ║                                                                  ║
    echo ╚══════════════════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo          [OK] Python %PYVER% found
echo.

:: Check pip
echo [STEP 2/4] Checking pip package manager...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo          [INFO] Installing pip...
    python -m ensurepip --upgrade >nul 2>&1
    if errorlevel 1 (
        echo          [ERROR] Could not install pip!
        pause
        exit /b 1
    )
)
echo          [OK] pip is available
echo.

:: Upgrade pip silently
echo [STEP 3/4] Installing dependencies...
echo.
echo          Installing: customtkinter (UI framework)
python -m pip install customtkinter --upgrade -q 2>nul
if errorlevel 1 (
    echo          [ERROR] Failed to install customtkinter
    goto :install_error
)
echo          [OK] customtkinter installed

echo          Installing: requests (HTTP client)
python -m pip install requests --upgrade -q 2>nul
if errorlevel 1 (
    echo          [ERROR] Failed to install requests
    goto :install_error
)
echo          [OK] requests installed

echo          Installing: beautifulsoup4 (HTML parser)
python -m pip install beautifulsoup4 --upgrade -q 2>nul
if errorlevel 1 (
    echo          [ERROR] Failed to install beautifulsoup4
    goto :install_error
)
echo          [OK] beautifulsoup4 installed

echo          Installing: Pillow (Image processing)
python -m pip install Pillow --upgrade -q 2>nul
if errorlevel 1 (
    echo          [ERROR] Failed to install Pillow
    goto :install_error
)
echo          [OK] Pillow installed

echo.
echo          All dependencies installed successfully!
echo.

:: Run the application
echo [STEP 4/4] Starting application...
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                   Launching URL to APK Converter                 ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"
python main.py

if errorlevel 1 (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════╗
    echo ║  APPLICATION ERROR                                               ║
    echo ╠══════════════════════════════════════════════════════════════════╣
    echo ║  The application encountered an error.                           ║
    echo ║  Check the error message above for details.                      ║
    echo ║                                                                  ║
    echo ║  Common solutions:                                               ║
    echo ║  1. Run as Administrator                                         ║
    echo ║  2. Check internet connection                                    ║
    echo ║  3. Reinstall Python with "Add to PATH" checked                 ║
    echo ╚══════════════════════════════════════════════════════════════════╝
    echo.
    pause
)
goto :eof

:install_error
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║  INSTALLATION ERROR                                              ║
echo ╠══════════════════════════════════════════════════════════════════╣
echo ║  Failed to install required packages.                            ║
echo ║                                                                  ║
echo ║  Try these solutions:                                            ║
echo ║  1. Check your internet connection                               ║
echo ║  2. Run Command Prompt as Administrator                          ║
echo ║  3. Try manually: pip install customtkinter requests             ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
pause
exit /b 1
