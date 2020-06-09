import pandas as pd
import re

def parse_price(row, sale=False):
    """
    Extract price data from `price`column
    """

    row = row[1]["price"]
    # Extract dollar amounts from string
    row = re.findall(r"\$\d+", row)
    if not row:
        return None
    elif len(row) == 1:
        if sale:
            return None
        else:
            return int(row[0].lstrip("$"))
    elif len(row) >= 2:
        if sale:
            return int(row[1].lstrip("$"))
        else:
            return int(row[0].lstrip("$"))

def parse_star_rating(row):
    """
    Extract hotel star rating data from `star_rating` column
    """

    row = row[1]["star_rating"]
    return float(row.strip("-star"))

def parse_num_reviews(row):
    """
    Extract number of reviews data from `num_reviews` column
    """

    row = row[1]["num_reviews"]
    row = re.findall(r"\d+", row)
    if row:
        return int(row[0])
    else:
        return None

def parse_rating(row, sentiment=False):
    """
    Extract hotel rating data from `rating` column
    """

    row = row[1]["rating"]
    if sentiment:
        row = re.sub(r"[-+]?\d*\.\d+|\d+", "", row).strip()
        if not row:
            return None
        else:
            return row
    else:
        row = re.findall(r"[-+]?\d*\.\d+|\d+", row)
        if row:
            return float(row[0])
        else:
            return None

def parse_landmarks(row):
    """
    Extract landmarks data from `landmarks` column
    """

    row = row[1]["landmarks"]
    # Extract distance to city center
    if "miles to City center" in row:
        try:
            return float(row.split("miles to City center")[0].strip())
        except ValueError:
            return None
    elif "mile to City center" in row:
        try:
            return float(row.split("mile to City center")[0].strip())
        except ValueError:
            return None
    else:
        return None

def drop_fully_booked(df):
    return df.dropna(subset=["price", "price_sale"], how="all")
    
def parse(df):
    """
    Top-level function for parsing and formatting a Pandas DataFrame containing hotels.com 
    hotel search result data. 

    Args:
        df (pd.DataFrame): Pandas hotel attributes DataFrame to be parsed

    Returns:
        pd.DataFrame: Parsed and formatted dataframe
    """

    # Store `price` column data in new column
    df["price_metadata"] = df["price"]

    price = []
    price_sale = []
    star_rating = []
    num_reviews = []
    rating = []
    rating_sentiment = []
    city_center_distance = []

    # Row-level processing
    # Add parsing functions as needed
    for row in df.iterrows():
        price.append(parse_price(row))
        price_sale.append(parse_price(row, sale=True))
        star_rating.append(parse_star_rating(row))
        num_reviews.append(parse_num_reviews(row))
        rating.append(parse_rating(row))
        rating_sentiment.append(parse_rating(row, sentiment=True))
        city_center_distance.append(parse_landmarks(row))
    
    # Update dataframe
    df["price"] = price
    df["price_sale"] = price_sale
    df["star_rating"] = star_rating
    df["num_reviews"] = num_reviews
    df["rating"] = rating
    df["rating_sentiment"] = rating_sentiment
    df["distance_centre"] = city_center_distance

    # Drop fully booked hotels (not of interest)
    df = drop_fully_booked(df)
    
    return df