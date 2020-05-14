"""
Various helper functions for manipulating python data structures and values

Run doctests with

python -m doctest -v dffml/util/data.py
"""
import ast
import types
import pydoc
import inspect
import dataclasses
from functools import wraps
import pathlib
from typing import Callable


def merge(one, two, list_append: bool = True):
    for key, value in two.items():
        if key in one:
            if isinstance(value, dict):
                merge(one[key], two[key], list_append=list_append)
            elif list_append and isinstance(value, list):
                one[key] += two[key]
        else:
            one[key] = two[key]
    return one


def traverse_config_set(target, *args):
    """
    Examples
    --------

    >>> from dffml import traverse_config_set
    >>>
    >>> traverse_config_set({
    ...     "level": {
    ...         "plugin": None,
    ...         "config": {
    ...             "one": {
    ...                 "plugin": 1,
    ...                 "config": {},
    ...             },
    ...         },
    ...     },
    ... }, "level", "one", 42)
    {'level': {'plugin': None, 'config': {'one': {'plugin': 42, 'config': {}}}}}
    """
    # Seperate the path down from the value to set
    path, value = args[:-1], args[-1]
    current = target
    last = target
    for level in path:
        if not level in current:
            current[level] = {"plugin": None, "config": {}}
        last = current[level]
        current = last["config"]
    last["plugin"] = value
    return target


def traverse_config_get(target, *args):
    """
    Examples
    --------

    >>> from dffml import traverse_config_get
    >>>
    >>> traverse_config_get({
    ...     "level": {
    ...         "plugin": None,
    ...         "config": {
    ...             "one": {
    ...                 "plugin": 1,
    ...                 "config": {},
    ...             },
    ...         },
    ...     },
    ... }, "level", "one")
    1
    """
    current = target
    last = target
    for level in args:
        last = current[level]
        current = last["config"]
    return last["plugin"]


def traverse_get(target, *args):
    """
    Travel down through a dict

    Examples
    --------

    >>> from dffml import traverse_get
    >>>
    >>> traverse_get({"one": {"two": 3}}, "one", "two")
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


# STANDARD_TYPES Will be the type names which are applicable across languages
# used to transform types from one language into anothers
STANDARD_TYPES = {"Dict": "map", "List": "array", "Any": "generic"}
STANDARD_TYPES_REVERSED = dict(
    zip(STANDARD_TYPES.values(), STANDARD_TYPES.keys())
)


def type_lookup(typename):
    if typename in STANDARD_TYPES_REVERSED:
        typename = f"typing.{STANDARD_TYPES_REVERSED[typename]}"
    # TODO(security) Make sure pydoc.locate won't blow up in our face ever
    typeof = pydoc.locate(typename)
    if typeof is None:
        raise TypeError(typename)
    return typeof


def export_value(obj, key, value):
    # TODO This is a workaround for the generator related AttributeError when
    # exporting a model.
    #
    # features is the key that triggers this error. It is this when it come
    # through here and dies:
    #
    #     [<generator object _asdict_inner.<locals>.<genexpr> at 0x7f21982ae4f8>]
    #
    # The following error is then raised:
    #
    # File "/home/user/Documents/python/dffml/dffml/util/data.py", line 115, in export_value
    #   obj[key] = value.export()
    # File "/home/user/Documents/python/dffml/dffml/feature/feature.py", line 317, in export
    #   return {feature.NAME: feature.export() for feature in self}
    # File "/home/user/Documents/python/dffml/dffml/feature/feature.py", line 317, in <dictcomp>
    #   return {feature.NAME: feature.export() for feature in self}
    # AttributeError: 'generator' object has no attribute 'export'
    #
    # At some point we need to figure out why this is happening.
    if isinstance(value, list) and value and inspect.isgenerator(value[0]):
        obj[key] = list(value[0])
    # export and _asdict are not classmethods
    if hasattr(value, "ENTRY_POINT_ORIG_LABEL") and hasattr(value, "config"):
        obj[key] = {"plugin": value.ENTRY_POINT_ORIG_LABEL}
        export_value(obj[key], "config", value.config)
    elif inspect.isclass(value):
        obj[key] = value.__qualname__
    elif isinstance(value, pathlib.Path):
        obj[key] = str(value)
    elif hasattr(value, "export"):
        obj[key] = value.export()
    elif hasattr(value, "_asdict"):
        obj[key] = value._asdict()
    elif dataclasses.is_dataclass(value):
        obj[key] = export_dict(**dataclasses.asdict(value))
    elif getattr(value, "__module__", None) == "typing":
        obj[key] = STANDARD_TYPES.get(
            str(value).replace("typing.", ""), "generic"
        )
    elif hasattr(value, "config") and hasattr(value, "ENTRY_POINT_ORIG_LABEL"):
        obj[key] = export_base_configurable(value)


def export_list(iterable):
    for i, value in enumerate(iterable):
        export_value(iterable, i, value)
        if isinstance(value, (dict, types.MappingProxyType)):
            iterable[i] = export_dict(**iterable[i])
        elif dataclasses.is_dataclass(value):
            iterable[i] = export_dict(**dataclasses.asdict(value))
        elif isinstance(value, list):
            iterable[i] = export_list(iterable[i])
    return iterable


def export_base_configurable(obj):
    return {
        "arg": obj.ENTRY_POINT_ORIG_LABEL,
        "config": export_dict(**obj.config._asdict()),
    }


def export_dict(**kwargs):
    """
    Return the dict given as kwargs but first recurse into each element and call
    its export or _asdict function if it is not a serializable type.
    """
    for key, value in kwargs.items():
        export_value(kwargs, key, value)
        if isinstance(kwargs[key], (dict, types.MappingProxyType)):
            kwargs[key] = export_dict(**kwargs[key])
        elif isinstance(kwargs[key], list):
            kwargs[key] = export_list(kwargs[key])
    return kwargs


def explore_directories(path_dict: dict):
    """
    Recursively explores any path binded to a key in `path_dict`

    Examples
    --------

    >>> import pathlib
    >>> import tempfile
    >>> from dffml import explore_directories
    >>>
    >>> with tempfile.TemporaryDirectory() as root:
    ...     # Setup directories for example
    ...     STRUCTURE = '''
    ...     root
    ...     |
    ...     +--- deadbeef
    ...     |    |
    ...     |    +--- file1.txt
    ...     |    +--- colosseum
    ...     |         |
    ...     |         +--- battle.rst
    ...     +--- face
    ...          |
    ...          +--- file2.jpg
    ...     '''
    ...     # The writes will produce the 0's in the output (for doctest)
    ...     pathlib.Path(root, "deadbeef").mkdir()
    ...     pathlib.Path(root, "deadbeef", "file1.txt").write_text("")
    ...     pathlib.Path(root, "deadbeef", "colosseum").mkdir()
    ...     pathlib.Path(root, "deadbeef", "colosseum", "battle.rst").write_text("")
    ...     pathlib.Path(root, "face").mkdir()
    ...     pathlib.Path(root, "face", "file2.jpg").write_text("")
    ...     # Explore directories
    ...     root = explore_directories(path_dict={
    ...         "root": root
    ...     })["root"]
    ...     # Check that everything was found
    ...     bool("deadbeef" in root)
    ...     bool("colosseum" in root["deadbeef"])
    ...     bool("battle" in root["deadbeef"]["colosseum"])
    ...     bool("face" in root)
    ...     bool("file2" in root["face"])
    0
    0
    0
    True
    True
    True
    True
    True
    """
    for key, val in path_dict.items():
        t_path = pathlib.Path(val)
        if t_path.is_dir():
            temp_path_dict = {}
            for _path in pathlib.Path(val).glob("*"):
                t_path = pathlib.Path(_path)
                temp_path_dict[t_path.stem] = _path
            explore_directories(temp_path_dict)
            path_dict[key] = temp_path_dict
    return path_dict


async def nested_apply(target: dict, func: Callable):
    """
    Applies `func` recursively to all non dict types in `target`
    """
    for key, val in target.items():
        if isinstance(val, dict):
            target[key] = await nested_apply(val, func)
        else:
            if inspect.iscoroutinefunction(func):
                target[key] = await func(val)
            else:
                target[key] = func(val)
    return target


def parser_helper(value):
    """
    Calls checks if value is string and if it is it converts it to a bool if
    the string is a string representation of common boolean value (on, off,
    true, false, yes, no). Otherwise it tries to call
    :py:func:`ast.literal_eval`, if that doesn't succeed the string value is
    returned.


    Examples
    --------

    >>> from dffml import parser_helper
    >>>
    >>> parser_helper("on")
    True
    >>> parser_helper("[1, 2, 3]")
    [1, 2, 3]
    >>> parser_helper("hello")
    'hello'
    >>> parser_helper("'on'")
    'on'
    """
    if not isinstance(value, str):
        return value
    if value.lower() in ["null", "nil", "none"]:
        return None
    elif value.lower() in ["yes", "true", "on"]:
        return True
    elif value.lower() in ["no", "false", "off"]:
        return False
    try:
        return ast.literal_eval(value)
    except:
        return value
