@echo off
echo Audio Downloader - Installation
echo ==============================
echo.

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.6 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

:: Install required packages
echo Installing required packages...
python -m pip install --upgrade pip
pip install -r audio_downloader_requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install required packages.
    echo.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

:: Create desktop shortcut
echo Creating desktop shortcut...
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
if %errorlevel% neq 0 (
    echo Failed to create desktop shortcut.
    echo.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

echo.
echo Installation completed successfully!
echo You can now run Audio Downloader from your desktop.
echo.
echo Press any key to exit...
pause > nul
exit /b 0 