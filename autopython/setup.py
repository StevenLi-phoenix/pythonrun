#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autopython",
    version="0.1.1",
    author="lishuyu",
    author_email="example@example.com",
    description="自动导入和安装Python模块的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lishuyu/autopython",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="import, package management, dependency, automation",
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "autopython=autopython.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/lishuyu/autopython/issues",
        "Source": "https://github.com/lishuyu/autopython",
    },
) 