"""错误处理器

提供统一的错误处理和验证功能。
"""

from typing import Optional
from src.core.data_models import ImageConfig


class ErrorHandler:
    """错误处理器类
    
    提供文件错误、解析错误的处理方法，以及配置验证功能。
    """
    
    @staticmethod
    def handle_file_error(error: Exception, filepath: str) -> str:
        """处理文件相关错误
        
        根据不同的异常类型生成相应的错误消息。
        
        Args:
            error: 捕获的异常对象
            filepath: 文件路径
            
        Returns:
            str: 格式化的错误消息
            
        Requirements: 1.4, 8.2, 9.1, 9.5
        """
        if isinstance(error, FileNotFoundError):
            return f"文件未找到: {filepath}"
        elif isinstance(error, PermissionError):
            return f"无权限访问文件: {filepath}"
        elif isinstance(error, IsADirectoryError):
            return f"指定路径是目录而非文件: {filepath}"
        elif isinstance(error, IOError):
            return f"文件读取失败: {filepath} - {str(error)}"
        elif isinstance(error, OSError):
            return f"操作系统错误: {filepath} - {str(error)}"
        else:
            return f"文件加载失败: {filepath} - {str(error)}"
    
    @staticmethod
    def handle_parse_error(error: Exception, context: Optional[str] = None) -> str:
        """处理解析错误
        
        生成解析错误的友好提示消息。
        
        Args:
            error: 捕获的异常对象
            context: 可选的上下文信息（如"解析第5帧时"）
            
        Returns:
            str: 格式化的错误消息
            
        Requirements: 8.2, 8.5, 9.2, 9.3
        """
        context_str = f"{context}: " if context else ""
        
        if isinstance(error, ValueError):
            return f"{context_str}数据解析错误 - {str(error)}"
        elif isinstance(error, IndexError):
            return f"{context_str}数据访问超出范围 - {str(error)}"
        elif isinstance(error, MemoryError):
            return f"{context_str}内存不足，无法完成解析操作"
        elif isinstance(error, TypeError):
            return f"{context_str}数据类型错误 - {str(error)}"
        else:
            return f"{context_str}解析失败 - {str(error)}"
    
    @staticmethod
    def validate_config(config: ImageConfig, file_size: Optional[int] = None) -> tuple[bool, str]:
        """验证配置参数
        
        验证ImageConfig的有效性，并可选地检查与文件大小的兼容性。
        
        Args:
            config: 图像配置对象
            file_size: 可选的文件大小（字节），用于验证配置是否与文件兼容
            
        Returns:
            tuple[bool, str]: (是否有效, 错误消息)
            
        Requirements: 2.1, 2.2, 9.1, 9.2, 9.3
        """
        # 首先使用ImageConfig自身的验证方法
        is_valid, error_msg = config.validate()
        if not is_valid:
            return False, error_msg
        
        # 如果提供了文件大小，进行额外的兼容性检查
        if file_size is not None:
            if file_size == 0:
                return False, "文件为空，无法解析图像数据"
            
            # 计算单帧所需的字节数
            frame_size = config.width * config.height * config.get_bytes_per_pixel()
            
            # 考虑行偏移
            effective_frame_size = frame_size + config.row_offset
            
            if effective_frame_size > file_size:
                return False, f"文件大小不足以包含一帧完整图像（需要至少 {effective_frame_size} 字节，实际 {file_size} 字节）"
            
            if file_size < 0:
                return False, "文件大小不能为负数"
        
        return True, ""
    
    @staticmethod
    def show_error_dialog(error_message: str) -> None:
        """显示错误对话框
        
        在GUI环境中显示错误消息对话框。
        在非GUI环境中，将错误消息打印到标准错误输出。
        
        Args:
            error_message: 要显示的错误消息
            
        Requirements: 8.2, 8.5
        
        Note:
            此方法在GUI实现时将使用QMessageBox。
            当前实现为占位符，便于在没有GUI的情况下进行测试。
        """
        try:
            # 尝试导入PyQt5并显示对话框
            from PyQt5.QtWidgets import QMessageBox, QApplication
            
            # 检查是否有QApplication实例
            app = QApplication.instance()
            if app is None:
                # 如果没有GUI环境，打印到stderr
                import sys
                print(f"错误: {error_message}", file=sys.stderr)
            else:
                # 在GUI环境中显示对话框
                QMessageBox.critical(None, "错误", error_message)
        except ImportError:
            # 如果PyQt5未安装，打印到stderr
            import sys
            print(f"错误: {error_message}", file=sys.stderr)
    
    @staticmethod
    def show_warning_dialog(warning_message: str) -> None:
        """显示警告对话框
        
        在GUI环境中显示警告消息对话框。
        在非GUI环境中，将警告消息打印到标准输出。
        
        Args:
            warning_message: 要显示的警告消息
            
        Requirements: 8.5, 9.2
        
        Note:
            此方法在GUI实现时将使用QMessageBox。
            当前实现为占位符，便于在没有GUI的情况下进行测试。
        """
        try:
            # 尝试导入PyQt5并显示对话框
            from PyQt5.QtWidgets import QMessageBox, QApplication
            
            # 检查是否有QApplication实例
            app = QApplication.instance()
            if app is None:
                # 如果没有GUI环境，打印到stdout
                print(f"警告: {warning_message}")
            else:
                # 在GUI环境中显示对话框
                QMessageBox.warning(None, "警告", warning_message)
        except ImportError:
            # 如果PyQt5未安装，打印到stdout
            print(f"警告: {warning_message}")
