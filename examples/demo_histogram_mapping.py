"""演示直方图映射效果

这个脚本创建一个模拟的16位红外图像，并展示使用和不使用
直方图映射的显示效果差异。
"""

import numpy as np
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.converters import apply_histogram_mapping


def create_sample_16bit_image(width=640, height=512):
    """创建一个模拟的16位红外图像
    
    模拟真实红外图像的特点：只使用0-65535范围的一小部分
    
    Args:
        width: 图像宽度
        height: 图像高度
        
    Returns:
        np.ndarray: 16位图像数组
    """
    # 创建一个渐变图像，值范围在1000-5000之间
    # 这模拟了真实红外图像的特点
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    X, Y = np.meshgrid(x, y)
    
    # 创建一些有趣的图案
    pattern = np.sin(X * 10) * np.cos(Y * 10) * 0.5 + 0.5
    
    # 映射到1000-5000范围（仅占16位范围的7.6%）
    image = (pattern * 4000 + 1000).astype(np.uint16)
    
    # 添加一些噪声
    noise = np.random.randint(-100, 100, size=image.shape, dtype=np.int16)
    image = np.clip(image.astype(np.int32) + noise, 0, 65535).astype(np.uint16)
    
    return image


def analyze_image(image, name="Image"):
    """分析图像的统计信息
    
    Args:
        image: 图像数组
        name: 图像名称
    """
    print(f"\n{name} 统计信息:")
    print(f"  数据类型: {image.dtype}")
    print(f"  形状: {image.shape}")
    print(f"  最小值: {image.min()}")
    print(f"  最大值: {image.max()}")
    print(f"  平均值: {image.mean():.2f}")
    print(f"  标准差: {image.std():.2f}")
    print(f"  值范围: {image.max() - image.min()}")
    
    if image.dtype == np.uint16:
        range_percent = (image.max() - image.min()) / 65535 * 100
        print(f"  使用16位范围的: {range_percent:.2f}%")


def simple_linear_mapping(image_16bit):
    """简单线性映射（不使用直方图映射）
    
    Args:
        image_16bit: 16位图像
        
    Returns:
        np.ndarray: 8位图像
    """
    return (image_16bit.astype(np.float64) / 65535.0 * 255).astype(np.uint8)


def main():
    """主函数"""
    print("=" * 70)
    print("16位图像直方图映射效果演示")
    print("=" * 70)
    
    # 创建模拟的16位红外图像
    print("\n1. 创建模拟的16位红外图像...")
    image_16bit = create_sample_16bit_image()
    analyze_image(image_16bit, "原始16位图像")
    
    # 方法1：简单线性映射（会导致图像很暗）
    print("\n2. 应用简单线性映射（除以65535）...")
    image_simple = simple_linear_mapping(image_16bit)
    analyze_image(image_simple, "简单线性映射结果")
    
    # 方法2：直方图映射（推荐）
    print("\n3. 应用直方图映射（推荐方法）...")
    image_histogram = apply_histogram_mapping(image_16bit)
    analyze_image(image_histogram, "直方图映射结果")
    
    # 对比分析
    print("\n" + "=" * 70)
    print("效果对比:")
    print("=" * 70)
    
    print("\n简单线性映射:")
    print(f"  显示范围: {image_simple.min()} - {image_simple.max()}")
    print(f"  对比度: {image_simple.max() - image_simple.min()}")
    print(f"  视觉效果: {'❌ 很暗，几乎看不到细节' if image_simple.max() < 50 else '✓ 可见'}")
    
    print("\n直方图映射:")
    print(f"  显示范围: {image_histogram.min()} - {image_histogram.max()}")
    print(f"  对比度: {image_histogram.max() - image_histogram.min()}")
    print(f"  视觉效果: {'✓ 清晰可见，对比度良好' if image_histogram.max() > 200 else '需要改进'}")
    
    # 计算改善程度
    contrast_improvement = (image_histogram.max() - image_histogram.min()) / (image_simple.max() - image_simple.min() + 1e-10)
    print(f"\n对比度改善: {contrast_improvement:.1f}x")
    
    print("\n" + "=" * 70)
    print("结论:")
    print("=" * 70)
    print("""
对于只使用部分值范围的16位图像（如红外图像），直方图映射能够：
1. 自动检测实际使用的值范围
2. 将其拉伸到完整的0-255显示范围
3. 提供清晰可见的图像，而不是几乎全黑的图像

这就是为什么IR Image Viewer默认对16位图像使用直方图映射！
    """)
    
    # 保存示例数据（可选）
    try:
        output_dir = "examples/output"
        os.makedirs(output_dir, exist_ok=True)
        
        np.save(os.path.join(output_dir, "sample_16bit.npy"), image_16bit)
        np.save(os.path.join(output_dir, "simple_mapping.npy"), image_simple)
        np.save(os.path.join(output_dir, "histogram_mapping.npy"), image_histogram)
        
        print(f"\n示例数据已保存到: {output_dir}/")
        print("  - sample_16bit.npy: 原始16位图像")
        print("  - simple_mapping.npy: 简单线性映射结果")
        print("  - histogram_mapping.npy: 直方图映射结果")
    except Exception as e:
        print(f"\n注意: 无法保存示例数据: {e}")


if __name__ == '__main__':
    main()
