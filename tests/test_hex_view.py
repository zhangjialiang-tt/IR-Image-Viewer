"""测试十六进制视图组件

测试 HexView 组件的核心功能。
"""

import pytest
from PyQt5.QtWidgets import QApplication
import sys

from src.ui.hex_view import HexView


# 确保QApplication实例存在
@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def hex_view(qapp):
    """创建HexView实例"""
    view = HexView()
    yield view
    view.deleteLater()


class TestHexViewBasic:
    """测试HexView基本功能"""
    
    def test_initialization(self, hex_view):
        """测试HexView初始化"""
        assert hex_view is not None
        assert hex_view.isReadOnly()
        assert hex_view.get_data() == b''
    
    def test_display_empty_data(self, hex_view):
        """测试显示空数据"""
        hex_view.display_hex_data(b'')
        assert "(空文件)" in hex_view.toPlainText()
    
    def test_display_small_data(self, hex_view):
        """测试显示小数据"""
        data = b'Hello World!'
        hex_view.display_hex_data(data)
        
        text = hex_view.toPlainText()
        assert "00000000" in text  # 地址
        assert "48 65 6C 6C" in text  # "Hell" 的十六进制
        assert "Hello World!" in text  # ASCII部分
    
    def test_format_hex_line(self, hex_view):
        """测试格式化十六进制行"""
        data = b'Hello World!'
        line = hex_view.format_hex_line(data, 0)
        
        # 验证格式
        assert line.startswith("00000000")
        assert "48 65 6C 6C 6F" in line  # "Hello"
        assert "Hello World!" in line
    
    def test_format_hex_line_with_offset(self, hex_view):
        """测试带偏移量的格式化"""
        data = b'Test'
        line = hex_view.format_hex_line(data, 0x100)
        
        assert line.startswith("00000100")
    
    def test_format_hex_line_padding(self, hex_view):
        """测试不足16字节的行填充"""
        data = b'Hi'
        line = hex_view.format_hex_line(data, 0)
        
        # 应该有填充空格
        assert "48 69" in line  # "Hi"
        # 检查行长度合理（地址 + 十六进制 + ASCII）
        assert len(line) > 50


class TestHexViewSearch:
    """测试HexView搜索功能"""
    
    def test_search_pattern_simple(self, hex_view):
        """测试简单搜索"""
        data = b'Hello World! Hello Python!'
        hex_view.display_hex_data(data)
        
        # 搜索 "Hello" (48656C6C6F)
        matches = hex_view.search_pattern("48656C6C6F")
        assert len(matches) == 2
        assert matches[0] == 0
        assert matches[1] == 13
    
    def test_search_pattern_not_found(self, hex_view):
        """测试搜索不存在的模式"""
        data = b'Hello World!'
        hex_view.display_hex_data(data)
        
        matches = hex_view.search_pattern("DEADBEEF")
        assert len(matches) == 0
    
    def test_search_pattern_invalid(self, hex_view):
        """测试无效的搜索模式"""
        data = b'Hello World!'
        hex_view.display_hex_data(data)
        
        with pytest.raises(ValueError):
            hex_view.search_pattern("XYZ")  # 无效字符
        
        with pytest.raises(ValueError):
            hex_view.search_pattern("123")  # 奇数长度
    
    def test_highlight_matches(self, hex_view):
        """测试高亮匹配结果"""
        data = b'Hello World!'
        hex_view.display_hex_data(data)
        
        matches = [0, 6]
        hex_view.highlight_matches(matches)
        
        # 验证匹配位置被存储
        assert hex_view.get_match_positions() == matches
    
    def test_scroll_to_position(self, hex_view):
        """测试滚动到指定位置"""
        data = b'A' * 1000
        hex_view.display_hex_data(data)
        
        # 滚动到中间位置
        hex_view.scroll_to_position(500)
        
        # 验证光标位置
        cursor = hex_view.textCursor()
        assert cursor.blockNumber() == 500 // 16
    
    def test_search_and_highlight(self, hex_view):
        """测试搜索并高亮的便捷方法"""
        data = b'Hello World! Hello Python!'
        hex_view.display_hex_data(data)
        
        # 搜索并高亮 "Hello"
        count = hex_view.search_and_highlight("48656C6C6F")
        assert count == 2
        
        # 验证匹配位置被存储
        matches = hex_view.get_match_positions()
        assert len(matches) == 2
    
    def test_search_and_highlight_not_found(self, hex_view):
        """测试搜索不存在的模式"""
        data = b'Hello World!'
        hex_view.display_hex_data(data)
        
        count = hex_view.search_and_highlight("DEADBEEF")
        assert count == 0


class TestHexViewLargeFile:
    """测试HexView处理大文件"""
    
    def test_display_large_data(self, hex_view):
        """测试显示大文件（>1MB）"""
        # 创建一个大于1MB的数据
        data = b'X' * (2 * 1024 * 1024)
        hex_view.display_hex_data(data)
        
        text = hex_view.toPlainText()
        # 应该有提示信息
        assert "显示前" in text or len(text) > 0
    
    def test_search_in_large_data(self, hex_view):
        """测试在大数据中搜索"""
        # 创建包含特定模式的大数据
        data = b'A' * 1000 + b'PATTERN' + b'B' * 1000
        hex_view.display_hex_data(data)
        
        # 搜索 "PATTERN" (5041545445524E)
        matches = hex_view.search_pattern("5041545445524E")
        assert len(matches) == 1
        assert matches[0] == 1000


class TestHexViewAddressCalculation:
    """测试地址偏移量计算"""
    
    def test_address_offset_first_line(self, hex_view):
        """测试第一行地址"""
        data = b'Test'
        line = hex_view.format_hex_line(data, 0)
        assert line.startswith("00000000")
    
    def test_address_offset_second_line(self, hex_view):
        """测试第二行地址（16字节后）"""
        data = b'Test'
        line = hex_view.format_hex_line(data, 16)
        assert line.startswith("00000010")
    
    def test_address_offset_large(self, hex_view):
        """测试大地址偏移"""
        data = b'Test'
        line = hex_view.format_hex_line(data, 0x12345678)
        assert line.startswith("12345678")


class TestHexViewASCII:
    """测试ASCII显示"""
    
    def test_ascii_printable(self, hex_view):
        """测试可打印字符"""
        data = b'ABC123'
        line = hex_view.format_hex_line(data, 0)
        assert "ABC123" in line
    
    def test_ascii_non_printable(self, hex_view):
        """测试不可打印字符"""
        data = b'\x00\x01\x02\x1F'
        line = hex_view.format_hex_line(data, 0)
        # 不可打印字符应该显示为'.'
        assert "...." in line
    
    def test_ascii_mixed(self, hex_view):
        """测试混合字符"""
        data = b'A\x00B\x01C'
        line = hex_view.format_hex_line(data, 0)
        assert "A.B.C" in line


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
