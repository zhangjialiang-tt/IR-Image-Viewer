"""主窗口模块

IR Image Viewer 应用程序的主窗口实现。
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QAction, QFileDialog, QMessageBox,
    QToolBar, QStatusBar, QLabel, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from typing import Optional
import os
import numpy as np

from .control_panel import ControlPanel
from .image_view import ImageView
from .hex_view import HexView
from .histogram_view import HistogramView
from ..core.file_loader import FileLoader
from ..core.image_parser import ImageParser
from ..core.frame_manager import FrameManager
from ..core.data_models import ImageConfig, FileInfo
from ..utils.error_handler import ErrorHandler


class IRImageViewer(QMainWindow):
    """红外图像查看器主窗口
    
    应用程序的主窗口，集成所有UI组件和核心功能。
    
    Attributes:
        _file_loader: 文件加载器
        _image_parser: 图像解析器
        _frame_manager: 帧管理器
        _current_config: 当前图像配置
        _current_file_info: 当前文件信息
        _current_data: 当前加载的文件数据
    """
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 核心组件
        self._file_loader = FileLoader()
        self._image_parser: Optional[ImageParser] = None
        self._frame_manager: Optional[FrameManager] = None
        
        # 当前状态
        self._current_config = ImageConfig()
        self._current_file_info: Optional[FileInfo] = None
        self._current_data: Optional[bytes] = None
        
        # UI组件
        self._control_panel: Optional[ControlPanel] = None
        self._image_view: Optional[ImageView] = None
        self._hex_view: Optional[HexView] = None
        self._histogram_view: Optional[HistogramView] = None
        self._tab_widget: Optional[QTabWidget] = None
        
        # 设置窗口
        self.setWindowTitle("红外图像二进制数据查看器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化UI
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """设置用户界面
        
        创建菜单栏、工具栏、状态栏和主显示区域。
        
        Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
        """
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建工具栏
        self._create_tool_bar()
        
        # 创建状态栏
        self._create_status_bar()
        
        # 创建中央部件
        self._create_central_widget()
        
    def _create_menu_bar(self) -> None:
        """创建菜单栏
        
        Requirements: 7.4
        """
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 打开文件
        open_action = QAction("打开(&O)...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("打开二进制图像文件")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出应用程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        # 放大
        zoom_in_action = QAction("放大(&I)", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.setStatusTip("放大图像")
        zoom_in_action.triggered.connect(self._on_zoom_in)
        view_menu.addAction(zoom_in_action)
        
        # 缩小
        zoom_out_action = QAction("缩小(&O)", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.setStatusTip("缩小图像")
        zoom_out_action.triggered.connect(self._on_zoom_out)
        view_menu.addAction(zoom_out_action)
        
        # 适应窗口
        fit_window_action = QAction("适应窗口(&F)", self)
        fit_window_action.setShortcut("Ctrl+0")
        fit_window_action.setStatusTip("调整图像大小以适应窗口")
        fit_window_action.triggered.connect(self._on_fit_to_window)
        view_menu.addAction(fit_window_action)
        
        # 搜索菜单
        search_menu = menubar.addMenu("搜索(&S)")
        
        # 十六进制搜索
        hex_search_action = QAction("十六进制搜索(&H)...", self)
        hex_search_action.setShortcut("Ctrl+F")
        hex_search_action.setStatusTip("在十六进制视图中搜索")
        hex_search_action.triggered.connect(self._on_hex_search)
        search_menu.addAction(hex_search_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 关于
        about_action = QAction("关于(&A)", self)
        about_action.setStatusTip("关于本应用程序")
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
        
    def _create_tool_bar(self) -> None:
        """创建工具栏
        
        Requirements: 7.5
        """
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 打开文件
        open_action = QAction("打开", self)
        open_action.setStatusTip("打开二进制图像文件")
        open_action.triggered.connect(self._on_open_file)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # 放大
        zoom_in_action = QAction("放大", self)
        zoom_in_action.setStatusTip("放大图像")
        zoom_in_action.triggered.connect(self._on_zoom_in)
        toolbar.addAction(zoom_in_action)
        
        # 缩小
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.setStatusTip("缩小图像")
        zoom_out_action.triggered.connect(self._on_zoom_out)
        toolbar.addAction(zoom_out_action)
        
        # 适应窗口
        fit_action = QAction("适应窗口", self)
        fit_action.setStatusTip("调整图像大小以适应窗口")
        fit_action.triggered.connect(self._on_fit_to_window)
        toolbar.addAction(fit_action)
        
        toolbar.addSeparator()
        
        # 播放
        play_action = QAction("播放", self)
        play_action.setStatusTip("播放动画")
        play_action.triggered.connect(self._on_play)
        toolbar.addAction(play_action)
        
        # 暂停
        pause_action = QAction("暂停", self)
        pause_action.setStatusTip("暂停播放")
        pause_action.triggered.connect(self._on_pause)
        toolbar.addAction(pause_action)
        
        toolbar.addSeparator()
        
        # 十六进制搜索
        search_action = QAction("搜索", self)
        search_action.setStatusTip("在十六进制视图中搜索")
        search_action.triggered.connect(self._on_hex_search)
        toolbar.addAction(search_action)
        
    def _create_status_bar(self) -> None:
        """创建状态栏
        
        Requirements: 7.1, 8.3, 8.4
        """
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        
        # 创建状态栏标签
        self._status_label = QLabel("就绪")
        self._status_bar.addWidget(self._status_label)
        
        # 文件信息标签
        self._file_info_label = QLabel("")
        self._status_bar.addPermanentWidget(self._file_info_label)
        
        # 像素信息标签
        self._pixel_info_label = QLabel("")
        self._status_bar.addPermanentWidget(self._pixel_info_label)
        
    def _create_central_widget(self) -> None:
        """创建中央部件
        
        创建主显示区域，包括控制面板和标签页视图。
        
        Requirements: 7.1, 7.2, 7.3
        """
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局（水平布局）
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧：控制面板
        self._control_panel = ControlPanel()
        self._control_panel.setMaximumWidth(300)
        main_layout.addWidget(self._control_panel)
        
        # 右侧：标签页视图
        self._tab_widget = QTabWidget()
        
        # 图像视图标签页
        self._image_view = ImageView()
        self._tab_widget.addTab(self._image_view, "图像视图")
        
        # 十六进制视图标签页
        self._hex_view = HexView()
        self._tab_widget.addTab(self._hex_view, "十六进制视图")
        
        # 直方图视图标签页
        self._histogram_view = HistogramView()
        self._tab_widget.addTab(self._histogram_view, "直方图")
        
        main_layout.addWidget(self._tab_widget, 1)  # 标签页占据剩余空间
        
        # 连接控制面板信号
        self._connect_control_panel_signals()
        
        # 连接图像视图信号
        self._image_view.pixel_info_changed.connect(self._on_pixel_info_changed)
        
    def _connect_control_panel_signals(self) -> None:
        """连接控制面板信号到处理函数"""
        self._control_panel.resolution_changed.connect(self._on_resolution_changed)
        self._control_panel.bit_depth_changed.connect(self._on_bit_depth_changed)
        self._control_panel.data_type_changed.connect(self._on_data_type_changed)
        self._control_panel.endianness_changed.connect(self._on_endianness_changed)
        self._control_panel.row_offset_changed.connect(self._on_row_offset_changed)
        self._control_panel.frame_changed.connect(self._on_frame_changed)
        self._control_panel.play_clicked.connect(self._on_play)
        self._control_panel.pause_clicked.connect(self._on_pause)
        
    def load_file(self, filepath: str = None) -> bool:
        """加载二进制图像文件
        
        如果未提供文件路径，则显示文件选择对话框。
        
        Args:
            filepath: 文件路径，如果为None则显示对话框
            
        Returns:
            bool: 加载成功返回True，否则返回False
            
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        # 如果未提供文件路径，显示文件选择对话框
        if filepath is None:
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                "打开二进制图像文件",
                "",
                "所有文件 (*);;二进制文件 (*.bin *.raw *.dat)"
            )
            
            if not filepath:
                return False  # 用户取消
        
        try:
            # 更新状态
            self.update_status("正在加载文件...")
            
            # 加载文件
            self._current_data = self._file_loader.load_file(filepath)
            
            # 获取文件信息
            self._current_file_info = self._file_loader.get_file_info()
            
            # 创建图像解析器
            self._image_parser = ImageParser(self._current_config)
            
            # 验证参数
            is_valid, error_msg = self._image_parser.validate_parameters(
                self._current_file_info.file_size
            )
            
            if not is_valid:
                self.show_error(f"配置参数无效: {error_msg}")
                return False
            
            # 计算总帧数
            total_frames = self._image_parser.calculate_total_frames(
                self._current_file_info.file_size
            )
            self._current_file_info.total_frames = total_frames
            
            # 创建帧管理器
            if total_frames > 0:
                self._frame_manager = FrameManager(total_frames)
                self._frame_manager.frame_changed.connect(self._on_frame_manager_changed)
            
            # 更新控制面板
            self._control_panel.update_frame_info(0, total_frames)
            
            # 显示第一帧
            self._display_current_frame()
            
            # 显示十六进制数据（只显示当前图像数据范围）
            self._update_hex_view()
            
            # 更新状态栏
            self._update_file_info_display()
            self.update_status(f"文件加载成功: {self._current_file_info.filename}")
            
            return True
            
        except Exception as e:
            error_msg = ErrorHandler.handle_file_error(e, filepath)
            self.show_error(error_msg)
            self.update_status("文件加载失败")
            return False
    
    def _display_current_frame(self) -> None:
        """显示当前帧图像"""
        if self._image_parser is None or self._current_data is None:
            return
        
        try:
            # 获取当前帧索引
            frame_index = 0
            if self._frame_manager is not None:
                frame_index = self._frame_manager.get_current_frame()
            
            # 解析帧数据
            image_data = self._image_parser.parse_frame(self._current_data, frame_index)
            
            # 显示图像
            self._image_view.display_image(image_data, self._current_config.bit_depth)
            
            # 更新直方图
            self._update_histogram(image_data)
            
        except Exception as e:
            error_msg = ErrorHandler.handle_parse_error(e, f"显示第{frame_index}帧")
            self.show_error(error_msg)
    
    def _update_histogram(self, image_data: np.ndarray) -> None:
        """更新直方图视图
        
        显示当前帧的像素值分布直方图。
        
        Args:
            image_data: 当前帧的图像数据
        """
        if self._histogram_view is None:
            return
        
        try:
            # 显示直方图
            self._histogram_view.display_histogram(
                image_data, 
                self._current_config.bit_depth,
                self._current_config.is_signed
            )
        except Exception as e:
            error_msg = ErrorHandler.handle_parse_error(e, "更新直方图")
            self.show_error(error_msg)
    
    def _update_hex_view(self) -> None:
        """更新十六进制视图
        
        只显示当前配置对应的图像数据范围（offset + image_length），
        而不是整个文件。
        """
        if self._image_parser is None or self._current_data is None:
            return
        
        try:
            # 计算当前帧的数据范围
            frame_size = self._image_parser.calculate_frame_size()
            offset = self._current_config.row_offset
            
            # 获取当前帧索引
            frame_index = 0
            if self._frame_manager is not None:
                frame_index = self._frame_manager.get_current_frame()
            
            # 计算起始和结束位置
            start_pos = offset + frame_index * frame_size
            end_pos = start_pos + frame_size
            
            # 确保不超出文件范围
            end_pos = min(end_pos, len(self._current_data))
            
            # 提取当前帧的数据
            frame_data = self._current_data[start_pos:end_pos]
            
            # 显示十六进制数据，使用实际的文件偏移量作为地址显示
            self._hex_view.display_hex_data(frame_data, offset=start_pos)
            
        except Exception as e:
            error_msg = ErrorHandler.handle_parse_error(e, "更新十六进制视图")
            self.show_error(error_msg)
    
    def _update_file_info_display(self) -> None:
        """更新文件信息显示
        
        Requirements: 1.5
        """
        if self._current_file_info is None:
            self._file_info_label.setText("")
            return
        
        # 格式化文件大小
        size_mb = self._current_file_info.file_size / (1024 * 1024)
        size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{self._current_file_info.file_size / 1024:.2f} KB"
        
        # 显示文件信息
        info_text = (
            f"文件: {self._current_file_info.filename} | "
            f"大小: {size_str} | "
            f"路径: {self._current_file_info.filepath}"
        )
        self._file_info_label.setText(info_text)
    
    def update_status(self, message: str) -> None:
        """更新状态栏消息
        
        Args:
            message: 状态消息
            
        Requirements: 8.3, 8.4
        """
        self._status_label.setText(message)
    
    def show_error(self, error_message: str) -> None:
        """显示错误对话框
        
        Args:
            error_message: 错误消息
            
        Requirements: 8.2, 8.5
        """
        QMessageBox.critical(self, "错误", error_message)
    
    # 槽函数：菜单和工具栏动作
    
    @pyqtSlot()
    def _on_open_file(self) -> None:
        """打开文件菜单项/工具栏按钮点击处理"""
        self.load_file()
    
    @pyqtSlot()
    def _on_zoom_in(self) -> None:
        """放大按钮点击处理"""
        self._image_view.zoom_in()
    
    @pyqtSlot()
    def _on_zoom_out(self) -> None:
        """缩小按钮点击处理"""
        self._image_view.zoom_out()
    
    @pyqtSlot()
    def _on_fit_to_window(self) -> None:
        """适应窗口按钮点击处理"""
        self._image_view.fit_to_window()
    
    @pyqtSlot()
    def _on_play(self) -> None:
        """播放按钮点击处理"""
        if self._frame_manager is not None:
            self._frame_manager.play(fps=10)
    
    @pyqtSlot()
    def _on_pause(self) -> None:
        """暂停按钮点击处理"""
        if self._frame_manager is not None:
            self._frame_manager.pause()
    
    @pyqtSlot()
    def _on_about(self) -> None:
        """关于菜单项点击处理"""
        QMessageBox.about(
            self,
            "关于红外图像查看器",
            "红外图像二进制数据查看器 v1.0\n\n"
            "用于加载、显示和分析二进制格式的红外图像数据。\n"
            "支持多种图像分辨率和数据格式（8位/16位灰度）。"
        )
    
    @pyqtSlot()
    def _on_hex_search(self) -> None:
        """十六进制搜索菜单项/工具栏按钮点击处理
        
        Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
        """
        if self._current_data is None:
            QMessageBox.warning(self, "警告", "请先加载文件")
            return
        
        # 切换到十六进制视图标签页
        self._tab_widget.setCurrentIndex(1)
        
        # 显示输入对话框
        hex_pattern, ok = QInputDialog.getText(
            self,
            "十六进制搜索",
            "请输入十六进制搜索模式（例如：48656C6C6F 表示 'Hello'）："
        )
        
        if not ok or not hex_pattern:
            return
        
        # 移除空格
        hex_pattern = hex_pattern.replace(' ', '')
        
        try:
            # 执行搜索并高亮显示
            match_count = self._hex_view.search_and_highlight(hex_pattern)
            
            if match_count > 0:
                # 显示搜索结果
                QMessageBox.information(
                    self,
                    "搜索结果",
                    f"找到 {match_count} 个匹配项"
                )
                self.update_status(f"找到 {match_count} 个匹配项")
            else:
                # 没有找到匹配
                QMessageBox.information(
                    self,
                    "搜索结果",
                    "未找到匹配项"
                )
                self.update_status("未找到匹配项")
                
        except ValueError as e:
            # 输入无效
            QMessageBox.warning(
                self,
                "输入错误",
                f"无效的十六进制搜索模式：{str(e)}"
            )
            self.update_status("搜索失败：输入无效")
    
    # 槽函数：控制面板信号
    
    @pyqtSlot(int, int)
    def _on_resolution_changed(self, width: int, height: int) -> None:
        """分辨率改变处理"""
        self._current_config.width = width
        self._current_config.height = height
        self._reparse_image()
    
    @pyqtSlot(int)
    def _on_bit_depth_changed(self, bit_depth: int) -> None:
        """位深度改变处理"""
        self._current_config.bit_depth = bit_depth
        self._reparse_image()
    
    @pyqtSlot(bool)
    def _on_data_type_changed(self, is_signed: bool) -> None:
        """数据类型改变处理"""
        self._current_config.is_signed = is_signed
        self._reparse_image()
    
    @pyqtSlot(str)
    def _on_endianness_changed(self, endianness: str) -> None:
        """字节序改变处理"""
        self._current_config.endianness = endianness
        self._reparse_image()
    
    @pyqtSlot(int)
    def _on_row_offset_changed(self, offset: int) -> None:
        """行偏移改变处理"""
        self._current_config.row_offset = offset
        self._reparse_image()
    
    @pyqtSlot(int)
    def _on_frame_changed(self, frame_index: int) -> None:
        """帧索引改变处理（来自控制面板）"""
        if self._frame_manager is not None:
            try:
                self._frame_manager.set_current_frame(frame_index)
            except ValueError as e:
                self.show_error(str(e))
    
    @pyqtSlot(int)
    def _on_frame_manager_changed(self, frame_index: int) -> None:
        """帧索引改变处理（来自帧管理器）"""
        # 更新控制面板显示
        if self._frame_manager is not None:
            total_frames = self._frame_manager.get_total_frames()
            self._control_panel.update_frame_info(frame_index, total_frames)
        
        # 显示新帧
        self._display_current_frame()
        
        # 更新十六进制视图（显示当前帧的数据）
        self._update_hex_view()
    
    @pyqtSlot(int, int, int)
    def _on_pixel_info_changed(self, x: int, y: int, value: int) -> None:
        """像素信息改变处理"""
        self._pixel_info_label.setText(f"坐标: ({x}, {y}) | 像素值: {value}")
    
    def _reparse_image(self) -> None:
        """重新解析图像
        
        当配置参数改变时，重新创建解析器并显示图像和十六进制数据。
        """
        if self._current_data is None:
            return
        
        try:
            # 创建新的图像解析器
            self._image_parser = ImageParser(self._current_config)
            
            # 验证参数
            is_valid, error_msg = self._image_parser.validate_parameters(
                len(self._current_data)
            )
            
            if not is_valid:
                self.show_error(f"配置参数无效: {error_msg}")
                return
            
            # 重新计算总帧数
            total_frames = self._image_parser.calculate_total_frames(len(self._current_data))
            
            # 更新帧管理器
            if total_frames > 0:
                if self._frame_manager is None:
                    self._frame_manager = FrameManager(total_frames)
                    self._frame_manager.frame_changed.connect(self._on_frame_manager_changed)
                else:
                    # 暂停播放
                    if self._frame_manager.is_playing():
                        self._frame_manager.pause()
                    # 更新总帧数
                    self._frame_manager.set_total_frames(total_frames)
            
            # 更新控制面板
            current_frame = 0
            if self._frame_manager is not None:
                current_frame = self._frame_manager.get_current_frame()
            self._control_panel.update_frame_info(current_frame, total_frames)
            
            # 显示当前帧
            self._display_current_frame()
            
            # 更新十六进制视图 - 只显示当前图像数据范围
            self._update_hex_view()
            
            self.update_status("图像已重新解析")
            
        except Exception as e:
            error_msg = ErrorHandler.handle_parse_error(e, "重新解析图像")
            self.show_error(error_msg)
    
    def closeEvent(self, event) -> None:
        """窗口关闭事件处理
        
        清理资源。
        """
        # 停止播放
        if self._frame_manager is not None and self._frame_manager.is_playing():
            self._frame_manager.pause()
        
        # 关闭文件加载器
        self._file_loader.close()
        
        event.accept()
