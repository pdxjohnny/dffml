import os
import io
import json
import asyncio
import contextlib
import re
import pathlib
from dffml.df.types import DataFlow, Input
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.dataflow import run_dataflow, RunDataFlowConfig
from dffml.operation.output import GetSingle

from dffml.feature.feature import Feature, DefFeature
from dffml.model.model import ModelContext, Model
from dffml.accuracy import Accuracy as AccuracyType
from typing import List, Dict, Any, Optional, Tuple, AsyncIterator
from dffml.repo import Repo
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig
from dffml.feature.feature import Feature, Features

from dffml.util.entrypoint import entrypoint
from dffml.df.base import op
from dffml.df.types import Definition, DataFlow
from dffml.operation.mapping import (
    mapping_expand_all_values,
    mapping_expand_all_keys,
    mapping_extract_value,
    create_mapping,
)
from dffml.operation.array import array_create, array_append
from dffml.operation.model import model_predict, ModelPredictConfig
from dffml.operation.db import (
    DatabaseQueryConfig,
    SqliteDatabase,
    db_query_update,
)
from dffml.config.config import ConfigLoaders
from model.tensorflow.dffml_model_tensorflow.dnnc import (
    DNNClassifierModel,
    DNNClassifierModelConfig,
)


"""
TODO
    * Insert prediction to database
    * make dataflow_yaml general
    * generalize??
    * export dataflow -> predict_dataflow
    * change documentation
"""

dataflow_yaml = "./cgi-bin/dataflow.yaml"

class CustomSqliteDatabase(SqliteDatabase):
    @classmethod
    def sanitize_non_bindable(self, val):
        if not re.match('^[a-zA-Z0-9()_]*$',password):
            raise ValueError(
                f"`{val}` : [a-zA-Z0-9_] characters are only allowed as table,column names"
            )
        return val


async def main():
    async with ConfigLoaders() as cfgl:
        _,data_df = await cfgl.load_file(filepath=dataflow_yaml)
    data_df=DataFlow._fromdict(**data_df)
    prediction_df = DataFlow(
            operations={
                "run_dataflow": run_dataflow.op,
                "get_single": GetSingle.imp.op,
                "model_predict": model_predict.op,
                "mapping_expand_all_values": mapping_expand_all_values.op,
                "mapping_expand_all_keys": mapping_expand_all_keys.op,
                "mapping_extract_value": mapping_extract_value.op,
                "create_value_mapping": create_mapping.op,
                "conditions_array_create": array_create.op,
                "conditions_array_append_1": array_append.op,
                "conditions_array_append_2": array_append.op,
                "conditions_or": array_create.op,
                "conditions_and": array_create.op,
                "update_db": db_query_update.op,
            },
            configs={
                "run_dataflow": RunDataFlowConfig(dataflow=data_df),
                "model_predict": ModelPredictConfig(
                    model = DNNClassifierModel(
                        DNNClassifierModelConfig(
                            predict = DefFeature("maintained",int,1),
                            classifications = [1,1],
                            features= Features(
                                DefFeature("authors",int,10),
                                DefFeature("commits",int,10),
                                DefFeature("work",int,10),
                                )
                            )
                        )
                    ),
                "update_db": DatabaseQueryConfig(
                                database=CustomSqliteDatabase(
                                    SqliteDatabaseConfig(
                                        filename="db.db"
                                        )
                                    )
                                ),
            },
            seed=[
                # Make the output of the dataflow the prediction
                Input(
                    value=[create_mapping.op.outputs["mapping"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                # # model_predict outputs: {'model_predictions': {'maintained':
                # {'confidence': 0.9989588260650635, 'value': '1'}}}
                # # we need to extract the 'value' from it.
                Input(
                    value=["maintained","value"],
                    definition=mapping_extract_value.op.inputs["traverse"],
                ),
                # # Create a key value mapping where the key is "value"
                # # {'maintained': 1}
                Input(
                    value="maintained",
                    definition=create_mapping.op.inputs["key"],
                    origin="seed.create_value_mapping.key",
                ),
                # # Create the conditions array for the db update operation
                Input(
                    value="src_url",
                    definition=array_append.op.inputs["value"],
                    origin="seed.conditions.index.0",
                ),
                Input(
                    value="=",
                    definition=array_append.op.inputs["value"],
                    origin="seed.conditions.index.1",
                ),
                # # The table to update
                Input(
                    value='status',
                    definition=db_query_update.op.inputs["table_name"],
                ),
            ],
            implementations={
                "model_predict": model_predict.imp,
                mapping_expand_all_values.op.name: mapping_expand_all_values.imp,
                mapping_expand_all_keys.op.name: mapping_expand_all_keys.imp,
                create_mapping.op.name: create_mapping.imp,
                mapping_extract_value.op.name: mapping_extract_value.imp,
                array_create.op.name: array_create.imp,
                array_append.op.name: array_append.imp,
                db_query_update.op.name: db_query_update.imp,
            },
        )


        # Redirect output of run_dataflow to model_predict
    prediction_df.flow["mapping_expand_all_keys"].inputs["mapping"] = [
        {"run_dataflow": "results"}
    ]
    prediction_df.flow["mapping_expand_all_values"].inputs["mapping"] = [
        {"run_dataflow": "results"}
    ]
    prediction_df.flow["model_predict"].inputs["features"] = [
        {"mapping_expand_all_values": "value"}
    ]
    prediction_df.flow["mapping_extract_value"].inputs["mapping"] = [
        {"model_predict": "prediction"}
    ]

    # Create value mapping
    prediction_df.flow["create_value_mapping"].inputs["key"] = [
        "seed.create_value_mapping.key"
    ]
    prediction_df.flow["create_value_mapping"].inputs["value"] = [
        {"mapping_extract_value": "value"}
    ]

    # Create db update conditions array
    prediction_df.flow["conditions_array_append_1"].inputs.update(
        {
            "array": [{"conditions_array_create": "array"}],
            "value": ["seed.conditions.index.1"],
        }
    )
    prediction_df.flow["conditions_array_append_2"].inputs.update(
        {
            "array": [{"conditions_array_append_1": "array"}],
            "value": [{"mapping_expand_all_keys": "key"}],
        }
    )
    # Nest the condition array in the
    # ((key = ?) OR (1 = 1)) AND ((1 = 1))
    # Format that the update operation requires
    prediction_df.flow["conditions_or"].inputs.update(
        {"value": [{"conditions_array_append_2": "array"}]}
    )
    prediction_df.flow["conditions_and"].inputs.update(
        {"value": [{"conditions_or": "array"}]}
    )
    # Use key value mapping as data for db update
    prediction_df.flow["update_db"].inputs.update(
        {
            "data": [{"create_value_mapping": "mapping"}],
            "conditions": [{"conditions_and": "array"}],
        }
    )

    prediction_df.update_by_origin()


    test_inputs = [
        {
            "https://github.com/aghinsa/interactive_wall.git": [
                {
                    "value": "https://github.com/aghinsa/interactive_wall.git",
                    "definition": data_df.definitions["URL"].name,
                },

            ]
        }
    ]

    async with MemoryOrchestrator.withconfig({}) as orchestrator:
        async with orchestrator(prediction_df) as octx:
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
                print(f"result are :{results}")



#Run
asyncio.run(main())