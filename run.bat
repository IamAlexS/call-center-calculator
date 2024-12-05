@echo off
echo Starting Call Center Calculator...

:: Check if venv exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b
)

:: Activate virtual environment
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b
)

:: Run the application
echo Opening calculator in your default browser...
streamlit run src/app.py --server.address localhost --server.port 8501

pause 