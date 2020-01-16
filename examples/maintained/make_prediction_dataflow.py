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
    mapping_extract_value,
    create_mapping,
    mapping_merge,
)
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

from feature.git.dffml_feature_git.feature.operations import count_authors,git_commits,work,check_if_valid_git_repository_URL
from feature.git.dffml_feature_git.feature.definitions import *

from dffml.df.base import op
from dffml.operation.output import GroupBy

dataflow_yaml = "./cgi-bin/dataflow.yaml"

#operation to collect features [authors,work,commits] to make features to pass to model
@op(
    inputs = {
        "authors" : count_authors.op.outputs["authors"],
        "work" : work.op.outputs["work"],
        "commits" : git_commits.op.outputs["commits"]
        }
    ,
    outputs ={
        "features" : model_predict.op.inputs["features"]
            }
)
async def collect_maintained_features(authors,work,commits):
    return {
        "features":{
            "authors":authors,
            "work":work,
            "commits":commits
        }
    }

#does outputing same defintion cause context to run twice?
#operation to publish url
@op(inputs={"url":URL},
    outputs={"url":Definition(name="repeated_url",primitive="str")}
    )
async def publish_url(url):
    return {"url":url}

prediction_df = DataFlow(
    operations={
        # "work": work.op,
        # "count_authors": count_authors.op,
        # "git_commits": git_commits.op,
        "get_single": GetSingle.imp.op,
        "model_predict": model_predict.op,
        "mapping_extract_value": mapping_extract_value.op,
        "create_src_url_mapping": create_mapping.op,
        "create_maintained_mapping": create_mapping.op,
        # "create_insert_data": mapping_merge.op,
        "collect_maintained_features":collect_maintained_features.op,
        "publish_url": publish_url.op,
        "group_by" : GroupBy.op
        # "insert_db": db_query_insert.op,
    },
    configs={
        "model_predict": ModelPredictConfig(
            model=DNNClassifierModel(
                DNNClassifierModelConfig(
                    predict=DefFeature("maintained", int, 1),
                    classifications=[0, 1],
                    features=Features(
                        DefFeature("authors", int, 10),
                        DefFeature("commits", int, 10),
                        DefFeature("work", int, 10),
                    ),
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
        Input(
            value=[git_commits.op.outputs["commits"].name],
            definition=GetSingle.op.inputs["spec"]
        ),
        # Input(
        #     value=[collect_maintained_features.op.outputs["features"].name],
        #     definition=GetSingle.op.inputs["spec"]
        # ),
        # Input(
        #     value=[model_predict.op.outputs["prediction"].name],
        #     definition=GetSingle.op.inputs["spec"],
        # ),

        # Input(
        #     value=[create_mapping.op.outputs["mapping"].name],
        #     definition=GetSingle.op.inputs["spec"],
        # ),
        # # model_predict outputs: {'model_predictions': {'maintained':
        # # {'confidence': 0.9989588260650635, 'value': '1'}}}
        # # we need to extract the 'value' from it.
        # Input(
        #     value=["maintained", "value"],
        #     definition=mapping_extract_value.op.inputs["traverse"],
        # ),
        # # Create a key value mapping where the key is "value"
        # # {'maintained': 1}
        # Input(
        #     value="src_url",
        #     definition=create_mapping.op.inputs["key"],
        #     origin="seed.create_src_url_mapping.key",
        # ),
        # Input(
        #     value="maintained",
        #     definition=create_mapping.op.inputs["key"],
        #     origin="seed.create_maintained_mapping.key",
        # ),
        # # The table to insert
        # Input(
        #     value="status",
        #     definition=db_query_insert.op.inputs["table_name"],
        # ),
    ],
    implementations={
        # db_query_insert.op.name: db_query_insert.imp,
    },
)



# # Redirect output of run_dataflow to model_predict
# prediction_df.flow["model_predict"].inputs["features"] = [
#     {"group_by": "output"}
# ]

# prediction_df.flow["mapping_extract_value"].inputs["mapping"] = [
#     {"model_predict": "prediction"}
# ]

# # Create src_url mapping
# prediction_df.flow["create_src_url_mapping"].inputs["key"] = [
#     "seed.create_src_url_mapping.key"
# ]
# prediction_df.flow["create_src_url_mapping"].inputs["value"] = [
#     {"publish_url": "url"}
# ]

# #Create maintined mapping
# prediction_df.flow["create_maintained_mapping"].inputs["key"] = [
#     "seed.create_maintained_mapping.key"
# ]
# prediction_df.flow["create_maintained_mapping"].inputs["value"] = [
#     {"mapping_extract_value": "value"}
# ]

# # Merge src_url and maintained mappings to create data for insert
# prediction_df.flow["create_insert_data"].inputs["one"] = [
#     {"create_src_url_mapping": "mapping"}
# ]
# prediction_df.flow["create_insert_data"].inputs["two"] = [
#     {"create_maintained_mapping": "mapping"}
# ]

# Use key value mapping as data for db insert
# prediction_df.flow["insert_db"].inputs["data"] = [
#     {"create_insert_data": "mapping"},
# ]

prediction_df.update_by_origin()
