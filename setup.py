#!/usr/bin/env python3
"""
OCR评估框架安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# 读取版本信息
version_file = Path(__file__).parent / "src" / "ocr_evaluation" / "__init__.py"
version = "1.0.0"
if version_file.exists():
    for line in version_file.read_text().splitlines():
        if line.startswith("__version__"):
            version = line.split('"')[1]
            break

# 读取依赖项
requirements_file = Path(__file__).parent / "requirements" / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="ocr-evaluation",
    version=version,
    author="Ray", 
    author_email="ray.pf.lau@gmail.com",
    description="专业的OCR模型评估和对比框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/forayl/ocr-evaluation",
    
    # 包配置
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    # 依赖项
    install_requires=[
        "PyYAML>=6.0",
        "numpy>=1.20.0",
        "Pillow>=8.0.0",
    ],
    
    extras_require={
        "paddleocr": [
            "paddlepaddle>=2.4.0",
            "paddleocr>=2.6.0",
        ],
        "qwen": [
            "lmstudio>=1.0.0",
        ],
        "all": [
            "paddlepaddle>=2.4.0", 
            "paddleocr>=2.6.0",
            "lmstudio>=1.0.0",
            "pandas>=1.3.0",
            "scipy>=1.7.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
        ],
        "docs": [
            "Sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.12.0",
            "sphinx-copybutton>=0.5.0",
            "sphinx-tabs>=3.0.0",
            "myst-parser>=0.18.0",
            "Pygments>=2.10.0",
        ],
    },
    
    # 命令行入口点
    entry_points={
        "console_scripts": [
            "ocr-evaluation=ocr_evaluation.cli.main:cli_entry",
        ],
    },
    
    # 包含数据文件
    include_package_data=True,
    package_data={
        "ocr_evaluation": [
            "config/*.yaml",
            "config/*.json",
        ],
    },
    
    # 项目分类
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Python版本要求
    python_requires=">=3.8",
    
    # 项目关键词
    keywords="ocr, evaluation, paddleocr, qwen, computer-vision, machine-learning",
    
    # 项目状态
    zip_safe=False,
)