@echo off
REM GRINGO AI OS Launcher Script for Windows
REM Quick start script for GRINGO with all services

echo 🤖 Starting GRINGO AI OS...
echo ==========================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ first.
    echo 💡 Download from: https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 📦 Checking dependencies...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing dependencies...
    pip install -r requirements.txt
)

REM Check if Ollama is available (optional)
echo 🤖 Checking Ollama service...
where ollama >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama not found - AI features will be limited
    echo 💡 Install Ollama from https://ollama.ai for full AI capabilities
) else (
    echo ✅ Ollama found
    REM Note: Ollama service management differs on Windows
    echo 💡 Make sure Ollama service is running
)

REM Create workspace if it doesn't exist
if not exist "gringo_workspace" (
    echo 📁 Creating workspace...
    mkdir gringo_workspace\projects
    mkdir gringo_workspace\tools
    mkdir gringo_workspace\agents
    mkdir gringo_workspace\temp
    echo ✅ Workspace created
)

REM Find available port (simplified for Windows)
set PORT=8504

echo 🚀 Starting GRINGO on port %PORT%...
echo 🌐 Open your browser to: http://localhost:%PORT%
echo 💡 Press Ctrl+C to stop GRINGO
echo.

REM Start Streamlit
streamlit run ultimate_gringo.py --server.port %PORT% --server.headless true --server.runOnSave true

echo 👋 GRINGO stopped. Goodbye!
pause
