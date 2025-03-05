#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版包名推荐功能
"""

# 导入一些拼写错误的包名
import nump as np  # numpy的拼写错误
import pands as pd  # pandas的拼写错误

# 如果导入成功会执行以下代码
try:
    # numpy功能
    arr = np.array([1, 2, 3, 4, 5])
    print(f"numpy数组: {arr}")
    
    # pandas功能
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    print(f"pandas数据框:\n{df}")
except Exception as e:
    print(f"执行出错: {e}")
    print("导入可能成功但模块接口不兼容") 