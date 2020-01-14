import os
import io
import json
import asyncio
import contextlib
import logging
import re
import pathlib

logging.basicConfig(level=logging.DEBUG)

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


"""
TODO
    * Insert prediction to database
    * make dataflow_yaml general
    * generalize??
    * export dataflow -> predict_dataflow
    * change documentation
"""

prediction_df_yaml = "./cgi-bin/prediction_dataflow.dirconf.yaml"

async def main():
    async with ConfigLoaders() as cfgl:
        _, prediction_df = await cfgl.load_file(filepath=prediction_df_yaml)
        prediction_df = DataFlow._fromdict(**prediction_df)

    # TODO It looks like it's loading the outer dataflow properly, but not the
    # inner (not converting into DataFlow object) this is somewhat to be
    # expected, since the code above is what's doing the loading. This needs to
    # be sorted out.
    print(prediction_df)

    test_inputs = [
        {
            "https://github.com/aghinsa/interactive_wall.git": [
                {
                    "value": "https://github.com/aghinsa/interactive_wall.git",
                    "definition": prediction_df.configs["run_dataflow"].dataflow.definitions["URL"].name,
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

if __name__ == "__main__":
    asyncio.run(main())
