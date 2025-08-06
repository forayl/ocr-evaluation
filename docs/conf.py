# -*- coding: utf-8 -*-
"""
Sphinx 配置文件
用于生成 OCR 评估框架的文档
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# 项目信息
project = "OCR Evaluation Framework"
copyright = "2024, Ray"
author = "Ray"

# 版本信息
try:
    from ocr_evaluation import __version__
    version = __version__
    release = __version__
except ImportError:
    version = "1.0.0"
    release = "1.0.0"

# 扩展配置
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx_rtd_theme",
]

# 模板配置
templates_path = ["_templates"]

# 源文件后缀
source_suffix = {
    ".rst": "restructuredtext",
}

# 主文档
master_doc = "index"

# 语言设置
language = "zh_CN"

# 排除的文件和目录
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# 主题设置
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "titles_only": False,
    "collapse_navigation": False,
}

# 静态文件路径
html_static_path = ["_static"]

# HTML 输出选项
htmlhelp_basename = "OCREvaluationFrameworkdoc"

# LaTeX 输出选项
latex_elements = {
    "papersize": "a4paper",
    "pointsize": "12pt",
    "preamble": "",
    "figure_align": "htbp",
}

latex_documents = [
    (master_doc, "OCREvaluationFramework.tex", "OCR Evaluation Framework Documentation", author, "manual"),
]

# 手册页输出
man_pages = [
    (master_doc, "ocrevaluationframework", "OCR Evaluation Framework Documentation", [author], 1)
]

# Texinfo 输出
texinfo_documents = [
    (master_doc, "OCREvaluationFramework", "OCR Evaluation Framework Documentation", author, "OCREvaluationFramework", "专业的OCR模型评估和对比框架", "Miscellaneous"),
]

# Epub 输出
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# 扩展配置
todo_include_todos = True

# 自动文档配置
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Napoleon 配置
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_custom_sections = None

# Intersphinx 映射
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
} 