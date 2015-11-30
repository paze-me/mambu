#!/usr/bin/env python

from setuptools import setup

setup(
    name='Mambu',
    version='0.0.5',
    description='Python module for Mambu API',
    author='Paze.me Limited',
    author_email='hansel.dunlop@paze.me',
    url='https://www.mambu.com',
    packages=['mambu', 'mambu.etc', 'mambu.tools'],
    install_requires=[
        'requests'
    ]
)
