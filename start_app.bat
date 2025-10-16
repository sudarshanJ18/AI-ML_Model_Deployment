@echo off
echo ========================================
echo Starting Face Recognition Application
echo ========================================

echo.
echo 1. Installing Backend Dependencies...
cd backend
pip install fastapi uvicorn python-multipart pydantic
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo 2. Starting Backend Server...
start "Backend Server" cmd /k "python main.py"
cd ..

echo.
echo 3. Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo 4. Installing Frontend Dependencies...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo 5. Starting Frontend Server...
start "Frontend Server" cmd /k "npm start"
cd ..

echo.
echo ========================================
echo Both servers are starting...
echo.
echo Backend API: http://localhost:8001
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8001/docs
echo.
echo Wait for both servers to fully start before testing!
echo ========================================
pause
