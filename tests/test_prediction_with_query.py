import os
import io
import json
import unittest.mock
import tempfile

from dffml.df.types import DataFlow, Input
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.dataflow import run_dataflow, RunDataFlowConfig
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from tests.test_df import DATAFLOW, add, mult, parse_line
from tests.test_cli import FakeFeature,FakeConfig
from dffml.model.model import ModelContext, Model
from dffml.accuracy import Accuracy as AccuracyType
from typing import List, Dict, Any, Optional, Tuple, AsyncIterator
from dffml.repo import Repo
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig

from dffml.util.entrypoint import entry_point
from dffml.df.mediator import add_ops_to_dataflow
from dffml.df.base import op
from dffml.df.types import Definition,DataFlow
from dffml.operation.model import model_predict,ModelPredictConfig
from dffml.operation.sqlite import SqliteQueryConfig,SqliteDatabase,sqlite_query


# Model
class FakeModelContext(ModelContext):
    async def train(self,*args,**kwargs):
        pass
    async def accuracy(self,*args,**kwargs):
        return AccuracyType(0.5)
    async def predict(self,repos:AsyncIterator[Repo])->AsyncIterator[Repo]:
        async for repo in repos:
            repo.predicted(repo.feature("fake")*10,50)
            yield repo

@entry_point("fake")
class FakeModel(Model):
        CONTEXT = FakeModelContext
        CONFIG = FakeConfig


class TestRunOnDataflow(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        fileno, cls.database_name = tempfile.mkstemp(suffix=".db")
        os.close(fileno)
        cls.sdb = SqliteDatabase(
            SqliteDatabaseConfig(filename=cls.database_name)
        )
        cls.table_name="fakeTable"

    async def test_run(self):
        test_dataflow = DataFlow(
            operations={
                "run_dataflow": run_dataflow.op,
                "get_single": GetSingle.imp.op,
                "model_predict" : model_predict.op,
                # "sqlite_query_create" : sqlite_query.op,
                # "sqlite_query_insert" : sqlite_query.op,
                # "sqlite_query_update" : sqlite_query.op,
                # "sqlite_query_lookup" : sqlite_query.op,

            },
            configs={
                "run_dataflow": RunDataFlowConfig(dataflow=DATAFLOW),
                "model_predict" : ModelPredictConfig(model=FakeModel,msg="Fake Model!"),
                # "sqlite_query_create":SqliteQueryConfig(
                #                     database =self.sdb,
                #                     query_type = "create"
                #                     ),
                # "sqlite_query_insert" :SqliteQueryConfig(
                #                     database =self.sdb,
                #                     query_type = "insert"
                #                     ),
                # "sqlite_query_update":SqliteQueryConfig(
                #                     database =self.sdb,
                #                     query_type = "update"
                #                     ),
                # "sqlite_query_lookup":SqliteQueryConfig(
                #                     database =self.sdb,
                #                     query_type = "lookup"
                #                     )
                } ,
            seed=[
                Input(
                    value=[run_dataflow.op.outputs["results"].name],
                    definition=GetSingle.op.inputs["spec"],
                )
            ],
            implementations = {"model_predict":model_predict.imp}
        )

        definitions=test_dataflow.definitions
        #adding ops to connect current ops in `test dataflow`
        # def _calcToDbInsert(results):
        #     ans = {
        #         "query"
        #     }
        test_inputs = [
            {
                "add_op": [
                    {
                        "value": "add 40 and 2",
                        "definition": parse_line.op.inputs["line"].name,
                    },
                    {
                        "value": [add.op.outputs["sum"].name],
                        "definition": GetSingle.op.inputs["spec"].name,
                    },
                ]
            },
            {
                "mult_op": [
                    {
                        "value": "multiply 42 and 10",
                        "definition": parse_line.op.inputs["line"].name,
                    },
                    {
                        "value": [mult.op.outputs["product"].name],
                        "definition": GetSingle.op.inputs["spec"].name,
                    },
                ]
            },
        ]
        test_outputs = {"add_op": 42, "mult_op": 420}

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(test_dataflow) as octx:
                async for _ctx, results in octx.run(
                    {
                        list(test_input.keys())[0]: [
                            Input(
                                value=test_input,
                                definition=run_dataflow.op.inputs["inputs"],
                            )
                        ]
                        for test_input in test_inputs
                    }
                ):
                    print(results)