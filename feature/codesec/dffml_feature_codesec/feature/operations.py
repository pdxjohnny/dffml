import io
import os
import sys
import asyncio
import tempfile
from typing import Dict, Any

import aiohttp
from rpmfile import RPMFile

from dffml.df import op, Stage, Operation, OperationImplementation, \
    OperationImplementationContext

from dffml_feature_git.util.proc import check_output

# pylint: disable=no-name-in-module
from .definitions import URL, \
    RPMObject, \
    rpm_filename, \
    binary, \
    binary_is_PIE

from .log import LOGGER

if sys.platform == 'win32':
    asyncio.set_event_loop(asyncio.ProactorEventLoop())

rpm_url_to_rpmfile = Operation(
    name='rpm_url_to_rpmfile',
    inputs={
        'URL': URL,
    },
    outputs={
        'rpm': RPMObject
    },
    conditions=[])

class RPMURLToRPMFileContext(OperationImplementationContext):

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.debug('Start resp: %s', inputs['URL'])
        async with self.parent.session.get(inputs['URL']) as resp:
            self.logger.debug('Reading resp (%s): %s...', inputs['URL'], resp)
            body = await resp.read()
            self.logger.debug('Done reading resp (%s): %d bytes',
                              inputs['URL'], len(body))
            rpmbody = io.BytesIO(body)
            self.logger.debug('rpmbody: %s', rpmbody)
            try:
                rpm = RPMFile(name=inputs['URL'],
                              fileobj=rpmbody)
            except Exception as error:
                self.logger.debug('Failed to instantiate RPMFile: %s', error)
                return
            self.logger.debug('Created RPM resp: %s', inputs['URL'])
            return {
                'rpm': rpm.__enter__()
            }

class RPMURLToRPMFile(OperationImplementation):

    op = rpm_url_to_rpmfile

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.session = None

    def __call__(self,
                 ctx: 'BaseInputSetContext',
                 ictx: 'BaseInputNetworkContext') \
            -> RPMURLToRPMFileContext:
        return RPMURLToRPMFileContext(self, ctx, ictx)

    async def __aenter__(self) -> 'OperationImplementationContext':
        self.client = aiohttp.ClientSession(trust_env=True)
        self.session = await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.client is not None:
            await self.client.__aexit__(exc_type, exc_value, traceback)
            self.client = None
        self.session = None

@op(inputs={
        'rpm': RPMObject
    },
    outputs={
        'files': rpm_filename
    },
    expand=['files'])
async def files_in_rpm(rpm: RPMFile):
    return {
        'files': list(map(lambda rpminfo: rpminfo.name, rpm.getmembers()))
    }

@op(inputs={
        'rpm': RPMObject,
        'filename': rpm_filename
    },
    outputs={
        'binary': binary
    })
async def binary_file(rpm: RPMFile, filename: str):
    tempf = tempfile.NamedTemporaryFile(delete=False)
    handle = rpm.extractfile(filename)
    sig = handle.read(4)
    if len(sig) != 4 or sig != b'\x7fELF':
        return
    tempf.write(b'\x7fELF')
    tempf.write(handle.read())
    tempf.close()
    return {
        'binary': tempf.name
    }

@op(inputs={
        'binary_path': binary
    },
    outputs={
        'is_pie': binary_is_PIE
    })
async def pwn_checksec(binary_path: str):
    is_pie = False
    try:
        checksec = (await check_output('pwn', 'checksec', binary_path))\
            .split('\n')
        checksec = list(map(lambda line: line.replace(':', '')
                            .strip().split(maxsplit=1),
                            checksec))
        checksec = list(filter(bool, checksec))
        checksec = dict(checksec)
        LOGGER.debug('checksec: %s', checksec)
        is_pie = bool('enabled' in checksec['PIE'])
    except Exception as error:
        LOGGER.info('pwn_checksec: %s', error)
    return {
        'is_pie': is_pie
    }

@op(inputs={
    'rpm': RPMObject
    },
    outputs={},
    stage=Stage.CLEANUP)
async def cleanup_rpm(rpm: RPMFile):
    rpm.__exit__()

@op(inputs={
    'binary_path': binary
    },
    outputs={},
    stage=Stage.CLEANUP)
async def cleanup_binary(binary_path: str):
    os.unlink(binary_path)
