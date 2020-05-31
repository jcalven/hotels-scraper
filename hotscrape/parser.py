import pandas as pd
import re

def parse_price(row, sale=False):
    # Extract price data from `price`column
    row = row[1]["price"]
    # Extract dollar amounts from string
    row = re.findall(r"\$\d+", row)
    # row = row.findall(r"\$\d+")

    # Extract dollar amounts from string
    # df["price"] = df_.price.str.findall(r"\$\d+")

    if not row:
        return None
    elif len(row) == 1:
        if sale:
            return None
        else:
            return int(row[0].lstrip("$"))
    elif len(row) == 2:
        if sale:
            return int(row[1].lstrip("$"))
        else:
            return int(row[0].lstrip("$"))

def parse_star_rating(row):
    # Extract hotel star rating from `star_rating` column
    row = row[1]["star_rating"]
    return float(row.strip("-star"))

def parse_num_reviews(row):
    # Extract hotel star rating from `star_rating` column
    row = row[1]["num_reviews"]
    row = re.findall(r"\d+", row)
    if row:
        return int(row[0])
    else:
        return None

def parse_rating(row, sentiment=False):
    # Extract hotel star rating from `star_rating` column
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
    
def parse(df):
    # Cast date columns as datetime type
    df["checkin_date"] = pd.to_datetime(df["checkin_date"])
    df["checkout_date"] = pd.to_datetime(df["checkout_date"])

    # Store `price`column data in new column
    df["price_metadata"] = df["price"]

    price = []
    price_sale = []
    star_rating = []
    num_reviews = []
    rating = []
    rating_sentiment = []

    # df["rating_sentiment"] = df["rating"]

    # Row-level processing
    for row in df.iterrows():
        price.append(parse_price(row))
        price_sale.append(parse_price(row, sale=True))
        star_rating.append(parse_star_rating(row))
        num_reviews.append(parse_num_reviews(row))
        rating.append(parse_rating(row))
        rating_sentiment.append(parse_rating(row, sentiment=True))
    
    df["price"] = price
    df["price_sale"] = price_sale
    df["star_rating"] = star_rating
    df["num_reviews"] = num_reviews
    df["rating"] = rating
    df["rating_sentiment"] = rating_sentiment
    
    return df