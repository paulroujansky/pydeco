#! /usr/bin/env python
#
from setuptools import setup, find_packages

# platform specific dependency
exclude = ['data', 'contrib', 'doc', 'tests']

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='pydeco',
    description='Python Class Decorator',
    url='https://github.com/paulroujansky/pydeco',
    author='P Roujansky',
    author_email='paul@roujansky.eu',
    license='UNLICENSED',
    version='0.1',
    include_package_data=True,
    install_requires=requirements,
    packages=find_packages(exclude=exclude),
    zip_safe=False)
