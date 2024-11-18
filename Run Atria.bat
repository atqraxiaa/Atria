@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%APPDATA%\Atria"
set "LOGFILE=%temp%\output.log"

echo Running Atria.py...
timeout /t 2 /nobreak >nul

cd /d "%VENV_DIR%"
if exist "Scripts\activate.bat" (
    call "Scripts\activate.bat"
) else (
    echo Virtual environment not found in %VENV_DIR%.
    exit /b 1
)

cd /d "%SCRIPT_DIR%"
python Atria_Config.py > "%LOGFILE%" 2>&1
set "exit_code=%errorlevel%"

if %exit_code% neq 0 (
    echo,
    echo Log output:
    type "%LOGFILE%"
    echo Press any key to delete the log file and exit...
    pause >nul
    del "%LOGFILE%"
) else (
    del "%LOGFILE%"
)

exit /b %exit_code%
