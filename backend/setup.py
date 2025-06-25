#!/usr/bin/env python3
"""
IntelliAssist.AI Backend Package Setup
"""

import os
import re
from pathlib import Path
from setuptools import setup, find_packages

def get_version():
    """Read version from __init__.py"""
    init_file = Path(__file__).parent / "__init__.py"
    if not init_file.exists():
        return "1.0.0"
    
    content = init_file.read_text()
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', content, re.MULTILINE)
    if version_match:
        return version_match.group(1)
    return "1.0.0"

def get_requirements():
    """Read requirements from requirements.txt"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        return []
    
    requirements = []
    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
    return requirements

def get_long_description():
    """Read long description from README.md"""
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        return readme_file.read_text(encoding='utf-8')
    return "IntelliAssist.AI Backend - AI-powered task management and assistance"

setup(
    name="intelliassist-backend",
    version=get_version(),
    author="IntelliAssist.AI Team",
    author_email="team@intelliassist.ai",
    description="AI-powered task management and assistance backend",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AI-Based-Task-TT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "intelliassist-backend=main:app",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.sql", "*.env.example", "*.md"],
    },
) 