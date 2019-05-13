import os
import sys
import glob
import json
import pkgutil
import inspect
import argparse
import importlib
from collections import OrderedDict
from typing import Dict, List, NamedTuple

def traverse_set(target, *args):
    '''
    >>> traverse_set({'level': {'one': 1}}, 'level', 'one', 42)
    {'level': {'one': 42}}
    '''
    # Seperate the path down from the value to set
    path, value = args[:-1], args[-1]
    current = target
    for level in path[:-1]:
        if not level in current:
            current[level] = {}
        current = current[level]
    current[path[-1]] = value
    return target

# From https://stackoverflow.com/a/32782927 @mistermiyagi
def namedtuple_asdict(obj):
    if hasattr(obj, "_asdict"): # detect namedtuple
        return OrderedDict(zip(obj._fields, (namedtuple_asdict(item) \
                               for item in obj)))
    elif isinstance(obj, str): # iterables - strings
        return obj
    elif isinstance(obj, dict): # iterables - mapping
        return OrderedDict(zip(obj.keys(), (namedtuple_asdict(item) \
                               for item in obj.values())))
    elif hasattr(obj, '__iter__'): # iterables - strings
        return type(obj)((namedtuple_asdict(item) for item in obj))
    else: # non-iterable cannot contain namedtuples
        return obj

class Documentation(NamedTuple):
    name: str
    module: str
    source: str
    filename: str
    docstring: str
    args: Dict[str, str]

class ClassDocumentation(NamedTuple):
    name: str
    module: str
    values: List[Documentation]
    methods: List[Documentation]
    filename: str
    docstring: str

def recursive_import_module(module):
    for pkg in pkgutil.walk_packages(module.__path__, module.__name__ + '.'):
        if pkg.name.startswith(module.__name__):
            yield importlib.import_module(pkg.name)

def import_module(module_name):
    return list(recursive_import_module(importlib.import_module(module_name)))

def is_from_module(top_module, loaded):
    top_dirname = os.path.dirname(inspect.getsourcefile(top_module))
    source_file = inspect.getsourcefile(loaded)
    return bool(source_file is not None and source_file.startswith(top_dirname))

def filename(top_module, loaded):
    top_dirname = os.path.dirname(inspect.getsourcefile(top_module))
    return inspect.getsourcefile(loaded).replace(top_dirname, top_module.__name__)

def doc_func(top_module, module, loaded):
    return Documentation(
        name=loaded.__name__,
        module=module.__name__,
        source=inspect.getsource(loaded),
        filename=filename(top_module, loaded),
        docstring=inspect.getdoc(loaded),
        args=str(inspect.signature(loaded)))

def doc_class(top_module, module, loaded):
    methods = [doc_func(top_module, module, func) \
               for name, func in inspect.getmembers(loaded,
               lambda func: (inspect.isfunction(func) \
                                or inspect.ismethod(func)) \
                                and is_from_module(top_module, func))]
    return ClassDocumentation(
        name=loaded.__name__,
        module=module.__name__,
        values=[],
        methods=methods,
        filename=filename(top_module, loaded),
        docstring=inspect.getdoc(loaded))

def doc_value(top_module, module, loaded):
    return Documentation(
        name=loaded.__name__,
        module=module.__name__,
        source=inspect.getsource(loaded),
        filename=filename(top_module, loaded),
        docstring=inspect.getdoc(loaded),
        args={})

def module_doc(top_module, module, items):
    doc = {
        '__values': {},
        '__functions': {},
        '__classes': {}
        }
    for name, loaded in items.items():
        if not is_from_module(top_module, loaded):
            continue
        if inspect.isfunction(loaded):
            doc['__functions'][name] = doc_func(top_module, module, loaded)
        elif inspect.isclass(loaded):
            doc['__classes'][name] = doc_class(top_module, module, loaded)
        else:
            doc['__values'][name] = doc_value(top_module, module, loaded)
    return doc

def original_to_module(module, item):
    originates_from = inspect.getmodule(getattr(module, item))
    # TODO Not getting defined values such as VERSION
    return bool(originates_from is not None \
                and originates_from.__name__ == module.__name__)

def get_docs(module_name):
    top_module = importlib.import_module(module_name)
    modules = import_module(module_name)
    for module in modules:
        docs = module_doc(top_module, module,
                          {item: getattr(module, item) \
                           for item in module.__dir__() \
                           if original_to_module(module, item)})
        yield module.__name__, docs

def main():
    pretty_json = dict(sort_keys=True, indent=4,
                       separators=(',', ': '))

    parser = argparse.ArgumentParser(description='Create JSON docs')
    parser.add_argument('module', help='Module to document')
    args = parser.parse_args()

    result = {}
    for key, value in namedtuple_asdict(dict(get_docs(args.module))).items():
        key = key.split('.')
        traverse_set(result, *key, value)
    print(json.dumps(result, **pretty_json))

if __name__ == '__main__':
    main()
