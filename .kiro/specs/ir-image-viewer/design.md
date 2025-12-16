# Design Document

## Overview

红外图像二进制数据查看器（IR Image Viewer）是一个基于PyQt5的桌面应用程序，用于加载、显示和分析二进制格式的红外图像数据。该应用程序支持多种图像分辨率和数据格式（8位/16位灰度），提供图像可视化和十六进制数据查看两种模式，并包含搜索、多帧播放等高级功能。

系统采用模型-视图-控制器（MVC）架构模式，将数据处理、UI显示和业务逻辑分离，确保代码的可维护性和可扩展性。

## Architecture

### 系统架构

系统采用分层架构设计：

1. **表示层（Presentation Layer）**：基于PyQt5的GUI组件
   - 主窗口（MainWindow）
   - 图像视图（ImageView）
   - 十六进制视图（HexView）
   - 控制面板（ControlPanel）

2. **业务逻辑层（Business Logic Layer）**：
   - 文件加载器（FileLoader）
   - 图像解析器（ImageParser）
   - 数据转换器（DataConverter）
   - 帧管理器（FrameManager）

3. **数据层（Data Layer）**：
   - 二进制数据缓存
   - 图像数据模型
   - 配置管理

### 技术栈

- **Python 3.8+**：主要编程语言
- **PyQt5**：GUI框架
- **NumPy**：高效的数组操作和图像数据处理
- **Pillow (PIL)**：图像格式转换
- **mmap**：大文件内存映射


## Components and Interfaces

### 1. IRImageViewer (主窗口类)

主应用程序窗口，继承自 QMainWindow。

**职责**：
- 初始化和管理所有UI组件
- 协调各组件之间的交互
- 处理菜单和工具栏事件

**接口**：
```python
class IRImageViewer(QMainWindow):
    def __init__(self)
    def setup_ui(self) -> None
    def load_file(self, filepath: str) -> bool
    def update_status(self, message: str) -> None
    def show_error(self, error_message: str) -> None
```

### 2. FileLoader (文件加载器)

负责加载和管理二进制文件。

**职责**：
- 读取二进制文件
- 对大文件使用内存映射
- 提供文件元数据

**接口**：
```python
class FileLoader:
    def load_file(self, filepath: str) -> bytes
    def get_file_size(self) -> int
    def get_file_info(self) -> dict
    def use_memory_mapping(self) -> bool
```


### 3. ImageParser (图像解析器)

将二进制数据解析为图像数据。

**职责**：
- 根据配置参数解析二进制数据
- 处理不同位深度（8位/16位）
- 处理字节序转换
- 应用行偏移

**接口**：
```python
class ImageParser:
    def __init__(self, width: int, height: int, bit_depth: int, 
                 endianness: str, row_offset: int)
    def parse_frame(self, data: bytes, frame_index: int) -> np.ndarray
    def calculate_frame_size(self) -> int
    def calculate_total_frames(self, file_size: int) -> int
    def validate_parameters(self, file_size: int) -> bool
```

### 4. ImageView (图像显示组件)

显示解析后的图像数据。

**职责**：
- 渲染图像
- 处理缩放操作
- 显示像素信息
- 提供交互功能

**接口**：
```python
class ImageView(QWidget):
    def display_image(self, image_data: np.ndarray) -> None
    def zoom_in(self) -> None
    def zoom_out(self) -> None
    def fit_to_window(self) -> None
    def get_pixel_info(self, x: int, y: int) -> tuple
    def mouseMoveEvent(self, event: QMouseEvent) -> None
```


### 5. HexView (十六进制查看器)

以十六进制格式显示文件内容。

**职责**：
- 将二进制数据转换为十六进制显示
- 显示地址偏移量和ASCII字符
- 实现虚拟滚动优化性能
- 支持搜索和高亮

**接口**：
```python
class HexView(QWidget):
    def display_hex_data(self, data: bytes, offset: int = 0) -> None
    def search_pattern(self, hex_pattern: str) -> list
    def highlight_matches(self, positions: list) -> None
    def scroll_to_position(self, position: int) -> None
    def format_hex_line(self, data: bytes, address: int) -> str
```

### 6. FrameManager (帧管理器)

管理多帧图像的播放和导航。

**职责**：
- 管理当前帧索引
- 控制动画播放
- 处理帧切换逻辑

**接口**：
```python
class FrameManager:
    def __init__(self, total_frames: int)
    def set_current_frame(self, frame_index: int) -> None
    def get_current_frame(self) -> int
    def next_frame(self) -> int
    def previous_frame(self) -> int
    def play(self, fps: int) -> None
    def pause(self) -> None
    def is_playing(self) -> bool
```


### 7. ControlPanel (控制面板)

提供参数配置界面。

**职责**：
- 显示和管理配置参数
- 发送参数变更信号
- 提供播放控制

**接口**：
```python
class ControlPanel(QWidget):
    # Signals
    resolution_changed = pyqtSignal(int, int)
    bit_depth_changed = pyqtSignal(int)
    endianness_changed = pyqtSignal(str)
    row_offset_changed = pyqtSignal(int)
    frame_changed = pyqtSignal(int)
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    
    def setup_ui(self) -> None
    def update_frame_info(self, current: int, total: int) -> None
```

## Data Models

### ImageConfig (图像配置)

存储图像解析参数。

```python
@dataclass
class ImageConfig:
    width: int = 640
    height: int = 512
    bit_depth: int = 8  # 8 or 16
    endianness: str = 'little'  # 'little' or 'big'
    row_offset: int = 0
    
    def validate(self) -> bool:
        """验证配置参数的有效性"""
        pass
    
    def get_bytes_per_pixel(self) -> int:
        """返回每像素字节数"""
        return self.bit_depth // 8
```


### FileInfo (文件信息)

存储加载文件的元数据。

```python
@dataclass
class FileInfo:
    filepath: str
    filename: str
    file_size: int
    total_frames: int
    is_memory_mapped: bool
```

### FrameData (帧数据)

表示单帧图像数据。

```python
@dataclass
class FrameData:
    frame_index: int
    pixel_data: np.ndarray
    width: int
    height: int
    bit_depth: int
    
    def to_qimage(self) -> QImage:
        """转换为QImage用于显示"""
        pass
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. 
Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

在定义具体属性之前，我们需要识别并消除冗余属性：

**识别的冗余情况**：
1. 属性 1.2（文件读取）和属性 5.1（十六进制显示）存在重叠 - 如果文件能正确读取，十六进制显示自然正确
2. 属性 3.1（图像显示）已经包含了数据转换的正确性，不需要单独的转换属性
3. 多个缩放相关属性（3.4, 3.5）可以合并为一个综合的缩放属性

**合并后的核心属性**：
- 文件操作属性（加载、错误处理）
- 数据解析属性（位深度、字节序、偏移）
- 图像显示属性（缩放、像素信息）
- 帧管理属性（帧计算、帧切换）
- 十六进制属性（格式转换、搜索）


### Core Properties

**Property 1: 文件读取完整性**
*For any* 有效的二进制文件，当系统读取该文件时，读取的字节数应该等于文件的实际大小
**Validates: Requirements 1.2**

**Property 2: 错误处理一致性**
*For any* 无效文件或加载错误，系统应该显示错误消息并且不改变当前应用状态
**Validates: Requirements 1.4, 8.2**

**Property 3: 文件信息显示完整性**
*For any* 成功加载的文件，状态栏显示的文件信息应该包含文件名、大小和路径
**Validates: Requirements 1.5**

**Property 4: 分辨率解析正确性**
*For any* 有效的分辨率配置（宽度和高度），解析后的图像数据维度应该与配置的分辨率匹配
**Validates: Requirements 2.1**

**Property 5: 位深度解析正确性**
*For any* 二进制数据和位深度设置（8位或16位），每个像素占用的字节数应该等于 bit_depth / 8
**Validates: Requirements 2.2**

**Property 6: 字节序转换正确性**
*For any* 16位数据，大端和小端转换应该产生不同的像素值，且转换两次应该返回原始值（round-trip）
**Validates: Requirements 2.3**

**Property 7: 行偏移解析正确性**
*For any* 有效的行偏移量，解析应该从文件的 (offset) 字节位置开始读取数据
**Validates: Requirements 2.4**


**Property 8: 图像数据转换正确性**
*For any* 有效的像素数据数组，转换为QImage后的尺寸应该与原始数组的形状匹配
**Validates: Requirements 3.1**

**Property 9: 像素信息准确性**
*For any* 图像上的有效坐标(x, y)，返回的像素值应该等于图像数据数组中 [y, x] 位置的值
**Validates: Requirements 3.2**

**Property 10: 图像缩放一致性**
*For any* 缩放比例因子，缩放后的图像尺寸应该等于原始尺寸乘以缩放因子
**Validates: Requirements 3.4, 3.5**

**Property 11: 帧数计算正确性**
*For any* 文件大小和帧大小配置，总帧数应该等于 floor(file_size / frame_size)
**Validates: Requirements 4.1**

**Property 12: 帧索引访问正确性**
*For any* 有效的帧索引 i（0 <= i < total_frames），解析第 i 帧应该读取从位置 (i * frame_size) 开始的数据
**Validates: Requirements 4.2**

**Property 13: 播放速度控制正确性**
*For any* 帧率设置 fps，连续两帧之间的时间间隔应该约等于 1000/fps 毫秒
**Validates: Requirements 4.5**

**Property 14: 十六进制转换正确性（Round-trip）**
*For any* 二进制数据，将其转换为十六进制字符串，然后再转换回二进制，应该得到原始数据
**Validates: Requirements 5.1**


**Property 15: 地址偏移量正确性**
*For any* 十六进制显示的行号 n（每行16字节），该行的地址偏移量应该等于 n * 16
**Validates: Requirements 5.2**

**Property 16: ASCII转换正确性**
*For any* 字节值 b，如果 32 <= b <= 126，ASCII表示应该是对应的可打印字符，否则应该是 '.'
**Validates: Requirements 5.3**

**Property 17: 十六进制搜索输入验证**
*For any* 输入字符串，如果它只包含十六进制字符（0-9, a-f, A-F）且长度为偶数，则应该被验证为有效
**Validates: Requirements 6.1**

**Property 18: 十六进制搜索完整性**
*For any* 有效的十六进制搜索模式和文件数据，搜索结果应该包含所有匹配位置，且每个位置的数据确实匹配搜索模式
**Validates: Requirements 6.2**

**Property 19: 搜索结果高亮正确性**
*For any* 搜索匹配位置列表，所有匹配位置在十六进制视图中应该被标记为高亮状态
**Validates: Requirements 6.3**

**Property 20: 无效操作提示一致性**
*For any* 无效操作（如空文件、参数超出范围），系统应该显示包含错误描述的提示消息
**Validates: Requirements 8.5, 9.1, 9.2, 9.3**


## Error Handling

### 错误类型和处理策略

1. **文件访问错误**
   - FileNotFoundError：文件不存在
   - PermissionError：无权限访问
   - IOError：读取失败
   - 处理：显示错误对话框，保持当前状态

2. **数据解析错误**
   - ValueError：参数无效（如负数分辨率）
   - IndexError：帧索引超出范围
   - 处理：显示警告消息，使用默认值或拒绝操作

3. **内存错误**
   - MemoryError：内存不足
   - 处理：尝试使用内存映射，或提示用户关闭其他应用

4. **UI错误**
   - 图像显示失败
   - 处理：显示占位符图像和错误信息

### 错误处理实现

```python
class ErrorHandler:
    @staticmethod
    def handle_file_error(error: Exception, filepath: str) -> None:
        """处理文件相关错误"""
        if isinstance(error, FileNotFoundError):
            show_error_dialog(f"文件未找到: {filepath}")
        elif isinstance(error, PermissionError):
            show_error_dialog(f"无权限访问文件: {filepath}")
        else:
            show_error_dialog(f"文件读取失败: {str(error)}")
    
    @staticmethod
    def handle_parse_error(error: Exception) -> None:
        """处理解析错误"""
        show_warning_dialog(f"数据解析错误: {str(error)}")
    
    @staticmethod
    def validate_config(config: ImageConfig, file_size: int) -> tuple[bool, str]:
        """验证配置参数"""
        if config.width <= 0 or config.height <= 0:
            return False, "分辨率必须为正数"
        
        frame_size = config.width * config.height * config.get_bytes_per_pixel()
        if frame_size > file_size:
            return False, "文件大小不足以包含一帧完整图像"
        
        return True, ""
```


## Testing Strategy

本项目采用双重测试策略，结合单元测试和基于属性的测试（Property-Based Testing），以确保代码的正确性和健壮性。

### 单元测试

单元测试用于验证特定示例、边界情况和错误条件。

**测试框架**：pytest

**测试覆盖范围**：

1. **文件加载测试**
   - 测试加载小文件（< 100MB）
   - 测试加载大文件（> 100MB）使用内存映射
   - 测试加载不存在的文件
   - 测试加载空文件

2. **图像解析测试**
   - 测试8位灰度图像解析
   - 测试16位灰度图像解析
   - 测试大端/小端字节序
   - 测试行偏移功能

3. **UI组件测试**
   - 测试主窗口初始化
   - 测试标签页切换
   - 测试菜单和工具栏功能

4. **边界情况测试**
   - 空文件处理
   - 文件大小不足一帧
   - 帧索引超出范围
   - 无效的十六进制搜索字符串


### 基于属性的测试（Property-Based Testing）

基于属性的测试用于验证通用属性在大量随机输入下的正确性。

**测试框架**：Hypothesis

**配置要求**：
- 每个属性测试至少运行 100 次迭代
- 使用 Hypothesis 的策略生成器创建随机测试数据

**测试标注格式**：
每个属性测试必须使用注释明确标注对应的设计文档属性：
```python
# Feature: ir-image-viewer, Property 1: 文件读取完整性
@given(st.binary(min_size=1, max_size=10000))
def test_file_read_integrity(data):
    ...
```

**属性测试覆盖**：

1. **Property 1: 文件读取完整性**
   - 生成随机二进制数据
   - 验证读取的字节数等于文件大小

2. **Property 4: 分辨率解析正确性**
   - 生成随机分辨率配置
   - 验证解析后的图像维度匹配

3. **Property 6: 字节序转换正确性（Round-trip）**
   - 生成随机16位数据
   - 验证大端↔小端转换的往返一致性

4. **Property 9: 像素信息准确性**
   - 生成随机图像数据和坐标
   - 验证返回的像素值正确

5. **Property 11: 帧数计算正确性**
   - 生成随机文件大小和帧配置
   - 验证帧数计算公式

6. **Property 14: 十六进制转换正确性（Round-trip）**
   - 生成随机二进制数据
   - 验证 binary → hex → binary 转换一致性

7. **Property 17: 十六进制搜索输入验证**
   - 生成随机字符串
   - 验证验证逻辑的正确性

8. **Property 18: 十六进制搜索完整性**
   - 生成随机数据和搜索模式
   - 验证所有匹配位置都被找到


### 测试数据生成策略

使用 Hypothesis 的策略生成器创建智能的测试数据：

```python
from hypothesis import strategies as st

# 生成有效的图像配置
@st.composite
def valid_image_config(draw):
    width = draw(st.integers(min_value=64, max_value=2048))
    height = draw(st.integers(min_value=64, max_value=2048))
    bit_depth = draw(st.sampled_from([8, 16]))
    endianness = draw(st.sampled_from(['little', 'big']))
    row_offset = draw(st.integers(min_value=0, max_value=1000))
    return ImageConfig(width, height, bit_depth, endianness, row_offset)

# 生成有效的十六进制字符串
@st.composite
def valid_hex_string(draw):
    length = draw(st.integers(min_value=1, max_value=50)) * 2  # 确保偶数长度
    hex_chars = '0123456789abcdefABCDEF'
    return ''.join(draw(st.lists(st.sampled_from(hex_chars), 
                                  min_size=length, max_size=length)))

# 生成图像数据
@st.composite
def image_data(draw, width, height, bit_depth):
    if bit_depth == 8:
        return draw(st.lists(st.integers(min_value=0, max_value=255),
                            min_size=width*height, max_size=width*height))
    else:  # 16-bit
        return draw(st.lists(st.integers(min_value=0, max_value=65535),
                            min_size=width*height, max_size=width*height))
```

### 集成测试

虽然不是核心重点，但需要进行基本的集成测试：

1. **端到端工作流测试**
   - 加载文件 → 配置参数 → 显示图像 → 切换帧
   - 加载文件 → 查看十六进制 → 搜索模式

2. **组件交互测试**
   - 控制面板参数变更触发图像重新解析
   - 帧管理器与图像视图的同步


## Implementation Details

### 性能优化策略

1. **大文件处理**
   ```python
   def load_file(self, filepath: str) -> bytes:
       file_size = os.path.getsize(filepath)
       if file_size > 100 * 1024 * 1024:  # 100MB
           # 使用内存映射
           with open(filepath, 'rb') as f:
               return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
       else:
           # 直接读取
           with open(filepath, 'rb') as f:
               return f.read()
   ```

2. **帧数据缓存**
   - 使用 LRU 缓存存储最近访问的帧
   - 缓存大小：最多10帧

3. **十六进制视图虚拟滚动**
   - 只渲染可见区域的数据
   - 使用 QAbstractScrollArea 实现

4. **图像显示优化**
   - 使用 NumPy 进行快速数组操作
   - 缓存缩放后的图像

### UI布局设计

```
┌─────────────────────────────────────────────────────────┐
│ 菜单栏: 文件 | 编辑 | 视图 | 帮助                          │
├─────────────────────────────────────────────────────────┤
│ 工具栏: [打开] [保存] | [放大] [缩小] [适应] | [播放] [暂停] │
├──────────────────────┬──────────────────────────────────┤
│                      │  ┌────────────────────────────┐  │
│  控制面板             │  │                            │  │
│  ┌────────────────┐  │  │                            │  │
│  │ 分辨率:        │  │  │      图像视图 / 十六进制    │  │
│  │ [640x512 ▼]   │  │  │                            │  │
│  │                │  │  │                            │  │
│  │ 位深度:        │  │  │                            │  │
│  │ ○ 8位 ● 16位  │  │  │                            │  │
│  │                │  │  │                            │  │
│  │ 字节序:        │  │  │                            │  │
│  │ ○ 小端 ● 大端  │  │  │                            │  │
│  │                │  │  │                            │  │
│  │ 行偏移: [0]    │  │  │                            │  │
│  │                │  │  │                            │  │
│  │ 帧控制:        │  │  │                            │  │
│  │ 当前帧: [1/10] │  │  │                            │  │
│  │ [◀] [▶] [▶▶]  │  │  │                            │  │
│  └────────────────┘  │  └────────────────────────────┘  │
│                      │                                  │
├──────────────────────┴──────────────────────────────────┤
│ 状态栏: 文件: test.bin | 大小: 3.2 MB | 坐标: (120, 45) 值: 128 │
└─────────────────────────────────────────────────────────┘
```


### 依赖项

```
# requirements.txt
PyQt5>=5.15.0
numpy>=1.19.0
Pillow>=8.0.0
pytest>=6.0.0
hypothesis>=6.0.0
pytest-qt>=4.0.0
```

### 项目结构

```
ir-image-viewer/
├── src/
│   ├── __init__.py
│   ├── main.py                 # 应用程序入口
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # 主窗口
│   │   ├── image_view.py       # 图像视图
│   │   ├── hex_view.py         # 十六进制视图
│   │   └── control_panel.py    # 控制面板
│   ├── core/
│   │   ├── __init__.py
│   │   ├── file_loader.py      # 文件加载器
│   │   ├── image_parser.py     # 图像解析器
│   │   ├── frame_manager.py    # 帧管理器
│   │   └── data_models.py      # 数据模型
│   └── utils/
│       ├── __init__.py
│       ├── error_handler.py    # 错误处理
│       └── converters.py       # 数据转换工具
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_file_loader.py
│   │   ├── test_image_parser.py
│   │   ├── test_frame_manager.py
│   │   └── test_converters.py
│   └── property/
│       ├── test_properties_file.py
│       ├── test_properties_parse.py
│       ├── test_properties_hex.py
│       └── strategies.py       # Hypothesis 策略
├── requirements.txt
├── README.md
└── setup.py
```

## 扩展性考虑

1. **支持新的图像格式**
   - 创建新的解析器类继承 `ImageParser`
   - 在配置中注册新格式

2. **添加新的查看模式**
   - 创建新的视图组件继承 `QWidget`
   - 在主窗口的标签页中添加

3. **支持图像处理功能**
   - 在 `ImageView` 中添加滤镜和增强功能
   - 使用 NumPy 或 OpenCV 进行处理

4. **导出功能**
   - 添加导出为常见图像格式（PNG, JPEG）
   - 导出十六进制数据为文本文件

5. **批处理功能**
   - 支持批量加载多个文件
   - 支持批量导出帧

