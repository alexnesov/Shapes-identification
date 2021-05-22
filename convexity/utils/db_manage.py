import pandas as pd
import numpy as np
import os
import pymysql
from enum import Enum, auto
from sqlalchemy import create_engine
import sqlalchemy as sa
import functools
import traceback

import sqlite3
from sqlite3 import Error


class QuRetType(Enum):
    """
    Enumeration of return type for querries
    
    Values:
        
    - None (nothing returned)
    
    - FIRST (first row returned as tuple)
    
    - ALL (all data returned as list of tuples)
    
    - ALLASPD (all data returned as pandas data frame)
    
    - ALLASCSV (all data returned as data frame and export to csv)
    
    - ALLASXLS (all data returned as pandas data frame and export excel)
    
    """
    NONE = auto()       #nothing returned
    FIRST = auto()      #first data set returned as tuple
    ALL = auto()        #all data returned as list of tuples
    ALLASPD = auto()    #all data returned as pandas data frame
    ALLASCSV = auto()   #all data written to some csv file
    ALLASXLS = auto()   #all data written to some xls file    
    




class DBAccCM:
    """
    Context manager to deal with db connection
    """
    def __init__(self, dbname):

        self.dbname = dbname
        self.db_pass = os.environ.get('aws_db_pass')
        self.db_user = os.environ.get('aws_db_user')
        self.db_endp = os.environ.get('aws_db_endpoint')
        
    def __enter__(self):        
        """
        Executed on entering the connection in a with statement.
        Returns a connection object of type mysql.
        """
        try:
            self.conn = pymysql.connect(host=f'{self.db_endp}',user=f'{self.db_user}',password=f'{self.db_pass}',database=f'{self.dbname}')
            return self.conn
        except Exception as e:
            raise RuntimeError('Connection could not be established.')

    def __exit__(self, *args):
        self.conn.close()


class DBManager:

    def __init__(self):
        pass

    def connection(self, dbname):
        """
        returns a database name connection to database 'dbname'
        """
        conCM = DBAccCM(dbname)
        return conCM


    def exc_query(self, db_name, query, retres = QuRetType.NONE, outpfile = None):
        """
        opens a cursor, executes a query and returns the result depending on type


        :Param db_name: name of data base 
        :Param query: query to be executed
        :Param retres: return type (see :py:class:`db.db_manage.QuRetType`)

        :Param outpfile: full path to output file if retres is 
                    QuRetType.ALLASCSV or QuRetType.ALLASXLS
    
        :returns: data in format as specified by retres
        """
        try:
            ret = None
            with self.connection(db_name) as conn:

                if retres is QuRetType.ALLASPD or \
                    retres is QuRetType.ALLASCSV:
                    ret = pd.read_sql(query, conn)
                else:
                    c = conn.cursor()
                    c.execute(query)
                    conn.commit()
                    if retres is QuRetType.FIRST:
                        ret = c.fetchone()
                    elif retres is QuRetType.ALL:
                        ret = c.fetchall()
                    else:
                        pass

        except Exception as e:
            print("An error occured during the query execution.")
            print(f"{traceback.format_exc()}")
        return ret


def dfToRDS(df, table, db_name, location='RDS'):
    """
    For an unknown reason, didn't succeed to send df to RDS with connection method above.
    So had to use sqlalchemy's create_engine function

    :param df: a dataframe to send to RDS
    :param table: the table in which we want to insert the data
    :param db_name: the initial db to which we want to connect (containing the target table)
    :param location: whether we want to send data to remote RDS or on my local machine. Default = RDS
    """

    db_pass = os.environ.get('aws_db_pass')
    db_user = os.environ.get('aws_db_user')
    db_endp = os.environ.get('aws_db_endpoint')
    
    if location=='RDS':
        connection_url = sa.engine.url.URL(drivername="mysql+pymysql",
                                    username=f"{db_user}",
                                    password=f"{db_pass}",
                                    host=f"{db_endp}",
                                    database=f"{db_name}"
                                    )
    elif location=='local':         
        connection_url = sa.engine.url.URL(drivername="mysql+pymysql",
                                    username=f"root",
                                    password=f"{db_pass}",
                                    host=f"localhost",
                                    database=f"{db_name}",
                                    port=3306
                                    )
                                   
    engine = create_engine(connection_url)

    try:
        with engine.connect() as connection:
            df.to_sql(f'{table}', con=connection, if_exists='append',index=False)
    except Exception as e:
        print(f"{traceback.format_exc()}")
        raise RuntimeError('Connection could not be established.')
    finally:
        engine.dispose()

            


@functools.lru_cache(maxsize=1)
def std_db_acc_obj():         
    """                                                             
    Creates the standard data base access object (see: :py:class:`DBManager`)
    """
    db_acc_obj = DBManager()     
    return db_acc_obj      



