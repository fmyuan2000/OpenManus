@echo off
setlocal

rem Open an interactive CMD with Miniforge + conda env activated and cwd set to repo root.
set "MINIFORGE_ROOT=C:\ProgramData\miniforge3"
set "ENV_NAME=open_manus"

if not exist "%MINIFORGE_ROOT%\Scripts\activate.bat" (
  echo [ERROR] Miniforge not found: "%MINIFORGE_ROOT%\Scripts\activate.bat"
  echo         Please edit MINIFORGE_ROOT in: %~f0
  exit /b 1
)

set "PROJECT_ROOT=%~dp0.."
for %%I in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fI"

rem Use the exact Miniforge activation entrypoint, then activate env and cd into repo.
"%windir%\system32\cmd.exe" /K ""%MINIFORGE_ROOT%\Scripts\activate.bat" "%MINIFORGE_ROOT%" ^&^& conda activate %ENV_NAME% ^&^& cd /d "%PROJECT_ROOT%""
