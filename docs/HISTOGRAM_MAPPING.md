# 16位图像直方图映射技术说明

## 问题背景

### 为什么16位图像显示为全黑？

16位灰度图像的像素值范围是 0-65535，但实际的红外图像数据通常只使用这个范围的一小部分。例如：

- **理论范围**: 0 - 65535
- **实际使用范围**: 1000 - 5000（仅占7.6%）

如果直接将16位值线性映射到8位显示（除以65535再乘以255），结果是：
- 1000 → 3.9 ≈ 4（接近黑色）
- 5000 → 19.5 ≈ 20（仍然很暗）

这导致整个图像看起来几乎全黑，无法看到任何细节。

## 解决方案：直方图映射

### 基本原理

直方图映射（Histogram Mapping）也称为对比度拉伸（Contrast Stretching），通过以下步骤增强图像：

1. **检测实际值范围**: 使用百分位数统计找出图像实际使用的值范围
2. **拉伸到全范围**: 将实际范围线性映射到0-255
3. **忽略异常值**: 使用百分位数而非最小/最大值，避免极端值影响

### 数学公式

```
vmin = percentile(image, 0.1%)    # 第0.1百分位数
vmax = percentile(image, 99.9%)   # 第99.9百分位数

output = clip((input - vmin) / (vmax - vmin) * 255, 0, 255)
```

### 示例

假设一个16位红外图像：
- 实际值范围: 1000 - 5000
- 百分位数: vmin=1000, vmax=5000

映射后：
- 1000 → 0（黑色）
- 3000 → 127（中灰）
- 5000 → 255（白色）

现在图像使用了完整的0-255范围，对比度清晰可见！

## 实现细节

### 函数签名

```python
def apply_histogram_mapping(
    array: np.ndarray, 
    percentile_low: float = 0.1, 
    percentile_high: float = 99.9
) -> np.ndarray:
    """应用直方图映射增强对比度"""
```

### 参数说明

- **percentile_low** (默认0.1%): 
  - 用于确定映射的最小值
  - 忽略最暗的0.1%像素（可能是噪声或坏点）
  
- **percentile_high** (默认99.9%):
  - 用于确定映射的最大值
  - 忽略最亮的0.1%像素（可能是过曝或异常值）

### 为什么使用百分位数？

使用百分位数而非简单的min/max有以下优势：

1. **抗噪声**: 单个坏点不会影响整体映射
2. **抗异常值**: 极端值不会压缩正常值的显示范围
3. **稳定性**: 对不同图像都能产生一致的良好效果

### 特殊情况处理

#### 1. 常数图像（所有像素值相同）

```python
if vmax - vmin < 1e-10:
    return np.full(array.shape, 128, dtype=np.uint8)
```

映射到中间灰度值（128），避免除零错误。

#### 2. 空数组

```python
if array.size == 0:
    return array.astype(np.uint8)
```

直接返回空的uint8数组。

#### 3. 非常小的值范围

即使原始范围很小（如10个灰度级），也会拉伸到可见范围，确保对比度。

## 性能考虑

### 计算复杂度

- **百分位数计算**: O(n log n)，其中n是像素数量
- **线性映射**: O(n)
- **总体**: O(n log n)

对于典型的640×512图像（327,680像素），计算时间约为几毫秒，完全可以接受。

### 内存使用

- 需要临时的float64数组进行计算
- 峰值内存约为原始数组的3倍
- 对于16位640×512图像：约2MB临时内存

## 使用示例

### 基本使用

```python
from src.utils.converters import apply_histogram_mapping
import numpy as np

# 加载16位图像
image_16bit = np.random.randint(1000, 5000, (512, 640), dtype=np.uint16)

# 应用直方图映射
image_8bit = apply_histogram_mapping(image_16bit)

# 现在可以正常显示
```

### 在图像转换中自动应用

```python
from src.utils.converters import numpy_to_qimage

# 转换为QImage时自动应用直方图映射
qimage = numpy_to_qimage(image_16bit, bit_depth=16, use_histogram_mapping=True)
```

### 禁用直方图映射

如果您确定图像已经使用了全范围，可以禁用：

```python
qimage = numpy_to_qimage(image_16bit, bit_depth=16, use_histogram_mapping=False)
```

## 效果对比

### 不使用直方图映射

```
原始值范围: 1000-5000
显示值范围: 4-20
视觉效果: 几乎全黑，看不到细节
```

### 使用直方图映射

```
原始值范围: 1000-5000
显示值范围: 0-255
视觉效果: 对比度清晰，细节可见
```

## 适用场景

### 推荐使用

- ✅ 16位红外图像
- ✅ 医学影像（CT、MRI）
- ✅ 科学成像数据
- ✅ 任何使用部分值范围的图像

### 不推荐使用

- ❌ 已经过处理的8位图像（可能过度增强）
- ❌ 需要保持绝对值的定量分析
- ❌ 已经归一化的图像

## 与其他技术的比较

### vs. 简单线性映射

| 特性 | 简单线性映射 | 直方图映射 |
|------|------------|-----------|
| 计算速度 | 快 | 稍慢 |
| 抗噪声 | 差 | 好 |
| 对比度 | 差 | 优秀 |
| 适用性 | 有限 | 广泛 |

### vs. 直方图均衡化

| 特性 | 直方图映射 | 直方图均衡化 |
|------|-----------|-------------|
| 保持相对值 | 是 | 否 |
| 计算复杂度 | O(n log n) | O(n) |
| 视觉效果 | 自然 | 可能过度增强 |
| 适用场景 | 通用 | 特定场景 |

## 测试验证

项目包含全面的测试套件（`tests/test_converters_histogram.py`）：

- ✅ 基本功能测试
- ✅ 边界情况测试
- ✅ 异常值处理测试
- ✅ 相对值保持测试
- ✅ 性能测试

运行测试：
```bash
pytest tests/test_converters_histogram.py -v
```

## 参考资料

1. Gonzalez & Woods, "Digital Image Processing", Chapter 3
2. [Histogram Equalization - Wikipedia](https://en.wikipedia.org/wiki/Histogram_equalization)
3. [Contrast Stretching - ImageJ Documentation](https://imagej.net/imaging/contrast-stretching)

## 总结

直方图映射是解决16位图像显示问题的有效方法：

- **自动化**: 无需手动调整参数
- **鲁棒性**: 对各种图像都有良好效果
- **高效**: 计算开销小
- **可靠**: 经过充分测试验证

这使得IR Image Viewer能够正确显示各种16位红外图像，提供良好的用户体验。
