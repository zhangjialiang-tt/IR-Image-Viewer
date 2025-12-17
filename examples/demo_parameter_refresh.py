"""演示参数实时刷新功能

这个脚本演示当修改图像参数时，图像和十六进制视图如何自动刷新。
"""

import numpy as np
import os


def create_multi_resolution_file(filepath):
    """创建一个可以用多种分辨率解析的测试文件
    
    这个文件包含足够的数据，可以用不同的分辨率来解析。
    
    Args:
        filepath: 输出文件路径
    """
    # 创建512字节的文件头
    header = b'HEADER' + b'\x00' * 506
    
    # 创建足够大的图像数据（支持多种分辨率）
    # 使用1280×1024×2字节 = 2,621,440字节
    image_data = np.random.randint(1000, 5000, (1024, 1280), dtype=np.uint16)
    
    # 写入文件
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(image_data.tobytes())
    
    return len(header), image_data.nbytes


def main():
    """主函数"""
    print("=" * 70)
    print("参数实时刷新功能演示")
    print("=" * 70)
    
    # 创建输出目录
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建测试文件
    filepath = os.path.join(output_dir, "multi_resolution_test.bin")
    header_size, data_size = create_multi_resolution_file(filepath)
    
    total_size = header_size + data_size
    
    print(f"\n创建测试文件: {filepath}")
    print(f"  文件头大小: {header_size} 字节")
    print(f"  图像数据大小: {data_size} 字节")
    print(f"  总大小: {total_size} 字节")
    
    print("\n" + "=" * 70)
    print("使用说明")
    print("=" * 70)
    
    print("""
这个文件可以用多种方式解析，演示参数实时刷新功能：

1. 启动应用程序并加载文件:
   python main.py {filepath}

2. 尝试不同的配置（每次修改后图像和十六进制视图会自动刷新）:

   配置1: 640×512, 16位, 小端, 偏移512
   - 分辨率: 640×512
   - 位深度: 16位
   - 字节序: 小端
   - 文件偏移: 512
   - 结果: 显示640×512的图像
   - 十六进制视图: 显示512字节开始的640×512×2=655,360字节

   配置2: 320×256, 16位, 小端, 偏移512
   - 修改分辨率为: 320×256
   - 结果: 图像立即刷新为320×256
   - 十六进制视图: 自动更新，只显示320×256×2=163,840字节

   配置3: 1280×1024, 8位, 小端, 偏移512
   - 修改分辨率为: 1280×1024（自定义）
   - 修改位深度为: 8位
   - 结果: 图像立即刷新
   - 十六进制视图: 显示1280×1024×1=1,310,720字节

   配置4: 尝试不同的文件偏移
   - 修改文件偏移为: 0（包含文件头）
   - 修改文件偏移为: 512（跳过文件头）
   - 修改文件偏移为: 1024（从不同位置开始）
   - 结果: 每次修改后图像和十六进制视图立即更新

3. 观察实时刷新效果:
   - ✓ 修改参数后无需重新加载文件
   - ✓ 图像视图立即显示新的解析结果
   - ✓ 十六进制视图只显示当前配置对应的数据范围
   - ✓ 地址偏移量正确显示实际文件位置

4. 十六进制视图智能显示:
   - 只显示: 文件偏移 + 当前帧大小
   - 不显示: 整个文件
   - 优势: 
     * 更快的显示速度
     * 更清晰的数据对应关系
     * 更容易分析当前图像的原始数据
    """.format(filepath=filepath))
    
    print("\n" + "=" * 70)
    print("关键特性")
    print("=" * 70)
    
    print("""
1. 实时刷新
   - 修改任何参数（分辨率、位深度、字节序、文件偏移）
   - 图像和十六进制视图立即更新
   - 无需重新加载文件

2. 智能十六进制显示
   - 只显示当前图像数据范围
   - 地址偏移量显示实际文件位置
   - 便于分析和调试

3. 多帧支持
   - 切换帧时，十六进制视图也会更新
   - 显示当前帧对应的数据

4. 用户体验
   - 快速试错，找到正确参数
   - 实时反馈，所见即所得
   - 提高工作效率
    """)
    
    print(f"\n测试文件已创建: {filepath}")
    print("现在可以使用IR Image Viewer打开并测试参数实时刷新功能！")


if __name__ == '__main__':
    main()
