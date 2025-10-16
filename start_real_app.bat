@echo off
echo ========================================
echo Starting Real Face Recognition App
echo ========================================

echo.
echo Installing ML dependencies...
cd backend
pip install -r requirements.txt

echo.
echo Starting the application...
python main.py

pause