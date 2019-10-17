import abc
from typing import Dict, Any

from ..util.entrypoint import base_entry_point
from ..base import (
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)


class BaseConfigLoaderContext(BaseDataFlowFacilitatorObjectContext):
    @abc.abstractmethod
    def load(self, resource: Any) -> Dict:
        """
        ConfigLoaders need to be able to return the dict representation of the
        resources they are asked to load.
        """


@base_entry_point("dffml.config", "config")
class BaseConfigLoader(BaseDataFlowFacilitatorObject):
    pass
