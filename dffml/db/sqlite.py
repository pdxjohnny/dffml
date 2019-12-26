import abc
import asyncio
import sqlite3
from typing import Dict, Any, List, Union, Tuple, Optional, AsyncIterator


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
    @classmethod
    def make_condition_expression(cls, conditions):
        # TODO cnd.value should be replaced with a ? in the built SQL statement
        # and all the values which were replaced with a ? should be passed to
        # execute in the list of bound parameters (its second argument)
        #
        # For example, the update query for test_2_update is currently run as:
        #
        # cursor.execute("UPDATE myTable SET `age` = ? WHERE ((firstName = 'John') OR (lastName = 'Miles')) AND ((age < '38'))", (35,))
        #
        # It should become:
        #
        # cursor.execute("UPDATE myTable SET `age` = ? WHERE ((firstName = ?) OR (lastName = ?)) AND ((age < ?))", (35, "John", "Miles", 38,))

        def _make_condition_expression(conditions):
            def make_or(lst):
                exp = [
                    f"({cnd.column} {cnd.operation} '{cnd.value}')"
                    for cnd in lst
                ]
                return " OR ".join(exp)

            def make_and(lst):
                lst = [f"({x})" for x in lst]
                return " AND ".join(lst)

            lst = map(make_or, conditions)
            lst = make_and(lst)
            return lst

        condition_exp = None
        if (not conditions == None) and (len(conditions) != 0):
            condition_exp = _make_condition_expression(conditions)
        return condition_exp

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
        self,
        table_name: str,
        data: Dict[str, Any],
        conditions: Optional[Conditions] = None,
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
        self,
        table_name: str,
        cols: Optional[List[str]] = None,
        conditions: Optional[Conditions] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Returns list of rows (satisfying `conditions` if provided) from
        `table_name`
        """

        condition_exp = self.make_condition_expression(conditions)
        if not cols:
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
                for row in self.parent.cursor.fetchall():
                    yield dict(row)

    async def remove(
        self, table_name: str, conditions: Optional[Conditions] = None
    ):
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
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
        self.lock = asyncio.Lock()
