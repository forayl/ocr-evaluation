#!/usr/bin/env python3
"""
数据迁移脚本 - 将原有数据迁移到新框架结构
"""

import sys
import shutil
from pathlib import Path
import argparse

def setup_project_path():
    """设置项目路径"""
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

def migrate_data(source_dir: Path, target_dir: Path, dry_run: bool = False):
    """迁移数据到新结构
    
    Args:
        source_dir: 原始数据目录
        target_dir: 目标数据目录
        dry_run: 是否仅预览而不实际执行
    """
    print(f"🔄 数据迁移")
    print(f"源目录: {source_dir}")
    print(f"目标目录: {target_dir}")
    print(f"模式: {'预览模式' if dry_run else '执行模式'}")
    print("-" * 50)
    
    if not source_dir.exists():
        print(f"❌ 源目录不存在: {source_dir}")
        return False
    
    # 创建目标目录结构
    target_images = target_dir / "data" / "images"
    target_reports = target_dir / "data" / "reports"
    target_outputs = target_dir / "data" / "outputs"
    
    if not dry_run:
        target_images.mkdir(parents=True, exist_ok=True)
        target_reports.mkdir(parents=True, exist_ok=True)
        target_outputs.mkdir(parents=True, exist_ok=True)
    
    # 迁移图片数据
    images_source = source_dir / "images"
    if images_source.exists():
        print("📁 迁移图片数据...")
        
        for item in images_source.iterdir():
            if item.is_dir():
                target_path = target_images / item.name
                print(f"  📂 {item.name} -> {target_path}")
                
                if not dry_run:
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(item, target_path)
                
                # 检查Label.txt文件
                label_file = item / "Label.txt"
                if label_file.exists():
                    print(f"    ✅ 找到标签文件: {label_file}")
                else:
                    print(f"    ⚠️  缺少标签文件: {label_file}")
    
    # 迁移现有报告
    reports_to_migrate = [
        "PP-OCRv5_准确率报告.md",
        "Qwen2.5-VL-7B_准确率报告.md", 
        "Qwen2.5-VL-7B_示例报告.md"
    ]
    
    print("\n📊 迁移现有报告...")
    for report_name in reports_to_migrate:
        source_report = source_dir / report_name
        if source_report.exists():
            target_report = target_reports / report_name
            print(f"  📄 {report_name} -> {target_report}")
            
            if not dry_run:
                shutil.copy2(source_report, target_report)
        else:
            print(f"  ❓ 报告不存在: {report_name}")
    
    # 迁移结果文件
    results_to_migrate = [
        "ocr_results.json",
        "qwen_results.json"
    ]
    
    print("\n📈 迁移结果文件...")
    for result_name in results_to_migrate:
        source_result = source_dir / result_name
        if source_result.exists():
            target_result = target_outputs / result_name
            print(f"  📈 {result_name} -> {target_result}")
            
            if not dry_run:
                shutil.copy2(source_result, target_result)
        else:
            print(f"  ❓ 结果文件不存在: {result_name}")
    
    # 迁移输出目录
    output_source = source_dir / "output"
    if output_source.exists():
        print("\n📤 迁移输出文件...")
        
        for output_file in output_source.glob("*.json"):
            target_file = target_outputs / output_file.name
            print(f"  📤 {output_file.name} -> {target_file}")
            
            if not dry_run:
                shutil.copy2(output_file, target_file)
    
    # 保留原有脚本作为备份
    backup_dir = target_dir / "legacy_scripts"
    scripts_to_backup = [
        "ocr_accuracy_test.py",
        "lmstudio_qwen_accuracy_test.py",
        "run_qwen_test.py",
        "test_lmstudio_connection.py",
        "test.py"
    ]
    
    print("\n💾 备份原有脚本...")
    if not dry_run:
        backup_dir.mkdir(exist_ok=True)
    
    for script_name in scripts_to_backup:
        source_script = source_dir / script_name
        if source_script.exists():
            target_script = backup_dir / script_name
            print(f"  💾 {script_name} -> {target_script}")
            
            if not dry_run:
                shutil.copy2(source_script, target_script)
    
    # 创建迁移配置文件
    print("\n⚙️  生成迁移配置...")
    migration_config = target_dir / "migration_config.yaml"
    
    if not dry_run:
        config_content = f"""# 迁移配置 - 基于原有设置自动生成
# 迁移时间: {Path(__file__).stat().st_mtime}

models:
  paddleocr:
    # 基于原有 ocr_accuracy_test.py 的最佳配置
    use_doc_orientation_classify: false
    use_doc_unwarping: false
    use_textline_orientation: false
    lang: 'en'
    use_gpu: false
  
  qwen_vl:
    # 基于原有 lmstudio_qwen_accuracy_test.py 的配置
    model_name: 'qwen/qwen2.5-vl-7b'
    lmstudio_url: 'ws://localhost:1234'
    temperature: 0.1
    max_tokens: 50

evaluation:
  accuracy_threshold: 0.95
  use_levenshtein: true
  case_sensitive: true

logging:
  level: 'INFO'
  format: '%(asctime)s - %(levelname)s - %(message)s'

output:
  reports_dir: 'data/reports'
  results_dir: 'data/outputs'
  report_format: 'markdown'

# 迁移记录
migration:
  source_directory: '{source_dir}'
  migration_date: '{Path(__file__).stat().st_mtime}'
  original_scripts_backed_up: true
  data_preserved: true
"""
        
        with open(migration_config, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"  ⚙️  配置文件已生成: {migration_config}")
    
    print(f"\n{'🎯 迁移预览完成!' if dry_run else '✅ 迁移完成!'}")
    
    if not dry_run:
        print("\n📋 下一步操作:")
        print("1. 检查迁移的数据是否完整")
        print("2. 使用新框架运行测试验证")
        print("3. 对比新旧结果确保一致性")
        print("4. 更新文档和配置")
        
        print(f"\n🔧 验证命令:")
        print(f"cd {target_dir}")
        print("python scripts/run_evaluation.py config show")
        print("python scripts/run_evaluation.py evaluate paddleocr --images-dir data/images")
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='迁移原有数据到新框架结构')
    parser.add_argument(
        'source_dir',
        type=Path,
        help='原始项目目录路径'
    )
    parser.add_argument(
        '--target-dir', '-t',
        type=Path,
        default=Path(__file__).parent.parent,
        help='目标框架目录路径 (默认: 当前框架目录)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式，不实际执行迁移'
    )
    
    args = parser.parse_args()
    
    # 设置项目路径
    setup_project_path()
    
    # 执行迁移
    success = migrate_data(args.source_dir, args.target_dir, args.dry_run)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()