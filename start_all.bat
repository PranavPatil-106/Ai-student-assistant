@echo off
echo ============================================
echo AI-Powered Student Learning Assistant
echo Starting All Services
echo ============================================
echo.

cd /d "%~dp0"

echo Checking HuggingFace model...
call venv\Scripts\activate.bat
cd backend
python download_model.py
cd ..
echo.

echo Starting Backend API (FastAPI)...
start "Backend API" cmd /k "call venv\Scripts\activate.bat && cd backend && python main.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend (Streamlit)...
start "Frontend Streamlit" cmd /k "call venv\Scripts\activate.bat && cd frontend && streamlit run streamlit_app.py"

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
