import socket
from http import HTTPStatus
from urllib.parse import urlparse
from contextlib import asynccontextmanager

from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from aiohttp import web
from aiohttp import client
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
import aiohttp
import asyncio

from dffml.log import LOGGER

import logging
logging.basicConfig(level=logging.DEBUG)

# From StackOverflow: https://stackoverflow.com/a/52403071
class ReverseProxyHandlerContext(object):

    def __init__(self,
                 parent: 'ReverseProxyHandler',
                 *,
                 hostname: str = None,
                 address: str = '127.0.0.1',
                 port: int = 0) -> None:
        '''
        Hostname must be set in order to resolve subdomains
        '''
        self.parent = parent
        self.hostname = 'localhost' if hostname is None else hostname
        self.address = address
        self.port = port
        self.upstream = {}
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    async def wsforward(self, ws_from, ws_to):
        async for msg in ws_from:
            self.logger.info('>>> msg: %s', msg)
            if msg.type == aiohttp.WSMsgType.TEXT:
                await ws_to.send_str(msg.data)
            elif msg.type == aiohttp.WSMsgType.BINARY:
                await ws_to.send_bytes(msg.data)
            elif msg.type == aiohttp.WSMsgType.PING:
                await ws_to.ping()
            elif msg.type == aiohttp.WSMsgType.PONG:
                await ws_to.pong()
            elif ws_to.closed:
                await ws_to.close(code=ws_to.close_code, message=msg.extra)
            else:
                raise ValueError('Unexpected message type: %s' % (msg,))

    def subdomain(self, headers):
        '''
        Helper method for accessing subdomain protion of Host header. Returns
        None if header not present or subdomain not present.
        '''
        host = headers.get('host', False)
        if not host:
            return None
        if not '.' in host:
            return None
        # Check for port
        if ':' in host:
            host, _port = host.split(':')
        # Check to see if host is an ip address. If so then then bail
        if all(map(lambda part: part.isdigit(), host.split('.', maxsplit=4))):
            return None
        # Ensure hostname is present
        if not self.hostname in host:
            return None
        # Discard hostname
        host = host[:host.index(self.hostname)]
        # Split on .
        host = list(filter(lambda part: bool(len(part)), host.split('.')))
        return '.'.join(host)

    async def handler_proxy(self, req):
        headers = req.headers.copy()
        self.logger.debug('headers: %s', headers)

        subdomain = self.subdomain(headers)
        path = req.path
        self.logger.debug('subdomain: %r, path: %r', subdomain, path)

        upstream = self.get_upstream(subdomain, path)
        if not upstream:
            return web.Response(status=HTTPStatus.NOT_FOUND)

        if 'connection' in headers \
                and 'upgrade' in headers \
                and headers['connection'] == 'Upgrade' \
                and headers['upgrade'] == 'websocket' and req.method == 'GET':
            # Handle websocket proxy
            ws_server = web.WebSocketResponse()
            await ws_server.prepare(req)
            self.logger.info('##### WS_SERVER %s', ws_server)

            client_session = aiohttp.ClientSession(cookies=req.cookies)
            async with client_session.ws_connect(
              baseUrl+req.path_qs,
            ) as ws_client:
              self.logger.info('##### WS_CLIENT %s', ws_client)

              coro = asyncio.wait([
                      wsforward(ws_server,ws_client),
                      wsforward(ws_client,ws_server)
                  ],
                  return_when=asyncio.FIRST_COMPLETED)
              # TODO replace with
              # https://aiohttp.readthedocs.io/en/stable/web_advanced.html#background-tasks
              finished,unfinished = await coro

              return ws_server
        else:
            # Handle regular HTTP request proxy
            self.logger.debug('upstream for (%r): %s', upstream,
                              (subdomain, path,))
            async with client.request(
                req.method,
                upstream,
                headers=headers,
                allow_redirects=False,
                data=await req.read()
            ) as res:
                self.logger.debug('upstream url(%s) status: %d', upstream,
                                  res.status)
                return web.Response(
                  headers=res.headers,
                  status=res.status,
                  body=await res.read()
                )
            return ws_server

    def set_upstream(self,
                     url: str,
                     subdomain: str,
                     path: str):
        if not subdomain in self.upstream:
            self.upstream[subdomain] = {}
        self.upstream[subdomain][path] = url

    def get_upstream(self,
                     subdomain: str,
                     path: str):
        paths = self.upstream.get(subdomain, {})
        if not paths:
            return False
        longest_match = ''
        for local_path, upstream in paths.items():
            if path.startswith(local_path) \
                    and len(local_path) > len(longest_match):
                longest_match = local_path
        if not longest_match:
            return False
        upstream = urlparse(paths[longest_match])
        upstream = upstream._replace(path=path.replace(longest_match, upstream.path))
        return upstream.geturl()

    async def __aenter__(self) -> 'ReverseProxyHandlerContext':
        self.app = web.Application()
        self.app.router.add_route('*', '/{path:.*}', self.handler_proxy)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.address, self.port)
        await self.site.start()
        self.address, self.port = self.site._server.sockets[0].getsockname()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.site.stop()
        await self.runner.cleanup()

class ReverseProxyHandler(object):

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    def __call__(self, hostname=None, address='127.0.0.1', port=0) \
            -> 'ReverseProxyHandlerContext':
        return ReverseProxyHandlerContext(self,
                                          hostname=hostname,
                                          address=address,
                                          port=port)

@asynccontextmanager
async def rproxy(self, upstream_path, subdomain, path):
    rproxyh = ReverseProxyHandler(BaseConfig())
    async with rproxyh('localhost') as ctx:
        ctx.set_upstream('http://%s:%d%s' % \
                         (self.server.host, self.server.port, upstream_path,),
                         subdomain='test',
                         path='/route/this')
        yield ctx

class TestReverseProxyHandler(AioHTTPTestCase):

    TEST_ADDRESS = 'localhost'
    PROXY_SUBDOMAIN = 'test'
    PROXY_PATH = '/route/this'
    UPSTREAM_PATH = '/to/here'

    async def get_application(self):
        async def hello(request):
            return web.Response(text=request.path)
        app = web.Application()
        app.router.add_get(self.UPSTREAM_PATH + '{path:.*}', hello)
        return app

    @unittest_run_loop
    async def test_not_found(self):
        async with rproxy(self,
                          self.UPSTREAM_PATH,
                          subdomain=self.PROXY_SUBDOMAIN,
                          path=self.PROXY_PATH) as rctx, \
                aiohttp.ClientSession() as session:
            url = 'http://%s.%s:%d%s' % \
                  (self.PROXY_SUBDOMAIN + '.not.found',
                   self.TEST_ADDRESS,
                   rctx.port,
                   self.PROXY_PATH,)
            LOGGER.debug('rproxy url: %s', url)
            async with session.get(url) as resp:
                self.assertEqual(resp.status, HTTPStatus.NOT_FOUND)

    @unittest_run_loop
    async def test_path(self):
        async with rproxy(self,
                          self.UPSTREAM_PATH,
                          subdomain=self.PROXY_SUBDOMAIN,
                          path=self.PROXY_PATH) as rctx, \
                aiohttp.ClientSession() as session:
            url = 'http://%s.%s:%d%s' % \
                  (self.PROXY_SUBDOMAIN,
                   self.TEST_ADDRESS,
                   rctx.port,
                   self.PROXY_PATH,)
            LOGGER.debug('rproxy url: %s', url)
            async with session.get(url) as resp:
                self.assertEqual(resp.status, HTTPStatus.OK)
                text = await resp.text()
                self.assertEqual(self.UPSTREAM_PATH, text)

    @unittest_run_loop
    async def test_path_joined(self):
        async with rproxy(self,
                          self.UPSTREAM_PATH,
                          subdomain=self.PROXY_SUBDOMAIN,
                          path=self.PROXY_PATH) as rctx, \
                aiohttp.ClientSession() as session:
            url = 'http://%s.%s:%d%s' % \
                  (self.PROXY_SUBDOMAIN,
                   self.TEST_ADDRESS,
                   rctx.port,
                   self.PROXY_PATH + '/test/joined',)
            LOGGER.debug('rproxy url: %s', url)
            async with session.get(url) as resp:
                self.assertEqual(resp.status, HTTPStatus.OK)
                text = await resp.text()
                self.assertEqual(self.UPSTREAM_PATH + '/test/joined', text)
