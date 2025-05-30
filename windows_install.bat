
@echo off
:: 管理员权限验证
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system" || (
    echo Requesting Administrative Privileges...
    timeout /T 2 /NOBREAK >nul
    powershell start -verb runas '%~f0'
    exit /b
)

:: GUI路径选择
setlocal enabledelayedexpansion
for /f "tokens=*" %%a in ('powershell -command "Add-Type -AssemblyName System.Windows.Forms; $d=New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description='Please Select Install Directory'; if($d.ShowDialog()-eq'OK'){ $d.SelectedPath }"') do (
    set "target=%%a"
)

if not defined target (
    set /p "target=please input directory path"
)

:: 路径验证

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

:: 文件拷贝示例（替换为实际文件）
echo Copying Files...
xcopy "%~dp0\*.*" "!target!\" /y /e /i /q >nul 2>&1
if errorlevel 1 (
    echo Error: Copy File Failed
    pause
    exit /b 1
)

timeout /T 2 /NOBREAK >nul

:: 环境变量设置
echo Setting Environment Variables...
setx IMAKECORE_ROOT "!target!" /m >nul
setx IQMakeCore "%%IMAKECORE_ROOT%%/.system/IMakeCore.prf" /m >nul
setx ICMakeCore "%%IMAKECORE_ROOT%%/.system/IMakeCore.cmake" /m >nul

timeout /T 2 /NOBREAK >nul

echo Task Finished, Press Any Key To Exit...

pause >nul
