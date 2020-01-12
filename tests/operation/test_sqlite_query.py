import tempfile
import os
import sys
from collections import OrderedDict
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig
from dffml.util.asynctestcase import AsyncTestCase
from dffml.operation.db import SqliteQueryConfig,sqlite_query_create_table,sqlite_query_insert,sqlite_query_lookup
from dffml.df.types import DataFlow, Input,Operation
from dffml.operation.output import GetSingle
from dffml.df.memory import MemoryOrchestrator



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

    def _create_dataflow_with_op(self,query_op,seed=[]):
        return DataFlow(
            operations={
                "sqlite_query": query_op.op,
                "get_single": GetSingle.imp.op,
            },
            configs={"sqlite_query": SqliteQueryConfig(
                    database =self.sdb,
                        )
                    },
            seed=seed,
            implementations={query_op.op.name:query_op.imp}
        )

    async def test_0_create(self):

        df = self._create_dataflow_with_op(sqlite_query_create_table)
        test_inputs = {
            "create" : {
                "table_name" : self.table_name,
                "cols" : self.cols,
            }
        }

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(df) as octx:
                async for _ctx, results in octx.run(
                    {
                        test_ctx : [
                            Input(
                                value=val,
                                definition=sqlite_query_create_table.op.inputs[key]
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

        df = self._create_dataflow_with_op(sqlite_query_insert)
        for _data in  self.data_dicts:
            test_inputs = {
                "insert" : {
                    "table_name" : self.table_name,
                    "data":_data,
                }
            }

            async with MemoryOrchestrator.withconfig({}) as orchestrator:
                async with orchestrator(df) as octx:
                    async for _ctx, results in octx.run(
                        {
                            test_ctx : [
                                Input(
                                    value=val,
                                    definition=sqlite_query_insert.op.inputs[key]
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
        seed = [
            Input(
                    value=[sqlite_query_lookup.op.outputs["lookups"].name],
                    definition=GetSingle.op.inputs["spec"],
                )
            ]
        df = self._create_dataflow_with_op(sqlite_query_lookup,seed=seed)
        test_inputs = {
            "lookup" : {
                "table_name" : self.table_name,
                "cols" : [],
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
                                definition=sqlite_query_lookup.op.inputs[key]
                            )
                            for key,val in test_val.items()
                        ]
                        for test_ctx,test_val in test_inputs.items()
                    }
                ):
                   self.assertIn("query_lookups",results)
                   results = results["query_lookups"]
                   self.assertEqual(self.data_dicts,results)


