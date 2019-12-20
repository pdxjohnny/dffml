import abc
from dffml.df.base import BaseDataFlowObject,BaseDataFlowObjectContext
from typing import Any,List,Callable,Optional,Dict,Tuple
from collections import namedtuple
from dffml.util.entrypoint import base_entry_point
import abc
import inspect
import types
from functools import wraps

Condition=namedtuple('Condtion',['column','operation','value'])


class DatabaseContextConstraint:

    def __init_subclass__(cls,**kwargs):
        super().__init_subclass__(**kwargs)
        for attr in vars(cls).keys():
            if (
                (not attr.startswith("__"))
                and not attr.startswith("sanitize")
            ):
                setattr(cls,attr,cls.sanitize(getattr(cls,attr)))
    
    


class BaseDatabaseContext(BaseDataFlowObjectContext,DatabaseContextConstraint):

    @classmethod
    def sanitize_non_bindable(self,val):
        return '_'.join(val.split(" "))
    
    @classmethod    
    def sanitize(self,func):
        sig=inspect.signature(func)
        def scrub(obj):
            if(isinstance(obj,str)):
                return self.sanitize_non_bindable(obj)
            if(isinstance(obj,Dict)):
                nobj={ self.sanitize_non_bindable(k):v for k,v in obj.items() }
                return nobj
            if(isinstance(obj,List)):
                nobj= list(map(scrub,obj))
                return nobj
            if(isinstance(obj,Condition)):
                column,*others = obj 
                nobj = Condition._make( [scrub(column),*others])
                return nobj

        @wraps(func)
        def wrappper(*args,**kwargs):
            bounded = sig.bind(*args,*kwargs)
            for arg in bounded.arguments:
                if (arg=='self' or arg=='cls'):
                    continue    
                bounded.arguments[arg]=scrub(bounded.arguments[arg])
            return func(*bounded.args , **bounded.kwargs)
        return wrappper
    

    def make_conditions(self,lst):
        res = [ list(map(Condition._make,cnd)) for cnd in lst ]
        return res

    def _make_condition_expression(self,conditions):
        def make_or(lst):
            exp = [ f"({cnd.column} {cnd.operation} '{cnd.value}')"
                    for cnd in lst
                    ]
            return " OR ".join(exp)
        def make_and(lst):
            lst = [ f"({x})" for x in lst  ]
            return " AND ".join(lst)

        lst = (map(make_or,conditions))
        lst = make_and(lst)
        return lst
    
    def make_condition_expression(self,conditions):
        condition_exp = None
        if (not conditions==None) and (len(conditions)!=0) :
            if not (isinstance(conditions[0][0] ,Condition)):
                conditions=self.make_conditions(conditions)
            condition_exp = self._make_condition_expression(conditions)
        return condition_exp


    @abc.abstractmethod
    async def create_table(self,table_name : str,cols:Dict[str,str])->None:
        """
        creates a table with name `table_name` if it doesn't exist
        """
    
    @abc.abstractmethod
    async def insert(self,table_name:str,data:Dict[str,Any])->None:
        """
        inserts values to corresponding
            cols (according to position) to the table `table_name`
        """

    @abc.abstractmethod
    async def update(self,table_name:str,data:Dict[str,Any],
            condition:"Optional[ Callable[...,bool]]" )->None:
            """
            updates values of rows (satisfying `condition` if provided) with 
            `data` in `table_name`
            """

    @abc.abstractmethod
    async def lookup(self,table_name:str,cols:List[str],
        condition : "Optional[ Callable[...,bool]]" )->List[Any]:
        """
        returns list of rows (satisfying `condition` if provided) from `table_name` 
        """             

@base_entry_point("dffml.db","db")
class BaseDatabaseObject(BaseDataFlowObject):
    """
    """