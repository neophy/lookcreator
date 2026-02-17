@echo off
REM Look Creator - Quick Start Script for Windows

echo.
echo ================================
echo Look Creator - Quick Start
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python found

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo [!] .env file not found
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo [!] IMPORTANT: Please edit the .env file and add your ANTHROPIC_API_KEY
    echo     You can get your API key from: https://console.anthropic.com/
    echo.
    echo     After adding your API key, run this script again.
    pause
    exit /b 1
)

REM Load environment variables
echo Loading environment variables...
for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do set %%a

REM Check if API key is set
if "%ANTHROPIC_API_KEY%"=="" (
    echo [X] ANTHROPIC_API_KEY is not set in .env file
    echo     Please edit .env and add your API key
    pause
    exit /b 1
)

if "%ANTHROPIC_API_KEY%"=="your_api_key_here" (
    echo [X] ANTHROPIC_API_KEY is not set in .env file
    echo     Please edit .env and add your API key
    pause
    exit /b 1
)

echo [OK] API key found
echo.
echo ================================
echo Setup complete! Starting app...
echo ================================
echo.
echo The app will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the app
echo.

REM Run Streamlit
streamlit run app.py
