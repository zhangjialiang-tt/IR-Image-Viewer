# IR Image Viewer 打包文件

本目录包含将 IR Image Viewer 程序打包为 Windows 可执行文件的所有相关文件。

## 📁 目录结构

```
packaging/
├── dist/                      # 打包输出目录
│   └── IR_Image_Viewer.exe   # 可执行文件
├── build/                     # 打包临时文件（可删除）
├── build_exe.spec            # PyInstaller 配置文件
├── build_exe.bat             # 一键打包脚本
├── clean_build.bat           # 清理临时文件脚本
├── run_gui.bat               # 快速启动脚本
├── setup_cx_freeze.py        # 备选打包方案（cx_Freeze）
├── BUILD_EXE_README.md       # 详细打包技术文档
├── IR_Image_Viewer_使用说明.md # 用户使用手册
├── 打包完成说明.txt          # 打包结果说明
└── 快速开始.txt              # 快速开始指南
```

## 🚀 快速使用

### 运行已打包的程序

```bash
# 方式1: 直接运行
dist\IR_Image_Viewer.exe

# 方式2: 使用启动脚本
run_gui.bat
```

### 重新打包

如果修改了源代码，需要重新打包：

```bash
# 方式1: 使用批处理脚本
build_exe.bat

# 方式2: 使用 PyInstaller 命令
pyinstaller build_exe.spec
```

### 清理临时文件

```bash
# 方式1: 使用批处理脚本
clean_build.bat

# 方式2: 手动删除 build/ 和 dist/ 目录
```

## 📖 文档说明

- **BUILD_EXE_README.md**: 详细的打包技术文档，包含常见问题和解决方案
- **IR_Image_Viewer_使用说明.md**: 最终用户使用手册，分发时建议附带
- **快速开始.txt**: 简明的快速开始指南

## 📦 分发说明

分发给最终用户时，只需提供：

1. `dist/IR_Image_Viewer.exe`（必需）
2. `IR_Image_Viewer_使用说明.md`（推荐）

无需其他文件，用户无需安装 Python 环境。

## 🔧 技术细节

- **打包工具**: PyInstaller
- **Python 版本**: 3.8+
- **打包模式**: 单文件模式 (--onefile / standalone)
- **窗口模式**: GUI 模式 (no console)

## ⚠️ 注意事项

1. `build/` 目录是临时文件，可以安全删除
2. `dist/` 目录包含最终的可执行文件，请勿删除
3. 修改源代码后必须重新打包才能生效
4. 打包前确保安装了所有依赖 (PyQt5, numpy, Pillow)

---

返回项目根目录: `cd ..`
