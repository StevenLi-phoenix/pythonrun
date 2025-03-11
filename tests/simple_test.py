#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
"""

import os
import sys

print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"命令行参数: {sys.argv}")

# 尝试导入一个可能不存在的模块
try:
    import nonexistent_module
    print("成功导入nonexistent_module")
except ImportError:
    print("无法导入nonexistent_module") 