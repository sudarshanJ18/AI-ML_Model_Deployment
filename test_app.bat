@echo off
echo ========================================
echo Testing Face Recognition Application
echo ========================================

echo.
echo Testing Backend API...
curl -s http://localhost:8001/health
if %errorlevel% equ 0 (
    echo ✅ Backend is running on port 8001
) else (
    echo ❌ Backend is not responding on port 8001
    echo Please make sure the backend is running!
)

echo.
echo Testing Frontend...
curl -s http://localhost:3000
if %errorlevel% equ 0 (
    echo ✅ Frontend is running on port 3000
) else (
    echo ❌ Frontend is not responding on port 3000
    echo Please make sure the frontend is running!
)

echo.
echo ========================================
echo Test completed!
echo.
echo If both services are running, open:
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8001/docs
echo ========================================
pause