#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的setup.py文件，主要配置已移至pyproject.toml
保留此文件是为了向后兼容
"""

from setuptools import setup

setup(
    use_scm_version=True,
) 