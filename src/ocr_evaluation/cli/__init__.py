#!/usr/bin/env python3
"""
OCR评估框架CLI模块
"""

from .main import main, create_cli_parser
from .commands import EvaluateCommand, CompareCommand, ConfigCommand

__all__ = [
    'main', 'create_cli_parser',
    'EvaluateCommand', 'CompareCommand', 'ConfigCommand'
]