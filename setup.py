#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='linnskuconvert',
    version='1.0',
    description='Convertes between Linnworks and Channel SKUs',
    author='Luke Shiner',
    install_requires=['pyperclip', 'tabler'],
    packages=find_packages(),
    )
