#!/usr/bin/env python3
"""
配置管理测试
"""

import unittest
import tempfile
import json
import yaml
from pathlib import Path

from src.ocr_evaluation.config import Config, get_config, set_config


class TestConfig(unittest.TestCase):
    """配置管理测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        for file in self.temp_dir.glob("*"):
            file.unlink()
        self.temp_dir.rmdir()
    
    def test_default_config(self):
        """测试默认配置"""
        config = Config()
        
        # 测试基本配置项
        self.assertEqual(config.get('models.paddleocr.lang'), 'en')
        self.assertEqual(config.get('models.qwen_vl.model_name'), 'qwen/qwen2.5-vl-7b')
        self.assertEqual(config.get('evaluation.accuracy_threshold'), 0.95)
        self.assertEqual(config.get('logging.level'), 'INFO')
    
    def test_config_get_set(self):
        """测试配置获取和设置"""
        config = Config()
        
        # 测试获取不存在的键
        self.assertIsNone(config.get('nonexistent.key'))
        self.assertEqual(config.get('nonexistent.key', 'default'), 'default')
        
        # 测试设置和获取
        config.set('test.key', 'test_value')
        self.assertEqual(config.get('test.key'), 'test_value')
        
        # 测试嵌套设置
        config.set('nested.level1.level2', 'deep_value')
        self.assertEqual(config.get('nested.level1.level2'), 'deep_value')
    
    def test_yaml_config_loading(self):
        """测试YAML配置文件加载"""
        # 创建测试YAML配置
        yaml_config = {
            'models': {
                'paddleocr': {
                    'lang': 'ch',
                    'use_gpu': True
                }
            },
            'logging': {
                'level': 'DEBUG'
            }
        }
        
        yaml_file = self.temp_dir / 'test_config.yaml'
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_config, f)
        
        # 加载配置
        config = Config(yaml_file)
        
        # 验证配置合并
        self.assertEqual(config.get('models.paddleocr.lang'), 'ch')
        self.assertEqual(config.get('models.paddleocr.use_gpu'), True)
        self.assertEqual(config.get('logging.level'), 'DEBUG')
        
        # 验证默认配置仍然存在
        self.assertEqual(config.get('models.qwen_vl.model_name'), 'qwen/qwen2.5-vl-7b')
    
    def test_json_config_loading(self):
        """测试JSON配置文件加载"""
        # 创建测试JSON配置
        json_config = {
            'models': {
                'qwen_vl': {
                    'temperature': 0.5
                }
            },
            'evaluation': {
                'accuracy_threshold': 0.8
            }
        }
        
        json_file = self.temp_dir / 'test_config.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_config, f)
        
        # 加载配置
        config = Config(json_file)
        
        # 验证配置合并
        self.assertEqual(config.get('models.qwen_vl.temperature'), 0.5)
        self.assertEqual(config.get('evaluation.accuracy_threshold'), 0.8)
    
    def test_config_save(self):
        """测试配置保存"""
        config = Config()
        
        # 修改配置
        config.set('test.value', 'save_test')
        config.set('models.paddleocr.lang', 'fr')
        
        # 保存为YAML
        yaml_file = self.temp_dir / 'saved_config.yaml'
        config.save_config(yaml_file)
        
        # 验证文件存在
        self.assertTrue(yaml_file.exists())
        
        # 加载保存的配置并验证
        loaded_config = Config(yaml_file)
        self.assertEqual(loaded_config.get('test.value'), 'save_test')
        self.assertEqual(loaded_config.get('models.paddleocr.lang'), 'fr')
    
    def test_convenience_methods(self):
        """测试便捷方法"""
        config = Config()
        
        # 测试模型配置获取方法
        paddleocr_config = config.get_paddleocr_config()
        self.assertIsInstance(paddleocr_config, dict)
        self.assertIn('lang', paddleocr_config)
        
        qwen_config = config.get_qwen_config()
        self.assertIsInstance(qwen_config, dict)
        self.assertIn('model_name', qwen_config)
        
        # 测试其他便捷方法
        logging_config = config.get_logging_config()
        self.assertIn('level', logging_config)
        
        output_config = config.get_output_config()
        self.assertIn('reports_dir', output_config)
    
    def test_global_config(self):
        """测试全局配置管理"""
        # 测试默认全局配置
        global_config = get_config()
        self.assertIsInstance(global_config, Config)
        
        # 测试设置全局配置
        new_config = Config()
        new_config.set('global.test', 'global_value')
        set_config(new_config)
        
        # 验证全局配置已更新
        updated_global = get_config()
        self.assertEqual(updated_global.get('global.test'), 'global_value')


if __name__ == '__main__':
    unittest.main()