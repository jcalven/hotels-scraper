import yaml
import logging
import numpy as np
import sqlalchemy as sqlal
from sqlalchemy import Table, Column, Integer, String, Float, MetaData, ForeignKey, DateTime

logger = logging.getLogger("hotels-scraper.sql.sql")

class TableMaker(object):

    """
    Class for creating an SQLite database with a given schema.
    """

    def __init__(self, metadata=None):
        if metadata:
            self.metadata = metadata
        else:
            self.metadata = MetaData()
    
    def create_columns(self, schema):
        res = []
        meta = schema[0]["meta"]
        columns = schema[1]["columns"]
        for name, dtype in columns.items():
            if name == meta["primary_key"]:
                res.append(sqlal.Column(name, eval(dtype), nullable=False, primary_key=name))
            elif name == meta.get("foreign_key"):
                res.append(sqlal.Column(name, eval(dtype), ForeignKey(meta.get("reference"))))
            else:
                res.append(sqlal.Column(name, eval(dtype), nullable=True))
        return res
    
    def create_table(self, name, schema):
        table = Table(name, self.metadata,
                      *self.create_columns(schema)
                     )
        return table
    
def create_connection(filename):
    """
    Creates a connection to the database
    """
    engine = sqlal.create_engine(f'sqlite:///{filename}.db')
    connection = engine.connect()
    return connection
        
def create_database(filename, schemas, conn=None):
    """
    Helper function for creating the database
    """
    tablemaker = TableMaker()
    if not conn:
        conn = create_connection(filename)
    for name, schema in schemas.items():
        _ = tablemaker.create_table(name, schema)
        # table.create_all(connection, checkfirst=True) #Creates the table
    tablemaker.metadata.create_all(conn, checkfirst=True) # Creates the table
    return conn

def to_sql(df, table_name, conn):

    """
    Upserts new data to the database.
    """

    ids = tuple(df.index.to_list())
    n_rows = len(ids)
    if n_rows == 1:
        ids = ids[0]
        res = conn.execute(f"SELECT id FROM {table_name} WHERE id IN ({ids})")
    else:
        ids = tuple(ids)
        res = conn.execute(f"SELECT id FROM {table_name} WHERE id IN {ids}")
    indx = np.array(res.fetchall()).flatten()
    df = df.loc[df.index.difference(indx)]
    if not df.empty:
        msg = "[~] Updating records ..."
        logger.info(msg)
        print(msg)
        try:
            df.to_sql(table_name, conn, if_exists="append", index=True)
            msg = f"[~] {df.shape[0]}/{n_rows} records upserted to table <{table_name}>"
            logger.info(msg)
            print(msg)
        except Exception as error:
            logger.error(error)
    else:
        msg = f"0/{n_rows} records upserted to <{table_name}>. (No unique records in DataFrame)"
        logger.info(msg)
        print(msg)