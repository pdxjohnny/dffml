import pathlib
from typing import Dict, Any

from ..util.entrypoint import entry_point
from .config import BaseConfigLoaderContext, BaseConfigLoader


class JSONConfigLoaderContext(BaseConfigLoaderContext):
    def load(self, resource: Any) -> Dict:
        if not isinstance(resource, pathlib.Path):
            resource = pathlib.Path(resource)
        return json.loads(resource.read_text())


@entry_point("json")
class JSONConfigLoader(BaseConfigLoader):
    pass
