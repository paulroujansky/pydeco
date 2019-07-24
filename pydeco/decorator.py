"""Decorator for class methods (compatible with Python 3.0 or higher).

The herebelow class :class:`MethodsDecorator` enables to decorate multiple
methods of a given class with custom decorators by simply decorating said class
with it. One then needs to specify, as a dictionary, which decorator is used to
decorate which methods.

"""
from functools import wraps
from abc import abstractmethod

from .utils import is_wrapped


class Decorator(object):
    """Decorator base class."""

    def __init__(self, *args, **kwargs):
        self.instances = []

    def flush_instances(self):
        """Flush instances."""
        self.instances = []

    @abstractmethod
    def wrapper(self, instance, func, *args, **kwargs):
        """Wrap func."""
        pass

    def activate(self):
        """Activate decorator for all methods of decorated instances."""
        for instance in self.instances:
            instance.activate_decorator(self.__class__.__name__)

    def deactivate(self):
        """Deactivate decorator for all methods of decorated instances."""
        for instance in self.instances:
            instance.deactivate_decorator(self.__class__.__name__)

    def is_active(self, instance):
        """Return True if decorator is active for input instance."""
        if instance not in self.instances:
            err = ('Current decorator does not decorate a method of input '
                   'class instance.')
            raise ValueError(err)
        if not is_wrapped(instance):
            return True
        else:
            return instance.is_decorator_active(self.__class__.__name__)

    def __call__(self, func):
        """Call."""
        @wraps(func)
        def _wrapped_func(instance, func, *args, **kwargs):
            """Call wrapper is decorator is active, otherwise call func."""
            if instance not in self.instances:
                self.instances.append(instance)

            if self.is_active(instance):
                # active decorator for the current func: wrap it
                # check if input is a bound method or not
                if hasattr(func, '__self__'):

                    # wrap func as it is a bound method
                    def func_(instance, *args, **kwargs):
                        return func(*args, **kwargs)

                    return self.wrapper(instance, func_, *args, **kwargs)
                else:
                    return self.wrapper(instance, func, *args, **kwargs)
            else:
                # inactive decorator for the current func
                return func(instance, *args, **kwargs)

        if hasattr(func, '__self__'):
            # input object is a method of an instance
            instance = func.__self__
            return lambda *args, **kwargs: \
                _wrapped_func(instance, func, *args, **kwargs)
        else:
            return lambda instance, *args, **kwargs: \
                _wrapped_func(instance, func, *args, **kwargs)


class MethodsDecorator(object):
    """Class that enables to decorate specific methods with given decorator.

    Parameters
    ----------
    mapping : dict
        Mapping containing decorators as key and methods (as str or a list of
        str) as values (ex: ``{Timer(): ['fit', 'predict']}``)

    Examples
    --------
    We assume here that a decorator named :class:`Timer` (used to compute
    running time of called functions) is already implemented. The below code
    applies such a decorator to the method :meth:`method_1` of class
    :class:`MyClass` so as to compute running time every time :meth:`method_1`
    is called.

    >>> @MethodsDecorator(mapping={Timer(): 'method_1'})
    >>> class MyClass():
    >>>
    >>>    def method_1(self, *args, **kwargs):
    >>>       return

    The "@" syntax is a proxy for the below implementation:

    >>> class MyClass():
    >>>
    >>>    def method_1(self, *args, **kwargs):
    >>>       return
    >>>
    >>> MyClass = MethodsDecorator(mapping={Timer(): 'method_1'})(MyClass)

    See the examples section for more insights on how to use
    :class:`MethodsDecorator`.

    """

    def __init__(self, mapping={}):

        self.mapping = mapping
        for decorator, methods in mapping.items():
            if not isinstance(methods, (tuple, list)):
                methods = [methods]
            assert callable(decorator)
            assert all([isinstance(method, str) for method in methods])
            self.mapping[decorator] = methods

    def __call__(self, cls):
        """Return wrapped input class with decorated methods."""
        mapping = self.mapping

        class MC(type):
            """Decorating methods for the input class with given decorator.

            Attributes
            ----------
            decorated : bool
                Indicates that current class is decorated.
            class_decorator : type
                Type of the class decorator used to decorate the current class.

            """

            def __init__(cls, name, bases, dict):

                for decorator, methods in self.mapping.items():
                    for method in methods:
                        if not hasattr(cls, method):
                            err = 'Input class has not method "{}"'.format(
                                method)
                            raise ValueError(err)
                        setattr(cls, method, decorator(getattr(cls, method)))

                super(MC, cls).__init__(name, bases, dict)

        global Wrapper

        class Wrapper(cls, metaclass=MC):
            """Wrapped class where each specified method is decorated."""

            __wrapped_class = cls  # base class
            __decorated = True  # indicates that the class is decorated
            __wrapper = self.__class__  # type of class decorator
            __decorator_mapping = mapping  # decorator mapping

            def __init__(self, *args, **kwargs):
                self.decorators = {
                    decorator.__class__.__name__: decorator
                    for decorator in mapping.keys()
                }
                self.active_decorators = \
                    {decorator: True for decorator in self.decorators}
                cls.__init__(self, *args, **kwargs)

            def _check_decorator_name(self, name):
                if name not in self.decorators:
                    err = ('Could not find decorator "{}". Available '
                           'decorators: {}'.format(
                               name, list(self.decorators.keys())))
                    raise ValueError(err)

            def is_decorator_active(self, name):
                """Check if input decorator is active."""
                self._check_decorator_name(name)
                return self.active_decorators[name]

            def activate_decorator(self, name):
                """Activate decorator."""
                self._check_decorator_name(name)
                self.active_decorators[name] = True

            def deactivate_decorator(self, name):
                """Deactivate decorator."""
                self._check_decorator_name(name)
                self.active_decorators[name] = False

        # Updating wrapped class name and documentation
        Wrapper.__name__ = 'Wrapped(' + cls.__name__ + ')'
        Wrapper.__doc__ = cls.__doc__

        return Wrapper
