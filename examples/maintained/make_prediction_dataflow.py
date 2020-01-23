import os
import io
import json
import asyncio
import contextlib
import logging
import re
import pathlib

# logging.basicConfig(level=logging.DEBUG)

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
    mapping_merge,
)
from dffml.operation.array import array_create, array_append
from dffml.operation.model import model_predict, ModelPredictConfig
from dffml.operation.db import (
    DatabaseQueryConfig,
    db_query_insert,
)
from dffml.config.config import ConfigLoaders

from dffml_source_mysql.db import (
    MySQLDatabase,
    MySQLDatabaseConfig,
)

from dffml_model_tensorflow.dnnc import (
    DNNClassifierModel,
    DNNClassifierModelConfig,
)

from feature.git.dffml_feature_git.feature.definitions import *



@op(inputs={"url":URL},
    outputs={"url":Definition(name="repeated_url",primitive="str")}
    )
async def publish_url(url):
    return {"url":url}

@op(inputs={"url":URL},
    outputs={
        "flow_inputs": run_dataflow.op.inputs["inputs"]
    }
)
async def publish_url_as_flow_input(url):
        flow_in =  { 
            url: [
                {
                    "value": url,
                    "definition": URL.name,
                },
            ]
        }
        return {"flow_inputs":flow_in}

async def main():
    dataflow_yaml = "./cgi-bin/dataflow.yaml"
    async with ConfigLoaders() as cfgl:
        _,data_df = await cfgl.load_file(filepath=dataflow_yaml)
    data_df=DataFlow._fromdict(**data_df)

    prediction_df = DataFlow(
            operations={
                "publish_url_as_flow_input" : publish_url_as_flow_input.op,
                "publish_url" : publish_url.op,
                "run_dataflow": run_dataflow.op,
                "get_single": GetSingle.imp.op,
                "model_predict": model_predict.op,
                "mapping_expand_all_values": mapping_expand_all_values.op,
                "mapping_expand_all_keys": mapping_expand_all_keys.op,
                "mapping_extract_value": mapping_extract_value.op,
                "create_src_url_mapping": create_mapping.op,
                "create_maintained_mapping": create_mapping.op,
                "create_insert_data": mapping_merge.op,
                # "insert_db": db_query_insert.op,
            },
            configs={
                "run_dataflow": RunDataFlowConfig(dataflow=data_df),
                "model_predict": ModelPredictConfig(
                    model = DNNClassifierModel(
                        DNNClassifierModelConfig(
                            predict = DefFeature("maintained",int,1),
                            classifications = [0, 1],
                            features= Features(
                                DefFeature("authors",int,10),
                                DefFeature("commits",int,10),
                                DefFeature("work",int,10),
                                )
                            )
                        )
                    ),
                # "insert_db": DatabaseQueryConfig(
                #     database=MySQLDatabase(
                #         MySQLDatabaseConfig(
                #             host="127.0.0.1",
                #             port=3306,
                #             user="user",
                #             password="pass",
                #             db="db",
                #             ca=None,
                #         )
                #     )
                # ),
            },
            seed=[
                # Make the output of the dataflow the prediction

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
                    value="src_url",
                    definition=create_mapping.op.inputs["key"],
                    origin="seed.create_src_url_mapping.key",
                ),
                Input(
                    value="maintained",
                    definition=create_mapping.op.inputs["key"],
                    origin="seed.create_maintained_mapping.key",
                ),
                Input(
                    value=[mapping_merge.op.outputs["mapping"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                # # The table to insert
                # Input(
                #     value='status',
                #     definition=db_query_insert.op.inputs["table_name"],
                # ),
            ],
            implementations={
                # db_query_insert.op.name: db_query_insert.imp,
                "publish_url_as_flow_input" : publish_url_as_flow_input.imp,
                "publish_url" : publish_url.imp,
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

    # Create src_url mapping
    prediction_df.flow["create_src_url_mapping"].inputs["key"] = [
            "seed.create_src_url_mapping.key"
        ]
    prediction_df.flow["create_src_url_mapping"].inputs["value"] = [
            {"mapping_expand_all_keys": "key"}
        ]
    # Create maintined mapping
    prediction_df.flow["create_maintained_mapping"].inputs["key"] = [
            "seed.create_maintained_mapping.key"
        ]
    prediction_df.flow["create_maintained_mapping"].inputs["value"] = [
            {"mapping_extract_value": "value"}
        ]
    # Merge src_url and maintained mappings to create data for insert
    prediction_df.flow["create_insert_data"].inputs["one"] = [
            {"create_src_url_mapping": "mapping"}
        ]
    prediction_df.flow["create_insert_data"].inputs["two"] = [
            {"create_maintained_mapping": "mapping"}
        ]
    # Use key value mapping as data for db insert
    # prediction_df.flow["insert_db"].inputs["data"] = [
    #         {"create_insert_data": "mapping"},
    #     ]

    prediction_df.update_by_origin()

    exported = prediction_df.export()
    DataFlow._fromdict(**exported)
    # TODO fix_export

    # with open('collect_and_predict_df.json','w+') as f:
    #     json.dump(prediction_df.export(),f)

    test_inputs ={
        "interactive_wall": [
            Input(
                value= "https://github.com/aghinsa/interactive_wall.git",
                definition = URL,
            )
        ]
    }

    async with MemoryOrchestrator.withconfig({}) as orchestrator:
        async with orchestrator(prediction_df) as octx:
            async for _ctx, results in octx.run(test_inputs):
                print(f"result are :{results}")

if __name__ == "__main__":
    asyncio.run(main())