"""测试大文件内存映射功能"""

import os
import tempfile
import mmap
import pytest
from src.core.file_loader import FileLoader


def test_large_file_uses_memory_mapping():
    """测试大文件使用内存映射"""
    # 创建一个大于100MB的临时文件
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        # 写入101MB的数据
        chunk_size = 1024 * 1024  # 1MB
        test_byte = b'X'
        for _ in range(101):
            f.write(test_byte * chunk_size)
        temp_path = f.name
    
    try:
        loader = FileLoader()
        data = loader.load_file(temp_path)
        
        # 验证使用了内存映射
        assert loader.use_memory_mapping()
        assert isinstance(data, mmap.mmap)
        
        # 验证文件大小
        expected_size = 101 * 1024 * 1024
        assert loader.get_file_size() == expected_size
        
        # 验证可以读取数据
        assert data[0:1] == b'X'
        assert data[1024*1024:1024*1024+1] == b'X'
        
        # 测试get_file_info
        file_info = loader.get_file_info()
        assert file_info.is_memory_mapped
        assert file_info.file_size == expected_size
        
        loader.close()
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_threshold_boundary():
    """测试100MB阈值边界"""
    # 测试刚好100MB的文件（应该使用内存映射）
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        chunk_size = 1024 * 1024  # 1MB
        for _ in range(100):
            f.write(b'A' * chunk_size)
        temp_path = f.name
    
    try:
        loader = FileLoader()
        data = loader.load_file(temp_path)
        
        # 100MB应该使用内存映射
        assert loader.use_memory_mapping()
        assert isinstance(data, mmap.mmap)
        
        loader.close()
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_below_threshold():
    """测试小于100MB的文件不使用内存映射"""
    # 创建99MB的文件
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        chunk_size = 1024 * 1024  # 1MB
        for _ in range(99):
            f.write(b'B' * chunk_size)
        temp_path = f.name
    
    try:
        loader = FileLoader()
        data = loader.load_file(temp_path)
        
        # 99MB不应该使用内存映射
        assert not loader.use_memory_mapping()
        assert isinstance(data, bytes)
        
        loader.close()
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
