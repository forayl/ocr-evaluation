#!/usr/bin/env python3
"""
快速运行评估的脚本
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ocr_evaluation.cli.main import main

if __name__ == "__main__":
    sys.exit(main())