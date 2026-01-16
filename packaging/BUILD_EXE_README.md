# IR Image Viewer 打包为 EXE 文件说明

本文档说明如何将 `main.py` 打包成独立的 Windows 可执行文件（.exe）。

## 方法一：使用 PyInstaller（推荐）

### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

### 2. 使用提供的 spec 文件打包

在 `packaging` 目录下运行：

```bash
pyinstaller build_exe.spec
```

打包完成后，可执行文件位于 `dist/IR_Image_Viewer.exe`

### 3. 或者使用命令行直接打包（不使用 spec 文件）

在项目根目录下运行：

```bash
pyinstaller --name=IR_Image_Viewer ^
    --onefile ^
    --windowed ^
    --add-data="src;src" ^
    --hidden-import=PyQt5 ^
    --hidden-import=numpy ^
    --hidden-import=PIL ^
    --exclude-module=matplotlib ^
    --exclude-module=scipy ^
    --exclude-module=pandas ^
    main.py
```

**注意**：Windows 命令行使用 `^` 作为续行符，PowerShell 使用 `` ` ``

### 4. 测试可执行文件

```bash
dist\IR_Image_Viewer.exe
```

---

## 方法二：使用 cx_Freeze（备选）

### 1. 安装 cx_Freeze

```bash
pip install cx_Freeze
```

### 2. 执行打包

```bash
python setup_cx_freeze.py build
```

可执行文件位于 `build/` 目录下的子目录中。

---

## 打包选项说明

### PyInstaller 参数解释

- `--name=IR_Image_Viewer`: 设置输出的 exe 文件名
- `--onefile`: 打包成单个 exe 文件（推荐）
- `--windowed` 或 `-w`: 不显示控制台窗口（GUI 程序必须）
- `--add-data`: 添加数据文件（格式：源路径;目标路径）
- `--hidden-import`: 添加隐式导入的模块
- `--exclude-module`: 排除不需要的大型模块，减小文件大小
- `--icon=icon.ico`: 设置自定义图标（可选）

---

## 常见问题解决

### 问题 1：打包后运行报错 "Failed to execute script"

**解决方案**：
- 在 `build_exe.spec` 中将 `console=False` 改为 `console=True` 重新打包，查看错误信息
- 检查是否缺少依赖模块，特别是 PyQt5 的插件

### 问题 2：文件体积过大

**解决方案**：
- 在干净的虚拟环境中打包
- 排除不必要的模块（matplotlib, scipy 等）
- 使用 `--onefile` 选项

### 问题 3：PyQt5 相关的图标或资源不显示

**解决方案**：
- 确保所有资源文件都包含在 `--add-data` 中
- 检查代码中引用资源文件的路径是否使用了相对路径处理（适应打包后的环境）

---

## 打包前检查清单

- [ ] 已安装所有依赖：`pip install -r requirements.txt`
- [ ] 已安装 PyInstaller：`pip install pyinstaller`
- [ ] 应用程序在开发环境中正常运行 (`python main.py`)
- [ ] 已测试所有核心功能

---

## 技术支持

如遇到打包问题，请检查：
- Python 版本（建议 3.8+）
- PyInstaller 版本
- 依赖库版本兼容性
