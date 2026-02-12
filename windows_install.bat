@echo off
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system" || (
    echo Requesting Administrative Privileges...
    timeout /T 2 /NOBREAK >nul
    powershell start -verb runas '%~f0'
    exit /b
)

setlocal enabledelayedexpansion

rem 设置默认安装路径为用户目录下的 IMakeCore 目录
for /f "tokens=*" %%a in ('powershell -command "[Environment]::GetFolderPath('UserProfile')"') do (
    set "userProfile=%%a"
)

set "target=!userProfile!\IMakeCore"

echo Default installation directory: !target!

if "!target!"=="" (
    echo error: Path Invalid, Please Restart Script Again
    pause
    exit /b 1
)

rem 如果目录不存在，则创建它
if not exist "!target!\" (
    echo Creating directory: !target!
    mkdir "!target!"
    if errorlevel 1 (
        echo Error: Failed to create directory
        pause
        exit /b 1
    )
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

echo Refreshing Environment Variables...
timeout /T 1 /NOBREAK >nul

powershell -command "[System.Environment]::SetEnvironmentVariable('dummy', 'dummy', 'Machine'); [System.Environment]::SetEnvironmentVariable('dummy', $null, 'Machine')" >nul

rundll32.exe user32.dll,UpdatePerUserSystemParameters 1, True >nul

powershell -command "$HWND_BROADCAST = 0xffff; $WM_SETTINGCHANGE = 0x001A; $null = [WinAPI.SendMessageTimeout]::Invoke($HWND_BROADCAST, $WM_SETTINGCHANGE, [IntPtr]::Zero, 'Environment', 2, 5000, [ref] $null)" >nul

for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul ^| findstr /i "Path"') do (
    set "PATH=%%B"
)

timeout /T 2 /NOBREAK >nul

echo Task Finished, Press Any Key To Exit...
pause >nul