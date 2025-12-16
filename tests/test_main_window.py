"""主窗口单元测试

测试IRImageViewer主窗口的基本功能。
"""

import pytest
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# 添加src目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.main_window import IRImageViewer
from src.core.data_models import ImageConfig


@pytest.fixture(scope='module')
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def main_window(qapp):
    """创建主窗口实例"""
    window = IRImageViewer()
    yield window
    window.close()


class TestMainWindowInitialization:
    """测试主窗口初始化"""
    
    def test_window_creation(self, main_window):
        """测试窗口创建"""
        assert main_window is not None
        assert main_window.windowTitle() == "红外图像二进制数据查看器"
    
    def test_menu_bar_exists(self, main_window):
        """测试菜单栏存在"""
        menubar = main_window.menuBar()
        assert menubar is not None
        
        # 检查菜单项
        actions = menubar.actions()
        menu_titles = [action.text() for action in actions]
        assert "文件(&F)" in menu_titles
        assert "视图(&V)" in menu_titles
        assert "帮助(&H)" in menu_titles
    
    def test_toolbar_exists(self, main_window):
        """测试工具栏存在"""
        from PyQt5.QtWidgets import QToolBar
        toolbars = main_window.findChildren(QToolBar)
        assert len(toolbars) > 0
    
    def test_status_bar_exists(self, main_window):
        """测试状态栏存在"""
        statusbar = main_window.statusBar()
        assert statusbar is not None
    
    def test_control_panel_exists(self, main_window):
        """测试控制面板存在"""
        assert main_window._control_panel is not None
    
    def test_tab_widget_exists(self, main_window):
        """测试标签页部件存在"""
        assert main_window._tab_widget is not None
        assert main_window._tab_widget.count() == 2
        
        # 检查标签页标题
        assert main_window._tab_widget.tabText(0) == "图像视图"
        assert main_window._tab_widget.tabText(1) == "十六进制视图"
    
    def test_image_view_exists(self, main_window):
        """测试图像视图存在"""
        assert main_window._image_view is not None
    
    def test_hex_view_exists(self, main_window):
        """测试十六进制视图存在"""
        assert main_window._hex_view is not None


class TestMainWindowMethods:
    """测试主窗口方法"""
    
    def test_update_status(self, main_window):
        """测试更新状态栏"""
        test_message = "测试消息"
        main_window.update_status(test_message)
        assert main_window._status_label.text() == test_message
    
    def test_show_error(self, main_window, qtbot):
        """测试显示错误对话框"""
        # 这个测试只验证方法可以调用，不实际显示对话框
        # 在实际测试中，我们会模拟对话框
        assert hasattr(main_window, 'show_error')
    
    def test_initial_config(self, main_window):
        """测试初始配置"""
        assert main_window._current_config is not None
        assert main_window._current_config.width == 640
        assert main_window._current_config.height == 512
        assert main_window._current_config.bit_depth == 8


class TestMainWindowSignalConnections:
    """测试信号连接"""
    
    def test_control_panel_signals_connected(self, main_window):
        """测试控制面板信号已连接"""
        # 验证控制面板信号已连接
        assert main_window._control_panel is not None
        
        # 测试分辨率改变
        main_window._control_panel.resolution_changed.emit(800, 600)
        assert main_window._current_config.width == 800
        assert main_window._current_config.height == 600
    
    def test_bit_depth_change(self, main_window):
        """测试位深度改变"""
        main_window._control_panel.bit_depth_changed.emit(16)
        assert main_window._current_config.bit_depth == 16
    
    def test_endianness_change(self, main_window):
        """测试字节序改变"""
        main_window._control_panel.endianness_changed.emit('big')
        assert main_window._current_config.endianness == 'big'
    
    def test_row_offset_change(self, main_window):
        """测试行偏移改变"""
        main_window._control_panel.row_offset_changed.emit(100)
        assert main_window._current_config.row_offset == 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
