@echo off
SETLOCAL

REM Check if Chocolatey is installed
choco --version 2>nul
if %errorlevel% neq 0 (
    echo Chocolatey is not installed. Installing Chocolatey...
    @powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
) else (
    echo Chocolatey is already installed.
)

REM Check if Python is installed
python --version 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    choco install python -y
) else (
    echo Python is already installed.
)

REM Check if Git is installed
git --version 2>nul
if %errorlevel% neq 0 (
    echo Git is not installed. Installing Git...
    choco install git.install --params "/GitAndUnixToolsOnPath /Editor:Nano /PseudoConsoleSupport /NoAutoCrlf" -y
) else (
    echo Git is already installed.
)

REM Check if cygwin is installed
cygcheck -V 2>nul
if %errorlevel% neq 0 (
    echo cygwin is not installed. Installing cygwin...
    choco install cygwin -y
) else (
    echo cygwin is already installed.
)

refreshenv

REM Countdown from 5
echo cloudmesh has all required dependencies. Starting in 5 seconds...

for /l %%i in (5,-1,1) do (
    echo %%i
    timeout /t 1 >nul
)


ENDLOCAL