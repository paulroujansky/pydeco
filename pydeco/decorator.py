"""Decorator for class methods.

...                                                                        TODO

"""


class MethodsDecorator(object):
    """Class that enables to decorate specific methods with given decorator.

    Parameters
    ----------
    mapping : dict
        Mapping containing decorators as key and methods (as list of str) as
        values (ex: {Timer(): ['fit', 'predict']})

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
        """Call."""
        class MC(type):
            """Decorating methods for the input class with given decorator."""

            def __init__(cls, name, bases, dict):
                for decorator, methods in self.mapping.items():
                    for method in methods:
                        if not hasattr(cls, method):
                            err = 'Input class has not method "{}"'.format(
                                method)
                            raise ValueError(err)
                        setattr(cls, method, decorator(getattr(cls, method)))
                    super(MC, cls).__init__(name, bases, dict)

        class Wrapped(cls, metaclass=MC):
            """Wrapped class where each specified method is decorated."""

            pass

        return Wrapped
