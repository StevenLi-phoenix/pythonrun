#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
autopython - 自动导入和安装Python模块的工具
"""

import os
import sys
import ast
import importlib
import subprocess
import logging
from typing import List
from .utils import *

logger = logging.getLogger('autopython')


def findall_imports(file_path: str, max_depth: int = 10) -> List[str]:
    """查找所有导入的模块"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    CURRENT_FILE_DIRECTORY = os.path.dirname(file_path)

    tree = ast.parse(content)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if name.name not in STDLIB_MODULES:
                    imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ''
            for name in node.names:
                if name.name not in STDLIB_MODULES:
                    imports.append(f"{module}.{name.name}")
    imports = list(set(imports)) # Deduplicate
    for import_name in imports:
        if check_local_py(CURRENT_FILE_DIRECTORY, import_name):
            imports.remove(import_name)
            imports.extend(findall_imports(os.path.join(CURRENT_FILE_DIRECTORY, import_name + ".py"), max_depth - 1))
        elif check_local_package(CURRENT_FILE_DIRECTORY, import_name):
            imports.remove(import_name)
            recursive_dir = os.listdir(os.path.join(CURRENT_FILE_DIRECTORY, import_name))
            for recursive_filename in recursive_dir:
                if recursive_filename.endswith(".py"):
                    imports.extend(findall_imports(os.path.join(CURRENT_FILE_DIRECTORY, import_name, recursive_filename), max_depth - 1))
    return imports

def check_local_py(CURRENT_FILE_DIRECTORY, import_name: str) -> bool:
    """检查本地是否存在该模块"""
    if os.path.exists(os.path.join(CURRENT_FILE_DIRECTORY, import_name + ".py")):
        return True
    return False

def check_local_package(CURRENT_FILE_DIRECTORY, import_name: str) -> bool:
    """检查本地是否存在该模块"""
    if os.path.exists(os.path.join(CURRENT_FILE_DIRECTORY, import_name, "__init__.py")):
        return True
    return False

def find_missing_imports(imports: List[str]) -> List[str]:
    """查找缺失的模块"""
    missing_imports = []
    for import_name in imports:
        if importlib.util.find_spec(import_name) is None:
            missing_imports.append(import_name)
    return missing_imports

def main():
    """主函数"""
    # 加载配置
    if not os.path.exists(CONFIG_FILE):
        first_run_setup()

    config = load_config()
    
    if len(sys.argv) < 2:
        logging.info("用法: autopython <python_file> [args...]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not file_path.endswith('.py'):
        logger.warning(f"文件 {file_path} 不是Python文件")
    
    imports = find_missing_imports(findall_imports(file_path))
    flag_installAllRequired = True
    if imports:
        logging.info(f"缺失的模块: {imports}")
        if config.get('auto_update_pip', False):
            logger.info("正在更新pip")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            update_stdlib_modules()
        for import_name in imports:
            if config.get('auto_install', False) or input(f"是否安装 {import_name}? (y/n): ") == 'y':
                flag_installAllRequired &= install_package(import_name)
            else:
                # User can't install all required packages, can't pythonrun the script
                flag_installAllRequired = False
    
    if flag_installAllRequired:
        # run in detached mode, forward all arguments and cwd
        logger.debug(f"正在替换当前进程，运行 {file_path} {sys.argv[2:]}")
        os.execv(sys.executable, [sys.executable, file_path] + sys.argv[2:])
    else:
        logger.warning("无法安装所有缺失的模块，无法运行脚本")


if __name__ == "__main__":
    main()