@echo off
echo Starting Atai Travel...

:: Start backend
start "Atai Backend" cmd /k "cd backend && pip install -r requirements.txt && python seed.py && uvicorn app.main:app --reload --port 8000"

:: Wait a moment then start frontend
timeout /t 5 /nobreak > NUL
start "Atai Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
