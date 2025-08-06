#!/usr/bin/env python3
"""
文档构建脚本
用于自动化生成项目文档
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✓ 命令执行成功: {cmd}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ 命令执行失败: {cmd}")
        print(f"错误输出: {e.stderr}")
        return None

def build_docs(docs_dir, output_format="html"):
    """构建文档"""
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        print(f"✗ 文档目录不存在: {docs_dir}")
        return False
    
    # 切换到文档目录
    os.chdir(docs_path)
    
    # 清理之前的构建
    print("清理之前的构建...")
    run_command("make clean")
    
    # 构建文档
    print(f"构建 {output_format} 格式的文档...")
    if output_format == "html":
        result = run_command("make html")
    elif output_format == "pdf":
        result = run_command("make pdf")
    elif output_format == "epub":
        result = run_command("make epub")
    else:
        print(f"✗ 不支持的输出格式: {output_format}")
        return False
    
    if result is not None:
        print(f"✓ 文档构建成功！")
        print(f"输出目录: {docs_path / '_build' / output_format}")
        return True
    else:
        print("✗ 文档构建失败！")
        return False

def install_docs_dependencies():
    """安装文档构建依赖"""
    print("安装文档构建依赖...")
    
    # 安装项目依赖
    result = run_command("pip install -e .[docs]")
    if result is None:
        return False
    
    # 安装文档专用依赖
    docs_req_file = Path("requirements/requirements-docs.txt")
    if docs_req_file.exists():
        result = run_command(f"pip install -r {docs_req_file}")
        if result is None:
            return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="构建项目文档")
    parser.add_argument(
        "--format", 
        choices=["html", "pdf", "epub"], 
        default="html",
        help="输出格式 (默认: html)"
    )
    parser.add_argument(
        "--docs-dir", 
        default="docs",
        help="文档目录 (默认: docs)"
    )
    parser.add_argument(
        "--install-deps", 
        action="store_true",
        help="安装文档构建依赖"
    )
    parser.add_argument(
        "--serve", 
        action="store_true",
        help="构建完成后启动本地服务器"
    )
    
    args = parser.parse_args()
    
    # 安装依赖
    if args.install_deps:
        if not install_docs_dependencies():
            sys.exit(1)
    
    # 构建文档
    if not build_docs(args.docs_dir, args.format):
        sys.exit(1)
    
    # 启动本地服务器
    if args.serve and args.format == "html":
        print("启动本地文档服务器...")
        docs_path = Path(args.docs_dir)
        build_path = docs_path / "_build" / "html"
        if build_path.exists():
            print(f"文档服务器启动在: http://localhost:8000")
            print("按 Ctrl+C 停止服务器")
            try:
                subprocess.run(
                    ["python", "-m", "http.server", "8000"], 
                    cwd=build_path
                )
            except KeyboardInterrupt:
                print("\n服务器已停止")
        else:
            print("✗ HTML 构建目录不存在")

if __name__ == "__main__":
    main() 