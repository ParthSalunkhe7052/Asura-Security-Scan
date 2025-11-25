#!/bin/bash

# Exit on error
set -e

echo "========================================"
echo "   ASURA - AI SecureLab Setup v0.3.0"
echo "========================================"
echo ""
echo "This script will:"
echo "1. Check prerequisites (Python, Node.js)"
echo "2. Create Python virtual environment"
echo "3. Install backend dependencies"
echo "4. Install frontend dependencies"
echo "5. Create .env file from template"
echo ""
echo "Time estimate: 3-5 minutes"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "[0/5] Checking prerequisites..."
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found!"
    echo "Please install Python 3.11 or higher:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python@3.11"
    exit 1
fi
python3 --version
echo "✓ Python is installed"

# Check Node.js
echo ""
echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found!"
    echo "Please install Node.js 18 or higher:"
    echo "  Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install nodejs"
    echo "  macOS: brew install node"
    exit 1
fi
node --version
echo "✓ Node.js is installed"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm not found!"
    echo "Please install npm (usually comes with Node.js)"
    exit 1
fi
echo "✓ npm is installed"

# Create virtual environment
echo ""
echo "[1/5] Creating Python virtual environment..."
cd backend
python3 -m venv venv
echo "✓ Virtual environment created"

# Install backend dependencies
echo ""
echo "[2/5] Installing backend dependencies..."
source venv/bin/activate
echo "Upgrading pip..."
python -m pip install --upgrade pip
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Backend dependencies installed"

cd ..

# Install frontend dependencies
echo ""
echo "[3/5] Installing frontend dependencies..."
cd frontend
npm install
echo "✓ Frontend dependencies installed"

cd ..

# Setup .env file
echo ""
echo "[4/5] Setting up environment file..."
cd backend
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "IMPORTANT: To enable AI features (optional):"
    echo "  1. Get free API key from https://openrouter.ai"
    echo "  2. Edit backend/.env"
    echo "  3. Add: OPENROUTER_API_KEY=your-key-here"
else
    echo "✓ .env file already exists"
fi
cd ..

# Create directories
echo ""
echo "[5/5] Creating necessary directories..."
mkdir -p backend/logs/scans
echo "✓ Directories created"

echo ""
echo "========================================"
echo "   Setup Complete! 🎉"
echo "========================================"
echo ""
echo "========================================"
echo "   Next Steps:"
echo "========================================"
echo ""
echo "✅ Backend dependencies installed"
echo "✅ Frontend dependencies installed"
echo "✅ Environment configured"
echo ""
echo "========================================"
echo "   Next Steps:"
echo "========================================"
echo ""
echo "To start ASURA:"
echo "  1. Run: ./start.sh"
echo "  2. Backend will open at: http://localhost:8000"
echo "  3. Frontend will open at: http://localhost:5173"
echo ""
echo "For manual start:"
echo "  Terminal 1: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
echo "Documentation:"
echo "  - README.md - Project overview"
echo "  - QUICK_START.md - Usage guide"
echo "  - CONTRIBUTING.md - How to contribute"
echo ""
echo "Optional AI Features:"
echo "  - Get API key: https://openrouter.ai"
echo "  - Edit: backend/.env"
echo "  - Add: OPENROUTER_API_KEY=your-key"
echo ""
echo "========================================"
echo ""
