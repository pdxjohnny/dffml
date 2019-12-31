import tempfile
import os
import sys
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig
from dffml.util.asynctestcase import AsyncTestCase
from dffml.operation.sqlite import sqlite_query,SqliteQueryConfig
from dffml.df.types import DataFlow, Input,Operation
from dffml.operation.output import GetSingle
from dffml.df.memory import MemoryOrchestrator

definitions  = Operation.definitions(sqlite_query.op)
for definition_name,definition in definitions.items():
    setattr(sys.modules[__name__], definition_name, definition)


class TestSqliteQuery(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        fileno, cls.database_name = tempfile.mkstemp(suffix=".db")
        os.close(fileno)
        cls.sdb = SqliteDatabase(
            SqliteDatabaseConfig(filename=cls.database_name)
        )

    def _create_dataflow_with_config(self,cfg):
        return DataFlow(
            operations={
                "sqlite_query": sqlite_query.op,
                "get_single": GetSingle.imp.op,
            },
            configs={"sqlite_query": cfg},
            seed=[
                Input(
                    value=[sqlite_query.op.outputs["lookups"].name],
                    definition=GetSingle.op.inputs["spec"],
                )
            ],
        )

    async def test_0_create_set_get(self):

        cfg =SqliteQueryConfig(
                database =self.sdb,
                query_type = "create"
        )
        df = self._create_dataflow_with_config(cfg)
        test_inputs = {
            "create" : {
                "table_name" : "myTable",
                 "cols" : {
                        "key": "real",
                        "firstName": "text",
                        "lastName": "text",
                        "age": "real",
                        }
            }
        }
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(df) as octx:
                async for _ctx, results in octx.run(
                    {
                        "create" : [
                            Input(
                                value=val,
                                definition=sqlite_query.op.inputs[key]
                            )
                            for key,val in test_inputs['create'].items()
                        ]
                    }
                ):
                    print(results)

