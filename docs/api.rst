API 文档
========

本文档介绍 OCR 评估框架的 API 接口。

核心模块
--------

.. automodule:: ocr_evaluation
   :members:
   :undoc-members:
   :show-inheritance:

配置模块
--------

.. automodule:: ocr_evaluation.config
   :members:
   :undoc-members:
   :show-inheritance:

设置模块
--------

.. automodule:: ocr_evaluation.config.settings
   :members:
   :undoc-members:
   :show-inheritance:

常量模块
--------

.. automodule:: ocr_evaluation.config.constants
   :members:
   :undoc-members:
   :show-inheritance:

模型模块
--------

基础评估器
----------

.. automodule:: ocr_evaluation.models.base
   :members:
   :undoc-members:
   :show-inheritance:

PaddleOCR 评估器
----------------

.. automodule:: ocr_evaluation.models.paddleocr_evaluator
   :members:
   :undoc-members:
   :show-inheritance:

Qwen 评估器
----------

.. automodule:: ocr_evaluation.models.qwen_evaluator
   :members:
   :undoc-members:
   :show-inheritance:

工具模块
--------

日志工具
--------

.. automodule:: ocr_evaluation.utils.logging_utils
   :members:
   :undoc-members:
   :show-inheritance:

报告生成器
----------

.. automodule:: ocr_evaluation.utils.report_generator
   :members:
   :undoc-members:
   :show-inheritance:

命令行接口
----------

主程序
------

.. automodule:: ocr_evaluation.cli.main
   :members:
   :undoc-members:
   :show-inheritance:

命令模块
--------

.. automodule:: ocr_evaluation.cli.commands
   :members:
   :undoc-members:
   :show-inheritance:

使用示例
--------

基本使用
--------

.. code-block:: python

   from ocr_evaluation import OCREvaluator
   from ocr_evaluation.config.settings import Settings

   # 加载配置
   settings = Settings.from_yaml("config.yaml")

   # 创建评估器
   evaluator = OCREvaluator(settings)

   # 运行评估
   results = evaluator.evaluate()

   # 生成报告
   evaluator.generate_report(results)

自定义评估器
-----------

.. code-block:: python

   from ocr_evaluation.models.base import BaseEvaluator

   class CustomEvaluator(BaseEvaluator):
       def __init__(self, config):
           super().__init__(config)
           # 初始化自定义模型
       
       def recognize_text(self, image_path):
           # 实现文本识别逻辑
           return recognized_text
       
       def evaluate_single(self, image_path, ground_truth):
           # 实现单张图片评估逻辑
           return evaluation_result

配置管理
--------

.. code-block:: python

   from ocr_evaluation.config.settings import Settings

   # 从文件加载配置
   settings = Settings.from_yaml("config.yaml")

   # 从字典创建配置
   config_dict = {
       "data": {
           "images_dir": "data/images",
           "ground_truth_file": "data/ground_truth.json"
       },
       "evaluators": [
           {
               "name": "paddleocr",
               "type": "paddleocr",
               "config": {"lang": "ch"}
           }
       ]
   }
   settings = Settings.from_dict(config_dict)

   # 保存配置
   settings.save_yaml("new_config.yaml")

日志配置
--------

.. code-block:: python

   from ocr_evaluation.utils.logging_utils import setup_logging

   # 设置日志
   logger = setup_logging(
       level="INFO",
       log_file="evaluation.log",
       format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
   )

   # 使用日志
   logger.info("开始评估")
   logger.error("评估失败")

报告生成
--------

.. code-block:: python

   from ocr_evaluation.utils.report_generator import ReportGenerator

   # 创建报告生成器
   generator = ReportGenerator()

   # 生成 HTML 报告
   generator.generate_html_report(results, "report.html")

   # 生成 JSON 报告
   generator.generate_json_report(results, "report.json")

   # 生成 CSV 报告
   generator.generate_csv_report(results, "report.csv") 