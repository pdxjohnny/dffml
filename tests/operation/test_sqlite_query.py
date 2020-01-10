import tempfile
import os
import sys
from collections import OrderedDict
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig
from dffml.util.asynctestcase import AsyncTestCase
from dffml.operation.db import sqlite_query,SqliteQueryConfig
from dffml.df.types import DataFlow, Input,Operation
from dffml.operation.output import GetSingle
from dffml.df.memory import MemoryOrchestrator

DEFINITIONS  = Operation.definitions(sqlite_query.op)



class TestSqliteQuery(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        fileno, cls.database_name = tempfile.mkstemp(suffix=".db")
        os.close(fileno)
        cls.sdb = SqliteDatabase(
            SqliteDatabaseConfig(filename=cls.database_name)
        )
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        # for ease of testing
        cls.sdb.db.row_factory = dict_factory
        cls.sdb.cursor =  cls.sdb.db.cursor()

    def setUp(self):
        self.table_name="myTable"
        self.cols = {
            "key": "real",
            "firstName": "text",
            "lastName": "text",
            "age": "real",
        }
        self.data_dicts =[
            {"key": 10, "firstName": "John", "lastName": "Doe", "age": 16},
            {"key": 11, "firstName": "John", "lastName": "Miles", "age": 37},
            {"key": 12, "firstName": "Bill", "lastName": "Miles", "age": 40},
        ]

    def _create_dataflow_with_config(self,cfg):

        seed = [
            Input(
                    value=[sqlite_query.op.outputs["lookups"].name],
                    definition=GetSingle.op.inputs["spec"],
                )
            ]
        return DataFlow(
            operations={
                "sqlite_query": sqlite_query.op,
                "get_single": GetSingle.imp.op,
            },
            configs={"sqlite_query": cfg},
            seed=seed
        )

    async def test_0_create(self):
        cfg =SqliteQueryConfig(
                database =self.sdb,
                query_type = "create"
        )
        df = self._create_dataflow_with_config(cfg)
        test_inputs = {
            "create" : {
                "table_name" : self.table_name,
                "cols" : self.cols,
                "data":{},
                "conditions":[],
            }
        }

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(df) as octx:
                async for _ctx, results in octx.run(
                    {
                        test_ctx : [
                            Input(
                                value=val,
                                definition=sqlite_query.op.inputs[key]
                            )
                            for key,val in test_val.items()
                        ]
                        for test_ctx,test_val in test_inputs.items()
                    }
                ):
                    async with self.sdb() as db_ctx:
                        query = (
                            "SELECT count(name) FROM sqlite_master "
                            + f" WHERE type='table' and name='{self.table_name}' "
                            )
                        db_ctx.parent.cursor.execute(query)
                        results = db_ctx.parent.cursor.fetchone()
                        self.assertEqual(results['count(name)'], 1)

    async def test_1_insert(self):
        cfg =SqliteQueryConfig(
                database =self.sdb,
                query_type = "insert"
        )
        df = self._create_dataflow_with_config(cfg)
        for _data in  self.data_dicts:
            test_inputs = {
                "insert" : {
                    "table_name" : self.table_name,
                    "cols" : [],
                    "data":_data,
                    "conditions":[],
                }
            }

            async with MemoryOrchestrator.withconfig({}) as orchestrator:
                async with orchestrator(df) as octx:
                    async for _ctx, results in octx.run(
                        {
                            test_ctx : [
                                Input(
                                    value=val,
                                    definition=sqlite_query.op.inputs[key]
                                )
                                for key,val in test_val.items()
                            ]
                            for test_ctx,test_val in test_inputs.items()
                        }
                    ):
                        continue

        async with self.sdb() as db_ctx:
            query = (
                f"SELECT * FROM {self.table_name} "
                )
            db_ctx.parent.cursor.execute(query)
            rows = db_ctx.parent.cursor.fetchall()
            self.assertEqual(self.data_dicts,rows)

    async def test_2_lookup(self):
        cfg =SqliteQueryConfig(
                database =self.sdb,
                query_type = "lookup"
        )
        df = self._create_dataflow_with_config(cfg)
        test_inputs = {
            "insert" : {
                "table_name" : self.table_name,
                "cols" : [],
                "data":{},
                "conditions":[],
            }
        }

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(df) as octx:
                async for _ctx, results in octx.run(
                    {
                        test_ctx : [
                            Input(
                                value=val,
                                definition=sqlite_query.op.inputs[key]
                            )
                            for key,val in test_val.items()
                        ]
                        for test_ctx,test_val in test_inputs.items()
                    }
                ):
                   self.assertIn("query_lookups",results)
                   results = results["query_lookups"]
                   self.assertEqual(self.data_dicts,results)


