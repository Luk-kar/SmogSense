"""
It fetches data from Twitter (known also as X) based on the provided user arguments and
tweet arguments. The acquired data is then saved to a JSON file for testing purposes.

NOTES:
1. Create an social media account on Twitter and get the 
   username, password, email to supply the `config.ini`.
   Use the `config.ini.example` as a template.
2. Due to anti-bot measures, the tests are not provided due to 
   the request limit of the Twitter servers.
3. Be aware that Twitter may occasionally block access without warning and later restore privileges.
   To minimize risks, avoid downloading excessive amounts of data in a single session. For safety
   reasons and to avoid detection or server overload, consider implementing slower download rates
   or delays between requests.
4. The number of tweets available via the search API may be 
   significantly lower than the total number
   of tweets on the server. This limitation is due to API 
   constraints, indexing, and the availability
   of historical data.
5. For production cases, an alternative solution should be implemented 
   to avoid the rate limit:
   https://developer.x.com/en/use-cases/do-research/academic-research
6. The free developer account is practically unusable even for testing purposes. (As the 16.01.2025)


WARNING: 
The code snippet is provided for educational purposes only. It is not intended for production use.
You should comply with all applicable laws, terms of service, and ethical guidelines when using 
this tool. Unauthorized scraping or misuse of APIs may violate Twitter's policies and result in
Legal consequences or account suspension.
"""

# Python
import asyncio
import json

if __name__ == "__main__":
    import os
    import sys

    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(
        current_dir
    )  # Adjust if `helpers` is not directly in the parent
    sys.path.insert(0, parent_dir)

# API
from src.data_acquisition.social_media.helpers.acquisition import (
    acquire_social_media_data,
)
from src.data_acquisition.social_media.helpers.settings import user_args, twits_args


def run_acquisition():
    """
    Run the social media data acquisition.
    """
    return asyncio.run(
        acquire_social_media_data(user_args, twits_args, max_tweets=1000)
    )


if __name__ == "__main__":
    tweets = run_acquisition()

    POLISH_SUPPORT = "utf-8"

    # For testing purposes
    with open("tweets.json", "w", encoding=POLISH_SUPPORT) as f:
        json.dump(tweets, f, ensure_ascii=False, indent=4)
