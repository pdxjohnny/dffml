import copy
import math
import urllib.parse
from typing import List, Dict, Any

from dffml.df.base import op
from dffml.operation.mapping import MAPPING

import aiohttp

from dffml.df.types import Definition

URL = Definition(name="URL", primitive="string")
IMAGE_NAME = Definition(name="DOCKER_IMAGE", primitive="string")


@op(
    inputs={"url": URL},
    outputs={"mapping": MAPPING},
    imp_enter={
        "session": (lambda self: aiohttp.ClientSession(trust_env=True))
    },
)
async def url_to_mapping(self, url: str) -> Dict[str, Any]:
    """
    Make a GET request to a URL and retrive the reponse as an array of bytes.
    """
    async with self.parent.session.get(url) as resp:
        return {"mapping": await resp.json()}


@op(
    inputs={"page": MAPPING},
    outputs={"urls": URL, "images": IMAGE_NAME},
    expand=["urls", "images"],
)
def dockerhub_scrape_page(page: Dict) -> Dict[str, Any]:
    images: List[str] = []
    for summary in page["summaries"]:
        images.append(summary["slug"])
    # If we're on the first page, calculate the urls of all the rest of the
    # pages so that they can be requested all at once
    if page["page"] == 1 and page["next"]:
        pages = math.ceil(page["count"] / page["page_size"])
        urls = []
        url = urllib.parse.urlparse(page["next"])
        query = urllib.parse.parse_qs(url.query)
        for i in range(2, pages + 1):
            replace = copy.deepcopy(query)
            for key, value in replace.items():
                replace[key] = value[0]
            replace["page"] = str(i)
            urls.append(
                url._replace(query=urllib.parse.urlencode(replace)).geturl()
            )
        return {"urls": urls, "images": images}
    return {"images": images}
