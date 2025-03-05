#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试拼写错误检测功能
"""

# 导入一些明显拼写错误的包名
import mathplotlib.pyplot as plt  # matplotlib的拼写错误
import scipi as sp  # scipy的拼写错误

# 如果导入成功会执行以下代码
try:
    # matplotlib功能
    x = [1, 2, 3, 4, 5]
    y = [10, 20, 30, 40, 50]
    plt.plot(x, y)
    plt.title("测试图表")
    plt.show()
    
    # scipy功能
    matrix = sp.array([[1, 2], [3, 4]])
    eigenvalues = sp.linalg.eigvals(matrix)
    print(f"特征值: {eigenvalues}")
except Exception as e:
    print(f"执行出错: {e}")
    print("导入可能成功但模块接口不兼容") 