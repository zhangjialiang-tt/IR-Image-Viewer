"""验证FileLoader满足所有需求

Requirements验证:
- 1.2: WHEN 用户选择一个二进制文件 THEN IR_Viewer SHALL 读取文件内容并存储在内存中
- 1.3: WHEN 文件大小超过100MB THEN IR_Viewer SHALL 使用内存映射技术加载文件以优化内存使用
- 1.4: WHEN 文件加载失败 THEN IR_Viewer SHALL 显示错误消息并保持当前状态不变
"""

import os
import tempfile
import mmap
import pytest
from src.core.file_loader import FileLoader


def test_requirement_1_2_read_file_content():
    """验证需求1.2：读取文件内容并存储在内存中"""
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        test_data = b'Binary image data' * 1000
        f.write(test_data)
        temp_path = f.name
    
    try:
        loader = FileLoader()
        data = loader.load_file(temp_path)
        
        # 验证文件内容被读取
        assert data is not None
        assert len(data) == len(test_data)
        assert data == test_data
        
        # 验证数据存储在内存中（可以访问）
        assert data[0:17] == b'Binary image data'
        
        loader.close()
    finally:
        os.unlink(temp_path)


def test_requirement_1_3_memory_mapping_for_large_files():
    """验证需求1.3：大文件使用内存映射"""
    # 创建一个大于100MB的文件
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        chunk_size = 1024 * 1024  # 1MB
        for _ in range(101):  # 101MB
            f.write(b'X' * chunk_size)
        temp_path = f.name
    
    try:
        loader = FileLoader()
        data = loader.load_file(temp_path)
        
        # 验证使用了内存映射
        assert loader.use_memory_mapping() is True
        assert isinstance(data, mmap.mmap)
        
        # 验证内存映射的数据可以访问
        assert data[0:1] == b'X'
        
        # 验证file_info反映了内存映射状态
        file_info = loader.get_file_info()
        assert file_info.is_memory_mapped is True
        
        loader.close()
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_requirement_1_4_error_handling_file_not_found():
    """验证需求1.4：文件加载失败时的错误处理（文件不存在）"""
    loader = FileLoader()
    
    # 尝试加载不存在的文件
    with pytest.raises(FileNotFoundError) as exc_info:
        loader.load_file("nonexistent_file.bin")
    
    # 验证错误消息包含文件路径
    assert "nonexistent_file.bin" in str(exc_info.value)
    
    # 验证状态保持不变（未加载任何文件）
    assert loader.get_file_size() == 0
    assert loader.use_memory_mapping() is False
    
    with pytest.raises(RuntimeError):
        loader.get_file_info()


def test_requirement_1_4_error_handling_permission_error():
    """验证需求1.4：文件加载失败时的错误处理（权限错误）"""
    # 创建一个文件
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        f.write(b'test data')
        temp_path = f.name
    
    try:
        # 移除读权限（在Windows上可能不完全生效，但测试逻辑是正确的）
        os.chmod(temp_path, 0o000)
        
        loader = FileLoader()
        
        # 尝试加载无权限的文件
        try:
            loader.load_file(temp_path)
            # 如果没有抛出异常，说明权限限制在当前系统上不生效
            # 这在某些系统上是正常的
        except PermissionError as e:
            # 验证错误消息
            assert "无权限访问文件" in str(e) or "Permission" in str(e)
            
            # 验证状态保持不变
            assert loader.get_file_size() == 0
    finally:
        # 恢复权限以便删除
        try:
            os.chmod(temp_path, 0o666)
            os.unlink(temp_path)
        except:
            pass


def test_requirement_1_4_error_handling_empty_file():
    """验证需求1.4：文件加载失败时的错误处理（空文件）"""
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        temp_path = f.name
        # 不写入任何数据
    
    try:
        loader = FileLoader()
        
        # 尝试加载空文件
        with pytest.raises(ValueError) as exc_info:
            loader.load_file(temp_path)
        
        # 验证错误消息
        assert "文件为空" in str(exc_info.value)
        
        # 验证状态保持不变
        with pytest.raises(RuntimeError):
            loader.get_file_info()
    finally:
        os.unlink(temp_path)


def test_requirement_1_4_error_handling_invalid_path():
    """验证需求1.4：文件加载失败时的错误处理（无效路径）"""
    loader = FileLoader()
    
    # 测试空路径
    with pytest.raises(ValueError) as exc_info:
        loader.load_file("")
    
    assert "文件路径不能为空" in str(exc_info.value)
    
    # 验证状态保持不变
    assert loader.get_file_size() == 0


def test_get_file_info_metadata():
    """验证get_file_info返回正确的元数据"""
    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
        test_data = b'Test metadata'
        f.write(test_data)
        temp_path = f.name
    
    try:
        loader = FileLoader()
        loader.load_file(temp_path)
        
        file_info = loader.get_file_info()
        
        # 验证元数据
        assert file_info.filepath == os.path.abspath(temp_path)
        assert file_info.filename == os.path.basename(temp_path)
        assert file_info.file_size == len(test_data)
        assert file_info.is_memory_mapped is False
        
        loader.close()
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
