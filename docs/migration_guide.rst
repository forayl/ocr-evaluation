迁移指南
========

本文档帮助您在不同版本之间迁移 OCR 评估框架。

版本 1.0.0
----------

这是初始版本，没有迁移要求。

### 新功能

* 支持 PaddleOCR 引擎评估
* 支持 Qwen 多模态模型评估
* 提供标准化的评估指标
* 命令行界面支持
* 配置文件管理
* 详细的评估报告生成

### 配置格式

配置文件使用 YAML 格式，基本结构如下：

.. code-block:: yaml

   # 数据配置
   data:
     images_dir: "data/images"
     ground_truth_file: "data/ground_truth.json"
     output_dir: "data/outputs"

   # 评估器配置
   evaluators:
     - name: "paddleocr"
       type: "paddleocr"
       config:
         use_angle_cls: true
         lang: "ch"

   # 评估指标
   metrics:
     - "accuracy"
     - "precision"
     - "recall"
     - "f1_score"

### API 变更

暂无 API 变更，这是初始版本。

### 依赖变更

主要依赖：

* Python 3.8+
* PyYAML >= 6.0
* numpy >= 1.20.0
* Pillow >= 8.0.0

可选依赖：

* paddlepaddle >= 2.4.0 (PaddleOCR 支持)
* paddleocr >= 2.6.0 (PaddleOCR 支持)
* lmstudio >= 1.0.0 (Qwen 支持)

### 升级步骤

1. 备份现有配置和数据
2. 安装新版本
3. 更新配置文件（如果需要）
4. 测试功能

### 已知问题

暂无已知问题。

### 支持

如果您在迁移过程中遇到问题：

* 查看文档：本文档
* 搜索问题：GitHub Issues
* 提交问题：创建新的 Issue
* 联系维护者：ray.pf.lau@gmail.com 