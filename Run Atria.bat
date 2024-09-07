@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "LOGFILE=%temp%\output.log"

echo Running Atria.py...
timeout /t 2 /nobreak >nul

cd /d "%SCRIPT_DIR%\Atria"
if exist "Scripts\Activate" call "Scripts\Activate"

cd /d "%SCRIPT_DIR%"
python Atria.py > "%LOGFILE%" 2>&1
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