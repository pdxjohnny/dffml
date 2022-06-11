# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import sys
import json
import uuid
import enum
import logging
import inspect
import asyncio
import datetime
import argparse
import dataclasses
from typing import Dict, Any, NewType
import dataclasses

from ...record import Record
from ...feature import Feature
from ...df.types import DataFlow, Operation
from ...df.base import op
from ...df.system_context.system_context import SystemContext

from ..data import export_dict, merge
from .arg import Arg, parse_unknown
from ...base import (
    config,
    mkarg,
    field,
    make_config,
    subclass,
)
from ...configloader.configloader import ConfigLoaders

DisplayHelp = "Display help message"


class CMDOutputOverride:
    """
    Override dumping of results
    """


if sys.platform == "win32":  # pragma: no cov
    asyncio.set_event_loop(asyncio.ProactorEventLoop())


class ParseLoggingAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(
            namespace, self.dest, getattr(logging, value.upper(), logging.INFO)
        )
        logging.basicConfig(level=getattr(namespace, self.dest))


class JSONEncoder(json.JSONEncoder):
    """
    Encodes dffml types to JSON representation.
    """

    def default(self, obj):
        typename_lower = str(type(obj)).lower()
        if isinstance(obj, Record):
            return obj.dict()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return str(obj)
        elif isinstance(obj, Feature):
            return obj.name
        elif isinstance(obj, enum.Enum):
            return str(obj.value)
        elif isinstance(obj, type):
            return str(obj.__qualname__)
        elif "numpy." in typename_lower:
            if ".int" in typename_lower or ".uint" in typename_lower:
                return int(obj)
            elif typename_lower.startswith("float"):
                return float(obj)
            elif "ndarray" in typename_lower:
                return obj.tolist()
        elif str(obj).startswith("typing."):
            return str(obj).split(".")[-1]
        return json.JSONEncoder.default(self, obj)


log_cmd = Arg(
    "-log",
    help="Logging level",
    action=ParseLoggingAction,
    required=False,
    default=logging.INFO,
)


class Parser(argparse.ArgumentParser):
    def add_subs(self, add_from: "CMD"):
        """
        Add sub commands and arguments recursively
        """
        # Only one subparser should be created even if multiple sub commands
        subparsers = None
        for name, method in (
            [
                (name.lower().replace("_", ""), method)
                for name, method in inspect.getmembers(add_from)
            ]
            if not isinstance(add_from, SystemContext)
            else add_from.config.upstream.operations.items()
        ):
            if (
                isinstance(method, SystemContext)
                or (
                    inspect.isclass(method)
                    and (
                        issubclass(method, CMD)
                        or issubclass(method, SystemContext)
                    )
                )
            ):
                if subparsers is None:  # pragma: no cover
                    subparsers = self.add_subparsers()  # pragma: no cover
                parser = subparsers.add_parser(
                    name,
                    description=None
                    if method.__doc__ is None
                    else method.__doc__,
                    formatter_class=getattr(
                        method,
                        "CLI_FORMATTER_CLASS",
                        argparse.ArgumentDefaultsHelpFormatter,
                    ),
                )
                parser.set_defaults(cmd=method)
                parser.set_defaults(parser=parser)
                parser.add_subs(method)  # type: ignore

        # Add arguments to the Parser
        position_list = {}
        config = getattr(add_from, "config", add_from.CONFIG)
        for i, field in enumerate(dataclasses.fields(config)):
            arg = mkarg(field, dataclass=config)
            if isinstance(arg, Arg):
                position = None
                if not "default" in arg and not arg.get("required", False):
                    position_list[i] = (field.name, arg)
                else:
                    try:
                        self.add_argument(
                            "-" + field.name.replace("_", "-"), **arg
                        )
                    except argparse.ArgumentError as error:
                        raise Exception(repr(add_from)) from error

        if position_list:
            for position in sorted(position_list.keys()):
                name, positional_arg = position_list[position]
                self.add_argument(name.replace("_", "-"), **positional_arg)
            position_list.clear()

        # Add `-log` argument if it's not already added
        try:
            self.add_argument(log_cmd.name, **log_cmd)
        except argparse.ArgumentError:
            pass


@config
class CMDConfig:
    log: str = field(
        "Logging Level",
        default=logging.INFO,
        required=False,
        action=ParseLoggingAction,
    )


ExtraConfig = NewType("dffml.util.cli.cmd.extra_config", dict)
CMDKeywordArgs = NewType("dffml.util.cli.cmd.kwargs", dict)
CLICMD = NewType("dffml.util.cli.cmd", object)
# TODO CLICMDResults might Union[list, dict] or Any?
CLICMDResults = NewType("dffml.util.cli.cmd.results", dict)


@op
async def run_cli_command(
    self, cmd: CLICMD, extra_config: ExtraConfig, kwargs: CMDKeywordArgs,
) -> CLICMDResults:
    if inspect.isclass(cmd) and issubclass(cmd, CMD):
        # Backwards compatability with old style CLI commands
        cmd = cmd(**kwargs)
        return await cmd.do_run()
    if isinstance(cmd, SystemContext):
        # If the command defined is a system context
        async with self.subflow(cmd) as octx:
            async for ctx, results in octx.run(
                [
                    Input(value=extra_config, definition=ExtraConfig),
                    Input(value=kwargs, definition=CMDKeywordArgs),
                    Input(value=cmd, definition=CLICMD),
                ],
            ):
                return results
    raise TypeError(f"Unknown cmd type. Not sure what to do with cmd: {cmd!r}")


class CMD:
    JSONEncoder = JSONEncoder
    EXTRA_CONFIG_ARGS = {}
    CONFIG = CMDConfig
    ENTRY_POINT_NAME = ["service"]

    def __init__(self, extra_config=None, **kwargs) -> None:
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger(
                "%s.%s"
                % (self.__class__.__module__, self.__class__.__qualname__)
            )
        if extra_config is None:
            extra_config = {}
        self.extra_config = extra_config

        for field in dataclasses.fields(self.CONFIG):
            arg = mkarg(field, dataclass=self.CONFIG)
            if isinstance(arg, Arg):
                if not field.name in kwargs and "default" in arg:
                    kwargs[field.name] = arg["default"]
                if field.name in kwargs and not hasattr(self, field.name):
                    self.logger.debug(
                        "Setting %s = %r", field.name, kwargs[field.name]
                    )
                    setattr(self, field.name, kwargs[field.name])
                else:
                    breakpoint()
                    self.logger.debug("Ignored %s", field.name)

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    @classmethod
    async def parse_args(cls, *args):
        parser = Parser(
            description=cls.__doc__,
            formatter_class=getattr(
                cls,
                "CLI_FORMATTER_CLASS",
                argparse.ArgumentDefaultsHelpFormatter,
            ),
        )
        parser.add_subs(cls)
        return parser, parser.parse_known_args(args)

    async def do_run(self):
        async with self:
            if inspect.isasyncgenfunction(self.run):
                return [res async for res in self.run()]
            else:
                return await self.run()

    @classmethod
    async def cli(cls, *args):
        parser, (args, unknown) = await cls.parse_args(*args)
        async with ConfigLoaders() as configloaders:
            args.extra_config = await parse_unknown(
                *unknown, configloaders=configloaders
            )
        if (
            getattr(cls, "run", None) is not None
            and getattr(args, "cmd", None) is None
        ):
            args.cmd = cls
        if getattr(args, "cmd", None) is None:
            parser.print_help()
            return DisplayHelp
        if not inspect.isfunction(getattr(args.cmd, "run", None)) and not isinstance(args.cmd, SystemContext):
            args.parser.print_help()
            return DisplayHelp
        cmd = args.cmd(**cls.sanitize_args(vars(args)))
        return await cmd.do_run()

    @classmethod
    def sanitize_args(cls, args):
        """
        Remove CMD internals from arguments passed to subclasses of CMD.
        """
        for rm in ["cmd", "parser", "log"]:
            if rm in args:
                del args[rm]
        return args

    @classmethod
    async def _main(cls, *args):
        return await cls.cli(*args)

    @classmethod
    def main(cls, loop=None, argv=sys.argv):
        """
        Runs cli commands in asyncio loop and outputs in appropriate format
        """
        if loop is None:
            # In order to use asyncio.subprocess_create_exec from event loops in
            # non-main threads we have to call asyncio.get_child_watcher(). This
            # is only for Python 3.7
            if (
                sys.version_info.major == 3
                and sys.version_info.minor == 7
                and sys.platform != "win32"
            ):
                asyncio.get_child_watcher()
            # Create a new event loop
            loop = asyncio.get_event_loop()
            # In Python 3.8 ThreadedChildWatcher becomes the default which
            # should work fine for us. However, in Python 3.7 SafeChildWatcher
            # is the default and may cause BlockingIOErrors when many
            # subprocesses are created
            # https://docs.python.org/3/library/asyncio-policy.html#asyncio.FastChildWatcher
            if (
                sys.version_info.major == 3
                and sys.version_info.minor == 7
                and sys.platform != "win32"
            ):
                watcher = asyncio.FastChildWatcher()
                asyncio.set_child_watcher(watcher)
                watcher.attach_loop(loop)
        result = None
        try:
            result = loop.run_until_complete(cls._main(*argv[1:]))

            if (
                result is not None
                and result is not DisplayHelp
                and result is not CMDOutputOverride
                and result != [CMDOutputOverride]
            ):
                json.dump(
                    export_dict(result=result)["result"],
                    sys.stdout,
                    sort_keys=True,
                    indent=4,
                    separators=(",", ": "),
                    cls=cls.JSONEncoder,
                )
                print()
        except KeyboardInterrupt:  # pragma: no cover
            pass  # pragma: no cover
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    def __call__(self):
        return asyncio.run(self.do_run())

    @classmethod
    def args(cls, args, *above) -> Dict[str, Any]:
        """
        For compatibility with scripts/docs.py. Nothing else at the moment so if
        it doesn't work with other things that's why.
        """
        return args

    @classmethod
    def subclass(
        cls, new_class_name: str, field_modifications: Dict[str, Any]
    ) -> "BaseDataFlowFacilitatorObjectContext":
        """
        >>> import sys
        >>> import asyncio
        >>>
        >>> import dffml
        >>> import dffml.cli.dataflow
        >>>
        >>> # The overlayed keyword arguements of fields within to be created
        >>> field_modifications = {
        ...     "dataflow": {"default_factory": lambda: dffml.DataFlow()},
        ...     "simple": {"default": True},
        ...     "stages": {"default_factory": lambda: [dffml.Stage.PROCESSING]},
        ... }
        >>> # Create a derived class
        >>> DiagramForMyDataFlow = dffml.cli.dataflow.Diagram.subclass(
        ...     "DiagramForMyDataFlow", field_modifications,
        ... )
        >>> print(DiagramForMyDataFlow)
        <class 'dffml.util.cli.cmd.DiagramForMyDataFlow'>
        >>> print(DiagramForMyDataFlow.CONFIG)
        <class 'types.DiagramForMyDataFlowConfig'>
        >>> asyncio.run(DiagramForMyDataFlow._main())
        graph TD
        """
        return subclass(cls, new_class_name, field_modifications)
