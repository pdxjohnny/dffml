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
import collections
from itertools import product
from datetime import datetime
from typing import AsyncIterator, Dict, List, Tuple, Any, NamedTuple, Union, \
        get_type_hints, NewType, Optional, Set, Iterator

from dffml.df import *
from dffml.operation.output import GroupBy
from dffml_feature_codesec.feature.operations import *

from dffml_feature_graphing.df.graphing import \
        GraphingMemoryOperationImplementationNetwork

from dffml.util.asynctestcase import AsyncTestCase

OPWRAPED = opwraped_in(sys.modules[__name__])
OPERATIONS = operation_in(sys.modules[__name__]) + \
             list(map(lambda item: item.op, OPWRAPED))
OPIMPS = opimp_in(sys.modules[__name__]) + \
         list(map(lambda item: item.imp, OPWRAPED))

class TestRunner(AsyncTestCase):

    async def test_run(self):
        linker = Linker()
        exported = linker.export(*OPERATIONS)
        definitions, operations, _outputs = linker.resolve(exported)

        repos = [
            'https://download.clearlinux.org/releases/10540/clear/x86_64/os/Packages/sudo-setuid-1.8.17p1-34.x86_64.rpm',
            'https://rpmfind.net/linux/fedora/linux/updates/29/Everything/x86_64/Packages/g/gzip-1.9-9.fc29.x86_64.rpm',
            'https://archives.fedoraproject.org/pub/archive/fedora/linux/releases/20/Everything/x86_64/os/Packages/c/curl-7.32.0-3.fc20.x86_64.rpm'
            ]
        urls = [Input(value=URL,
                      definition=definitions['URL'],
                      parents=False) for URL in repos]

        opimps = {imp.op.name: imp \
                  for imp in \
                  [Imp(BaseConfig()) for Imp in OPIMPS]}

        dff = DataFlowFacilitator(
            input_network = MemoryInputNetwork(BaseConfig()),
            operation_network = MemoryOperationNetwork(
                MemoryOperationNetworkConfig(
                    operations=list(operations.values())
                )
            ),
            lock_network = MemoryLockNetwork(BaseConfig()),
            rchecker = MemoryRedundancyChecker(
                BaseRedundancyCheckerConfig(
                    key_value_store=MemoryKeyValueStore(BaseConfig())
                )
            ),
            opimp_network = GraphingMemoryOperationImplementationNetwork(
                MemoryOperationImplementationNetworkConfig(
                    operations=opimps
                )
            ),
            orchestrator = MemoryOrchestrator(BaseConfig())
        )


        # Orchestrate the running of these operations
        async with dff as dff:
            async with dff() as dffctx:
                # Add our inputs to the input network with the context being the URL
                for url in urls:
                    await dffctx.ictx.add(
                        MemoryInputSet(
                            MemoryInputSetConfig(
                                ctx=StringInputSetContext(url.value),
                                inputs=[url]
                            )
                        )
                    )
                async for ctx, results in dffctx.evaluate():
                    print()
                    print((await ctx.handle()).as_string(),
                          json.dumps(results, sort_keys=True,
                                     indent=4, separators=(',', ':')))
                    print()
                    # self.assertTrue(results)
