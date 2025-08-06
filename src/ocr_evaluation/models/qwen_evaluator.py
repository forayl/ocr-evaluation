#!/usr/bin/env python3
"""
Qwen2.5-VL评估器实现
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import re
import platform
import sys

from .base import BaseEvaluator
from ..config import ModelTypes, QwenConstants, TextProcessingConstants


class QwenVLEvaluator(BaseEvaluator):
    """Qwen2.5-VL多模态模型评估器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化Qwen评估器
        
        Args:
            config: Qwen模型配置参数
        """
        # 使用默认配置
        default_config = {
            'model_name': QwenConstants.DEFAULT_MODEL_NAME,
            'lmstudio_url': QwenConstants.DEFAULT_LMSTUDIO_URL,
            'temperature': QwenConstants.DEFAULT_TEMPERATURE,
            'max_tokens': QwenConstants.DEFAULT_MAX_TOKENS,
            'prompt_template': QwenConstants.DEFAULT_PROMPT
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(default_config)
        
        # 更新技术细节
        self.technical_details.update({
            'model_name': self.config['model_name'],
            'lmstudio_url': self.config['lmstudio_url'],
            'prompt_template': self.config['prompt_template'],
            'post_processing_rules': [
                "移除解释性前缀词语",
                "去除引号和特殊符号",
                "提取第一行内容", 
                "使用正则表达式匹配字母数字模式",
                "返回最长匹配结果"
            ],
            'test_environment': {
                'python_version': sys.version,
                'platform': platform.platform(),
                'architecture': platform.architecture(),
                'processor': platform.processor(),
            }
        })
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return "Qwen2.5-VL-7B"
    
    def get_model_type(self) -> str:
        """获取模型类型"""
        return ModelTypes.QWEN_VL
    
    def initialize(self) -> bool:
        """初始化Qwen模型"""
        if self.is_initialized:
            return True
        
        self.logger.info("正在初始化Qwen2.5-VL-7B模型...")
        start_time = datetime.now()
        
        try:
            # 导入LMStudio SDK
            import lmstudio as lms
            
            # 记录SDK版本
            try:
                self.technical_details['sdk_version'] = lms.__version__
            except:
                self.technical_details['sdk_version'] = "未知版本"
            
            # 初始化模型连接
            self.model = lms.llm(self.config['model_name'])
            
            # 测试连接
            test_chat = lms.Chat()
            test_chat.add_user_message("Hello, this is a connection test.")
            
            try:
                test_response = self.model.respond(test_chat)
                
                self.logger.info("Qwen2.5-VL-7B模型初始化成功")
                self.logger.info(f"连接测试响应: {str(test_response.content)[:50]}...")
                
                self.is_initialized = True
                
                # 记录初始化时间
                init_time = (datetime.now() - start_time).total_seconds()
                self.technical_details['initialization_time'] = init_time
                
                return True
                
            except Exception as e:
                self.logger.error(f"Qwen模型连接测试失败: {e}")
                self._log_setup_instructions()
                return False
                
        except ImportError:
            self.logger.error("LMStudio SDK未安装，请运行: pip install lmstudio")
            return False
        except Exception as e:
            self.logger.error(f"Qwen模型初始化失败: {e}")
            self._log_setup_instructions()
            return False
    
    def _log_setup_instructions(self):
        """输出设置说明"""
        self.logger.error("")
        self.logger.error("请按照以下步骤操作:")
        self.logger.error("1. 启动LMStudio应用")
        self.logger.error(f"2. 在LMStudio中搜索并下载 {self.config['model_name']} 模型")
        self.logger.error("3. 加载该模型到LMStudio")
        self.logger.error(f"4. 确保LMStudio Server正在运行 (通常在 {self.config['lmstudio_url']})")
        self.logger.error("5. 重新运行此脚本")
    
    def recognize_image(self, image_path: Path) -> str:
        """使用Qwen2.5-VL识别单张图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            str: 识别的文本结果
        """
        if not self.is_initialized:
            raise RuntimeError("模型未初始化")
        
        try:
            import lmstudio as lms
            
            # 准备图片
            image_handle = lms.prepare_image(str(image_path))
            
            # 创建对话
            chat = lms.Chat()
            
            # 使用配置的提示词模板
            prompt = self.config['prompt_template']
            
            chat.add_user_message(prompt, images=[image_handle])
            
            # 获取模型响应
            prediction = self.model.respond(chat)
            
            # 提取识别文本
            raw_response = ""
            if hasattr(prediction, 'content'):
                raw_response = str(prediction.content)
            elif isinstance(prediction, str):
                raw_response = prediction
            else:
                raw_response = str(prediction)
            
            # 清理响应文本
            cleaned_text = self._clean_response(raw_response.strip())
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Qwen识别失败 {image_path}: {e}")
            return ""
    
    def _clean_response(self, response: str) -> str:
        """清理模型响应，提取产品编号
        
        Args:
            response: 模型原始响应
            
        Returns:
            str: 清理后的文本
        """
        if not response:
            return ""
        
        # 移除常见的解释性前缀
        cleaned = response
        for prefix in TextProcessingConstants.EXPLANATION_PREFIXES:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
        
        # 移除引号
        cleaned = cleaned.strip(TextProcessingConstants.QUOTE_CHARS)
        
        # 如果响应包含多行，取第一行
        lines = cleaned.split('\n')
        if lines:
            cleaned = lines[0].strip()
        
        # 使用正则表达式提取最可能的产品编号格式
        matches = TextProcessingConstants.ALPHANUMERIC_PATTERN.findall(cleaned.upper())
        
        if matches:
            # 返回最长的匹配项
            longest_match = max(matches, key=len)
            return longest_match
        
        return cleaned
    
    def cleanup(self):
        """清理Qwen资源"""
        if self.model is not None:
            # LMStudio SDK通常不需要显式清理，但可以释放引用
            self.model = None
        self.is_initialized = False
        self.logger.debug("Qwen模型资源已清理")
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型详细信息"""
        info = {
            'model_name': self.get_model_name(),
            'model_type': self.get_model_type(),
            'config': self.config,
            'is_initialized': self.is_initialized,
            'lmstudio_url': self.config['lmstudio_url'],
            'prompt_template': self.config['prompt_template'],
            'post_processing_enabled': True
        }
        
        if 'sdk_version' in self.technical_details:
            info['sdk_version'] = self.technical_details['sdk_version']
        
        return info
    
    def test_connection(self) -> bool:
        """测试LMStudio连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            if not self.is_initialized:
                return self.initialize()
            
            # 进行简单的文本生成测试
            import lmstudio as lms
            test_chat = lms.Chat()
            test_chat.add_user_message("Say 'connection test successful' in exactly 3 words.")
            
            response = self.model.respond(test_chat)
            self.logger.info(f"连接测试成功: {response.content}")
            return True
            
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False
    
    @classmethod
    def create_with_default_config(cls) -> 'QwenVLEvaluator':
        """使用默认配置创建评估器实例
        
        Returns:
            QwenVLEvaluator: 使用默认配置的评估器实例
        """
        return cls()
    
    @classmethod
    def create_from_config_dict(cls, config_dict: Dict[str, Any]) -> 'QwenVLEvaluator':
        """从配置字典创建评估器实例
        
        Args:
            config_dict: 配置字典，通常来自配置文件
            
        Returns:
            QwenVLEvaluator: 评估器实例
        """
        qwen_config = config_dict.get('models', {}).get('qwen_vl', {})
        return cls(qwen_config)