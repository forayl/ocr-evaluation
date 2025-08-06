#!/usr/bin/env python3
"""
OCR评估框架主CLI入口
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List

from .commands import EvaluateCommand, CompareCommand, ConfigCommand
from ..config import get_config, PROJECT_ROOT
from ..utils import get_logger


def create_cli_parser() -> argparse.ArgumentParser:
    """创建CLI参数解析器"""
    parser = argparse.ArgumentParser(
        prog='ocr-evaluation',
        description='OCR模型评估和对比框架',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用PaddleOCR评估图片
  ocr-evaluation evaluate paddleocr -i ./images -o ./reports

  # 对比两个模型
  ocr-evaluation compare paddleocr qwen_vl -i ./images

  # 显示配置
  ocr-evaluation config show

  # 生成默认配置文件
  ocr-evaluation config generate -o my_config.yaml

更多信息请访问: https://github.com/forayl/ocr-evaluation
        """
    )
    
    # 添加版本信息
    parser.add_argument(
        '--version',
        action='version',
        version='OCR Evaluation Framework v1.0.0'
    )
    
    # 创建子命令
    subparsers = parser.add_subparsers(
        dest='command',
        help='可用命令',
        metavar='COMMAND'
    )
    
    # 评估命令
    evaluate_parser = subparsers.add_parser(
        'evaluate',
        help='评估OCR模型',
        description='在指定数据集上评估单个OCR模型的性能'
    )
    EvaluateCommand.add_arguments(evaluate_parser)
    EvaluateCommand().add_common_arguments(evaluate_parser)
    
    # 对比命令
    compare_parser = subparsers.add_parser(
        'compare',
        help='对比多个OCR模型',
        description='在相同数据集上对比多个OCR模型的性能'
    )
    CompareCommand.add_arguments(compare_parser)
    CompareCommand().add_common_arguments(compare_parser)
    
    # 配置命令
    config_parser = subparsers.add_parser(
        'config',
        help='管理配置',
        description='查看、设置或生成配置文件'
    )
    ConfigCommand.add_arguments(config_parser)
    ConfigCommand().add_common_arguments(config_parser)
    
    # 添加全局参数
    parser.add_argument(
        '--project-root',
        type=Path,
        help='项目根目录路径'
    )
    
    return parser


def show_welcome():
    """显示欢迎信息"""
    print("🔍 OCR评估框架 v1.0.0")
    print("=" * 50)
    print()


def show_help_hint(parser: argparse.ArgumentParser):
    """显示帮助提示"""
    print("使用 --help 查看详细帮助信息")
    print()
    print("快速开始:")
    print("  ocr-evaluation evaluate paddleocr    # 评估PaddleOCR")
    print("  ocr-evaluation compare paddleocr qwen_vl  # 对比模型")
    print("  ocr-evaluation config show           # 查看配置")


def validate_project_structure(project_root: Path) -> bool:
    """验证项目结构"""
    required_dirs = ['data', 'data/images']
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            print(f"❌ 缺少必要目录: {dir_path}")
            return False
    
    return True


def setup_project_environment(project_root: Optional[Path] = None):
    """设置项目环境"""
    if project_root:
        # 验证项目结构
        if not validate_project_structure(project_root):
            print("❌ 项目结构不完整，请检查必要目录是否存在")
            return False
    
    # 创建必要目录
    try:
        from ..config import IMAGES_DIR, REPORTS_DIR, OUTPUTS_DIR
        
        for directory in [IMAGES_DIR, REPORTS_DIR, OUTPUTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        return True
    except Exception as e:
        print(f"❌ 创建项目目录失败: {e}")
        return False


def main(argv: Optional[List[str]] = None) -> int:
    """主入口函数
    
    Args:
        argv: 命令行参数列表，如果为None则使用sys.argv[1:]
        
    Returns:
        int: 退出码，0表示成功，非0表示失败
    """
    try:
        # 解析命令行参数
        parser = create_cli_parser()
        args = parser.parse_args(argv)
        
        # 显示欢迎信息
        show_welcome()
        
        # 检查是否指定了命令
        if not args.command:
            print("❌ 请指定要执行的命令")
            print()
            show_help_hint(parser)
            return 1
        
        # 设置项目环境
        if not setup_project_environment(args.project_root):
            return 1
        
        # 执行对应的命令
        if args.command == 'evaluate':
            command = EvaluateCommand()
            return command.run(args)
        
        elif args.command == 'compare':
            command = CompareCommand()
            return command.run(args)
        
        elif args.command == 'config':
            command = ConfigCommand()
            return command.run(args)
        
        else:
            print(f"❌ 未知命令: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        return 1
    
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        # 在调试模式下显示完整错误信息
        if '--verbose' in (argv or sys.argv):
            import traceback
            traceback.print_exc()
        return 1


def cli_entry():
    """CLI入口点，用于setuptools entry_points"""
    sys.exit(main())


if __name__ == '__main__':
    sys.exit(main())