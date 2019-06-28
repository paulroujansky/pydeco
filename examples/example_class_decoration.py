"""
==============================================================================
Example: decorating specified methods of a custom class with custom decorators
==============================================================================

This example shows how to decorate methods of a custom class with custom
decorators.

"""
from pydeco import DecorateMethods

###############################################################################
# Create custom decorators


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

###############################################################################
# Create custom class


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

###############################################################################
# Call methods

# Without decorators
# -----------------------------------------------------------------------------

# instantiate the class
a = A()

# run methods
a.method_1()
a.method_2()
a.method_3()

# With decorators for the respective methods
# -----------------------------------------------------------------------------

# decorate the class
decorated_A = DecorateMethods(
    mapping={
        Decorator1(): ['method_1', 'method_2'],
        Decorator2(): ['method_1', 'method_3']
    })(A)

# instantiate the class
a = decorated_A()

# run methods
a.method_1()
a.method_2()
a.method_3()
