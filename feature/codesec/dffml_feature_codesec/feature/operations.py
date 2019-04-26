import io
import os
import sys
import abc
import glob
import json
import uuid
import shutil
import inspect
import asyncio
import hashlib
import tempfile
import unittest
import itertools
import subprocess
import collections
import asyncio.subprocess
from itertools import product
from datetime import datetime
from contextlib import asynccontextmanager, AsyncExitStack
from typing import AsyncIterator, Dict, List, Tuple, Any, NamedTuple, Union, \
        get_type_hints, NewType, Optional, Set, Iterator

import aiohttp
from rpmfile import RPMFile

from dateutil.relativedelta import relativedelta

from dffml.df import op, Stage, Operation, OperationImplementation, OperationImplementationContext

from .definitions import *

from dffml_feature_git.util.proc import check_output, create, stop, inpath

from .log import LOGGER

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

rpm_url_to_rpmfile = Operation(
    name='rpm_url_to_rpmfile',
    inputs={
        'URL': URL,
    },
    outputs={
        'rpm': RPMObject
    },
    conditions=[]
)

class RPMURLToRPMFileContext(OperationImplementationContext):

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        URL = inputs['URL']
        async with self.parent.session.get(URL) as resp:
            rpm = RPMFile(name=URL,
                          fileobj=io.BytesIO(await resp.read()))
            return {
                    'rpm': rpm.__enter__()
                    }

class RPMURLToRPMFile(OperationImplementation):

    op = rpm_url_to_rpmfile

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
    expand=['files']
)
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
        }
)
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
        'binary': binary
        },
    outputs={
        'is_pie': binary_is_PIE
        },
)
async def pwn_checksec(binary: str):
    is_pie = False
    try:
        checksec = (await check_output('pwn', 'checksec', binary))\
                   .split('\n')
        checksec = list(map(lambda line: line.replace(':', '')\
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
    stage=Stage.CLEANUP
)
async def cleanup_rpm(rpm: RPMFile):
    rpm.__exit__()

@op(inputs={
        'binary': binary
        },
    outputs={},
    stage=Stage.CLEANUP
)
async def cleanup_binary(binary: str):
    os.unlink(binary)
