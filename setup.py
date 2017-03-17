#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pkg_resources
from setuptools import find_packages
from setuptools import setup


install_requires = [
    'docopt>=0.6.2',
]


setup(
    name='docopt_utils',
    description='Helper functions and classes for docopt',
    author='King Chung Huang',
    packages=find_packages(),
    install_requires=install_requires,
    zip_safe=True
)
