@echo off
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system" || (
    echo Requesting Administrative Privileges...
    timeout /T 2 /NOBREAK >nul
    powershell start -verb runas '%~f0'
    exit /b
)

setlocal enabledelayedexpansion

rem 设置 UTF-8 编码以支持中文路径
chcp 65001 >nul 2>&1

rem 设置默认安装路径为用户目录下的 IMakeCore 目录
rem 使用 PowerShell 直接获取并设置变量，避免批处理解析路径时的编码问题
for /f "delims=" %%a in ('powershell -command "$u = [Environment]::GetFolderPath('UserProfile'); Write-Host $u"') do set "userProfile=%%a"

set "target=!userProfile!\IMakeCore"

echo Default installation directory: !target!

if "!target!"=="" (
    echo error: Path Invalid, Please Restart Script Again
    pause
    exit /b 1
)

if exist "!target!\" (
    rmdir /s /q "!target!" 2>nul
    if errorlevel 1 (
        echo Warning: Failed to remove directory, continuing...
    )
)

rem 如果目录不存在，则创建它
if not exist "!target!\" (
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

rem 使用 PowerShell 设置持久化环境变量
powershell -command "[Environment]::SetEnvironmentVariable('IMAKECORE_ROOT', '!target!', 'Machine')" >nul
powershell -command "[Environment]::SetEnvironmentVariable('IQMakeCore', '!target!\\.system\\.IMakeCore.prf', 'Machine')" >nul
powershell -command "[Environment]::SetEnvironmentVariable('ICMakeCore', '!target!\\.system\\.IMakeCore.cmake', 'Machine')" >nul

set "pathToAdd=!target!\.programs\windows"

for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul ^| findstr /i "Path"') do (
    set "currentPath=%%B"
)

rem 确保 currentPath 被定义（即使为空）
if not defined currentPath set "currentPath="

rem 使用 PowerShell 进行更可靠的路径检查
set "pathExists="
if "!currentPath!" neq "" (
    powershell -command "$path = '%currentPath%'; $search = '%pathToAdd%'; if ($path -split ';' -contains $search) { exit 1 } else { exit 0 }" >nul
    if !errorlevel! equ 1 (
        set "pathExists=1"
    )
)

if not defined pathExists (
    rem 路径不存在，需要添加
    if "!currentPath!" equ "" (
        set "newPath=!pathToAdd!"
    ) else (
        set "newPath=!currentPath!;!pathToAdd!"
    )
    
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d "!newPath!" /f >nul
    echo Added !pathToAdd! to system PATH
) else (
    echo !pathToAdd! already exists in system PATH, skipping...
)

echo Refreshing Environment Variables...
timeout /T 1 /NOBREAK >nul

rem 刷新系统环境变量到当前进程
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v IMAKECORE_ROOT 2^>nul ^| findstr /i "IMAKECORE_ROOT"') do (
    set "IMAKECORE_ROOT=%%B"
)
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v IQMakeCore 2^>nul ^| findstr /i "IQMakeCore"') do (
    set "IQMakeCore=%%B"
)
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v ICMakeCore 2^>nul ^| findstr /i "ICMakeCore"') do (
    set "ICMakeCore=%%B"
)
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul ^| findstr /i "Path"') do (
    set "PATH=%%B"
)

rem 使用 PowerShell 广播环境变量变更消息到所有窗口
powershell -command "$HWND_BROADCAST = 0xffff; $WM_SETTINGCHANGE = 0x001A; $null = [WinAPI.SendMessageTimeout]::Invoke($HWND_BROADCAST, $WM_SETTINGCHANGE, [IntPtr]::Zero, 'Environment', 2, 5000, [ref] $null)" >nul

timeout /T 2 /NOBREAK >nul

echo Task Finished, Press Any Key To Exit...
pause >nul
