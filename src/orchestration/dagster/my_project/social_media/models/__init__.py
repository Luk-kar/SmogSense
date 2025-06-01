"""
Defines SQLAlchemy models for the 'social_media' data,
including User, Tweet, Engagement, Place, BoundingBox, Hashtag, and HashtagTweet.

Mirrors the provided dbdiagram with references and primary keys.
"""

# SQLAlchemy
from sqlalchemy import (
    BigInteger,
    Column,
    String,
    Text,
    Boolean,
    Integer,
    ForeignKey,
    MetaData,
    CheckConstraint,
    SMALLINT,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Third-party
# For handling geometry columns (PostGIS)
from geoalchemy2 import Geometry

# Set up your schema name
SCHEMA_NAME = "social_media_dim"

# Standard WGS 84 coordinate system used for GPS and mapping:
# https://en.wikipedia.org/wiki/World_Geodetic_System
SRID_WGS84 = 4326

# Create a MetaData object referencing that schema
metadata_social_media = MetaData(schema=SCHEMA_NAME)

# Base class for your models
BaseSocialMedia = declarative_base(metadata=metadata_social_media)


class Tweet(BaseSocialMedia):
    """
    tweet table: stores main tweet content and references user.
    id_tweet is a varchar PK.
    """

    __tablename__ = "tweet"
    __table_args__ = (
        CheckConstraint(
            "TRIM(text) != ''", name="check_tweet_text_not_empty"
        ),  # Ensure text is not empty
        CheckConstraint(
            "created_at >= '2006-03-21 00:00:00+00'", name="check_created_at_valid_date"
        ),  # Ensure date is not older than Twitter's launch
        CheckConstraint(
            "day_of_week BETWEEN 1 AND 7", name="check_day_of_week_range"
        ),  # Ensure day_of_week value is within valid range
        CheckConstraint(
            "month BETWEEN 1 AND 12", name="check_month_range"
        ),  # Ensure month value is within valid range
        {"schema": SCHEMA_NAME},
    )

    # Columns:
    id_tweet = Column(BigInteger, primary_key=True)
    id_user = Column(
        BigInteger, ForeignKey(f"{SCHEMA_NAME}.user.id_user"), nullable=False
    )

    text = Column(Text, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    day_of_week = Column(SMALLINT, nullable=False)
    month = Column(SMALLINT, nullable=False)

    id_place = Column(
        BigInteger, ForeignKey(f"{SCHEMA_NAME}.place.id_place"), nullable=True
    )

    # Relationships:
    # one-to-one:
    engagement = relationship("Engagement", back_populates="tweet", uselist=False)
    user = relationship("User", back_populates="tweet", uselist=False)
    place = relationship("Place", back_populates="tweet", uselist=False)
    # one-to-many:
    tweet_hashtag = relationship("HashtagTweet", back_populates="tweet")


class User(BaseSocialMedia):
    """
    User table: stores user-specific attributes.
    id_user is a varchar PK.
    """

    __tablename__ = "user"
    __table_args__ = (
        CheckConstraint("favourite_count >= 0", name="check_favourite_count_positive"),
        CheckConstraint("follower_count >= 0", name="check_follower_count_positive"),
        CheckConstraint("listed_count >= 0", name="check_listed_count_positive"),
        CheckConstraint("tweet_count >= 0", name="check_tweet_count_positive"),
        {"schema": SCHEMA_NAME},
    )

    # Columns
    id_user = Column(BigInteger, primary_key=True, autoincrement=False)
    favourite_count = Column(Integer, nullable=False)
    follower_count = Column(Integer, nullable=False)
    listed_count = Column(Integer, nullable=False)
    tweet_count = Column(Integer, nullable=False)
    is_verified_paid_blue = Column(Boolean, nullable=False)
    is_verified_unpaid = Column(Boolean, nullable=False)

    # Relationship: a user can have many tweet
    # one-to-many:
    tweet = relationship("Tweet", back_populates="user")


class Engagement(BaseSocialMedia):
    """
    Engagement table: 1-to-1 with a tweet, storing engagement metrics.
    id_tweet is both the PK and an FK to tweet.
    """

    __tablename__ = "engagement"
    __table_args__ = (
        CheckConstraint("like_count >= 0", name="check_like_count_positive"),
        CheckConstraint("retweet_count >= 0", name="check_retweet_count_positive"),
        CheckConstraint("quote_count >= 0", name="check_quote_count_positive"),
        CheckConstraint("reply_count >= 0", name="check_reply_count_positive"),
        CheckConstraint("view_count >= 0", name="check_view_count_positive"),
        {"schema": SCHEMA_NAME},
    )

    # Columns
    id_tweet = Column(
        BigInteger, ForeignKey(f"{SCHEMA_NAME}.tweet.id_tweet"), primary_key=True
    )
    like_count = Column(Integer, nullable=False)
    retweet_count = Column(Integer, nullable=False)
    quote_count = Column(Integer, nullable=False)
    reply_count = Column(Integer, nullable=False)
    view_count = Column(BigInteger, nullable=False)

    # Relationship back to the single tweet
    # one-to-one:
    tweet = relationship("Tweet", back_populates="engagement", uselist=False)


class Place(BaseSocialMedia):
    """
    Place table: optional location details linked to tweet.
    id_place is bigint PK.
    """

    __tablename__ = "place"
    __table_args__ = (
        CheckConstraint("TRIM(country) != ''", name="check_country_not_empty"),
        CheckConstraint(
            "TRIM(country_code) != ''", name="check_country_code_not_empty"
        ),
        CheckConstraint("TRIM(full_name) != ''", name="check_full_name_not_empty"),
        CheckConstraint("TRIM(place_name) != ''", name="check_place_name_not_empty"),
        CheckConstraint("TRIM(place_type) != ''", name="check_place_type_not_empty"),
        UniqueConstraint(
            "id_bounding_box",
            "country",
            "country_code",
            "full_name",
            "place_name",
            "place_type",
            name="uq_place_unique",
        ),
        {"schema": SCHEMA_NAME},
    )

    # Columns
    id_place = Column(BigInteger, primary_key=True, autoincrement=True)
    id_bounding_box = Column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.bounding_box.id_bounding_box"),
        nullable=True,
    )

    # GeoAlchemy2 Geometry column for spatial data (Point type with SRID 4326)
    centroid = Column(
        Geometry("POINT", srid=SRID_WGS84),
        nullable=True,
    )

    country = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    place_name = Column(String, nullable=False)
    place_type = Column(String, nullable=False)

    # Relationship: one bounding box per place
    bounding_box = relationship("BoundingBox", back_populates="place")

    # Relationship: a place can be referenced by many tweet
    # one-to-many:
    tweet = relationship("Tweet", back_populates="place")


class BoundingBox(BaseSocialMedia):
    """
    BoundingBoxes table: detailed bounding box geometry for a place.
    id_bounding_box is bigint PK.
    """

    __tablename__ = "bounding_box"
    __table_args__ = (
        CheckConstraint(
            "TRIM(type) != ''", name="check_type_not_empty"
        ),  # Ensure type is non-empty
        CheckConstraint(
            "type IN ('Point', 'Polygon', 'MultiPolygon')",
            name="check_valid_type",
        ),
        {"schema": SCHEMA_NAME},
    )

    id_bounding_box = Column(BigInteger, primary_key=True, autoincrement=True)

    # GeoAlchemy2 Geometry column to store spatial bounding box data
    coordinates = Column(
        Geometry("GEOMETRY", srid=SRID_WGS84),
        nullable=False,
        unique=True,  # Each bounding box should have unique coordinates
    )

    # Restrict to valid geometry types: Point, Polygon, MultiPolygon
    type = Column(String, nullable=False)
    # Relationship: one bounding box can be used by many place (if you want strictly 1-1, you can keep it that way).
    # one-to-many:
    place = relationship("Place", back_populates="bounding_box")


class Hashtag(BaseSocialMedia):
    """
    Hashtag table: master list of hashtag, each with a unique ID.
    """

    __tablename__ = "hashtag"
    __table_args__ = (
        CheckConstraint(
            "TRIM(hashtag_name) != ''", name="check_hashtag_name_not_empty"
        ),  # Ensure hashtag_name is non-empty
        {"schema": SCHEMA_NAME},
    )

    id_hashtag = Column(BigInteger, primary_key=True)
    hashtag_name = Column(String, nullable=False, unique=True)

    # Relationship: a hashtag can appear in many tweet
    # one-to-many:
    tweet_hashtag = relationship("HashtagTweet", back_populates="hashtag")


class HashtagTweet(BaseSocialMedia):
    """
    Hashtag-Tweet bridge table (many-to-one relationship).
    Candidate key on (id_tweet, id_hashtag).
    """

    __tablename__ = "tweet_hashtag"
    __table_args__ = (
        UniqueConstraint("id_tweet", "id_hashtag", name="uq_tweet_hashtag"),
        {"schema": SCHEMA_NAME},
    )

    # Columns
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_tweet = Column(
        BigInteger,
        ForeignKey(f"{SCHEMA_NAME}.tweet.id_tweet"),
        nullable=False,
    )
    id_hashtag = Column(
        Integer, ForeignKey(f"{SCHEMA_NAME}.hashtag.id_hashtag"), nullable=False
    )

    # Relationships:
    # many-to-one: Many HashtagTweet rows can reference the same Tweet
    tweet = relationship("Tweet", back_populates="tweet_hashtag")

    # many-to-one: Many HashtagTweet rows can reference the same Hashtag
    hashtag = relationship("Hashtag", back_populates="tweet_hashtag")
