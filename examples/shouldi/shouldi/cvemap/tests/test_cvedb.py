import os
import aiohttp

from cvemap.cvedb import CVEDB, Server, Client

from .asynctestcase import AsyncTestCase

TESTS_CACHEDIR = os.path.join(os.getcwd(), '.cache')
CVEDB.CACHEDIR = TESTS_CACHEDIR

class TestCVEDB(AsyncTestCase):

    def setUp(self):
        self.cvedb = CVEDB()

    def test_00_cachedir(self):
        self.assertEqual(self.cvedb.cachedir, TESTS_CACHEDIR)

    async def test_01_getmeta(self):
        async with aiohttp.ClientSession(trust_env=True) as session:
            jsonurl, meta = await self.cvedb.getmeta(session,
                    'https://nvd.nist.gov/feeds/json/cve/1.0/nvdcve-1.0-modified.meta')
            self.assertIn('sha256', meta)

    async def test_02_nist_scrape(self):
        async with aiohttp.ClientSession(trust_env=True) as session:
            jsonshas = await self.cvedb.nist_scrape(session, self.cvedb.feed)
            self.assertIn('https://nvd.nist.gov/feeds/json/cve/1.0/nvdcve-1.0-2015.json.gz',
                    jsonshas)

    async def test_03_refesh(self):
        async with aiohttp.ClientSession(trust_env=True) as session:
            await self.cvedb.refresh(session)
            self.assertEqual(self.cvedb.cachedir, TESTS_CACHEDIR)

    async def test_04_verify_false(self):
        self.cvedb.verify = False
        async with self.cvedb:
            self.assertTrue(self.cvedb.dataset)

class TestClient(AsyncTestCase):

    async def setUp(self):
        self.server = Server()
        await self.server.__aenter__()
        self.client = Client('http://localhost:%d' % (self.server.port,))
        await self.client.__aenter__()

    async def tearDown(self):
        await self.client.__aexit__(None, None, None)
        await self.server.__aexit__(None, None, None)

    async def test_00_cve(self):
        self.assertTrue(await self.client.cve('CVE-2014-1943'))

    async def test_01_cves(self):
        self.assertTrue(len([cve async for cve in self.client.cves()]))
