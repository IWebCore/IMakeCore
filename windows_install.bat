@echo off
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system" || (
    echo Requesting Administrative Privileges...
    timeout /T 2 /NOBREAK >nul
    powershell start -verb runas '%~f0'
    exit /b
)

setlocal enabledelayedexpansion
for /f "tokens=*" %%a in ('powershell -command "Add-Type -AssemblyName System.Windows.Forms; $d=New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description='Please Select Install Directory'; if($d.ShowDialog()-eq'OK'){ $d.SelectedPath }"') do (
    set "target=%%a"
)

if not defined target (
    set /p "target=please input directory path"
)

if "!target!"=="" (
    echo error: Path Invalid, Please Restart Script Again
    pause
    exit /b 1
)

if not exist "!target!\" (
    echo error: Path Invalid, Please Restart Script Again
    pause
    exit /b 1
)

echo Copying Files...
xcopy "%~dp0\*.*" "!target!\" /y /e /i /q >nul 2>&1
if errorlevel 1 (
    echo Error: Copy File Failed
    pause
    exit /b 1
)

timeout /T 2 /NOBREAK >nul

echo Setting Environment Variables...
setx IMAKECORE_ROOT "!target!" /m >nul
setx IQMakeCore "%%IMAKECORE_ROOT%%/.system/.IMakeCore.prf" /m >nul
setx ICMakeCore "%%IMAKECORE_ROOT%%/.system/.IMakeCore.cmake" /m >nul

set "pathToAdd=%%IMAKECORE_ROOT%%\.programs\windows"

for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul ^| findstr /i "Path"') do (
    set "currentPath=%%B"
)

set "pathExists="
if defined currentPath (
    echo !currentPath! | findstr /c:"!pathToAdd!" >nul && set "pathExists=1"
)

if not defined pathExists (
    set "newPath=!currentPath!;!pathToAdd!"
    
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d "!newPath!" /f >nul
)

timeout /T 2 /NOBREAK >nul

echo Task Finished, Press Any Key To Exit...
pause >nul