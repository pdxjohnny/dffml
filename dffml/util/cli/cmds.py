import os
import sys
import ast
import copy
import json
import asyncio
import inspect
import logging
import argparse
from typing import Optional

from ...repo import Repo
from ...port import Port
from ...feature import Feature, Features
from ...source.source import BaseSource, Sources
from ...source.json import JSONSource
from ...source.file import FileSourceConfig
from ...model import Model

from ...df.types import Operation
from ...df.linker import Linker
from ...df.base import Input, \
                  BaseInputNetwork, \
                  BaseOperationNetwork, \
                  BaseLockNetwork, \
                  BaseRedundancyChecker, \
                  BaseOperationImplementationNetwork, \
                  BaseOrchestrator, \
                  StringInputSetContext

from ...df.memory import MemoryInputNetwork, \
                  MemoryOperationNetwork, \
                  MemoryLockNetwork, \
                  MemoryRedundancyChecker, \
                  MemoryOperationImplementationNetwork, \
                  MemoryOrchestrator, \
                  MemoryInputSet, \
                  MemoryInputSetConfig

from ...df.dff import DataFlowFacilitator

from ..data import merge
from .arg import Arg
from .cmd import CMD
from .parser import list_action, \
                    ParseOutputSpecsAction, \
                    ParseInputsAction, \
                    ParseRemapAction

class ListEntrypoint(CMD):
    '''
    Subclass this with an Entrypoint to display all registered classes.
    '''

    def display(self, cls):
        '''
        Print out the loaded but uninstantiated class
        '''
        if not cls.__doc__ is None:
            print('%s:' % (cls.__qualname__))
            print(cls.__doc__.rstrip())
        else:
            print('%s' % (cls.__qualname__))
        print()

    async def run(self):
        '''
        Display all classes registered with the entrypoint
        '''
        for cls in self.ENTRYPOINT.load():
            self.display(cls)

class FeaturesCMD(CMD):
    '''
    Set timeout for features
    '''

    arg_features = Arg('-features', nargs='+', required=True,
            default=Features(), type=Feature.load, action=list_action(Features))
    arg_timeout = Arg('-timeout', help='Feature evaluation timeout',
            required=False, default=Features.TIMEOUT, type=int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.features.timeout = self.timeout

class SourcesCMD(CMD):

    arg_sources = Arg('-sources', help='Sources for loading and saving',
            nargs='+',
            default=Sources(JSONSource(FileSourceConfig(
                filename=os.path.join(os.path.expanduser('~'),
                                      '.cache', 'dffml.json')))),
            type=BaseSource.load_labeled,
            action=list_action(Sources))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Go through the list of sources and instantiate them with a config
        # created from loading their arguments from cmd (self).
        for i in range(0, len(self.sources)):
            if inspect.isclass(self.sources[i]):
                self.sources[i] = self.sources[i].withconfig(self)

class ModelCMD(CMD):
    '''
    Set a models model dir.
    '''

    arg_model = Arg('-model', help='Model used for ML',
            type=Model.load, required=True)
    arg_model_dir = Arg('-model_dir', help='Model directory for ML',
            default=os.path.join(os.path.expanduser('~'), '.cache', 'dffml'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model.model_dir = self.model_dir

class PortCMD(CMD):

    arg_port = Arg('port', type=Port.load)

class KeysCMD(CMD):

    arg_keys = Arg('-keys', help='Key used for source lookup and evaluation',
            nargs='+', required=True)
'''
        setattr(namespace, self.dest, Operation.load_multiple(values).values())
        setattr(namespace, self.dest,
                OperationImplementation.load_multiple(values).values())
        setattr(namespace, self.dest, BaseInputNetwork.load(value))
        setattr(namespace, self.dest, BaseOperationNetwork.load(value))
        setattr(namespace, self.dest, BaseLockNetwork.load(value))
        setattr(namespace, self.dest, BaseRedundancyChecker.load(value))
        setattr(namespace, self.dest, BaseKeyValueStore.load(value))
        setattr(namespace, self.dest,
                BaseOperationImplementationNetwork.load(value))
        setattr(namespace, self.dest, BaseOrchestrator.load(value))
        setattr(namespace, self.dest, Model.load(value)())
        setattr(namespace, self.dest, Port.load(value)())
'''

class BaseDataFlowFacilitatorCMD(CMD):
    '''
    Set timeout for features
    '''

    arg_ops = Arg('-ops', required=True, nargs='+',
            type=Operation.load)
    arg_input_network = Arg('-input-network',
            type=BaseInputNetwork.load,
            default=MemoryInputNetwork)
    arg_operation_network = Arg('-operation-network',
            type=BaseOperationNetwork.load,
            default=MemoryOperationNetwork)
    arg_lock_network = Arg('-lock-network',
            type=BaseLockNetwork.load,
            default=MemoryLockNetwork)
    arg_rchecker = Arg('-rchecker',
            type=BaseRedundancyChecker.load,
            default=MemoryRedundancyChecker)
    # TODO We should be able to specify multiple operation implementation
    # networks. This would enable operations to live in different place,
    # accessed via the orchestrator transparently.
    arg_opimpn = Arg('-opimpn',
            type=BaseOperationImplementationNetwork.load,
            default=MemoryOperationImplementationNetwork)
    arg_orchestrator = Arg('-orchestrator',
            type=BaseOrchestrator.load,
            default=MemoryOrchestrator)
    arg_output_specs = Arg('-output-specs', required=True, nargs='+',
            action=ParseOutputSpecsAction)
    arg_inputs = Arg('-inputs', nargs='+',
            action=ParseInputsAction, default=[],
            help='Other inputs to add under each ctx (repo\'s src_url will ' + \
                 'be used as the context)')
    arg_repo_def = Arg('-repo-def', default=False, type=str,
            help='Definition to be used for repo.src_url.' + \
                 'If set, repo.src_url will be added to the set of inputs ' + \
                 'under each context (which is also the repo\'s src_url)')
    arg_remap = Arg('-remap', nargs='+', required=True,
            action=ParseRemapAction,
            help='For each repo, -remap output_operation_name.sub=feature_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dff = DataFlowFacilitator(
            input_network=self.input_network.withconfig(self),
            operation_network=self.operation_network.withconfig(self),
            lock_network=self.lock_network.withconfig(self),
            rchecker=self.rchecker.withconfig(self),
            opimp_network=self.opimpn.withconfig(self),
            orchestrator=self.orchestrator.withconfig(self)
        )
        self.linker = Linker()
        self.exported = self.linker.export(*self.ops)
        self.definitions, self.operations, _outputs = \
                self.linker.resolve(self.exported)

    # Load all entrypoints which may possibly be selected. Then have them add
    # their arguments to the DataFlowFacilitator-tots command.
    @classmethod
    def add_bases(cls):
        # TODO Add args() for each loaded class as argparse arguments
        return cls
        cls = copy.deepcopy(cls)
        for base in [BaseInputNetwork,
                     BaseOperationNetwork,
                     BaseLockNetwork,
                     BaseRedundancyChecker,
                     BaseOperationImplementationNetwork,
                     BaseOrchestrator]:
            for loaded in base.load():
                loaded.args(cls.EXTRA_CONFIG_ARGS)
        return cls

DataFlowFacilitatorCMD = BaseDataFlowFacilitatorCMD.add_bases()
