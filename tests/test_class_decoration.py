"""Test class decoration."""
import os
import pickle as pkl
import sys
from copy import deepcopy

import pytest
from joblib import Parallel, delayed

from pydeco import MethodsDecorator
from pydeco.utils import PYTHON_VERSION


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
            # print('[Decorator 1] -> decorating...')
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
            # print('[Decorator 2] -> decorating...')
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


# Define custom function
# ----------------------

def myfunc(i, instance, copy, verbose=True):
    """In the title."""
    # keep track of iterations within each PID
    pid = os.getpid()  # get current process ID
    if pid not in iter_process:
        iter_process[pid] = 0

    if verbose:
        print('Iter {}: PID={}\n'.format(i + 1, pid))

    assert (instance.cnt_dec_1 == iter_process[pid] * 2 and
            instance.cnt_dec_2 == iter_process[pid])

    # run methods
    instance.method_1()
    instance.method_2()
    instance.method_3()

    assert (instance.cnt_dec_1 == (iter_process[pid] + 1) * 2 and
            instance.cnt_dec_2 == iter_process[pid] + 1)

    # increment iter within current PID
    iter_process[pid] += 1

    return


# Tests
# ----------------------------------------------------------------------------

def test_class_decoration(verbose=False):
    """Test class decoration."""
    # instantiate the class
    instance = MyClass()

    assert repr(instance) == 'MyClass(cnt_dec_1=0, cnt_dec_1=0)'

    # run methods
    instance.method_1()
    instance.method_2()
    instance.method_3()

    assert instance.cnt_dec_1 == 0 and instance.cnt_dec_2 == 0

    # decorate methods
    MyClass_deco = MethodsDecorator(
        mapping={
            Decorator1(name='decorator_1'): ['method_1', 'method_2'],
            Decorator2(name='decorator_2'): 'method_1'
        })(MyClass)

    # instantiate the class
    instance = MyClass_deco()

    assert repr(instance) == 'Wrapped(MyClass)(cnt_dec_1=0, cnt_dec_1=0)'

    # run methods
    instance.method_1()
    instance.method_2()
    instance.method_3()

    assert repr(instance) == 'Wrapped(MyClass)(cnt_dec_1=2, cnt_dec_1=1)'
    assert instance.cnt_dec_1 == 2 and instance.cnt_dec_2 == 1

    # decorate methods
    with pytest.raises(ValueError,
                       match='Input class has not method "method_4"'):
        MyClass_deco = MethodsDecorator(
            mapping={
                Decorator1(name='decorator_1'): ['method_1', 'method_2'],
                Decorator2(name='decorator_2'): ['method_1', 'method_4']
            })(MyClass)


def test_deepcopying():
    """Test deepcopying."""
    # decorate methods of base class
    MyClass_deco = MethodsDecorator(
        mapping={
            Decorator1(name='decorator_1'): ['method_1', 'method_2'],
            Decorator2(name='decorator_2'): 'method_1'
        })(MyClass)

    # instantiate the decorated class
    instance = MyClass_deco()
    # create a deepcopy of `instance`
    instance_2 = deepcopy(instance)

    assert instance != instance_2

    assert instance.cnt_dec_1 == 0 and instance.cnt_dec_2 == 0
    assert instance_2.cnt_dec_1 == 0 and instance_2.cnt_dec_2 == 0

    # run methods for `instance`
    instance.method_1()
    instance.method_2()
    instance.method_3()

    # check that internal variables of `instance`' have changed but not of
    # `instance_2`
    assert instance.cnt_dec_1 == 2 and instance.cnt_dec_2 == 1
    assert instance_2.cnt_dec_1 == 0 and instance_2.cnt_dec_2 == 0


def test_pickling():
    """Test pickling."""
    # decorate methods of base class
    MyClass_deco = MethodsDecorator(
        mapping={
            Decorator1(name='decorator_1'): ['method_1', 'method_2'],
            Decorator2(name='decorator_2'): 'method_1'
        })(MyClass)

    # instantiate the decorated class
    instance = MyClass_deco()

    # Save instance as a pickle object
    tmp = pkl.dumps(instance)
    # Load pickled module
    instance_2 = pkl.loads(tmp)

    assert instance != instance_2

    assert instance.cnt_dec_1 == 0 and instance.cnt_dec_2 == 0
    assert instance_2.cnt_dec_1 == 0 and instance_2.cnt_dec_2 == 0

    # run methods for `instance`
    instance.method_1()
    instance.method_2()
    instance.method_3()

    # check that internal variables of `instance`' have changed but not of
    # `instance_2`
    assert instance.cnt_dec_1 == 2 and instance.cnt_dec_2 == 1
    assert instance_2.cnt_dec_1 == 0 and instance_2.cnt_dec_2 == 0

    # run methods
    instance_2.method_1()
    instance_2.method_2()
    instance_2.method_3()

    assert instance.cnt_dec_1 == 2 and instance.cnt_dec_2 == 1
    assert instance_2.cnt_dec_1 == 2 and instance_2.cnt_dec_2 == 1


@pytest.mark.parametrize(argnames='copy', argvalues=(True, False))
@pytest.mark.parametrize(argnames='n_iter', argvalues=(10, 20, 30))
def test_parallelizing(copy, n_iter, n_jobs=1, verbose=True):
    """Test parallelizing."""
    # store number of iterations for each process
    global iter_process
    iter_process = dict()

    # decorate methods of base class
    MyClass_deco = MethodsDecorator(
        mapping={
            Decorator1(name='decorator_1'): ['method_1', 'method_2'],
            Decorator2(name='decorator_2'): 'method_1'
        })(MyClass)

    # instantiate the decorated class
    instance = MyClass_deco()

    # create a "reference" instance
    instance_ref = deepcopy(instance)

    # run parallel jobs
    if verbose:
        print('Parallelizing: {} iterations distributed on {} jobs'.format(
            n_iter, n_jobs))

    backend = 'multiprocessing' if copy else 'threading'
    print(copy, type(copy), backend)

    with Parallel(n_jobs=n_jobs,
                  verbose=verbose,
                  pre_dispatch=True,
                  backend=backend) as parallel:
        _ = parallel(
            delayed(myfunc)(i, instance, copy=copy, verbose=verbose)
            for i in range(n_iter)
        )

    # check that instance has not changed if copy is True
    if copy and n_jobs > 1:
        assert instance.cnt_dec_1 == 0 and instance.cnt_dec_2 == 0
    else:
        assert (instance.cnt_dec_1 == (n_iter * 2) and
                instance.cnt_dec_2 == n_iter)
    # check that reference instance has not changed
    assert instance_ref.cnt_dec_1 == 0 and instance_ref.cnt_dec_2 == 0


if __name__ == "__main__":
    pytest.main([__file__])
