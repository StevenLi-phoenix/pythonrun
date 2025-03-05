#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试拼写错误包名的脚本
"""

# 拼写错误的numpy（正确应为numpy）
import numpie as np

# 如果导入成功会执行以下代码
try:
    data = np.random.rand(5)
    print(f"随机数组: {data}")
except Exception as e:
    print(f"执行出错: {e}")
    print("导入可能成功但模块接口不兼容") 