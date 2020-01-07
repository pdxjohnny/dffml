import os
import io
import json
import unittest.mock
import tempfile

from dffml.base import config
from dffml.df.types import DataFlow, Input
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.dataflow import run_dataflow, RunDataFlowConfig
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from tests.test_df import DATAFLOW, add, mult, parse_line
from tests.test_cli import FakeFeature
from dffml.feature.feature import Feature, DefFeature
from dffml.model.model import ModelContext, Model
from dffml.accuracy import Accuracy as AccuracyType
from typing import List, Dict, Any, Optional, Tuple, AsyncIterator
from dffml.repo import Repo
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig

from dffml.util.entrypoint import entry_point
from dffml.df.base import op
from dffml.df.types import Definition,DataFlow
from dffml.operation.mapping import mapping_expand_all_values, mapping_expand_all_keys, mapping_extract_value, create_mapping,mapping_formatter
from dffml.operation.model import model_predict,ModelPredictConfig
from dffml.operation.sqlite import SqliteQueryConfig,SqliteDatabase,sqlite_query


@config
class FakeModelConfig:
    feature: Feature


# Model
class FakeModelContext(ModelContext):
    async def train(self,*args,**kwargs):
        pass
    async def accuracy(self,*args,**kwargs):
        return AccuracyType(0.5)
    async def predict(self,repos:AsyncIterator[Repo])->AsyncIterator[Repo]:
        async for repo in repos:
            repo.predicted(
                repo.feature(self.parent.config.feature.NAME) * 10,
                0.5
            )
            yield repo

@entry_point("fake")
class FakeModel(Model):
        CONTEXT = FakeModelContext
        CONFIG = FakeModelConfig


class TestRunOnDataflow(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        fileno, cls.database_name = tempfile.mkstemp(suffix=".db")
        os.close(fileno)
        cls.sdb = SqliteDatabase(
            SqliteDatabaseConfig(filename=cls.database_name)
        )
        cls.table_name="fakeTable"

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.database_name)

    async def setUp(self):
        super().setUp()
        async with SqliteDatabase(SqliteDatabaseConfig(filename=self.database_name)) as db:
            async with db() as ctx:
                await ctx.create_table(self.table_name, {
                    "key": "text",
                    "value": "int",
                })
                await ctx.insert(self.table_name, {"key": "add_op", "value": 0})
                await ctx.insert(self.table_name, {"key": "mult_op", "value": 0})

    async def test_run(self):
        # results = [row async for row in db_ctx.lookup(self.table_name)]

        def _modelPredictToQuery_formatter(data):
            """
             data : {'add_op': 420}
            """

            _key,_val = next(iter(data.items()))

            table_name = self.table_name
            data={"value":_val}
            conditions=[[
                        ["key","=",_key ]
                    ]]
            cols=[]

            return {
                "table_name" : table_name,
                "data" : data,
                "conditions" : conditions,
                "cols" : cols
            }


        test_dataflow = DataFlow(
            operations={
                "run_dataflow": run_dataflow.op,
                "get_single": GetSingle.imp.op,
                "model_predict" : model_predict.op,
                "mapping_expand_all_values": mapping_expand_all_values.op,
                "mapping_expand_all_keys": mapping_expand_all_keys.op,
                "create_mapping": create_mapping.op,
                "mapping_extract_value": mapping_extract_value.op,
                "sqlite_query_update" : sqlite_query.op,
                "mapping_formatter" : mapping_formatter.op
            },
            configs={
                "run_dataflow": RunDataFlowConfig(dataflow=DATAFLOW),
                "model_predict" : ModelPredictConfig(
                    model=FakeModel(
                        FakeModelConfig(
                            feature=DefFeature("result", int, 1),
                        )
                    ),
                    msg="Fake Model!",
                ),
                "sqlite_query_update": SqliteQueryConfig(
                    database=self.sdb,
                    query_type="update"
                ),
            },
            seed=[
                Input(
                    value=[create_mapping.op.outputs["mapping"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=[mapping_formatter.op.outputs["formatted_data"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    # {'confidence': 0.5, 'value': 4200} -> 4200
                    value=["value"],
                    definition=mapping_extract_value.op.inputs["traverse"],
                ),
                Input(
                        value = _modelPredictToQuery_formatter,
                        definition = mapping_formatter.op.inputs["format_function"]
                    )
            ],
            implementations={
                "model_predict" : model_predict.imp,
                mapping_expand_all_values.op.name: mapping_expand_all_values.imp,
                mapping_expand_all_keys.op.name: mapping_expand_all_keys.imp,
                create_mapping.op.name: create_mapping.imp,
                mapping_extract_value.op.name: mapping_extract_value.imp,
                mapping_formatter.op.name : mapping_formatter.imp,
            },
        )
        # Redirect output of run_dataflow to model_predict
        test_dataflow.flow["mapping_expand_all_keys"].inputs["mapping"] = \
                [{"run_dataflow": "results"}]
        test_dataflow.flow["mapping_expand_all_values"].inputs["mapping"] = \
                [{"run_dataflow": "results"}]
        test_dataflow.flow["model_predict"].inputs["features"] = \
                [{"mapping_expand_all_values": "value"}]
        test_dataflow.flow["mapping_extract_value"].inputs["mapping"] = \
                [{"model_predict": "prediction"}]
        test_dataflow.flow["create_mapping"].inputs["value"] = \
                [{"mapping_extract_value": "value"}]


        # test_dataflow.flow["mapping_expand_all_values"].inputs["mapping"] = \
        #         [{"mapping_formatter": "formated_data"}]


        test_dataflow.update_by_origin()

        definitions=test_dataflow.definitions

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

        async with SqliteDatabase(SqliteDatabaseConfig(filename=self.database_name)) as db:
            async with db() as db_ctx:
                results = [row async for row in db_ctx.lookup(self.table_name)]
                print(f"Final lookup : {results}\n")
