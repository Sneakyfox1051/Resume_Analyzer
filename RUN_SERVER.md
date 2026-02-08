# How to Run the Server

## The Problem
When you run `uvicorn` directly, it might use the system Python instead of your virtual environment, causing "ModuleNotFoundError" errors.

## Solution: Use Virtual Environment Python

### Method 1: Activate Virtual Environment First (Recommended)
```powershell
# Activate virtual environment
.\myenv\Scripts\Activate.ps1

# Then run uvicorn normally
uvicorn app.main:app --reload
```

### Method 2: Use Virtual Environment Python Directly
```powershell
.\myenv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Method 3: Create a Batch Script
Create a file `run_server.bat`:
```batch
@echo off
call myenv\Scripts\activate.bat
uvicorn app.main:app --reload
```

Then just run:
```powershell
.\run_server.bat
```

## Verify You're Using the Right Python

Check which Python is being used:
```powershell
where python
```

Should show: `D:\Downloads\HR_automationPipeline_agentic_ai\myenv\Scripts\python.exe`

If it shows a different path, activate the virtual environment first!

## Access the Application

Once running, access:
- **Web Interface**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc
