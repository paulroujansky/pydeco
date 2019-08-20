"""Test Decorator class."""
import os
import pickle as pkl
import sys
from copy import deepcopy

import pytest
from joblib import Parallel, delayed

from pydeco import Decorator
from pydeco.decorator import unregister, unregister_all
from pydeco.utils import PYTHON_VERSION

global logs
logs = []


# Utils
# -----------------------------------------------------------------------------

# Defining custom func decorators
# -------------------------------

class Decorator1(Decorator):
    """Decorator 1."""

    def __init__(self, name, *args, **kwargs):
        self.name = name
        Decorator.__init__(self)

    def __repr__(self):
        """Return the string representation."""
        return '{} (id={})'.format(self.__class__.__name__, id(self))

    def wrapper(self, instance, func, *args, **kwargs):
        """Wrap input instance method."""
        logs.append({
            self.__class__.__name__: id(self),
            instance.__class__.__name__: id(instance)
        })
        # print('[Decorator 1] -> decorating...')
        instance.cnt_dec_1 += 1  # updating instance cnt for decorator
        return func(instance, *args, **kwargs)


class Decorator2(Decorator):
    """Decorator 2."""

    def __init__(self, name, *args, **kwargs):
        self.name = name
        Decorator.__init__(self)

    def __repr__(self):
        """Return the string representation."""
        return '{} (id={})'.format(self.__class__.__name__, id(self))

    def wrapper(self, instance, func, *args, **kwargs):
        """Wrap input instance method."""
        logs.append({
            self.__class__.__name__: id(self),
            instance.__class__.__name__: id(instance)
        })
        # print('[Decorator 1] -> decorating...')
        instance.cnt_dec_2 += 1  # updating instance cnt for decorator
        return func(instance, *args, **kwargs)


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

def test_decoration(verbose=False):
    """Test decoration."""
    global logs
    logs = []

    # instantiate the class
    instance = MyClass()

    # instantiate the decorators
    decorator_1 = Decorator1(name='decorator_1')
    decorator_2 = Decorator2(name='decorator_2')

    assert repr(instance) == 'MyClass(cnt_dec_1=0, cnt_dec_1=0)'

    # run methods
    instance.method_1()
    instance.method_2()
    instance.method_3()

    err = (
        'Current decorator does not decorate a method of input class instance.'
    )
    with pytest.raises(ValueError, match=err):
        assert (not decorator_1.is_active(instance) and
                not decorator_2.is_active(instance))
    assert instance.cnt_dec_1 == 0 and instance.cnt_dec_2 == 0

    # decorate methods with given decorators
    MyClass.method_1 = decorator_1(MyClass.method_1)
    MyClass.method_1 = decorator_2(MyClass.method_1)
    MyClass.method_2 = decorator_1(MyClass.method_2)

    # instantiate the class
    instance = MyClass()

    err = (
        'Current decorator does not decorate a method of input class instance.'
    )
    with pytest.raises(ValueError, match=err):
        assert (not decorator_1.is_active(instance) and
                not decorator_2.is_active(instance))
    assert repr(instance) == 'MyClass(cnt_dec_1=0, cnt_dec_1=0)'

    # run methods
    instance.method_1()
    instance.method_2()
    instance.method_3()

    assert decorator_1.is_active(instance) and decorator_2.is_active(instance)
    assert instance.cnt_dec_1 == 2 and instance.cnt_dec_2 == 1


if __name__ == "__main__":
    # pytest.main([__file__])
    test_decoration()
