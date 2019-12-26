import abc
import asyncio
import sqlite3
from typing import Dict, Any, List, Union, Tuple


from dffml.db.base import (
    BaseDatabaseContext,
    BaseDatabase,
    Condition,
    Conditions,
)
from dffml.base import config
from dffml.util.entrypoint import entry_point


@config
class SqliteDatabaseConfig:
    filename: str


class SqliteDatabaseContext(BaseDatabaseContext):
    async def create_table(
        self, table_name: str, cols: Dict[str, str]
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
        self.parent.cursor.execute(query)

    async def insert(self, table_name: str, data: Dict[str, Any]) -> None:
        """
        Inserts values to corresponding cols (according to position) to the
        table `table_name`
        """
        col_exp = ", ".join([f"`{col}`" for col in data])
        query = (
            f"INSERT INTO {table_name} "
            + f"( {col_exp} )"
            + f" VALUES( {', '.join('?' * len(data))} ) "
        )
        async with self.parent.lock:
            with self.parent.db:
                self.logger.debug(query)
                self.parent.cursor.execute(query, list(data.values()))

    async def update(
        self, table_name: str, data: Dict[str, Any], conditions: Conditions
    ) -> None:
        """
        Updates values of rows (satisfying `conditions` if provided) with
        `data` in `table_name`
        """
        condition_exp = self.make_condition_expression(conditions)

        query = (
            f"UPDATE {table_name} SET "
            + " ".join([f"`{col}` = ?" for col in data])
            + (f" WHERE {condition_exp}" if condition_exp is not None else "")
        )

        async with self.parent.lock:
            with self.parent.db:
                self.logger.debug(query)
                self.parent.cursor.execute(query, list(data.values()))

    async def lookup(
        self, table_name: str, cols: List[str], conditions: Conditions
    ):
        """
        Returns list of rows (satisfying `conditions` if provided) from
        `table_name`
        """

        condition_exp = self.make_condition_expression(conditions)
        if len(cols) == 0:
            col_exp = "*"
        else:
            col_exp = ", ".join([f"`{col}`" for col in cols])

        query = f"SELECT {col_exp} FROM {table_name} " + (
            f" WHERE {condition_exp}" if condition_exp is not None else ""
        )

        async with self.parent.lock:
            with self.parent.db:
                self.logger.debug(query)
                self.parent.cursor.execute(query)
                return self.parent.cursor.fetchall()

    async def remove(self, table_name: str, conditions: Conditions):
        """
        Removes rows (satisfying `conditions` if provided) from `table_name`
        """
        condition_exp = self.make_condition_expression(conditions)
        query = f"DELETE FROM {table_name} " + (
            f" WHERE {condition_exp}" if condition_exp is not None else ""
        )
        async with self.parent.lock:
            with self.parent.db:
                self.logger.debug(query)
                self.parent.cursor.execute(query)


@entry_point("sqlite")
class SqliteDatabase(BaseDatabase):
    CONFIG = SqliteDatabaseConfig
    CONTEXT = SqliteDatabaseContext

    def __init__(self, cfg):
        super().__init__(cfg)
        self.db = sqlite3.connect(self.config.filename)
        self.cursor = self.db.cursor()
        self.lock = asyncio.Lock()
