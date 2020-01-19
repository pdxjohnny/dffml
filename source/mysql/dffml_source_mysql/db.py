import ssl
from typing import Dict, Any, List, Union, Tuple, Optional, AsyncIterator

import aiomysql

from dffml.db.base import (
    BaseDatabase,
    Condition,
    Conditions,
)
from dffml.db.sqlite import SqliteDatabaseContext
from dffml.base import config
from dffml.repo import Repo
from dffml.util.entrypoint import entrypoint


@config
class MySQLDatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    db: str
    ca: str = None


class MySQLDatabaseContext(SqliteDatabaseContext):
    BIND_DECLARATION: str = "%s"

    async def create_table(
        self, table_name: str, cols: Dict[str, str], *args, **kwargs
    ) -> None:
        """
        Creates a table with name `table_name` if it doesn't exist.
        arg `cols` : dict mapping column names to type of columns
        """

        query = (
            f"CREATE TABLE IF NOT EXISTS {table_name} ("
            + ", ".join([f"`{k}` {v}" for k, v in cols.items()])
            + ")"
        )

        self.logger.debug(query)
        await self.conn.execute(query)

    async def insert(
        self, table_name: str, data: Dict[str, Any], *args, **kwargs
    ) -> None:
        """
        Inserts values to corresponding cols (according to position) to the
        table `table_name`
        """
        col_exp = ", ".join([f"`{col}`" for col in data])
        query = (
            f"INSERT INTO {table_name} "
            + f"( {col_exp} )"
            + f" VALUES( {', '.join([self.BIND_DECLARATION] * len(data))} ) "
        )

        self.logger.debug(query)
        await self.conn.execute(query, list(data.values()))

    async def update(
        self,
        table_name: str,
        data: Dict[str, Any],
        conditions: Optional[Conditions] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        Updates values of rows (satisfying `conditions` if provided) with
        `data` in `table_name`
        """
        query_values = list(data.values())
        condition_dict = self.make_condition_expression(conditions)

        if condition_dict is not None:
            condition_exp = condition_dict["expression"]
            query_values.extend(condition_dict["values"])
        else:
            condition_exp = None

        query = (
            f"UPDATE {table_name} SET "
            + " ,".join([f"`{col}` = {self.BIND_DECLARATION}" for col in data])
            + (f" WHERE {condition_exp}" if condition_exp is not None else "")
        )

        self.logger.debug(query)
        await self.conn.execute(query, query_values)

    async def lookup(
        self,
        table_name: str,
        cols: Optional[List[str]] = None,
        conditions: Optional[Conditions] = None,
        *args,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Returns list of rows (satisfying `conditions` if provided) from
        `table_name`
        """

        condition_dict = self.make_condition_expression(conditions)
        query_values = []
        if condition_dict is not None:
            condition_exp = condition_dict["expression"]
            query_values.extend(condition_dict["values"])
        else:
            condition_exp = None

        if not cols:
            col_exp = "*"
        else:
            col_exp = ", ".join([f"`{col}`" for col in cols])

        query = f"SELECT {col_exp} FROM {table_name} " + (
            f" WHERE {condition_exp}" if condition_exp is not None else ""
        )

        self.logger.debug(query)
        await self.conn.execute(query, query_values)
        for row in await self.conn.fetchall():
            yield dict(row)

    async def remove(
        self, table_name: str, conditions: Optional[Conditions] = None
    ):
        """
        Removes rows (satisfying `conditions` if provided) from `table_name`
        """
        condition_dict = self.make_condition_expression(conditions)

        if condition_dict is not None:
            condition_exp = condition_dict["expression"]
            query_values=condition_dict["values"]
        else:
            condition_exp = None

        query = f"DELETE FROM {table_name} " + (
            f" WHERE {condition_exp}" if condition_exp is not None else ""
        )
        await self.conn.execute(query)

    async def insert_or_update(
        self,table_name:str,data:Dict[str,Any]):
        col_exp = ", ".join([f"`{col}`" for col in data])
        query = (
            f"INSERT INTO {table_name} "
            + f"( {col_exp} )"
            + f" VALUES( {', '.join([self.BIND_DECLARATION] * len(data))} ) "
            + " ON DUPLICATE KEY UPDATE "
            + " ,".join([f"`{col}` = {self.BIND_DECLARATION}" for col in data])
        )
        vals = list(data.values())*2
        await self.conn.execute(query,vals)

    async def __aenter__(self) -> "MySQLDatabaseContext":
        self.__conn = self.parent.db.cursor(aiomysql.DictCursor)
        self.conn = await self.__conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__conn.__aexit__(exc_type, exc_value, traceback)
        await self.parent.db.commit()


@entrypoint("mysql")
class MySQLDatabase(BaseDatabase):
    CONFIG = MySQLDatabaseConfig
    CONTEXT = MySQLDatabaseContext

    def __init__(self, cfg):
        super().__init__(cfg)
        self.db = None
        self.pool = None

    async def __aenter__(self) -> "MySQLDatabase":
        # Verify MySQL connection using provided certificate, if given
        ssl_ctx = None
        if self.config.ca is not None:
            self.logger.debug(
                f"Secure connection to MySQL: CA file: {self.config.ca}"
            )
            ssl_ctx = ssl.create_default_context(cafile=self.config.ca)
        else:
            self.logger.critical("Insecure connection to MySQL")
        # Connect to MySQL
        self.pool = await aiomysql.create_pool(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            db=self.config.db,
            ssl=ssl_ctx,
        )
        self.__db = self.pool.acquire()
        self.db = await self.__db.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__db.__aexit__(exc_type, exc_value, traceback)
        self.pool.close()
        await self.pool.wait_closed()
