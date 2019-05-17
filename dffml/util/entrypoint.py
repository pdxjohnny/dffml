# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Loader subclasses know how to load classes under their entry point which conform
to their subclasses.
'''
import copy
import pkg_resources
from typing import List, Dict

class MissingLabel(Exception):
    pass # pragma: no cover

class Entrypoint(object):
    '''
    Uses the pkg_resources.iter_entry_points on the ENTRY_POINT of the class
    '''

    ENTRY_POINT = 'util.entrypoint'
    # Label is for configuration. Sometimes multiple of the same classes will be
    # loaded. They need to determine which config options are meant for which
    # class. Therefore a label is applied to each class after it is loaded. If
    # there is only one instance of any type of a certain entry point a label
    # need not be applied because that class will know any thing that applies to
    # configuration for its entry point belongs solely to it.
    ENTRY_POINT_LABEL  = ''

    @classmethod
    def load(cls, loading=None):
        '''
        Loads all installed loading and returns them as a list. Sources to be
        loaded should be registered to ENTRY_POINT via setuptools.
        '''
        loading_classes = []
        for i in pkg_resources.iter_entry_points(cls.ENTRY_POINT):
            loaded = i.load()
            loaded.ENTRY_POINT_LABEL = i.name
            if issubclass(loaded, cls):
                loading_classes.append(loaded)
                if loading is not None and i.name == loading:
                    return loaded
        if loading is not None:
            raise KeyError('%s was not found in (%s)' % \
                    (repr(loading), ', '.join(list(map(str, loading_classes)))))
        return loading_classes

    @classmethod
    def load_multiple(cls, to_load: List[str]):
        '''
        Loads each class requested without instantiating it.
        '''
        return {name: cls.load(name) for name in to_load}

    @classmethod
    def load_dict(cls, to_load: Dict[str, str]):
        '''
        Loads each class tagged with the key it should be accessed by without
        instantiating it.
        '''
        return {key: cls.load(name) for key, name in to_load.items()}

    @classmethod
    def load_labeled(cls, label_and_loading):
        if '=' in label_and_loading:
            label, loading = label_and_loading.split('=', maxsplit=1)
        else:
            raise MissingLabel('%r is missing a label. '
                               'Correct syntax: label=%s' \
                               % (label_and_loading, label_and_loading,))
        loaded = copy.deepcopy(cls.load(loading))
        loaded.ENTRY_POINT_LABEL = label
        return loaded
