import io
import json
import unittest.mock

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

from dffml.util.entrypoint import entry_point
from dffml.operation.mediator import mediator
from dffml.df.base import op
from dffml.df.types import Definition,DataFlow

fakeDefinition=Definition(name="fakeDefinition",primitive="Dict[str:Any]")

@op(
    name="fake_op",
    inputs={
        "fake_inputs":fakeDefinition
        },
    outputs={}
)
def fake_op(fake_inputs):
    print("\n\n fake_op ran \n\n")
    print(f"Prining fake inputs : \n{fake_inputs}\n")


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
class FakeModel:
        CONTEXT = FakeModelContext
        CONFIG = FakeConfig

class TestRunOnDataflow(AsyncTestCase):
    async def test_run(self):
        test_dataflow = DataFlow(
            operations={
                "run_dataflow": run_dataflow.op,
                "get_single": GetSingle.imp.op,
                "fake_op" : fake_op.op
            },
            configs={"run_dataflow": RunDataFlowConfig(dataflow=DATAFLOW)},
            seed=[
                Input(
                    value=[run_dataflow.op.outputs["results"].name],
                    definition=GetSingle.op.inputs["spec"],
                )
            ],
            implementations={"fake_op":fake_op.imp}

        )

        #mediating
        def _calcToFake(results):
            return {
                "fake_inputs":results
            }

        mapping_data={
            "calcToFake":
                {
                    'input_types' : [
                            ('results','flow_results')
                    ],
                    'output_types' : [('fake_inputs','fakeDefinition')],
                    'redirect_function' : _calcToFake
                }
        }

        test_dataflow2=mediator(dataflow=test_dataflow,
                    mapping_data=mapping_data,
                    )

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
            async with orchestrator(test_dataflow2) as octx:
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