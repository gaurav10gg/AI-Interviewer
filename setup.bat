@echo off
echo ============================================
echo AI Interview System - Windows Setup
echo ============================================
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Please ensure Python 3.8+ is installed
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Download spaCy model
echo Downloading spaCy language model...
python -m spacy download en_core_web_sm
if errorlevel 1 (
    echo ERROR: Failed to download spaCy model
    pause
    exit /b 1
)

REM Create __init__.py files
echo Creating package files...
type nul > backend\__init__.py
type nul > interview\__init__.py
type nul > evaluation\__init__.py
type nul > speech\__init__.py

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Install Ollama from: https://ollama.ai/download
echo 2. Start Ollama: ollama serve
echo 3. Pull model: ollama pull llama3
echo 4. Test system: python test_system.py
echo 5. Run server: python run.py
echo.
echo Then open browser at: http://localhost:8000
echo.
pause