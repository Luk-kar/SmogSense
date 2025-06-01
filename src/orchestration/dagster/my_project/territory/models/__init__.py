"""
This module defines SQLAlchemy models for the 'air quality_integrated' data.
It integrate common data from the 'air_quality_dim_station' and 
'air_quality_dim_annual_statistics' schemas.
"""

# SQLAlchemy
from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    MetaData,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

# Third-party
# For handling geometry columns (PostGIS)
from geoalchemy2 import Geometry


SCHEMA_NAME = "territory_dim"
metadata_station = MetaData(schema=SCHEMA_NAME)
BaseIntegrated = declarative_base(metadata=metadata_station)


class Province(BaseIntegrated):
    """
    Province model for the 'province' table in the 'territory_dim' schema.
    """

    __tablename__ = "province"

    id_province = Column(Integer, primary_key=True, autoincrement=True)
    province = Column(String(255), nullable=False, unique=True)
    coordinates = Column(Geometry("GEOMETRY", srid=4326), nullable=False)
    __table_args__ = (
        CheckConstraint("TRIM(province) != ''", name="check_province_not_empty"),
        {"schema": SCHEMA_NAME},
    )
