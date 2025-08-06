#!/usr/bin/env python3
"""
OCR模型评估器模块
"""

from .base import BaseEvaluator, EvaluationResult, DirectoryResult, TestSummary
from .paddleocr_evaluator import PaddleOCREvaluator
from .qwen_evaluator import QwenVLEvaluator

# 评估器注册表
EVALUATOR_REGISTRY = {
    'paddleocr': PaddleOCREvaluator,
    'qwen_vl': QwenVLEvaluator
}

def create_evaluator(model_type: str, config: dict = None) -> BaseEvaluator:
    """创建指定类型的评估器
    
    Args:
        model_type: 模型类型名称
        config: 模型配置参数
        
    Returns:
        BaseEvaluator: 评估器实例
        
    Raises:
        ValueError: 不支持的模型类型
    """
    if model_type not in EVALUATOR_REGISTRY:
        raise ValueError(f"不支持的模型类型: {model_type}. "
                        f"支持的类型: {list(EVALUATOR_REGISTRY.keys())}")
    
    evaluator_class = EVALUATOR_REGISTRY[model_type]
    return evaluator_class(config)

def get_supported_models() -> list:
    """获取支持的模型类型列表"""
    return list(EVALUATOR_REGISTRY.keys())

__all__ = [
    # 基类和数据结构
    'BaseEvaluator', 'EvaluationResult', 'DirectoryResult', 'TestSummary',
    
    # 具体实现
    'PaddleOCREvaluator', 'QwenVLEvaluator',
    
    # 工厂函数
    'create_evaluator', 'get_supported_models',
    
    # 注册表
    'EVALUATOR_REGISTRY'
]