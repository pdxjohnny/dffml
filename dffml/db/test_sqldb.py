import os

from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase
from dffml.db.sqldb import SqlDatabase,SqlDatabaseContextConfig

class TestSqlDatabase(AsyncTestCase):

    @classmethod
    def setUp(cls):
        cls.sdb = SqlDatabase(BaseConfig())
        cls.database_name = "_test_database.db"
        cls.cfg = SqlDatabaseContextConfig(filename=cls.database_name)

        cls.table_name="my table"
        cls.cols = {"first name":"text",
                    "last name":"text",
                    "age":"numbers"}
    
    @classmethod
    def tearDownClass(cls):
        os.remove(cls.database_name)


    async def test_create_table(self):
        async with  self.sdb as sdb:
            async with sdb(self.cfg) as db:
                await db.create_table(self.table_name,self.cols)
                query = ("SELECT count(name) FROM sqlite_master "
                        + " WHERE type='table' and name='my_table' "
                        )
                db.cursor.execute(query)
                results=db.cursor.fetchone()
                self.assertEqual(results[0],1)

    
    async def test_set_get(self):

        data_dicts=[
                {
                "first name":"John",
                "last name":"Doe",
                "age":32
                },
                {
                "first name":"John",
                "last name":"Miller",
                "age":37
                },
                {
                "first name":"Richard",
                "last name":"Miles",
                "age":40   
                }   
            ]

        expected = [ tuple(d.values()) for d in data_dicts ]
       

        async with  self.sdb as sdb:
            async with sdb(self.cfg) as db:
                for data_dict in data_dicts:
                    await db.insert(self.table_name,data_dict)

                results = await db.lookup(self.table_name,[],[])
                self.assertCountEqual(results,expected)
                
            
