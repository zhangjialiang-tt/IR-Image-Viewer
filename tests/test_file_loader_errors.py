"""测试FileLoader错误处理"""

import os
import tempfile
import pytest
from src.core.file_loader import FileLoader


def test_directory_instead_of_file():
    """测试传入目录而不是文件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        loader = FileLoader()
        with pytest.raises(ValueError, match="路径不是文件"):
            loader.load_file(temp_dir)


def test_get_file_info_before_loading():
    """测试在加载文件前调用get_file_info"""
    loader = FileLoader()
    with pytest.raises(RuntimeError, match="未加载文件"):
        loader.get_file_info()


def test_multiple_loads():
    """测试多次加载文件"""
    # 创建两个临时文件
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f1:
        f1.write(b'File 1 content')
        temp_path1 = f1.name
    
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f2:
        f2.write(b'File 2 content is different')
        temp_path2 = f2.name
    
    try:
        loader = FileLoader()
        
        # 加载第一个文件
        data1 = loader.load_file(temp_path1)
        assert data1 == b'File 1 content'
        size1 = loader.get_file_size()
        
        # 加载第二个文件（应该清理第一个文件的数据）
        data2 = loader.load_file(temp_path2)
        assert data2 == b'File 2 content is different'
        size2 = loader.get_file_size()
        
        # 验证大小不同
        assert size1 != size2
        
        # 验证file_info是第二个文件的
        file_info = loader.get_file_info()
        assert file_info.filename == os.path.basename(temp_path2)
        
        loader.close()
    finally:
        os.unlink(temp_path1)
        os.unlink(temp_path2)


def test_close_and_reuse():
    """测试关闭后重新使用"""
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        f.write(b'Test data')
        temp_path = f.name
    
    try:
        loader = FileLoader()
        
        # 第一次加载
        data1 = loader.load_file(temp_path)
        assert data1 == b'Test data'
        
        # 关闭
        loader.close()
        
        # 关闭后应该无法获取file_info
        with pytest.raises(RuntimeError):
            loader.get_file_info()
        
        # 重新加载
        data2 = loader.load_file(temp_path)
        assert data2 == b'Test data'
        
        loader.close()
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
