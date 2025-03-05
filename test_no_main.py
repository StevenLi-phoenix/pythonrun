#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试没有main块的脚本
"""

import pandas as pd
from datetime import datetime

print(f"当前时间: {datetime.now()}")

# 创建一个简单的DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Age': [25, 30, 35, 40],
    'City': ['New York', 'Paris', 'London', 'Tokyo']
}

df = pd.DataFrame(data)
print("DataFrame:")
print(df)

# 简单的数据操作
print("\n年龄大于30的人:")
print(df[df['Age'] > 30]) 