@echo off
echo ========================================
echo    ASURA - AI SecureLab Setup v0.3.0
echo ========================================
echo.
echo This script will:
echo 1. Check prerequisites (Python, Node.js)
echo 2. Create Python virtual environment
echo 3. Install backend dependencies
echo 4. Install frontend dependencies
echo 5. Create .env file from template
echo.
echo Time estimate: 3-5 minutes
echo.
pause

echo.
echo [0/5] Checking prerequisites...
echo.

echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11 or higher from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo ✓ Python is installed

echo.
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js 18 or higher from https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo ✓ Node.js is installed

echo.
echo [1/5] Creating Python virtual environment...
cd backend
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created

echo.
echo [2/5] Installing backend dependencies...
call venv\Scripts\activate
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
echo ✓ Backend dependencies installed

cd ..

echo.
echo [3/5] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
echo ✓ Frontend dependencies installed

cd ..

echo.
echo [4/5] Setting up environment file...
cd backend
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env >nul
    echo ✓ .env file created
    echo.
    echo IMPORTANT: To enable AI features (optional):
    echo   1. Get free API key from https://openrouter.ai
    echo   2. Edit backend\.env
    echo   3. Add: OPENROUTER_API_KEY=your-key-here
) else (
    echo ✓ .env file already exists
)
cd ..

echo.
echo [5/5] Creating necessary directories...
if not exist backend\logs mkdir backend\logs
if not exist backend\logs\scans mkdir backend\logs\scans
echo ✓ Directories created

echo.
echo ========================================
echo    Setup Complete! 🎉
echo ========================================
echo.
echo ========================================
echo    Next Steps:
echo ========================================
echo.
echo ✅ Backend dependencies installed
echo ✅ Frontend dependencies installed
echo ✅ Environment configured
echo.
echo ========================================
echo    Next Steps:
echo ========================================
echo.
echo To start ASURA:
echo   1. Run: start.bat
echo   2. Backend will open at: http://localhost:8000
echo   3. Frontend will open at: http://localhost:5173
echo.
echo For manual start:
echo   Terminal 1: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo   Terminal 2: cd frontend ^&^& npm run dev
echo.
echo Documentation:
echo   - README.md - Project overview
echo   - QUICK_START.md - Usage guide
echo   - CONTRIBUTING.md - How to contribute
echo.
echo Optional AI Features:
echo   - Get API key: https://openrouter.ai
echo   - Edit: backend\.env
echo   - Add: OPENROUTER_API_KEY=your-key
echo.
echo ========================================
echo.
pause
