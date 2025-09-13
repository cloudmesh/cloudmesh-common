@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM -------------------------------------------------------------
REM Resolve Chocolatey path (no reliance on PATH)
REM -------------------------------------------------------------
set "CHOCO="
set "CHOCOROOT="

REM Try Machine scope ChocolateyInstall
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command ^
  "$m=[Environment]::GetEnvironmentVariable('ChocolateyInstall','Machine'); if([string]::IsNullOrWhiteSpace($m)){''} else {$m}"`) do (
  set "CHOCOROOT=%%I"
)

REM Fallback: User scope ChocolateyInstall
if not defined CHOCOROOT (
  for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command ^
    "$u=[Environment]::GetEnvironmentVariable('ChocolateyInstall','User'); if([string]::IsNullOrWhiteSpace($u)){''} else {$u}"`) do (
    set "CHOCOROOT=%%I"
  )
)

REM Fallback: default install location (use ProgramData, not hard-coded C:)
if not defined CHOCOROOT set "CHOCOROOT=%ProgramData%\Chocolatey"

REM If choco.exe exists there, use it
if exist "%CHOCOROOT%\bin\choco.exe" set "CHOCO=%CHOCOROOT%\bin\choco.exe"

REM As a last resort, try PATH (doesn't break if it's already on PATH)
if not defined CHOCO (
  for /f "delims=" %%I in ('where choco 2^>nul') do set "CHOCO=%%~fI"
)

REM -------------------------------------------------------------
REM Install Chocolatey if still not found
REM -------------------------------------------------------------
if not defined CHOCO (
  echo Chocolatey is not installed. Installing Chocolatey...
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    REM Re-resolve after install
    set "CHOCOROOT=%ProgramData%\Chocolatey"
    if exist "%CHOCOROOT%\bin\choco.exe" (
    set "CHOCO=%CHOCOROOT%\bin\choco.exe"
    ) else (
    for /f "usebackq delims=" %%I in (`
        powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('ChocolateyInstall','Machine') ?? ''"
    `) do set "CHOCOROOT=%%I"
    if exist "%CHOCOROOT%\bin\choco.exe" set "CHOCO=%CHOCOROOT%\bin\choco.exe"
    )
)

if not exist "%CHOCO%" (
  echo ERROR: Could not locate choco.exe after installation.
  exit /b 1
)

echo Using Chocolatey: "%CHOCO%"
echo.

REM -------------------------------------------------------------
REM Check/install Python
REM -------------------------------------------------------------
where python >nul 2>nul
if errorlevel 1 (
  echo Python is not on PATH. Installing Python...
  "%CHOCO%" install python -y
) else (
  echo Python is already available.
)

REM -------------------------------------------------------------
REM Check/install Git
REM -------------------------------------------------------------
where git >nul 2>nul
if errorlevel 1 (
  echo Git is not on PATH. Installing Git...
  "%CHOCO%" install git.install --params "/GitAndUnixToolsOnPath /Editor:Nano /PseudoConsoleSupport /NoAutoCrlf" -y
) else (
  echo Git is already available.
)

REM -------------------------------------------------------------
REM Check/install Cygwin (cygcheck in PATH means it's present)
REM -------------------------------------------------------------
where cygcheck >nul 2>nul
if errorlevel 1 (
  echo Cygwin is not on PATH. Installing Cygwin...
  "%CHOCO%" install cygwin -y
) else (
  echo Cygwin is already available.
)

REM -------------------------------------------------------------
REM Countdown + refresh environment in THIS window
REM -------------------------------------------------------------
echo.
echo cloudmesh has all required dependencies. Starting in 5 seconds...
for /l %%i in (5,-1,1) do (
  echo %%i
  timeout /t 1 >nul
)

if exist "%CHOCOROOT%\bin\refreshenv.cmd" (
  call "%CHOCOROOT%\bin\refreshenv.cmd"
) else (
  set "PATH=%PATH%;%CHOCOROOT%\bin"
)

REM --- snapshot refreshed values while SETLOCAL is active ---
set "PATH_SNAP=!PATH!"
set "CHOCO_SNAP=%CHOCOROOT%"

REM --- propagate to the caller after ENDLOCAL ---
ENDLOCAL & (
  set "PATH=%PATH_SNAP%"
  if not defined ChocolateyInstall set "ChocolateyInstall=%CHOCO_SNAP%"
)
