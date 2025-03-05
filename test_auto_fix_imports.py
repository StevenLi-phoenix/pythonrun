"""
测试自动修复导入语句的功能
"""
import mathplotlib.pyplot as plt
import scipy as sp
try:
    x = sp.linspace(0, 10, 100)
    y = sp.sin(x)
    plt.figure(figsize=(8, 4))
    plt.plot(x, y)
    plt.title('正弦波')
    plt.xlabel('x')
    plt.ylabel('sin(x)')
    plt.grid(True)
    plt.savefig('sine_wave.png')
    plt.close()
    print('成功创建了正弦波图表并保存为 sine_wave.png')
except Exception as e:
    print(f'执行出错: {e}')
