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
        """
        Returns a dict with keys 'expression','values' if conditions is not empty
        else returns `None`

        eg :
            Input : conditions = [
                [["firstName", "=", "John"], ["lastName", "=", "Miles"]],
                [["age", "<", "38"]],
            ]

            Output : {
                'expression':
                    '((firstName = ? ) OR (lastName = ? )) AND ((age < ? ))',
                'values':
                     ['John', 'Miles', '38']
                }
        """

        def _make_condition_expression(conditions):
            def make_or(lst):
                val_list = []
                exp = []

                for cnd in lst:
                    exp.append(f"(`{cnd.column}` {cnd.operation} ? )")
                    val_list.append(cnd.value)

                result = {"expression": " OR ".join(exp), "values": val_list}

                return result

            lst = map(make_or, conditions)

            result_exps = []
            result_vals = []
            for result in lst:
                temp_exp = result["expression"]
                temp_exp = f"({temp_exp})"
                result_exps.append(temp_exp)
                result_vals.extend(result["values"])

            result_exps = " AND ".join(result_exps)
            result = {"expression": result_exps, "values": result_vals}

            return result

        condition_dict = None
        if (not conditions == None) and (len(conditions) != 0):
            condition_dict = _make_condition_expression(conditions)
        return condition_dict

    async def create_table(
        self, table_name: str, cols: Dict[str, str],*args,**kwargs
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

    async def insert(self, table_name: str, data: Dict[str, Any]
        ,*args,**kwargs) -> None:
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
        *args,**kwargs
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
            + " ".join([f"`{col}` = ?" for col in data])
            + (f" WHERE {condition_exp}" if condition_exp is not None else "")
        )

        async with self.parent.lock:
            with self.parent.db:
                self.logger.debug(query)
                self.parent.cursor.execute(query, query_values)

    async def lookup(
        self,
        table_name: str,
        cols: Optional[List[str]] = None,
        conditions: Optional[Conditions] = None,
        *args,**kwargs
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

        async with self.parent.lock:
            with self.parent.db:
                self.logger.debug(query)
                self.parent.cursor.execute(query, query_values)
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
