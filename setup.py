#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="amb-cli",
    version="2.0.0",
    description="CLI Global do AMB_V2 - Automação, Agentes e Integrações",
    py_modules=["cli"],
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0"
    ],
    entry_points={
        "console_scripts": [
            "amb = cli:main",
        ],
    },
)
