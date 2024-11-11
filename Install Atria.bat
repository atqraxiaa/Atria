:: This code is from myself, specifically @lyraalei on Discord.
:: Contact me if you do encounter bugs, or want to add something in the script. thanks <3

@echo off
setlocal

cd /d "%~dp0"
net sess >nul 2>&1 || (
    echo(CreateObject("Shell.Application"^).ShellExecute"%~0",,,"RunAs",1:CreateObject("Scripting.FileSystemObject"^).DeleteFile(wsh.ScriptFullName^)>"%temp%\%~nx0.vbs"
    start wscript.exe "%temp%\%~nx0.vbs"
    exit
)

set "REQUIREMENTS_FILE=requirements.txt"
set "PYTHON_EXE=python"
set "TARGET_VERSION=3.12.7"

if exist "%SystemRoot%\System32\python.exe" set "PYTHON_EXE=%SystemRoot%\System32\python.exe"
if exist "%SystemRoot%\System32\py.exe" set "PYTHON_EXE=%SystemRoot%\System32\py.exe"

%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed.
    goto Update
)

echo Python executable found. Checking version...
echo,
for /f "tokens=2 delims= " %%a in ('"%PYTHON_EXE% --version" 2^>nul') do set PY_VER=%%a

for /f "tokens=1,2,3 delims=." %%a in ("%PY_VER%") do (
    set MAJOR_VER=%%a
    set MINOR_VER=%%b
    set PATCH_VER=%%c
)

set MAJOR_VER=%MAJOR_VER: =%
set MINOR_VER=%MINOR_VER: =%
set PATCH_VER=%PATCH_VER: =%

echo Detected Python version: %MAJOR_VER%.%MINOR_VER%.%PATCH_VER%

for /f "tokens=1,2,3 delims=." %%a in ("%TARGET_VERSION%") do (
    set TARGET_MAJOR=%%a
    set TARGET_MINOR=%%b
    set TARGET_PATCH=%%c
)

set TARGET_MAJOR=%TARGET_MAJOR: =%
set TARGET_MINOR=%TARGET_MINOR: =%
set TARGET_PATCH=%TARGET_PATCH: =%

echo Target Python version: %TARGET_MAJOR%.%TARGET_MINOR%.%TARGET_PATCH%

if "%PATCH_VER%"=="0" set PATCH_VER=
if "%MINOR_VER%"=="0" if "%PATCH_VER%"=="" set MINOR_VER=

if "%TARGET_PATCH%"=="0" set TARGET_PATCH=
if "%TARGET_MINOR%"=="0" if "%TARGET_PATCH%"=="" set TARGET_MINOR=

:: This commented code below is for debugging purposes only. Do not enable it unless you know what you're doing!
:: echo,
:: echo After trimming:
:: echo Detected Python version: %MAJOR_VER%.%MINOR_VER%.%PATCH_VER%
:: echo Target Python version: %TARGET_MAJOR%.%TARGET_MINOR%.%TARGET_PATCH%
::
:: if "%MAJOR_VER%"=="%TARGET_MAJOR%" (
::     if "%MINOR_VER%"=="%TARGET_MINOR%" (
::         if "%PATCH_VER%"=="%TARGET_PATCH%" (
::             echo Python is up-to-date.
::         ) else (
::             echo Python versions differ in PATCH level.
::         )
::     ) else (
::         echo Python versions differ in MINOR level.
::     )
:: ) else (
::     echo Python versions differ in MAJOR level.
:: )
::

if "%PATCH_VER%"=="" set PATCH_VER=0
if "%TARGET_PATCH%"=="" set TARGET_PATCH=0

if %MAJOR_VER% GTR %TARGET_MAJOR% (
    echo Python version is newer than the target. Installing Visual C++ Build Tools...
    echo,
    timeout /t 5 /nobreak >nul
    goto CheckVCPP
) else if %MAJOR_VER% LSS %TARGET_MAJOR% (
    echo Python version is older than the target. Updating to %TARGET_VERSION%...
    goto Update
) else (
    if %MINOR_VER% GTR %TARGET_MINOR% (
        echo Python version is newer than the target. Installing Visual C++ Build Tools...
        echo,
        timeout /t 5 /nobreak >nul
        goto CheckVCPP
    ) else if %MINOR_VER% LSS %TARGET_MINOR% (
        echo Python version is older than the target. Updating to %TARGET_VERSION%...
        goto Update
    ) else (
        if %PATCH_VER% GEQ %TARGET_PATCH% (
            echo Python version is already up-to-date. Installing Visual C++ Build Tools...
            echo,
            timeout /t 5 /nobreak >nul
            goto CheckVCPP
        ) else (
            echo Python version is older than the target. Updating to %TARGET_VERSION%...
            goto Update
        )
    )
)

:Update
set "TARGET_VERSION=3.12.7"

echo Downloading Python %TARGET_VERSION%...
powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/%TARGET_VERSION%/python-%TARGET_VERSION%-amd64.exe -OutFile \"%~dp0python_installer.exe\" -UseBasicParsing"
powershell -Command "while (!(Test-Path \"%~dp0python_installer.exe\")) { Start-Sleep -Milliseconds 100 }"

echo Installing Python %TARGET_VERSION%...
"%~dp0python_installer.exe" /quiet PrependPath=1

if %errorlevel% neq 0 (
    echo [ERROR] Installation failed with error code %errorlevel%.
    pause
    exit /b %errorlevel%
)

del "%~dp0python_installer.exe"
python -m ensurepip --upgrade

set "PYTHON_PATH=%LocalAppData%\Programs\Python\Python312"
setx PATH "%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PATH%" /M

echo,
echo Taking ownership and granting full control on Python aliases...
takeown /f "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python.exe" /r /d y
takeown /f "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python3.exe" /r /d y

if %errorlevel%==0 (
    echo [SUCCESS] Successfully removed Python aliases.
) else (
    echo [ERROR] Failed to remove Python aliases.
)

echo,
echo Granting full control to the current user on python.exe and python3.exe...
icacls "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python.exe" /grant %username%:F
icacls "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python3.exe" /grant %username%:F

if %errorlevel%==0 (
    echo [SUCCESS] Successfully removed Python aliases.
) else (
    echo [ERROR] Failed to remove Python aliases.
)

timeout /t 5 /nobreak >nul

echo,
echo Attempting to remove Python from Manage App Execution Aliases...
powershell -Command "Remove-Item -Path $env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\python.exe -Force"
powershell -Command "Remove-Item -Path $env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\python3.exe -Force"

if %errorlevel%==0 (
    echo [SUCCESS] Python aliases were successfully removed from Manage App Execution Aliases.
) else (
    echo [ERROR] Failed to remove Python aliases. Please check permissions or try again.
)

echo Python has been installed. Restarting system (Press Ctrl+C to cancel)...
timeout /t 15
shutdown /r /t 0

:CheckVCPP
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" >nul 2>&1 || reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\17.0\VC\Runtimes\x64" >nul 2>&1

if %errorlevel% equ 0 (
    echo Visual C++ Build Tools are already installed. Skipping installation.
    goto InstallPackages
) else (
    echo Visual C++ Build Tools not found. Proceeding with installation...
    goto InstallVCPP
)

:InstallVCPP
echo Downloading Visual C++ Build Tools installer...
powershell -Command "Invoke-WebRequest -Uri https://aka.ms/vs/17/release/vs_BuildTools.exe -OutFile \"%~dp0vs_BuildTools.exe\" -UseBasicParsing"
powershell -Command "while (!(Test-Path \"%~dp0vs_BuildTools.exe\")) { Start-Sleep -Milliseconds 100 }"

echo Installing Visual C++ Build Tools...
"%~dp0vs_BuildTools.exe" --quiet --wait --norestart --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended

if %errorlevel% equ 3010 (
    echo [SUCCESS] Installation completed successfully but requires a restart.
    del "%~dp0vs_BuildTools.exe"
    echo The system will now restart in 15 seconds. Press Ctrl+C to cancel.
    timeout /t 15
    shutdown /r /t 0
    exit
)

if %errorlevel% neq 0 (
    echo [ERROR] Visual C++ Build Tools installation failed with error code %errorlevel%.
    pause
    exit /b %errorlevel%
)

del "%~dp0vs_BuildTools.exe"

echo Visual C++ Build Tools has been installed. Installing packages...
echo If the logs below contain errors, please run this batch file again.
echo,
timeout /t 5 /nobreak >nul
goto InstallPackages

:InstallPackages
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%\Atria"

echo Creating a virtual environment named "Atria"...
echo,
if not exist "%VENV_DIR%" (
    python -m venv "%VENV_DIR%"
) 
call "%VENV_DIR%\Scripts\activate.bat"

python -m pip install --upgrade pip
pip install -r requirements.txt
call "%VENV_DIR%\Scripts\deactivate.bat"

endlocal
echo,
echo Finished installing packages.
timeout /t 5 /nobreak >nul
exit
