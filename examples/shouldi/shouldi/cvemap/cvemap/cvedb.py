'''
Retrieval access and caching of NIST CVE database
'''
import os
import re
import gzip
import json
import glob
import asyncio
import hashlib
import logging

import aiohttp
from aiohttp import web
from bs4 import BeautifulSoup

from .log import LOGGER

class CVEDB(object):

    CACHEDIR = os.path.join(os.path.expanduser('~'), '.cache')
    FEED = 'https://nvd.nist.gov/vuln/data-feeds'
    LOGGER = LOGGER.getChild('CVEDB')

    def __init__(self, verify = True):
        self.feed = self.FEED
        self.cachedir = self.CACHEDIR
        self.lock = asyncio.Lock()
        self.dataset = {}
        self.session = None
        self.verify = verify

    async def getmeta(self, session, metaurl):
        async with session.get(metaurl) as response:
            return metaurl.replace('.meta', '.json.gz'), \
                    dict([line.split(':', maxsplit=1) \
                    for line in (await response.text()).split('\r\n') \
                    if ':' in line])

    async def nist_scrape(self, session, feed):
        async with session.get(feed) as response:
            page = await response.text()
            data = BeautifulSoup(page, 'html.parser')
            jsonmetalinks = [project.get('href') for project in \
                    data.find_all(href=re.compile('/json/.*.meta'))]
            return dict(await asyncio.gather(*[
                self.getmeta(session, metaurl) for metaurl in jsonmetalinks]))

    async def refresh(self, session):
        if not os.path.isdir(self.cachedir):
            os.makedirs(self.cachedir)
        update = await self.nist_scrape(session, self.feed)
        await asyncio.gather(*[self.cache_update(session, url, meta['sha256']) \
                for url, meta in update.items()])

    async def cache_update(self, session, url, sha):
        filename = url.split('/')[-1].replace('.gz', '')
        filepath = os.path.join(self.cachedir, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as handle:
                if self.sha_validate(url, sha, handle.read()):
                    handle.seek(0)
                    await self.dataset_load(filename, handle.read().decode())
                    return
        self.LOGGER.info('Updating CVE cache for %s', filename)
        async with session.get(url) as response:
            jsondata = gzip.decompress(await response.read())
            if not self.sha_validate(url, sha, jsondata):
                return
            with open(filepath, 'wb') as handle:
                handle.write(jsondata)
            await self.dataset_load(filename, jsondata)

    def sha_validate(self, key, sha, data):
        sha = sha.upper()
        gotsha = hashlib.sha256(data).hexdigest().upper()
        if gotsha != sha:
            self.LOGGER.critical('SHA mismatch for %s '
                                 '(have: %r, want: %r)', key, gotsha, sha)
            return False
        return True

    async def dataset_load(self, key, jsondata):
        data = json.loads(jsondata)
        async with self.lock:
            for cve in data['CVE_Items']:
                self.dataset[cve['cve']['CVE_data_meta']['ID']] = cve
        self.LOGGER.debug('Loaded %s(%d) into %s.dataset', key,
                          len(data['CVE_Items']), self.__class__.__qualname__)

    async def load_no_verify(self):
        for filepath in glob.glob(os.path.join(self.cachedir, '*')):
            if os.path.isfile(filepath):
                with open(filepath, 'rb') as handle:
                    await self.dataset_load(filepath, handle.read().decode())

    async def cve(self, cveid):
        return self.dataset[cveid]

    async def cves(self):
        for cveID, cve in self.dataset.items():
            yield cveID, cve

    async def __aenter__(self):
        client = aiohttp.ClientSession(trust_env=True)
        self.session = await client.__aenter__()
        if not self.verify:
            self.LOGGER.warning('Not verifying CVE DB cache')
            await self.load_no_verify()
        else:
            await self.refresh(self.session)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.__aexit__(exc_type, exc_value, traceback)

class Server(object):

    def __init__(self, addr = '127.0.0.1', port = 0):
        self.addr = addr
        self.port = port
        self.cvedb = CVEDB()
        self.runner = None

    async def web_cves(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for cve in request.app['cvedb'].cves():
            await ws.send_json(cve)
        await ws.close()
        return ws

    async def web_cve(self, request):
        cve = await request.app['cvedb'].cve(request.match_info['cveid'])
        return web.json_response(cve)

    async def __aenter__(self):
        await self.cvedb.__aenter__()
        app = web.Application()
        app['cvedb'] = self.cvedb
        app.add_routes([
            web.get('/cves', self.web_cves),
            web.get('/cve/{cveid}', self.web_cve),
        ])
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.addr, self.port)
        await site.start()
        self.port = self.runner.addresses[0][1]
        LOGGER.info('Serving on %s:%d', self.addr, self.port)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.cvedb.__aexit__(exc_type, exc_value, traceback)
        await self.runner.cleanup()

    @classmethod
    async def run_forever(cls, *args, **kwargs):
        async with cls(*args, **kwargs):
            while True:
                await asyncio.sleep(60)

    @classmethod
    def start(cls, *args, loop = asyncio.get_event_loop(), **kwargs):
        logging.basicConfig(level=logging.DEBUG)
        try:
            loop.run_until_complete(cls.run_forever(*args, **kwargs))
        except KeyboardInterrupt:
            pass
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

class Client(object):

    def __init__(self, server, **kwargs):
        self.server = server
        self.session = None
        self.client_args = kwargs

    async def __aenter__(self):
        client = aiohttp.ClientSession(**self.client_args)
        self.session = await client.__aenter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.__aexit__(exc_type, exc_value, traceback)

    async def cve(self, cveid):
        async with self.session.get(self.server + '/cve/' + cveid) as response:
            return await response.json()

    async def cves(self):
        async with self.session.ws_connect(self.server + '/cves') as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    yield json.loads(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
            await ws.close()
