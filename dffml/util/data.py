"""
Various helper functions for manipulating python data structures and values
"""
from functools import wraps


def merge(one, two):
    for key, value in two.items():
        if key in one and isinstance(value, dict):
            merge(one[key], two[key])
        else:
            one[key] = two[key]


def traverse_config_set(target, *args):
    """
    >>> traverse_set({'level': {'one': 1}}, 'level', 'one', 42)
    {'level': {'one': 42}}
    """
    # Seperate the path down from the value to set
    path, value = args[:-1], args[-1]
    current = target
    last = target
    for level in path:
        if not level in current:
            current[level] = {"arg": None, "config": {}}
        last = current[level]
        current = last["config"]
    last["arg"] = value
    return target


def traverse_config_get(target, *args):
    """
    >>> traverse_set({'level': {'one': 1}}, 'level', 'one', 42)
    {'level': {'one': 42}}
    """
    current = target
    last = target
    for level in args:
        last = current[level]
        current = last["config"]
    return last["arg"]


def traverse_get(target, *args):
    """
    Travel down through a dict
    >>> traverse_get({"one": {"two": 3}}, ["one", "two"])
    3
    """
    current = target
    for level in args:
        current = current[level]
    return current


def ignore_args(func):
    """
    Decorator to call the decorated function without any arguments passed to it.
    """

    @wraps(func)
    def wrapper(*_args, **_kwargs):
        return func()

    return wrapper


def export_value(obj, key, value):
    if hasattr(value, "export"):
        obj[key] = value.export()
    elif hasattr(value, "_asdict"):
        obj[key] = value._asdict()


def export_list(iterable):
    for i, value in enumerate(iterable):
        export_value(iterable, i, value)
        if isinstance(iterable[i], dict):
            iterable[i] = export_dict(**value)
        elif isinstance(value, list):
            iterable[i] = export_list(value)
    return iterable


def export_dict(**kwargs):
    """
    Return the dict given as kwargs but first recurse into each element and call
    its export or _asdict function if it is not a serializable type.
    """
    for key, value in kwargs.items():
        export_value(kwargs, key, value)
        if isinstance(value, dict):
            kwargs[key] = export_dict(**value)
        elif isinstance(value, list):
            kwargs[key] = export_list(value)
    return kwargs
