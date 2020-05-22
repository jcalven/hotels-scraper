import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
import re
import json

from datetime import date
from datetime import datetime
import calendar
from dateutil.parser import parse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import chromedriver_binary
# driver = webdriver.Chrome()

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class Scraper(object):

    def __init__(self,):

        pass

    #def 


def get_hotels_page(url):    
    
    '''
    Takes an url from Hotels.com and 
    infinitely scrolls down to end of page
    until no more content can be loaded.
    '''
    # Open up chrome in incognito
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--incognito")
    # driver = webdriver.Chrome()
    
    options = Options()
    options.add_argument('--private')
    options.add_argument("--headless")
    driver = Firefox(executable_path="geckodriver", options=options)
    driver.set_window_size(1920,1080)

    # Nagivate to url 
    driver.get(url)
    
    # Scroll down until the end of the page
    scroll_count = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            if driver.find_element_by_id("listings-loading").value_of_css_property("display") == "block":
                scroll_count = 0
            else:
                time.sleep(0.5)
                scroll_count += 1
        except:
            continue
 
        if any([cur_elem.is_displayed() for cur_elem in driver.find_elements_by_class_name("info")]):
            break

        if scroll_count > 20:
            break
            
    # Grabs the html of the fully scrolled-down page and parse it with BeautifulSoup  
    # innerHTML = driver.execute_script('return document.body.innerHTML')
    innerHTML = driver.page_source
    parsed_html = BeautifulSoup(innerHTML, 'lxml')
    driver.close()
    return parsed_html

def generate_url(destination, checkin_date, checkout_date=None, price_min=0, price_max=10000, price_multiplier=1, 
                 star_rating_min=1, star_rating_max=5, guest_rating_min=1, guest_rating_max=9, distance_centre=None, 
                 rooms=1, adults=2, children=0, currency="USD"):

#https://www.hotels.com/search.do?resolved-location=CITY%3A1504033%3AUNKNOWN%3AUNKNOWN&f-price-currency-code=USD&f-price-multiplier=1&f-price-min=30&f-price-max=395&f-star-rating=5,4,3,2,1&f-guest-rating-min=2&f-guest-rating-max=9&f-distance=2.0&f-lid=1504033&destination-id=1504033&q-destination=Las%20Vegas,%20Nevada,%20United%20States%20of%20America&q-check-in=2020-05-13&q-check-out=2020-05-14&q-rooms=1&q-room-0-adults=2&q-room-0-children=0&sort-order=DISTANCE_FROM_LANDMARK

    # Concatenate star rating list into string of correct format
    star_rating = "".join(map(lambda x: str(x)+",", range(star_rating_max,star_rating_min-1,-1))).rstrip(",")

    # Format destination dict
    destination = {key: val.replace(" ", "%20") for key, val in destination.items()}
    dest_field_1 = destination.get("city")
    dest_field_2 = destination.get("state")
    dest_field_3 = destination.get("country")

    if not checkout_date:
        checkout_date = (pd.to_datetime(checkin_date) + pd.DateOffset(1)).strftime("%Y-%m-%d")

    url = "".join([
        "https://www.hotels.com/search.do?",
        f"f-price-currency-code={currency}&",
        f"f-price-multiplier={price_multiplier}&",
        f"f-price-min={price_min}&",
        f"f-price-max={price_max}&",
        f"f-star-rating={star_rating}&",
        f"f-guest-rating-min={guest_rating_min}&",
        f"f-guest-rating-max={guest_rating_max}&",
        f"f-distance={distance_centre}&" if distance_centre else "",
        f"q-destination={dest_field_1},%20{dest_field_2},%20{dest_field_3}&",
        f"q-check-in={checkin_date}&",
        f"q-check-out={checkout_date}&",
        f"q-rooms={rooms}&",
        f"q-room-0-adults={adults}&",
        f"q-room-0-children={children}"
    ])

    return url

feature_html_details = {'name': ('h3', 'p-name'),
                        'address': ('span', 'address'),
                        'maplink': ('a', 'map-link xs-welcome-rewards'),
                        'landmarks': ('ul', 'property-landmarks'),
                        'amenities': ('ul', 'hmvt8258-amenities'),
                        'details': ('div', 'additional-details resp-module'),
                        'review_box': ('div', 'details resp-module'),
                        'rating': ('strong', re.compile('guest-reviews-badge.*')),
                        'num_reviews': ('span','small-view'),
                        'price': ('aside', re.compile('pricing resp-module.*')),
                        'star_rating': ('span', 'star-rating-text')}


def get_content_list(soup, tag, class_):
    raw = soup.find_all(tag, {'class': class_})
    raw_list = [content.text for content in raw]
    return raw_list


def get_attributes(soup):

    attributes_dict = {key: get_content_list(soup, feature_html_details[key][0], feature_html_details[key][1]) for key in feature_html_details}
    n_hotels = len(attributes_dict["name"])
    # attributes_dict["checkin"] = [checkin] * n_hotels
    # attributes_dict["checkout"] = [checkout] * n_hotels
    # attributes_dict["adults"] = [adults] * n_hotels
    # attributes_dict["children"] = [children] * n_hotels

    #print(f'{checkin} and {checkout} is successful!', hotel_df.shape)
    return attributes_dict

# def combine_df(search):
    # """
    # [summary]

    # Args:
    #     dates ([type]): [description]
    #     adults (str, optional): [description]. Defaults to '2'.
    #     children (str, optional): [description]. Defaults to '0'.

    # Returns:
    #     [type]: [description]
    # """
    
    # # combined_hotel_df = pd.DataFrame()

    
    # # for ii, date in enumerate(dates):
    # #     n_dates = len(dates)
    # #     print(f"({ii+1}/{n_dates}) Scraping {date[0]}")
    # #     url = generate_url(date[0], date[1], adults, children)
    # #     soup = get_hotels_page(url)
    # #     try:
    # #         partial_df = get_attributes(soup, date[0], date[1], adults, children)
    # #         #combined_hotel_df = pd.concat([combined_hotel_df, partial_df], ignore_index = True)
    # #         with open("hotels_vegas.json", "a", encoding='utf-8') as file:
    # #             json.dump(partial_df, file, indent=4)
    # #     except:
    # #         print(f" -Skipping {date[0]}...")
    # #         pass
    # #     #if ii == 5:
    # #     #    break
            
    # # #print(f'This dataset has {combined_hotel_df.shape[0]} rows and {combined_hotel_df.shape[0]} columns')
    # # return partial_df, soup #combined_hotel_df



if __name__ == '__main__':

    # list_checkin = pd.date_range('2020-05-05', '2020-11-05', freq='D').strftime("%Y-%m-%d").tolist()
    # list_checkout = pd.date_range('2020-05-06', '2020-11-06', freq='D').strftime("%Y-%m-%d").tolist()

    #dates_list = []
    #for checkin, checkout in zip(list_checkin, list_checkout):
    #    dates_list.append((checkin, checkout))

    search_dict = {
        "destination": {"city": "Las Vegas", "state": "Nevada", "country": "United States of America"},
        "checkin_date": "2020-05-20",
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

    url = generate_url(**search_dict)
    soup = get_hotels_page(url)
    res = get_attributes(soup)
    #raw_hotel_2_0, souppp = combine_df(search_dict)