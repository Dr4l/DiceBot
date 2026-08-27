@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Could not create the virtual environment. Is Python installed and on PATH?
        exit /b 1
    )
)

set "NEED_SETUP="
if not exist ".env" (
    set "NEED_SETUP=1"
) else (
    findstr /b /r /c:"DISCORD_TOKEN=..*" ".env" >nul 2>&1
    if errorlevel 1 set "NEED_SETUP=1"
)

if defined NEED_SETUP (
    echo.
    set /p "DISCORD_TOKEN=Enter your Discord Bot Token (not Application ID or Server ID): "
    if not defined DISCORD_TOKEN (
        echo A token is required.
        exit /b 1
    )
    >".env" echo DISCORD_TOKEN=!DISCORD_TOKEN!
    echo Token saved to .env. It will not be requested again.
)

echo Installing or checking dependencies...
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
if errorlevel 1 exit /b 1

echo Starting bot...
".venv\Scripts\python.exe" bot.py