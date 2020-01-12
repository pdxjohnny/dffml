import inspect


from ..base import config
from ..db.sqlite import SqliteDatabase,SqliteDatabaseContext
from typing import Dict,Any,Optional,List
from ..df.base import op
from ..db.base import Conditions
from ..df.types import Definition


#definitions
QUERY_TABLE=Definition(name="query_table",primitive="str")
QUERY_DATA=Definition(name="query_data", primitive="Dict[str, Any]")
QUERY_CONDITIONS=Definition(name="query_conditions",primitive="Conditions")
QUERY_COLS=Definition(name="query_cols",primitive="List[str]")
QUERY_LOOKUPS=Definition(name="query_lookups", primitive="Dict[str, Any]")

@config
class SqliteQueryConfig:
    """
        query_type : "create","insert","update","remove","lookup"
    """
    database : SqliteDatabase


# TODO Figure out a way to handle defaults so that all inputs need not be passed to the 
# flow on execution
# Note : Add `query_type`:str to `SqliteQueryConfig` before use.
@op(
    name="dffml.sqlitedb.query",
    inputs={
        "table_name":QUERY_TABLE,
        "data": QUERY_DATA,
        "conditions":QUERY_CONDITIONS,
        "cols":QUERY_COLS
    },
    outputs={
        "lookups":QUERY_LOOKUPS
    },
    config_cls=SqliteQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def sqlite_query(self,*,
                table_name : str,
                data : Dict[str,Any] = {},
                conditions : Conditions = [],
                cols : List[str] = [],
                ) -> Optional[Dict[str, Any]]:

    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)

    kwargs={arg:values[arg] for arg in args[1:]}
    query_fn = self.config.query_type
    if 'create' in query_fn:
        query_fn='create_table'
    allowed = ['create_table','remove','update','insert','lookup']
    if not query_fn in allowed:
        raise ValueError(f"Only queries of type {allowed} is allowed")


    query_fn=getattr(self.dbctx,query_fn)

    try:
        await query_fn(**kwargs)
        return {"lookups":{}}

    except TypeError as e:
        if 'async_gen' in repr(e):
            result = query_fn(**kwargs)
            return {"lookups":[res async for res in result] }
        else :
            raise e


@op(
    inputs={
        "table_name":QUERY_TABLE,
        "cols":QUERY_COLS
    },
    outputs={
        "lookups":QUERY_LOOKUPS
    },
    config_cls=SqliteQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def sqlite_query_create_table(self,*,
                table_name : str,
                cols : List[str] = [],
                ) -> Dict[str, Any]:
                await self.dbctx.create_table(table_name=table_name,
                                        cols=cols)
                return {"lookups":{}}

@op(
    inputs={
        "table_name":QUERY_TABLE,
        "data":QUERY_DATA
    },
    outputs={
        "lookups":QUERY_LOOKUPS
    },
    config_cls=SqliteQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def sqlite_query_insert(self,*,
                table_name : str,
                data : Dict[str,Any],
                ) -> Dict[str, Any]:
                await self.dbctx.insert(table_name=table_name,
                                        data=data)
                return {"lookups":{}}

@op(
    inputs={
        "table_name":QUERY_TABLE,
        "data":QUERY_DATA,
        "conditions":QUERY_CONDITIONS
    },
    outputs={
        "lookups":QUERY_LOOKUPS
    },
    config_cls=SqliteQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def sqlite_query_update(self,*,
                table_name : str,
                data : Dict[str,Any],
                conditions : Conditions = []
                ) -> Dict[str, Any]:
                await self.dbctx.update(table_name=table_name,
                                        data=data,
                                        conditions=conditions)
                return {"lookups":{}}

@op(
    inputs={
        "table_name":QUERY_TABLE,
        "conditions":QUERY_CONDITIONS
    },
    outputs={
        "lookups":QUERY_LOOKUPS
    },
    config_cls=SqliteQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def sqlite_query_remove(self,*,
                table_name : str,
                conditions : Conditions = []
                ) -> Dict[str, Any]:
                await self.dbctx.remove(table_name=table_name,
                                        conditions=conditions)
                return {"lookups":{}}


@op(
    inputs={
        "table_name":QUERY_TABLE,
        "cols":QUERY_COLS,
        "conditions":QUERY_CONDITIONS
    },
    outputs={
        "lookups":QUERY_LOOKUPS
    },
    config_cls=SqliteQueryConfig,
    imp_enter={"database": (lambda self: self.config.database)},
    ctx_enter={"dbctx": (lambda self: self.parent.database())},
)
async def sqlite_query_lookup(self,*,
                table_name : str,
                cols : List[str] = [],
                conditions : Conditions = []
                ) -> Dict[str, Any]:
                result =  self.dbctx.lookup(table_name=table_name,
                                        cols=cols,
                                        conditions=conditions)
                return {"lookups":[res async for res in result] }







