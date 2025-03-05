#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试search_package功能的脚本
"""

import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_search')

# 导入autopython的search_package函数
try:
    from autopython.autopython.main import search_package
except ImportError:
    # 尝试导入本地版本
    sys.path.append('.')
    try:
        from autopython.main import search_package
    except ImportError:
        logger.error("无法导入search_package函数，请确保autopython已正确安装")
        sys.exit(1)

def main():
    """测试搜索包功能"""
    search_terms = [
        "numpy",           # 存在的常用包
        "numpie",          # 拼写错误的常用包
        "pandas_dataframe", # 拼写错误的包名
        "tensorflow_lite",  # 相关包
        "totally_nonexistent_package_123" # 完全不存在的包
    ]
    
    for term in search_terms:
        logger.info(f"\n{'='*50}")
        logger.info(f"搜索包: {term}")
        logger.info(f"{'='*50}")
        
        results = search_package(term)
        
        if results:
            logger.info(f"找到 {len(results)} 个相关包:")
            for i, pkg in enumerate(results, 1):
                pkg_info = f"{i}. {pkg.get('name', '')}"
                if pkg.get('version'):
                    pkg_info += f" (版本: {pkg['version']})"
                if pkg.get('summary'):
                    pkg_info += f" - {pkg['summary']}"
                logger.info(pkg_info)
        else:
            logger.info(f"未找到与 {term} 相关的包")
        
        logger.info(f"{'='*50}\n")

if __name__ == "__main__":
    main() 