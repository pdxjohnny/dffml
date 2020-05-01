import re
import os
from typing import AsyncIterator, Dict, NewType

import aiohttp
from bs4 import BeautifulSoup

from .base import Distro, PackageURL, BinaryPath


class ClearLinux(Distro):
    PACKAGE_LIST_URL = os.environ.get(
        "PACKAGE_LIST_URL",
        "https://download.clearlinux.org/current/x86_64/os/Packages/",
    )

    async def packages(self) -> AsyncIterator[PackageURL]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PACKAGE_LIST_URL) as resp:
                soup = BeautifulSoup(await resp.text(), features="html.parser")
                for link in soup.find_all("a", href=re.compile(".rpm")):
                    yield self.PACKAGE_LIST_URL + link["href"]
