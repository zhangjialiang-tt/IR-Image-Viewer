"""图像视图组件

提供图像显示、缩放和像素信息查看功能。
"""

import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QScrollArea, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPixmap, QImage, QMouseEvent
from typing import Optional, Tuple

from src.utils.converters import numpy_to_qimage


class ImageView(QWidget):
    """图像视图组件
    
    显示解析后的图像数据，支持缩放和像素信息查看。
    
    Signals:
        pixel_info_changed: 像素信息变化信号，参数为(x, y, value)
    
    Attributes:
        _image_data: 当前显示的图像数据（NumPy数组）
        _bit_depth: 图像位深度
        _zoom_factor: 当前缩放因子
        _qimage: 转换后的QImage对象
        _pixmap: 显示用的QPixmap对象
    """
    
    pixel_info_changed = pyqtSignal(int, int, int)  # x, y, value
    
    def __init__(self, parent=None):
        """初始化图像视图
        
        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        
        # 数据属性
        self._image_data: Optional[np.ndarray] = None
        self._bit_depth: int = 8
        self._zoom_factor: float = 1.0
        self._qimage: Optional[QImage] = None
        self._pixmap: Optional[QPixmap] = None
        
        # 设置UI
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI组件"""
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(False)
        self._scroll_area.setAlignment(Qt.AlignCenter)
        
        # 创建图像标签
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setMouseTracking(True)
        self._image_label.mouseMoveEvent = self._on_mouse_move
        
        # 设置滚动区域的内容
        self._scroll_area.setWidget(self._image_label)
        
        # 添加到布局
        layout.addWidget(self._scroll_area)
        
    def display_image(self, image_data: np.ndarray, bit_depth: int = 8) -> None:
        """显示图像
        
        Args:
            image_data: NumPy数组，形状为(height, width)
            bit_depth: 位深度，8或16
            
        Raises:
            ValueError: 如果图像数据无效
        """
        if image_data is None:
            raise ValueError("图像数据不能为None")
        
        if image_data.ndim != 2:
            raise ValueError(f"图像数据必须是二维数组，当前维度: {image_data.ndim}")
        
        # 保存图像数据
        self._image_data = image_data
        self._bit_depth = bit_depth
        
        # 转换为QImage
        self._qimage = numpy_to_qimage(image_data, bit_depth)
        
        # 应用当前缩放并显示
        self._update_display()
        
    def _update_display(self):
        """更新显示（应用缩放）"""
        if self._qimage is None:
            return
        
        # 计算缩放后的尺寸
        scaled_width = int(self._qimage.width() * self._zoom_factor)
        scaled_height = int(self._qimage.height() * self._zoom_factor)
        
        # 创建缩放后的pixmap
        self._pixmap = QPixmap.fromImage(self._qimage).scaled(
            scaled_width,
            scaled_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # 显示
        self._image_label.setPixmap(self._pixmap)
        self._image_label.resize(self._pixmap.size())
        
    def zoom_in(self) -> None:
        """放大图像
        
        每次放大1.2倍，最大放大到10倍。
        """
        if self._qimage is None:
            return
        
        new_zoom = self._zoom_factor * 1.2
        if new_zoom <= 10.0:
            self._zoom_factor = new_zoom
            self._update_display()
            
    def zoom_out(self) -> None:
        """缩小图像
        
        每次缩小到原来的1/1.2，最小缩小到0.1倍。
        """
        if self._qimage is None:
            return
        
        new_zoom = self._zoom_factor / 1.2
        if new_zoom >= 0.1:
            self._zoom_factor = new_zoom
            self._update_display()
            
    def fit_to_window(self) -> None:
        """适应窗口大小
        
        自动调整图像大小以适应当前窗口尺寸。
        """
        if self._qimage is None:
            return
        
        # 获取可用空间
        available_width = self._scroll_area.viewport().width()
        available_height = self._scroll_area.viewport().height()
        
        # 计算缩放因子
        width_ratio = available_width / self._qimage.width()
        height_ratio = available_height / self._qimage.height()
        
        # 使用较小的比例以确保图像完全可见
        self._zoom_factor = min(width_ratio, height_ratio, 1.0)
        
        self._update_display()
        
    def get_pixel_info(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """获取指定位置的像素信息
        
        Args:
            x: 像素X坐标（图像坐标系）
            y: 像素Y坐标（图像坐标系）
            
        Returns:
            Optional[Tuple[int, int, int]]: (x, y, pixel_value) 或 None（如果坐标无效）
        """
        if self._image_data is None:
            return None
        
        height, width = self._image_data.shape
        
        # 检查坐标是否在有效范围内
        if x < 0 or x >= width or y < 0 or y >= height:
            return None
        
        # 获取像素值
        pixel_value = int(self._image_data[y, x])
        
        return (x, y, pixel_value)
        
    def _on_mouse_move(self, event: QMouseEvent):
        """处理鼠标移动事件
        
        Args:
            event: 鼠标事件
        """
        if self._image_data is None or self._pixmap is None:
            return
        
        # 获取鼠标在标签中的位置
        pos = event.pos()
        
        # 转换为图像坐标（考虑缩放）
        if self._zoom_factor > 0:
            image_x = int(pos.x() / self._zoom_factor)
            image_y = int(pos.y() / self._zoom_factor)
            
            # 获取像素信息
            pixel_info = self.get_pixel_info(image_x, image_y)
            
            if pixel_info is not None:
                x, y, value = pixel_info
                self.pixel_info_changed.emit(x, y, value)
                
    def clear(self):
        """清除显示的图像"""
        self._image_data = None
        self._qimage = None
        self._pixmap = None
        self._zoom_factor = 1.0
        self._image_label.clear()
        
    def get_zoom_factor(self) -> float:
        """获取当前缩放因子
        
        Returns:
            float: 当前缩放因子
        """
        return self._zoom_factor
        
    def set_zoom_factor(self, zoom_factor: float) -> None:
        """设置缩放因子
        
        Args:
            zoom_factor: 缩放因子（0.1-10.0）
        """
        if 0.1 <= zoom_factor <= 10.0:
            self._zoom_factor = zoom_factor
            self._update_display()
