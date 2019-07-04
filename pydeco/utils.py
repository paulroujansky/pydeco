"""Utils functions."""
import os
import sys
from ast import literal_eval


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


PYTHON_VERSION = python_version()
