#!/bin/bash

echo "========================================"
echo "   ASURA - AI SecureLab v0.3.0"
echo "   Starting Backend and Frontend"
echo "========================================"
echo ""
echo "Performing startup checks..."
echo ""

# Check Python
echo "[1/5] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found!"
    echo "Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi
python3 --version
echo "✓ Python found"

# Check Node.js
echo ""
echo "[2/5] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found!"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi
node --version
echo "✓ Node.js found"

# Check virtual environment
echo ""
echo "[3/5] Checking virtual environment..."
if [ ! -d "backend/venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi
echo "✓ Virtual environment found"

# Check dependencies
echo ""
echo "[4/5] Checking dependencies..."
if [ ! -d "frontend/node_modules" ]; then
    echo "WARNING: Frontend dependencies not installed"
    echo "Please run ./setup.sh first"
    exit 1
fi
echo "✓ Dependencies installed"

# Start services
echo ""
echo "[5/5] Starting services..."
echo ""

# Detect terminal emulator
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Starting Backend Server..."
    osascript -e 'tell app "Terminal" to do script "cd '"$PWD"'/backend && source venv/bin/activate && echo \"\" && echo \"========================================\" && echo \"   ASURA Backend Server\" && echo \"========================================\" && echo \"\" && uvicorn app.main:app --reload --reload-dir app --reload-exclude \"tests/*\""'
    
    sleep 3
    
    echo "Starting Frontend Server..."
    osascript -e 'tell app "Terminal" to do script "cd '"$PWD"'/frontend && echo \"\" && echo \"========================================\" && echo \"   ASURA Frontend Server\" && echo \"========================================\" && echo \"\" && npm run dev"'
    
elif command -v gnome-terminal &> /dev/null; then
    # Linux with GNOME Terminal
    echo "Starting Backend Server..."
    gnome-terminal --title="ASURA Backend - http://localhost:8000" -- bash -c "cd $PWD/backend && source venv/bin/activate && echo '' && echo '========================================' && echo '   ASURA Backend Server' && echo '========================================' && echo '' && uvicorn app.main:app --reload --reload-dir app --reload-exclude 'tests/*'; exec bash"
    
    sleep 3
    
    echo "Starting Frontend Server..."
    gnome-terminal --title="ASURA Frontend - http://localhost:5173" -- bash -c "cd $PWD/frontend && echo '' && echo '========================================' && echo '   ASURA Frontend Server' && echo '========================================' && echo '' && npm run dev; exec bash"
    
elif command -v konsole &> /dev/null; then
    # Linux with KDE Konsole
    echo "Starting Backend Server..."
    konsole --title "ASURA Backend - http://localhost:8000" -e bash -c "cd $PWD/backend && source venv/bin/activate && echo '' && echo '========================================' && echo '   ASURA Backend Server' && echo '========================================' && echo '' && uvicorn app.main:app --reload --reload-dir app --reload-exclude 'tests/*'; exec bash" &
    
    sleep 3
    
    echo "Starting Frontend Server..."
    konsole --title "ASURA Frontend - http://localhost:5173" -e bash -c "cd $PWD/frontend && echo '' && echo '========================================' && echo '   ASURA Frontend Server' && echo '========================================' && echo '' && npm run dev; exec bash" &
    
elif command -v xterm &> /dev/null; then
    # Linux with xterm
    echo "Starting Backend Server..."
    xterm -title "ASURA Backend - http://localhost:8000" -e bash -c "cd $PWD/backend && source venv/bin/activate && echo '' && echo '========================================' && echo '   ASURA Backend Server' && echo '========================================' && echo '' && uvicorn app.main:app --reload --reload-dir app --reload-exclude 'tests/*'; exec bash" &
    
    sleep 3
    
    echo "Starting Frontend Server..."
    xterm -title "ASURA Frontend - http://localhost:5173" -e bash -c "cd $PWD/frontend && echo '' && echo '========================================' && echo '   ASURA Frontend Server' && echo '========================================' && echo '' && npm run dev; exec bash" &
    
else
    # Fallback - run in background
    echo "No supported terminal emulator detected. Running in background..."
    echo ""
    echo "Starting Backend Server..."
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --reload-dir app --reload-exclude "tests/*" > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    echo "Starting Frontend Server..."
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "Backend PID: $BACKEND_PID (logs: backend.log)"
    echo "Frontend PID: $FRONTEND_PID (logs: frontend.log)"
    echo ""
    echo "To stop services:"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
fi

echo ""
echo "========================================"
echo "   ASURA Started Successfully! 🚀"
echo "========================================"
echo ""
echo "✅ Backend:  http://localhost:8000"
echo "✅ Frontend: http://localhost:5173"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
if [[ "$OSTYPE" != "darwin"* ]] && ! command -v gnome-terminal &> /dev/null && ! command -v konsole &> /dev/null && ! command -v xterm &> /dev/null; then
    echo "Services are running in background."
    echo "Check backend.log and frontend.log for output."
else
    echo "Two new terminal windows have opened:"
    echo "  1. Backend Server (FastAPI)"
    echo "  2. Frontend Server (Vite + React)"
fi
echo ""
echo "🛡️  Wait 10-15 seconds for servers to fully start"
echo "🌐 Then open: http://localhost:5173 in your browser"
echo ""
echo "To stop ASURA:"
if [[ "$OSTYPE" != "darwin"* ]] && ! command -v gnome-terminal &> /dev/null && ! command -v konsole &> /dev/null && ! command -v xterm &> /dev/null; then
    echo "  - Run: kill $BACKEND_PID $FRONTEND_PID"
else
    echo "  - Close both terminal windows"
    echo "  - Or press Ctrl+C in each window"
fi
echo ""
echo "Need help?"
echo "  - See QUICK_START.md"
echo "  - Check README.md"
echo "  - Report issues on GitHub"
echo ""
echo "========================================"
echo ""
