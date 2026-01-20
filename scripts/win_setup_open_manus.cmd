@echo off
setlocal

rem One-time bootstrap for OpenManus on Windows using Miniforge.
set "MINIFORGE_ROOT=C:\ProgramData\miniforge3"
set "ENV_NAME=open_manus"
set "PY_VER=3.12"

if not exist "%MINIFORGE_ROOT%\Scripts\activate.bat" (
  echo [ERROR] Miniforge not found: "%MINIFORGE_ROOT%\Scripts\activate.bat"
  echo         Please edit MINIFORGE_ROOT in: %~f0
  exit /b 1
)

call "%MINIFORGE_ROOT%\Scripts\activate.bat" "%MINIFORGE_ROOT%" || exit /b 1

conda env list | findstr /r /c:"\b%ENV_NAME%\b" >nul
if errorlevel 1 (
  echo [INFO] Creating conda env: %ENV_NAME% (python=%PY_VER%)
  conda create -n %ENV_NAME% python=%PY_VER% -y || exit /b 1
)

call conda activate %ENV_NAME% || exit /b 1

echo [INFO] Installing Python deps...
python -m pip install -U pip || exit /b 1
python -m pip install -r "%~dp0..\requirements.txt" || exit /b 1
python -m pip install -e "%~dp0.." --no-deps || exit /b 1

echo [INFO] Installing Playwright browser (chromium only)...
python -m playwright install chromium || exit /b 1

echo [OK] Environment ready: %ENV_NAME%
echo     Next: scripts\win_open_manus_shell.cmd
