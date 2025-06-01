"""
This module provides functionality to acquire social media data using the Twikit API
in the final form of the application.
"""

# Python
from datetime import datetime
import random
import time
from typing import Union

# Third-party
from twikit import TooManyRequests

# API
from src.data_acquisition.social_media.helpers.client_setup import (
    setup_client_connection,
)
from src.data_acquisition.social_media.helpers.fetching import (
    get_tweets,
    extract_tweet_records,
)
from src.data_acquisition.social_media.helpers._time import get_random_wait_time


async def acquire_social_media_data(
    user_args: dict[str, str],
    twits_args: dict[str, Union[str, int]],
    max_tweets: int = 100,
):
    """
    Acquire social media data using the Twikit API.
    """

    client = await setup_client_connection(user_args)

    tweets_count = 0
    tweets = None
    tweet_records = []

    while tweets_count < max_tweets:

        try:
            tweets = await get_tweets(client, twits_args, tweets)

            if not tweets:
                print(f"{datetime.now()} - No more tweets found")
                break

            extract_tweet_records(tweets, tweet_records)

            tweets_count += len(tweet_records)

            print(f"Tweets extracted:\n{len(tweet_records)}.")

        except TooManyRequests as e:

            reset_time = datetime.fromtimestamp(
                getattr(e, "rate_limit_reset", datetime.now().timestamp())
            )

            handle_rate_limit(reset_time)

            continue

    print(f"{datetime.now()} - Done! Got {len(tweet_records)} tweets found")

    return tweet_records


def handle_rate_limit(reset_time: datetime):
    """
    Handle the rate limit by waiting until the reset time.
    """
    wait_buffer = get_random_wait_time()

    time_to_reset = reset_time - datetime.now()
    reset_seconds = time_to_reset.total_seconds()

    if reset_seconds > wait_buffer:

        # add a random delay to avoid detection
        additional_delay = random.uniform(0.1, 0.9)
        print(f"{datetime.now()} - Rate limit reached. Waiting until {reset_time}.")
        time.sleep(reset_seconds + additional_delay)

    else:
        print(
            f"{datetime.now()} - Rate limit reached. Waiting for {wait_buffer} seconds."
        )
        time.sleep(wait_buffer)
