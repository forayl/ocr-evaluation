#!/usr/bin/env python3
"""
OCR评估框架配置管理模块
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import json


class Config:
    """配置管理类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'models': {
            'paddleocr': {
                'use_doc_orientation_classify': False,
                'use_doc_unwarping': False,
                'use_textline_orientation': False,
                'lang': 'en',
                'use_gpu': False
            },
            'qwen_vl': {
                'model_name': 'qwen/qwen2.5-vl-7b',
                'lmstudio_url': 'ws://localhost:1234',
                'temperature': 0.1,
                'max_tokens': 50
            }
        },
        'evaluation': {
            'accuracy_threshold': 0.95,
            'use_levenshtein': True,
            'case_sensitive': True
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': None  # 设置为文件路径以启用文件日志
        },
        'output': {
            'reports_dir': 'data/reports',
            'results_dir': 'data/outputs',
            'report_format': 'markdown'  # 支持 'markdown', 'json', 'html'
        }
    }
    
    def __init__(self, config_file: Optional[Path] = None):
        """初始化配置
        
        Args:
            config_file: 配置文件路径，如果未指定则使用默认配置
        """
        self._config = self.DEFAULT_CONFIG.copy()
        self._config_file = config_file
        
        if config_file and config_file.exists():
            self.load_config(config_file)
    
    def load_config(self, config_file: Path):
        """从文件加载配置
        
        Args:
            config_file: 配置文件路径，支持YAML和JSON格式
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yml', '.yaml']:
                    user_config = yaml.safe_load(f)
                elif config_file.suffix.lower() == '.json':
                    user_config = json.load(f)
                else:
                    raise ValueError(f"不支持的配置文件格式: {config_file.suffix}")
            
            # 递归合并配置
            self._config = self._merge_configs(self._config, user_config)
            
        except Exception as e:
            raise ValueError(f"加载配置文件失败 {config_file}: {e}")
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并配置字典"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点分割路径
        
        Args:
            key: 配置键，支持嵌套路径如 'models.paddleocr.lang'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """设置配置值
        
        Args:
            key: 配置键，支持嵌套路径
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        # 导航到父级字典
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def save_config(self, config_file: Optional[Path] = None):
        """保存配置到文件
        
        Args:
            config_file: 配置文件路径，如果未指定则使用初始化时的文件
        """
        file_path = config_file or self._config_file
        if not file_path:
            raise ValueError("未指定配置文件路径")
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yml', '.yaml']:
                yaml.dump(self._config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            elif file_path.suffix.lower() == '.json':
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            else:
                raise ValueError(f"不支持的配置文件格式: {file_path.suffix}")
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取完整配置字典"""
        return self._config.copy()
    
    # 便捷方法
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """获取指定模型的配置"""
        return self.get(f'models.{model_name}', {})
    
    def get_paddleocr_config(self) -> Dict[str, Any]:
        """获取PaddleOCR配置"""
        return self.get_model_config('paddleocr')
    
    def get_qwen_config(self) -> Dict[str, Any]:
        """获取Qwen配置"""
        return self.get_model_config('qwen_vl')
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get('logging', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """获取输出配置"""
        return self.get('output', {})


# 全局配置实例
_global_config: Optional[Config] = None

def get_config() -> Config:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config

def set_config(config: Config):
    """设置全局配置实例"""
    global _global_config
    _global_config = config

def load_config_from_file(config_file: Path) -> Config:
    """从文件加载配置并设置为全局配置"""
    config = Config(config_file)
    set_config(config)
    return config