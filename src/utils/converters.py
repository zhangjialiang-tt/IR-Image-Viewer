"""数据转换工具

提供各种数据格式转换功能，包括：
- 二进制到十六进制转换
- 十六进制到二进制转换
- 字节到ASCII字符转换
- NumPy数组到QImage转换
"""

import numpy as np
from typing import Union


def binary_to_hex(data: bytes) -> str:
    """将二进制数据转换为十六进制字符串
    
    Args:
        data: 二进制数据
        
    Returns:
        str: 十六进制字符串（大写，无前缀）
        
    Example:
        >>> binary_to_hex(b'\x01\x02\x03')
        '010203'
    """
    return data.hex().upper()


def hex_to_binary(hex_string: str) -> bytes:
    """将十六进制字符串转换为二进制数据
    
    Args:
        hex_string: 十六进制字符串（可以包含空格）
        
    Returns:
        bytes: 二进制数据
        
    Raises:
        ValueError: 如果输入不是有效的十六进制字符串
        
    Example:
        >>> hex_to_binary('010203')
        b'\x01\x02\x03'
    """
    # 移除空格
    hex_string = hex_string.replace(' ', '')
    
    # 验证输入
    if len(hex_string) % 2 != 0:
        raise ValueError("十六进制字符串长度必须为偶数")
    
    try:
        return bytes.fromhex(hex_string)
    except ValueError as e:
        raise ValueError(f"无效的十六进制字符串: {e}")


def byte_to_ascii(byte_value: int) -> str:
    """将字节值转换为ASCII字符表示
    
    可打印字符（32-126）显示为对应字符，其他显示为'.'
    
    Args:
        byte_value: 字节值（0-255）
        
    Returns:
        str: ASCII字符或'.'
        
    Example:
        >>> byte_to_ascii(65)
        'A'
        >>> byte_to_ascii(10)
        '.'
    """
    if 32 <= byte_value <= 126:
        return chr(byte_value)
    return '.'


def bytes_to_ascii(data: bytes) -> str:
    """将字节序列转换为ASCII字符串表示
    
    Args:
        data: 字节数据
        
    Returns:
        str: ASCII字符串表示
        
    Example:
        >>> bytes_to_ascii(b'Hello\x00World')
        'Hello.World'
    """
    return ''.join(byte_to_ascii(b) for b in data)


def numpy_to_qimage(array: np.ndarray, bit_depth: int = 8):
    """将NumPy数组转换为QImage对象
    
    支持8位和16位灰度图像。
    
    Args:
        array: NumPy数组，形状为(height, width)
        bit_depth: 位深度，8或16
        
    Returns:
        QImage: Qt图像对象
        
    Raises:
        ValueError: 如果数组维度不正确或位深度无效
        ImportError: 如果PyQt5未安装
    """
    try:
        from PyQt5.QtGui import QImage
    except ImportError:
        raise ImportError("需要安装PyQt5才能使用此功能")
    
    # 验证输入
    if array.ndim != 2:
        raise ValueError(f"数组必须是二维的，当前维度: {array.ndim}")
    
    if bit_depth not in [8, 16]:
        raise ValueError(f"位深度必须为8或16，当前值: {bit_depth}")
    
    height, width = array.shape
    
    if bit_depth == 8:
        # 8位图像：确保数据类型为uint8
        if array.dtype != np.uint8:
            # 归一化到0-255范围
            array = array.astype(np.float64)
            array = (array - array.min()) / (array.max() - array.min() + 1e-10) * 255
            array = array.astype(np.uint8)
        
        # 创建QImage（灰度格式）
        bytes_per_line = width
        qimage = QImage(array.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        
    else:  # 16位
        # 16位图像：转换为8位显示
        if array.dtype != np.uint16:
            array = array.astype(np.uint16)
        
        # 归一化到0-255范围
        array_normalized = (array.astype(np.float64) / 65535.0 * 255).astype(np.uint8)
        
        bytes_per_line = width
        qimage = QImage(array_normalized.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
    
    # 重要：复制数据以避免内存问题
    return qimage.copy()


def validate_hex_string(hex_string: str) -> bool:
    """验证十六进制字符串的有效性
    
    有效的十六进制字符串应该：
    1. 只包含十六进制字符（0-9, a-f, A-F）
    2. 长度为偶数（可以忽略空格）
    
    Args:
        hex_string: 待验证的字符串
        
    Returns:
        bool: 是否为有效的十六进制字符串
    """
    # 移除空格
    hex_string = hex_string.replace(' ', '')
    
    # 检查长度
    if len(hex_string) == 0 or len(hex_string) % 2 != 0:
        return False
    
    # 检查字符
    valid_chars = set('0123456789abcdefABCDEF')
    return all(c in valid_chars for c in hex_string)
