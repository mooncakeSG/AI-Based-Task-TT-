#!/usr/bin/env python3
"""
IntelliAssist.AI Backend Package Setup - Simplified Version
"""

from setuptools import setup, find_packages

# Hard-coded version to avoid file reading issues
VERSION = "1.0.0"

# Essential dependencies only
INSTALL_REQUIRES = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
]

setup(
    name="intelliassist-backend",
    version=VERSION,
    author="IntelliAssist.AI Team",
    author_email="team@intelliassist.ai",
    description="AI-powered task management and assistance backend",
    long_description="IntelliAssist.AI Backend - AI-powered task management and assistance",
    long_description_content_type="text/plain",
    url="https://github.com/mooncakeSG/AI-Based-Task-TT",
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
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    zip_safe=False,
) 