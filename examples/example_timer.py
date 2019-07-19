"""
============================================================================
Example: decorating specified methods of a custom class with timer decorator
============================================================================

This example shows how to decorate methods of a custom class with a timer
decorator.

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
        result = func(instance, *args, **kwargs)

        # compute elapsed time
        te = time.time()
        runtime = (te - ts) * 1000
        # Update total runtime of timer
        self.total_runtime += runtime

        print('[Log] runtime {!r} : {:2.2f} ms'.format(func.__name__, runtime))

        # return outputs of `func`
        return result


###############################################################################
# Create custom class and decorate some of its methods with :class:`Timer`

# instantiate decorator
timer = Timer()


# create class :class:`MyClass` and decorate `method_1` and `method_2` with
# decorator `timer`
@MethodsDecorator(mapping={timer: ['method_1', 'method_2']})
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
# Run tests

# instantiate the class
instance = MyClass()

# run methods
instance.method_1()
instance.method_2()
instance.method_3()

print(timer)

# deactivate timer for all methods of linked decorated instances
timer.deactivate()

# run methods
instance.method_1()
instance.method_2()
instance.method_3()

print(timer)

# activate timer back for all methods of linked decorated instances
timer.activate()

# run methods
instance.method_1()
instance.method_2()
instance.method_3()

print(timer)
