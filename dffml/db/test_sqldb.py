from dffml.util.asynctestcase import AsyncTestCase
from dffml.db.sqldb import SqlDatabase,SqlDatabaseContextConfig
from dffml.df.base import BaseConfig

class TestSqlDatabase(AsyncTestCase):
    def setUp(self):
        self.sdb = SqlDatabase(BaseConfig())
        self.table_name="mytable"
        self.cols = {"name":"text","age":"numbers"}
        self.cfg = SqlDatabaseContextConfig(filename="_test_database")

    async def test_create_table(self):
        async with  self.sdb as sdb:
            async with sdb(self.cfg) as ctx:
                await ctx.create_table(self.table_name,self.cols)
    
    async def test_set_get(self):

        data_dict={"name":"Tony","age":"12"}
        data_list=["Stark","32"]
    
        async with  self.sdb as sdb:
            async with sdb(self.cfg) as ctx:
                await ctx.insert(self.table_name,data_dict)
                await ctx.insert(self.table_name,data_list)
                results = await ctx.lookup(self.table_name,[],[])
                print(results)
