"""
This module provides helper functions and classes for constructing and validating
queries for the Twitter API, with additional arguments for language codes and date ranges.
"""

# Python
from datetime import datetime
from typing import NamedTuple

# Third-party
from iso639 import iter_langs

# ISO 639-1 language code -> language_code/full_name
code_language_name_pairs = {lg.pt1: lg.name for lg in iter_langs() if lg.pt1}


class Query:
    """
    A class to represent a query for the Twitter API.

    Attributes:
    -----------
    query : str
        The search query string.
    lang : str
        The language code for the query (ISO 639-1 standard).
    until : str
        The end date for the query in YYYY-MM-DD format.
    since : str
        The start date for the query in YYYY-MM-DD format.

    Methods:
    --------
    __str__():
        Returns the string representation of the query.
    __repr__():
        Returns the string representation of the query.

    construct_query(query: str, lang: str, until: str, since: str) -> str:
        Constructs a valid query string for the Twitter API.
    check_date(date: str) -> bool:
        Checks if the given date is in the valid format and range.
    check_lang(language: str) -> bool:
        Checks if the given language code is valid in the ISO 639-1 standard.
    """

    def __init__(self, query, lang, until, since):

        if not Query.check_date(until):
            raise ValueError(
                f"Invalid date format for 'until': {until}. Expected YYYY-MM-DD."
            )
        if not Query.check_date(since):
            raise ValueError(
                f"Invalid date format for 'since': {since}. Expected YYYY-MM-DD."
            )
        if not Query.check_lang(lang):
            raise ValueError(
                f"Invalid language code: {lang}. Expected one of: {code_language_name_pairs}."
            )

        self.query = query
        self.lang = lang
        self.until = until
        self.since = since

        self.str = f"{self.query}lang:{self.lang} until:{self.until} since:{self.since}"

        self.str = self.construct_query(self.query, self.lang, self.until, self.since)

    def __str__(self):
        return self.str

    def __repr__(self):
        return self.str

    @classmethod
    def construct_query(cls, query: str, lang: str, until: str, since: str) -> str:
        """
        Construct a valid query string for the Twitter API.
        """

        return " ".join(
            filter(
                None,
                [
                    f"{query}",
                    f"lang:{lang}" if lang else "",
                    (f"until:{until} since:{since}" if until and since else ""),
                ],
            )
        )

    @classmethod
    def check_date(cls, date: str) -> bool:
        """
        Check if the given date is in the valid format and range.
        """

        OLDEST_DATE = "2006-03-21"  # Twitter's launch date
        MOST_RECENT_DATE = datetime.now().strftime("%Y-%m-%d")  # Today's OS clock date

        try:
            # Parse the given date
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            # Parse the range limits
            oldest_date_parsed = datetime.strptime(OLDEST_DATE, "%Y-%m-%d")
            most_recent_date_parsed = datetime.strptime(MOST_RECENT_DATE, "%Y-%m-%d")

            # Check if the date is within the range
            if oldest_date_parsed <= parsed_date <= most_recent_date_parsed:
                return True
            else:
                raise ValueError(
                    f"Date {date} is out of range."
                    f"Valid range is {OLDEST_DATE} to {MOST_RECENT_DATE}."
                )

        except ValueError as error:

            raise ValueError(
                f"Invalid date format or range error: {date}. {error}"
            ) from error

    @classmethod
    def check_lang(cls, language: str) -> bool:
        """
        Check if the given language code is valid in the ISO 639-1 standard.
        """

        return language.lower() in code_language_name_pairs


class PRODUCTION(NamedTuple):
    """
    Categories for displaying tweets in the Twitter search API.

    Attributes:
    -----------
    TOP : str
        Tweets that are deemed most relevant or engaging based on Twitter's algorithm,
        typically showing popular or trending content.
    LATEST : str
        Tweets displayed in reverse chronological order, focusing on the newest posts.
    MEDIA : str
        Tweets containing images, videos, or other multimedia content, curated for users
        interested in visual content.
    """

    TOP = "Top"
    LATEST = "Latest"
    MEDIA = "Media"
