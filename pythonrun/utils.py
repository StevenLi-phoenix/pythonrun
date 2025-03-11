from typing import List, Set, Dict, Optional, Tuple, Any
import subprocess
import sys
import logging
import os
from pathlib import Path
import json
import time
import re

# 配置日志
if os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes', 'on'):
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
else:
    logging.basicConfig(
        level=logging.INFO,
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

# 安全加载JSON文件
def safe_load_json(file_path: str, default_value: Any = None) -> Any:
    """安全加载JSON文件，如果文件不存在或格式错误则返回默认值"""
    if not os.path.exists(file_path):
        return default_value
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, PermissionError, FileNotFoundError) as e:
        logger.error(f"无法加载JSON文件 {file_path}: {e}")
        return default_value

# 加载标准库模块和包映射
STDLIB_MODULES = safe_load_json(os.path.join(CURRENT_FILE_DIRECTORY, 'stdlib_modules.json'), {})
PACKAGE_MAPPING = safe_load_json(os.path.join(CURRENT_FILE_DIRECTORY, 'package_mapping.json'), {})


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
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes', 'on'):
                logger.debug(f"已加载配置: {config}")
            return config
    except (json.JSONDecodeError, PermissionError, FileNotFoundError) as e:
        logger.error(f"无法加载配置文件: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """保存配置到文件"""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        if os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes', 'on'):
            logger.debug(f"已保存配置: {config}")
    except (PermissionError, FileNotFoundError) as e:
        logger.error(f"无法保存配置文件: {e}")

def search_package(package_name: str, max_depth: int = 1) -> Optional[Dict]:
    """Get PyPI package information"""
    logger.info(f"Searching for package {package_name}")
    
    # 验证包名是否合法
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', package_name):
        logger.warning(f"包名 {package_name} 包含非法字符")
        return None
        
    try:
        if max_depth <= 0:
            logger.warning(f"Recursion max_depth reached while searching for package {package_name}")
            return None
            
        # 尝试导入requests，如果没有安装则跳过搜索
        try:
            import requests
            # 设置超时，避免长时间等待
            if os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes', 'on'):
                logger.debug(f"正在请求 PyPI API: {package_name}")
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"PyPI返回非200状态码: {response.status_code}")
                return None
        except ImportError:
            # 安装requests后重试，但减少递归深度
            logger.info("正在安装requests模块...")
            install_package('requests')
            return search_package(package_name, max_depth - 1)
        except requests.exceptions.RequestException as e:
            logger.error(f"请求PyPI时出错: {e}")
            return None
    except Exception as e:
        logger.error(f"搜索包 {package_name} 时出错: {e}")
        return None

def install_package(package_name: str) -> bool:
    """安装Python包"""
    logger.info(f"Installing package {package_name}")
    
    # 验证包名
    if not package_name or not isinstance(package_name, str):
        logger.error("No package name provided or invalid package name")
        return False
        
    # 验证包名是否合法
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', package_name):
        logger.warning(f"包名 {package_name} 包含非法字符")
        return False
        
    # 检查包映射
    if package_name in PACKAGE_MAPPING:
        mapped_package = PACKAGE_MAPPING[package_name]
        logging.info(f"将 {package_name} 映射为 {mapped_package}")
        if mapped_package is None:
            logger.warning(f"Package {package_name} is mapped to None in package_mapping.json")
            return False
        package_name = mapped_package
        
    # 检查是否为标准库模块
    if package_name in STDLIB_MODULES:
        logger.info(f"Package {package_name} is a standard library module and cannot be installed")
        return True  # 返回True因为标准库已经可用
        
    try:
        # 使用subprocess安装包，设置超时
        if os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes', 'on'):
            logger.debug(f"正在执行: pip install {package_name}")
            
        process = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package_name],
            timeout=300,  # 5分钟超时
            check=False,
            capture_output=os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes', 'on')
        )
        
        if process.returncode != 0:
            logger.error(f"安装 {package_name} 失败，返回码: {process.returncode}")
            if os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes', 'on') and hasattr(process, 'stderr'):
                logger.debug(f"错误输出: {process.stderr.decode('utf-8', errors='replace')}")
            # 尝试搜索包信息，但不递归调用install_package
            search_package(package_name)
            return False
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"安装 {package_name} 超时")
        return False
    except Exception as e:
        logger.error(f"安装 {package_name} 时出错: {e}")
        return False
    
    
def update_stdlib_modules(expire_time_day=30) -> None:
    """
    更新标准库模块
    expire_time_day: 更新时间，单位为天，默认30天
    """
    try:
        stdlib_file = os.path.join(CURRENT_FILE_DIRECTORY, 'stdlib_modules.json')
        if os.path.exists(stdlib_file):
            last_update_time = os.path.getmtime(stdlib_file)
            if time.time() - last_update_time < expire_time_day * 24 * 60 * 60:
                logger.debug(f"标准库模块已在{expire_time_day}天内更新")
                return
                
        logger.debug("Updating standard library modules (from https://docs.python.org/3/py-modindex.html)")
        
        try:
            import requests
            # 设置超时，避免长时间等待
            if os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes', 'on'):
                logger.debug("正在请求Python文档...")
                
            response = requests.get('https://docs.python.org/3/py-modindex.html', timeout=10)
            if response.status_code != 200:
                logger.warning(f"获取标准库模块列表失败，状态码: {response.status_code}")
                return
                
            html_content = response.text
            module_links = re.findall(r'<code class="xref">([^<]+)</code>', html_content)
            
            # 更新标准库模块字典
            updated_modules = {}
            for module_link in module_links:
                module_name = module_link.split('.')[0]
                updated_modules[module_name] = module_link
                
            # 安全写入文件
            try:
                with open(stdlib_file, 'w', encoding='utf-8') as f:
                    json.dump(updated_modules, f, indent=4)
                # 更新全局变量
                global STDLIB_MODULES
                STDLIB_MODULES = updated_modules
                if os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes', 'on'):
                    logger.debug(f"已更新标准库模块，共 {len(updated_modules)} 个")
            except (PermissionError, FileNotFoundError) as e:
                logger.error(f"无法写入标准库模块文件: {e}")
                
        except ImportError:
            # 如果没有requests，尝试安装它
            if install_package('requests'):
                # 安装成功后重试，但不递归调用
                logger.info("已安装requests，请稍后再次尝试更新标准库模块")
            else:
                logger.error("无法安装requests，无法更新标准库模块")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求Python文档时出错: {e}")
    except Exception as e:
        logger.error(f"更新标准库模块时出错: {e}")
        
        
if __name__ == "__main__":
    update_stdlib_modules()
                
                