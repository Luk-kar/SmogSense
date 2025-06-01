"""
This module defines the ORM models for pollutants, measurements, and geometry data.
These models integrate with SQLAlchemy and reflect the relationships defined in the provided DBML schema.
"""

# SQLAlchemy
from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Float,
    Integer,
    Index,
    MetaData,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Third-party
# For handling geometry columns (PostGIS)
from geoalchemy2 import Geometry

# Define schema and metadata
SCHEMA_NAME = "air_quality_dim_map_pollutant"
metadata_map = MetaData(schema=SCHEMA_NAME)
BaseMap = declarative_base(metadata=metadata_map)


class Pollutant(BaseMap):
    """
    Pollutant model for the 'pollutant' table.
    Represents a type of pollutant with a given name and associated indicator.
    """

    __tablename__ = "pollutant"

    id_pollutant = Column(Integer, primary_key=True, autoincrement=True)
    pollutant_name = Column(String(255), nullable=False, unique=True)
    indicator_type = Column(String(255), nullable=False)

    measurements = relationship("Measurement", back_populates="pollutant")


class Measurement(BaseMap):
    """
    Measurement model for the 'measurement' table.
    Stores measurement data for a given pollutant, including the year and publication date.
    """

    __tablename__ = "measurement"

    id_measurement = Column(Integer, primary_key=True, autoincrement=True)
    id_pollutant = Column(
        Integer, ForeignKey(f"{SCHEMA_NAME}.pollutant.id_pollutant"), nullable=False
    )
    data_year = Column(Integer, nullable=False)
    date_published = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("id_pollutant", "data_year", name="unique_pollutant_year"),
        {"schema": SCHEMA_NAME},
    )

    pollutant = relationship("Pollutant", back_populates="measurements")
    geometry_records = relationship("GeometryRecord", back_populates="measurements")


class GeometryRecord(BaseMap):
    """
    GeometryRecord model for the 'geometry' table.
    Stores spatial geometry data associated with a measurement and a particular value.
    """

    __tablename__ = "geometry"

    id_geometry = Column(Integer, primary_key=True, autoincrement=True)
    id_measurement = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.measurement.id_measurement"),
        nullable=False,
    )
    geometry = Column(
        Geometry("GEOMETRY", srid=4326), nullable=False
    )  # Adjust SRID if needed
    value = Column(Float, nullable=False)

    __table_args__ = (
        Index(
            "unique_measurement_geometry",
            "id_measurement",
            func.md5(func.ST_AsText(geometry)),
            "value",
            unique=True,
        ),
        Index("idx_geometry_gist", geometry, postgresql_using="gist"),
        {"schema": SCHEMA_NAME},
    )

    measurements = relationship("Measurement", back_populates="geometry_records")
