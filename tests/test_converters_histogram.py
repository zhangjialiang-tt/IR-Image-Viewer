"""测试数据转换工具的直方图映射功能

验证16位图像的直方图映射能够正确增强对比度。
"""

import pytest
import numpy as np
from src.utils.converters import apply_histogram_mapping, numpy_to_qimage


class TestHistogramMapping:
    """测试直方图映射功能"""
    
    def test_histogram_mapping_basic(self):
        """测试基本的直方图映射"""
        # 创建一个使用小范围值的16位图像
        # 模拟真实红外图像：只使用1000-5000范围
        array = np.random.randint(1000, 5000, size=(100, 100), dtype=np.uint16)
        
        # 应用直方图映射
        result = apply_histogram_mapping(array)
        
        # 验证结果
        assert result.dtype == np.uint8
        assert result.shape == array.shape
        assert result.min() >= 0
        assert result.max() <= 255
        # 应该使用了大部分0-255范围（至少50%）
        assert result.max() - result.min() > 127
    
    def test_histogram_mapping_full_range(self):
        """测试已经使用全范围的图像"""
        # 创建使用全范围的图像
        array = np.random.randint(0, 65535, size=(100, 100), dtype=np.uint16)
        
        result = apply_histogram_mapping(array)
        
        assert result.dtype == np.uint8
        assert result.shape == array.shape
        # 应该映射到接近全范围
        assert result.max() > 200
        assert result.min() < 50
    
    def test_histogram_mapping_constant_image(self):
        """测试常数图像（所有像素值相同）"""
        # 创建常数图像
        array = np.full((100, 100), 1000, dtype=np.uint16)
        
        result = apply_histogram_mapping(array)
        
        assert result.dtype == np.uint8
        assert result.shape == array.shape
        # 常数图像应该映射到中间灰度值
        assert np.all(result == 128)
    
    def test_histogram_mapping_with_outliers(self):
        """测试包含异常值的图像"""
        # 创建主要在1000-5000范围的图像
        array = np.random.randint(1000, 5000, size=(100, 100), dtype=np.uint16)
        
        # 添加一些异常值
        array[0, 0] = 0
        array[0, 1] = 65535
        
        result = apply_histogram_mapping(array)
        
        # 百分位数方法应该忽略异常值
        assert result.dtype == np.uint8
        # 大部分图像应该有良好的对比度
        assert result[10:90, 10:90].max() - result[10:90, 10:90].min() > 100
    
    def test_numpy_to_qimage_16bit_with_histogram(self):
        """测试16位图像转QImage时使用直方图映射"""
        # 创建使用小范围的16位图像
        array = np.random.randint(1000, 5000, size=(100, 100), dtype=np.uint16)
        
        # 转换为QImage（默认使用直方图映射）
        qimage = numpy_to_qimage(array, bit_depth=16, use_histogram_mapping=True)
        
        assert qimage is not None
        assert qimage.width() == 100
        assert qimage.height() == 100
    
    def test_numpy_to_qimage_16bit_without_histogram(self):
        """测试16位图像转QImage时不使用直方图映射"""
        # 创建使用小范围的16位图像
        array = np.random.randint(1000, 5000, size=(100, 100), dtype=np.uint16)
        
        # 转换为QImage（不使用直方图映射）
        qimage = numpy_to_qimage(array, bit_depth=16, use_histogram_mapping=False)
        
        assert qimage is not None
        assert qimage.width() == 100
        assert qimage.height() == 100
    
    def test_histogram_mapping_preserves_relative_values(self):
        """测试直方图映射保持相对值关系"""
        # 创建有明确大小关系的图像
        array = np.array([
            [1000, 2000, 3000],
            [2000, 3000, 4000],
            [3000, 4000, 5000]
        ], dtype=np.uint16)
        
        result = apply_histogram_mapping(array)
        
        # 验证相对关系保持
        # 如果 a < b，则映射后 a' < b'
        assert result[0, 0] < result[0, 1] < result[0, 2]
        assert result[1, 0] < result[1, 1] < result[1, 2]
        assert result[2, 0] < result[2, 1] < result[2, 2]
    
    def test_8bit_image_with_histogram(self):
        """测试8位图像也可以使用直方图映射"""
        # 创建使用部分范围的8位图像
        array = np.random.randint(50, 150, size=(100, 100), dtype=np.uint8)
        
        result = apply_histogram_mapping(array)
        
        assert result.dtype == np.uint8
        assert result.shape == array.shape
        # 应该拉伸到更大的范围
        assert result.max() > 200
        assert result.min() < 50


class TestHistogramMappingEdgeCases:
    """测试直方图映射的边界情况"""
    
    def test_empty_array(self):
        """测试空数组"""
        array = np.array([], dtype=np.uint16).reshape(0, 0)
        
        result = apply_histogram_mapping(array)
        
        assert result.shape == (0, 0)
        assert result.dtype == np.uint8
    
    def test_single_pixel(self):
        """测试单像素图像"""
        array = np.array([[1000]], dtype=np.uint16)
        
        result = apply_histogram_mapping(array)
        
        assert result.shape == (1, 1)
        assert result[0, 0] == 128  # 常数图像映射到中间值
    
    def test_very_small_range(self):
        """测试非常小的值范围"""
        # 值范围只有10
        array = np.random.randint(1000, 1010, size=(100, 100), dtype=np.uint16)
        
        result = apply_histogram_mapping(array)
        
        assert result.dtype == np.uint8
        # 即使原始范围很小，也应该拉伸到可见范围
        assert result.max() - result.min() > 50
    
    def test_negative_values_in_float_array(self):
        """测试包含负值的浮点数组"""
        array = np.random.randn(100, 100) * 1000  # 包含负值
        
        result = apply_histogram_mapping(array)
        
        assert result.dtype == np.uint8
        assert result.min() >= 0
        assert result.max() <= 255


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
