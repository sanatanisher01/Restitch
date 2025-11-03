@echo off
echo ========================================
echo    ReStitch - Sustainable Fashion Platform
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Attempting to install...
    echo.
    
    REM Try winget first (Windows 10/11)
    winget install Python.Python.3.11 --silent >nul 2>&1
    if not errorlevel 1 (
        echo Python installed via winget. Please restart this script.
        pause
        exit /b 0
    )
    
    REM Try chocolatey
    choco install python --version=3.11.6 -y >nul 2>&1
    if not errorlevel 1 (
        echo Python installed via chocolatey. Please restart this script.
        pause
        exit /b 0
    )
    
    REM Manual download as fallback
    echo Downloading Python installer...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe
    if errorlevel 1 (
        echo ERROR: Cannot download Python. Please install Python manually from python.org
        pause
        exit /b 1
    )
    
    echo Installing Python...
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo Python installed. Please restart this script.
    pause
    exit /b 0
)

echo Python found!
echo.

echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [3/4] Setting up database...
python fix_db.py
if errorlevel 1 (
    echo Trying alternative database setup...
    python seed.py
    if errorlevel 1 (
        echo WARNING: Database setup had issues, but continuing...
    )
)

echo [4/4] Starting ReStitch application...
echo.
echo ========================================
echo   ReStitch is starting...
echo   Open your browser and go to:
echo   http://localhost:5000
echo.
echo   Login Credentials:
echo   Admin: admin@restitch.com / admin123
echo   User:  priya@example.com / password123
echo ========================================
echo.

start http://localhost:5000
python restitch.py