import logging
import pandas as pd
from datetime import datetime, timedelta
import hotscrape.scraper as hs
from hotscrape.utils import load_schema
import hotscrape.sql as sql
# from . import scraper as hs
# from . utils import load_schema
# from . import sql
# logging.basicConfig(filename='logs/run.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.basicConfig(filename='logs/run.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger('hotels-scraper.run')

def run_scraper(search, connection):
    df_search, df_attributes = hs.run(search)
    # Upsert search and search results to DB
    sql.to_sql(df_search, "search", connection)
    sql.to_sql(df_attributes, "hotels", connection)
    # df_search.to_sql("search", connection, if_exists="append", index=True)
    # df_attributes.to_sql("hotels", connection, if_exists="append", index=True)

def run(search, db_path="hotels-scraper/test_sql"):
    logger.info("Start run\n")

    schema = load_schema()

    connection = sql.create_database("./test_sql", schema)

    if not isinstance(search, (list)):
        search = [search]

    for s in search:
        run_scraper(s, connection)
    logger.info("Run finished")

if __name__ == "__main__":
    
    t_start = datetime.now() + timedelta(days=1)
    t_end = t_start + timedelta(days=181)
    list_checkin = pd.date_range(t_start, t_end, freq='D').strftime("%Y-%m-%d").tolist()

    search_dict = {
        "destination": {"city": "Las Vegas", "state": "Nevada", "country": "United States of America"},
        "checkin_datetime": None, 
        "checkout_datetime": None,
        "price_min": 0,
        "price_max": 10000,
        "price_multiplier": 1,
        "star_rating_min": 1,
        "star_rating_max": 5,
        "guest_rating_min": 1,
        "guest_rating_max": 9,
        "distance_centre": None,
        "rooms": 1,
        "adults": 2,
        "children": 0,
        "currency": "USD"
        }  
    
    # Build array of search dicts with different checkin dates
    search = []
    for checkin in list_checkin:
        search_dict.update(checkin_datetime=checkin)
        search.append(dict(search_dict))

    schema = load_schema()
    run(search, schema)