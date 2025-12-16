"""文件加载器模块

负责加载和管理二进制文件，支持小文件直接读取和大文件内存映射。
"""

import os
import mmap
from typing import Union, Optional
from pathlib import Path
from .data_models import FileInfo


class FileLoader:
    """文件加载器
    
    负责加载二进制文件并提供文件元数据。对于大于100MB的文件，
    自动使用内存映射技术以优化内存使用。
    
    Attributes:
        _filepath: 当前加载的文件路径
        _data: 文件数据（bytes或mmap对象）
        _file_size: 文件大小（字节）
        _is_memory_mapped: 是否使用内存映射
        _mmap_file: 内存映射文件对象（用于保持引用）
    """
    
    # 大文件阈值：100MB
    LARGE_FILE_THRESHOLD = 100 * 1024 * 1024
    
    def __init__(self):
        """初始化文件加载器"""
        self._filepath: Optional[str] = None
        self._data: Optional[Union[bytes, mmap.mmap]] = None
        self._file_size: int = 0
        self._is_memory_mapped: bool = False
        self._mmap_file: Optional[object] = None
    
    def load_file(self, filepath: str) -> bytes:
        """加载二进制文件
        
        根据文件大小自动选择加载策略：
        - 小于100MB：直接读取到内存
        - 大于等于100MB：使用内存映射
        
        Args:
            filepath: 文件路径
            
        Returns:
            bytes: 文件数据（bytes或mmap对象）
            
        Raises:
            FileNotFoundError: 文件不存在
            PermissionError: 无权限访问文件
            IOError: 文件读取失败
            ValueError: 文件路径为空或无效
        """
        # 验证文件路径
        if not filepath:
            raise ValueError("文件路径不能为空")
        
        filepath = str(Path(filepath).resolve())
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        # 检查是否是文件（而不是目录）
        if not os.path.isfile(filepath):
            raise ValueError(f"路径不是文件: {filepath}")
        
        # 检查文件权限
        if not os.access(filepath, os.R_OK):
            raise PermissionError(f"无权限访问文件: {filepath}")
        
        # 清理之前的数据
        self._cleanup()
        
        try:
            # 获取文件大小
            self._file_size = os.path.getsize(filepath)
            self._filepath = filepath
            
            # 检查文件是否为空
            if self._file_size == 0:
                raise ValueError("文件为空")
            
            # 根据文件大小选择加载策略
            if self._file_size >= self.LARGE_FILE_THRESHOLD:
                # 大文件：使用内存映射
                self._data = self._load_with_memory_mapping(filepath)
                self._is_memory_mapped = True
            else:
                # 小文件：直接读取
                self._data = self._load_directly(filepath)
                self._is_memory_mapped = False
            
            return self._data
            
        except (FileNotFoundError, PermissionError, ValueError):
            # 重新抛出已知的异常
            raise
        except Exception as e:
            # 捕获其他异常并转换为IOError
            raise IOError(f"文件读取失败: {str(e)}") from e
    
    def _load_directly(self, filepath: str) -> bytes:
        """直接读取文件到内存
        
        Args:
            filepath: 文件路径
            
        Returns:
            bytes: 文件内容
            
        Raises:
            IOError: 读取失败
        """
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"文件读取失败: {str(e)}") from e
    
    def _load_with_memory_mapping(self, filepath: str) -> mmap.mmap:
        """使用内存映射加载文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            mmap.mmap: 内存映射对象
            
        Raises:
            IOError: 内存映射失败
        """
        try:
            # 打开文件并保持引用
            self._mmap_file = open(filepath, 'rb')
            # 创建内存映射（只读）
            return mmap.mmap(self._mmap_file.fileno(), 0, access=mmap.ACCESS_READ)
        except Exception as e:
            # 如果失败，关闭文件
            if self._mmap_file:
                self._mmap_file.close()
                self._mmap_file = None
            raise IOError(f"内存映射失败: {str(e)}") from e
    
    def get_file_size(self) -> int:
        """获取文件大小
        
        Returns:
            int: 文件大小（字节）
        """
        return self._file_size
    
    def get_file_info(self) -> FileInfo:
        """获取文件元数据
        
        Returns:
            FileInfo: 文件信息对象
            
        Raises:
            RuntimeError: 未加载文件
        """
        if self._filepath is None or self._data is None:
            raise RuntimeError("未加载文件")
        
        filename = os.path.basename(self._filepath)
        
        # 注意：total_frames 需要根据图像配置计算，这里暂时设为0
        # 实际值将在与ImageParser集成时计算
        return FileInfo(
            filepath=self._filepath,
            filename=filename,
            file_size=self._file_size,
            total_frames=0,  # 将在后续与ImageParser集成时计算
            is_memory_mapped=self._is_memory_mapped
        )
    
    def use_memory_mapping(self) -> bool:
        """检查是否使用内存映射
        
        Returns:
            bool: True表示使用内存映射，False表示直接读取
        """
        return self._is_memory_mapped
    
    def get_data(self) -> Optional[Union[bytes, mmap.mmap]]:
        """获取文件数据
        
        Returns:
            Optional[Union[bytes, mmap.mmap]]: 文件数据，如果未加载则返回None
        """
        return self._data
    
    def _cleanup(self):
        """清理资源"""
        # 关闭内存映射
        if self._data and isinstance(self._data, mmap.mmap):
            try:
                self._data.close()
            except:
                pass
        
        # 关闭文件
        if self._mmap_file:
            try:
                self._mmap_file.close()
            except:
                pass
        
        # 重置状态
        self._data = None
        self._mmap_file = None
        self._filepath = None
        self._file_size = 0
        self._is_memory_mapped = False
    
    def close(self):
        """关闭文件加载器并释放资源"""
        self._cleanup()
    
    def __del__(self):
        """析构函数，确保资源被释放"""
        self._cleanup()
