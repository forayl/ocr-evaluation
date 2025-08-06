# 从旧版本迁移到新框架

本文档介绍如何从原始的单独脚本迁移到新的专业OCR评估框架。

## 🔄 迁移概述

新框架将原来的独立脚本重构为一个专业的、可扩展的评估系统：

```
原始结构                           新框架结构
├── ocr_accuracy_test.py          ├── src/ocr_evaluation/
├── lmstudio_qwen_accuracy_test.py │   ├── models/
├── run_qwen_test.py               │   │   ├── paddleocr_evaluator.py
├── test_lmstudio_connection.py    │   │   └── qwen_evaluator.py
└── images/                        │   ├── cli/
                                   │   └── utils/
                                   └── scripts/run_evaluation.py
```

## 📋 迁移步骤

### 1. 代码迁移

#### 旧的PaddleOCR脚本
```python
# 旧版本 ocr_accuracy_test.py
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_doc_orientation_classify=False, ...)
result = ocr.ocr(image_path)
```

#### 新框架使用
```python
# 新框架
from ocr_evaluation import evaluate_model
summary = evaluate_model('paddleocr', './images')
```

#### 旧的Qwen脚本
```python
# 旧版本 lmstudio_qwen_accuracy_test.py
import lmstudio as lms
model = lms.llm("qwen/qwen2.5-vl-7b")
result = model.respond(chat)
```

#### 新框架使用
```python
# 新框架
from ocr_evaluation import evaluate_model
summary = evaluate_model('qwen_vl', './images')
```

### 2. 配置迁移

#### 旧版本的硬编码配置
```python
# 旧版本
ocr_model = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang='en'
)
```

#### 新框架配置文件
```yaml
# config.yaml
models:
  paddleocr:
    use_doc_orientation_classify: false
    use_doc_unwarping: false
    use_textline_orientation: false
    lang: 'en'
```

### 3. 报告格式迁移

#### 旧版本手动生成报告
```python
# 旧版本
report = []
report.append(f"# {model_name} 准确率报告")
report.append(f"总体准确率: {accuracy:.4f}")
with open(report_file, 'w') as f:
    f.write('\n'.join(report))
```

#### 新框架自动报告生成
```python
# 新框架
from ocr_evaluation.utils import ReportGenerator
generator = ReportGenerator('./reports')
generator.save_markdown_report(summary)
```

## 🔧 功能对照表

| 旧功能 | 新框架对应功能 | 优势 |
|--------|---------------|------|
| `ocr_accuracy_test.py` | `PaddleOCREvaluator` | 配置化、可扩展 |
| `lmstudio_qwen_accuracy_test.py` | `QwenVLEvaluator` | 统一接口、错误处理 |
| 手动报告生成 | `ReportGenerator` | 模板化、格式统一 |
| 硬编码配置 | YAML配置文件 | 灵活、可版本控制 |
| 独立脚本 | CLI命令 | 专业、易用 |

## 📊 数据格式兼容性

### Label.txt格式
新框架完全兼容原有的Label.txt格式：
```
image.jpg	[{"transcription": "text", "points": [...], "difficult": false}]
```

### 目录结构
新框架支持原有的目录结构：
```
images/
├── data/
│   ├── Label.txt
│   └── *.jpg
└── ocr (2)/
    ├── lotid/
    │   ├── Label.txt
    │   └── *.jpg
    └── waferid/
        ├── Label.txt
        └── *.jpg
```

## 🚀 迁移示例

### 原始PaddleOCR评估
```bash
# 旧版本
python ocr_accuracy_test.py
```

### 新框架等效命令
```bash
# 新框架
python scripts/run_evaluation.py evaluate paddleocr \
    --images-dir ./images \
    --output-dir ./reports
```

### 原始Qwen评估
```bash
# 旧版本
python run_qwen_test.py
```

### 新框架等效命令
```bash
# 新框架
python scripts/run_evaluation.py evaluate qwen_vl \
    --images-dir ./images \
    --output-dir ./reports
```

## 🔍 配置迁移工具

### 自动生成配置文件
```bash
# 基于当前设置生成配置
python scripts/run_evaluation.py config generate -o migrated_config.yaml
```

### 验证配置
```bash
# 查看当前配置
python scripts/run_evaluation.py config show
```

## ⚠️ 注意事项

### 1. 依赖项变化
- 新框架使用模块化依赖安装
- 可以选择只安装需要的模型支持

### 2. 输出格式变化
- 报告格式更加标准化
- 包含更多技术细节
- 支持JSON和Markdown双格式

### 3. 错误处理改进
- 更完善的异常处理
- 详细的错误日志
- 优雅的错误恢复

## 🧪 迁移验证

### 1. 功能验证
```bash
# 运行相同数据集测试
python scripts/run_evaluation.py evaluate paddleocr -i ./images
# 对比结果与原始脚本输出
```

### 2. 性能验证
```bash
# 对比处理时间和内存使用
python scripts/run_evaluation.py evaluate paddleocr --verbose
```

### 3. 准确率验证
```bash
# 确保评估结果一致
python scripts/run_evaluation.py compare paddleocr qwen_vl
```

## 💡 最佳实践

### 1. 渐进式迁移
- 先迁移配置文件
- 再迁移评估逻辑
- 最后整合报告生成

### 2. 保留原始备份
- 保留原始脚本作为备份
- 对比新旧结果确保一致性
- 逐步删除旧代码

### 3. 利用新特性
- 使用配置文件管理参数
- 采用专业CLI界面
- 利用模型对比功能

## 🆘 迁移支持

如果在迁移过程中遇到问题：

1. **查看文档**: 详细阅读新框架文档
2. **运行测试**: 使用测试数据验证功能
3. **对比输出**: 确保结果与原始脚本一致
4. **提交issue**: 在GitHub上报告问题

## 📈 迁移后的优势

1. **更好的维护性**: 模块化架构，易于扩展
2. **专业的界面**: 统一的CLI命令
3. **配置管理**: 灵活的配置系统
4. **错误处理**: 完善的异常处理机制
5. **测试支持**: 完整的单元测试
6. **文档齐全**: 详细的使用文档

---

迁移完成后，你将拥有一个更加专业、可维护和可扩展的OCR评估系统！