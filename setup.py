"""IR Image Viewer 安装配置文件

用于安装和分发IR Image Viewer应用程序。

使用方法:
    pip install -e .              # 开发模式安装
    pip install .                 # 正常安装
    python setup.py install       # 使用setuptools安装
"""

from setuptools import setup, find_packages
import os


# 读取README文件作为长描述
def read_readme():
    """读取README.md文件内容
    
    Returns:
        str: README文件内容，如果文件不存在则返回空字符串
    """
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


# 读取requirements.txt文件
def read_requirements():
    """读取requirements.txt文件并解析依赖
    
    Returns:
        list: 依赖包列表
    """
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if line and not line.startswith('#'):
                    requirements.append(line)
    
    return requirements


# 分离运行时依赖和测试依赖
def split_requirements(requirements):
    """将依赖分为运行时依赖和测试依赖
    
    Args:
        requirements (list): 所有依赖列表
        
    Returns:
        tuple: (运行时依赖列表, 测试依赖列表)
    """
    runtime_deps = []
    test_deps = []
    
    test_packages = ['pytest', 'hypothesis', 'pytest-qt', 'pytest-cov']
    
    for req in requirements:
        # 检查是否是测试相关的包
        is_test_dep = any(test_pkg in req.lower() for test_pkg in test_packages)
        
        if is_test_dep:
            test_deps.append(req)
        else:
            runtime_deps.append(req)
    
    return runtime_deps, test_deps


# 获取版本号
VERSION = '1.0.0'

# 读取所有依赖
all_requirements = read_requirements()
install_requires, tests_require = split_requirements(all_requirements)

setup(
    # 基本信息
    name='ir-image-viewer',
    version=VERSION,
    description='红外图像二进制数据查看器 - 用于加载、显示和分析二进制格式的红外图像数据',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    
    # 作者信息
    author='IR Image Viewer Team',
    author_email='contact@example.com',
    
    # 项目链接
    url='https://github.com/example/ir-image-viewer',
    
    # 许可证
    license='MIT',
    
    # 分类信息
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Image Processing',
        'Topic :: Scientific/Engineering :: Visualization',
        'Operating System :: OS Independent',
    ],
    
    # 关键词
    keywords='infrared image viewer binary data visualization hexadecimal',
    
    # Python版本要求
    python_requires='>=3.8',
    
    # 包配置
    packages=find_packages(exclude=['tests', 'tests.*']),
    
    # 包含非Python文件
    include_package_data=True,
    
    # 依赖配置
    install_requires=install_requires,
    
    # 额外依赖（可选）
    extras_require={
        'test': tests_require,
        'dev': tests_require + [
            'black',
            'flake8',
            'mypy',
        ],
    },
    
    # 测试配置
    tests_require=tests_require,
    test_suite='tests',
    
    # 入口点配置
    entry_points={
        'console_scripts': [
            'ir-image-viewer=main:main',
        ],
        'gui_scripts': [
            'ir-image-viewer-gui=main:main',
        ],
    },
    
    # 项目URLs
    project_urls={
        'Bug Reports': 'https://github.com/example/ir-image-viewer/issues',
        'Source': 'https://github.com/example/ir-image-viewer',
        'Documentation': 'https://github.com/example/ir-image-viewer/wiki',
    },
    
    # 其他配置
    zip_safe=False,
)
