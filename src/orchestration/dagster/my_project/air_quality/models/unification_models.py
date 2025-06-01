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
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base

SCHEMA_NAME = "air_quality_dim_integrated"
metadata_station = MetaData(schema=SCHEMA_NAME)
BaseIntegrated = declarative_base(metadata=metadata_station)


# Define SQLAlchemy models matching the PostgreSQL tables
class Province(BaseIntegrated):
    """
    Province model for the 'province' table in the 'air_quality_dim_integrated' schema.
    """

    __tablename__ = "province"

    id_province = Column(Integer, primary_key=True, autoincrement=True)
    province = Column(String(255), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("TRIM(province) != ''", name="check_province_not_empty"),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"province": "asc"}


class Indicator(BaseIntegrated):
    """
    Indicator model for the 'indicator' table in the 'air_quality_dim_integrated' schema.
    """

    __tablename__ = "indicator"
    __table_args__ = (
        UniqueConstraint("formula", "name", name="uq_indicator_formula_name"),
        CheckConstraint("TRIM(formula) != ''", name="check_formula_not_empty"),
        CheckConstraint("TRIM(name) != ''", name="check_name_not_empty"),
        CheckConstraint("TRIM(description) != ''", name="check_description_not_empty"),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"formula": "asc"}

    # Columns
    id_indicator = Column(Integer, primary_key=True, autoincrement=False)

    formula = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=False, unique=True)


# NOTE: air_quality_dim_pollutant.pollutant model
# Added the id_indicator as fkey from air_quality_dim_annual_statistics.indicator
