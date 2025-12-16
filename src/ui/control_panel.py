"""控制面板组件

提供图像解析参数配置和帧控制的用户界面。
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QRadioButton, QButtonGroup, QSpinBox,
    QPushButton, QGroupBox
)
from PyQt5.QtCore import pyqtSignal


class ControlPanel(QWidget):
    """控制面板
    
    提供用户界面用于配置图像解析参数和控制帧播放。
    
    Signals:
        resolution_changed: 分辨率改变信号，参数为(width, height)
        bit_depth_changed: 位深度改变信号，参数为bit_depth (8或16)
        endianness_changed: 字节序改变信号，参数为endianness ('little'或'big')
        row_offset_changed: 行偏移改变信号，参数为offset值
        frame_changed: 帧索引改变信号，参数为frame_index
        play_clicked: 播放按钮点击信号
        pause_clicked: 暂停按钮点击信号
    """
    
    # 定义信号
    resolution_changed = pyqtSignal(int, int)  # (width, height)
    bit_depth_changed = pyqtSignal(int)  # 8 or 16
    endianness_changed = pyqtSignal(str)  # 'little' or 'big'
    row_offset_changed = pyqtSignal(int)  # offset value
    frame_changed = pyqtSignal(int)  # frame index
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """初始化控制面板
        
        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        
        # 预设分辨率列表 (width, height)
        self._resolutions = [
            (320, 256),
            (640, 512),
            (800, 600),
            (1024, 768),
            (1280, 1024),
            (1920, 1080),
        ]
        
        # 当前帧信息
        self._current_frame = 0
        self._total_frames = 1
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """设置用户界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # 1. 分辨率设置组
        resolution_group = QGroupBox("分辨率")
        resolution_layout = QVBoxLayout()
        
        self.resolution_combo = QComboBox()
        for width, height in self._resolutions:
            self.resolution_combo.addItem(f"{width}×{height}", (width, height))
        # 默认选择640×512
        self.resolution_combo.setCurrentIndex(1)
        self.resolution_combo.currentIndexChanged.connect(self._on_resolution_changed)
        
        resolution_layout.addWidget(self.resolution_combo)
        resolution_group.setLayout(resolution_layout)
        main_layout.addWidget(resolution_group)
        
        # 2. 位深度设置组
        bit_depth_group = QGroupBox("位深度")
        bit_depth_layout = QVBoxLayout()
        
        self.bit_depth_8 = QRadioButton("8位")
        self.bit_depth_16 = QRadioButton("16位")
        self.bit_depth_8.setChecked(True)  # 默认8位
        
        # 创建按钮组以确保互斥
        self.bit_depth_group = QButtonGroup()
        self.bit_depth_group.addButton(self.bit_depth_8, 8)
        self.bit_depth_group.addButton(self.bit_depth_16, 16)
        self.bit_depth_group.buttonClicked.connect(self._on_bit_depth_changed)
        
        bit_depth_layout.addWidget(self.bit_depth_8)
        bit_depth_layout.addWidget(self.bit_depth_16)
        bit_depth_group.setLayout(bit_depth_layout)
        main_layout.addWidget(bit_depth_group)
        
        # 3. 字节序设置组
        endianness_group = QGroupBox("字节序")
        endianness_layout = QVBoxLayout()
        
        self.endianness_little = QRadioButton("小端 (Little)")
        self.endianness_big = QRadioButton("大端 (Big)")
        self.endianness_little.setChecked(True)  # 默认小端
        
        # 创建按钮组以确保互斥
        self.endianness_group = QButtonGroup()
        self.endianness_group.addButton(self.endianness_little, 0)
        self.endianness_group.addButton(self.endianness_big, 1)
        self.endianness_group.buttonClicked.connect(self._on_endianness_changed)
        
        endianness_layout.addWidget(self.endianness_little)
        endianness_layout.addWidget(self.endianness_big)
        endianness_group.setLayout(endianness_layout)
        main_layout.addWidget(endianness_group)
        
        # 4. 行偏移设置组
        row_offset_group = QGroupBox("行偏移")
        row_offset_layout = QVBoxLayout()
        
        self.row_offset_spin = QSpinBox()
        self.row_offset_spin.setMinimum(0)
        self.row_offset_spin.setMaximum(10000)
        self.row_offset_spin.setValue(0)
        self.row_offset_spin.setSuffix(" 字节")
        self.row_offset_spin.valueChanged.connect(self._on_row_offset_changed)
        
        row_offset_layout.addWidget(self.row_offset_spin)
        row_offset_group.setLayout(row_offset_layout)
        main_layout.addWidget(row_offset_group)
        
        # 5. 帧控制组
        frame_control_group = QGroupBox("帧控制")
        frame_control_layout = QVBoxLayout()
        
        # 当前帧显示
        self.frame_label = QLabel("当前帧: 1 / 1")
        frame_control_layout.addWidget(self.frame_label)
        
        # 帧导航按钮
        frame_nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("◀ 上一帧")
        self.prev_button.clicked.connect(self._on_prev_frame)
        
        self.next_button = QPushButton("下一帧 ▶")
        self.next_button.clicked.connect(self._on_next_frame)
        
        frame_nav_layout.addWidget(self.prev_button)
        frame_nav_layout.addWidget(self.next_button)
        frame_control_layout.addLayout(frame_nav_layout)
        
        # 播放控制按钮
        play_control_layout = QHBoxLayout()
        
        self.play_button = QPushButton("▶ 播放")
        self.play_button.clicked.connect(self._on_play_clicked)
        
        self.pause_button = QPushButton("⏸ 暂停")
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.pause_button.setEnabled(False)  # 初始状态禁用暂停按钮
        
        play_control_layout.addWidget(self.play_button)
        play_control_layout.addWidget(self.pause_button)
        frame_control_layout.addLayout(play_control_layout)
        
        frame_control_group.setLayout(frame_control_layout)
        main_layout.addWidget(frame_control_group)
        
        # 添加弹性空间
        main_layout.addStretch()
    
    def _on_resolution_changed(self, index: int) -> None:
        """分辨率改变时的处理函数"""
        width, height = self.resolution_combo.currentData()
        self.resolution_changed.emit(width, height)
    
    def _on_bit_depth_changed(self) -> None:
        """位深度改变时的处理函数"""
        bit_depth = self.bit_depth_group.checkedId()
        self.bit_depth_changed.emit(bit_depth)
    
    def _on_endianness_changed(self) -> None:
        """字节序改变时的处理函数"""
        if self.endianness_little.isChecked():
            self.endianness_changed.emit('little')
        else:
            self.endianness_changed.emit('big')
    
    def _on_row_offset_changed(self, value: int) -> None:
        """行偏移改变时的处理函数"""
        self.row_offset_changed.emit(value)
    
    def _on_prev_frame(self) -> None:
        """上一帧按钮点击处理"""
        if self._total_frames > 0:
            self._current_frame = (self._current_frame - 1) % self._total_frames
            self.update_frame_info(self._current_frame, self._total_frames)
            self.frame_changed.emit(self._current_frame)
    
    def _on_next_frame(self) -> None:
        """下一帧按钮点击处理"""
        if self._total_frames > 0:
            self._current_frame = (self._current_frame + 1) % self._total_frames
            self.update_frame_info(self._current_frame, self._total_frames)
            self.frame_changed.emit(self._current_frame)
    
    def _on_play_clicked(self) -> None:
        """播放按钮点击处理"""
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.play_clicked.emit()
    
    def _on_pause_clicked(self) -> None:
        """暂停按钮点击处理"""
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_clicked.emit()
    
    def update_frame_info(self, current: int, total: int) -> None:
        """更新帧信息显示
        
        Args:
            current: 当前帧索引（从0开始）
            total: 总帧数
        """
        self._current_frame = current
        self._total_frames = total
        
        # 显示时使用1-based索引
        display_current = current + 1 if total > 0 else 0
        self.frame_label.setText(f"当前帧: {display_current} / {total}")
        
        # 更新按钮状态
        has_frames = total > 0
        self.prev_button.setEnabled(has_frames)
        self.next_button.setEnabled(has_frames)
        self.play_button.setEnabled(has_frames)
    
    def get_resolution(self) -> tuple[int, int]:
        """获取当前选择的分辨率
        
        Returns:
            tuple[int, int]: (width, height)
        """
        return self.resolution_combo.currentData()
    
    def get_bit_depth(self) -> int:
        """获取当前选择的位深度
        
        Returns:
            int: 8或16
        """
        return self.bit_depth_group.checkedId()
    
    def get_endianness(self) -> str:
        """获取当前选择的字节序
        
        Returns:
            str: 'little'或'big'
        """
        return 'little' if self.endianness_little.isChecked() else 'big'
    
    def get_row_offset(self) -> int:
        """获取当前行偏移值
        
        Returns:
            int: 行偏移量（字节）
        """
        return self.row_offset_spin.value()
    
    def set_resolution(self, width: int, height: int) -> None:
        """设置分辨率
        
        Args:
            width: 宽度
            height: 高度
        """
        for i in range(self.resolution_combo.count()):
            w, h = self.resolution_combo.itemData(i)
            if w == width and h == height:
                self.resolution_combo.setCurrentIndex(i)
                return
    
    def set_bit_depth(self, bit_depth: int) -> None:
        """设置位深度
        
        Args:
            bit_depth: 8或16
        """
        if bit_depth == 8:
            self.bit_depth_8.setChecked(True)
        elif bit_depth == 16:
            self.bit_depth_16.setChecked(True)
    
    def set_endianness(self, endianness: str) -> None:
        """设置字节序
        
        Args:
            endianness: 'little'或'big'
        """
        if endianness == 'little':
            self.endianness_little.setChecked(True)
        else:
            self.endianness_big.setChecked(True)
    
    def set_row_offset(self, offset: int) -> None:
        """设置行偏移
        
        Args:
            offset: 行偏移量（字节）
        """
        self.row_offset_spin.setValue(offset)
