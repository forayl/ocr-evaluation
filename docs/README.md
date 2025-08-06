# OCR 评估框架文档

本目录包含 OCR 评估框架的完整文档。

## 文档结构

```
docs/
├── conf.py              # Sphinx 配置文件
├── index.rst            # 文档主页
├── installation.rst     # 安装指南
├── quickstart.rst       # 快速开始
├── api.rst             # API 文档
├── migration_guide.rst  # 迁移指南
├── changelog.rst       # 变更日志
├── Makefile            # 构建脚本
└── README.md           # 本文档
```

## 构建文档

### 方法一：使用 Makefile

```bash
# 进入文档目录
cd docs

# 构建 HTML 文档
make html

# 构建 PDF 文档
make pdf

# 构建 EPUB 文档
make epub

# 清理构建文件
make clean

# 启动本地服务器查看文档
make serve
```

### 方法二：使用构建脚本

```bash
# 安装依赖并构建 HTML 文档
python scripts/build_docs.py --install-deps --format html

# 构建 PDF 文档
python scripts/build_docs.py --format pdf

# 构建并启动本地服务器
python scripts/build_docs.py --format html --serve
```

### 方法三：使用 Sphinx 命令

```bash
# 进入文档目录
cd docs

# 构建 HTML 文档
sphinx-build -b html . _build/html

# 构建 PDF 文档
sphinx-build -b latex . _build/latex
cd _build/latex && make all-pdf
```

## 安装依赖

### 安装文档构建依赖

```bash
# 安装项目依赖（包括文档工具）
pip install -e .[docs]

# 安装文档专用依赖
pip install -r requirements/requirements-docs.txt
```

### 主要依赖

- Sphinx >= 4.0.0
- sphinx-rtd-theme >= 1.0.0
- sphinx-autodoc-typehints >= 1.12.0
- myst-parser >= 0.18.0

## 文档格式

### RST 格式

文档主要使用 reStructuredText (RST) 格式编写，这是 Sphinx 的标准格式。

### Markdown 支持

项目也支持 Markdown 格式，通过 `myst-parser` 扩展实现。

## 自定义文档

### 添加新页面

1. 创建新的 `.rst` 文件
2. 在 `index.rst` 的 `toctree` 中添加引用
3. 重新构建文档

### 修改主题

在 `conf.py` 中修改 `html_theme_options` 来自定义主题。

### 添加扩展

在 `conf.py` 的 `extensions` 列表中添加新的 Sphinx 扩展。

## 部署到 Read the Docs

项目已配置 `.readthedocs.yaml` 文件，支持自动部署到 Read the Docs。

### 本地测试

```bash
# 构建文档
make html

# 检查构建结果
open _build/html/index.html
```

### 常见问题

1. **构建失败**: 检查是否安装了所有依赖
2. **导入错误**: 确保项目路径正确配置
3. **主题问题**: 检查 `sphinx-rtd-theme` 是否正确安装

## 贡献文档

欢迎贡献文档改进！

1. Fork 项目
2. 创建功能分支
3. 修改文档
4. 测试构建
5. 提交 Pull Request

## 更多信息

- [Sphinx 文档](https://www.sphinx-doc.org/)
- [Read the Docs 文档](https://docs.readthedocs.io/)
- [reStructuredText 语法](https://docutils.sourceforge.io/rst.html) 