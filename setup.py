#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="amb-cli",
    version="2.3.0",
    description="CLI Global do AMB_V2 - Automação, Agentes e Integrações",
    py_modules=["cli", "amb_bootstrap"],
    packages=find_packages(include=["amb_cli*"]),
    install_requires=[
        "requests>=2.28.0"
    ],
    entry_points={
        "console_scripts": [
            "amb = amb_cli.cli:main",
        ],
    },
)

