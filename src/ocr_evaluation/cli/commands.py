#!/usr/bin/env python3
"""
CLI命令实现
"""

import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import json

from ..config import (
    get_config, load_config_from_file, 
    DATA_DIR, IMAGES_DIR, REPORTS_DIR, OUTPUTS_DIR,
    ModelTypes
)
from ..models import create_evaluator, get_supported_models
from ..utils import ReportGenerator, setup_logging, get_logger, create_progress_logger


class BaseCommand:
    """命令基类"""
    
    def __init__(self):
        self.logger = None
    
    def setup_logging(self, args):
        """设置日志系统"""
        # 从命令行参数或配置获取日志级别
        log_level = getattr(args, 'log_level', None)
        if log_level:
            config_dict = {'logging': {'level': log_level}}
            setup_logging(config_dict)
        else:
            config = get_config()
            setup_logging(config.config)
        
        self.logger = get_logger(self.__class__.__name__)
    
    def add_common_arguments(self, parser: argparse.ArgumentParser):
        """添加通用参数"""
        parser.add_argument(
            '--config', '-c',
            type=Path,
            help='配置文件路径 (YAML或JSON格式)'
        )
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='日志级别'
        )
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='详细输出 (相当于 --log-level DEBUG)'
        )
    
    def load_config(self, args):
        """加载配置"""
        if args.verbose:
            args.log_level = 'DEBUG'
        
        if args.config and args.config.exists():
            load_config_from_file(args.config)
            if hasattr(args, 'log_level') and args.log_level:
                config = get_config()
                config.set('logging.level', args.log_level)


class EvaluateCommand(BaseCommand):
    """评估命令"""
    
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        """添加评估命令参数"""
        parser.add_argument(
            'model',
            choices=get_supported_models(),
            help='要使用的模型类型'
        )
        parser.add_argument(
            '--images-dir', '-i',
            type=Path,
            default=IMAGES_DIR,
            help=f'图片目录路径 (默认: {IMAGES_DIR})'
        )
        parser.add_argument(
            '--output-dir', '-o',
            type=Path,
            default=REPORTS_DIR,
            help=f'报告输出目录 (默认: {REPORTS_DIR})'
        )
        parser.add_argument(
            '--model-config',
            type=str,
            help='模型配置 (JSON格式字符串)'
        )
        parser.add_argument(
            '--report-format',
            choices=['markdown', 'json', 'both'],
            default='both',
            help='报告格式 (默认: both)'
        )
        parser.add_argument(
            '--report-name',
            type=str,
            help='自定义报告文件名前缀'
        )
    
    def run(self, args):
        """执行评估命令"""
        self.load_config(args)
        self.setup_logging(args)
        
        self.logger.info("🚀 开始OCR模型评估")
        self.logger.info(f"模型类型: {args.model}")
        self.logger.info(f"图片目录: {args.images_dir}")
        self.logger.info(f"输出目录: {args.output_dir}")
        
        try:
            # 验证输入目录
            if not args.images_dir.exists():
                self.logger.error(f"图片目录不存在: {args.images_dir}")
                return 1
            
            # 创建输出目录
            args.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 解析模型配置
            model_config = None
            if args.model_config:
                try:
                    model_config = json.loads(args.model_config)
                except json.JSONDecodeError as e:
                    self.logger.error(f"模型配置JSON格式错误: {e}")
                    return 1
            
            # 创建评估器
            self.logger.info("正在创建评估器...")
            evaluator = create_evaluator(args.model, model_config)
            
            # 执行评估
            self.logger.info("正在执行数据集评估...")
            summary = evaluator.evaluate_dataset(args.images_dir)
            
            if summary is None:
                self.logger.error("评估失败")
                return 1
            
            # 生成报告
            self.logger.info("正在生成评估报告...")
            report_generator = ReportGenerator(args.output_dir)
            
            report_files = []
            
            if args.report_format in ['markdown', 'both']:
                markdown_file = report_generator.save_markdown_report(
                    summary, 
                    args.report_name + '.md' if args.report_name else None
                )
                report_files.append(markdown_file)
            
            if args.report_format in ['json', 'both']:
                json_file = report_generator.save_json_results(
                    summary,
                    args.report_name + '.json' if args.report_name else None
                )
                report_files.append(json_file)
            
            # 显示结果摘要
            self._show_summary(summary)
            
            # 显示生成的文件
            self.logger.info("\n📄 生成的报告文件:")
            for file_path in report_files:
                self.logger.info(f"  - {file_path}")
            
            self.logger.info("✅ 评估完成!")
            return 0
            
        except Exception as e:
            self.logger.error(f"评估过程中发生错误: {e}", exc_info=True)
            return 1
    
    def _show_summary(self, summary):
        """显示评估结果摘要"""
        self.logger.info("\n📊 评估结果摘要:")
        self.logger.info(f"  模型: {summary.model_name}")
        self.logger.info(f"  总图片数: {summary.total_images}")
        self.logger.info(f"  总体准确率: {summary.overall_accuracy:.4f} ({summary.overall_accuracy*100:.2f}%)")
        self.logger.info(f"  完全匹配率: {summary.overall_exact_match_rate:.4f} ({summary.overall_exact_match_rate*100:.2f}%)")
        
        # 显示各目录结果
        self.logger.info("\n📁 分目录结果:")
        for dir_result in summary.directory_results:
            dir_name = dir_result.directory.name
            self.logger.info(f"  {dir_name}: {dir_result.total_images}张图片, "
                           f"准确率 {dir_result.average_accuracy:.4f} ({dir_result.average_accuracy*100:.2f}%)")


class CompareCommand(BaseCommand):
    """模型对比命令"""
    
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        """添加对比命令参数"""
        parser.add_argument(
            'models',
            nargs='+',
            choices=get_supported_models(),
            help='要对比的模型类型 (可指定多个)'
        )
        parser.add_argument(
            '--images-dir', '-i',
            type=Path,
            default=IMAGES_DIR,
            help=f'图片目录路径 (默认: {IMAGES_DIR})'
        )
        parser.add_argument(
            '--output-dir', '-o',
            type=Path,
            default=REPORTS_DIR,
            help=f'报告输出目录 (默认: {REPORTS_DIR})'
        )
        parser.add_argument(
            '--comparison-report',
            type=str,
            default='model_comparison',
            help='对比报告文件名前缀 (默认: model_comparison)'
        )
    
    def run(self, args):
        """执行模型对比命令"""
        self.load_config(args)
        self.setup_logging(args)
        
        self.logger.info("🔄 开始模型对比评估")
        self.logger.info(f"对比模型: {', '.join(args.models)}")
        
        try:
            # 验证输入
            if len(args.models) < 2:
                self.logger.error("至少需要指定两个模型进行对比")
                return 1
            
            if not args.images_dir.exists():
                self.logger.error(f"图片目录不存在: {args.images_dir}")
                return 1
            
            args.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 评估每个模型
            summaries = []
            for model_type in args.models:
                self.logger.info(f"\n🔍 评估模型: {model_type}")
                
                evaluator = create_evaluator(model_type)
                summary = evaluator.evaluate_dataset(args.images_dir)
                
                if summary:
                    summaries.append(summary)
                    self.logger.info(f"  {model_type} 完成: 准确率 {summary.overall_accuracy:.4f}")
                else:
                    self.logger.warning(f"  {model_type} 评估失败")
            
            if len(summaries) < 2:
                self.logger.error("至少需要两个成功的评估结果才能进行对比")
                return 1
            
            # 生成对比报告
            self.logger.info("\n📊 生成对比报告...")
            comparison_report = self._generate_comparison_report(summaries)
            
            report_file = args.output_dir / f"{args.comparison_report}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(comparison_report)
            
            self.logger.info(f"📄 对比报告已保存至: {report_file}")
            
            # 显示对比摘要
            self._show_comparison_summary(summaries)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"对比过程中发生错误: {e}", exc_info=True)
            return 1
    
    def _generate_comparison_report(self, summaries: List) -> str:
        """生成对比报告"""
        from datetime import datetime
        
        report = []
        report.append("# OCR模型对比评估报告")
        report.append("")
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**对比模型**: {', '.join([s.model_name for s in summaries])}")
        report.append("")
        
        # 总体对比表格
        report.append("## 📊 总体性能对比")
        report.append("")
        report.append("| 模型 | 总图片数 | 总体准确率 | 完全匹配率 | 平均处理时间 |")
        report.append("|------|----------|------------|------------|--------------|")
        
        for summary in summaries:
            processing_time = summary.technical_details.get('average_processing_time', 0)
            report.append(f"| {summary.model_name} | {summary.total_images} | "
                         f"{summary.overall_accuracy:.4f} ({summary.overall_accuracy*100:.2f}%) | "
                         f"{summary.overall_exact_match_rate:.4f} ({summary.overall_exact_match_rate*100:.2f}%) | "
                         f"{processing_time:.3f}s |")
        
        report.append("")
        
        # 分目录对比
        report.append("## 📁 分目录性能对比")
        report.append("")
        
        # 获取所有目录
        all_directories = set()
        for summary in summaries:
            for dir_result in summary.directory_results:
                all_directories.add(dir_result.directory.name)
        
        for directory in sorted(all_directories):
            report.append(f"### {directory}")
            report.append("")
            report.append("| 模型 | 图片数量 | 准确率 | 完全匹配率 |")
            report.append("|------|----------|--------|------------|")
            
            for summary in summaries:
                dir_result = next(
                    (dr for dr in summary.directory_results if dr.directory.name == directory),
                    None
                )
                if dir_result:
                    report.append(f"| {summary.model_name} | {dir_result.total_images} | "
                                 f"{dir_result.average_accuracy:.4f} ({dir_result.average_accuracy*100:.2f}%) | "
                                 f"{dir_result.exact_match_rate:.4f} ({dir_result.exact_match_rate*100:.2f}%) |")
                else:
                    report.append(f"| {summary.model_name} | - | - | - |")
            
            report.append("")
        
        # 结论和建议
        report.append("## 💡 结论和建议")
        report.append("")
        
        # 找出表现最好的模型
        best_model = max(summaries, key=lambda s: s.overall_accuracy)
        report.append(f"### 最佳整体性能: {best_model.model_name}")
        report.append(f"- 准确率: {best_model.overall_accuracy:.4f} ({best_model.overall_accuracy*100:.2f}%)")
        report.append(f"- 完全匹配率: {best_model.overall_exact_match_rate:.4f} ({best_model.overall_exact_match_rate*100:.2f}%)")
        report.append("")
        
        # 各模型优势分析
        report.append("### 模型特性分析")
        report.append("")
        for summary in summaries:
            model_type = summary.technical_details.get('model_type', 'unknown')
            if model_type == 'paddleocr':
                report.append(f"**{summary.model_name}** (专业OCR模型):")
                report.append("- ✅ 专门针对文字识别优化")
                report.append("- ✅ 处理速度快")
                report.append("- ❌ 功能相对单一")
            elif model_type == 'qwen_vl':
                report.append(f"**{summary.model_name}** (多模态LLM):")
                report.append("- ✅ 具备图像理解能力")
                report.append("- ✅ 可处理复杂场景")
                report.append("- ❌ 推理速度相对较慢")
            report.append("")
        
        return "\n".join(report)
    
    def _show_comparison_summary(self, summaries: List):
        """显示对比摘要"""
        self.logger.info("\n📊 模型对比摘要:")
        
        # 按准确率排序
        sorted_summaries = sorted(summaries, key=lambda s: s.overall_accuracy, reverse=True)
        
        for i, summary in enumerate(sorted_summaries, 1):
            self.logger.info(f"  {i}. {summary.model_name}: "
                           f"准确率 {summary.overall_accuracy:.4f} ({summary.overall_accuracy*100:.2f}%), "
                           f"匹配率 {summary.overall_exact_match_rate:.4f} ({summary.overall_exact_match_rate*100:.2f}%)")


class ConfigCommand(BaseCommand):
    """配置管理命令"""
    
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        """添加配置命令参数"""
        subparsers = parser.add_subparsers(dest='config_action', help='配置操作')
        
        # 显示配置
        show_parser = subparsers.add_parser('show', help='显示当前配置')
        show_parser.add_argument(
            '--key', '-k',
            type=str,
            help='显示特定配置项 (支持点分割路径，如 models.paddleocr.lang)'
        )
        
        # 设置配置
        set_parser = subparsers.add_parser('set', help='设置配置项')
        set_parser.add_argument('key', help='配置项键名 (支持点分割路径)')
        set_parser.add_argument('value', help='配置项值')
        
        # 生成默认配置文件
        generate_parser = subparsers.add_parser('generate', help='生成默认配置文件')
        generate_parser.add_argument(
            '--output', '-o',
            type=Path,
            default='config.yaml',
            help='输出文件路径 (默认: config.yaml)'
        )
        generate_parser.add_argument(
            '--format',
            choices=['yaml', 'json'],
            default='yaml',
            help='配置文件格式 (默认: yaml)'
        )
    
    def run(self, args):
        """执行配置命令"""
        self.load_config(args)
        self.setup_logging(args)
        
        if args.config_action == 'show':
            return self._show_config(args)
        elif args.config_action == 'set':
            return self._set_config(args)
        elif args.config_action == 'generate':
            return self._generate_config(args)
        else:
            self.logger.error("未指定配置操作，使用 --help 查看可用操作")
            return 1
    
    def _show_config(self, args) -> int:
        """显示配置"""
        config = get_config()
        
        if args.key:
            # 显示特定配置项
            value = config.get(args.key)
            if value is not None:
                self.logger.info(f"{args.key}: {value}")
            else:
                self.logger.error(f"配置项 '{args.key}' 不存在")
                return 1
        else:
            # 显示完整配置
            import yaml
            config_yaml = yaml.dump(config.config, default_flow_style=False, 
                                   allow_unicode=True, indent=2)
            print(config_yaml)
        
        return 0
    
    def _set_config(self, args) -> int:
        """设置配置项"""
        config = get_config()
        
        # 尝试解析值的类型
        value = args.value
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        config.set(args.key, value)
        self.logger.info(f"配置项 '{args.key}' 已设置为: {value}")
        
        return 0
    
    def _generate_config(self, args) -> int:
        """生成默认配置文件"""
        try:
            config = get_config()
            config.save_config(args.output)
            self.logger.info(f"默认配置文件已生成: {args.output}")
            return 0
        except Exception as e:
            self.logger.error(f"生成配置文件失败: {e}")
            return 1