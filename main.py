import logging
import pandas as pd
from datetime import datetime, timedelta
import argparse
import hotscrape.scraper as hs
from hotscrape.utils import load_schema
import hotscrape.sql as sql
from hotscrape.search_parser import Search, create_search_list

logging.basicConfig(filename='logs/run.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger('hotels-scraper.run')

def run_scraper(search, connection):
    """
    Helper function for running the scraper and sql upserts
    """
    df_search, df_attributes = hs.run(search)
    # Upsert search and search results to DB
    if not df_search.empty:
        sql.to_sql(df_search, "search", connection)
    if not df_attributes.empty:
        sql.to_sql(df_attributes, "hotels", connection)
    print("\n\n")

def run(search_path, db_path, schema_path):
    """
    Top-level function for running the hotscrape program. 

    Args:
        search_path (str): Path to search config file
        db_path (str): Path to database file
        schema_path (str): Path to database schema file
    """

    logger.info("=======================================================")
    logger.info("                       START RUN                       ")
    logger.info("=======================================================\n")

    schema = load_schema(schema_path)

    connection = sql.create_database(db_path, schema)

    search_list = create_search_list(search_path)

    if not isinstance(search_list, (list)):
        search_list = [search_list]

    logger.info(search_list)

    for s_init in search_list:
        # msg = f"Run: {s_init}"
        # logger.info(msg)
        # print(msg)
        for s in Search.generate(s_init):
            run_scraper(s.to_dict(), connection)
    msg = "Run finished"
    logger.info(msg)
    print(msg)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("-i", "--input", default="default_search.ini", help="Config file to use for search (e.g. default.ini)")
    parser.add_argument("-d", "--database", default="default_sql", help="Path to database (e.g. default_sql.db)")
    parser.add_argument("-s", "--schema", default="db_schema.yml", help="Database schema file (e.g. db_schema.db)")
    args = parser.parse_args()

    run(args.input, args.database, args.schema)