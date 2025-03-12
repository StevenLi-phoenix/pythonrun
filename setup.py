#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的setup.py文件，主要配置已移至pyproject.toml
保留此文件是为了向后兼容
"""

import os
import sys
from setuptools import setup

# 检测是否在PyPI上传环境中
is_pypi_upload = any(arg.startswith('upload') or arg.startswith('bdist') or arg.startswith('sdist') for arg in sys.argv)

if is_pypi_upload:
    # 上传到PyPI时使用固定版本号
    setup(
        version="1.1.4",  # 与pyproject.toml中的版本保持一致
    )
else:
    # 开发环境使用setuptools_scm
    setup(
        use_scm_version=True,
    ) 