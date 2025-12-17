"""直方图视图组件

显示图像的像素值分布直方图。
"""

import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from typing import Optional


class HistogramView(QWidget):
    """直方图视图组件
    
    显示图像的像素值分布直方图，帮助用户了解图像的动态范围和对比度。
    
    Attributes:
        _histogram_data: 直方图数据（每个bin的计数）
        _bin_edges: bin的边界值
        _bit_depth: 图像位深度
        _is_signed: 是否为有符号数据
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化直方图视图
        
        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        
        # 数据属性
        self._histogram_data: Optional[np.ndarray] = None
        self._bin_edges: Optional[np.ndarray] = None
        self._bit_depth: int = 8
        self._is_signed: bool = False
        self._min_value: float = 0
        self._max_value: float = 255
        
        # 设置最小尺寸
        self.setMinimumSize(400, 300)
        
        # 设置背景色
        self.setStyleSheet("background-color: white;")
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 添加信息标签
        self._info_label = QLabel("直方图：显示当前帧的像素值分布")
        self._info_label.setStyleSheet("color: gray; font-size: 10pt;")
        self._info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._info_label)
        
        # 添加统计信息标签
        self._stats_label = QLabel("")
        self._stats_label.setStyleSheet("color: black; font-size: 9pt;")
        self._stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._stats_label)
        
        # 添加弹性空间，让直方图绘制区域占据剩余空间
        layout.addStretch()
    
    def display_histogram(self, image_data: np.ndarray, bit_depth: int = 8, is_signed: bool = False) -> None:
        """显示图像的直方图
        
        计算并显示图像的像素值分布。
        
        Args:
            image_data: 图像数据数组，形状为(height, width)
            bit_depth: 位深度，8或16
            is_signed: 是否为有符号数据（仅16位时有效）
        """
        if image_data is None or image_data.size == 0:
            self._histogram_data = None
            self._info_label.setText("直方图：无数据")
            self._stats_label.setText("")
            self.update()
            return
        
        self._bit_depth = bit_depth
        self._is_signed = is_signed
        
        # 计算直方图
        # 对于8位：256个bins
        # 对于16位：使用256个bins来简化显示
        num_bins = 256
        
        # 计算直方图
        self._histogram_data, self._bin_edges = np.histogram(
            image_data.flatten(), 
            bins=num_bins
        )
        
        # 计算统计信息
        self._min_value = float(np.min(image_data))
        self._max_value = float(np.max(image_data))
        mean_value = float(np.mean(image_data))
        std_value = float(np.std(image_data))
        
        # 更新信息标签
        if bit_depth == 8:
            self._info_label.setText("直方图：8位灰度图像 (0-255)")
        else:  # 16位
            if is_signed:
                self._info_label.setText("直方图：16位有符号图像 (-32768-32767)")
            else:
                self._info_label.setText("直方图：16位无符号图像 (0-65535)")
        
        # 更新统计信息
        if is_signed and bit_depth == 16:
            stats_text = (
                f"最小值: {self._min_value:.0f} | "
                f"最大值: {self._max_value:.0f} | "
                f"平均值: {mean_value:.1f} | "
                f"标准差: {std_value:.1f}"
            )
        else:
            stats_text = (
                f"最小值: {self._min_value:.0f} | "
                f"最大值: {self._max_value:.0f} | "
                f"平均值: {mean_value:.1f} | "
                f"标准差: {std_value:.1f}"
            )
        
        self._stats_label.setText(stats_text)
        
        # 触发重绘
        self.update()
    
    def clear(self) -> None:
        """清空直方图"""
        self._histogram_data = None
        self._bin_edges = None
        self._info_label.setText("直方图：无数据")
        self._stats_label.setText("")
        self.update()
    
    def paintEvent(self, event):
        """绘制直方图
        
        Args:
            event: 绘制事件
        """
        super().paintEvent(event)
        
        if self._histogram_data is None or len(self._histogram_data) == 0:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取绘制区域（留出边距和标签空间）
        margin = 40
        top_margin = 80  # 为标签留出空间
        width = self.width() - 2 * margin
        height = self.height() - margin - top_margin
        
        if width <= 0 or height <= 0:
            return
        
        # 绘制坐标轴
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        # Y轴
        painter.drawLine(margin, top_margin, margin, top_margin + height)
        # X轴
        painter.drawLine(margin, top_margin + height, margin + width, top_margin + height)
        
        # 绘制直方图
        if len(self._histogram_data) > 0:
            # 归一化直方图数据到绘制高度
            max_count = np.max(self._histogram_data)
            if max_count > 0:
                normalized_data = self._histogram_data / max_count * height
            else:
                normalized_data = self._histogram_data
            
            # 计算每个bar的宽度
            bar_width = width / len(self._histogram_data)
            
            # 绘制直方图条
            painter.setPen(QPen(QColor(100, 150, 255), 1))
            painter.setBrush(QColor(100, 150, 255, 180))
            
            for i, count in enumerate(normalized_data):
                if count > 0:
                    x = margin + i * bar_width
                    y = top_margin + height - count
                    painter.drawRect(int(x), int(y), max(1, int(bar_width)), int(count))
        
        # 绘制刻度标签
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        font = QFont("Arial", 8)
        painter.setFont(font)
        
        # X轴标签（显示值范围）
        # 显示最小值
        painter.drawText(
            margin - 20, 
            top_margin + height + 20, 
            f"{self._min_value:.0f}"
        )
        
        # 显示最大值
        max_text = f"{self._max_value:.0f}"
        painter.drawText(
            margin + width - 20, 
            top_margin + height + 20, 
            max_text
        )
        
        # 显示中间值
        mid_value = (self._min_value + self._max_value) / 2
        painter.drawText(
            margin + width // 2 - 20, 
            top_margin + height + 20, 
            f"{mid_value:.0f}"
        )
        
        # Y轴标签
        painter.drawText(
            5, 
            top_margin + 10, 
            "频数"
        )
        
        # X轴标签
        painter.drawText(
            margin + width // 2 - 20, 
            top_margin + height + 35, 
            "像素值"
        )
