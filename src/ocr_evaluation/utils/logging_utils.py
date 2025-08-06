#!/usr/bin/env python3
"""
日志工具模块
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
import sys
from datetime import datetime

from ..config import LoggingConstants


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（仅在控制台使用）"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 保存原始级别名
        original_levelname = record.levelname
        
        # 如果支持颜色输出
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        # 格式化消息
        formatted = super().format(record)
        
        # 恢复原始级别名
        record.levelname = original_levelname
        
        return formatted


class OCRLogger:
    """OCR评估框架统一日志管理器"""
    
    def __init__(self, name: str = "ocr_evaluation"):
        """初始化日志管理器
        
        Args:
            name: 日志器名称
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self._configured = False
    
    def configure(self, config: Optional[Dict[str, Any]] = None):
        """配置日志系统
        
        Args:
            config: 日志配置字典
        """
        if self._configured:
            return
        
        # 使用默认配置或用户配置
        log_config = config or {}
        level = log_config.get('level', LoggingConstants.DEFAULT_LEVEL)
        format_str = log_config.get('format', LoggingConstants.DEFAULT_FORMAT)
        log_file = log_config.get('file')
        
        # 设置日志级别
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(numeric_level)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 控制台处理器（带颜色）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        
        # 使用带颜色的格式化器
        console_formatter = ColoredFormatter(format_str)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果指定了文件路径）
        if log_file:
            self._add_file_handler(log_file, format_str, numeric_level)
        
        # 防止重复配置
        self._configured = True
        
        self.logger.debug(f"日志系统已配置: 级别={level}, 文件={'是' if log_file else '否'}")
    
    def _add_file_handler(self, log_file: str, format_str: str, level: int):
        """添加文件处理器"""
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用轮转文件处理器
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            
            # 文件不使用颜色
            file_formatter = logging.Formatter(format_str)
            file_handler.setFormatter(file_formatter)
            
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            self.logger.warning(f"无法创建日志文件 {log_file}: {e}")
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """获取子日志器
        
        Args:
            name: 子日志器名称，如果未指定则返回主日志器
            
        Returns:
            logging.Logger: 日志器实例
        """
        if name is None:
            return self.logger
        
        # 创建子日志器
        child_name = f"{self.name}.{name}"
        child_logger = logging.getLogger(child_name)
        
        # 子日志器继承父日志器配置
        if not self._configured:
            self.configure()
        
        return child_logger
    
    @classmethod
    def setup_from_config(cls, config: Dict[str, Any]) -> 'OCRLogger':
        """从配置字典创建日志管理器
        
        Args:
            config: 配置字典
            
        Returns:
            OCRLogger: 配置好的日志管理器
        """
        log_config = config.get('logging', {})
        logger_manager = cls()
        logger_manager.configure(log_config)
        return logger_manager


class LogContextManager:
    """日志上下文管理器，用于临时改变日志级别"""
    
    def __init__(self, logger: logging.Logger, level: int):
        """初始化上下文管理器
        
        Args:
            logger: 要管理的日志器
            level: 临时设置的级别
        """
        self.logger = logger
        self.new_level = level
        self.old_level = None
    
    def __enter__(self):
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)


class ProgressLogger:
    """进度日志器，用于显示评估进度"""
    
    def __init__(self, logger: logging.Logger, total: int):
        """初始化进度日志器
        
        Args:
            logger: 底层日志器
            total: 总任务数
        """
        self.logger = logger
        self.total = total
        self.current = 0
        self.start_time = datetime.now()
    
    def update(self, message: str = ""):
        """更新进度
        
        Args:
            message: 可选的进度消息
        """
        self.current += 1
        percentage = (self.current / self.total) * 100
        
        # 计算预估剩余时间
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if self.current > 0:
            eta = elapsed * (self.total - self.current) / self.current
            eta_str = f", 预估剩余: {eta:.0f}秒"
        else:
            eta_str = ""
        
        progress_msg = f"进度: {self.current}/{self.total} ({percentage:.1f}%){eta_str}"
        if message:
            progress_msg = f"{progress_msg} - {message}"
        
        self.logger.info(progress_msg)
    
    def finish(self, message: str = "完成"):
        """完成进度
        
        Args:
            message: 完成消息
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        avg_time = elapsed / self.total if self.total > 0 else 0
        
        finish_msg = f"{message} - 总用时: {elapsed:.2f}秒, 平均: {avg_time:.2f}秒/项"
        self.logger.info(finish_msg)


# 全局日志管理器实例
_global_logger_manager: Optional[OCRLogger] = None

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取全局日志器
    
    Args:
        name: 子日志器名称
        
    Returns:
        logging.Logger: 日志器实例
    """
    global _global_logger_manager
    
    if _global_logger_manager is None:
        _global_logger_manager = OCRLogger()
        _global_logger_manager.configure()
    
    return _global_logger_manager.get_logger(name)

def setup_logging(config: Dict[str, Any]):
    """设置全局日志配置
    
    Args:
        config: 日志配置
    """
    global _global_logger_manager
    _global_logger_manager = OCRLogger.setup_from_config(config)

def with_log_level(logger: logging.Logger, level: int) -> LogContextManager:
    """临时改变日志级别的上下文管理器
    
    Args:
        logger: 日志器
        level: 临时级别
        
    Returns:
        LogContextManager: 上下文管理器
    """
    return LogContextManager(logger, level)

def create_progress_logger(logger: logging.Logger, total: int) -> ProgressLogger:
    """创建进度日志器
    
    Args:
        logger: 底层日志器
        total: 总任务数
        
    Returns:
        ProgressLogger: 进度日志器
    """
    return ProgressLogger(logger, total)