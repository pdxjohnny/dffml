import asyncio
import sqlite3
import abc
import operator 
from functools import reduce
from dffml.db.base import BaseDatabaseContext,BaseDatabaseObject,Condition
from dffml.base import config
from dffml.df.base import BaseConfig,BaseDataFlowObject
from typing import Dict,Any,List,Union,Tuple
from dffml.util.entrypoint import entry_point, EntrypointNotFound

Conditions = Union [
                    List[ List[ Condition] ],
                    List[ List[ Tuple[str] ] ],
                 ]

@config
class SqlDatabaseContextConfig:
    filename:str

class SqlDatabaseContext(BaseDatabaseContext):
    def __init__(self,config,parent:"SqlDatabaseObject"):
        super().__init__(config,parent)
        self.db = sqlite3.connect(self.config.filename)
        self.cursor=self.db.cursor()
        self.lock=asyncio.Lock()
        print(f"init sqldbctx  self = {self}\n")

    
    async def create_table(self,table_name:str ,cols:Dict[str,str])->None:
        """
        creates a table with name `table_name` if it doesn't exist.
        arg `cols` : dict mapping column names to type of columns 
        """

        query =( f"CREATE TABLE IF NOT EXISTS  {table_name} (" 
                    + ','.join([ f"{k} {v}" for k,v in cols.items()])  
                    + ")"
                )
        print(f"Self : {self}")
        self.cursor.execute(query)
        

    async def insert(self,table_name:str,data:Dict[str,str]) -> None:
        """
        inserts values to corresponding
            cols (according to position) to the table `table_name`
        """
        query=f"INSERT INTO {table_name} "
        
        if(isinstance(data,List)):
            query+= f"VALUES ({ ', '.join('?' * len(data)) })"
            async with self.lock:
                with self.db:
                    self.cursor.execute(query,data)
                    return

        if(isinstance(data,Dict)):
            query+= f"( {','.join(data)} ) VALUES( {', '.join('?' * len(data))} ) "  
       
        async with self.lock:
            with self.db:
                self.cursor.execute(query, 
                                    list( data.values() )
                                    )
                return

    
    async def update(self,table_name:str,data:Dict[str,str],
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
       
        async with self.lock:
            with self.db:
                self.cursor.execute(query,list(data.values()))
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
        
        async with self.lock:
            with self.db:    
                self.cursor.execute(query)
                results = self.cursor.fetchall()

        return results
    
    async def remove(self,table_name:str,conditions:Conditions):
        condition_exp=self.make_condition_expression(conditions)
        query =( f"DELETE FROM {table_name} " 
                + (f" WHERE {condition_exp}" if condition_exp is not None else "")
            )
        async with self.lock:
            with self.db:    
                self.cursor.execute(query)
        
        return  

class BaseSqlDatabaseDataFlowObject(BaseDataFlowObject):
    def __call__(self,cfg:SqlDatabaseContextConfig) -> SqlDatabaseContext:
        return self.CONTEXT(cfg ,self)

@entry_point("sqldb")
class SqlDatabase(BaseDatabaseObject,BaseSqlDatabaseDataFlowObject):
    CONTEXT = SqlDatabaseContext
 



