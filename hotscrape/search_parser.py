from configparser import ConfigParser
import pandas as pd
from datetime import datetime, timedelta

def create_search_list(config_path):
    """
    Helper function for parsing the search config file.
    Returns a list of config section dictionaries.
    """
    config = ConfigParser()
    config.read(config_path)
    return [dict(config.items(s)) for s in config.sections()]


class MissingKeyError(Exception):
    """
    Custom exception triggered when search dictionary is missing
    a mandatory key.
    """
    def __init__(self, keyword):
        self.keyword = keyword
        self.message = f"Must specify {self.keyword}"
        super().__init__(self.message)


class ValueOutOfRangeError(Exception):
    """
    Custom exception triggered when search dictionary items are out of range.
    """
    def __init__(self, name, val, min, max):
        self.val = val
        if val > max:
            cond = f"{name} > {max} ({val} > {max})"
        elif val < min:
            cond = f"{name} < {min} ({val} < {min})"
        else:
            cond = ""
        self.message = f"Value is out of range: {cond} [{min} <= {name} <= {max}]"
        super().__init__(self.message)


class Search():
    """
    Class to structure the search config file content into a format required by scraper.py
    """

    __counter = 0

    search_key_limits = {
        "checkin_datetime": None, 
        "checkout_datetime": None,
        "price_min": (0, 10000),
        "price_max": (0, 10000),
        "price_multiplier": (1, 20),
        "star_rating_min": (1, 5),
        "star_rating_max": (1, 5),
        "guest_rating_min": (1, 9),
        "guest_rating_max": (1, 9),
        "distance_centre": (0, 50),
        "rooms": (1, 10),
        "adults": (1, 10),
        "children": (0, 20),
        "currency": None
        }

    @classmethod
    def _count(cls):
        cls.__counter += 1
        return cls.__counter
    @classmethod
    def _reset_count(cls):
        cls.__counter = 0

    @classmethod
    def generate(cls, config, count_key="search_span"):
        """
        Creates an iterator of Search instances with unique checkin/checkout dates

        Args:
            config (dict): Search config content
            count_key (str, optional): Key to use for search span. Defaults to "search_span".

        Yields:
            Search: Unique Search instances
        """
        search_span = int(config.get(count_key))
        if search_span is not None:
            for i in range(search_span):
                yield cls(config)
        cls._reset_count()

    @staticmethod
    def _recast(string):
        """
        Check if string is int, float, or neither. Returns correctly typecasted input.
        """
        if string == "None":
            return eval(string)
        try:
            return int(string)
        except ValueError:
            pass
        try:
            return float(string)
        except ValueError:
            pass
        finally:
            return string

    @staticmethod
    def _check_value_range(name, val, min, max, is_none=False):
        if not is_none:
            if val < min or val > max:
                raise ValueOutOfRangeError(name, val, min, max)

    def __init__(self, config):

        self.counter = self._count()

        # Search dict from config file
        self.config = config

        # Default search values
        self.city = None
        self.state = None
        self.country = None
        self.checkin_datetime = None 
        self.checkout_datetime = None
        self.price_min = 0
        self.price_max = 10000
        self.price_multiplier = 1
        self.star_rating_min = 1
        self.star_rating_max = 5
        self.guest_rating_min = 1
        self.guest_rating_max = 9
        self.distance_centre = None
        self.rooms = 1
        self.adults = 2
        self.children = 0
        self.currency = "USD"

        # Number of nights
        self.nights = 1 

        # Search span in days
        self.search_span = 182

        self.check_input()

    def to_dict(self):
        """
        Returns a search dictionary that is accepted by scraper.py
        """
        destination = {
            "city": self.city,
            "state": self.state,
            "country": self.country
        }
        res = {key: self.__getattribute__(key) for key in self.search_key_limits}
        res["destination"] = destination
        return res

    def check_input(self, config=None):
        """
        Checks search config parameters for problems and updates parameters where needed.
        """

        for key, val in self.config.items():
            val = self._recast(val)

            if self.search_key_limits.get(key) is not None:
                # Exception for search parameters that are allowed to be None
                if key == "distance_centre":
                    self._check_value_range(key, val, *self.search_key_limits.get(key), is_none=True)
                else:
                    self._check_value_range(key, val, *self.search_key_limits.get(key), is_none=False)

            if key == "checkin_datetime":
                if val is None:
                    t_start = datetime.now() + timedelta(days=self.counter)
                else:
                    t_start = pd.to_datetime(val) + timedelta(days=self.counter-1)
                self.__setattr__(key, t_start)
            else:
                self.__setattr__(key, val)

        if self.__getattribute__("checkout_datetime") is None:
                self.__setattr__("checkout_datetime", self.__getattribute__("checkin_datetime") + timedelta(days=self.nights))

        for key in ["city", "state", "country"]:
            if self.__getattribute__(key) is None:
                MissingKeyError(key)