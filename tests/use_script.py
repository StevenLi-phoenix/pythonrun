#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试autopython功能的脚本
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

print(f"当前时间: {datetime.now()}")
print(f"Numpy版本: {np.__version__}")

data = np.random.rand(50)
print(f"随机数据: {data[:5]}...")

# 只有在交互环境中才显示图表
if '__file__' in globals():
    plt.figure(figsize=(8, 4))
    plt.plot(data)
    plt.title('Random Data Generated with NumPy')
    plt.savefig('test_plot.png')
    print("图表已保存为 test_plot.png")

def main():
    print("测试函数被调用")
    return np.mean(data)

if __name__ == "__main__":
    print("在main块中执行")
    result = main()
    print(f"数据平均值: {result}") 