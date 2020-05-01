import abc
from typing import AsyncIterator, Dict, NewType

from dffml import (
    run,
    DataFlow,
    Input,
    Associate,
    MemoryOrchestratorContextConfig,
)

from ..operations import (
    url_to_urlbytes,
    urlbytes_to_tarfile,
    urlbytes_to_rpmfile,
    files_in_rpm,
    is_binary_pie,
    cleanup_rpm,
)

# Data Types
PackageURL = NewType("PackageURL", str)
BinaryPath = NewType("BinaryPath", bool)


class Distro(abc.ABC):
    """
    Abstract base class which should be implemented to scan a Linux distro
    """

    # Max package URLs to scan at once
    MAX_CTXS: int = 50
    # DataFlow for analysis
    DATAFLOW = DataFlow.auto(
        url_to_urlbytes,
        urlbytes_to_tarfile,
        urlbytes_to_rpmfile,
        files_in_rpm,
        is_binary_pie,
        cleanup_rpm,
        Associate,
    )

    @abc.abstractmethod
    async def packages(self) -> AsyncIterator[PackageURL]:
        """
        Yields URLs of packages within the most recent release of the distro.
        """

    @abc.abstractmethod
    async def report(self) -> Dict[PackageURL, Dict[BinaryPath, bool]]:
        """
        Returns a dictionary mapping package URLs to a dictionary with the keys
        being binaries and the values being a boolean for if that binary is a
        position independent executable.
        """

    async def report(self) -> Dict[PackageURL, Dict[BinaryPath, bool]]:
        return {
            (await ctx.handle()).as_string(): results.get(
                is_binary_pie.op.outputs["is_pie"].name, {}
            )
            async for ctx, results in run(
                MemoryOrchestratorContextConfig(
                    self.DATAFLOW, max_ctxs=self.MAX_CTXS
                ),
                {
                    url: [
                        Input(
                            value=url,
                            definition=url_to_urlbytes.op.inputs["URL"],
                        ),
                        Input(
                            value=[
                                is_binary_pie.op.inputs["filename"].name,
                                is_binary_pie.op.outputs["is_pie"].name,
                            ],
                            definition=Associate.op.inputs["spec"],
                        ),
                    ]
                    async for url in self.packages()
                },
            )
        }
