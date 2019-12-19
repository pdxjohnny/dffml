import abc
from dffml.df.base import BaseDataFlowObject,BaseDataFlowObjectContext
from typing import Any,List,Callable,Optional,Dict


import abc
import inspect
import types

def sanitize_non_bindable(*to_scrub):
    
    def scrub(obj):
        if(isinstance(obj,str)):
            return '_'.join(obj.split(" "))
        if(isinstance(obj,Dict)):
            nobj={ scrub(k):v for k,v in obj.items() }
            return nobj
        
    def sanitize(func):
        sig=inspect.signature(func)
        def wrappper(*args,**kwargs):
            bounded = sig.bind(*args,*kwargs)
            for arg in to_scrub:
                if arg in bounded.arguments:
                    bounded.arguments[arg]=scrub(bounded.arguments[arg])
            return func(*bounded.args , **bounded.kwargs)
        return wrappper
    return sanitize


class DatabaseContextMeta(type):
    def __init__(cls,name,bases,clsdict):
        to_scrub=["cols","table_name","data"]
        for f in clsdict:
            if (not f.startswith("__")) and ( type(getattr(cls,f)) == types.FunctionType):
                setattr(cls,f,sanitize_non_bindable(*to_scrub)(getattr(cls,f)))



class BaseDatabaseContext(BaseDataFlowObjectContext,metaclass=DatabaseContextMeta):

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

#TODO add entrypoint here
class BaseDatabaseObject(BaseDataFlowObject):
    """
    """