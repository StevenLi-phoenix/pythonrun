#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
autopython - 自动导入和安装Python模块的工具
"""

import os
import sys
import ast
import re
import importlib
import subprocess
import logging
import tempfile
import json
from typing import List, Set, Dict, Optional, Tuple, Any
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('autopython')

# 配置文件路径
CONFIG_DIR = os.path.join(str(Path.home()), '.autopython')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

# 标准库列表
STDLIB_MODULES = set(sys.builtin_module_names)
STDLIB_MODULES.update([
    'abc', 'argparse', 'asyncio', 'base64', 'collections', 'copy', 'datetime',
    'functools', 'hashlib', 'http', 'io', 'itertools', 'json', 'logging', 'math', 
    'os', 'pickle', 'random', 're', 'shutil', 'socket', 'sys', 'tempfile', 
    'threading', 'time', 'traceback', 'urllib', 'warnings', 'zipfile'
])

# 包与模块的映射关系，有些模块名与包名不同
PACKAGE_MAPPING = {
    'PIL': 'pillow',
    'cv2': 'opencv-python',
    'sklearn': 'scikit-learn',
    'bs4': 'beautifulsoup4',
    'yaml': 'pyyaml',
    'Image': 'pillow',
    'tkinter': None,  # 标准库但可能需要额外安装
    'matplotlib.pyplot': 'matplotlib',
    'numpy.linalg': 'numpy',
    'pandas.DataFrame': 'pandas',
    'tensorflow.keras': 'tensorflow',
    'torch.nn': 'torch',
    'transformers': 'transformers',
    'seaborn': 'seaborn',
    'plotly.express': 'plotly',
    'dash': 'dash',
    'requests': 'requests',
    'flask': 'flask',
    'django': 'django',
    'sqlalchemy': 'sqlalchemy',
    'scipy': 'scipy',
    'nltk': 'nltk',
    'spacy': 'spacy',
    'gensim': 'gensim',
    'xgboost': 'xgboost',
    'lightgbm': 'lightgbm',
    'catboost': 'catboost',
    'scrapy': 'scrapy',
    'kivy': 'kivy',
    'pydantic': 'pydantic',
    'fastapi': 'fastapi',
}

# 默认配置
DEFAULT_CONFIG = {
    'auto_install': False,    # 是否自动安装包
    'auto_update_pip': False, # 是否自动更新pip
}

def parse_imports(code: str) -> List[Tuple[str, Optional[str]]]:
    """解析代码中的导入语句，返回所有导入的模块名
    
    返回: [(模块名, 别名), ...]
    """
    modules = []
    
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            # 处理 import X 格式
            if isinstance(node, ast.Import):
                for name in node.names:
                    modules.append((name.name, name.asname))
            
            # 处理 from X import Y 格式
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0:  # 不处理相对导入
                    module_name = node.module
                    if module_name:
                        # 只添加主模块名，不添加子模块
                        main_module = module_name.split('.')[0]
                        modules.append((main_module, None))
    except SyntaxError as e:
        logger.error(f"解析代码时出现语法错误: {e}")
        
    return modules

def get_installed_packages() -> Dict[str, str]:
    """获取当前环境中已安装的包
    
    返回: {包名: 版本号, ...}
    """
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        
        import json
        packages = json.loads(result.stdout)
        return {pkg['name'].lower(): pkg['version'] for pkg in packages}
    except Exception as e:
        logger.error(f"获取已安装包信息失败: {e}")
        return {}

def get_package_for_module(module_name: str) -> Optional[str]:
    """根据模块名获取对应的包名"""
    # 处理子模块
    base_module = module_name.split('.')[0]
    
    # 检查映射关系
    if module_name in PACKAGE_MAPPING:
        return PACKAGE_MAPPING[module_name]
    elif base_module in PACKAGE_MAPPING:
        return PACKAGE_MAPPING[base_module]
    
    # 默认情况下包名与模块名相同
    if base_module in STDLIB_MODULES:
        return None  # 标准库不需要安装
    
    return base_module

def search_package(package_name: str) -> List[Dict]:
    """搜索PyPI上的相关包
    
    返回: 与搜索词相关的包列表
    """
    try:
        # 尝试导入requests，如果没有安装则跳过搜索
        import requests
        try:
            # 常见的拼写错误模式
            common_typos = {
                # 常见拼写错误替换
                'nump': 'numpy',
                'pands': 'pandas',
                'mathplotlib': 'matplotlib',
                'scipi': 'scipy',
                'opencv': 'opencv-python',
                'sk': 'scikit',
                'tensorflow': 'tensorflow',
                'pytorch': 'torch',
                'beautifulsoup': 'beautifulsoup4',
                'bs': 'beautifulsoup4',
                'req': 'requests',
                'pil': 'pillow',
                'yaml': 'pyyaml',
            }
            
            # 检查是否是常见的拼写错误
            if package_name.lower() in common_typos:
                suggested_name = common_typos[package_name.lower()]
                logger.info(f"您可能是指 {suggested_name}? 尝试使用正确的包名。")
                # 尝试获取建议包的信息
                suggested_url = f"https://pypi.org/pypi/{suggested_name}/json"
                response = requests.get(suggested_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return [{
                        'name': data['info']['name'],
                        'version': data['info']['version'],
                        'summary': data['info']['summary'],
                        'is_suggestion': True,
                        'original_name': package_name
                    }]
            
            # 使用莱文斯坦距离找出相似的包名
            def levenshtein_distance(s1, s2):
                if len(s1) < len(s2):
                    return levenshtein_distance(s2, s1)
                if len(s2) == 0:
                    return len(s1)
                previous_row = range(len(s2) + 1)
                for i, c1 in enumerate(s1):
                    current_row = [i + 1]
                    for j, c2 in enumerate(s2):
                        insertions = previous_row[j + 1] + 1
                        deletions = current_row[j] + 1
                        substitutions = previous_row[j] + (c1 != c2)
                        current_row.append(min(insertions, deletions, substitutions))
                    previous_row = current_row
                return previous_row[-1]
            
            # 使用PyPI的JSON API搜索包
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # 包存在，直接返回这个包的信息
                data = response.json()
                return [{
                    'name': data['info']['name'],
                    'version': data['info']['version'],
                    'summary': data['info']['summary']
                }]
            
            # 如果没有精确匹配，尝试搜索相关包
            search_url = f"https://pypi.org/search/?q={package_name}"
            logger.info(f"未找到精确匹配的包。您可以访问以下链接手动搜索相关包：\n{search_url}")
            
            # 尝试使用PyPI API搜索相似的包
            search_api_url = f"https://pypi.org/simple/"
            response = requests.get(search_api_url, timeout=5)
            if response.status_code == 200:
                # 简单解析结果，查找相似名称的包
                import re
                content = response.text
                all_packages = re.findall(r'<a[^>]*>([^<]*)</a>', content)
                
                # 找出相似包名
                similar_packages = []
                for pkg in all_packages:
                    # 完全包含
                    if package_name.lower() in pkg.lower() or pkg.lower() in package_name.lower():
                        similar_packages.append({
                            'name': pkg,
                            'similarity': 0.9 if pkg.lower().startswith(package_name.lower()) else 0.7
                        })
                    # 莱文斯坦距离
                    else:
                        distance = levenshtein_distance(package_name.lower(), pkg.lower())
                        # 只考虑较短距离的包
                        max_acceptable_distance = min(3, max(1, len(package_name) // 3))
                        if distance <= max_acceptable_distance:
                            similarity = 1.0 - (distance / max(len(package_name), len(pkg)))
                            if similarity > 0.6:  # 只保留相似度较高的
                                similar_packages.append({
                                    'name': pkg,
                                    'similarity': similarity
                                })
                
                # 按相似度排序并获取前5个
                similar_packages.sort(key=lambda x: x['similarity'], reverse=True)
                results = [{'name': pkg['name']} for pkg in similar_packages[:5]]
                return results
            
            return []
        except Exception as e:
            logger.error(f"搜索包时出错: {e}")
            return []
    except ImportError:
        logger.warning("未安装requests库，无法搜索包信息")
        # 提供PyPI搜索链接
        search_url = f"https://pypi.org/search/?q={package_name}"
        logger.info(f"您可以访问以下链接手动搜索相关包：\n{search_url}")
        return []

def install_package(package_name: str) -> bool:
    """安装指定的包
    
    返回: 安装是否成功
    """
    if not package_name or package_name in STDLIB_MODULES:
        return True
        
    try:
        logger.info(f"正在安装包: {package_name}")
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package_name],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"安装包 {package_name} 失败: {e}")
        
        # 尝试搜索相关包
        logger.info(f"正在搜索与 {package_name} 相关的包...")
        similar_packages = search_package(package_name)
        
        if similar_packages:
            # 检查是否有建议包
            suggested_packages = [pkg for pkg in similar_packages if pkg.get('is_suggestion', False)]
            if suggested_packages:
                pkg = suggested_packages[0]
                logger.info(f"您可能是想安装 {pkg['name']} 而不是 {pkg['original_name']}?")
                logger.info(f"建议的安装命令: {sys.executable} -m pip install {pkg['name']}")
                
                # 询问是否使用建议的包
                if input(f"是否安装建议的包 {pkg['name']}? (y/n): ").lower() == 'y':
                    try:
                        logger.info(f"正在安装建议的包: {pkg['name']}")
                        subprocess.run(
                            [sys.executable, '-m', 'pip', 'install', pkg['name']],
                            check=True
                        )
                        return True
                    except subprocess.CalledProcessError as e:
                        logger.error(f"安装建议的包 {pkg['name']} 失败: {e}")
            else:
                logger.info("找到以下相关包，您可以尝试手动安装：")
                for pkg in similar_packages:
                    pkg_info = f"{pkg.get('name', '')}"
                    if pkg.get('version'):
                        pkg_info += f" (版本: {pkg['version']})"
                    if pkg.get('summary'):
                        pkg_info += f" - {pkg['summary']}"
                    logger.info(f"  - {pkg_info}")
            
            install_cmd = f"{sys.executable} -m pip install {package_name}"
            logger.info(f"安装命令: {install_cmd}")
        else:
            logger.info(f"未找到与 {package_name} 相关的包。请检查包名是否正确，或者手动搜索PyPI。")
            logger.info(f"您可以尝试使用以下命令安装：{sys.executable} -m pip install {package_name}")
        
        return False

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        # 如果配置目录不存在，创建它
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        # 首次运行，询问用户
        config = first_run_setup()
        save_config(config)
        return config
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 确保配置完整，如有新配置项则添加默认值
        updated = False
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                updated = True
        
        if updated:
            save_config(config)
        
        return config
    except Exception as e:
        logger.error(f"加载配置文件时出错: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logger.error(f"保存配置文件时出错: {e}")

def first_run_setup() -> Dict[str, Any]:
    """首次运行的设置向导"""
    config = DEFAULT_CONFIG.copy()
    
    print("\n欢迎使用 AutoPython！")
    print("这是首次运行，请进行一些简单的设置。\n")
    
    # 询问是否自动安装包
    print("AutoPython 可以在运行脚本时自动安装缺少的包。")
    response = input("是否默认自动安装缺少的包？(y/n): ").strip().lower()
    config['auto_install'] = response == 'y'
    
    # 询问是否自动更新pip
    print("\nPip 是 Python 的包管理器，保持最新版本有助于避免安装问题。")
    response = input("是否在检测到新版本时自动更新 pip？(y/n): ").strip().lower()
    config['auto_update_pip'] = response == 'y'
    
    print("\n设置已保存。您可以随时通过修改配置文件来更改这些设置。")
    print(f"配置文件位置: {CONFIG_FILE}\n")
    
    return config

def modify_code_to_autoinstall(code: str) -> str:
    """修改代码，添加自动安装导入的功能
    
    返回: 修改后的代码
    """
    modules = parse_imports(code)
    
    # 获取所有非标准库导入
    non_stdlib_modules = []
    for module_name, _ in modules:
        package_name = get_package_for_module(module_name)
        if package_name:
            non_stdlib_modules.append((module_name, package_name))
    
    if not non_stdlib_modules:
        return code  # 没有需要处理的模块
    
    # 添加自动安装的代码
    autoinstall_code = """
# 自动安装和导入模块的辅助代码
def _autopython_autoinstall():
    import importlib
    import subprocess
    import sys
    import re
    import os
    
    # 加载配置
    import json
    from pathlib import Path
    
    CONFIG_DIR = os.path.join(str(Path.home()), '.autopython')
    CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
    
    # 默认配置
    config = {
        'auto_install': False,
        'auto_update_pip': False,
    }
    
    # 尝试加载配置
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config.update(json.load(f))
    except Exception as e:
        print(f"加载配置时出错: {e}")

"""
    
    for module_name, package_name in non_stdlib_modules:
        if package_name:
            autoinstall_code += f"""
    try:
        importlib.import_module('{module_name}')
    except ImportError:
        try:
            print(f"正在安装缺失的依赖包: {package_name}")
            # 检查是否有pip更新
            if config['auto_update_pip']:
                try:
                    pip_check = subprocess.run(
                        [sys.executable, '-m', 'pip', 'list', '--outdated'],
                        capture_output=True, text=True, check=False
                    )
                    if "pip" in pip_check.stdout:
                        print("检测到pip可更新，正在更新...")
                        subprocess.run(
                            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                            check=False
                        )
                except Exception as e:
                    print(f"检查pip更新时出错: {{e}}")
            
            # 安装包
            subprocess.run([sys.executable, '-m', 'pip', 'install', '{package_name}'], check=True)
        except subprocess.CalledProcessError:
            print(f"\\n安装包 {package_name} 失败！")
            print(f"请尝试手动安装: {{sys.executable}} -m pip install {package_name}")
            print(f"或访问 https://pypi.org/search/?q={package_name} 搜索相关包\\n")
            
            if config['auto_install'] or input("是否继续执行代码?(y/n): ").lower() != 'y':
                sys.exit(1)

"""
    
    autoinstall_code += """
_autopython_autoinstall()
del _autopython_autoinstall
"""
    
    # 在导入语句之前插入自动安装代码
    # 尝试找到代码中的第一个非注释、非空行
    lines = code.split('\n')
    insert_pos = 0
    
    # 查找适合插入的位置（跳过文件头的注释和空行）
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            if i > 0 and re.match(r'^""".*', stripped):
                # 如果是文档字符串，找到它的结束位置
                for j in range(i+1, len(lines)):
                    if re.search(r'"""$', lines[j]):
                        insert_pos = j + 1
                        break
                else:
                    insert_pos = i  # 没找到结束，就在开始处插入
            else:
                insert_pos = i
            break
    
    # 插入自动安装代码
    modified_code = '\n'.join(lines[:insert_pos]) + '\n' + autoinstall_code + '\n'.join(lines[insert_pos:])
    return modified_code

def process_file(file_path: str, run: bool = True) -> None:
    """处理Python文件，添加自动导入功能并执行"""
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 修改代码，添加自动安装功能
        modified_code = modify_code_to_autoinstall(code)
        
        # 创建临时文件来运行修改后的代码
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', encoding='utf-8', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(modified_code)
        
        if run:
            logger.info(f"正在执行文件: {file_path}")
            # 设置环境变量，传递原始文件路径
            env = os.environ.copy()
            
            # 执行修改后的代码
            # 传递原脚本的参数
            cmd = [sys.executable, temp_path] + sys.argv[2:]
            result = subprocess.run(cmd, check=False, env=env)
        
        # 删除临时文件
        os.unlink(temp_path)
            
    except Exception as e:
        logger.error(f"处理文件时出错: {e}")

def handle_main_problem(file_path: str) -> None:
    """处理if __name__ == '__main__'的问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 检查代码中是否有if __name__ == '__main__'
        has_main_block = re.search(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', code) is not None
        
        if has_main_block:
            # 有main块，需要特殊处理
            modified_code = modify_code_to_autoinstall(code)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.py', mode='w', encoding='utf-8', delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(modified_code)
            
            # 设置__name__='__main__'来执行临时文件
            cmd = [sys.executable, '-c', f"__name__ = '__main__'; exec(open('{temp_path}').read())"]
            subprocess.run(cmd, check=False)
            
            # 删除临时文件
            os.unlink(temp_path)
        else:
            # 没有main块，直接处理
            process_file(file_path)
    
    except Exception as e:
        logger.error(f"处理main块时出错: {e}")

def main():
    """主函数"""
    # 加载配置
    config = load_config()
    
    if len(sys.argv) < 2:
        print("用法: autopython <python_file> [args...]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not file_path.endswith('.py'):
        logger.warning(f"文件 {file_path} 不是Python文件")
    
    handle_main_problem(file_path)

if __name__ == "__main__":
    main() 