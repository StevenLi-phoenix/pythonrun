from typing import List, Set, Dict, Optional, Tuple, Any
import subprocess
import sys
import logging
import os
from pathlib import Path
import json
import time

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pythonrun')

# 配置文件路径
if os.name != 'nt':
    # for linux and macos
    CONFIG_DIR = os.path.join(str(Path.home()), '.config', 'pythonrun')
else:
    # for windows
    CONFIG_DIR = os.path.join(str(Path.home()), 'AppData', 'Local', 'pythonrun')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

# 当前文件路径
CURRENT_FILE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# 默认配置
DEFAULT_CONFIG = {
    'auto_install': False,    # 是否自动安装包
    'auto_update_pip': False, # 是否自动更新pip
}

if os.path.exists(os.path.join(CURRENT_FILE_DIRECTORY, 'stdlib_modules.json')):
    STDLIB_MODULES = json.load(open(os.path.join(CURRENT_FILE_DIRECTORY, 'stdlib_modules.json'), 'r', encoding='utf-8'))
else:
    STDLIB_MODULES = {}
if os.path.exists(os.path.join(CURRENT_FILE_DIRECTORY, 'package_mapping.json')):
    PACKAGE_MAPPING = json.load(open(os.path.join(CURRENT_FILE_DIRECTORY, 'package_mapping.json'), 'r', encoding='utf-8'))
else:
    PACKAGE_MAPPING = {}


def first_run_setup() -> Dict[str, Any]:
    """首次运行的设置向导"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config = DEFAULT_CONFIG.copy()
    print("\n欢迎使用 PythonRun！")
    print("这是首次运行，请进行一些简单的设置。\n")
    
    # 询问是否自动安装包
    print("PythonRun 可以在运行脚本时自动安装缺少的包。")
    response = input("是否默认自动安装缺少的包？(y/n): ").strip().lower()
    config['auto_install'] = response.lower() == 'y'
    
    # 询问是否自动更新pip
    print("\nPip 是 Python 的包管理器，保持最新版本有助于避免安装问题。")
    response = input("是否在检测到新版本时自动更新 pip？(y/n): ").strip().lower()
    config['auto_update_pip'] = response.lower() == 'y'
    
    print("\n设置已保存。您可以随时通过修改配置文件来更改这些设置。")
    print(f"配置文件位置: {CONFIG_FILE}\n")
    
    save_config(config)
    
    return config

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config: Dict[str, Any]) -> None:
    """保存配置到文件"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def search_package(package_name: str, max_depth: int = 1) -> List[Dict]:
    """Get PyPI package information"""
    logger.info(f"Searching for package {package_name}")
    try:
        if max_depth == 0:
            raise ValueError(f"Recursion max_depth reached while searching for package {package_name}")
        # 尝试导入requests，如果没有安装则跳过搜索
        import requests
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        return response.json()
    except ImportError:
        install_package('requests')
        search_package(package_name, max_depth - 1)
    except ValueError as e:
        raise e

def install_package(package_name: str) -> bool:
    logger.info(f"Installing package {package_name}")
    if not package_name:
        raise ValueError("No package name provided")
    if package_name in PACKAGE_MAPPING:
        logging.info(f"将 {package_name} 映射为 {PACKAGE_MAPPING[package_name]}")
        package_name = PACKAGE_MAPPING[package_name]
        if package_name is None:
            logger.warning(f"Package {package_name} is mapped to None in package_mapping.json")
            return False
    if package_name in STDLIB_MODULES:
        raise ValueError(f"Package {package_name} is a standard library module and cannot be installed")
    try:
        output = subprocess.run([sys.executable, '-m', 'pip', 'install', package_name])
        if output.returncode != 0:
            raise subprocess.CalledProcessError(output.returncode, output.args)
        return True
    except subprocess.CalledProcessError:
        logger.error(f"安装 {package_name} 失败")
        search_package(package_name)
        return False
    
    
def update_stdlib_modules(expire_time_day=30) -> None:
    """
    更新标准库模块
    expire_time_day: 更新时间，单位为天，默认30天
    """
    if os.path.exists(os.path.join(CURRENT_FILE_DIRECTORY, 'stdlib_modules.json')):
        last_update_time = os.path.getmtime(os.path.join(CURRENT_FILE_DIRECTORY, 'stdlib_modules.json'))
        if time.time() - last_update_time < expire_time_day * 24 * 60 * 60:
            logger.debug(f"标准库模块已在{expire_time_day}天内更新")
            return
    logger.debug("Updating standard library modules (from https://docs.python.org/3/py-modindex.html)")
    try:
        import requests
        response = requests.get('https://docs.python.org/3/py-modindex.html')
        html_content = response.text
        import re
        module_links = re.findall(r'<code class="xref">([^<]+)</code>', html_content)
        for module_link in module_links:
            module_name = module_link.split('.')[0]
            STDLIB_MODULES[module_name] = module_link
        with open(os.path.join(CURRENT_FILE_DIRECTORY, 'stdlib_modules.json'), 'w', encoding='utf-8') as f:
            json.dump(STDLIB_MODULES, f, indent=4)
    except ImportError:
        install_package('requests')
        update_stdlib_modules()
    except Exception as e:
        logger.error(f"Failed to update standard library modules: {e}")
        
        
if __name__ == "__main__":
    update_stdlib_modules()
                
                