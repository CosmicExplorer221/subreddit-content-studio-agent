# Troubleshooting Guide

## Backend Not Running

### Symptoms
- Frontend shows "ECONNREFUSED" errors
- API calls fail with 500 errors
- Cannot access http://localhost:8000

### Solutions

#### 1. Check if Backend is Running

**Windows:**
```bash
netstat -ano | findstr :8000
```

**Linux/Mac:**
```bash
lsof -i :8000
```

If nothing is returned, the backend is not running.

#### 2. Start Backend Manually

```bash
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize data (first time only)
python -m app.core.initialize

# Start server
python -m app.main
```

Backend should start at http://localhost:8000

#### 3. Check for Errors

Look for error messages in the terminal where backend is running:

**Common Issues:**

**Missing Dependencies:**
```
ModuleNotFoundError: No module named 'fastapi'
```
**Fix:** `pip install -r requirements.txt`

**Port Already in Use:**
```
OSError: [Errno 48] Address already in use
```
**Fix:** Kill process on port 8000
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

**Import Errors:**
```
ImportError: cannot import name 'get_storage'
```
**Fix:** Make sure you're in the `backend` directory when running commands

## Frontend Not Loading

### Symptoms
- Blank page
- "Cannot GET /" error
- Vite not starting

### Solutions

#### 1. Check if Frontend is Running

Frontend should be at http://localhost:3000

If not:
```bash
cd frontend
npm install
npm run dev
```

#### 2. Clear Cache and Reinstall

```bash
cd frontend
rm -rf node_modules .vite dist
npm install
npm run dev
```

#### 3. Check Node.js Version

```bash
node --version  # Should be 18+
npm --version
```

## Proxy Connection Issues

### Error: `connect ECONNREFUSED ::1:8000`

This is an IPv6 vs IPv4 issue.

**Already Fixed** in latest vite.config.ts using `127.0.0.1` instead of `localhost`

If still having issues:
1. Restart frontend: `npm run dev`
2. Make sure backend is running on `http://127.0.0.1:8000`

## API Errors

### 500 Internal Server Error

Check backend logs for the actual error. Common causes:

1. **Missing API Keys** - Configure in `backend/.env`
2. **Invalid Data** - Check `backend/data/` files are valid JSON
3. **Import Errors** - Reinstall dependencies

### 404 Not Found

- Backend is running but endpoint doesn't exist
- Check API docs at http://localhost:8000/api/docs

### 503 Service Unavailable

- Service not configured (e.g., Gemini, Notion)
- Add API keys to `backend/.env`

## Database/Storage Issues

### No Categories or Templates

Run initialization:
```bash
cd backend
python -m app.core.initialize
```

This creates:
- Railway category
- Professional template
- Default settings

### JSON Decode Errors

Check for corrupted JSON files:
```bash
cd backend/data/categories
python -m json.tool railway.json
```

If invalid, delete and re-initialize.

## Quick Verification

Run the verification script:
```bash
python verify_backend.py
```

This checks:
- Python version
- Data directory
- FastAPI imports
- Dependencies

## Complete Reset

If all else fails, start fresh:

```bash
# Backend
cd backend
rm -rf venv data
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
python -m app.core.initialize
python -m app.main

# Frontend (in new terminal)
cd frontend
rm -rf node_modules dist .vite
npm install
npm run dev
```

## Getting Help

1. Check backend logs for specific errors
2. Check frontend console (F12 in browser)
3. Verify all dependencies are installed
4. Make sure ports 3000 and 8000 are available
5. Try accessing backend directly: http://localhost:8000/api/health

## Environment Setup Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend initialized (`python -m app.core.initialize`)
- [ ] API keys configured in `backend/.env`
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
