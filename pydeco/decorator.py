"""Decorator for class methods (compatible with Python 3.0 or higher).

The herebelow class :class:`MethodsDecorator` enables to decorate multiple
methods of a given class with custom decorators by simply decorating said class
with it. One then needs to specify, as a dictionary, which decorator is used to
decorate which methods.

"""


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
                cls.class_decorator = self.__class__  # type of class decorator

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

            pass

        Wrapped.__name__ = 'Wrapped(' + cls.__name__ + ')'

        return Wrapped
