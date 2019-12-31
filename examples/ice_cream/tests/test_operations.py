import sys
import pkg_resources

from dffml.cli.dataflow import RunAllRepos
from dffml.source.source import Sources
from dffml.source.csv import CSVSource, CSVSourceConfig
from dffml.df.types import Input, DataFlow
from dffml.df.base import operation_in, opimp_in, Operation
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from ice_cream.operations import *

OPIMPS = opimp_in(sys.modules[__name__])
PRESIDENTS_CSV = pkg_resources.resource_filename("ice_cream", "presidents.csv")


class TestOperations(AsyncTestCase):
    async def test_run(self):
        # Create the dataflow
        dataflow = DataFlow.auto(*OPIMPS)
        # Specify what we want as the output
        dataflow.seed.append(
            Input(
                value=[TOWN_NAME.name],
                definition=GetSingle.op.inputs['spec'],
            )
        )
        # Scrape the data
        async for result in RunAllRepos(
            repo_def=PERSON_NAME.name,
            dataflow=dataflow,
            sources=Sources(
                CSVSource(
                    CSVSourceConfig(
                        filename=PRESIDENTS_CSV,
                        key='name',
                    ),
                ),
            ),
        ).run():
            print(result)
