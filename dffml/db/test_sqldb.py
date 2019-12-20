from dffml.util.asynctestcase import AsyncTestCase
from dffml.db.sqldb import SqlDatabase,SqlDatabaseContextConfig
from dffml.df.base import BaseConfig

class TestSqlDatabase(AsyncTestCase):
    def setUp(self):
        self.sdb = SqlDatabase(BaseConfig())
    
    async def test_create_table(self):
        cfg = SqlDatabaseContextConfig(filename=":memory:")
        async with  self.sdb as sdb:
            async with sdb(cfg) as ctx:
                await ctx.create_table("feedtable", {"name":"text"})
                # condition=[[Condition("colName","=","string val")] ]
                # await ctx.update("feedtable",{},condition)