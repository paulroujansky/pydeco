"""Test utils."""
from pydeco.utils import PYTHON_VERSION, is_wrapped
from pydeco.decorator import Decorator


def test_python_version():
    """Test Python version."""
    if PYTHON_VERSION < 3:
        raise OSError('`pydeco` compatible with Python 3.0 and higher only.')


def test_is_wrapped():
    """Test `is_wrapped` function."""
    objs = ['string', {'a': 1}, None, 3]

    for obj in objs:
        assert not is_wrapped(obj)
