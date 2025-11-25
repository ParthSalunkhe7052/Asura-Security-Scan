@echo off
echo ========================================
echo    ASURA - AI SecureLab v0.3.0
echo    Starting Backend and Frontend
echo ========================================
echo.
echo Performing startup checks...
echo.

echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo ✓ Python found

echo.
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo ✓ Node.js found

echo.
echo [3/5] Checking virtual environment...
if not exist backend\venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)
echo ✓ Virtual environment found

echo.
echo [4/5] Checking dependencies...
if not exist frontend\node_modules (
    echo WARNING: Frontend dependencies not installed
    echo Please run setup.bat first
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [5/5] Starting services...
echo.
echo Starting Backend Server...
start "ASURA Backend - http://localhost:8000" cmd /k "cd backend && .\venv\Scripts\activate && echo. && echo ======================================== && echo    ASURA Backend Server && echo ======================================== && echo. && uvicorn app.main:app --reload --reload-dir app"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "ASURA Frontend - http://localhost:5173" cmd /k "cd frontend && echo. && echo ======================================== && echo    ASURA Frontend Server && echo ======================================== && echo. && npm run dev"

echo.
echo ========================================
echo    ASURA Started Successfully! 🚀
echo ========================================
echo.
echo ✅ Backend:  http://localhost:8000
echo ✅ Frontend: http://localhost:5173  
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Two new windows have opened:
echo   1. Backend Server (FastAPI)
echo   2. Frontend Server (Vite + React)
echo.
echo 🛡️  Wait 10-15 seconds for servers to fully start
echo 🌐 Then open: http://localhost:5173 in your browser
echo.
echo To stop ASURA:
echo   - Close both terminal windows
echo   - Or press Ctrl+C in each window
echo.
echo Need help?
echo   - See QUICK_START.md
echo   - Check README.md
echo   - Report issues on GitHub
echo.
echo ========================================
echo.
echo Press any key to close this launcher window...
echo (The backend and frontend will keep running)
pause > nul
