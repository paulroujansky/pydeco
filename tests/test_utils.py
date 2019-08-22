"""Test utils."""
import pytest

from pydeco import Decorator, MethodsDecorator
from pydeco.utils import PYTHON_VERSION, is_wrapped, wrapped_class
from pydeco.utils.register import (assign, get_registered_wrappers_classnames,
                                   get_unassigned_wrappers_classnames,
                                   unassign, unregister, unregister_all)

# Utils
# -----------------------------------------------------------------------------

# Defining custom func decorators
# -------------------------------

class Decorator1(object):
    """Decorator 1."""

    def __init__(self, name, *args, **kwargs):
        self.name = name

    def __call__(self, f):
        """Call."""
        def wrapped_f(instance, *args, **kwargs):
            """Wrap input instance method with runtime measurement."""
            instance.cnt_dec_1 += 1  # updating instance cnt for decorator
            return f(instance, *args, **kwargs)
        return wrapped_f


class Decorator2(object):
    """Decorator 2."""

    def __init__(self, name, *args, **kwargs):
        self.name = name

    def __call__(self, f):
        """Call."""
        def wrapped_f(instance, *args, **kwargs):
            """Wrap input instance method with runtime measurement."""
            instance.cnt_dec_2 += 1  # updating instance cnt for decorator
            return f(instance, *args, **kwargs)
        return wrapped_f


# Defining custom processing class
# --------------------------------

class MyClass():
    """Custom class."""

    def __init__(self, *args, **kwargs):
        self.cnt_dec_1 = 0
        self.cnt_dec_2 = 0

    def method_1(self, *args, **kwargs):
        # print('Run method 1')
        pass

    def method_2(self, *args, **kwargs):
        # print('Run method 2')
        pass

    def method_3(self, *args, **kwargs):
        # print('Run method 3')
        pass

    def __repr__(self):
        return '{}(cnt_dec_1={}, cnt_dec_1={})'.format(
            self.__class__.__name__, self.cnt_dec_1, self.cnt_dec_2)


# Tests
# ----------------------------------------------------------------------------

def test_python_version():
    """Test Python version."""
    if PYTHON_VERSION < 3:
        raise OSError('`pydeco` compatible with Python 3.0 and higher only.')


def test_is_wrapped():
    """Test `is_wrapped` function."""
    unregister_all()
    # instantiate the base class
    instance = MyClass()

    # decorate methods
    MyClass_deco = MethodsDecorator(
        mapping={
            Decorator1(name='decorator_1'): ['method_1', 'method_2'],
            Decorator2(name='decorator_2'): 'method_1'
        })(MyClass)

    # instantiate the wrapped class
    instance_2 = MyClass_deco()

    # list of objects to check
    objs = ['string', {'a': 1}, None, 3, list, dict, int, str, Decorator]

    # check that hereabove objects (instances and classes) are not wrapped
    for obj in objs:
        assert not is_wrapped(obj)

    # check that :class:`MyClass` is not wrapped
    assert not is_wrapped(MyClass)
    # check that :class:`MyClass` instance `instance` is not wrapped
    assert not is_wrapped(instance)

    # check that :class:`MyClass_deco` is wrapped
    assert is_wrapped(MyClass_deco)
    # check that :class:`MyClass_deco` instance `instance_2` is wrapped
    assert is_wrapped(instance_2)


def test_wrapped_class():
    """Test `wrapped_class` function."""
    # instantiate the base class
    instance = MyClass()

    assert wrapped_class(instance) is MyClass

    # decorate methods
    MyClass_deco = MethodsDecorator(
        mapping={
            Decorator1(name='decorator_1'): ['method_1', 'method_2'],
            Decorator2(name='decorator_2'): 'method_1'
        })(MyClass)

    # instantiate the wrapped class
    instance_2 = MyClass_deco()

    assert wrapped_class(instance_2) is MyClass


@pytest.mark.parametrize('n_dispatch', (0, 2, 5, 10))
def test_class_registration(n_dispatch):
    """Test class registration."""
    # instantiate the base class
    unregister_all()
    from pydeco.utils.parser import CONFIG
    CONFIG['N_DISPATCH'] = n_dispatch

    registered_wrappers = get_registered_wrappers_classnames()
    assert len(registered_wrappers) == 0
    with pytest.raises(ValueError, match='No assigned wrapper found.'):
        unassigned_wrappers = get_unassigned_wrappers_classnames('MyClass')

    instance = MyClass()

    # decorate methods
    MyClass_deco = MethodsDecorator(
        mapping={
            Decorator1(name='decorator_1'): ['method_1', 'method_2'],
            Decorator2(name='decorator_2'): 'method_1'
        })(MyClass)

    registered_wrappers = get_registered_wrappers_classnames()
    assert len(registered_wrappers) == n_dispatch + 1
    unassigned_wrappers = get_unassigned_wrappers_classnames('MyClass')
    assert len(unassigned_wrappers) == n_dispatch + 1

    # instantiate the wrapped class
    instance_2 = MyClass_deco()

    registered_wrappers = get_registered_wrappers_classnames()
    assert len(registered_wrappers) == n_dispatch + 1

    if n_dispatch == 0:
        with pytest.raises(ValueError, match='No assigned wrapper found.'):
            unassigned_wrappers = get_unassigned_wrappers_classnames('MyClass')
    else:
        unassigned_wrappers = get_unassigned_wrappers_classnames('MyClass')
        assert len(unassigned_wrappers) == n_dispatch
        assert 'Wrapped(MyClass)' not in unassigned_wrappers

    from copy import deepcopy
    # create a copy of "instance_2"
    if n_dispatch == 0:
        with pytest.raises(ValueError, match='No assigned wrapper found.'):
            instance_3 = deepcopy(instance_2)
    else:
        instance_3 = deepcopy(instance_2)

    registered_wrappers = get_registered_wrappers_classnames()
    assert len(registered_wrappers) == n_dispatch + 1

    if n_dispatch != 0:
        unassigned_wrappers = get_unassigned_wrappers_classnames('MyClass')
        assert len(unassigned_wrappers) == n_dispatch - 1
        assert 'Wrapped(MyClass)' not in unassigned_wrappers
        assert 'Wrapped2(MyClass)' not in unassigned_wrappers

    # Unregistering "instance_2"
    unregister(instance_2.__class__)
    registered_wrappers = get_registered_wrappers_classnames()
    assert len(registered_wrappers) == n_dispatch
    assert 'Wrapped(MyClass)' not in registered_wrappers
    if n_dispatch != 0:
        unassigned_wrappers = get_unassigned_wrappers_classnames('MyClass')
        assert len(unassigned_wrappers) == n_dispatch - 1
        assert 'Wrapped(MyClass)' not in unassigned_wrappers
        assert 'Wrapped2(MyClass)' not in unassigned_wrappers


if __name__ == "__main__":
    pytest.main([__file__])
