import abc
import inspect
import types

from typing import Any, List, Callable, Optional, Dict, Tuple, Union
from collections import namedtuple
from functools import wraps


from dffml.df.base import BaseDataFlowObject, BaseDataFlowObjectContext
from dffml.util.entrypoint import base_entry_point


Condition = namedtuple("Condtion", ["column", "operation", "value"])
Conditions = Union[
    List[List[Condition]], List[List[Tuple[str]]],
]


class DatabaseContextConstraint(abc.ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr in vars(cls).keys():
            func = getattr(cls, attr)
            if (
                (not attr.startswith("__"))
                and inspect.isfunction(func)
                and not (
                    inspect.ismethod(func) and func.__self__ is cls
                )  # checks if `@classmethod`
            ):
                setattr(cls, attr, cls.sanitize(func))


class BaseDatabaseContext(
    BaseDataFlowObjectContext, DatabaseContextConstraint
):
    """
    Base context class for database interaction
    """

    @classmethod
    def sanitize_non_bindable(self, val):
        if val.isalnum():
            return val
        raise ValueError(
            f"`{val}` : Only alphanumeric [a-zA-Z0-9] characters are allowed as table,column names"
        )

    @classmethod
    def sanitize(self, func):
        sig = inspect.signature(func)

        def scrub(obj):
            if isinstance(obj, str):
                return self.sanitize_non_bindable(obj)
            if isinstance(obj, Dict):
                nobj = {
                    self.sanitize_non_bindable(k): v for k, v in obj.items()
                }
                return nobj
            if isinstance(obj, List):
                nobj = list(map(scrub, obj))
                return nobj
            if isinstance(obj, Condition):
                column, *others = obj
                nobj = Condition._make([scrub(column), *others])
                return nobj
            else:
                return obj

        @wraps(func)
        def wrappper(*args, **kwargs):
            bounded = sig.bind(*args, *kwargs)
            for arg in bounded.arguments:
                if arg == "self" or arg == "cls":
                    continue
                if arg == "conditions":
                    bounded.arguments[arg] = self.make_conditions(
                        bounded.arguments[arg]
                    )
                bounded.arguments[arg] = scrub(bounded.arguments[arg])
            return func(*bounded.args, **bounded.kwargs)

        return wrappper

    @classmethod
    def make_conditions(self, lst):
        if (not lst) or isinstance(lst[0][0], Condition):
            return lst
        res = [list(map(Condition._make, cnd)) for cnd in lst]
        return res

    @classmethod
    def make_condition_expression(self, conditions):
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

    @abc.abstractmethod
    async def create_table(
        self, table_name: str, cols: Dict[str, str]
    ) -> None:
        """
        creates a table with name `table_name` if it doesn't exist
        """

    @abc.abstractmethod
    async def insert(self, table_name: str, data: Dict[str, Any]) -> None:
        """
        Inserts values to corresponding cols (according to position) to the
        table `table_name`
        """

    @abc.abstractmethod
    async def update(
        self, table_name: str, data: Dict[str, Any], conditions: Conditions
    ) -> None:
        """
        Updates values of rows (satisfying `conditions` if provided) with `data`
        in `table_name`
        """

    @abc.abstractmethod
    async def lookup(
        self, table_name: str, cols: List[str], conditions: Conditions
    ):
        """
        Returns list of rows (satisfying `conditions` if provided) from
        `table_name`
        """

    @abc.abstractmethod
    async def remove(self, table_name: str, conditions: Conditions):
        """
        Removes rows (satisfying `conditions`) from `table_name`
        """


@base_entry_point("dffml.db", "db")
class BaseDatabaseObject(BaseDataFlowObject):
    """
    Base class for database interaction
    """

    def __call__(self) -> BaseDatabaseContext:
        return self.CONTEXT(self)
