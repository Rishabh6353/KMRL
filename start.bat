@echo off
echo ==========================================================
echo     INTELLIGENT DOCUMENT PROCESSING SYSTEM
echo ==========================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Installing core dependencies...
echo.

REM Install minimal dependencies first
pip install Flask flask-cors flask-sqlalchemy python-dotenv requests

REM Try to install image processing packages
echo Installing image processing packages...
pip install pytesseract
pip install Pillow

REM Try optional packages
echo Installing optional packages...
pip install pandas numpy scikit-learn --quiet

echo.
echo Setup complete! Starting the application...
echo.
echo Open your browser to: http://localhost:5000
echo.

REM Start the simplified application
python app_simple.py

pause