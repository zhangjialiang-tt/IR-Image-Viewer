"""
cx_Freeze setup script for IR Image Viewer
备选打包方案，使用 cx_Freeze 代替 PyInstaller
"""

import sys
import os
from cx_Freeze import setup, Executable

# 依赖项
build_exe_options = {
    "packages": ["numpy", "PIL", "PyQt5"],
    "includes": ["numpy.core._methods", "numpy.lib.format"],
    "include_files": [
        ("../src", "src"),
    ],
    "excludes": [
        "matplotlib",
        "scipy",
        "pandas",
        "pytest",
        "hypothesis",
    ],
}

# 基础配置
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 不显示控制台窗口

# 可执行文件配置
executables = [
    Executable(
        "../main.py",
        base=base,
        target_name="IR_Image_Viewer.exe",
        icon=None,  # 可以添加图标路径
    )
]

# 设置
setup(
    name="IR_Image_Viewer",
    version="1.0.0",
    description="IR Image Viewer Binary Data Analysis Tool",
    options={"build_exe": build_exe_options},
    executables=executables,
)
