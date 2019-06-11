import io
import tarfile
import hashlib
import tempfile
from typing import Dict, Any

import aiohttp
from dffml.df.types import Definition, Stage
from dffml.df.base import op

from .pypi import package, package_version, package_releases

source_directory = Definition(name="source_directory", primitive="str")


class DownloadHashMismatch(Exception):
    pass  # pragma: no cov

class SourceReleaseNotFound(Exception):
    pass  # pragma: no cov


@op(
    inputs={
        "package": package,
        "version": package_version,
        "releases": package_releases,
    },
    outputs={"source": source_directory},
    imp_enter={
        "session": (lambda self: aiohttp.ClientSession(trust_env=True))
    },
)
async def download_pypi_package(
    self, package: str, version: str, package_releases: Dict[str, Any]
) -> Dict[str, Any]:
    # Each release has a list of objects within it with different URLs for
    # different release types, we want the source release.
    release = list(
        filter(
            lambda release: release["packagetype"] == "source",
            package_releases[version],
        )
    )
    if not release:
        raise SourceReleaseNotFound()

    # Download the package
    async with self.parent.session.get(release['url']) as resp:
        package = await resp.read()
        # Check the hash
        if hashlib.sha256(package).hexdigest() != package['digests']['sha256']:
            raise DownloadHashMismatch()
        # Create the source directory we'll extract to
        source_dir = tempfile.mktempd()
        # Extract the package to the source directory
        with tarfile.open(fileobj=io.BytesIO(package)) as tarobj:
            tarobj.extractall(path=source_dir)
        return {"source": source_dir}

@op(
    inputs={"source": source_directory},
    outputs={},
    stage=Stage.CLEANUP
)
async def cleanup_source_directory(source_dir) -> None:
    """
    Before output operations are run, cleanup operations are run. They free any
    allocated resources that we're created while the context was running.
    """
    shutil.rmtree(source_dir)
