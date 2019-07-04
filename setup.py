#! /usr/bin/env python

# Standard library modules.
from setuptools import setup, find_packages
import codecs
import os
import re
import sys

# platform specific dependency
exclude = ['data', 'contrib', 'doc', 'tests']

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


def get_absolute_path(*args):
    """Transform relative pathnames into absolute pathnames."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)


def get_contents(*args):
    """Get the contents of a file relative to the source distribution dir."""
    with codecs.open(get_absolute_path(*args), 'r', 'UTF-8') as handle:
        return handle.read()


def get_version(*args):
    """Extract the version number from a Python module."""
    contents = get_contents(*args)
    metadata = dict(re.findall('__([a-z]+)__ = [\'"]([^\'"]+)', contents))
    return metadata['version']


setup(
    name='pydeco',
    version=get_version('pydeco', '__init__.py'),
    python_requires='>=3',
    description='Python Class Methods Decorator',
    url='https://github.com/paulroujansky/pydeco',
    author='Paul Roujansky',
    long_description=get_contents('README.rst'),
    long_description_content_type='text/x-rst',
    author_email='paul@roujansky.eu',
    license='MIT',
    test_suite='pydeco.tests',
    install_requires=requirements,
    packages=find_packages(exclude=exclude),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False)
