import os
import re
import time
import json
import asyncio
import itertools
import urllib.parse
import concurrent.futures._base as base
from asyncio.subprocess import PIPE
from contextlib import contextmanager

import aiohttp
from bs4 import BeautifulSoup

from .log import LOGGER

@contextmanager
def timeit(name):
    start = time.monotonic()
    yield
    end = time.monotonic()
    LOGGER.debug('%s took %.2f seconds', name, end - start)

# TODO Deceiving name no longer uses sem
async def withsem(sem, coro, key=None):
    if not key is None:
        return key, await coro
    return await coro

class CVEMap(object):

    TIMEOUT = 60
    LINK_RE = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    def __init__(self, db):
        self.db = db
        self.timeout = self.TIMEOUT
        self.session = None

    async def __aenter__(self):
        client = aiohttp.ClientSession(trust_env=True)
        self.session = await client.__aenter__()
        await self.db.__aenter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.__aexit__(exc_type, exc_value, traceback)
        await self.db.__aexit__(exc_type, exc_value, traceback)

    async def src_url(self, cveid):
        cve = await self.db.cve(cveid)
        urls = await self.scrape_urls([ref['url'] for ref in \
                cve['cve']['references']['reference_data']])
        possible = await self.versions_from_urls(urls)
        vendors = cve['cve']['affects']['vendor']['vendor_data']
        products = list(itertools.chain(*[vendor['product']['product_data'] \
                for vendor in vendors]))
        versions = {product['product_name']: [version['version_value'] \
                        for version in product['version']['version_data']] \
                        for product in products}
        most_likely = {}
        for url, tags in possible.items():
            for tag in tags:
                for name, affected in versions.items():
                    for version in affected:
                        if version in tag:
                            most_likely[url] = name
        if not most_likely:
            return None
        if len(most_likely) == 1:
            return list(most_likely.keys())[0]
        LOGGER.warning('Multiple possible matches for %s: %r', cveid,
                most_likely)
        for url, name in most_likely.items():
            # TODO rank and return most likely
            if name in url:
                return url
        return None

    async def versions_from_urls(self, urls):
        sem = asyncio.Semaphore(value=len(os.sched_getaffinity(0)))
        versions = await asyncio.gather(*[
            withsem(sem, self.versions(url), key=url) for url in urls])
        return dict(versions)

    async def scrape_urls(self, urls):
        sem = asyncio.Semaphore(value=len(os.sched_getaffinity(0)))
        all_urls = [] + urls
        for _ in range(0, 3):
            urls = list(itertools.chain(*(await asyncio.gather(*[
                withsem(sem, self.find_urls(url)) for url in urls]))))
            all_urls += urls
        return list(set(all_urls))

    async def find_urls(self, url):
        try:
            async with self.session.get(url, timeout=self.timeout) as response:
                ctype = response.headers.get('Content-Type', '').lower()
                length = response.headers.get('content-length', '0')
                length = int(response.headers.get('Content-Length', length))
                if response.status != 200 or length > (2 * 1024 * 1024) \
                        or not [check for check in ['text/html', 'text/plain'] \
                        if check in ctype]:
                    return []
                page = await response.text()
                with timeit('parsing'):
                    return self.urls_from_bytes(url, page)
        except Exception as error:
            LOGGER.debug('Error getting url %r: %s', url, error)
            return []

    def urls_from_bytes(self, url, page):
        return [url for url in self._urls_from_bytes(url, page) \
                if self.veturl(url)]

    def veturl(self, url):
        for check in ['mitre.org', 'nist.gov', 'facebook.com', 'twitter.com']:
            if check in url:
                return False
        return True

    def _urls_from_bytes(self, url, page):
        htmlurls = list(self.html_urls(url, page))
        if htmlurls:
            return htmlurls
        return self.LINK_RE.findall(page)

    def html_urls(self, url, page):
        soup = BeautifulSoup(page, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href.startswith('/'):
                href = urllib.parse.urljoin(url, href)
            if not '://' in href:
                continue
            yield href

    async def versions(self, url):
        return await self.versions_git(url)

    async def http_git_tags(self, url):
        try:
            joined = (url + '/info/refs?service=git-upload-pack')
            async with self.session.get(joined, timeout=self.timeout,
                                        headers={'User-Agent': 'git/2.14.1'}) as response:
                length = response.headers.get('content-length', '0')
                length = int(response.headers.get('Content-Length', length))
                if response.status != 200 or length > (2 * 1024 * 1024):
                    return []
                return self.parse_refs(await response.text())
        except Exception as error:
            LOGGER.debug('Error getting url %r: %s', url, error)
            return []

    async def versions_git(self, url):
        if url.startswith('http://') or url.startswith('https://'):
            return await self.http_git_tags(url)
        if not url.startswith('git://') and not url.startswith('ssh://'):
            LOGGER.warning('Bad url: %r', url)
            return []
        stdout = None
        env = os.environ.copy()
        env['git_askpass'] = 'echo'
        proc = await asyncio.create_subprocess_exec('git',
                                                    'ls-remote',
                                                    '--tags',
                                                    url,
                                                    env=env,
                                                    start_new_session=True,
                                                    stdout=PIPE,
                                                    stderr=PIPE)
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(),
                                                    timeout=self.timeout)
        except base.TimeoutError:
            pass
        try:
            proc.kill()
        except:
            pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=self.timeout)
        except base.TimeoutError:
            return []
        if stdout is None or not len(stdout):
            return []
        return self.parse_refs(stdout)

    def parse_refs(self, refs):
        return list(set([ref.split('/')[-1]\
                .replace('^{}', '')\
                for ref in refs.split('\n') \
                if 'refs/tags/' in ref]))

    async def cves(self, src_url):
        # TODO Split URL into parts and search through all the CVEs for ones
        # that look like they contain data associated with our URL
        async for cve in self.db.cves():
            if src_url in json.dumps(cve):
                yield cve
