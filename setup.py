#!/usr/bin/env python

from setuptools import setup

__version__ = '0.0.20'

setup(
    name='Mambu',
    version=__version__,
    description='Python module for Mambu API',
    author='Paze.me Limited',
    author_email='hansel.dunlop@paze.me',
    url='https://www.mambu.com',
    packages=['mambu', 'mambu.etc', 'mambu.tools'],
    package_data={'mambu': ['etc/*.yaml']},
    install_requires=[
        'requests'
    ]
)
