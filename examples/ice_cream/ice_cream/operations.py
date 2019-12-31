import shutil
import tempfile
from typing import Dict, Any

import aiohttp

from dffml.df.base import op
from dffml.df.types import Definition

PERSON_NAME = Definition(name="person_name", primitive="string")
TOWN_NAME = Definition(name="town_name", primitive="string")


@op(
    inputs={"name": PERSON_NAME},
    outputs={"town": TOWN_NAME},
    # imp_enter allows us to create instances of objects which are async context
    # managers and assign them to self.parent which is an object of type
    # OperationImplementation which will be alive for the lifetime of the
    # Orchestrator which runs all these operations.
    imp_enter={
        "session": (lambda self: aiohttp.ClientSession(trust_env=True))
    },
)
async def wikipedia_hometown(self, name: str) -> Dict[str, Any]:
    """
    Download the information on the package in JSON format.
    """
    url = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
    async with self.parent.session.get(url) as resp:
        if resp.status != 200:
            return
        text = await resp.text()
        # Find the box that says when they were born
        if not 'Born</th>' in text:
            return
        start = text.index('Born</th>')
        text = text[start:]
        # The next link will be the link to the place they were born
        # <a href="..." title="Port Conway, Virginia">Port...
        title = 'title="'
        if not title in text:
            return
        # Go to the end of title="
        start = text.index(title) + len(title)
        text = text[start:]
        # Now go until the next qoute to get just the name
        # Port Conway, Virginia">Port...
        if not '"' in text:
            return
        # Port Conway, Virginia
        return {"town": text[:text.index('"')]}
