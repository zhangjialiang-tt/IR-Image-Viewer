"""红外图像查看器应用程序入口点

这是IR Image Viewer应用程序的主入口点。该应用程序用于加载、显示和分析
二进制格式的红外图像数据。

使用方法:
    python main.py [文件路径]

参数:
    文件路径 (可选): 启动时自动加载的二进制图像文件路径

示例:
    python main.py                          # 启动应用程序
    python main.py data/sample.bin          # 启动并加载指定文件
    python main.py --help                   # 显示帮助信息
"""

import sys
import argparse
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from src.ui.main_window import IRImageViewer


def parse_arguments():
    """解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的命令行参数对象
    """
    parser = argparse.ArgumentParser(
        description='红外图像二进制数据查看器 - 用于加载、显示和分析二进制格式的红外图像数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                          启动应用程序
  %(prog)s data/sample.bin          启动并加载指定文件
  %(prog)s -f data/image.raw        使用 -f 参数加载文件

支持的功能:
  - 多种图像分辨率 (640×512, 320×256, 1280×1024等)
  - 8位和16位灰度图像
  - 大端/小端字节序支持
  - 多帧图像播放
  - 十六进制数据查看和搜索
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        default=None,
        help='要加载的二进制图像文件路径'
    )
    
    parser.add_argument(
        '-f', '--file',
        dest='file_flag',
        metavar='FILE',
        help='要加载的二进制图像文件路径（替代位置参数）'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='IR Image Viewer 1.0.0'
    )
    
    return parser.parse_args()


def validate_file_path(filepath):
    """验证文件路径是否有效
    
    Args:
        filepath (str): 要验证的文件路径
        
    Returns:
        tuple: (bool, str) - (是否有效, 错误消息)
    """
    if not filepath:
        return True, ""
    
    if not os.path.exists(filepath):
        return False, f"文件不存在: {filepath}"
    
    if not os.path.isfile(filepath):
        return False, f"路径不是文件: {filepath}"
    
    if not os.access(filepath, os.R_OK):
        return False, f"无权限读取文件: {filepath}"
    
    return True, ""


def main():
    """主函数
    
    创建应用程序实例，解析命令行参数，初始化主窗口，
    并可选地加载指定的文件。
    
    Returns:
        int: 应用程序退出代码
    """
    # 解析命令行参数
    args = parse_arguments()
    
    # 确定要加载的文件路径（优先使用 -f 参数）
    filepath = args.file_flag if args.file_flag else args.file
    
    # 验证文件路径
    if filepath:
        is_valid, error_msg = validate_file_path(filepath)
        if not is_valid:
            print(f"错误: {error_msg}", file=sys.stderr)
            return 1
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("IR Image Viewer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("IR Image Viewer")
    
    # 创建主窗口
    window = IRImageViewer()
    
    # 显示窗口
    window.show()
    
    # 如果指定了文件路径，尝试加载文件
    if filepath:
        try:
            # 转换为绝对路径
            abs_filepath = os.path.abspath(filepath)
            # 加载文件
            success = window.load_file(abs_filepath)
            if not success:
                QMessageBox.warning(
                    window,
                    "文件加载失败",
                    f"无法加载文件: {filepath}\n请检查文件格式是否正确。"
                )
        except Exception as e:
            QMessageBox.critical(
                window,
                "错误",
                f"加载文件时发生错误: {str(e)}"
            )
    
    # 运行应用程序事件循环
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
