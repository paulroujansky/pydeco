"""Decorator for class methods (compatible with Python 3.0 or higher).

The herebelow class :class:`MethodsDecorator` enables to decorate multiple
methods of a given class with custom decorators by simply decorating said class
with it. One then needs to specify, as a dictionary, which decorator is used to
decorate which methods.

"""
from functools import wraps
from abc import abstractmethod


class Decorator(object):
    """Decorator base class."""

    def __init__(self, *args, **kwargs):
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
        return instance.is_decorator_active(self.__class__.__name__)

    def __call__(self, func):
        """Call."""
        @wraps(func)
        def _wrapped_func(instance, *args, **kwargs):
            """Call wrapper is decorator is active, otherwise call func."""
            if instance not in self.instances:
                self.instances.append(instance)
            if self.is_active(instance):
                # active decorator for the current func: wrap it
                return self.wrapper(instance, func, *args, **kwargs)
            else:
                # inactive decorator for the current func
                return func(instance, *args, **kwargs)

        if hasattr(func, '__self__'):
            # input object is a method of an instance
            instance = func.__self__
            return lambda *args, **kwargs: \
                _wrapped_func(instance, *args, **kwargs)
        return _wrapped_func


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

                cls.decorated = True  # indicates that the class is decorated
                cls.wrapper = self.__class__  # type of class decorator
                cls.__decorator_mapping = self.mapping
                cls.decorators = {
                    decorator.__class__.__name__: decorator
                    for decorator in self.mapping.keys()
                }

                for decorator, methods in self.mapping.items():
                    for method in methods:
                        if not hasattr(cls, method):
                            err = 'Input class has not method "{}"'.format(
                                method)
                            raise ValueError(err)
                        setattr(cls, method, decorator(getattr(cls, method)))

                super(MC, cls).__init__(name, bases, dict)

        global Wrapped

        class Wrapped(cls, metaclass=MC):
            """Wrapped class where each specified method is decorated."""

            def __init__(self, *args, **kwargs):
                self.active_decorators = \
                    {decorator: True for decorator in self.decorators}
                super(Wrapped, self).__init__(*args, **kwargs)

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
        Wrapped.__name__ = 'Wrapped(' + cls.__name__ + ')'
        Wrapped.__doc__ = cls.__doc__

        return Wrapped
