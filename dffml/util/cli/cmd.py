# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import ast
import sys
import json
import logging
import inspect
import asyncio
import argparse
from typing import Tuple, Dict, Any

from ...repo import Repo
from ...feature import Feature

from ..data import merge
from .arg import Arg

DisplayHelp = 'Display help message'

class MissingConfig(Exception):
    pass # pragma: no cover

class ParseLoggingAction(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest,
                getattr(logging, value.upper(), logging.INFO))
        logging.basicConfig(level=getattr(namespace, self.dest))

class JSONEncoder(json.JSONEncoder):
    '''
    Encodes dffml types to JSON representation.
    '''

    def default(self, obj):
        if isinstance(obj, Repo):
            return obj.dict()
        elif isinstance(obj, Feature):
            return obj.NAME
        return json.JSONEncoder.default(self, obj)

class Parser(argparse.ArgumentParser):

    def add_subs(self, add_from: 'CMD'):
        '''
        Add sub commands and arguments recursively
        '''
        # Only one subparser should be created even if multiple sub commands
        subparsers = None
        for name, method in [(name.lower().replace('_', ''), method) \
                for name, method in inspect.getmembers(add_from)]:
            if inspect.isclass(method) and issubclass(method, CMD):
                if subparsers is None: # pragma: no cover
                    subparsers = self.add_subparsers() # pragma: no cover
                parser = subparsers.add_parser(name, help=None \
                        if method.__doc__ is None else method.__doc__.strip())
                parser.set_defaults(cmd=method)
                parser.set_defaults(parser=parser)
                parser.add_subs(method) # type: ignore
            elif isinstance(method, Arg):
                self.add_argument(method.name, **method)

class CMD(object):

    JSONEncoder = JSONEncoder
    EXTRA_CONFIG_ARGS = {}

    arg_log = Arg('-log', help='Logging level', action=ParseLoggingAction,
            required=False, default=logging.INFO)

    def __init__(self, extra_config=None, **kwargs) -> None:
        self.logger = logging.getLogger('%s.%s' % (self.__class__.__module__,
                                                   self.__class__.__qualname__))
        if extra_config is None:
            extra_config = {}
        self.extra_config = extra_config
        for name, method in [(name.lower().replace('arg_', ''), method) \
                for name, method in inspect.getmembers(self) \
                if isinstance(method, Arg)]:
            if not name in kwargs and method.name in kwargs:
                name = method.name
            if not name in kwargs and 'default' in method:
                kwargs[name] = method['default']
            if name in kwargs:
                self.logger.debug('Setting %s = %r', name, kwargs[name])
                setattr(self, name, kwargs[name])
            else:
                self.logger.debug('Ignored %s', name)

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    def config(self, cls, *args: str) -> Any:
        '''
        From the overall config object, retrieve the sub config object
        applicable to this loaded Object.
        '''
        current = self.extra_config
        name = cls.ENTRY_POINT_NAME + [cls.ENTRY_POINT_LABEL] + list(args)
        for i in range(0, len(name)):
            level = name[i]
            if not level in current:
                raise MissingConfig('%s(%s) missing %r from %s.extra_config%s%s' % \
                                    (cls.__qualname__,
                                     cls.ENTRY_POINT_LABEL,
                                     level,
                                     self.__class__.__qualname__,
                                     '.' if name[:i] else '',
                                     '.'.join(name[:i]),))
            current = current[level]
        return current

    @classmethod
    async def parse_args(cls, *args):
        parser = Parser()
        parser.add_subs(cls)
        return parser, parser.parse_known_args(args)

    @classmethod
    def str_to_bool(cls, value):
        if value.lower() in ['off', 'no', 'false']:
            return False
        elif value.lower() in ['on', 'yes', 'true']:
            return True
        return value

    @classmethod
    def try_literal_eval(cls, value):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return cls.str_to_bool(value)

    @classmethod
    def parse_one_arg(cls, arg, name, add_to_parsed):
        top = {}
        if name:
            if not add_to_parsed:
                # Bool value
                add_to_parsed = True
            else:
                if len(add_to_parsed) == 1:
                    add_to_parsed = add_to_parsed[0]
            current = top
            for level in name[:-1]:
                if not level in current:
                    current[level] = {}
                    current = current[level]
            current[name[-1]] = add_to_parsed
        return arg.lstrip('-').split('-'), top

    @classmethod
    def parse_unknown(cls, *unknown):
        parsed = {}
        name = []
        add_to_parsed = []
        for arg in unknown:
            if arg.startswith('-'):
                name, current = cls.parse_one_arg(arg, name, add_to_parsed)
                merge(parsed, current)
                add_to_parsed = []
            else:
                add_to_parsed.append(cls.try_literal_eval(arg))
        if unknown:
            name, current = cls.parse_one_arg(unknown[-1], name, add_to_parsed)
            merge(parsed, current)
        return parsed

    @classmethod
    async def cli(cls, *args):
        parser, (args, unknown) = await cls.parse_args(*args)
        args.extra_config = cls.parse_unknown(*unknown)
        if getattr(cls, 'run', None) is not None \
                and getattr(args, 'cmd', None) is None:
            args.cmd = cls
        if getattr(args, 'cmd', None) is None:
            parser.print_help()
            return DisplayHelp
        if getattr(args.cmd, 'run', None) is None:
            args.parser.print_help()
            return DisplayHelp
        cmd = args.cmd(**cls.sanitize_args(vars(args)))
        async with cmd:
            if inspect.isasyncgenfunction(cmd.run):
                return [res async for res in cmd.run()]
            else:
                return await cmd.run()

    @classmethod
    def sanitize_args(cls, args):
        '''
        Remove CMD internals from arguments passed to subclasses of CMD.
        '''
        for rm in ['cmd', 'parser', 'log']:
            if rm in args:
                del args[rm]
        return args

    @classmethod
    def main(cls, loop=asyncio.get_event_loop(), argv=sys.argv):
        '''
        Runs cli commands in asyncio loop and outputs in appropriate format
        '''
        result = None
        try:
            result = loop.run_until_complete(cls.cli(*argv[1:]))
        except KeyboardInterrupt: # pragma: no cover
            pass # pragma: no cover
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        if not result is None and result is not DisplayHelp:
            json.dump(result, sys.stdout, sort_keys=True, indent=4,
                      separators=(',', ': '), cls=cls.JSONEncoder)
            print()
