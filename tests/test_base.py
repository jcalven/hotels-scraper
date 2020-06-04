import yaml
import hotscrape.scraper as hs
from hotscrape.parser import parse

class TestBase():

    search_dict = {
        "destination": {"city": "Las Vegas", "state": "Nevada", "country": "United States of America"},
        "checkin_datetime": "2020-06-30",
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
        "currency": "USD",
    }

    schema_path = "./"
    with open(f"{schema_path}/db_schema.yml") as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        schema = yaml.load(file, Loader=yaml.FullLoader)