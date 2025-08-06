#!/usr/bin/env python3
"""
报告生成工具
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging

from ..models.base import TestSummary, DirectoryResult, EvaluationResult
from ..config import ReportConstants, EvaluationConstants


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """初始化报告生成器
        
        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir) if output_dir else Path("data/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def generate_markdown_report(self, summary: TestSummary) -> str:
        """生成Markdown格式报告
        
        Args:
            summary: 测试汇总结果
            
        Returns:
            str: Markdown格式的报告内容
        """
        report = []
        
        # 标题和基本信息
        report.append(f"# {summary.model_name} 图片识别准确率报告")
        report.append("")
        report.append(f"**测试时间**: {summary.test_timestamp}")
        report.append(f"**使用模型**: {summary.model_name}")
        report.append(f"**测试图片总数**: {summary.total_images}")
        report.append(f"**总体准确率**: {summary.overall_accuracy:.4f} ({summary.overall_accuracy*100:.2f}%)")
        report.append("")
        
        # 技术实现细节
        self._add_technical_details(report, summary.technical_details)
        
        # 分目录结果
        self._add_directory_results(report, summary.directory_results)
        
        # 统计信息
        self._add_statistics(report, summary)
        
        # 评估方法说明
        self._add_evaluation_methods(report)
        
        # 技术挑战和建议
        self._add_technical_insights(report, summary)
        
        # 技术规格汇总
        self._add_technical_summary(report, summary)
        
        return "\n".join(report)
    
    def _add_technical_details(self, report: List[str], technical_details: Dict[str, Any]):
        """添加技术实现细节部分"""
        report.append("## 🔧 技术实现细节")
        report.append("")
        
        # 模型配置
        report.append("### 模型配置")
        report.append("")
        model_name = technical_details.get('model_name', '未知')
        model_type = technical_details.get('model_type', '未知')
        report.append(f"- **模型名称**: {model_name}")
        report.append(f"- **模型类型**: {model_type}")
        
        # 具体配置信息
        config = technical_details.get('config', {})
        if config:
            for key, value in config.items():
                if key not in ['prompt_template']:  # 单独处理提示词
                    report.append(f"- **{key}**: {value}")
        
        # SDK和连接信息（如果是Qwen模型）
        if 'sdk_version' in technical_details:
            report.append(f"- **SDK版本**: {technical_details['sdk_version']}")
            report.append(f"- **接口类型**: LMStudio Python SDK")
            
        if 'lmstudio_url' in technical_details:
            report.append(f"- **连接方式**: WebSocket ({technical_details['lmstudio_url']})")
        
        report.append("")
        
        # 提示词设计（仅对Qwen模型）
        if 'prompt_template' in technical_details:
            report.append("### 提示词设计")
            report.append("")
            report.append("使用的提示词模板：")
            report.append("```")
            report.append(technical_details['prompt_template'])
            report.append("```")
            report.append("")
            
            report.append("**提示词设计原则**:")
            report.append("- 明确要求提取图片中的确切文本")
            report.append("- 强调这是字母数字编码或产品编号")
            report.append("- 要求仅返回文本，无额外解释")
            report.append("- 说明可能包含 # 或 . 等符号")
            report.append("")
        
        # 后处理规则（仅对Qwen模型）
        if 'post_processing_rules' in technical_details:
            report.append("### 后处理规则")
            report.append("")
            for i, rule in enumerate(technical_details['post_processing_rules'], 1):
                report.append(f"{i}. {rule}")
            report.append("")
        
        # 优化说明（仅对PaddleOCR）
        if 'optimization_notes' in technical_details:
            report.append("### 配置优化说明")
            report.append("")
            for note in technical_details['optimization_notes']:
                report.append(f"- {note}")
            report.append("")
        
        # 测试环境
        if 'test_environment' in technical_details:
            report.append("### 测试环境")
            report.append("")
            env = technical_details['test_environment']
            report.append(f"- **Python版本**: {env.get('python_version', '未知')}")
            report.append(f"- **操作系统**: {env.get('platform', '未知')}")
            report.append(f"- **系统架构**: {env.get('architecture', ('未知', '未知'))[0]}")
            report.append(f"- **处理器**: {env.get('processor', '未知')}")
            report.append("")
    
    def _add_directory_results(self, report: List[str], directory_results: List[DirectoryResult]):
        """添加分目录结果"""
        report.append("## 分目录结果")
        report.append("")
        
        for dir_result in directory_results:
            dir_name = dir_result.directory.name
            report.append(f"### {dir_name}")
            report.append("")
            report.append(f"- **目录路径**: {dir_result.directory}")
            report.append(f"- **图片数量**: {dir_result.total_images}")
            report.append(f"- **平均准确率**: {dir_result.average_accuracy:.4f} ({dir_result.average_accuracy*100:.2f}%)")
            report.append(f"- **完全匹配数量**: {dir_result.exact_match_count}")
            report.append(f"- **完全匹配率**: {dir_result.exact_match_rate:.4f} ({dir_result.exact_match_rate*100:.2f}%)")
            report.append("")
            
            # 详细结果表格（只显示前10个，避免报告过长）
            report.append("#### 详细识别结果（前10个样本）")
            report.append("")
            report.append("| 图片名称 | 标准答案 | 识别结果 | 准确率 | 完全匹配 |")
            report.append("|---------|---------|---------|--------|---------|")
            
            for i, result in enumerate(dir_result.results[:10]):
                match_mark = "✓" if result.exact_match else "✗"
                image_name = result.image_path.name
                report.append(f"| {image_name} | {result.ground_truth} | {result.predicted} | {result.accuracy:.4f} | {match_mark} |")
            
            if len(dir_result.results) > 10:
                report.append(f"| ... | ... | ... | ... | ... |")
                report.append(f"| (共{len(dir_result.results)}个样本) | | | | |")
            
            report.append("")
    
    def _add_statistics(self, report: List[str], summary: TestSummary):
        """添加统计信息"""
        report.append("## 统计信息")
        report.append("")
        
        # 计算准确率分布
        accuracy_ranges = {range_name: 0 for range_name in EvaluationConstants.ACCURACY_RANGES.keys()}
        total_exact_matches = 0
        
        for dir_result in summary.directory_results:
            total_exact_matches += dir_result.exact_match_count
            for result in dir_result.results:
                acc = result.accuracy
                for range_name, (min_acc, max_acc) in EvaluationConstants.ACCURACY_RANGES.items():
                    if range_name == '<0.6' and acc < max_acc:
                        accuracy_ranges[range_name] += 1
                        break
                    elif range_name != '<0.6' and min_acc <= acc < max_acc:
                        accuracy_ranges[range_name] += 1
                        break
                    elif range_name == '0.9-1.0' and acc >= min_acc:  # 包含1.0
                        accuracy_ranges[range_name] += 1
                        break
        
        report.append(f"- **完全匹配数量**: {total_exact_matches}")
        report.append(f"- **完全匹配率**: {summary.overall_exact_match_rate:.4f} ({summary.overall_exact_match_rate*100:.2f}%)")
        report.append("")
        
        report.append("### 准确率分布")
        report.append("")
        for range_name, count in accuracy_ranges.items():
            percentage = count / summary.total_images * 100 if summary.total_images > 0 else 0
            report.append(f"- **{range_name}**: {count} 张图片 ({percentage:.1f}%)")
        report.append("")
    
    def _add_evaluation_methods(self, report: List[str]):
        """添加评估方法说明"""
        report.append("## 📊 评估方法")
        report.append("")
        
        report.append("### 准确率计算")
        report.append("")
        report.append("本测试使用以下评估指标：")
        report.append("")
        report.append("1. **完全匹配准确率**：")
        report.append("   - 识别结果与标准答案完全相同时计为1，否则为0")
        report.append("   - 公式：`准确率 = 完全匹配数量 / 总图片数`")
        report.append("")
        report.append("2. **编辑距离准确率**：")
        report.append("   - 基于Levenshtein编辑距离计算字符级相似度")
        report.append("   - 公式：`准确率 = 1 - (编辑距离 / max(len(标准答案), len(识别结果)))`")
        report.append("")
        report.append("3. **总体准确率**：")
        report.append("   - 所有图片编辑距离准确率的平均值")
        report.append("")
        
        report.append("### 数据集说明")
        report.append("")
        report.append("**图片特征**：")
        report.append("- 内容：工业产品编号、批次号、序列号等")
        report.append("- 格式：字母数字组合，包含#、.等特殊符号")
        report.append("- 示例：P4P601#03, PLA196.12, PPT770#02")
        report.append("")
    
    def _add_technical_insights(self, report: List[str], summary: TestSummary):
        """添加技术洞察和建议"""
        report.append("## ⚠️ 技术挑战与解决方案")
        report.append("")
        
        model_name = summary.model_name
        if "Qwen" in model_name:
            report.append("### 主要挑战")
            report.append("")
            report.append("1. **多模态模型的文本提取**：")
            report.append("   - 挑战：LLM倾向于描述图片而非提取文本")
            report.append("   - 解决：设计专门的提示词强调仅提取文本")
            report.append("")
            report.append("2. **响应格式不一致**：")
            report.append("   - 挑战：模型可能返回解释性文字")
            report.append("   - 解决：实施多层后处理清洗规则")
            report.append("")
            report.append("3. **特殊符号识别**：")
            report.append("   - 挑战：#、.等符号可能被误识别")
            report.append("   - 解决：在提示词中明确说明可能的符号类型")
            report.append("")
        
        elif "PP-OCR" in model_name:
            report.append("### 配置优化要点")
            report.append("")
            report.append("1. **禁用文档预处理**：对小图片的简单文本，复杂预处理反而有害")
            report.append("2. **选择合适语言模型**：英文模型对字母数字混合文本效果更好")
            report.append("3. **参数调优**：根据具体图片特点调整检测和识别参数")
            report.append("")
        
        # 性能优化建议
        report.append("## 💡 结论与建议")
        report.append("")
        
        if summary.overall_accuracy >= 0.95:
            report.append(f"### {model_name} 表现优异")
            report.append("")
            report.append(f"- 准确率达到 {summary.overall_accuracy*100:.2f}%，表现优异")
            report.append("- 适用于对准确率要求较高的生产环境")
        elif summary.overall_accuracy >= 0.8:
            report.append(f"### {model_name} 表现良好")
            report.append("")
            report.append(f"- 准确率为 {summary.overall_accuracy*100:.2f}%，表现良好")
            report.append("- 可考虑进一步优化以提高准确率")
        else:
            report.append(f"### {model_name} 需要优化")
            report.append("")
            report.append(f"- 准确率为 {summary.overall_accuracy*100:.2f}%，建议进行优化")
            report.append("- 考虑调整配置参数或后处理规则")
        
        report.append("")
    
    def _add_technical_summary(self, report: List[str], summary: TestSummary):
        """添加技术规格汇总"""
        report.append("---")
        report.append("")
        report.append("### 📋 技术规格汇总")
        report.append("")
        report.append("```yaml")
        report.append("测试配置:")
        report.append(f"  模型: {summary.technical_details.get('model_name', '未知')}")
        report.append(f"  类型: {summary.technical_details.get('model_type', '未知')}")
        
        if 'sdk_version' in summary.technical_details:
            report.append(f"  SDK: LMStudio {summary.technical_details['sdk_version']}")
        
        report.append("")
        report.append("数据集:")
        report.append(f"  总图片数: {summary.total_images}")
        report.append("  格式: JPG/PNG等")
        report.append("  内容: 工业编号识别")
        report.append("")
        report.append("评估指标:")
        report.append(f"  总体准确率: {summary.overall_accuracy:.4f}")
        report.append(f"  完全匹配率: {summary.overall_exact_match_rate:.4f}")
        report.append("  计算方法: Levenshtein距离")
        
        # 性能信息
        if 'total_processing_time' in summary.technical_details:
            processing_time = summary.technical_details['total_processing_time']
            avg_time = summary.technical_details.get('average_processing_time', 0)
            report.append("")
            report.append("性能指标:")
            report.append(f"  总处理时间: {processing_time:.2f}秒")
            report.append(f"  平均处理时间: {avg_time:.2f}秒/图片")
        
        report.append("```")
        report.append("")
        report.append("*报告生成时间: " + datetime.now().strftime(ReportConstants.DISPLAY_TIMESTAMP_FORMAT) + "*")
    
    def save_markdown_report(self, summary: TestSummary, filename: Optional[str] = None) -> Path:
        """保存Markdown报告到文件
        
        Args:
            summary: 测试汇总结果
            filename: 文件名，如果未指定则自动生成
            
        Returns:
            Path: 保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime(ReportConstants.REPORT_TIMESTAMP_FORMAT)
            filename = ReportConstants.DEFAULT_REPORT_NAME_TEMPLATE.format(
                model=summary.model_name, timestamp=timestamp
            ) + ReportConstants.MARKDOWN_EXTENSION
        
        file_path = self.output_dir / filename
        report_content = self.generate_markdown_report(summary)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Markdown报告已保存至: {file_path}")
        return file_path
    
    def save_json_results(self, summary: TestSummary, filename: Optional[str] = None) -> Path:
        """保存JSON格式的详细结果
        
        Args:
            summary: 测试汇总结果
            filename: 文件名，如果未指定则自动生成
            
        Returns:
            Path: 保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime(ReportConstants.REPORT_TIMESTAMP_FORMAT)
            filename = ReportConstants.DEFAULT_RESULTS_NAME_TEMPLATE.format(
                model=summary.model_name, timestamp=timestamp
            ) + ReportConstants.JSON_EXTENSION
        
        file_path = self.output_dir / filename
        
        # 转换为JSON可序列化的格式
        json_data = self._summary_to_dict(summary)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"JSON结果已保存至: {file_path}")
        return file_path
    
    def _summary_to_dict(self, summary: TestSummary) -> Dict[str, Any]:
        """将TestSummary转换为字典格式"""
        return {
            'model_name': summary.model_name,
            'test_timestamp': summary.test_timestamp,
            'total_images': summary.total_images,
            'overall_accuracy': summary.overall_accuracy,
            'overall_exact_match_rate': summary.overall_exact_match_rate,
            'directory_results': [
                {
                    'directory': str(dir_result.directory),
                    'total_images': dir_result.total_images,
                    'average_accuracy': dir_result.average_accuracy,
                    'exact_match_count': dir_result.exact_match_count,
                    'exact_match_rate': dir_result.exact_match_rate,
                    'results': [
                        {
                            'image_path': str(result.image_path),
                            'ground_truth': result.ground_truth,
                            'predicted': result.predicted,
                            'accuracy': result.accuracy,
                            'exact_match': result.exact_match,
                            'metadata': result.metadata
                        }
                        for result in dir_result.results
                    ],
                    'metadata': dir_result.metadata
                }
                for dir_result in summary.directory_results
            ],
            'technical_details': summary.technical_details,
            'metadata': summary.metadata
        }