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
    if max_depth <= 0:
        logger.warning(f"达到最大递归深度，停止分析 {file_path}")
        return []
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"无法读取文件 {file_path}: {e}")
        return []
        
    CURRENT_FILE_DIRECTORY = os.path.dirname(os.path.abspath(file_path))

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        logger.error(f"解析文件 {file_path} 时出现语法错误: {e}")
        return []
        
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
    result_imports = imports.copy()  # 创建副本，避免在迭代时修改列表
    
    for import_name in imports:
        if check_local_py(CURRENT_FILE_DIRECTORY, import_name):
            result_imports.remove(import_name)
            local_file_path = os.path.join(CURRENT_FILE_DIRECTORY, import_name + ".py")
            # 避免循环引用
            if os.path.abspath(local_file_path) != os.path.abspath(file_path):
                result_imports.extend(findall_imports(local_file_path, max_depth - 1))
        elif check_local_package(CURRENT_FILE_DIRECTORY, import_name):
            result_imports.remove(import_name)
            package_dir = os.path.join(CURRENT_FILE_DIRECTORY, import_name)
            try:
                recursive_dir = os.listdir(package_dir)
                for recursive_filename in recursive_dir:
                    if recursive_filename.endswith(".py"):
                        local_file_path = os.path.join(package_dir, recursive_filename)
                        # 避免循环引用
                        if os.path.abspath(local_file_path) != os.path.abspath(file_path):
                            result_imports.extend(findall_imports(local_file_path, max_depth - 1))
            except (PermissionError, FileNotFoundError) as e:
                logger.error(f"无法访问目录 {package_dir}: {e}")
    
    return list(set(result_imports))  # 再次去重

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
    if not os.path.exists(file_path):
        logger.error(f"文件 {file_path} 不存在")
        sys.exit(1)
        
    if not file_path.endswith('.py'):
        logger.warning(f"文件 {file_path} 不是Python文件")
    
    try:
        imports = find_missing_imports(findall_imports(file_path))
        flag_installAllRequired = True
        if imports:
            logging.info(f"缺失的模块: {imports}")
            if config.get('auto_update_pip', False):
                logger.info("正在更新pip")
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
                update_stdlib_modules()
            for import_name in imports:
                if config.get('auto_install', False) or input(f"是否安装 {import_name}? (y/n): ").lower() == 'y':
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
    except Exception as e:
        logger.error(f"运行时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()