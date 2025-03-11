#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pythonrun 测试模块
"""
import os
import pytest
import subprocess
import sys
from pythonrun.main import findall_imports, find_missing_imports, check_local_py, STDLIB_MODULES


@pytest.fixture
def numpy_environment():
    """管理numpy环境的fixture"""
    # 检查numpy是否已安装
    check_cmd = [sys.executable, '-m', 'pip', 'show', 'numpy']
    result = subprocess.run(check_cmd, capture_output=True)
    numpy_installed = result.returncode == 0
    
    # 如果已安装，先卸载
    if numpy_installed:
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'numpy', '-y'], 
                      capture_output=True)
    
    yield
    
    # 恢复原始环境
    if numpy_installed:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy'], 
                      capture_output=True)


def test_basic_import():
    """测试basic_import.py"""
    assert findall_imports('./tests/basic_import.py') == ['numpy'], \
        "basic_import.py 应该导入 numpy"


def test_basic_recursive_import():
    """测试basic_recursive_import.py"""
    assert findall_imports('./tests/basic_recurcive_import.py') == ['numpy'], \
        "basic_recurcive_import.py 应该导入 numpy"


def test_local_test():
    """测试local_test.py"""
    assert findall_imports('./tests/local_test.py') == [], \
        "local_test.py 不应该导入任何模块"


def test_missing_import(numpy_environment):
    """测试缺失模块的检测"""
    # 确保numpy未安装
    assert find_missing_imports(["numpy", "sys"]) == ['numpy'], \
        "应该检测到numpy缺失"
    
    # 安装numpy
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy'], 
                  capture_output=True)
    
    # 确认numpy已安装
    assert find_missing_imports(["numpy", "sys"]) == [], \
        "安装后不应该检测到numpy缺失"


@pytest.mark.parametrize("module_name,expected", [
    ("os", True),  # 标准库
    ("sys", True),  # 标准库
    ("nonexistent_module_123456", False),  # 不存在的模块
])
def test_stdlib_modules(module_name, expected):
    """测试标准库模块检测"""
    assert (module_name in STDLIB_MODULES) == expected


def test_check_local_py():
    """测试本地.py文件检测"""
    # 创建临时测试文件
    test_dir = os.path.join(os.getcwd(), "test_temp")
    os.makedirs(test_dir, exist_ok=True)
    
    test_file = os.path.join(test_dir, "local_module.py")
    with open(test_file, "w") as f:
        f.write("# Test file")
    
    try:
        assert check_local_py(test_dir, "local_module") == True
        assert check_local_py(test_dir, "nonexistent_module") == False
    finally:
        # 清理
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(test_dir):
            os.rmdir(test_dir)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])