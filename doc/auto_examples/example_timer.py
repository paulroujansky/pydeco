"""
============================================================================
Example: decorating specified methods of a custom class with timer decorator
============================================================================

This example shows how to decorate methods of a custom class with a timer
decorator.

"""
import time

from pydeco import MethodsDecorator

###############################################################################
# Create timer decorator


class Timer(object):
    """Timer decorator."""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, f):
        """Call function."""
        def wrapped_f(instance, *args, **kwargs):
            """Wrap input instance method with runtime measurement."""
            ts = time.time()
            result = f(instance, *args, **kwargs)
            te = time.time()
            print('[Log] runtime {!r} : {:2.2f} ms\n'.format(
                f.__name__, (te - ts) * 1000))
            return result
        return wrapped_f


###############################################################################
# Create custom class and decorate some of its methods with :class:`Timer`


@MethodsDecorator(mapping={Timer(): ['method_1', 'method_2']})
class MyClass():
    """Custom class."""

    def __init__(self, *args, **kwargs):
        pass

    def method_1(self, sleep=.01, **kwargs):
        print('Running \'method_1\' (sleep {:2.2f} ms)'.format(sleep * 1000))
        time.sleep(sleep)

    def method_2(self, sleep=.02, **kwargs):
        print('Running \'method_2\' (sleep {:2.2f} ms)'.format(sleep * 1000))
        time.sleep(sleep)

    def method_3(self, sleep=.03, **kwargs):
        print('Running \'method_3\' (sleep {:2.2f} ms)'.format(sleep * 1000))
        time.sleep(sleep)

###############################################################################
# Test

# instantiate the class
instance = MyClass()

# run methods
instance.method_1()
instance.method_2()
instance.method_3()
