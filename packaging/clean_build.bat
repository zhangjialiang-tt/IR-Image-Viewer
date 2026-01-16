@echo off
REM ========================================
REM 清理打包生成的临时文件
REM ========================================

echo ========================================
echo 清理打包临时文件
echo ========================================
echo.

echo 正在清理...

if exist build (
    rmdir /s /q build
    echo [✓] 已删除 build 目录
)

if exist IR_Image_Viewer.spec (
    del /q IR_Image_Viewer.spec
    echo [✓] 已删除 IR_Image_Viewer.spec
)

if exist __pycache__ (
    rmdir /s /q __pycache__
    echo [✓] 已删除 __pycache__
)

echo.
echo 清理完成！
echo.
echo 注意: dist 目录已保留（包含可执行文件）
echo.
pause
