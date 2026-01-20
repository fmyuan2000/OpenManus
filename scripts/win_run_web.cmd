@echo off
setlocal

rem Run OpenManus web server within the conda env.
set "MINIFORGE_ROOT=C:\ProgramData\miniforge3"
set "ENV_NAME=open_manus"

if not exist "%MINIFORGE_ROOT%\Scripts\activate.bat" (
  echo [ERROR] Miniforge not found: "%MINIFORGE_ROOT%\Scripts\activate.bat"
  echo         Please edit MINIFORGE_ROOT in: %~f0
  exit /b 1
)

set "PROJECT_ROOT=%~dp0.."
for %%I in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fI"

call "%MINIFORGE_ROOT%\Scripts\activate.bat" "%MINIFORGE_ROOT%" || exit /b 1
call conda activate %ENV_NAME% || exit /b 1
cd /d "%PROJECT_ROOT%" || exit /b 1

python run_web.py

