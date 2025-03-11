# pythonrun (autopython)

自动导入和安装Python模块的工具，让你的Python脚本运行更加顺畅。

[![PyPI version](https://badge.fury.io/py/pythonrun.svg)](https://badge.fury.io/py/pythonrun)
[![Python Versions](https://img.shields.io/pypi/pyversions/pythonrun.svg)](https://pypi.org/project/pythonrun/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 功能特点

- 自动检测Python脚本中导入的模块
- 自动安装缺少的依赖包
- 智能处理本地模块和标准库
- 支持递归检测导入
- 处理 `if __name__ == "__main__"` 的情况
- 支持命令行参数传递
- 安装失败时搜索相关包并提供安装建议

## 安装

### 从PyPI安装（推荐）

```bash
pip install pythonrun
```

### 从源码安装

```bash
git clone https://github.com/StevenLi-phoenix/pythonrun.git
cd pythonrun
pip install -e .
```

## 使用方法

```bash
autopython your_script.py [arg1 arg2 ...]
```

### 配置选项

你可以通过配置文件自定义autopython的行为：

- `auto_install_all`: 自动安装所有缺失的依赖，无需确认
- `auto_update_pip`: 在安装依赖前自动更新pip

### 示例

假设你有一个名为 `example.py` 的脚本，它使用了numpy和matplotlib：

```python
import numpy as np
import matplotlib.pyplot as plt

data = np.random.rand(100)
plt.plot(data)
plt.title('Random Data')
plt.show()
```

如果你的系统没有安装numpy或matplotlib，使用autopython会自动安装它们：

```bash
autopython example.py
```

输出：

```
缺失的模块: ['numpy', 'matplotlib']
是否安装 numpy? (y/n): y
正在安装 numpy...
是否安装 matplotlib? (y/n): y
正在安装 matplotlib...
[图表显示]
```

### 处理安装失败的情况

如果安装失败，autopython会搜索相关包并提供安装建议：

```
正在安装缺失的依赖包: some-package
安装包 some-package 失败！

正在搜索与 some-package 相关的包...
找到以下相关包，您可以尝试手动安装：
  - some-package-lib (版本: 1.2.3) - 实用的Python包
  - another-package

安装命令: python -m pip install some-package

是否继续执行代码?(y/n): 
```

## 高级功能

### 本地模块检测

autopython能够智能识别本地模块，避免尝试从PyPI安装它们：

```python
# local_module.py
def hello():
    print("Hello from local module!")

# main.py
import local_module
local_module.hello()
```

运行 `autopython main.py` 不会尝试安装 local_module。

### 递归导入检测

autopython会递归检测导入的模块，确保所有依赖都被正确安装：

```python
# module_a.py
import numpy

# main.py
import module_a
```

运行 `autopython main.py` 会检测到 numpy 的依赖并安装它。

## 开发者指南

### 安装开发环境

```bash
git clone https://github.com/StevenLi-phoenix/pythonrun.git
cd pythonrun
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

## 贡献

欢迎通过Issue或Pull Request提供反馈和建议。

## 许可证

MIT 