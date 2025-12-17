"""演示有符号16位数据类型功能

这个脚本创建包含有符号和无符号16位数据的示例文件，
演示如何正确解析和显示它们。
"""

import numpy as np
import os


def create_signed_image_file(filepath):
    """创建包含有符号16位数据的图像文件
    
    模拟温度差异数据，包含正值和负值。
    
    Args:
        filepath: 输出文件路径
    """
    width, height = 640, 512
    
    # 创建一个包含正负值的图案
    # 模拟温度差异：-2000°C 到 +2000°C
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    # 创建一个径向渐变，中心为0，边缘为极值
    pattern = (X**2 + Y**2) * 2000 - 1000
    
    # 转换为int16
    image = pattern.astype(np.int16)
    
    # 写入文件
    with open(filepath, 'wb') as f:
        f.write(image.tobytes())
    
    return image


def create_unsigned_image_file(filepath):
    """创建包含无符号16位数据的图像文件
    
    模拟标准红外图像数据。
    
    Args:
        filepath: 输出文件路径
    """
    width, height = 640, 512
    
    # 创建一个渐变图案
    # 值范围：1000 到 5000
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    X, Y = np.meshgrid(x, y)
    
    # 创建图案
    pattern = (X + Y) / 2 * 4000 + 1000
    
    # 转换为uint16
    image = pattern.astype(np.uint16)
    
    # 写入文件
    with open(filepath, 'wb') as f:
        f.write(image.tobytes())
    
    return image


def main():
    """主函数"""
    print("=" * 70)
    print("有符号16位数据类型功能演示")
    print("=" * 70)
    
    # 创建输出目录
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建示例文件
    print("\n1. 创建示例文件...")
    
    signed_file = os.path.join(output_dir, "signed_temperature_diff.bin")
    unsigned_file = os.path.join(output_dir, "unsigned_infrared.bin")
    
    signed_data = create_signed_image_file(signed_file)
    unsigned_data = create_unsigned_image_file(unsigned_file)
    
    print(f"\n有符号数据文件: {signed_file}")
    print(f"  分辨率: 640×512")
    print(f"  数据类型: int16 (有符号)")
    print(f"  值范围: {signed_data.min()} 到 {signed_data.max()}")
    print(f"  用途: 温度差异数据（包含负值）")
    
    print(f"\n无符号数据文件: {unsigned_file}")
    print(f"  分辨率: 640×512")
    print(f"  数据类型: uint16 (无符号)")
    print(f"  值范围: {unsigned_data.min():.0f} 到 {unsigned_data.max():.0f}")
    print(f"  用途: 标准红外图像数据")
    
    print("\n" + "=" * 70)
    print("使用说明")
    print("=" * 70)
    
    print(f"""
查看有符号数据文件:
1. 启动应用程序:
   python main.py {signed_file}

2. 配置参数:
   - 分辨率: 640×512
   - 位深度: 16位
   - 数据类型: **有符号 (-32768-32767)**  ← 重要！
   - 字节序: 小端

3. 观察结果:
   - 图像正确显示，包含正值和负值
   - 直方图映射自动处理负值
   - 中心区域（接近0）显示为中灰色
   - 边缘区域（极值）显示为黑色或白色

查看无符号数据文件:
1. 启动应用程序:
   python main.py {unsigned_file}

2. 配置参数:
   - 分辨率: 640×512
   - 位深度: 16位
   - 数据类型: **无符号 (0-65535)**  ← 默认
   - 字节序: 小端

3. 观察结果:
   - 图像正确显示标准红外数据
   - 渐变从暗到亮
    """)
    
    print("\n" + "=" * 70)
    print("关键概念")
    print("=" * 70)
    
    print("""
1. 数据类型选择
   - **无符号（uint16）**: 0-65535
     * 适用于大多数红外图像
     * 所有值都是正数
     * 默认选项
   
   - **有符号（int16）**: -32768-32767
     * 适用于包含负值的数据
     * 例如：温度差异、变化量、误差数据
     * 需要手动选择

2. 自动启用/禁用
   - 8位时：数据类型选项自动禁用（8位总是无符号）
   - 16位时：数据类型选项自动启用

3. 直方图映射
   - 自动支持有符号数据
   - 正确处理负值
   - 使用百分位数拉伸，无论值范围如何

4. 实时切换
   - 可以在有符号和无符号之间切换
   - 图像立即刷新
   - 无需重新加载文件

5. 常见应用场景
   - 无符号：红外图像、X光图像、普通灰度图像
   - 有符号：温度差异、高度差异、误差图、变化检测
    """)
    
    print(f"\n示例文件已创建在: {output_dir}/")
    print("现在可以使用IR Image Viewer打开并测试有符号/无符号数据类型功能！")


if __name__ == '__main__':
    main()
