#!/usr/bin/env python3
"""
评估器测试
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.ocr_evaluation.models import (
    BaseEvaluator, EvaluationResult, DirectoryResult, 
    create_evaluator, get_supported_models
)


class MockEvaluator(BaseEvaluator):
    """测试用的模拟评估器"""
    
    def get_model_name(self) -> str:
        return "MockModel"
    
    def get_model_type(self) -> str:
        return "mock"
    
    def initialize(self) -> bool:
        self.is_initialized = True
        return True
    
    def recognize_image(self, image_path: Path) -> str:
        # 简单的模拟：返回文件名作为识别结果
        return image_path.stem
    
    def cleanup(self):
        self.is_initialized = False


class TestBaseEvaluator(unittest.TestCase):
    """基础评估器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.evaluator = MockEvaluator()
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        for file in self.temp_dir.rglob("*"):
            if file.is_file():
                file.unlink()
        for dir_path in sorted(self.temp_dir.rglob("*"), reverse=True):
            if dir_path.is_dir():
                dir_path.rmdir()
        self.temp_dir.rmdir()
    
    def test_accuracy_calculation(self):
        """测试准确率计算"""
        # 测试完全匹配
        accuracy = self.evaluator.calculate_accuracy("ABC123", "ABC123")
        self.assertEqual(accuracy, 1.0)
        
        # 测试完全不匹配
        accuracy = self.evaluator.calculate_accuracy("ABC123", "XYZ789")
        self.assertLess(accuracy, 1.0)
        self.assertGreater(accuracy, 0.0)
        
        # 测试空字符串
        accuracy = self.evaluator.calculate_accuracy("", "")
        self.assertEqual(accuracy, 1.0)
        
        # 测试部分匹配
        accuracy = self.evaluator.calculate_accuracy("ABC123", "ABC124")
        self.assertGreater(accuracy, 0.8)  # 应该有较高相似度
        self.assertLess(accuracy, 1.0)
    
    def test_levenshtein_distance(self):
        """测试编辑距离计算"""
        # 测试相同字符串
        distance = self.evaluator._levenshtein_distance("test", "test")
        self.assertEqual(distance, 0)
        
        # 测试单个字符差异
        distance = self.evaluator._levenshtein_distance("test", "best")
        self.assertEqual(distance, 1)
        
        # 测试插入操作
        distance = self.evaluator._levenshtein_distance("test", "tests")
        self.assertEqual(distance, 1)
        
        # 测试删除操作
        distance = self.evaluator._levenshtein_distance("tests", "test")
        self.assertEqual(distance, 1)
    
    def test_image_validation(self):
        """测试图片验证"""
        # 创建测试图片文件
        valid_image = self.temp_dir / "test.jpg"
        valid_image.write_text("fake image content")
        
        # 测试有效图片
        self.assertTrue(self.evaluator.validate_image(valid_image))
        
        # 测试不存在的文件
        nonexistent = self.temp_dir / "nonexistent.jpg"
        self.assertFalse(self.evaluator.validate_image(nonexistent))
        
        # 测试不支持的格式
        unsupported = self.temp_dir / "test.txt"
        unsupported.write_text("not an image")
        self.assertFalse(self.evaluator.validate_image(unsupported))
    
    def test_label_file_parsing(self):
        """测试标签文件解析"""
        # 创建测试标签文件
        label_content = [
            'image1.jpg\t[{"transcription": "ABC123", "points": [[0,0],[100,0],[100,50],[0,50]], "difficult": false}]',
            'image2.jpg\t[{"transcription": "XYZ789", "points": [[0,0],[100,0],[100,50],[0,50]], "difficult": false}]',
            'image3.jpg\t[{"transcription": "", "points": [[0,0],[100,0],[100,50],[0,50]], "difficult": false}]',  # 空标注
            'invalid_line',  # 无效行
            '',  # 空行
        ]
        
        label_file = self.temp_dir / "Label.txt"
        label_file.write_text('\n'.join(label_content), encoding='utf-8')
        
        # 解析标签文件
        labels = self.evaluator.parse_label_file(label_file)
        
        # 验证解析结果
        self.assertEqual(len(labels), 2)  # 只有2个有效标注
        self.assertEqual(labels['image1.jpg'], 'ABC123')
        self.assertEqual(labels['image2.jpg'], 'XYZ789')
        self.assertNotIn('image3.jpg', labels)  # 空标注应该被过滤
    
    def test_directory_evaluation(self):
        """测试目录评估"""
        # 创建测试目录结构
        test_dir = self.temp_dir / "test_images"
        test_dir.mkdir()
        
        # 创建测试图片
        (test_dir / "image1.jpg").write_text("fake image")
        (test_dir / "image2.jpg").write_text("fake image")
        
        # 创建标签文件
        label_content = [
            'image1.jpg\t[{"transcription": "image1", "points": [[0,0],[100,0],[100,50],[0,50]], "difficult": false}]',
            'image2.jpg\t[{"transcription": "different", "points": [[0,0],[100,0],[100,50],[0,50]], "difficult": false}]',
        ]
        label_file = test_dir / "Label.txt"
        label_file.write_text('\n'.join(label_content), encoding='utf-8')
        
        # 初始化并评估目录
        self.evaluator.initialize()
        result = self.evaluator.evaluate_directory(test_dir)
        
        # 验证结果
        self.assertIsInstance(result, DirectoryResult)
        self.assertEqual(result.total_images, 2)
        self.assertEqual(len(result.results), 2)
        
        # 验证第一个图片（完全匹配）
        image1_result = next(r for r in result.results if r.image_path.name == "image1.jpg")
        self.assertEqual(image1_result.ground_truth, "image1")
        self.assertEqual(image1_result.predicted, "image1")
        self.assertTrue(image1_result.exact_match)
        self.assertEqual(image1_result.accuracy, 1.0)
        
        # 验证第二个图片（不匹配）
        image2_result = next(r for r in result.results if r.image_path.name == "image2.jpg")
        self.assertEqual(image2_result.ground_truth, "different")
        self.assertEqual(image2_result.predicted, "image2")
        self.assertFalse(image2_result.exact_match)
        self.assertLess(image2_result.accuracy, 1.0)


class TestEvaluatorFactory(unittest.TestCase):
    """评估器工厂测试类"""
    
    def test_get_supported_models(self):
        """测试获取支持的模型列表"""
        models = get_supported_models()
        self.assertIsInstance(models, list)
        self.assertIn('paddleocr', models)
        self.assertIn('qwen_vl', models)
    
    @patch('src.ocr_evaluation.models.paddleocr_evaluator.PaddleOCR')
    def test_create_paddleocr_evaluator(self, mock_paddleocr):
        """测试创建PaddleOCR评估器"""
        # 模拟PaddleOCR
        mock_instance = Mock()
        mock_paddleocr.return_value = mock_instance
        
        evaluator = create_evaluator('paddleocr', {'lang': 'en'})
        
        self.assertEqual(evaluator.get_model_type(), 'paddleocr')
        self.assertEqual(evaluator.get_model_name(), 'PP-OCRv5')
    
    @patch('src.ocr_evaluation.models.qwen_evaluator.lmstudio')
    def test_create_qwen_evaluator(self, mock_lmstudio):
        """测试创建Qwen评估器"""
        evaluator = create_evaluator('qwen_vl', {'model_name': 'test-model'})
        
        self.assertEqual(evaluator.get_model_type(), 'qwen_vl')
        self.assertEqual(evaluator.get_model_name(), 'Qwen2.5-VL-7B')
    
    def test_create_invalid_evaluator(self):
        """测试创建无效的评估器类型"""
        with self.assertRaises(ValueError):
            create_evaluator('invalid_model_type')


class TestEvaluationDataStructures(unittest.TestCase):
    """评估数据结构测试类"""
    
    def test_evaluation_result(self):
        """测试评估结果数据结构"""
        result = EvaluationResult(
            image_path=Path("test.jpg"),
            ground_truth="ABC123",
            predicted="ABC123",
            accuracy=1.0,
            exact_match=True
        )
        
        self.assertEqual(result.image_path, Path("test.jpg"))
        self.assertEqual(result.ground_truth, "ABC123")
        self.assertEqual(result.predicted, "ABC123") 
        self.assertEqual(result.accuracy, 1.0)
        self.assertTrue(result.exact_match)
    
    def test_directory_result(self):
        """测试目录结果数据结构"""
        results = [
            EvaluationResult(Path("img1.jpg"), "A", "A", 1.0, True),
            EvaluationResult(Path("img2.jpg"), "B", "C", 0.5, False)
        ]
        
        dir_result = DirectoryResult(
            directory=Path("test_dir"),
            total_images=2,
            average_accuracy=0.75,
            exact_match_count=1,
            exact_match_rate=0.5,
            results=results
        )
        
        self.assertEqual(dir_result.directory, Path("test_dir"))
        self.assertEqual(dir_result.total_images, 2)
        self.assertEqual(dir_result.average_accuracy, 0.75)
        self.assertEqual(dir_result.exact_match_count, 1)
        self.assertEqual(dir_result.exact_match_rate, 0.5)
        self.assertEqual(len(dir_result.results), 2)


if __name__ == '__main__':
    unittest.main()