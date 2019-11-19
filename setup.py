#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="itty3",
    version="1.0.0-beta-1",
    description=(
        "The itty-bitty Python web framework... "
        "**Now Rewritten For Python 3!**"
    ),
    author="Daniel Lindsley",
    author_email="daniel@toastdriven.com",
    url="http://github.com/toastdriven/itty3/",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    py_modules=["itty3"],
    requires=[],
    install_requires=[],
    tests_require=["pytest",],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
