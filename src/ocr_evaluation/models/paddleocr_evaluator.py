#!/usr/bin/env python3
"""
PaddleOCR评估器实现
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .base import BaseEvaluator
from ..config import ModelTypes, PaddleOCRConstants


class PaddleOCREvaluator(BaseEvaluator):
    """PaddleOCR评估器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化PaddleOCR评估器
        
        Args:
            config: PaddleOCR配置参数
        """
        # 使用优化配置作为默认值
        default_config = PaddleOCRConstants.OPTIMIZED_CONFIG.copy()
        if config:
            default_config.update(config)
        
        super().__init__(default_config)
        
        # 更新技术细节
        self.technical_details.update({
            'optimized_config': PaddleOCRConstants.OPTIMIZED_CONFIG,
            'actual_config': self.config,
            'optimization_notes': [
                "禁用文档方向分类 - 对小图片的简单文本，复杂预处理反而有害",
                "禁用文档矫正 - 避免对简单文本图片过度处理",
                "禁用文本行方向分类 - 减少不必要的预处理步骤",
                "使用英文模型 - 对字母数字混合文本效果更好"
            ]
        })
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return "PP-OCRv5"
    
    def get_model_type(self) -> str:
        """获取模型类型"""
        return ModelTypes.PADDLEOCR
    
    def initialize(self) -> bool:
        """初始化PaddleOCR模型"""
        if self.is_initialized:
            return True
        
        self.logger.info("正在初始化PaddleOCR模型...")
        start_time = datetime.now()
        
        try:
            # 导入PaddleOCR
            from paddleocr import PaddleOCR
            
            # 创建OCR实例
            self.model = PaddleOCR(**self.config)
            
            # 进行一次测试调用以确保模型正常工作
            # 创建一个简单的测试图像数据
            import numpy as np
            test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255  # 白色图像
            
            try:
                _ = self.model.ocr(test_image, cls=False)
                self.logger.info("PaddleOCR模型初始化成功")
                self.is_initialized = True
                
                # 记录初始化时间
                init_time = (datetime.now() - start_time).total_seconds()
                self.technical_details['initialization_time'] = init_time
                
                return True
                
            except Exception as e:
                self.logger.error(f"PaddleOCR模型测试失败: {e}")
                return False
                
        except ImportError:
            self.logger.error("PaddleOCR未安装，请运行: pip install paddlepaddle paddleocr")
            return False
        except Exception as e:
            self.logger.error(f"PaddleOCR初始化失败: {e}")
            return False
    
    def recognize_image(self, image_path: Path) -> str:
        """使用PaddleOCR识别单张图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            str: 识别的文本结果
        """
        if not self.is_initialized:
            raise RuntimeError("模型未初始化")
        
        try:
            # 使用PaddleOCR进行识别
            result = self.model.ocr(str(image_path), cls=False)
            
            # 提取文本
            if result and len(result) > 0 and result[0]:
                # PaddleOCR返回格式: [[[bbox], (text, confidence)], ...]
                texts = []
                for detection in result[0]:
                    if len(detection) >= 2 and len(detection[1]) >= 2:
                        text = detection[1][0]  # 提取文本
                        confidence = detection[1][1]  # 提取置信度
                        
                        # 可以根据置信度过滤结果
                        if confidence > 0.5:  # 置信度阈值
                            texts.append(text)
                
                # 合并多个文本区域的结果
                if texts:
                    return ' '.join(texts).strip()
            
            return ""
            
        except Exception as e:
            self.logger.error(f"PaddleOCR识别失败 {image_path}: {e}")
            return ""
    
    def cleanup(self):
        """清理PaddleOCR资源"""
        if self.model is not None:
            # PaddleOCR通常不需要显式清理，但可以释放引用
            self.model = None
        self.is_initialized = False
        self.logger.debug("PaddleOCR资源已清理")
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型详细信息"""
        info = {
            'model_name': self.get_model_name(),
            'model_type': self.get_model_type(),
            'config': self.config,
            'is_initialized': self.is_initialized,
            'supported_languages': PaddleOCRConstants.SUPPORTED_LANGS,
            'current_language': self.config.get('lang', PaddleOCRConstants.DEFAULT_LANG)
        }
        
        if self.is_initialized:
            try:
                # 如果可能，获取更多运行时信息
                import paddle
                info['paddle_version'] = paddle.__version__
            except:
                pass
        
        return info
    
    @classmethod
    def create_with_optimal_config(cls) -> 'PaddleOCREvaluator':
        """使用最佳配置创建评估器实例
        
        Returns:
            PaddleOCREvaluator: 使用优化配置的评估器实例
        """
        return cls(PaddleOCRConstants.OPTIMIZED_CONFIG)
    
    @classmethod
    def create_from_config_dict(cls, config_dict: Dict[str, Any]) -> 'PaddleOCREvaluator':
        """从配置字典创建评估器实例
        
        Args:
            config_dict: 配置字典，通常来自配置文件
            
        Returns:
            PaddleOCREvaluator: 评估器实例
        """
        paddleocr_config = config_dict.get('models', {}).get('paddleocr', {})
        return cls(paddleocr_config)