#!/bin/bash

echo "========================================"
echo "LinkedIn Content Automation Tool"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3.11+ and try again"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed${NC}"
    echo "Please install Node.js 18+ and try again"
    exit 1
fi

echo -e "${YELLOW}[1/4] Checking backend dependencies...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo -e "${YELLOW}[2/4] Activating virtual environment and installing dependencies...${NC}"
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo -e "${YELLOW}[3/4] Checking frontend dependencies...${NC}"
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install
fi

echo -e "${YELLOW}[4/4] Starting application...${NC}"
echo ""
echo "Backend will start at: http://localhost:8000"
echo "Frontend will start at: http://localhost:3000"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop all servers${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
cd ../backend
source venv/bin/activate
python -m app.main &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Application started successfully!"
echo "========================================"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/api/docs"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
