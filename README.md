# OCR评估框架 (OCR Evaluation Framework)

一个专业的OCR模型评估和对比框架，支持多种OCR系统和多模态大语言模型的准确率测试和性能分析。

## 🚀 核心特性

- **多模型支持**: 支持PaddleOCR、Qwen2.5-VL等多种OCR模型
- **专业评估**: 基于Levenshtein编辑距离的准确率计算
- **详细报告**: 自动生成包含技术细节的Markdown和JSON报告
- **可扩展架构**: 易于添加新的OCR模型支持
- **命令行界面**: 专业的CLI工具，支持批量评估和模型对比
- **配置管理**: 灵活的YAML/JSON配置系统
- **完整测试**: 包含单元测试和集成测试

## 📦 快速安装

### 基础安装
```bash
# 克隆项目
git clone https://github.com/forayl/ocr-evaluation.git
cd ocr-evaluation

# 安装基础依赖
pip install -r requirements/requirements-min.txt

# 或安装完整依赖
pip install -r requirements/requirements.txt
```

### 开发安装
```bash
# 安装为可编辑包
pip install -e .

# 安装所有可选依赖
pip install -e .[all,dev]
```

## 🎯 快速开始

### 1. 命令行使用

```bash
# 查看帮助
python scripts/run_evaluation.py --help

# 评估PaddleOCR模型
python scripts/run_evaluation.py evaluate paddleocr \
    --images-dir ./data/images \
    --output-dir ./data/reports

# 对比多个模型
python scripts/run_evaluation.py compare paddleocr qwen_vl \
    --images-dir ./data/images \
    --output-dir ./data/reports

# 查看配置
python scripts/run_evaluation.py config show

# 生成默认配置文件
python scripts/run_evaluation.py config generate -o my_config.yaml
```

### 2. Python API使用

```python
from ocr_evaluation import evaluate_model, generate_report

# 评估单个模型
summary = evaluate_model('paddleocr', './data/images')
print(f"准确率: {summary.overall_accuracy:.2%}")

# 生成报告
report_path = generate_report(summary, './reports')
print(f"报告已保存至: {report_path}")
```

## 📁 项目结构

```
ocr_evaluation/
├── src/ocr_evaluation/          # 源代码
│   ├── models/                  # 模型实现
│   │   ├── base.py             # 基础评估器抽象类
│   │   ├── paddleocr_evaluator.py  # PaddleOCR评估器
│   │   └── qwen_evaluator.py   # Qwen2.5-VL评估器
│   ├── utils/                   # 工具函数
│   │   ├── report_generator.py # 报告生成器
│   │   └── logging_utils.py    # 日志工具
│   ├── cli/                     # 命令行界面
│   │   ├── main.py             # CLI主入口
│   │   └── commands.py         # CLI命令实现
│   └── config/                  # 配置管理
│       ├── settings.py         # 配置管理器
│       └── constants.py        # 常量定义
├── tests/                       # 单元测试
├── docs/                        # 文档
├── scripts/                     # 实用脚本
├── data/                        # 数据目录
│   ├── images/                  # 测试图片
│   ├── outputs/                 # 处理输出
│   └── reports/                 # 生成的报告
├── requirements/                # 依赖文件
├── config.yaml                  # 默认配置文件
└── setup.py                     # 安装脚本
```

## 🔧 配置说明

### 创建配置文件
```bash
# 生成默认配置
python scripts/run_evaluation.py config generate -o my_config.yaml
```

### 配置示例
```yaml
# 模型配置
models:
  paddleocr:
    use_doc_orientation_classify: false
    use_doc_unwarping: false
    use_textline_orientation: false
    lang: 'en'
  
  qwen_vl:
    model_name: 'qwen/qwen2.5-vl-7b'
    lmstudio_url: 'ws://localhost:1234'
    temperature: 0.1

# 评估配置
evaluation:
  accuracy_threshold: 0.95
  use_levenshtein: true

# 输出配置  
output:
  reports_dir: 'data/reports'
  report_format: 'markdown'
```

## 🤖 支持的模型

### PP-OCRv5 (PaddleOCR)
- **类型**: 专业OCR模型
- **优势**: 识别准确率高，处理速度快
- **适用**: 纯文本识别任务
- **配置**: 支持多语言，可调节预处理参数

### Qwen2.5-VL-7B
- **类型**: 多模态大语言模型
- **优势**: 图像理解能力强，支持复杂推理
- **适用**: 需要上下文理解的复杂场景
- **配置**: 支持提示词工程，可调节生成参数

## 📊 评估指标

### 1. 完全匹配准确率
- 识别结果与标准答案完全相同的比例
- 计算公式：`完全匹配数量 / 总样本数`

### 2. 编辑距离准确率  
- 基于Levenshtein编辑距离的字符级相似度
- 计算公式：`1 - (编辑距离 / max(标准答案长度, 识别结果长度))`

### 3. 准确率分布
- 统计不同准确率区间的样本分布
- 区间：0.9-1.0, 0.8-0.9, 0.7-0.8, 0.6-0.7, <0.6

## 📈 使用示例

### 评估工业编号识别
```bash
# 数据格式：Label.txt
# image1.jpg	[{"transcription": "P4P601#03", "points": [...], "difficult": false}]

# 运行评估
python scripts/run_evaluation.py evaluate paddleocr \
    --images-dir ./industrial_codes \
    --output-dir ./reports \
    --model-config '{"lang": "en", "use_gpu": false}'
```

### 对比不同模型性能
```bash
python scripts/run_evaluation.py compare paddleocr qwen_vl \
    --images-dir ./test_dataset \
    --comparison-report model_comparison_2024
```

## 🧪 运行测试

```bash
# 运行所有测试
python tests/run_tests.py

# 运行特定测试
python -m pytest tests/test_config.py -v

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=src/ocr_evaluation --cov-report=html
```

## 📋 数据格式

### 标签文件格式 (Label.txt)
```
图片路径	[{"transcription": "识别文本", "points": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], "difficult": false}]
```

### 支持的图片格式
- JPG/JPEG
- PNG
- BMP
- TIFF
- WebP

## 🔍 故障排除

### 常见问题

1. **PaddleOCR识别效果差**
   - 检查模型配置，特别是预处理参数
   - 尝试不同的语言模型设置

2. **LMStudio连接失败**
   - 确保LMStudio服务正在运行
   - 检查模型是否正确加载
   - 验证WebSocket连接地址

3. **内存不足**
   - 减少批处理大小
   - 关闭其他占用内存的程序
   - 考虑使用更小的模型

### 调试模式
```bash
# 启用详细日志
python scripts/run_evaluation.py evaluate paddleocr --verbose

# 使用自定义日志级别
python scripts/run_evaluation.py evaluate paddleocr --log-level DEBUG
```

## 🚀 部署说明

### 生产环境部署
1. 安装生产依赖
2. 配置环境变量
3. 设置定时任务
4. 配置监控和日志

### Docker部署
```dockerfile
# Dockerfile示例
FROM python:3.9-slim

WORKDIR /app
COPY requirements/ ./requirements/
RUN pip install -r requirements/requirements.txt

COPY src/ ./src/
COPY config.yaml ./
COPY scripts/ ./scripts/

CMD ["python", "scripts/run_evaluation.py", "evaluate", "paddleocr"]
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发环境设置
```bash
# 安装开发依赖
pip install -e .[dev]

# 安装pre-commit钩子
pre-commit install

# 运行代码检查
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持与联系

- **文档**: [在线文档](https://ocr-evaluation.readthedocs.io/)
- **问题反馈**: [GitHub Issues](https://github.com/forayl/ocr-evaluation/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/forayl/ocr-evaluation/discussions)
- **邮件联系**: ray.pf.lau@gmail.com

## 🎯 路线图

- [ ] 支持更多OCR模型 (EasyOCR, TrOCR等)
- [ ] Web界面和API服务
- [ ] 批量处理和并发优化
- [ ] 模型性能基准测试
- [ ] 可视化分析工具
- [ ] 云端部署支持

---

**⭐ 如果这个项目对你有帮助，请给我们一个Star!**