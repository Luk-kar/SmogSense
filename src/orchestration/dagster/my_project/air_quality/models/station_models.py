"""
This module defines SQLAlchemy models for the 'air quality station' data, including Province, Area, Location, and Station.
It also includes a custom Query class for applying default ordering to queries.


https://powietrze.gios.gov.pl/pjp/content/api
"""

# SQLAlchemy
from sqlalchemy import (
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

SCHEMA_NAME = "air_quality_dim_station"
metadata_station = MetaData(schema=SCHEMA_NAME)
BaseStation = declarative_base(metadata=metadata_station)


# Define SQLAlchemy models matching the PostgreSQL tables
class Province(BaseStation):
    """
    Province model for the 'province' table in the 'air_quality_dim_station' schema.
    """

    __tablename__ = "province"

    id_province = Column(Integer, primary_key=True, autoincrement=True)
    province = Column(String(255), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("TRIM(province) != ''", name="check_province_not_empty"),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"province": "asc"}

    areas = relationship("Area", back_populates="province")


class Area(BaseStation):
    """
    Area model for the 'area' table in the 'air_quality_dim_station' schema.
    """

    __tablename__ = "area"

    id_area = Column(Integer, primary_key=True, autoincrement=False)
    city_district = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    county = Column(String(255), nullable=False)
    id_province = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.province.id_province"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "city_district",
            "city",
            "county",
            "id_province",
            name="uq_area_location",
        ),
        CheckConstraint(
            "TRIM(city_district) != ''", name="check_city_district_not_empty"
        ),
        CheckConstraint("TRIM(city) != ''", name="check_city_not_empty"),
        CheckConstraint("TRIM(county) != ''", name="check_county_not_empty"),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {
        "id_province": "asc",
        "county": "asc",
        "city": "asc",
        "city_district": "asc",
    }

    province = relationship("Province", back_populates="areas")
    locations = relationship("Location", back_populates="area")


class Location(BaseStation):
    """
    Location model for the 'location' table in the 'air_quality_dim_station' schema.
    """

    __tablename__ = "location"

    id_location = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    id_area = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.area.id_area"),
        nullable=False,
    )
    street_address = Column(String(255), nullable=True)

    __table_args__ = (
        Index(
            "uq_location_street_address",
            "latitude",
            "longitude",
            "id_area",
            "street_address",
            unique=True,
            postgresql_where=street_address.isnot(None),
        ),
        Index(
            "uq_location_no_street_address",
            "latitude",
            "longitude",
            "id_area",
            unique=True,
            postgresql_where=street_address.is_(None),
        ),
        CheckConstraint(
            "latitude >= -90 AND latitude <= 90",
            name="check_latitude_range",
        ),
        CheckConstraint(
            "longitude >= -180 AND longitude <= 180",
            name="check_longitude_range",
        ),
        CheckConstraint(
            "TRIM(street_address) != ''", name="check_street_address_not_empty"
        ),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {
        "latitude": "asc",
        "longitude": "asc",
        "street_address": "asc",
    }

    area = relationship("Area")

    station = relationship("Station", back_populates="location")


class Station(BaseStation):
    """
    Station model for the 'station' table in the 'air_quality_dim_station' schema.
    """

    __tablename__ = "station"

    id_station = Column(
        Integer,
        primary_key=True,
        # NOTE: look at next NOTE ⬇️
        # ForeignKey(f"{SCHEMA_NAME}.sensor.id_sensor"),
        autoincrement=False,
    )
    station_name = Column(String(255), nullable=False)
    id_location = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.location.id_location"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("station_name", "id_location", name="uq_station_location"),
        CheckConstraint(
            "TRIM(station_name) != ''", name="check_station_name_not_empty"
        ),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"station_name": "asc", "id_location": "asc"}

    location = relationship("Location")

    # NOTE: Due to the external data sources,
    # For now we assume that the relations to the sensor table are not certain
    # sensors = relationship("Sensor", back_populates="station")
