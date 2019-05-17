'''
Various helper functions for manipulating python data structures and values
'''

def merge(primary, addition):
    '''
    Combine two dicts, a recursive dict.update().

    >>> merge({'level': {'one': 1}},
    ...       {'level': {'two': 2}, 'floor': {'four': 4}})
    {'level': {'one': 1, 'two': 2}, 'floor': {'four': 4}}
    '''
    for key, value in addition.items():
        if not key in primary:
            primary[key] = value
        elif isinstance(value, dict):
            merge(primary[key], value)
    return primary

def traverse_get(top, *args):
    '''
    >>> traverse_get({'level': {'one': 1}}, 'level', 'one')
    1
    '''
    current = top
    for level in args[:-1]:
        current = current[level]
    return current[args[-1]]

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

def traverse_config_set(target, *args):
    '''
    >>> traverse_set({'level': {'one': 1}}, 'level', 'one', 42)
    {'level': {'one': 42}}
    '''
    # Seperate the path down from the value to set
    path, value = args[:-1], args[-1]
    current = target
    last = target
    for level in path:
        if not level in current:
            current[level] = {'arg': None, 'config': {}}
        last = current[level]
        current = last['config']
    last['arg'] = value
    return target

def traverse_config_get(target, *args):
    '''
    >>> traverse_set({'level': {'one': 1}}, 'level', 'one', 42)
    {'level': {'one': 42}}
    '''
    current = target
    last = target
    for level in args:
        last = current[level]
        current = last['config']
    return last['arg']
