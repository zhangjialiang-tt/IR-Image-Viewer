"""图像解析器

负责将二进制数据解析为图像数据，支持不同的位深度、字节序和文件偏移。
"""

import numpy as np
from typing import Union
from .data_models import ImageConfig


class ImageParser:
    """图像解析器
    
    将二进制数据解析为图像数据，支持8位和16位灰度图像，
    可配置字节序和文件偏移（从文件的第N个字节开始读取）。
    
    Attributes:
        config: 图像配置参数
    """
    
    def __init__(self, config: ImageConfig):
        """初始化图像解析器
        
        Args:
            config: 图像配置参数
        
        Raises:
            ValueError: 如果配置参数无效
        """
        is_valid, error_msg = config.validate()
        if not is_valid:
            raise ValueError(f"无效的配置参数: {error_msg}")
        
        self.config = config
    
    def parse_frame(self, data: Union[bytes, memoryview], frame_index: int = 0) -> np.ndarray:
        """解析单帧图像数据
        
        从二进制数据中解析指定帧的图像数据。
        
        Args:
            data: 二进制数据（完整文件数据）
            frame_index: 帧索引（从0开始）
        
        Returns:
            np.ndarray: 解析后的图像数据数组，形状为 (height, width)
        
        Raises:
            ValueError: 如果帧索引无效或数据不足
        """
        frame_size = self.calculate_frame_size()
        total_frames = self.calculate_total_frames(len(data))
        
        if frame_index < 0 or frame_index >= total_frames:
            raise ValueError(
                f"帧索引 {frame_index} 超出范围 [0, {total_frames - 1}]"
            )
        
        # 计算帧的起始位置（考虑文件偏移）
        # 文件偏移 + 帧索引 * 帧大小
        frame_start = self.config.row_offset + frame_index * frame_size
        frame_end = frame_start + frame_size
        
        if frame_end > len(data):
            raise ValueError(
                f"数据不足：需要 {frame_end} 字节，但只有 {len(data)} 字节"
            )
        
        # 提取帧数据
        frame_data = data[frame_start:frame_end]
        
        # 根据位深度解析数据
        if self.config.bit_depth == 8:
            # 8位数据：每个字节是一个像素
            pixel_array = np.frombuffer(frame_data, dtype=np.uint8)
        else:  # 16位
            # 16位数据：每两个字节是一个像素
            dtype = np.dtype(np.uint16)
            
            # 设置字节序
            if self.config.endianness == 'big':
                dtype = dtype.newbyteorder('>')
            else:  # little
                dtype = dtype.newbyteorder('<')
            
            pixel_array = np.frombuffer(frame_data, dtype=dtype)
        
        # 重塑为二维数组 (height, width)
        try:
            image_array = pixel_array.reshape(self.config.height, self.config.width)
        except ValueError as e:
            raise ValueError(
                f"无法将数据重塑为 ({self.config.height}, {self.config.width}): {e}"
            )
        
        return image_array
    
    def calculate_frame_size(self) -> int:
        """计算单帧图像的字节大小
        
        Returns:
            int: 单帧图像占用的字节数
        """
        bytes_per_pixel = self.config.get_bytes_per_pixel()
        return self.config.width * self.config.height * bytes_per_pixel
    
    def calculate_total_frames(self, file_size: int) -> int:
        """计算文件中的总帧数
        
        Args:
            file_size: 文件大小（字节）
        
        Returns:
            int: 总帧数
        """
        frame_size = self.calculate_frame_size()
        
        # 考虑文件偏移后的可用数据大小
        available_size = file_size - self.config.row_offset
        
        if available_size <= 0:
            return 0
        
        # 计算完整帧数（向下取整）
        return available_size // frame_size
    
    def validate_parameters(self, file_size: int) -> tuple[bool, str]:
        """验证解析参数是否适用于给定的文件大小
        
        Args:
            file_size: 文件大小（字节）
        
        Returns:
            tuple[bool, str]: (是否有效, 错误消息)
        """
        # 首先验证配置本身
        is_valid, error_msg = self.config.validate()
        if not is_valid:
            return False, error_msg
        
        # 检查文件偏移是否超出文件大小
        if self.config.row_offset >= file_size:
            return False, f"文件偏移量 {self.config.row_offset} 超出文件大小 {file_size}"
        
        # 检查文件是否至少包含一帧完整图像
        frame_size = self.calculate_frame_size()
        available_size = file_size - self.config.row_offset
        
        if available_size < frame_size:
            return False, (
                f"文件大小不足以包含一帧完整图像：需要 {frame_size} 字节，"
                f"但只有 {available_size} 字节可用"
            )
        
        return True, ""
