@echo off
echo ========================================
echo   Chat App - Database Version
echo ========================================
echo.
echo Starting backend server with SQLite database...
echo Database file: chatapp.db
echo API URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python -m uvicorn main_with_db:app --host 0.0.0.0 --port 8000 --reload
