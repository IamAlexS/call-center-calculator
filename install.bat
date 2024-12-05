@echo off
echo ====================================
echo Call Center Calculator Installation
echo ====================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Installing Python 3.8...
    
    :: Download Python installer
    curl -o python-3.8.10-amd64.exe https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
    
    :: Install Python silently with PATH option enabled
    python-3.8.10-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Delete installer
    del python-3.8.10-amd64.exe
    
    :: Refresh environment variables
    call RefreshEnv.cmd
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b
    )
)

:: Activate virtual environment and install requirements
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b
)

echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b
)

echo Installation completed successfully!
echo Please use run.bat to start the calculator
pause 