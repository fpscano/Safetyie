@echo off
color 0A
cls
echo ═══════════════════════════════════════════════════════════
echo     WELCOME TO SECRET SAUCE - SIE PROJECT
echo ═══════════════════════════════════════════════════════════
echo.
echo Opening important files...
echo.
echo 1. PROJECT_MAP.txt ......... Project structure overview
echo 2. GETTING_STARTED.md ...... Quick start guide
echo 3. README.md ............... Full documentation
echo.

start notepad "PROJECT_MAP.txt"
timeout /t 1 /nobreak >nul
start "README" "README.md"
timeout /t 1 /nobreak >nul
start "Getting Started" "GETTING_STARTED.md"

echo.
echo ═══════════════════════════════════════════════════════════
echo     QUICK ACTIONS
echo ═══════════════════════════════════════════════════════════
echo.
echo What would you like to do?
echo.
echo [1] Test Locally (recommended first step)
echo [2] Open Website Folder
echo [3] Open Cano (Backend) Folder
echo [4] Open Diary Folder
echo [5] Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting local test server...
    cd cano
    powershell -ExecutionPolicy Bypass -File test-local.ps1
)

if "%choice%"=="2" (
    echo Opening website folder...
    explorer "website"
)

if "%choice%"=="3" (
    echo Opening cano folder...
    explorer "cano"
)

if "%choice%"=="4" (
    echo Opening diary folder...
    explorer "diary"
)

if "%choice%"=="5" (
    echo Goodbye!
    exit
)

pause
