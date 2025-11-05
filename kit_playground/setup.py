#!/usr/bin/env python3
"""
Setup script for Kit Playground package.

This allows kit_playground to be installed as a Python package:
    pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements from requirements.txt
backend_req_file = Path(__file__).parent / "backend" / "requirements.txt"
requirements = []
if backend_req_file.exists():
    with open(backend_req_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read long description from README if available
readme_file = Path(__file__).parent.parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="kit-playground",
    version="1.0.0",
    description="Interactive development environment for NVIDIA Omniverse Kit applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NVIDIA Corporation",
    author_email="",
    url="https://github.com/NVIDIA-Omniverse/kit-app-template",
    license="MIT",
    
    # Package discovery
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    
    # Include package data
    include_package_data=True,
    package_data={
        "kit_playground.backend": [
            "static/**/*",
            "data/**/*",
        ],
    },
    
    # Dependencies
    install_requires=requirements,
    
    # Python version requirement
    python_requires=">=3.7",
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "kit-playground=kit_playground.playground:main",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Additional metadata
    keywords="nvidia omniverse kit development playground template",
    project_urls={
        "Documentation": "https://docs.omniverse.nvidia.com/kit/docs/kit-app-template",
        "Source": "https://github.com/NVIDIA-Omniverse/kit-app-template",
        "Tracker": "https://github.com/NVIDIA-Omniverse/kit-app-template/issues",
    },
)

