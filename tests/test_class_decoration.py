"""Test class decoration."""
import os
import pickle as pkl
import sys
from copy import deepcopy

import pytest
from joblib import Parallel, delayed
from sklearn.base import BaseEstimator

from pydeco import Decorator, MethodsDecorator
from pydeco.utils.register import unregister_all
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
        return '{}[id={}]'.format(self.__class__.__name__, id(self))

    def wrapper(self, instance, func, *args, **kwargs):
        """Wrap input instance method with runtime measurement."""
        logs.append({
            self.__class__.__name__: id(self),
            instance.__class__.__name__: id(instance)
        })
        print('{} decorating {}[id={}]'.format(self, instance, id(instance)))
        instance.cnt_dec_1 += 1  # updating instance cnt for decorator
        return func(instance, *args, **kwargs)


class Decorator2(Decorator):
    """Decorator 2."""

    def __init__(self, name, *args, **kwargs):
        self.name = name
        Decorator.__init__(self)

    def __repr__(self):
        """Return the string representation."""
        return '{}[id={}]'.format(self.__class__.__name__, id(self))

    def wrapper(self, instance, func, *args, **kwargs):
        """Wrap input instance method with runtime measurement."""
        logs.append({
            self.__class__.__name__: id(self),
            instance.__class__.__name__: id(instance)
        })
        print('{} decorating {}[id={}]'.format(self, instance, id(instance)))
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


class MyEstimator(BaseEstimator):
    """Custom sickit-learn esimator."""

    def __init__(self, obj=None):
        self.obj = obj

    def method_1(self, *args, **kwargs):
        # print('Run method 1')
        self.obj.method_1()

    def method_2(self, *args, **kwargs):
        # print('Run method 2')
        self.obj.method_2()

    def method_3(self, *args, **kwargs):
        # print('Run method 3')
        self.obj.method_3()

    def __repr__(self):
        return '{}.{}(cnt_dec_1={}, cnt_dec_1={})'.format(
            self.__class__.__name__, self.obj.__class__.__name__,
            self.obj.cnt_dec_1, self.obj.cnt_dec_2)


# Define custom function
# ----------------------

def myfunc(i, instance, copy, iter_process, verbose=True):
    """In the title."""
    print('MYFUNC')
    # keep track of iterations within each PID
    pid = os.getpid()  # get current process ID

    if verbose:
        print('Iter {}: PID={}\n'.format(i + 1, pid))

    # run methods
    instance.method_1()
    instance.method_2()
    instance.method_3()

    return (pid, id(instance))


# Tests
# ----------------------------------------------------------------------------

def test_class_decoration(verbose=False):
    """Test class decoration."""
    from pydeco.utils.parser import CONFIG
    CONFIG['N_DISPATCH'] = None

    unregister_all()

    global logs
    logs = []

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

    unregister_all()


def test_deepcopying(verbose=True):
    """Test deepcopying."""
    from pydeco.utils.parser import CONFIG
    CONFIG['N_DISPATCH'] = 1

    unregister_all()

    global logs
    logs = []

    # decorate methods of base class
    MyClass_deco = MethodsDecorator(
        mapping={
            Decorator1(name='decorator_1'): ['method_1', 'method_2'],
            Decorator2(name='decorator_2'): 'method_1'
        })(MyClass)

    # instantiate the decorated class
    instance = MyClass_deco()

    if verbose:
        print('Before deepcopy...\n' + '-' * 18)
        for inst in [instance]:
            print('Instance: {} (id={})'.format(inst, id(inst)))
            print('Mapping:')
            print(inst._decorator_mapping)
            print('Decorators')
            for deco_name, deco in inst.decorators.items():
                print('\t Decorator: {}'.format(deco))
            print('\n')

    # create a deepcopy of `instance`
    instance_2 = deepcopy(instance)

    if verbose:
        print('After deepcopy...\n' + '-' * 17)
        for inst in [instance, instance_2]:
            print('Instance: {} (id={})'.format(inst, id(inst)))
            print('Mapping:')
            print(inst._decorator_mapping)
            print('Decorators')
            for deco_name, deco in inst.decorators.items():
                print('\t Decorator: {}'.format(deco))
            print('\n')

    # check that `instance` and `instance_2` are distinct objects
    assert instance is not instance_2
    # check that decorators of `instance` and `instance_2` are distinct objects
    for (deco1_name, deco1), (deco2_name, deco2) in zip(
            instance.decorators.items(), instance_2.decorators.items()):
        assert deco1 is not deco2

    assert instance.cnt_dec_1 == 0 and instance.cnt_dec_2 == 0
    assert instance_2.cnt_dec_1 == 0 and instance_2.cnt_dec_2 == 0

    assert instance.cnt_dec_1 == 0 and instance.cnt_dec_2 == 0
    assert instance_2.cnt_dec_1 == 0 and instance_2.cnt_dec_2 == 0

    # run methods for `instance`
    # run methods
    instance_2.method_1()
    instance_2.method_2()
    instance_2.method_3()

    for j, entry in enumerate(logs):
        assert entry['Wrapped2(MyClass)'] == id(instance_2)
        if j == 0:
            assert (entry['Decorator2'] ==
                    id(instance_2.decorators['Decorator2']))
        elif j == 1:
            assert (entry['Decorator1'] ==
                    id(instance_2.decorators['Decorator1']))
        elif j == 2:
            assert (entry['Decorator1'] ==
                    id(instance_2.decorators['Decorator1']))

    # check that internal variables of `instance`' have changed but not of
    # `instance_2`
    assert instance.cnt_dec_1 == 0 and instance.cnt_dec_2 == 0
    assert instance_2.cnt_dec_1 == 2 and instance_2.cnt_dec_2 == 1

    # run methods
    instance.method_1()
    instance.method_2()
    instance.method_3()

    for j, entry in enumerate(logs):
        if j < 3:
            assert entry['Wrapped2(MyClass)'] == id(instance_2)
            if j == 0:
                assert (entry['Decorator2'] ==
                        id(instance_2.decorators['Decorator2']))
            elif j == 1:
                assert (entry['Decorator1'] ==
                        id(instance_2.decorators['Decorator1']))
            elif j == 2:
                assert (entry['Decorator1'] ==
                        id(instance_2.decorators['Decorator1']))
        else:
            assert entry['Wrapped(MyClass)'] == id(instance)
            if j == 3:
                assert (entry['Decorator2'] ==
                        id(instance.decorators['Decorator2']))
            elif j == 4:
                assert (entry['Decorator1'] ==
                        id(instance.decorators['Decorator1']))
            elif j == 5:
                assert (entry['Decorator1'] ==
                        id(instance.decorators['Decorator1']))

    assert instance.cnt_dec_1 == 2 and instance.cnt_dec_2 == 1
    assert instance_2.cnt_dec_1 == 2 and instance_2.cnt_dec_2 == 1

    unregister_all()


@pytest.mark.parametrize('dcopy', (False, True))
def test_pickling(dcopy, verbose=True):
    """Test pickling."""
    from pydeco.utils.parser import CONFIG
    CONFIG['N_DISPATCH'] = 1

    unregister_all()

    global logs
    logs = []

    # decorate methods of base class
    MyClass_deco = MethodsDecorator(
        mapping={
            Decorator1(name='decorator_1'): ['method_1', 'method_2'],
            Decorator2(name='decorator_2'): 'method_1'
        })(MyClass)

    # instantiate the decorated class
    instance = MyClass_deco()

    if verbose:
        print('Before pickling...\n' + '-' * 18)
        for inst in [instance]:
            print('Instance: {} (id={})'.format(inst, id(inst)))
            print('Mapping:')
            print(inst._decorator_mapping)
            print('Decorators')
            for deco_name, deco in inst.decorators.items():
                print('\t Decorator: {}'.format(deco))
            print('\n')

    instance_ = deepcopy(instance) if dcopy else instance

    # Save instance as a pickle object
    tmp = pkl.dumps(instance_)

    # Load pickled module
    instance_2 = pkl.loads(tmp)

    if verbose:
        print('After pickling...\n' + '-' * 17)
        for inst in [instance, instance_2]:
            print('Instance: {} (id={})'.format(inst, id(inst)))
            print('Mapping:')
            print(inst._decorator_mapping)
            print('Decorators')
            for deco_name, deco in inst.decorators.items():
                print('\t Decorator: {}'.format(deco))
            print('\n')

    # check that `instance` and `instance_2` are distinct objects
    assert instance is not instance_2
    # check that decorators of `instance` and `instance_2` are distinct objects
    for (deco1_name, deco1), (deco2_name, deco2) in zip(
            instance.decorators.items(), instance_2.decorators.items()):
        assert deco1 is not deco2

    assert instance.cnt_dec_1 == 0 and instance.cnt_dec_2 == 0
    assert instance_2.cnt_dec_1 == 0 and instance_2.cnt_dec_2 == 0

    # run methods for `instance`
    # run methods
    instance_2.method_1()
    instance_2.method_2()
    instance_2.method_3()

    new_classname = 'Wrapped2(MyClass)' if dcopy else 'Wrapped(MyClass)'

    for j, entry in enumerate(logs):
        assert entry[new_classname] == id(instance_2)
        if j == 0:
            assert (entry['Decorator2'] ==
                    id(instance_.decorators['Decorator2']))
        elif j == 1:
            assert (entry['Decorator1'] ==
                    id(instance_.decorators['Decorator1']))
        elif j == 2:
            assert (entry['Decorator1'] ==
                    id(instance_.decorators['Decorator1']))

    # check that internal variables of `instance`' have changed but not of
    # `instance_2`
    assert instance.cnt_dec_1 == 0 and instance.cnt_dec_2 == 0
    assert instance_2.cnt_dec_1 == 2 and instance_2.cnt_dec_2 == 1

    # run methods
    instance.method_1()
    instance.method_2()
    instance.method_3()

    for j, entry in enumerate(logs):
        if j < 3:
            assert entry[new_classname] == id(instance_2)
            if j == 0:
                assert (entry['Decorator2'] ==
                        id(instance_.decorators['Decorator2']))
            elif j == 1:
                assert (entry['Decorator1'] ==
                        id(instance_.decorators['Decorator1']))
            elif j == 2:
                assert (entry['Decorator1'] ==
                        id(instance_.decorators['Decorator1']))
        else:
            assert entry['Wrapped(MyClass)'] == id(instance)
            if j == 3:
                assert (entry['Decorator2'] ==
                        id(instance.decorators['Decorator2']))
            elif j == 4:
                assert (entry['Decorator1'] ==
                        id(instance.decorators['Decorator1']))
            elif j == 5:
                assert (entry['Decorator1'] ==
                        id(instance.decorators['Decorator1']))

    assert instance.cnt_dec_1 == 2 and instance.cnt_dec_2 == 1
    assert instance_2.cnt_dec_1 == 2 and instance_2.cnt_dec_2 == 1

    unregister_all()


@pytest.mark.parametrize(argnames='copy', argvalues=(True, False))
@pytest.mark.parametrize(argnames='n_iter', argvalues=(10, 20, 30))
def test_parallelizing(copy, n_iter, n_jobs=1, verbose=True):
    """Test parallelizing."""
    from pydeco.utils.parser import CONFIG
    CONFIG['N_DISPATCH'] = n_iter + 1

    unregister_all()

    global logs
    logs = []

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

    if verbose:
        print('Before deepcopy...\n' + '-' * 18)
        for inst in [instance, instance_ref]:
            print('Instance: {} (id={})'.format(inst, id(inst)))
            print('Mapping:')
            print(inst._decorator_mapping)
            print('Decorators')
            for deco_name, deco in inst.decorators.items():
                print('\t Decorator: {}'.format(deco))
            print('\n')

    # run parallel jobs
    if verbose:
        print('Parallelizing: {} iterations distributed on {} jobs'.format(
            n_iter, n_jobs))

    backend = 'multiprocessing' if copy else 'threading'

    with Parallel(n_jobs=n_jobs,
                  verbose=verbose,
                  pre_dispatch='all',
                  backend=backend) as parallel:
        res = parallel(
            delayed(myfunc)(i, deepcopy(instance), copy=copy, verbose=verbose,
                            iter_process=iter_process)
            for i in range(n_iter)
        )

    unregister_all()


if __name__ == "__main__":
    pytest.main([__file__])
