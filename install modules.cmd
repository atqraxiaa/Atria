@echo off
setlocal

set "PYTHON_URL=https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe"
set "INSTALLER=python-installer.exe"
set "REQUIREMENTS_FILE=requirements.txt"

where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Python is already installed. Skipping installation.
) else (
    echo Downloading Python installer...
    start /wait curl -o "%INSTALLER%" "%PYTHON_URL%"

    echo Installing Python...
    start /wait "" "%INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1

    where python >nul 2>&1
    if errorlevel 1 (
        echo Python installation failed.
        exit /b 1
    )
)

echo Upgrading pip and installing packages from %REQUIREMENTS_FILE%...
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install -r "%REQUIREMENTS_FILE%"

if exist "%INSTALLER%" (
    echo Cleaning up...
    del "%INSTALLER%"
)

echo Python installation and package setup are complete.
endlocal
pause
