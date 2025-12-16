"""基本测试：验证FileLoader实现"""

import os
import tempfile
import pytest
from src.core.file_loader import FileLoader


def test_file_loader_can_be_instantiated():
    """测试FileLoader可以被实例化"""
    loader = FileLoader()
    assert loader is not None


def test_load_small_file():
    """测试加载小文件"""
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        test_data = b'Hello, World!' * 100  # 小文件
        f.write(test_data)
        temp_path = f.name
    
    try:
        loader = FileLoader()
        data = loader.load_file(temp_path)
        
        assert data == test_data
        assert loader.get_file_size() == len(test_data)
        assert not loader.use_memory_mapping()
        
        # 测试get_file_info
        file_info = loader.get_file_info()
        assert file_info.filepath == os.path.abspath(temp_path)
        assert file_info.file_size == len(test_data)
        assert not file_info.is_memory_mapped
        
        loader.close()
    finally:
        os.unlink(temp_path)


def test_file_not_found():
    """测试文件不存在错误"""
    loader = FileLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_file("nonexistent_file.bin")


def test_empty_filepath():
    """测试空文件路径"""
    loader = FileLoader()
    with pytest.raises(ValueError):
        loader.load_file("")


def test_empty_file():
    """测试空文件"""
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        temp_path = f.name
        # 不写入任何数据，创建空文件
    
    try:
        loader = FileLoader()
        with pytest.raises(ValueError, match="文件为空"):
            loader.load_file(temp_path)
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
