"""Example: decorating a class with custom decorators."""
from pydeco import DecorateMethods


class Decorator1(object):
    """Decorator 1."""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, f):
        """Call."""
        def wrapped_f(instance, *args, **kwargs):
            """Wrap input instance method with runtime measurement."""
            print('[Decorator 1] -> decorating...')
            return f(instance, *args, **kwargs)
        return wrapped_f


class Decorator2(object):
    """Decorator 2."""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, f):
        """Call."""
        def wrapped_f(instance, *args, **kwargs):
            """Wrap input instance method with runtime measurement."""
            print('[Decorator 2] -> decorating...')
            return f(instance, *args, **kwargs)
        return wrapped_f


class A():
    """Custom class."""

    def __init__(self, *args, **kwargs):
        pass

    def method_1(self, *args, **kwargs):
        print('Run method 1')

    def method_2(self, *args, **kwargs):
        print('Run method 2')

    def method_3(self, *args, **kwargs):
        print('Run method 3')


a = A()

a.method_1()
a.method_2()
a.method_3()

# decorate methods
decorated_A = DecorateMethods(
    mapping={
        Decorator1(): ['method_1', 'method_2'],
        Decorator2(): ['method_1', 'method_3']
    })(A)

a = decorated_A()

a.method_1()
a.method_2()
a.method_3()
