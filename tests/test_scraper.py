import hotscrape.scraper as hs
from hotscrape.parser import parse
import pandas as pd

class Test():

    search_dict = {
        "destination": {"city": "Las Vegas", "state": "Nevada", "country": "United States of America"},
        "checkin_date": "2020-05-30",
        "checkout_date": None,
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

    def test_url(self):
        url = hs.generate_url(**self.search_dict)
        assert url == "https://www.hotels.com/search.do?f-price-currency-code=USD&" \
            "f-price-multiplier=1&f-price-min=0&f-price-max=10000&" \
                "f-star-rating=5,4,3,2,1&f-guest-rating-min=1&" \
                    "f-guest-rating-max=9&q-destination=Las%20Vegas,%20Nevada,%20United%20States%20of%20America&" \
                        "q-check-in=2021-05-30&q-check-out=2021-05-31&q-rooms=1&q-room-0-adults=2&q-room-0-children=0"

    def test_get_soup(self):
        url = hs.generate_url(**self.search_dict)
        soup = hs.get_hotels_page(url)
        assert soup.is_empty_element == False

    def test_get_attributes(self):
        url = hs.generate_url(**self.search_dict)
        soup = hs.get_hotels_page(url)
        res = hs.get_attributes(soup)
        bla = "bla"
    #raw_hotel_2_0, souppp = combine_df(search_dict)

    def test_parser(self):
            url = hs.generate_url(**self.search_dict)
            soup = hs.get_hotels_page(url)
            res = hs.get_attributes(soup, **self.search_dict)
            df = pd.DataFrame(res)
            df_parsed = parse(df)
            pass