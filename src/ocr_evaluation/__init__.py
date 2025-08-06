#!/usr/bin/env python3
"""
OCR评估框架

一个专业的OCR模型评估和对比框架，支持多种OCR模型的准确率测试和性能分析。
"""

__version__ = "1.0.0"
__author__ = "Ray"
__email__ = "ray.pf.lau@gmail.com"
__description__ = "专业的OCR模型评估和对比框架"

from .config import (
    Config, get_config, set_config, load_config_from_file,
    ModelTypes, SUPPORTED_IMAGE_FORMATS, SUPPORTED_REPORT_FORMATS
)

from .models import (
    BaseEvaluator, EvaluationResult, DirectoryResult, TestSummary,
    PaddleOCREvaluator, QwenVLEvaluator,
    create_evaluator, get_supported_models
)

from .utils import (
    ReportGenerator, get_logger, setup_logging
)

# 便捷函数
def evaluate_model(model_type: str, images_dir: str, config: dict = None) -> TestSummary:
    """便捷的模型评估函数
    
    Args:
        model_type: 模型类型 ('paddleocr' 或 'qwen_vl')
        images_dir: 图片目录路径
        config: 可选的模型配置
        
    Returns:
        TestSummary: 评估结果汇总
        
    Example:
        >>> from ocr_evaluation import evaluate_model
        >>> summary = evaluate_model('paddleocr', './images')
        >>> print(f"准确率: {summary.overall_accuracy:.2%}")
    """
    from pathlib import Path
    
    evaluator = create_evaluator(model_type, config)
    return evaluator.evaluate_dataset(Path(images_dir))


def generate_report(summary: TestSummary, output_dir: str = "./reports", format: str = "markdown") -> str:
    """便捷的报告生成函数
    
    Args:
        summary: 评估结果汇总
        output_dir: 输出目录
        format: 报告格式 ('markdown' 或 'json')
        
    Returns:
        str: 生成的报告文件路径
        
    Example:
        >>> from ocr_evaluation import evaluate_model, generate_report
        >>> summary = evaluate_model('paddleocr', './images')
        >>> report_path = generate_report(summary)
        >>> print(f"报告已保存至: {report_path}")
    """
    from pathlib import Path
    
    generator = ReportGenerator(Path(output_dir))
    
    if format.lower() == "markdown":
        return str(generator.save_markdown_report(summary))
    elif format.lower() == "json":
        return str(generator.save_json_results(summary))
    else:
        raise ValueError(f"不支持的报告格式: {format}")


# 导出的公共API
__all__ = [
    # 版本信息
    '__version__', '__author__', '__email__', '__description__',
    
    # 配置管理
    'Config', 'get_config', 'set_config', 'load_config_from_file',
    'ModelTypes', 'SUPPORTED_IMAGE_FORMATS', 'SUPPORTED_REPORT_FORMATS',
    
    # 模型评估
    'BaseEvaluator', 'EvaluationResult', 'DirectoryResult', 'TestSummary',
    'PaddleOCREvaluator', 'QwenVLEvaluator',
    'create_evaluator', 'get_supported_models',
    
    # 工具函数
    'ReportGenerator', 'get_logger', 'setup_logging',
    
    # 便捷函数
    'evaluate_model', 'generate_report'
]