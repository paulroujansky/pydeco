"""Decorator for class methods (compatible with Python 3.0 or higher).

The herebelow class :class:`MethodsDecorator` enables to decorate multiple
methods of a given class with custom decorators by simply decorating said class
with it. One then needs to specify, as a dictionary, which decorator is used to
decorate which methods.

"""
import logging
import re
from abc import abstractmethod
from copy import deepcopy
from functools import wraps

from .utils import is_wrapped


def register(cls):
    """Register class."""
    classname = cls.__name__
    if classname in globals() and 'Wrapped(' not in classname:
        raise ValueError('{} is already a registered class.'.format(classname))
    globals()[classname] = cls


def unregister(cls):
    """Unregister class."""
    classname = cls if isinstance(cls, str) else cls.__name__
    if classname in globals():
        globals().pop(classname)
    else:
        logging.warning('{} is not a registered class'.format(classname))


def unregister_all():
    """Unregister all classes."""
    for classname in get_registered_wrappers_classnames():
        unregister(classname)


def get_registered_wrappers_classnames():
    """Get classnames of all registered wrappers."""
    return list(set([k for k in globals() if 'Wrapped' in k]))


def make_wrapper_classname(classname):
    """Return new wrapper classname based on registered classes."""
    registered_wrappers = get_registered_wrappers_classnames()
    searches = [re.search(r'Wrapped([0-9]*)\((.*)\)', elt)
                for elt in registered_wrappers]
    nums = [search.groups()[0] for search in searches
            if search is not None and search.groups() is not None]
    if len(nums) == 0:
        wrapper_classname = 'Wrapped({})'.format(classname)
    else:
        if len(nums) == 1 and nums[0] == '':
            max_num = 2
            wrapper_classname = 'Wrapped{}({})'.format(max_num, classname)
        else:
            nums = [int(num) for num in nums if num != '']
            max_num = sorted(nums)[-1] + 1
            wrapper_classname = 'Wrapped{}({})'.format(max_num, classname)
    return wrapper_classname


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
        def wrapped_func(instance, func, *args, **kwargs):
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

            @wraps(func)
            def _wrapped_func(*args, **kwargs):
                return wrapped_func(instance, func, *args, **kwargs)
            return _wrapped_func

        else:
            @wraps(func)
            def _wrapped_func(instance, *args, **kwargs):
                return wrapped_func(instance, func, *args, **kwargs)
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
        self.original_methods = dict()

    def __call__(self, cls):
        """Return wrapped input class with decorated methods."""
        mapping = self.mapping
        original_methods = self.original_methods

        class MC(type):
            """Decorating methods for the input class with given decorator.

            Attributes
            ----------
            decorated : bool
                Indicates that current class is decorated.
            class_decorator : type
                Type of the class decorator used to decorate the current class.

            """

            def __init__(cls_, name, bases, dict):
                for decorator, methods in self.mapping.items():
                    for method in methods:
                        if not hasattr(cls_, method):
                            err = 'Input class has not method "{}"'.format(
                                method)
                            raise ValueError(err)
                        if method not in self.original_methods:
                            self.original_methods[method] = (
                                getattr(cls_, method)
                            )
                        setattr(cls_, method,
                                decorator(getattr(cls_, method)))

                super(MC, cls_).__init__(name, bases, dict)

        global Wrapper

        class Wrapper(cls, metaclass=MC):
            """Wrapped class where each specified method is decorated."""

            __wrapped_class = cls  # base class
            __decorated = True  # indicates that the class is decorated
            __wrapper = self.__class__  # type of class decorator
            __decorator_mapping = mapping  # decorator mapping
            __original_methods = original_methods

            def __init__(self, *args, **kwargs):
                self._decorator_mapping = {
                    k: v for k, v in self.__decorator_mapping.items()
                }
                self.active_decorators = {
                    decorator: True for decorator in self.decorators
                }
                cls.__init__(self, *args, **kwargs)

            @property
            def decorators(self):
                """Return decorators."""
                return {
                    decorator.__class__.__name__: decorator
                    for decorator in self._decorator_mapping.keys()
                }

            def __deepcopy__(self, memo=None, _nil=[]):
                """Deepcopy."""
                # Remove decorators from self
                cls_self = self.__class__
                tmp_methods = dict()
                tmp_mapping = dict()
                tmp_active_decorators = dict()

                for decorator, methods in self._decorator_mapping.items():
                    tmp_mapping[decorator] = methods
                for decorator, is_active in self.active_decorators.items():
                    tmp_active_decorators[decorator] = is_active

                self._decorator_mapping = dict()
                self.active_decorators = dict()

                for method_name, method in self.__original_methods.items():
                    tmp_methods[method_name] = method
                    delattr(cls_self, method_name)

                # Copy self
                c_self = cls_self.__new__(cls_self)
                memo[id(self)] = c_self
                for k, v in self.__dict__.items():
                    setattr(c_self, k, deepcopy(v, memo))

                new_wrapper_classname = make_wrapper_classname(cls.__name__)

                # Copy self's Wrapper
                cls_c_self = type(new_wrapper_classname,
                                  c_self.__class__.__bases__,
                                  dict(c_self.__class__.__dict__))
                register(cls_c_self)
                c_self.__class__ = cls_c_self

                # Add back decorators to both self and its copy
                for method_name, method in tmp_methods.items():
                    setattr(cls_self, method_name, method)
                    setattr(cls_c_self, method_name, method)

                for decorator, methods in tmp_mapping.items():
                    decorator_name = decorator.__class__.__name__
                    c_decorator = deepcopy(decorator)
                    self._decorator_mapping[decorator] = methods
                    c_self._decorator_mapping[c_decorator] = methods

                    is_decorator_active = (
                        tmp_active_decorators[decorator_name]
                    )
                    self.active_decorators[decorator_name] = (
                        is_decorator_active)
                    c_self.active_decorators[decorator_name] = (
                        is_decorator_active)

                    for method_name in methods:
                        if not hasattr(self, method_name):
                            err = 'Input class has not method "{}"'.format(
                                method_name)
                            raise ValueError(err)
                        setattr(
                            cls_self, method_name,
                            decorator(getattr(cls_self, method_name)))
                        if not hasattr(c_self, method_name):
                            err = 'Input class has not method "{}"'.format(
                                method_name)
                            raise ValueError(err)
                        setattr(
                            cls_c_self, method_name,
                            c_decorator(getattr(cls_c_self, method_name)))
                # return copy
                return c_self

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
        Wrapper.__name__ = make_wrapper_classname(cls.__name__)
        Wrapper.__doc__ = cls.__doc__

        register(Wrapper)

        return Wrapper
