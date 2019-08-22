"""Functions used for class registration."""
import logging
import re
from ..decorator import shared_wrappers


def dispatch(cls, n_dispatch):
    """Dispatch wrapper."""
    n_dispatch = 0 if n_dispatch is None else n_dispatch
    if n_dispatch == 0:
        logging.warning('No dispatching as `n_dispatch` is null.')
        return
    elif not isinstance(n_dispatch, int):
        raise ValueError('`n_dispatch` should be an integer')
    base_classname = make_wrapper_classname(
        cls._Wrapper__wrapped_class.__name__)
    max_num, cls_name = (
        re.search(r'Wrapped([0-9]*)\((.*)\)', base_classname).groups()
    )
    for i in range(n_dispatch):
        new_classname = (
            'Wrapped{}({})'.format(int(max_num) + i, cls_name)
        )
        cls_copy = type(new_classname,
                        cls.__bases__,
                        dict(cls.__dict__))
        register(cls_copy, verbose=False)


def assign(cls, verbose=False):
    """Assign wrapper."""
    classname = cls if isinstance(cls, str) else cls.__name__
    if classname not in shared_wrappers:
        ValueError('{} is not a registered class'.format(classname))
    if shared_wrappers[classname]._Wrapper__assigned:
        ValueError('{} is already assigned'.format(classname))
    if verbose:
        print('Assigning: {}'.format(classname))
    shared_wrappers[classname]._Wrapper__assigned = True


def unassign(cls, verbose=False):
    """Unassign wrapper."""
    classname = cls if isinstance(cls, str) else cls.__name__
    if classname not in shared_wrappers:
        ValueError('{} is not a registered class'.format(classname))
    if not shared_wrappers[classname]._Wrapper__assigned:
        logging.warning('{} is not assigned'.format(classname))
        return
    if verbose:
        print('Unassigning: {}'.format(classname))
    shared_wrappers[classname]._Wrapper__assigned = False


def unassign_all(cls, verbose=False):
    """Unassign all wrappers."""
    classname = cls if isinstance(cls, str) else cls.__name__
    if verbose:
        print('Unassigning all wrappers of {}'.format(classname))
    for classname in get_unassigned_wrappers_classnames(classname):
        unregister(classname, verbose=False)


def get_unassigned_wrappers_classnames(classname):
    """Get unassigned wrappers classnames."""
    registered_wrappers = get_registered_wrappers_classnames()
    wrappers = (
        [(wrapper_name, shared_wrappers[wrapper_name])
         for wrapper_name in registered_wrappers]
    )
    unassigned_wrappers = (
        [wrapper_name for (wrapper_name, wrapper) in wrappers
         if not wrapper._Wrapper__assigned]
    )
    unassigned_wrappers = [
        wrapper for wrapper in unassigned_wrappers
        if re.search(r'Wrapped([0-9]*)\((.*)\)', wrapper).groups() is not None
    ]
    if len(unassigned_wrappers) == 0:
        raise ValueError('No assigned wrapper found.')

    return unassigned_wrappers


def get_first_unassigned_wrapper(classname):
    """Get first unassigned wrapper."""
    unassigned_wrappers = get_unassigned_wrappers_classnames(classname)
    nums = [re.search(r'Wrapped([0-9]*)\((.*)\)', wrapper).groups()[0]
            for wrapper in unassigned_wrappers]
    nums = [int(num) for num in nums if num != '']
    min_num = sorted(nums)[0]
    wrapper_classname = 'Wrapped{}({})'.format(min_num, classname)
    return shared_wrappers[wrapper_classname]


def register(cls, verbose=False):
    """Register class."""
    classname = cls.__name__
    if verbose:
        print('Registering: {}'.format(classname))
    if classname in shared_wrappers and 'Wrapped(' not in classname:
        raise ValueError('{} is already a registered class.'.format(classname))
    shared_wrappers[classname] = cls


def unregister(cls, verbose=False):
    """Unregister class."""
    classname = cls if isinstance(cls, str) else cls.__name__
    if verbose:
        print('Unregistering: {}'.format(classname))
    if classname in shared_wrappers:
        del shared_wrappers[classname]
    else:
        logging.warning('{} is not a registered class'.format(classname))


def unregister_all():
    """Unregister all classes."""
    for classname in get_registered_wrappers_classnames():
        unregister(classname, verbose=False)


def get_registered_wrappers_classnames():
    """Get classnames of all registered wrappers."""
    return list(set([k for k in shared_wrappers if 'Wrapped' in k]))


def make_wrapper_classname(classname):
    """Return new wrapper classname based on registered classes."""
    registered_wrappers = get_registered_wrappers_classnames()
    searches = [re.search(r'Wrapped([0-9]*)\((.*)\)', elt)
                for elt in registered_wrappers if 'DWrapped' not in elt]
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
