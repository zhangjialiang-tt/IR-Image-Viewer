"""图像解析器测试

测试ImageParser的核心功能，包括8位/16位解析、字节序转换和行偏移。
"""

import pytest
import numpy as np
from src.core.image_parser import ImageParser
from src.core.data_models import ImageConfig


class TestImageParserBasic:
    """基本功能测试"""
    
    def test_parse_8bit_image(self):
        """测试8位图像解析"""
        # 创建一个简单的4x4图像（16个像素）
        config = ImageConfig(width=4, height=4, bit_depth=8)
        parser = ImageParser(config)
        
        # 创建测试数据：0-15的连续值
        data = bytes(range(16))
        
        result = parser.parse_frame(data, frame_index=0)
        
        assert result.shape == (4, 4)
        assert result.dtype == np.uint8
        # 验证数据正确性
        expected = np.array(range(16), dtype=np.uint8).reshape(4, 4)
        np.testing.assert_array_equal(result, expected)
    
    def test_parse_16bit_little_endian(self):
        """测试16位小端图像解析"""
        config = ImageConfig(width=2, height=2, bit_depth=16, endianness='little')
        parser = ImageParser(config)
        
        # 创建测试数据：4个16位值 (0x0100, 0x0200, 0x0300, 0x0400)
        # 小端格式：低字节在前
        data = bytes([0x00, 0x01, 0x00, 0x02, 0x00, 0x03, 0x00, 0x04])
        
        result = parser.parse_frame(data, frame_index=0)
        
        assert result.shape == (2, 2)
        assert result.dtype == np.uint16
        expected = np.array([[256, 512], [768, 1024]], dtype=np.uint16)
        np.testing.assert_array_equal(result, expected)
    
    def test_parse_16bit_big_endian(self):
        """测试16位大端图像解析"""
        config = ImageConfig(width=2, height=2, bit_depth=16, endianness='big')
        parser = ImageParser(config)
        
        # 创建测试数据：4个16位值 (0x0100, 0x0200, 0x0300, 0x0400)
        # 大端格式：高字节在前
        data = bytes([0x01, 0x00, 0x02, 0x00, 0x03, 0x00, 0x04, 0x00])
        
        result = parser.parse_frame(data, frame_index=0)
        
        assert result.shape == (2, 2)
        # Check that it's a 16-bit unsigned integer (byte order may vary)
        assert result.dtype.kind == 'u' and result.dtype.itemsize == 2
        expected = np.array([[256, 512], [768, 1024]], dtype=np.uint16)
        np.testing.assert_array_equal(result, expected)
    
    def test_row_offset(self):
        """测试行偏移功能"""
        config = ImageConfig(width=2, height=2, bit_depth=8, row_offset=4)
        parser = ImageParser(config)
        
        # 前4个字节是偏移，后4个字节是实际图像数据
        data = bytes([0xFF, 0xFF, 0xFF, 0xFF, 1, 2, 3, 4])
        
        result = parser.parse_frame(data, frame_index=0)
        
        assert result.shape == (2, 2)
        expected = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        np.testing.assert_array_equal(result, expected)


class TestImageParserMultiFrame:
    """多帧测试"""
    
    def test_parse_multiple_frames(self):
        """测试解析多帧数据"""
        config = ImageConfig(width=2, height=2, bit_depth=8)
        parser = ImageParser(config)
        
        # 创建3帧数据，每帧4个字节
        data = bytes([
            1, 2, 3, 4,      # 第0帧
            5, 6, 7, 8,      # 第1帧
            9, 10, 11, 12    # 第2帧
        ])
        
        # 解析第0帧
        frame0 = parser.parse_frame(data, frame_index=0)
        expected0 = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        np.testing.assert_array_equal(frame0, expected0)
        
        # 解析第1帧
        frame1 = parser.parse_frame(data, frame_index=1)
        expected1 = np.array([[5, 6], [7, 8]], dtype=np.uint8)
        np.testing.assert_array_equal(frame1, expected1)
        
        # 解析第2帧
        frame2 = parser.parse_frame(data, frame_index=2)
        expected2 = np.array([[9, 10], [11, 12]], dtype=np.uint8)
        np.testing.assert_array_equal(frame2, expected2)


class TestImageParserCalculations:
    """计算方法测试"""
    
    def test_calculate_frame_size_8bit(self):
        """测试8位图像帧大小计算"""
        config = ImageConfig(width=640, height=512, bit_depth=8)
        parser = ImageParser(config)
        
        frame_size = parser.calculate_frame_size()
        
        assert frame_size == 640 * 512 * 1  # 327680 bytes
    
    def test_calculate_frame_size_16bit(self):
        """测试16位图像帧大小计算"""
        config = ImageConfig(width=640, height=512, bit_depth=16)
        parser = ImageParser(config)
        
        frame_size = parser.calculate_frame_size()
        
        assert frame_size == 640 * 512 * 2  # 655360 bytes
    
    def test_calculate_total_frames_no_offset(self):
        """测试总帧数计算（无偏移）"""
        config = ImageConfig(width=2, height=2, bit_depth=8, row_offset=0)
        parser = ImageParser(config)
        
        # 每帧4字节，总共12字节 = 3帧
        total_frames = parser.calculate_total_frames(12)
        
        assert total_frames == 3
    
    def test_calculate_total_frames_with_offset(self):
        """测试总帧数计算（有偏移）"""
        config = ImageConfig(width=2, height=2, bit_depth=8, row_offset=4)
        parser = ImageParser(config)
        
        # 前4字节偏移，剩余12字节 = 3帧
        total_frames = parser.calculate_total_frames(16)
        
        assert total_frames == 3
    
    def test_calculate_total_frames_partial_frame(self):
        """测试总帧数计算（包含不完整帧）"""
        config = ImageConfig(width=2, height=2, bit_depth=8)
        parser = ImageParser(config)
        
        # 每帧4字节，总共10字节 = 2完整帧 + 2字节（不完整）
        total_frames = parser.calculate_total_frames(10)
        
        assert total_frames == 2  # 只计算完整帧


class TestImageParserValidation:
    """参数验证测试"""
    
    def test_validate_parameters_valid(self):
        """测试有效参数验证"""
        config = ImageConfig(width=2, height=2, bit_depth=8)
        parser = ImageParser(config)
        
        is_valid, error_msg = parser.validate_parameters(file_size=100)
        
        assert is_valid is True
        assert error_msg == ""
    
    def test_validate_parameters_insufficient_data(self):
        """测试数据不足的验证"""
        config = ImageConfig(width=2, height=2, bit_depth=8)
        parser = ImageParser(config)
        
        # 需要4字节，但只有3字节
        is_valid, error_msg = parser.validate_parameters(file_size=3)
        
        assert is_valid is False
        assert "文件大小不足" in error_msg
    
    def test_validate_parameters_offset_exceeds_file_size(self):
        """测试偏移量超出文件大小"""
        config = ImageConfig(width=2, height=2, bit_depth=8, row_offset=100)
        parser = ImageParser(config)
        
        is_valid, error_msg = parser.validate_parameters(file_size=50)
        
        assert is_valid is False
        assert "行偏移量" in error_msg and "超出文件大小" in error_msg


class TestImageParserErrors:
    """错误处理测试"""
    
    def test_invalid_config_negative_width(self):
        """测试无效配置：负宽度"""
        config = ImageConfig(width=-1, height=2, bit_depth=8)
        
        with pytest.raises(ValueError, match="无效的配置参数"):
            ImageParser(config)
    
    def test_invalid_config_invalid_bit_depth(self):
        """测试无效配置：无效位深度"""
        config = ImageConfig(width=2, height=2, bit_depth=32)
        
        with pytest.raises(ValueError, match="无效的配置参数"):
            ImageParser(config)
    
    def test_parse_frame_invalid_index_negative(self):
        """测试无效帧索引：负数"""
        config = ImageConfig(width=2, height=2, bit_depth=8)
        parser = ImageParser(config)
        data = bytes(8)  # 2帧
        
        with pytest.raises(ValueError, match="帧索引.*超出范围"):
            parser.parse_frame(data, frame_index=-1)
    
    def test_parse_frame_invalid_index_too_large(self):
        """测试无效帧索引：超出范围"""
        config = ImageConfig(width=2, height=2, bit_depth=8)
        parser = ImageParser(config)
        data = bytes(8)  # 2帧
        
        with pytest.raises(ValueError, match="帧索引.*超出范围"):
            parser.parse_frame(data, frame_index=2)  # 只有0和1两帧
    
    def test_parse_frame_insufficient_data(self):
        """测试数据不足"""
        config = ImageConfig(width=2, height=2, bit_depth=8)
        parser = ImageParser(config)
        data = bytes(3)  # 需要4字节，但只有3字节
        
        # When data is insufficient, total_frames will be 0, so frame_index 0 will be out of range
        with pytest.raises(ValueError, match="帧索引.*超出范围"):
            parser.parse_frame(data, frame_index=0)
