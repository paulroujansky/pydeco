"""Utils functions."""
import os
import sys
from ast import literal_eval
from inspect import isclass


def python_version():
    """Return Python version."""
    if 'TRAVIS' in os.environ and 'TRAVIS_PYTHON_VERSION' in os.environ:
        # Travis CI
        py_version = literal_eval(os.environ['TRAVIS_PYTHON_VERSION'])
    else:
        # Local
        version_info = sys.version_info
        py_version = float(version_info.major + version_info.minor / 10)

    return py_version


def is_wrapped(obj):
    """Return True if input object is wrapped."""
    cls = obj if isclass(obj) else obj.__class__

    return getattr(cls, '_Wrapper__decorated', False)


def wrapped_class(obj):
    """Return wrapped class if object is wrapped, `cls` otherwise."""
    cls = obj if isclass(obj) else obj.__class__

    return getattr(cls, '_Wrapper__wrapped_class', cls)


PYTHON_VERSION = python_version()
