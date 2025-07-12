#!/usr/bin/env python3
"""
Setup script for SMS GoTo Home Assistant Integration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sms-goto-ha",
    version="1.0.0",
    author="Taylor Brinton",
    author_email="taylor@brinton.xyz",
    description="SMS GoTo integration for Home Assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oneofthegeeks/HA-SMS",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "test-sms-goto=sms_goto.test:main",
        ],
    },
) 