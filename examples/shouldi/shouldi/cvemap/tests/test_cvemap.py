import os

from cvemap.cvedb import CVEDB
from cvemap.cvemap import CVEMap

from .log import LOGGER
from .asynctestcase import AsyncTestCase

TESTS_CACHEDIR = os.path.join(os.getcwd(), '.cache')
CVEDB.CACHEDIR = TESTS_CACHEDIR

class TestCVEMapNoContext(AsyncTestCase):

    async def setUp(self):
        self.cvemap = CVEMap(CVEDB())

    def test_00_cachedir(self):
        self.assertEqual(self.cvemap.db.cachedir, TESTS_CACHEDIR)

    def test_01_html_urls(self):
        self.assertIn('https://example.com/p',
                self.cvemap.html_urls('https://example.com/',
                '<a href="/p"></a>'))

class TestCVEMap(AsyncTestCase):

    async def setUp(self):
        self.cvemap = CVEMap(CVEDB())
        await self.cvemap.__aenter__()

    async def tearDown(self):
        await self.cvemap.__aexit__(None, None, None)

    async def test_00_versions(self):
        self.assertIn('v2.6.30-rc6', await self.cvemap.versions(
                'https://git.kernel.org/pub/scm/virt/kvm/kvm.git'))

    async def test_01_versions_bad_url(self):
        self.assertFalse(await self.cvemap.versions('https://example.com'))

    async def test_02_versions_from_urls(self):
        cveid = "CVE-2018-1999018"
        urls = ['https://example.com',
                'https://git.kernel.org/pub/scm/virt/kvm/kvm.git']
        versions = await self.cvemap.versions_from_urls(urls)
        self.assertIn('v2.6.30-rc6',
                versions['https://git.kernel.org/pub/scm/virt/kvm/kvm.git'])

    async def test_03_CVE_2018_1999018(self):
        cveid = "CVE-2018-1999018"
        src_url = await self.cvemap.src_url(cveid)
        self.assertEqual(src_url, 'https://github.com/pydio/pydio-core')

    async def test_04_cves_from_src_url(self):
        url = 'https://github.com/glensc/file'
        cves = [cve async for cve in self.cvemap.cves(url)]
        # At time of writing there were two
        self.assertTrue(cves)
