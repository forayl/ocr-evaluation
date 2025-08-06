安装指南
========

本文档将指导您如何安装 OCR 评估框架。

系统要求
--------

* Python 3.8 或更高版本
* 操作系统：Windows、macOS 或 Linux

从 PyPI 安装
-----------

最简单的安装方式是通过 PyPI：

.. code-block:: bash

   pip install ocr-evaluation

安装特定版本：

.. code-block:: bash

   pip install ocr-evaluation==1.0.0

从源码安装
---------

如果您想从源码安装最新版本：

.. code-block:: bash

   git clone https://github.com/forayl/ocr-evaluation.git
   cd ocr-evaluation
   pip install -e .

安装可选依赖
-----------

安装所有依赖（包括开发工具）：

.. code-block:: bash

   pip install ocr-evaluation[all]

安装特定引擎支持：

.. code-block:: bash

   # PaddleOCR 支持
   pip install ocr-evaluation[paddleocr]

   # Qwen 支持
   pip install ocr-evaluation[qwen]

安装开发依赖：

.. code-block:: bash

   pip install ocr-evaluation[dev]

安装文档生成工具：

.. code-block:: bash

   pip install ocr-evaluation[docs]

验证安装
--------

安装完成后，您可以通过以下命令验证安装：

.. code-block:: bash

   ocr-evaluation --version

如果安装成功，您应该看到版本信息。

故障排除
--------

常见问题：

1. **权限错误**: 使用 `pip install --user` 或虚拟环境
2. **依赖冲突**: 建议使用虚拟环境
3. **编译错误**: 确保安装了开发工具

使用虚拟环境（推荐）：

.. code-block:: bash

   python -m venv ocr_env
   source ocr_env/bin/activate  # Linux/macOS
   # 或
   ocr_env\Scripts\activate     # Windows
   pip install ocr-evaluation 