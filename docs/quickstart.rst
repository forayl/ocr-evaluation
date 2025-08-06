快速开始
========

本指南将帮助您快速上手使用 OCR 评估框架。

基本使用
--------

1. **安装框架**

   .. code-block:: bash

      pip install ocr-evaluation

2. **准备配置文件**

   创建配置文件 `config.yaml`：

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
        
        - name: "qwen"
          type: "qwen"
          config:
            model_path: "path/to/qwen/model"

      # 评估指标
      metrics:
        - "accuracy"
        - "precision"
        - "recall"
        - "f1_score"

3. **运行评估**

   .. code-block:: bash

      ocr-evaluation run --config config.yaml

4. **查看结果**

   评估完成后，结果将保存在 `data/outputs` 目录中。

命令行界面
----------

框架提供了丰富的命令行选项：

.. code-block:: bash

   # 查看帮助
   ocr-evaluation --help

   # 运行评估
   ocr-evaluation run --config config.yaml

   # 生成报告
   ocr-evaluation report --output report.html

   # 查看版本
   ocr-evaluation --version

配置说明
--------

配置文件支持以下主要部分：

* **data**: 数据路径配置
* **evaluators**: OCR 评估器配置
* **metrics**: 评估指标配置
* **logging**: 日志配置

示例配置
--------

完整的配置文件示例：

.. code-block:: yaml

   # 数据配置
   data:
     images_dir: "data/images"
     ground_truth_file: "data/ground_truth.json"
     output_dir: "data/outputs"
     report_dir: "data/reports"

   # 评估器配置
   evaluators:
     - name: "paddleocr"
       type: "paddleocr"
       config:
         use_angle_cls: true
         lang: "ch"
         det_db_thresh: 0.3
         det_db_box_thresh: 0.5
         det_db_unclip_ratio: 1.6
         rec_char_dict_path: null
         rec_use_space_char: true
         use_gpu: false
     
     - name: "qwen"
       type: "qwen"
       config:
         model_path: "path/to/qwen/model"
         device: "cpu"
         max_length: 512

   # 评估指标
   metrics:
     - "accuracy"
     - "precision"
     - "recall"
     - "f1_score"
     - "edit_distance"
     - "character_accuracy"

   # 日志配置
   logging:
     level: "INFO"
     format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
     file: "logs/evaluation.log"

数据格式
--------

**图像数据**: 支持常见的图像格式（PNG、JPG、JPEG 等）

**标注数据**: JSON 格式，结构如下：

.. code-block:: json

   {
     "image1.jpg": {
       "text": "示例文本",
       "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
     },
     "image2.jpg": {
       "text": "另一个示例",
       "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
     }
   }

输出结果
--------

评估完成后，您将获得：

* **详细报告**: HTML 格式的评估报告
* **性能指标**: 各种评估指标的数值
* **错误分析**: 识别错误的详细分析
* **可视化图表**: 性能对比图表

下一步
------

* 查看 :doc:`api` 了解详细的 API 文档
* 阅读 :doc:`migration_guide` 了解版本迁移信息
* 查看 :doc:`changelog` 了解最新更新 