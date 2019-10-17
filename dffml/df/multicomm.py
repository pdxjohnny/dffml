import abc
import pathlib
import contextlib
from typing import Union, Tuple, Dict

from ..util.entrypoint import base_entry_point
from ..config.config import BaseConfigLoader
from .base import BaseConfig, BaseDataFlowObjectContext, BaseDataFlowObject
from .types import DataFlow


class MultiCommInAtomicMode(Exception):
    """
    Raised when registration is locked.
    """


class NoConfigsForMultiComm(Exception):
    """
    Raised when no configs are found for the loaded type of multicomm
    """


class NoDataFlows(Exception):
    """
    Raised when no dataflows are found
    """


class BaseCommChannelConfig:
    """
    Config structure for a communication channel. It MUST include a ``dataflow``
    parameter.
    """


class BaseMultiCommContext(BaseDataFlowObjectContext, abc.ABC):
    """
    Abstract Base Class for mutlicomm contexts
    """

    def __init__(self, parent: "BaseMultiComm") -> None:
        self.parent = parent

    @abc.abstractmethod
    async def register(self, config: BaseCommChannelConfig) -> None:
        """
        Register a communication channel with the multicomm context.
        """

    @abc.abstractmethod
    def register_config(self) -> BaseCommChannelConfig:
        """
        Return the config object to be passed to the resigter method
        """

    async def _load_file(
        self,
        parsers: Dict[str, BaseConfigLoader],
        exit_stack: contextlib.AsyncExitStack,
        base_dir: pathlib.Path,
        path: pathlib.Path,
    ) -> Dict:
        """
        Load one file and load the ConfigLoader for it if necessary, using the
        AsyncExitStack provided.
        """
        filetype = path.suffix.replace(".", "")
        # Load the parser for the filetype if it isn't already loaded
        if not filetype in parsers:
            # TODO Get configs for loaders from somewhere, probably the
            # config of the multicomm
            loader_cls = BaseConfigLoader.load(filetype)
            loader = await exit_stack.enter_async_context(
                loader_cls(BaseConfig())
            )
            parsers[filetype] = await exit_stack.enter_async_context(loader())
        # The config will be stored by its unique filepath split on dirs
        config_path = list(path.parts[len(base_dir.parts) :])
        # Get rid of suffix for last member of path
        config_path[-1] = path.stem
        config_path = tuple(config_path)
        # Load the file
        return config_path, await parsers[filetype].loadb(path.read_bytes())

    async def register_directory(
        self, directory: Union[pathlib.Path, str]
    ) -> None:
        """
        Register all configs found in a directory
        """
        # Get the config class for this multicomm
        config_cls: BaseCommChannelConfig = self.register_config()
        # For entering ConfigLoader contexts
        async with contextlib.AsyncExitStack() as exit_stack:
            # Configs for this multicomm
            mc_configs: Dict[Tuple, Union[Dict, BaseCommChannelConfig]] = {}
            df_configs: Dict[Tuple, DataFlow] = {}
            # Convert to pathlib object if not already
            if not isinstance(directory, pathlib.Path):
                directory = pathlib.Path(directory)
            # Load config loaders we'll need as we see their file types
            parsers: Dict[str, BaseConfigLoader] = {}
            # Grab all files containing BaseCommChannelConfigs. Each entry is a
            # BaseCommChannelConfig. However, we don't have its dataflow
            # property. Since that is stored in a separate directory
            mc_dir = pathlib.Path(directory, "mc", self.ENTRY_POINT_LABEL)
            if not mc_dir.is_dir():
                raise NoConfigsForMultiComm(f"In {mc_dir!s}")
            for path in mc_dir.rglob("*"):
                config_path, config = await self._load_file(
                    parsers, exit_stack, mc_dir, path
                )
                mc_configs[config_path] = config
            # Grab all files containing DataFlows
            df_dir = pathlib.Path(directory, "df")
            if not df_dir.is_dir():
                raise NoDataFlows(f"In {df_dir!s}")
            # Load all the DataFlows
            for path in df_dir.rglob("*"):
                config_path, config = await self._load_file(
                    parsers, exit_stack, df_dir, path
                )
                # TODO Provide a way to add overrides via another directory and
                # .update to the original
                df_configs[config_path] = config
                # Now that we have all the dataflow, add it to its respective
                # multicomm config
                mc_configs[config_path]["dataflow"] = config
                # Finally, turn the dict into an object and register it
                mc_configs[config_path] = config_cls._fromdict(
                    **mc_configs[config_path]
                )
                await self.register(mc_configs[config_path])


@base_entry_point("dffml.mutlicomm", "mc")
class BaseMultiComm(BaseDataFlowObject):
    """
    Abstract Base Class for mutlicomms
    """
