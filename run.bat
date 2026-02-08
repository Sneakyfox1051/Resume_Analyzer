@echo off
echo ========================================
echo HR Automation Pipeline - Server Startup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "myenv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv myenv
    pause
    exit /b 1
)

echo Starting server...
echo.
echo Server will be available at: http://127.0.0.1:8000
echo API Docs will be at: http://127.0.0.1:8000/docs
echo.
echo Press CTRL+C to stop the server
echo.

REM Run uvicorn with virtual environment Python
call myenv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause
