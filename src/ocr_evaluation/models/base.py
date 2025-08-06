#!/usr/bin/env python3
"""
OCR评估器抽象基类
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging


@dataclass
class EvaluationResult:
    """单个样本评估结果"""
    image_path: Path
    ground_truth: str
    predicted: str
    accuracy: float
    exact_match: bool
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DirectoryResult:
    """目录评估结果"""
    directory: Path
    total_images: int
    average_accuracy: float
    exact_match_count: int
    exact_match_rate: float
    results: List[EvaluationResult]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TestSummary:
    """完整测试汇总结果"""
    model_name: str
    test_timestamp: str
    total_images: int
    overall_accuracy: float
    overall_exact_match_rate: float
    directory_results: List[DirectoryResult]
    technical_details: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class BaseEvaluator(ABC):
    """OCR评估器基类
    
    定义了所有OCR模型评估器必须实现的接口
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化评估器
        
        Args:
            config: 模型配置字典
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None
        self.is_initialized = False
        
        # 技术细节记录
        self.technical_details = {
            'model_name': self.get_model_name(),
            'model_type': self.get_model_type(),
            'config': self.config.copy(),
            'initialization_time': None,
            'total_processing_time': None,
            'average_processing_time': None
        }
    
    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型名称"""
        pass
    
    @abstractmethod  
    def get_model_type(self) -> str:
        """获取模型类型"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化模型
        
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    def recognize_image(self, image_path: Path) -> str:
        """识别单张图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            str: 识别结果文本
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理资源"""
        pass
    
    def validate_image(self, image_path: Path) -> bool:
        """验证图片文件
        
        Args:
            image_path: 图片路径
            
        Returns:
            bool: 图片是否有效
        """
        if not image_path.exists():
            self.logger.warning(f"图片文件不存在: {image_path}")
            return False
        
        if not image_path.is_file():
            self.logger.warning(f"路径不是文件: {image_path}")
            return False
        
        # 检查文件扩展名
        from ..config import SUPPORTED_IMAGE_FORMATS
        if image_path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
            self.logger.warning(f"不支持的图片格式: {image_path.suffix}")
            return False
        
        # 检查文件大小
        from ..config import PerformanceConstants
        if image_path.stat().st_size > PerformanceConstants.MAX_IMAGE_SIZE:
            self.logger.warning(f"图片文件过大: {image_path}")
            return False
        
        return True
    
    def parse_label_file(self, label_file: Path) -> Dict[str, str]:
        """解析Label.txt文件
        
        Args:
            label_file: 标签文件路径
            
        Returns:
            Dict[str, str]: 图片名到标注文本的映射
        """
        import json
        import os
        
        labels = {}
        try:
            with open(label_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 解析格式: 图片路径\t[{"transcription": "文本", ...}]
                    parts = line.split('\t', 1)
                    if len(parts) != 2:
                        self.logger.warning(f"标签文件第{line_num}行格式错误: {line}")
                        continue
                    
                    image_path = parts[0]
                    image_name = os.path.basename(image_path)
                    
                    # 解析JSON标注
                    try:
                        annotations = json.loads(parts[1])
                        if annotations and isinstance(annotations, list) and len(annotations) > 0:
                            transcription = annotations[0].get('transcription', '')
                            if transcription:
                                labels[image_name] = transcription
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"解析JSON标注失败，第{line_num}行: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"解析标签文件失败 {label_file}: {e}")
        
        return labels
    
    def calculate_accuracy(self, ground_truth: str, predicted: str) -> float:
        """计算准确率
        
        Args:
            ground_truth: 标准答案
            predicted: 预测结果
            
        Returns:
            float: 准确率 (0.0 到 1.0)
        """
        if not ground_truth and not predicted:
            return 1.0
        if not ground_truth or not predicted:
            return 0.0
        
        # 完全匹配
        if ground_truth == predicted:
            return 1.0
        
        # 基于编辑距离的准确率
        return self._levenshtein_accuracy(ground_truth, predicted)
    
    def _levenshtein_accuracy(self, s1: str, s2: str) -> float:
        """计算基于Levenshtein编辑距离的准确率"""
        distance = self._levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        return max(0.0, 1.0 - distance / max_len) if max_len > 0 else 1.0
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算Levenshtein编辑距离"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
    
    def evaluate_directory(self, directory: Path) -> Optional[DirectoryResult]:
        """评估单个目录
        
        Args:
            directory: 包含图片和Label.txt的目录
            
        Returns:
            DirectoryResult: 目录评估结果，如果失败返回None
        """
        if not self.is_initialized:
            self.logger.error("模型未初始化")
            return None
        
        self.logger.info(f"评估目录: {directory}")
        
        # 查找标签文件
        label_file = directory / "Label.txt"
        if not label_file.exists():
            self.logger.warning(f"未找到标签文件: {label_file}")
            return None
        
        # 解析标签
        labels = self.parse_label_file(label_file)
        if not labels:
            self.logger.warning(f"标签文件为空: {label_file}")
            return None
        
        self.logger.info(f"找到 {len(labels)} 个标签")
        
        # 处理每个图片
        results = []
        total_accuracy = 0.0
        exact_matches = 0
        
        for image_name, ground_truth in labels.items():
            image_path = directory / image_name
            
            if not self.validate_image(image_path):
                continue
            
            # 识别图片
            try:
                predicted_text = self.recognize_image(image_path)
                accuracy = self.calculate_accuracy(ground_truth, predicted_text)
                exact_match = ground_truth == predicted_text
                
                result = EvaluationResult(
                    image_path=image_path,
                    ground_truth=ground_truth,
                    predicted=predicted_text,
                    accuracy=accuracy,
                    exact_match=exact_match
                )
                
                results.append(result)
                total_accuracy += accuracy
                if exact_match:
                    exact_matches += 1
                
                self.logger.debug(f"图片: {image_name}, 标准答案: {ground_truth}, "
                                f"识别结果: {predicted_text}, 准确率: {accuracy:.4f}")
                
            except Exception as e:
                self.logger.error(f"处理图片失败 {image_path}: {e}")
                continue
        
        if not results:
            self.logger.error(f"目录 {directory} 中没有有效的识别结果")
            return None
        
        # 计算统计信息
        avg_accuracy = total_accuracy / len(results)
        exact_match_rate = exact_matches / len(results)
        
        return DirectoryResult(
            directory=directory,
            total_images=len(results),
            average_accuracy=avg_accuracy,
            exact_match_count=exact_matches,
            exact_match_rate=exact_match_rate,
            results=results
        )
    
    def evaluate_dataset(self, images_dir: Path) -> Optional[TestSummary]:
        """评估完整数据集
        
        Args:
            images_dir: 包含所有测试图片目录的根目录
            
        Returns:
            TestSummary: 完整测试汇总结果
        """
        from datetime import datetime
        
        if not self.initialize():
            self.logger.error("模型初始化失败")
            return None
        
        start_time = datetime.now()
        self.logger.info(f"开始 {self.get_model_name()} 数据集评估")
        
        directory_results = []
        total_images = 0
        total_accuracy = 0.0
        total_exact_matches = 0
        
        # 遍历所有子目录
        for item in images_dir.iterdir():
            if not item.is_dir():
                continue
                
            # 检查是否直接包含Label.txt
            if (item / "Label.txt").exists():
                result = self.evaluate_directory(item)
                if result:
                    directory_results.append(result)
                    total_images += result.total_images
                    total_accuracy += result.average_accuracy * result.total_images
                    total_exact_matches += result.exact_match_count
            else:
                # 检查子目录
                for subitem in item.iterdir():
                    if subitem.is_dir() and (subitem / "Label.txt").exists():
                        result = self.evaluate_directory(subitem)
                        if result:
                            directory_results.append(result)
                            total_images += result.total_images
                            total_accuracy += result.average_accuracy * result.total_images
                            total_exact_matches += result.exact_match_count
        
        # 计算总体统计
        overall_accuracy = total_accuracy / total_images if total_images > 0 else 0.0
        overall_exact_match_rate = total_exact_matches / total_images if total_images > 0 else 0.0
        
        # 更新技术细节
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        self.technical_details.update({
            'total_processing_time': processing_time,
            'average_processing_time': processing_time / total_images if total_images > 0 else 0,
            'initialization_time': self.technical_details.get('initialization_time', 0)
        })
        
        self.logger.info(f"评估完成，总体准确率: {overall_accuracy:.4f} ({overall_accuracy*100:.2f}%)")
        
        # 清理资源
        self.cleanup()
        
        return TestSummary(
            model_name=self.get_model_name(),
            test_timestamp=end_time.isoformat(),
            total_images=total_images,
            overall_accuracy=overall_accuracy,
            overall_exact_match_rate=overall_exact_match_rate,
            directory_results=directory_results,
            technical_details=self.technical_details.copy()
        )