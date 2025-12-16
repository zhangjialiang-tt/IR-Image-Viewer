"""测试图像视图组件

验证ImageView组件的基本功能。
"""

import pytest
import numpy as np
from PyQt5.QtWidgets import QApplication
import sys

from src.ui.image_view import ImageView


@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def image_view(qapp):
    """创建ImageView实例"""
    view = ImageView()
    yield view
    view.close()


def test_image_view_initialization(image_view):
    """测试ImageView初始化"""
    assert image_view is not None
    assert image_view._image_data is None
    assert image_view._zoom_factor == 1.0


def test_display_image_8bit(image_view):
    """测试显示8位图像"""
    # 创建测试图像数据
    image_data = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    
    # 显示图像
    image_view.display_image(image_data, bit_depth=8)
    
    # 验证
    assert image_view._image_data is not None
    assert image_view._bit_depth == 8
    assert image_view._qimage is not None
    assert np.array_equal(image_view._image_data, image_data)


def test_display_image_16bit(image_view):
    """测试显示16位图像"""
    # 创建测试图像数据
    image_data = np.random.randint(0, 65536, (100, 100), dtype=np.uint16)
    
    # 显示图像
    image_view.display_image(image_data, bit_depth=16)
    
    # 验证
    assert image_view._image_data is not None
    assert image_view._bit_depth == 16
    assert image_view._qimage is not None


def test_display_image_invalid_data(image_view):
    """测试显示无效图像数据"""
    # 测试None
    with pytest.raises(ValueError, match="图像数据不能为None"):
        image_view.display_image(None)
    
    # 测试非二维数组
    with pytest.raises(ValueError, match="图像数据必须是二维数组"):
        image_view.display_image(np.array([1, 2, 3]))


def test_zoom_in(image_view):
    """测试放大功能"""
    # 创建并显示图像
    image_data = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    image_view.display_image(image_data)
    
    initial_zoom = image_view.get_zoom_factor()
    
    # 放大
    image_view.zoom_in()
    
    # 验证缩放因子增加
    assert image_view.get_zoom_factor() > initial_zoom
    assert image_view.get_zoom_factor() == pytest.approx(initial_zoom * 1.2)


def test_zoom_out(image_view):
    """测试缩小功能"""
    # 创建并显示图像
    image_data = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    image_view.display_image(image_data)
    
    initial_zoom = image_view.get_zoom_factor()
    
    # 缩小
    image_view.zoom_out()
    
    # 验证缩放因子减小
    assert image_view.get_zoom_factor() < initial_zoom
    assert image_view.get_zoom_factor() == pytest.approx(initial_zoom / 1.2)


def test_zoom_limits(image_view):
    """测试缩放限制"""
    # 创建并显示图像
    image_data = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    image_view.display_image(image_data)
    
    # 测试最大缩放
    for _ in range(20):
        image_view.zoom_in()
    assert image_view.get_zoom_factor() <= 10.0
    
    # 测试最小缩放
    for _ in range(40):
        image_view.zoom_out()
    assert image_view.get_zoom_factor() >= 0.1


def test_get_pixel_info(image_view):
    """测试获取像素信息"""
    # 创建已知的图像数据
    image_data = np.arange(100).reshape(10, 10).astype(np.uint8)
    image_view.display_image(image_data)
    
    # 测试有效坐标
    info = image_view.get_pixel_info(5, 3)
    assert info is not None
    x, y, value = info
    assert x == 5
    assert y == 3
    assert value == image_data[3, 5]
    
    # 测试边界坐标
    info = image_view.get_pixel_info(0, 0)
    assert info is not None
    assert info[2] == image_data[0, 0]
    
    info = image_view.get_pixel_info(9, 9)
    assert info is not None
    assert info[2] == image_data[9, 9]


def test_get_pixel_info_invalid_coordinates(image_view):
    """测试无效坐标的像素信息"""
    # 创建图像数据
    image_data = np.arange(100).reshape(10, 10).astype(np.uint8)
    image_view.display_image(image_data)
    
    # 测试超出范围的坐标
    assert image_view.get_pixel_info(-1, 5) is None
    assert image_view.get_pixel_info(5, -1) is None
    assert image_view.get_pixel_info(10, 5) is None
    assert image_view.get_pixel_info(5, 10) is None


def test_get_pixel_info_no_image(image_view):
    """测试没有图像时获取像素信息"""
    # 没有加载图像
    assert image_view.get_pixel_info(0, 0) is None


def test_clear(image_view):
    """测试清除图像"""
    # 创建并显示图像
    image_data = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    image_view.display_image(image_data)
    
    # 清除
    image_view.clear()
    
    # 验证
    assert image_view._image_data is None
    assert image_view._qimage is None
    assert image_view._pixmap is None
    assert image_view._zoom_factor == 1.0


def test_set_zoom_factor(image_view):
    """测试设置缩放因子"""
    # 创建并显示图像
    image_data = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    image_view.display_image(image_data)
    
    # 设置有效的缩放因子
    image_view.set_zoom_factor(2.0)
    assert image_view.get_zoom_factor() == 2.0
    
    image_view.set_zoom_factor(0.5)
    assert image_view.get_zoom_factor() == 0.5
    
    # 测试边界值
    image_view.set_zoom_factor(0.1)
    assert image_view.get_zoom_factor() == 0.1
    
    image_view.set_zoom_factor(10.0)
    assert image_view.get_zoom_factor() == 10.0
    
    # 测试超出范围的值（应该被忽略）
    image_view.set_zoom_factor(0.05)
    assert image_view.get_zoom_factor() == 10.0  # 保持之前的值
    
    image_view.set_zoom_factor(15.0)
    assert image_view.get_zoom_factor() == 10.0  # 保持之前的值
