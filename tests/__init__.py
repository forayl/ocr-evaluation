#!/usr/bin/env python3
"""
OCR评估框架测试模块
"""

# 测试配置
import sys
from pathlib import Path

# 添加源码路径到系统路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

__all__ = []