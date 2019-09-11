"""
==============================================================================
Example: decorating specified methods of a custom class with custom decorators
==============================================================================

This example shows how to decorate methods of a custom class with custom
decorators.

"""
import time

from pydeco import Decorator, MethodsDecorator

###############################################################################
# Create timer decorator


class Timer(Decorator):
    """Timer decorator."""

    def __init__(self, *args, **kwargs):
        self.run = 0
        self.run_by_func = dict()
        self.total_runtime = 0
        Decorator.__init__(self, *args, **kwargs)

    def __repr__(self):
        """Return the string representation."""
        return ('Timer(run={}, run_by_func={}, total_runtime={:2.2f} ms)'
                .format(self.run, self.run_by_func, self.total_runtime))

    def wrapper(self, instance, func, *args, **kwargs):
        """Wrap input instance method with runtime measurement."""
        # increment run attributes
        self.run += 1
        if func.__name__ not in self.run_by_func:
            self.run_by_func[func.__name__] = 1
        else:
            self.run_by_func[func.__name__] += 1

        # save current time
        ts = time.time()

        # call `func` on inputs
        outs = func(instance, *args, **kwargs)

        # compute elapsed time
        te = time.time()
        runtime = (te - ts) * 1000
        # Update total runtime of timer
        self.total_runtime += runtime

        print('[Log] runtime {!r} : {:2.2f} ms'.format(func.__name__, runtime))

        # return outputs of `func`
        return outs

###############################################################################
# Create custom decorators


class Decorator1(Decorator):
    """Decorator 1."""

    def __init__(self, *args, **kwargs):
        Decorator.__init__(self, *args, **kwargs)

    def wrapper(self, instance, func, *args, **kwargs):
        """Wrap input instance method with the herebelow code."""
        print('[Decorator 1] -> decorating {}.{}'.format(
            instance._Wrapper__wrapped_class.__name__, func.__name__))
        return func(instance, *args, **kwargs)


class Decorator2(Decorator):
    """Decorator 2."""

    def __init__(self, *args, **kwargs):
        Decorator.__init__(self, *args, **kwargs)

    def wrapper(self, instance, func, *args, **kwargs):
        """Wrap input instance method with the herebelow code."""
        print('[Decorator 2] -> decorating {}.{}'.format(
            instance._Wrapper__wrapped_class.__name__, func.__name__))
        return func(instance, *args, **kwargs)

###############################################################################
# Create custom class

timer = Timer()


class MyClass():
    """Custom class."""

    def __init__(self, *args, **kwargs):
        pass

    @timer
    def method_1(self, *args, **kwargs):
        print('Run method 1')

    @timer
    def method_2(self, *args, **kwargs):
        print('Run method 2')

    @timer
    def method_3(self, *args, **kwargs):
        print('Run method 3')

###############################################################################
# Test

# Without custom decorators
# -----------------------------------------------------------------------------

# instantiate the class
instance = MyClass()

# run methods
instance.method_1()
instance.method_2()
instance.method_3()

# With custom decorators for the respective methods
# -----------------------------------------------------------------------------

# decorate the class
MyClass_deco = MethodsDecorator(
    mapping={
        Decorator1(): ['method_1', 'method_2'],
        Decorator2(): ['method_1', 'method_3']
    })(MyClass)

# instantiate the class
instance = MyClass_deco()

# run methods
instance.method_1()
instance.method_2()
instance.method_3()
