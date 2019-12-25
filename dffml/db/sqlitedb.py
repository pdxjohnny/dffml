import asyncio
import sqlite3
import abc
import operator 


from dffml.db.base import BaseDatabaseContext,BaseDatabaseObject,Condition,Conditions
from dffml.base import config
from dffml.df.base import BaseConfig,BaseDataFlowObject
from dffml.util.entrypoint import entry_point, EntrypointNotFound

from typing import Dict,Any,List,Union,Tuple



@config
class SqliteDatabaseConfig:
    filename:str

class SqliteDatabaseContext(BaseDatabaseContext):
    def __init__(self,parent:"SqliteDatabaseObject"):
        self.parent = parent
        
        
        
    
    async def create_table(self,table_name:str ,cols:Dict[str,str])->None:
        """
        creates a table with name `table_name` if it doesn't exist.
        arg `cols` : dict mapping column names to type of columns 
        """

        query =( f"CREATE TABLE IF NOT EXISTS  {table_name} (" 
                    + ','.join([ f"{k} {v}" for k,v in cols.items()])  
                    + ")"
                )

        self.parent.cursor.execute(query)
        

    async def insert(self,table_name:str,data:Dict[str,Any]) -> None:
        """
        inserts values to corresponding
            cols (according to position) to the table `table_name`
        """
        query= (f"INSERT INTO {table_name} "
              + f"( {','.join(data)} ) VALUES( {', '.join('?' * len(data))} ) "
            )  
       
        async with self.parent.lock:
            with self.parent.db:
                self.parent.cursor.execute(query, 
                                    list( data.values() )
                                    )
                

    
    async def update(self,table_name:str,data:Dict[str,Any],
            conditions:Conditions) -> None:
        """
        updates values of rows (satisfying `condition` if provided) with 
        `data` in `table_name`
        """
        condition_exp = self.make_condition_expression(conditions)

        query = (f"UPDATE {table_name} SET " 
                + ' '.join([f"{col} = ?" for col in data])
                + (f" WHERE {condition_exp}" if condition_exp is not None else "")
            )
       
        async with self.parent.lock:
            with self.parent.db:
                self.parent.cursor.execute(query,list(data.values()))
        return 
            

    async def lookup(self,table_name:str,cols:List[str],conditions:Conditions):
        """
        returns list of rows (satisfying `condition` if provided) from `table_name` 
        """   

        condition_exp=self.make_condition_expression(conditions)
        if len(cols)==0:
            col_exp = '*'
        else:
            col_exp = ', '.join(cols)
        
        query = ( f"SELECT {col_exp} FROM {table_name} " 
                + (f" WHERE {condition_exp}" if condition_exp is not None else "")
            )
        
        async with self.parent.lock:
            with self.parent.db:    
                self.parent.cursor.execute(query)
                results = self.parent.cursor.fetchall()

        return results
    
    async def remove(self,table_name:str,conditions:Conditions):
        condition_exp=self.make_condition_expression(conditions)
        query =( f"DELETE FROM {table_name} " 
                + (f" WHERE {condition_exp}" if condition_exp is not None else "")
            )
        async with self.parent.lock:
            with self.parent.db:    
                self.parent.cursor.execute(query)
        
        return  


    

@entry_point("sqlitedb")
class SqliteDatabase(BaseDatabaseObject):
    CONTEXT = SqliteDatabaseContext
    CONFIG = SqliteDatabaseConfig

    def __init__(self,cfg):
        super().__init__(cfg)
        self.db = sqlite3.connect(self.config.filename)
        self.cursor=self.db.cursor()
        self.lock=asyncio.Lock()

    
 



