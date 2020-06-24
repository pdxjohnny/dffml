import sys
import asyncio

from cvemap.cvedb import CVEDB
from cvemap.cvemap import CVEMap

async def cli(cveid):
    cvemap = CVEMap(CVEDB())
    async with cvemap:
        print(await cvemap.src_url(cveid))

def main(loop=asyncio.get_event_loop()):
    try:
        loop.run_until_complete(cli(*sys.argv[1:]))
    except KeyboardInterrupt:
        pass
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
