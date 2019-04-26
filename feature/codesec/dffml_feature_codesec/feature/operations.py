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

from dffml.df import op, Stage

from .definitions import *

from dffml_feature_git.util.proc import check_output, create, stop, inpath

from .log import LOGGER

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

@op(inputs={
        'URL': URL,
        },
    outputs={
        'binary': binary
        },
    expand=['binary']
)
async def download_and_extract_rpm(URL: str):
    # TODO Make this not an op wrapped so the session can be reused
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(URL) as resp:
            fileobj = io.BytesIO(await resp.read())
            with RPMFile(name=URL, fileobj=fileobj) as rpm:
                binaries = []
                for filename in rpm.getmembers():
                    tempf = tempfile.NamedTemporaryFile(delete=False)
                    handle = rpm.extractfile(filename)
                    sig = handle.read(4)
                    if len(sig) != 4 or sig != b'\x7fELF':
                        continue
                    tempf.write(b'\x7fELF')
                    tempf.write(handle.read())
                    tempf.close()
                    binaries.append(tempf.name)
                return {
                        'binary': binaries
                        }

@op(inputs={
        'binary_path': binary
        },
    outputs={
        'is_pie': binary_is_PIE
        },
)
async def pwn_checksec(binary_path: str):
    is_pie = False
    try:
        checksec = (await check_output('pwn', 'checksec', binary_path)).split('\n')
        checksec = list(map(lambda line: line.replace(':', '')\
                                             .strip().split(maxsplit=1),
                            checksec))
        checksec = list(filter(bool, checksec))
        checksec = dict(checksec)
        is_pie = bool('enabled' in checksec['PIE'])
    except Exception as error:
        LOGGER.info('pwn_checksec: %s', error)
    return {
            'is_pie': is_pie
            }

@op(inputs={
        'binary_path': binary
        },
    outputs={},
    stage=Stage.CLEANUP
)
async def cleanup_binary(binary_path: str):
    os.unlink(binary_path)
    return {}
