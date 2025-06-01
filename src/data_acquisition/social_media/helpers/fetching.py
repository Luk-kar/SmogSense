"""
It includes functions to retrieve tweets, extract tweet records, and create structured tweet data.
This module provides helper functions for fetching and processing tweets from the Twikit API.
"""

# Python
import time
from datetime import datetime

# Third-party
from twikit import Client

# API
from src.data_acquisition.social_media.helpers._time import get_random_wait_time


def get_tweets(client: Client, twits_args: dict, tweets: dict) -> dict:
    """
    Get tweets from the Twikit API.
    """

    if tweets is None:
        print(f"{datetime.now()} - Getting tweets...")
        tweets = client.search_tweet(**twits_args)

    else:
        wait_time = get_random_wait_time()
        print(f"{datetime.now()} - Getting next tweets after {wait_time} seconds ...")
        time.sleep(wait_time)
        tweets = tweets.next()

    return tweets


def extract_tweet_records(tweets: dict, tweet_records: list[dict]):
    """
    Extract tweet records from the given tweets.
    """

    for tweet in tweets:

        tweet_dict = create_tweet_record(tweet)

        tweet_records.append(tweet_dict)


def create_tweet_record(tweet: dict) -> dict:
    """
    Create a record for a tweet.
    """

    tweet_dict = {
        "text": tweet.text,
    }

    tweet_dict["engagement"] = {
        "like_count": tweet.favorite_count,
        "retweet_count": tweet.retweet_count,
        "quote_count": tweet.quote_count,
        "reply_count": tweet.reply_count,
        "view_count": tweet.view_count,
    }

    tweet_dict["ids"] = {
        "id_user": tweet.user.id,
        "id_tweet": tweet.id,
        "reply_twit": getattr(tweet, "in_reply_to", None),
    }

    tweet_dict["user"] = {
        "tweets_count": tweet.user.statuses_count,
        "followers_count": tweet.user.followers_count,
        "favourites_count": tweet.user.favourites_count,
        "listed_count": tweet.user.listed_count,
        "withheld_in_countries": tweet.user.withheld_in_countries,
        "is_verified_paid_blue": tweet.user.verified,
        "is_verified_unpaid": tweet.user.verified,
    }

    if tweet.created_at:
        tweet_dict["created_at"] = tweet.created_at

    if tweet.hashtags:
        tweet_dict["hashtags"] = tweet.hashtags

    if tweet.place:
        tweet_place = {
            "place_name": tweet.place.name,
            "full_name": tweet.place.full_name,
            "country": tweet.place.country,
            "country_code": tweet.place.country_code,
            "place_type": tweet.place.place_type,
            "bounding_box": tweet.place.bounding_box,
            "centroid": tweet.place.centroid,
        }

        tweet_dict["place"] = tweet_place
    return tweet_dict
