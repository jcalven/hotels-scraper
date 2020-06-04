import pandas as pd
from bs4 import BeautifulSoup
import time
import re
import logging
from datetime import datetime
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from . parser import parse

logger = logging.getLogger("hotels-scraper.scraper.scraper")

feature_html_details = {'name': ('h3', 'p-name'),
                        'address': ('span', 'address'),
                        # 'maplink': ('a', 'map-link xs-welcome-rewards'),
                        'landmarks': ('ul', 'property-landmarks'),
                        'amenities': ('ul', 'hmvt8258-amenities'),
                        'details': ('div', 'additional-details resp-module'),
                        'review_box': ('div', 'details resp-module'),
                        'rating': ('strong', re.compile('guest-reviews-badge.*')),
                        'num_reviews': ('span','small-view'),
                        'price': ('aside', re.compile('pricing resp-module.*')),
                        'star_rating': ('span', 'star-rating-text')}

def get_hotels_page(url, max_scroll=20):    
    
    """
    Takes an url from Hotels.com and 
    infinitely scrolls down to end of page
    until no more content can be loaded.
    """
    # Open up chrome in incognito
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--incognito")
    # driver = webdriver.Chrome()
    
    logger.info("Opening URL\n")

    options = Options()
    options.add_argument('--private')
    options.add_argument("--headless")
    driver = Firefox(executable_path="geckodriver", options=options)
    driver.set_window_size(1920,1080)

    # Nagivate to url 
    driver.get(url)
    
    # Scroll down until the end of the page
    logger.info("Start scraping ...")
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
            logger.info("Scraping ended")
            break

        if scroll_count >= max_scroll:
            logger.info(f"Reached maximum number of page loads ({scroll_count}/{max_scroll}). Stopping ...")
            break
            
    # Grabs the html of the fully scrolled-down page and parse it with BeautifulSoup  
    # innerHTML = driver.execute_script('return document.body.innerHTML')
    parsed_html = BeautifulSoup(driver.page_source, 'lxml')
    driver.close()
    return parsed_html

def generate_url(destination, checkin_datetime, checkout_datetime=None, price_min=0, price_max=10000, price_multiplier=1, 
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

    # Format checkin/checkout dates
    checkin_date = checkin_datetime.strftime("%Y-%m-%d")
    checkout_date = checkout_datetime.strftime("%Y-%m-%d")

    # if not checkout_date:
    #     checkout_date = (pd.to_datetime(checkin_date) + pd.DateOffset(1)).strftime("%Y-%m-%d")

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

    logger.info(f"Searching url: {url}\n")
    return url

def get_content_list(soup, tag, class_):
    raw = soup.find_all(tag, {'class': class_})
    raw_list = [content.text for content in raw]
    return raw_list

def get_attributes(soup, **search_dict):
    attributes_dict = {key: get_content_list(soup, feature_html_details[key][0], feature_html_details[key][1]) for key in feature_html_details}
    return attributes_dict

def get_dfs(search_dict, attributes_dict):

    ### Processing `search_dict`
    # Expand `destination` field 
    tmp_dict = {key: val for key, val in search_dict["destination"].items()}
    search_dict.update(tmp_dict)
    del search_dict["destination"]

    # Add search timestamp if not already there
    # if not search_dict["search_datetime"]:
    search_dict["search_datetime"] = datetime.now()
    
    # Create search dataframe
    df_search = pd.DataFrame(search_dict, index=[0])

    # Create primary key from hashed dataframe
    primary_key = pd.util.hash_pandas_object(df_search, index=False)[0] % 0xffffffff
    df_search["id"] = primary_key.astype(int)
    df_search.set_index("id", drop=True, inplace=True)

    # Create new, derived, fields
    df_search["days_from_search"] = (df_search["checkin_datetime"] - df_search["search_datetime"]).dt.days
    df_search["nights"] = (df_search["checkout_datetime"] - df_search["checkin_datetime"]).dt.days

    ### Processing `attributes_dict`
    # Create attributes dataframe
    df_attributes = parse(pd.DataFrame(attributes_dict))

    # Add primary_key to attributes dataframe
    df_attributes["search_id"] = primary_key
    # Create another primary key 
    primary_key = pd.util.hash_pandas_object(df_attributes, index=False) % 0xffffffff
    df_attributes["id"] = primary_key.astype(int)

    # Drop rows with non-unique id's
    df_attributes.drop_duplicates(subset=["id"], inplace=True)
    df_attributes.set_index("id", drop=True, inplace=True)

    return df_search, df_attributes

def ensure_search_format(search_dict):

    logger.info(f"Search parameters: {search_dict}\n")

    # Check destination formatting
    assert search_dict.get("destination") is not None
    assert search_dict.get("destination").get("city") is not None
    assert search_dict.get("destination").get("state") is not None
    assert search_dict.get("destination").get("country") is not None

    # Check checkin/checkout formatting
    search_dict["checkin_datetime"] = pd.to_datetime(search_dict.get("checkin_datetime"))
    if not search_dict.get("checkout_datetime"):
        search_dict["checkout_datetime"] = search_dict.get("checkin_datetime") + pd.DateOffset(1)
    return search_dict

def run(search):
    """[summary]

    Args:
        search ([type]): [description]

    Returns:
        [type]: [description]
    """

    logger.info("\n\n")
    logger.info("Scraper initiated")
    # logger.info(f"Search parameters: {search}")


    search_dict = ensure_search_format(search)
    url = generate_url(**search_dict)
    
    soup = get_hotels_page(url)
    res = get_attributes(soup, **search_dict)

    df_search, df_attributes = get_dfs(search_dict, res)
    return df_search, df_attributes