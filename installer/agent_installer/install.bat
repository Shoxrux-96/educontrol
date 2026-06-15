@echo off
echo === EDU Control Pro - Agent Installer ===
echo.

REM Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Please run as Administrator!
    pause
    exit /b 1
)

set SERVER_URL=https://localhost:8000/ws/agent
set API_KEY=default-key

if not "%1"=="" set SERVER_URL=%1
if not "%2"=="" set API_KEY=%2

echo Server: %SERVER_URL%
echo Installing agent...
cd /d "%~dp0..\..\client_agent"

python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

setx SERVER_URL "%SERVER_URL%" /M
setx API_KEY "%API_KEY%" /M

python main.py install
python main.py start

echo.
echo Agent installed successfully!
pause
