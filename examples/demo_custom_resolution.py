"""演示自定义分辨率和文件偏移功能

这个脚本演示如何使用自定义分辨率和文件偏移功能。
"""

import numpy as np
import os


def create_sample_file_with_header(filepath, width, height, bit_depth=8, header_size=512):
    """创建一个带有文件头的示例二进制图像文件
    
    Args:
        filepath: 输出文件路径
        width: 图像宽度
        height: 图像高度
        bit_depth: 位深度（8或16）
        header_size: 文件头大小（字节）
    """
    # 创建文件头（模拟元数据）
    header = np.random.bytes(header_size)
    
    # 创建图像数据
    if bit_depth == 8:
        # 创建一个渐变图案
        image = np.zeros((height, width), dtype=np.uint8)
        for i in range(height):
            image[i, :] = int(255 * i / height)
    else:  # 16位
        # 创建一个更复杂的图案
        image = np.zeros((height, width), dtype=np.uint16)
        for i in range(height):
            for j in range(width):
                image[i, j] = int(65535 * (i + j) / (height + width))
    
    # 写入文件
    with open(filepath, 'wb') as f:
        f.write(header)  # 写入文件头
        f.write(image.tobytes())  # 写入图像数据
    
    return header_size


def main():
    """主函数"""
    print("=" * 70)
    print("自定义分辨率和文件偏移功能演示")
    print("=" * 70)
    
    # 创建输出目录
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 示例1：非标准分辨率的8位图像
    print("\n示例1：创建384×288的8位图像（带512字节文件头）")
    filepath1 = os.path.join(output_dir, "custom_384x288_8bit.bin")
    header_size1 = create_sample_file_with_header(filepath1, 384, 288, 8, 512)
    
    file_size1 = os.path.getsize(filepath1)
    image_size1 = 384 * 288 * 1
    
    print(f"  文件路径: {filepath1}")
    print(f"  文件大小: {file_size1} 字节")
    print(f"  文件头大小: {header_size1} 字节")
    print(f"  图像数据大小: {image_size1} 字节")
    print(f"\n  在IR Image Viewer中使用:")
    print(f"    1. 加载文件: {filepath1}")
    print(f"    2. 设置自定义分辨率: 384×288")
    print(f"    3. 设置位深度: 8位")
    print(f"    4. 设置文件偏移: {header_size1} 字节")
    
    # 示例2：非标准分辨率的16位图像
    print("\n示例2：创建1280×720的16位图像（带1024字节文件头）")
    filepath2 = os.path.join(output_dir, "custom_1280x720_16bit.bin")
    header_size2 = create_sample_file_with_header(filepath2, 1280, 720, 16, 1024)
    
    file_size2 = os.path.getsize(filepath2)
    image_size2 = 1280 * 720 * 2
    
    print(f"  文件路径: {filepath2}")
    print(f"  文件大小: {file_size2} 字节")
    print(f"  文件头大小: {header_size2} 字节")
    print(f"  图像数据大小: {image_size2} 字节")
    print(f"\n  在IR Image Viewer中使用:")
    print(f"    1. 加载文件: {filepath2}")
    print(f"    2. 设置自定义分辨率: 1280×720")
    print(f"    3. 设置位深度: 16位")
    print(f"    4. 设置文件偏移: {header_size2} 字节")
    
    # 示例3：无文件头的图像
    print("\n示例3：创建512×512的8位图像（无文件头）")
    filepath3 = os.path.join(output_dir, "custom_512x512_8bit_no_header.bin")
    
    # 创建图像数据（无文件头）
    image3 = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
    with open(filepath3, 'wb') as f:
        f.write(image3.tobytes())
    
    file_size3 = os.path.getsize(filepath3)
    
    print(f"  文件路径: {filepath3}")
    print(f"  文件大小: {file_size3} 字节")
    print(f"  文件头大小: 0 字节（无文件头）")
    print(f"\n  在IR Image Viewer中使用:")
    print(f"    1. 加载文件: {filepath3}")
    print(f"    2. 设置自定义分辨率: 512×512")
    print(f"    3. 设置位深度: 8位")
    print(f"    4. 设置文件偏移: 0 字节（默认）")
    
    print("\n" + "=" * 70)
    print("总结")
    print("=" * 70)
    print("""
自定义分辨率功能允许您：
✓ 输入任意宽度和高度（1-10000像素）
✓ 处理非标准分辨率的图像
✓ 保存自定义分辨率供重复使用

文件偏移功能允许您：
✓ 跳过文件头或元数据
✓ 从文件的任意位置开始读取
✓ 处理带有自定义格式的二进制文件

这两个功能结合使用，可以处理几乎任何格式的原始二进制图像数据！
    """)
    
    print(f"\n示例文件已创建在: {output_dir}/")
    print("您可以使用IR Image Viewer打开这些文件进行测试。")


if __name__ == '__main__':
    main()
