"""
==============================================================================
Example: decorating specified methods of a custom class with custom decorators
==============================================================================

This example shows how to decorate methods of a custom class with custom
decorators.

"""
from pydeco import Decorator, MethodsDecorator

###############################################################################
# Create custom decorators


class Decorator1(Decorator):
    """Decorator 1."""

    def __init__(self, *args, **kwargs):
        Decorator.__init__(self, *args, **kwargs)

    def wrapper(self, instance, func, *args, **kwargs):
        """Wrap input instance method with the herebelow code."""
        print('[Decorator 1] -> decorating...')
        return func(instance, *args, **kwargs)


class Decorator2(Decorator):
    """Decorator 2."""

    def __init__(self, *args, **kwargs):
        Decorator.__init__(self, *args, **kwargs)

    def wrapper(self, instance, func, *args, **kwargs):
        """Wrap input instance method with the herebelow code."""
        print('[Decorator 2] -> decorating...')
        return func(instance, *args, **kwargs)

###############################################################################
# Create custom class


class MyClass():
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
# Test

# Without decorators
# -----------------------------------------------------------------------------

# instantiate the class
instance = MyClass()

# run methods
instance.method_1()
instance.method_2()
instance.method_3()

# With decorators for the respective methods
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
