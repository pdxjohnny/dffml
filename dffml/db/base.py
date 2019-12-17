import abc
from dffml.df.base import BaseDataFlowObject,BaseDataFlowObjectContext
from typing import Any,List,Callable,Optional,Dict

class BaseDatabaseContext(BaseDataFlowObjectContext):

    @abc.abstractmethod
    async def create_table(self,table_name : str)->None:
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
            condition:Optional[Callable[...,bool]])->None:
            """
            updates values of rows (satisfying `condition` if provided) with 
            `data` in `table_name`
            """

    @abc.abstractmethod
    async def lookup(self,table_name:str,cols:List[str],
        condition:Optional[Callable[...,bool]] )->List[Any]:
        """
        returns list of rows (satisfying `condition` if provided) from `table_name` 
        """             

#TODO add entrypoint here
class BaseDatabase(BaseDataFlowObject):
    """
    """