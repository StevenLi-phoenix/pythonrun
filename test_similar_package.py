#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试类似包名搜索功能
"""

# 引用一个拼写不完全的numpy
import nump

# 如果成功导入会执行以下代码
try:
    data = nump.random.rand(5)
    print(f"随机数组: {data}")
except Exception as e:
    print(f"执行出错: {e}")
    print("导入可能成功但模块接口不兼容") 