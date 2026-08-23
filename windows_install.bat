@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

:: ── 权限提升 ───────────────────────────────────
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system" || (
    echo Requesting Administrator privileges...
    powershell start -verb runas '%~f0'
    exit /b
)

:: ── 确定安装目标 ───────────────────────────────
for /f "delims=" %%a in ('powershell -command "[Environment]::GetFolderPath('UserProfile')"') do set "USERPROFILE=%%a"
set "TARGET=%USERPROFILE%\IMakeCore"

echo.
echo IMakeCore Windows Installer
echo ─────────────────────────────
echo Target: %TARGET%

:: ── 清理旧目录 ─────────────────────────────────
if exist "%TARGET%\" (
    rmdir /s /q "%TARGET%" 2>nul
    if exist "%TARGET%\" (
        echo ERROR: Cannot remove existing directory. Close programs using it.
        pause
        exit /b 1
    )
)
mkdir "%TARGET%" || (
    echo ERROR: Cannot create target directory.
    pause
    exit /b 1
)

:: ── 拷贝文件 ───────────────────────────────────
echo Copying files...
xcopy "%~dp0*" "%TARGET%\" /y /e /i /q >nul 2>&1
if errorlevel 1 (
    echo ERROR: File copy failed.
    pause
    exit /b 1
)
echo   OK: files copied

:: ── 注册环境变量 (Machine 级别) ─────────────────
echo.
echo Setting environment variables...

set "IMAKECORE_ROOT=%TARGET%"
set "IQMakeCore=%TARGET%\.system\.IMakeCore.prf"
set "ICMakeCore=%TARGET%\.system\.IMakeCore.cmake"
set "IXMakeCore=%TARGET%\.system\.IMakeCore.xmake"
set "IMAKECORE_BIN=%TARGET%\.programs\windows"

:: setx = 持久化 (新窗口), set = 当前窗口
powershell -command "[Environment]::SetEnvironmentVariable('IMAKECORE_ROOT', '%IMAKECORE_ROOT%', 'Machine')" >nul || (echo ERROR: setx IMAKECORE_ROOT failed & pause & exit /b 1)
powershell -command "[Environment]::SetEnvironmentVariable('IQMakeCore', '%IQMakeCore%', 'Machine')" >nul || (echo ERROR: setx IQMakeCore failed & pause & exit /b 1)
powershell -command "[Environment]::SetEnvironmentVariable('ICMakeCore', '%ICMakeCore%', 'Machine')" >nul || (echo ERROR: setx ICMakeCore failed & pause & exit /b 1)
powershell -command "[Environment]::SetEnvironmentVariable('IXMakeCore', '%IXMakeCore%', 'Machine')" >nul || (echo ERROR: setx IXMakeCore failed & pause & exit /b 1)

:: ── 验证环境变量已持久化 ────────────────────────
echo Verifying...
for /f "usebackq tokens=2*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v IMAKECORE_ROOT 2^>nul ^| find "IMAKECORE_ROOT"`) do set "REG_IMR=%%b"
if not defined REG_IMR (echo ERROR: IMAKECORE_ROOT not persisted & pause & exit /b 1)
echo   OK: IMAKECORE_ROOT = %REG_IMR%

for /f "usebackq tokens=2*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v IQMakeCore 2^>nul ^| find "IQMakeCore"`) do set "REG_IQM=%%b"
if not defined REG_IQM (echo ERROR: IQMakeCore not persisted & pause & exit /b 1)
echo   OK: IQMakeCore = %REG_IQM%

for /f "usebackq tokens=2*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v ICMakeCore 2^>nul ^| find "ICMakeCore"`) do set "REG_ICM=%%b"
if not defined REG_ICM (echo ERROR: ICMakeCore not persisted & pause & exit /b 1)
echo   OK: ICMakeCore = %REG_ICM%

for /f "usebackq tokens=2*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v IXMakeCore 2^>nul ^| find "IXMakeCore"`) do set "REG_IXM=%%b"
if not defined REG_IXM (echo ERROR: IXMakeCore not persisted & pause & exit /b 1)
echo   OK: IXMakeCore = %REG_IXM%

:: ── PATH 追加 ──────────────────────────────────
echo.
echo Updating PATH...

for /f "usebackq tokens=2*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul ^| find "Path"`) do set "CUR_PATH=%%b"

:: 检查是否已在 PATH 中
set "PATH_FOUND="
for %%p in ("!CUR_PATH:;=" "!") do if /i "%%~p"=="%IMAKECORE_BIN%" set "PATH_FOUND=1"
if defined PATH_FOUND (
    echo   SKIP: already in PATH
) else (
    set "NEW_PATH=%CUR_PATH%;%IMAKECORE_BIN%"
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul
    echo   OK: added to PATH
)

:: ── 当前窗口刷新环境变量 ────────────────────────
echo.
echo Applying to current session...

:: 从注册表回读到当前 cmd 窗口
for /f "usebackq tokens=2*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v IMAKECORE_ROOT 2^>nul ^| find "IMAKECORE_ROOT"`) do set "IMAKECORE_ROOT=%%b"
for /f "usebackq tokens=2*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v IQMakeCore 2^>nul ^| find "IQMakeCore"`) do set "IQMakeCore=%%b"
for /f "usebackq tokens=2*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v ICMakeCore 2^>nul ^| find "ICMakeCore"`) do set "ICMakeCore=%%b"
for /f "usebackq tokens=2*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v IXMakeCore 2^>nul ^| find "IXMakeCore"`) do set "IXMakeCore=%%b"
for /f "usebackq tokens=2*" %%a in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul ^| find "Path"`) do set "PATH=%%b"

:: 广播 WM_SETTINGCHANGE (通知所有窗口环境变量已变更)
powershell -command "$null = [WinAPI.SendMessageTimeout]::Invoke(0xffff, 0x001A, [IntPtr]::Zero, 'Environment', 2, 5000, [ref]$null)" >nul 2>&1

:: ── 最终验证当前窗口 ────────────────────────────
echo.
echo Final verification:
set IMAKECORE_ROOT >nul 2>&1 && echo   IMAKECORE_ROOT = %IMAKECORE_ROOT% || echo   ERROR: IMAKECORE_ROOT not set in current session
set IQMakeCore >nul 2>&1     && echo   IQMakeCore     = %IQMakeCore% || echo   ERROR: IQMakeCore not set in current session
set ICMakeCore >nul 2>&1     && echo   ICMakeCore     = %ICMakeCore% || echo   ERROR: ICMakeCore not set in current session
set IXMakeCore >nul 2>&1     && echo   IXMakeCore     = %IXMakeCore% || echo   ERROR: IXMakeCore not set in current session

echo.
echo =========================================
echo Installation complete.
echo New terminal windows will have the env vars.
echo Current window already refreshed.
echo =========================================
timeout /T 3 /NOBREAK >nul
exit /b 0
