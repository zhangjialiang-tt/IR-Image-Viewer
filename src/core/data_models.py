"""数据模型定义

包含图像配置、文件信息和帧数据的数据类。
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class ImageConfig:
    """图像配置参数
    
    存储图像解析所需的所有配置参数，包括分辨率、位深度、字节序和行偏移。
    
    Attributes:
        width: 图像宽度（像素）
        height: 图像高度（像素）
        bit_depth: 位深度，8或16位
        endianness: 字节序，'little'（小端）或'big'（大端）
        row_offset: 文件偏移量（字节），从文件的第N个字节开始读取数据
    """
    width: int = 640
    height: int = 512
    bit_depth: int = 8  # 8 or 16
    endianness: str = 'little'  # 'little' or 'big'
    row_offset: int = 0  # file offset in bytes
    
    def validate(self) -> tuple[bool, str]:
        """验证配置参数的有效性
        
        Returns:
            tuple[bool, str]: (是否有效, 错误消息)
        """
        if self.width <= 0:
            return False, "宽度必须为正数"
        
        if self.height <= 0:
            return False, "高度必须为正数"
        
        if self.bit_depth not in [8, 16]:
            return False, "位深度必须为8或16"
        
        if self.endianness not in ['little', 'big']:
            return False, "字节序必须为'little'或'big'"
        
        if self.row_offset < 0:
            return False, "文件偏移量不能为负数"
        
        return True, ""
    
    def get_bytes_per_pixel(self) -> int:
        """返回每像素字节数
        
        Returns:
            int: 每像素占用的字节数
        """
        return self.bit_depth // 8


@dataclass
class FileInfo:
    """文件信息
    
    存储加载文件的元数据。
    
    Attributes:
        filepath: 文件完整路径
        filename: 文件名
        file_size: 文件大小（字节）
        total_frames: 总帧数
        is_memory_mapped: 是否使用内存映射
    """
    filepath: str
    filename: str
    file_size: int
    total_frames: int
    is_memory_mapped: bool


@dataclass
class FrameData:
    """帧数据
    
    表示单帧图像数据。
    
    Attributes:
        frame_index: 帧索引（从0开始）
        pixel_data: 像素数据数组
        width: 图像宽度
        height: 图像高度
        bit_depth: 位深度
    """
    frame_index: int
    pixel_data: np.ndarray
    width: int
    height: int
    bit_depth: int
    
    def to_qimage(self):
        """转换为QImage用于显示
        
        注意：此方法需要PyQt5支持，将在后续实现。
        
        Returns:
            QImage: Qt图像对象
        """
        # 此方法将在实现ImageView组件时完成
        raise NotImplementedError("to_qimage方法将在后续实现")
