#!/usr/bin/env python3
"""
OCR评估框架配置模块
"""

from .settings import Config, get_config, set_config, load_config_from_file
from .constants import (
    PROJECT_ROOT, DATA_DIR, IMAGES_DIR, OUTPUTS_DIR, REPORTS_DIR,
    SUPPORTED_IMAGE_FORMATS, SUPPORTED_REPORT_FORMATS,
    ModelTypes, PaddleOCRConstants, QwenConstants,
    EvaluationConstants, TextProcessingConstants,
    LoggingConstants, ReportConstants, ErrorCodes,
    PerformanceConstants, EnvVars
)

__all__ = [
    # 配置管理
    'Config', 'get_config', 'set_config', 'load_config_from_file',
    
    # 目录常量
    'PROJECT_ROOT', 'DATA_DIR', 'IMAGES_DIR', 'OUTPUTS_DIR', 'REPORTS_DIR',
    
    # 格式常量
    'SUPPORTED_IMAGE_FORMATS', 'SUPPORTED_REPORT_FORMATS',
    
    # 模型常量
    'ModelTypes', 'PaddleOCRConstants', 'QwenConstants',
    
    # 评估常量
    'EvaluationConstants', 'TextProcessingConstants',
    
    # 系统常量
    'LoggingConstants', 'ReportConstants', 'ErrorCodes',
    'PerformanceConstants', 'EnvVars'
]