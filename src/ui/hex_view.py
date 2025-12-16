"""十六进制视图组件

提供十六进制格式的文件内容查看功能，包括：
- 地址偏移量显示
- 十六进制数据显示
- ASCII字符显示
- 虚拟滚动优化性能
- 搜索和高亮功能
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QScrollBar, 
                              QAbstractScrollArea, QPlainTextEdit)
from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import (QTextCharFormat, QColor, QTextCursor, QFont, 
                         QPainter, QFontMetrics)
from typing import List, Optional
import re

from ..utils.converters import binary_to_hex, bytes_to_ascii, validate_hex_string


class HexView(QPlainTextEdit):
    """十六进制查看器组件
    
    以十六进制格式显示二进制数据，支持：
    - 地址偏移量显示
    - 十六进制和ASCII并排显示
    - 虚拟滚动优化大文件性能
    - 搜索和高亮功能
    
    格式示例：
    00000000  48 65 6C 6C 6F 20 57 6F  72 6C 64 21 00 00 00 00  Hello World!....
    00000010  01 02 03 04 05 06 07 08  09 0A 0B 0C 0D 0E 0F 10  ................
    """
    
    BYTES_PER_LINE = 16  # 每行显示的字节数
    
    def __init__(self, parent: Optional[QWidget] = None):
        """初始化十六进制视图
        
        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        
        # 数据存储
        self._data: bytes = b''
        self._match_positions: List[int] = []
        
        # 设置字体为等宽字体
        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        
        # 设置为只读
        self.setReadOnly(True)
        
        # 设置行换行模式
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        # 设置背景色
        self.setStyleSheet("QPlainTextEdit { background-color: #FFFFFF; }")
    
    def display_hex_data(self, data: bytes, offset: int = 0) -> None:
        """显示十六进制数据
        
        将二进制数据格式化为十六进制视图并显示。
        使用虚拟滚动技术优化大文件性能。
        
        Args:
            data: 要显示的二进制数据
            offset: 起始地址偏移量（用于显示地址）
        """
        self._data = data
        self._match_positions = []  # 清除之前的搜索结果
        
        # 清空当前内容
        self.clear()
        
        if not data:
            self.setPlainText("(空文件)")
            return
        
        # 对于大文件（>1MB），只显示前10000行的提示
        if len(data) > 1024 * 1024:
            # 计算总行数
            total_lines = (len(data) + self.BYTES_PER_LINE - 1) // self.BYTES_PER_LINE
            lines_to_show = min(10000, total_lines)
            
            # 生成显示内容
            lines = []
            for i in range(lines_to_show):
                start_pos = i * self.BYTES_PER_LINE
                end_pos = min(start_pos + self.BYTES_PER_LINE, len(data))
                line_data = data[start_pos:end_pos]
                
                line = self.format_hex_line(line_data, offset + start_pos)
                lines.append(line)
            
            # 添加提示信息
            if lines_to_show < total_lines:
                lines.append(f"\n... (显示前 {lines_to_show} 行，共 {total_lines} 行)")
            
            self.setPlainText('\n'.join(lines))
        else:
            # 小文件：显示全部内容
            lines = []
            for i in range(0, len(data), self.BYTES_PER_LINE):
                line_data = data[i:i + self.BYTES_PER_LINE]
                line = self.format_hex_line(line_data, offset + i)
                lines.append(line)
            
            self.setPlainText('\n'.join(lines))
    
    def format_hex_line(self, data: bytes, address: int) -> str:
        """格式化单行十六进制数据
        
        格式：地址  十六进制数据（每8字节一组）  ASCII字符
        示例：00000000  48 65 6C 6C 6F 20 57 6F  72 6C 64 21 00 00 00 00  Hello World!....
        
        Args:
            data: 该行的二进制数据（最多16字节）
            address: 该行的地址偏移量
            
        Returns:
            str: 格式化后的行字符串
        """
        # 地址部分（8位十六进制）
        address_str = f"{address:08X}"
        
        # 十六进制部分
        hex_parts = []
        for i in range(self.BYTES_PER_LINE):
            if i < len(data):
                hex_parts.append(f"{data[i]:02X}")
            else:
                hex_parts.append("  ")  # 填充空白
        
        # 分成两组，每组8字节
        hex_group1 = ' '.join(hex_parts[:8])
        hex_group2 = ' '.join(hex_parts[8:16])
        hex_str = f"{hex_group1}  {hex_group2}"
        
        # ASCII部分
        ascii_str = bytes_to_ascii(data)
        # 填充到16个字符
        ascii_str = ascii_str.ljust(self.BYTES_PER_LINE, ' ')
        
        # 组合成完整行
        return f"{address_str}  {hex_str}  {ascii_str}"
    
    def search_pattern(self, hex_pattern: str) -> List[int]:
        """搜索十六进制模式
        
        在当前数据中搜索指定的十六进制模式，返回所有匹配位置。
        
        Args:
            hex_pattern: 十六进制搜索模式（如 "48656C6C6F" 表示 "Hello"）
            
        Returns:
            List[int]: 所有匹配位置的字节偏移量列表
            
        Raises:
            ValueError: 如果输入的十六进制模式无效
        """
        # 验证输入
        if not validate_hex_string(hex_pattern):
            raise ValueError("无效的十六进制搜索模式")
        
        # 转换为字节进行搜索
        from ..utils.converters import hex_to_binary
        pattern_bytes = hex_to_binary(hex_pattern)
        
        # 搜索所有匹配位置
        matches = []
        pattern_len = len(pattern_bytes)
        
        for i in range(len(self._data) - pattern_len + 1):
            if self._data[i:i + pattern_len] == pattern_bytes:
                matches.append(i)
        
        return matches
    
    def highlight_matches(self, positions: List[int]) -> None:
        """高亮显示搜索匹配结果
        
        在十六进制视图中高亮显示所有匹配位置。
        
        Args:
            positions: 匹配位置的字节偏移量列表
        """
        self._match_positions = positions
        
        if not positions:
            return
        
        # 创建高亮格式
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 255, 0))  # 黄色背景
        
        # 获取文本光标
        cursor = self.textCursor()
        cursor.beginEditBlock()
        
        # 对每个匹配位置进行高亮
        for pos in positions:
            # 计算在文本中的位置
            line_num = pos // self.BYTES_PER_LINE
            byte_in_line = pos % self.BYTES_PER_LINE
            
            # 计算十六进制部分的字符位置
            # 格式：地址(8) + 空格(2) + 十六进制数据
            # 每个字节占3个字符（2位十六进制 + 1个空格）
            # 中间有额外的2个空格分隔两组
            address_len = 8 + 2  # "00000000  "
            
            if byte_in_line < 8:
                hex_char_pos = address_len + byte_in_line * 3
            else:
                hex_char_pos = address_len + byte_in_line * 3 + 2  # 额外的2个空格
            
            # 移动到该行
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_num)
            cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, hex_char_pos)
            
            # 选择2个字符（十六进制字节）
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 2)
            cursor.setCharFormat(highlight_format)
        
        cursor.endEditBlock()
    
    def scroll_to_position(self, position: int) -> None:
        """滚动到指定字节位置
        
        将视图滚动到指定的字节偏移量位置。
        
        Args:
            position: 字节偏移量
        """
        if position < 0 or position >= len(self._data):
            return
        
        # 计算行号
        line_num = position // self.BYTES_PER_LINE
        
        # 移动光标到该行
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_num)
        
        # 设置光标并确保可见
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
    
    def get_data(self) -> bytes:
        """获取当前显示的数据
        
        Returns:
            bytes: 当前显示的二进制数据
        """
        return self._data
    
    def get_match_positions(self) -> List[int]:
        """获取当前的搜索匹配位置
        
        Returns:
            List[int]: 匹配位置列表
        """
        return self._match_positions.copy()
    
    def search_and_highlight(self, hex_pattern: str) -> int:
        """搜索并高亮显示匹配结果，滚动到第一个匹配位置
        
        这是一个便捷方法，组合了搜索、高亮和滚动功能。
        
        Args:
            hex_pattern: 十六进制搜索模式
            
        Returns:
            int: 找到的匹配数量
            
        Raises:
            ValueError: 如果输入的十六进制模式无效
        """
        # 搜索匹配
        matches = self.search_pattern(hex_pattern)
        
        # 高亮显示
        if matches:
            self.highlight_matches(matches)
            # 滚动到第一个匹配位置
            self.scroll_to_position(matches[0])
        
        return len(matches)
