@echo off
REM ========================================
REM IR Image Viewer 一键打包脚本
REM ========================================

echo ========================================
echo IR Image Viewer Tool - EXE 打包工具
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 检查 Python 环境...
python --version

REM 检查并安装 PyInstaller
echo.
echo [2/4] 检查 PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller 未安装，正在安装...
    pip install pyinstaller
) else (
    echo PyInstaller 已安装
)

REM 清理旧的构建文件
echo.
echo [3/4] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist IR_Image_Viewer.spec del /q IR_Image_Viewer.spec

REM 执行打包
echo.
echo [4/4] 开始打包...
echo.

pyinstaller build_exe.spec

REM 检查打包结果
if exist dist\IR_Image_Viewer.exe (
    echo.
    echo ========================================
    echo 打包成功！
    echo ========================================
    echo.
    echo 可执行文件位置: dist\IR_Image_Viewer.exe
    echo 文件大小:
    dir dist\IR_Image_Viewer.exe | find "IR_Image_Viewer.exe"
    echo.
    echo 是否立即运行测试？
    echo.
    choice /C YN /M "按 Y 运行，按 N 退出"
    if errorlevel 2 goto end
    if errorlevel 1 goto run
) else (
    echo.
    echo ========================================
    echo 打包失败！
    echo ========================================
    echo 请检查错误信息
    pause
    exit /b 1
)

:run
echo.
echo 正在启动 IR_Image_Viewer.exe...
start dist\IR_Image_Viewer.exe

:end
echo.
echo 完成！
pause
