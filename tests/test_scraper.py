import pandas as pd
from tests.test_base import *

class TestScraper(TestBase):

    def test_url(self):
        search_dict = self.search_dict

        url = hs.generate_url(**search_dict)
        assert url == "https://www.hotels.com/search.do?f-price-currency-code=USD&" \
            "f-price-multiplier=1&f-price-min=0&f-price-max=10000&" \
                "f-star-rating=5,4,3,2,1&f-guest-rating-min=1&" \
                    "f-guest-rating-max=9&q-destination=Las%20Vegas,%20Nevada,%20United%20States%20of%20America&" \
                        "q-check-in=2021-05-30&q-check-out=2021-05-31&q-rooms=1&q-room-0-adults=2&q-room-0-children=0"

    def test_get_soup(self):
        
        search_dict = self.search_dict
        
        url = hs.generate_url(**search_dict)
        soup = hs.get_hotels_page(url)
        assert soup.is_empty_element == False

    def test_get_attributes(self):

        search_dict = self.search_dict
        
        url = hs.generate_url(**search_dict)
        soup = hs.get_hotels_page(url)
        res = hs.get_attributes(soup, **search_dict)
        assert sum(len(val) for val in res.values()) == len(res) * len(res["name"])

    def test_parser(self):

        search_dict = self.search_dict

        url = hs.generate_url(**search_dict)
        soup = hs.get_hotels_page(url)
        res = hs.get_attributes(soup, **search_dict)

        df_search, df_attributes = hs.get_dfs(search_dict, res)