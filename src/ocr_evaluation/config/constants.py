#!/usr/bin/env python3
"""
OCR评估框架常量定义
"""

from pathlib import Path
import re

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = DATA_DIR / "images"
OUTPUTS_DIR = DATA_DIR / "outputs"
REPORTS_DIR = DATA_DIR / "reports"

# 支持的文件格式
SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
SUPPORTED_REPORT_FORMATS = {'markdown', 'json', 'html'}

# 模型相关常量
class ModelTypes:
    """支持的模型类型"""
    PADDLEOCR = "paddleocr"
    QWEN_VL = "qwen_vl"
    
    @classmethod
    def all_types(cls):
        return [cls.PADDLEOCR, cls.QWEN_VL]

# PaddleOCR相关常量
class PaddleOCRConstants:
    """PaddleOCR相关常量"""
    DEFAULT_LANG = 'en'
    SUPPORTED_LANGS = ['ch', 'en', 'fr', 'german', 'korean', 'japan']
    
    # 最佳实践配置
    OPTIMIZED_CONFIG = {
        'use_doc_orientation_classify': False,
        'use_doc_unwarping': False, 
        'use_textline_orientation': False,
        'lang': 'en'
    }

# Qwen2.5-VL相关常量
class QwenConstants:
    """Qwen2.5-VL相关常量"""
    DEFAULT_MODEL_NAME = "qwen/qwen2.5-vl-7b"
    DEFAULT_LMSTUDIO_URL = "ws://localhost:1234"
    DEFAULT_TEMPERATURE = 0.1
    DEFAULT_MAX_TOKENS = 50
    
    # 默认提示词模板
    DEFAULT_PROMPT = """Please look at this image carefully and extract the exact text/code shown in the image. This appears to be an alphanumeric code or product number. Please provide ONLY the exact text you see, without any additional explanation or formatting. The text typically consists of letters, numbers, and may include symbols like # or ."""

# 评估相关常量
class EvaluationConstants:
    """评估相关常量"""
    DEFAULT_ACCURACY_THRESHOLD = 0.95
    ACCURACY_RANGES = {
        '0.9-1.0': (0.9, 1.0),
        '0.8-0.9': (0.8, 0.9),
        '0.7-0.8': (0.7, 0.8),
        '0.6-0.7': (0.6, 0.7),
        '<0.6': (0.0, 0.6)
    }

# 文本处理相关常量
class TextProcessingConstants:
    """文本处理相关常量"""
    # 字母数字产品编号的正则表达式模式
    ALPHANUMERIC_PATTERN = re.compile(r'[A-Z0-9]+[#.\-A-Z0-9]*')
    
    # 需要移除的解释性前缀
    EXPLANATION_PREFIXES = [
        "The text shown in the image is:",
        "The code in the image is:",
        "The text appears to be:",
        "I can see:",
        "The image shows:",
        "The alphanumeric code is:",
        "The product number is:",
        "Looking at this image, I can see:",
    ]
    
    # 需要清理的引号字符
    QUOTE_CHARS = '"\'`'

# 日志相关常量
class LoggingConstants:
    """日志相关常量"""
    DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DEFAULT_LEVEL = 'INFO'
    SUPPORTED_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

# 报告生成相关常量
class ReportConstants:
    """报告生成相关常量"""
    MARKDOWN_EXTENSION = '.md'
    JSON_EXTENSION = '.json'
    HTML_EXTENSION = '.html'
    
    DEFAULT_REPORT_NAME_TEMPLATE = "{model}_准确率报告_{timestamp}"
    DEFAULT_RESULTS_NAME_TEMPLATE = "{model}_results_{timestamp}"
    
    # 报告模板相关
    REPORT_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
    DISPLAY_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# 错误码定义
class ErrorCodes:
    """错误码定义"""
    SUCCESS = 0
    CONFIG_ERROR = 1
    MODEL_INIT_ERROR = 2
    DATA_ERROR = 3
    EVALUATION_ERROR = 4
    REPORT_ERROR = 5
    UNKNOWN_ERROR = 99

# 性能相关常量
class PerformanceConstants:
    """性能相关常量"""
    DEFAULT_BATCH_SIZE = 1  # OCR通常单张处理
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    TIMEOUT_SECONDS = 30  # 单张图片处理超时时间

# 环境变量名称
class EnvVars:
    """环境变量名称"""
    CONFIG_FILE = "OCR_EVALUATION_CONFIG"
    LOG_LEVEL = "OCR_EVALUATION_LOG_LEVEL"  
    OUTPUT_DIR = "OCR_EVALUATION_OUTPUT_DIR"
    LMSTUDIO_URL = "LMSTUDIO_URL"
    USE_GPU = "OCR_EVALUATION_USE_GPU"