# pythonrun

自动导入和安装Python模块的工具

[![PyPI version](https://badge.fury.io/py/pythonrun.svg)](https://badge.fury.io/py/pythonrun)
[![Python Versions](https://img.shields.io/pypi/pyversions/pythonrun.svg)](https://pypi.org/project/pythonrun/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![self testing](https://github.com/StevenLi-phoenix/pythonrun/actions/workflows/pytest.yml/badge.svg)](https://github.com/StevenLi-phoenix/pythonrun/actions/workflows/pytest.yml)

## 功能特点

- 自动检测Python脚本中导入的模块
- 自动安装缺少的依赖包
- 智能处理本地模块和标准库
- 支持递归检测导入
- 支持命令行参数传递
- 自动纠正部分包名（如将 `PIL` 纠正为 `Pillow`, `torch` 纠正为 `torch torchvision torchaudio`-这三个包需要一起安装，根据官网安装提示）
- 自动读取requirements.txt

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
pythonrun your_script.py [arg1 arg2 ...]
```

### 配置选项

你可以通过配置文件自定义pythonrun的行为，默认配置文件为 `~/.config/pythonrun/config.json`：
- `auto_install`: 自动安装所有缺失的依赖，无需确认
- `auto_update_pip`: 在安装依赖前自动更新pip
- `auto_read_requirements`: 自动读取requirements.txt

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

如果你的系统没有安装numpy或matplotlib，使用pythonrun会自动安装它们：

```bash
pythonrun example.py
```

输出：

```
缺失的模块: ['numpy', 'matplotlib']
是否安装 numpy? (y/n): y
正在安装 numpy...
是否安装 matplotlib? (y/n): y
正在安装 matplotlib...
<运行你的python脚本>
[图表显示]
```

### 本地模块检测

pythonrun能够智能识别本地模块，避免尝试从PyPI安装它们：

```python
# local_module.py
def hello():
    print("Hello from local module!")

# main.py
import local_module
local_module.hello()
```

运行 `pythonrun main.py` 不会尝试安装 local_module。

### 递归导入检测

pythonrun会递归检测导入的模块，确保所有依赖都被正确安装：

```python
# module_a.py
import numpy

# main.py
import module_a
```

运行 `pythonrun main.py` 会检测到 numpy 的依赖并安装它。

## 开发者指南

### 安装开发环境

```bash
git clone https://github.com/StevenLi-phoenix/pythonrun.git
cd pythonrun
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest tests/test_entry.py
```

## 最近更新

- 修复了递归导入时可能导致的无限循环问题
- 增强了错误处理和异常捕获
- 改进了文件操作的安全性
- 添加了包名验证，防止恶意注入
- 添加了网络请求和安装操作的超时控制
- 优化了标准库模块的更新逻辑

## 贡献

欢迎通过Issue或Pull Request提供反馈和建议。

## 许可证

MIT 
