#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试parse_imports功能
"""
import unittest
from autopython.main import parse_imports

class TestParseImports(unittest.TestCase):
    """测试解析导入语句的功能"""
    
    def test_simple_import(self):
        """测试简单导入"""
        code = "import os"
        result = parse_imports(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "os")
        self.assertIsNone(result[0][1])
    
    def test_import_with_alias(self):
        """测试带别名的导入"""
        code = "import numpy as np"
        result = parse_imports(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "numpy")
        self.assertEqual(result[0][1], "np")
    
    def test_from_import(self):
        """测试from导入"""
        code = "from os import path"
        result = parse_imports(code)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "os")
        self.assertIsNone(result[0][1])
    
    def test_multiple_imports(self):
        """测试多个导入"""
        code = """
import os
import sys
import numpy as np
from pathlib import Path
"""
        result = parse_imports(code)
        self.assertEqual(len(result), 4)
        modules = [mod for mod, _ in result]
        self.assertIn("os", modules)
        self.assertIn("sys", modules)
        self.assertIn("numpy", modules)
        self.assertIn("pathlib", modules)

if __name__ == "__main__":
    unittest.main() 