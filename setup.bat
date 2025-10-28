@echo off
REM Setup script for Power BI Automation (Windows)

echo ======================================
echo Power BI Automation - Setup Script
echo ======================================
echo.

REM Check Python version
echo Checking Python version...
python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

REM Install Playwright browsers
echo.
echo Installing Playwright browsers...
playwright install chromium

REM Create .env from example
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy env.example .env
    echo ✅ .env file created. Please edit it with your credentials.
) else (
    echo.
    echo ⚠️  .env file already exists, skipping...
)

REM Create necessary directories
echo.
echo Creating necessary directories...
if not exist downloads mkdir downloads
if not exist output mkdir output
if not exist logs mkdir logs

echo.
echo ======================================
echo ✅ Setup complete!
echo ======================================
echo.
echo Next steps:
echo 1. Edit the .env file with your credentials
echo 2. Activate the virtual environment: venv\Scripts\activate
echo 3. Run the application: streamlit run main.py
echo.
echo For help, see README.md
echo.
pause

