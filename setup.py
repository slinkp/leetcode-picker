"""Setup script for leetcode-picker."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="leetcode-picker",
    version="0.1.0",
    author="Paul",
    description="A CLI tool for picking random LeetCode problems and tracking progress",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.13",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "leetcode-picker=leetcode_picker.main:main",
        ],
    },
)