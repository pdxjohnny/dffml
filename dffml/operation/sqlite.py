import inspect


from ..base import config
from ..db.sqlite import SqliteDatabase,SqliteDatabaseContext
from typing import Dict,Any,Optional,List
from ..df.base import op
from ..db.base import Conditions
from ..df.types import Definition

@config
class SqliteQueryConfig:
    """
        query_type : "create","insert","update","remove","lookup"
    """
    database : SqliteDatabase
    query_type : str

@op(
    name="dffml.sqlitedb.query",
    inputs={
        "table_name":Definition(
            name="query_table",primitive="str"
        ),
        "data": Definition(
            name="query_data", primitive="Dict[str, Any]"
        ),
        "conditions":Definition(
            name="query_conditions",primitive="Conditions"
        ),
        "cols":Definition(
            name="query_cols",primitive="List[str]"
        ),
    },
    outputs={
        "lookups": Definition(
            name="query_lookups", primitive="Dict[str, Any]"
        )
    },
    config_cls=SqliteQueryConfig,
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def sqlite_query(self,*,
                table_name : str,
                data : Dict[str,Any] = {},
                Conditions : Conditions = [],
                cols : List[str] = [],
                ) -> Optional[Dict[str, Any]]:

    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    kwargs={(arg, values[arg]) for i in args[1:]}

    query_fn = self.config.query_type
    if 'create' in query_fn:
        query_fn='create_table'
    allowed = ['create_table','remove','update','insert','lookup']
    if not query_fn in allowed:
        raise ValueError(f"Only queries of type {allowed} is allowed")

    query_fn=getattr(self.dbctx,query_fn)
    if inspect.isasyncgenfunction(query_fn):
        async for res in query_fn(**kwargs):
            return{
                "lookups":res
            }
    else:
        query_fn(**kwargs)
        return {"lookups":{}}


