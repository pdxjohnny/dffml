import abc
from typing import Dict, Any

from ..util.entrypoint import base_entry_point
from ..base import (
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)


class BaseConfigLoaderContext(BaseDataFlowFacilitatorObjectContext):
    def __init__(self, parent: "BaseConfigLoader") -> None:
        super().__init__()
        self.parent = parent

    @abc.abstractmethod
    def load(self, resource: Any) -> Dict:
        """
        ConfigLoaders need to be able to return the dict representation of the
        resources they are asked to load.
        """


@base_entry_point("dffml.config", "config")
class BaseConfigLoader(BaseDataFlowFacilitatorObject):
    def __call__(self) -> BaseConfigLoaderContext:
        return self.CONTEXT(self)
