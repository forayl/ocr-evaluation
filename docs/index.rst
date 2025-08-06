OCR 评估框架文档
==================

欢迎使用 OCR 评估框架！这是一个专业的 OCR 模型评估和对比框架，支持多种 OCR 引擎的性能评估。

.. toctree::
   :maxdepth: 2
   :caption: 目录:

   installation
   quickstart
   api
   migration_guide
   changelog

索引和表格
----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

项目概述
--------

OCR 评估框架是一个用于评估和对比不同 OCR 模型性能的工具。它提供了：

* 多种 OCR 引擎支持（PaddleOCR、Qwen 等）
* 标准化的评估指标
* 详细的性能报告
* 易于使用的命令行界面
* 可扩展的评估框架

主要特性
--------

* **多引擎支持**: 支持 PaddleOCR、Qwen 等多种 OCR 引擎
* **标准化评估**: 提供统一的评估指标和流程
* **详细报告**: 生成详细的性能分析报告
* **易于使用**: 简单的命令行界面
* **可扩展性**: 支持自定义评估器和指标

快速开始
--------

安装框架：

.. code-block:: bash

   pip install ocr-evaluation

运行评估：

.. code-block:: bash

   ocr-evaluation run --config config.yaml

更多信息请查看 :doc:`quickstart` 章节。 