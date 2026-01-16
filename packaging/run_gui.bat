@echo off
REM ========================================
REM IR Image Viewer 快速启动脚本
REM ========================================

echo 正在启动 IR Image Viewer 工具...
echo.

if exist dist\IR_Image_Viewer.exe (
    start dist\IR_Image_Viewer.exe
    echo 程序已启动！
) else (
    echo [错误] 找不到 IR_Image_Viewer.exe
    echo 请先运行 build_exe.bat 进行打包
    pause
)
