@echo off
echo Starting Call Center Calculator...

:: Activate virtual environment
call venv\Scripts\activate

:: Run the application
streamlit run src/app.py --server.address localhost --server.port 8501

pause 