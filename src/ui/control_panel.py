"""控制面板组件

提供图像解析参数配置和帧控制的用户界面。
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QRadioButton, QButtonGroup, QSpinBox,
    QPushButton, QGroupBox, QLineEdit, QDialog, QDialogButtonBox,
    QFormLayout, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt


class ControlPanel(QWidget):
    """控制面板
    
    提供用户界面用于配置图像解析参数和控制帧播放。
    
    Signals:
        resolution_changed: 分辨率改变信号，参数为(width, height)
        bit_depth_changed: 位深度改变信号，参数为bit_depth (8或16)
        endianness_changed: 字节序改变信号，参数为endianness ('little'或'big')
        row_offset_changed: 文件偏移改变信号，参数为offset值（从文件的第N个字节开始读取）
        frame_changed: 帧索引改变信号，参数为frame_index
        play_clicked: 播放按钮点击信号
        pause_clicked: 暂停按钮点击信号
    """
    
    # 定义信号
    resolution_changed = pyqtSignal(int, int)  # (width, height)
    bit_depth_changed = pyqtSignal(int)  # 8 or 16
    data_type_changed = pyqtSignal(bool)  # True for signed, False for unsigned (16-bit only)
    endianness_changed = pyqtSignal(str)  # 'little' or 'big'
    row_offset_changed = pyqtSignal(int)  # file offset value (start reading from byte N)
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
        
        # 自定义分辨率
        self._custom_resolution = None
        
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
        # 添加"自定义..."选项
        self.resolution_combo.addItem("自定义...", None)
        # 默认选择640×512
        self.resolution_combo.setCurrentIndex(1)
        self.resolution_combo.currentIndexChanged.connect(self._on_resolution_changed)
        
        resolution_layout.addWidget(self.resolution_combo)
        
        # 添加自定义分辨率按钮（可选的替代方式）
        self.custom_resolution_button = QPushButton("设置自定义分辨率...")
        self.custom_resolution_button.clicked.connect(self._show_custom_resolution_dialog)
        resolution_layout.addWidget(self.custom_resolution_button)
        
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
        
        # 2.5. 数据类型设置组（仅16位时有效）
        data_type_group = QGroupBox("数据类型 (16位)")
        data_type_layout = QVBoxLayout()
        
        self.data_type_unsigned = QRadioButton("无符号 (0-65535)")
        self.data_type_signed = QRadioButton("有符号 (-32768-32767)")
        self.data_type_unsigned.setChecked(True)  # 默认无符号
        
        # 创建按钮组以确保互斥
        self.data_type_group = QButtonGroup()
        self.data_type_group.addButton(self.data_type_unsigned, 0)
        self.data_type_group.addButton(self.data_type_signed, 1)
        self.data_type_group.buttonClicked.connect(self._on_data_type_changed)
        
        data_type_layout.addWidget(self.data_type_unsigned)
        data_type_layout.addWidget(self.data_type_signed)
        data_type_group.setLayout(data_type_layout)
        
        # 初始状态：8位时禁用数据类型选择
        data_type_group.setEnabled(False)
        self.data_type_group_widget = data_type_group
        
        main_layout.addWidget(data_type_group)
        
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
        
        # 4. 文件偏移设置组（原"行偏移"）
        file_offset_group = QGroupBox("文件偏移")
        file_offset_layout = QVBoxLayout()
        
        # 添加说明标签
        offset_info_label = QLabel("从文件的第N个字节开始读取")
        offset_info_label.setStyleSheet("color: gray; font-size: 9pt;")
        file_offset_layout.addWidget(offset_info_label)
        
        self.row_offset_spin = QSpinBox()
        self.row_offset_spin.setMinimum(0)
        self.row_offset_spin.setMaximum(100000000)  # 增加最大值以支持大文件
        self.row_offset_spin.setValue(0)
        self.row_offset_spin.setSuffix(" 字节")
        self.row_offset_spin.valueChanged.connect(self._on_row_offset_changed)
        
        file_offset_layout.addWidget(self.row_offset_spin)
        file_offset_group.setLayout(file_offset_layout)
        main_layout.addWidget(file_offset_group)
        
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
        data = self.resolution_combo.currentData()
        
        # 如果选择了"自定义..."选项
        if data is None:
            self._show_custom_resolution_dialog()
        else:
            width, height = data
            self.resolution_changed.emit(width, height)
    
    def _show_custom_resolution_dialog(self) -> None:
        """显示自定义分辨率对话框"""
        dialog = CustomResolutionDialog(self)
        
        # 如果之前有自定义分辨率，使用它作为默认值
        if self._custom_resolution:
            dialog.set_resolution(*self._custom_resolution)
        
        if dialog.exec_() == QDialog.Accepted:
            width, height = dialog.get_resolution()
            self._custom_resolution = (width, height)
            
            # 更新下拉框
            self._update_custom_resolution_in_combo(width, height)
            
            # 发送信号
            self.resolution_changed.emit(width, height)
        else:
            # 用户取消，恢复到之前的选择
            if self.resolution_combo.currentData() is None:
                # 如果当前是"自定义..."，恢复到默认的640×512
                self.resolution_combo.setCurrentIndex(1)
    
    def _update_custom_resolution_in_combo(self, width: int, height: int) -> None:
        """更新下拉框中的自定义分辨率项
        
        Args:
            width: 宽度
            height: 高度
        """
        # 查找是否已经有自定义分辨率项
        custom_index = -1
        for i in range(self.resolution_combo.count()):
            item_text = self.resolution_combo.itemText(i)
            if item_text.startswith("自定义:"):
                custom_index = i
                break
        
        # 如果没有，在"自定义..."之前插入
        if custom_index == -1:
            custom_index = self.resolution_combo.count() - 1
            self.resolution_combo.insertItem(custom_index, f"自定义: {width}×{height}", (width, height))
        else:
            # 更新现有项
            self.resolution_combo.setItemText(custom_index, f"自定义: {width}×{height}")
            self.resolution_combo.setItemData(custom_index, (width, height))
        
        # 选择自定义分辨率项
        self.resolution_combo.setCurrentIndex(custom_index)
    
    def _on_bit_depth_changed(self) -> None:
        """位深度改变时的处理函数"""
        bit_depth = self.bit_depth_group.checkedId()
        
        # 根据位深度启用/禁用数据类型选择
        if bit_depth == 16:
            self.data_type_group_widget.setEnabled(True)
        else:  # 8位
            self.data_type_group_widget.setEnabled(False)
        
        self.bit_depth_changed.emit(bit_depth)
    
    def _on_data_type_changed(self) -> None:
        """数据类型改变时的处理函数"""
        is_signed = self.data_type_signed.isChecked()
        self.data_type_changed.emit(is_signed)
    
    def _on_endianness_changed(self) -> None:
        """字节序改变时的处理函数"""
        if self.endianness_little.isChecked():
            self.endianness_changed.emit('little')
        else:
            self.endianness_changed.emit('big')
    
    def _on_row_offset_changed(self, value: int) -> None:
        """文件偏移改变时的处理函数"""
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
    
    def get_data_type(self) -> bool:
        """获取当前选择的数据类型
        
        Returns:
            bool: True表示有符号，False表示无符号
        """
        return self.data_type_signed.isChecked()
    
    def get_endianness(self) -> str:
        """获取当前选择的字节序
        
        Returns:
            str: 'little'或'big'
        """
        return 'little' if self.endianness_little.isChecked() else 'big'
    
    def get_row_offset(self) -> int:
        """获取当前文件偏移值
        
        Returns:
            int: 文件偏移量（字节），从文件的第N个字节开始读取
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
            self.data_type_group_widget.setEnabled(False)
        elif bit_depth == 16:
            self.bit_depth_16.setChecked(True)
            self.data_type_group_widget.setEnabled(True)
    
    def set_data_type(self, is_signed: bool) -> None:
        """设置数据类型
        
        Args:
            is_signed: True表示有符号，False表示无符号
        """
        if is_signed:
            self.data_type_signed.setChecked(True)
        else:
            self.data_type_unsigned.setChecked(True)
    
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
        """设置文件偏移
        
        Args:
            offset: 文件偏移量（字节）
        """
        self.row_offset_spin.setValue(offset)


class CustomResolutionDialog(QDialog):
    """自定义分辨率对话框
    
    允许用户输入任意的图像宽度和高度。
    """
    
    def __init__(self, parent=None):
        """初始化对话框
        
        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        
        self.setWindowTitle("自定义分辨率")
        self.setModal(True)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # 宽度输入
        self.width_spin = QSpinBox()
        self.width_spin.setMinimum(1)
        self.width_spin.setMaximum(10000)
        self.width_spin.setValue(640)
        self.width_spin.setSuffix(" 像素")
        form_layout.addRow("宽度:", self.width_spin)
        
        # 高度输入
        self.height_spin = QSpinBox()
        self.height_spin.setMinimum(1)
        self.height_spin.setMaximum(10000)
        self.height_spin.setValue(512)
        self.height_spin.setSuffix(" 像素")
        form_layout.addRow("高度:", self.height_spin)
        
        layout.addLayout(form_layout)
        
        # 添加说明
        info_label = QLabel("请输入图像的宽度和高度（像素）")
        info_label.setStyleSheet("color: gray; font-size: 9pt;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 添加按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # 设置对话框大小
        self.setMinimumWidth(300)
    
    def _validate_and_accept(self) -> None:
        """验证输入并接受对话框"""
        width = self.width_spin.value()
        height = self.height_spin.value()
        
        # 验证分辨率是否合理
        if width < 1 or height < 1:
            QMessageBox.warning(
                self,
                "无效的分辨率",
                "宽度和高度必须大于0"
            )
            return
        
        if width > 10000 or height > 10000:
            QMessageBox.warning(
                self,
                "分辨率过大",
                "宽度和高度不能超过10000像素"
            )
            return
        
        # 验证通过，接受对话框
        self.accept()
    
    def get_resolution(self) -> tuple[int, int]:
        """获取用户输入的分辨率
        
        Returns:
            tuple[int, int]: (width, height)
        """
        return (self.width_spin.value(), self.height_spin.value())
    
    def set_resolution(self, width: int, height: int) -> None:
        """设置对话框中的分辨率值
        
        Args:
            width: 宽度
            height: 高度
        """
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)
