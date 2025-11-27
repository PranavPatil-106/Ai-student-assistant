@echo off
echo ============================================
echo AI-Powered Student Learning Assistant
echo Starting All Services
echo ============================================
echo.

cd /d "%~dp0"

echo Checking if virtual environment exists...
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo Initializing database...
cd backend
python init_db.py
cd ..

echo.
echo Checking HuggingFace model...
cd backend
python download_model.py
cd ..

echo.
echo Starting Backend API (FastAPI)...
start "Backend API" cmd /k "cd /d %CD%\venv\Scripts && activate.bat && cd /d %CD%\backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 5 /nobreak > nul

echo Starting Frontend (Streamlit)...
start "Frontend Streamlit" cmd /k "cd /d %CD%\venv\Scripts && activate.bat && cd /d %CD%\frontend && python -m streamlit run streamlit_app.py --server.port 8501"

echo.
echo ============================================
echo All services started!
echo ============================================
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo ============================================
echo.
echo Press any key to close this window
echo (Services will continue running in separate windows)
pause > nul