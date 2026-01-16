---
trigger: always_on
---

# Python 环境准则
- 在执行任何 Python 命令或安装依赖时，**必须**使用位于 `./.venv/bin/python` (Linux/Mac) 或 `C:\\100-Working\\102-Working-Prj\\Embedded_Group_Repositories\\.venv\\Scripts\\python.exe` (Windows) 的解释器。
- 禁止直接运行全局 `python` 或 `pip` 命令。
- 在运行脚本前，请确保先执行虚拟环境的激活指令。