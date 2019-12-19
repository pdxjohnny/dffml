import abc
from dffml.df.base import BaseDataFlowObject,BaseDataFlowObjectContext
from typing import Any,List,Callable,Optional,Dict,Tuple
from collections import namedtuple
import abc
import inspect
import types

Condition=namedtuple('Condtion',['column','operation','value'])

class DatabaseContextMeta(type):

    def __new__(cls,name,base,clsdict):
        temp_cls=type.__new__(cls,name,base,clsdict)
        new_dict={}
        avoid = ["sanitize","scrub","sanitize_non_bindable"]
        for fname,fval in clsdict.items():
            if ( (not fname.startswith("__") )
                and ( not fname in avoid )
                and ( type(fval) == types.FunctionType )
             ) :
                    new_dict[fname]=temp_cls.sanitize(fval)
            else:
                new_dict[fname]=fval
                    

        new_cls=type.__new__(cls,name,base,new_dict)
        return new_cls



class BaseDatabaseContext(BaseDataFlowObjectContext,metaclass=DatabaseContextMeta):

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

        def wrappper(*args,**kwargs):
            bounded = sig.bind(*args,*kwargs)
            for arg in bounded.arguments:
                bounded.arguments[arg]=scrub(bounded.arguments[arg])
            return func(*bounded.args , **bounded.kwargs)
        return wrappper
    

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