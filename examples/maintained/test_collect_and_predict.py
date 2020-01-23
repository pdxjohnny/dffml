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

from make_prediction_dataflow import prediction_df

collect_and_predict_df = prediction_df

# collect_and_predict_path = "./collect_and_predict_df.json"

async def main():
    # async with ConfigLoaders() as cfgl:
    #     _, collect_and_predict_df = await cfgl.load_file(filepath=collect_and_predict_path)
    #     collect_and_predict_df = DataFlow._fromdict(**collect_and_predict_df)

    test_inputs ={
            "interactive_wall": [
                Input(
                    value= "https://github.com/aghinsa/interactive_wall.git",
                    definition = collect_and_predict_df.definitions["URL"],
                )
            ]
        }

    async with MemoryOrchestrator.withconfig({}) as orchestrator:
        async with orchestrator(collect_and_predict_df) as octx:
            async for _ctx, results in octx.run(test_inputs):
                print(f"result are :{results}")

if __name__ == "__main__":
    asyncio.run(main())
