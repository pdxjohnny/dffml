# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import sys
import json
import logging
import inspect
import asyncio
import argparse

from ...repo import Repo
from ...feature import Feature

from .arg import Arg

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

    arg_log = Arg('-log', help='Logging level', action=ParseLoggingAction,
            required=False, default=logging.INFO)

    def __init__(self, **kwargs) -> None:
        self.logger = logging.getLogger('%s.%s' % (self.__class__.__module__,
                                                   self.__class__.__qualname__))
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

    @classmethod
    async def parse_args(cls, *args):
        parser = Parser()
        parser.add_subs(cls)
        return parser, parser.parse_args(args)

    @classmethod
    async def cli(cls, *args):
        self = cls()
        parser, args = await self.parse_args(*args)
        if getattr(args, 'cmd', None) is None:
            parser.print_help()
            return None
        if getattr(args.cmd, 'run', None) is None:
            args.parser.print_help()
            return None
        cmd = args.cmd(**self.sanitize_args(vars(args)))
        async with cmd:
            if inspect.isasyncgenfunction(cmd.run):
                return [res async for res in cmd.run()]
            else:
                return await cmd.run()

    def sanitize_args(self, args):
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
        if not result is None:
            json.dump(result, sys.stdout, sort_keys=True, indent=4,
                      separators=(',', ': '), cls=cls.JSONEncoder)
            print()
