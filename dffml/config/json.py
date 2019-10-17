import json
import pathlib
from typing import Dict, Any

from ..util.entrypoint import entry_point
from ..util.cli.arg import Arg
from ..base import BaseConfig
from .config import BaseConfigLoaderContext, BaseConfigLoader


class JSONConfigLoaderContext(BaseConfigLoaderContext):
    def load(self, resource: Any) -> Dict:
        if not isinstance(resource, pathlib.Path):
            resource = pathlib.Path(resource)
        return json.loads(resource.read_text())


@entry_point("json")
class JSONConfigLoader(BaseConfigLoader):
    CONTEXT = JSONConfigLoaderContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return BaseConfig()
