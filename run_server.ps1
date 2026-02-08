# Run Server Script for HR Automation Pipeline
# This ensures the server runs with the correct virtual environment

Write-Host "Starting HR Automation Pipeline Server..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "myenv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv myenv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment and run server
Write-Host "Using virtual environment Python..." -ForegroundColor Cyan
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Docs will be at: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run uvicorn with virtual environment Python
& "myenv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
