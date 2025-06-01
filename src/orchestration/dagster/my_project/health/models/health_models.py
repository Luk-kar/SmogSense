"""
This module defines SQLAlchemy models for the 'health_data' tables, including:
1) provinces
2) death_illness
3) measurement

Constraints enforced:
- province and illness are non-empty unique strings
- measurement has unique (id_illness, id_province, year)
- year > 0
- deaths > 0
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

SCHEMA_NAME = "health_dim"
metadata_health = MetaData(schema=SCHEMA_NAME)
BaseHealth = declarative_base(metadata=metadata_health)


class Province(BaseHealth):
    """
    Province model mapping the 'province' table in the 'health_data' schema.
    """

    __tablename__ = "province"

    id_province = Column(
        String(255), primary_key=True
    )  # Provided by external data source
    province = Column(String(255), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("TRIM(province) != ''", name="check_province_not_empty"),
        {"schema": SCHEMA_NAME},
    )

    measurements = relationship("Measurement", back_populates="province")
    province_population = relationship("ProvincePopulation", back_populates="province")


class DeathIllness(BaseHealth):
    """
    DeathIllness model mapping the 'death_illness' table in the 'health_data' schema.
    """

    __tablename__ = "death_illness"

    id_illness = Column(Integer, primary_key=True)  # Provided by external data source
    illness = Column(String(255), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("TRIM(illness) != ''", name="check_illness_not_empty"),
        {"schema": SCHEMA_NAME},
    )

    measurements = relationship("Measurement", back_populates="death_illness")


class Measurement(BaseHealth):
    """
    Measurement model mapping the 'measurement' table in the 'health_data' schema.
    """

    __tablename__ = "measurement"

    id_measurement = Column(Integer, primary_key=True, autoincrement=True)
    id_illness = Column(
        Integer, ForeignKey(f"{SCHEMA_NAME}.death_illness.id_illness"), nullable=False
    )
    id_province = Column(
        String(255), ForeignKey(f"{SCHEMA_NAME}.province.id_province"), nullable=False
    )
    year = Column(Integer, nullable=False)
    deaths = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "id_illness",
            "id_province",
            "year",
            name="uq_measurement_illness_province_year",
        ),
        CheckConstraint("year > 0", name="check_year_positive"),
        CheckConstraint("deaths >= 0", name="check_deaths_positive"),
        {"schema": SCHEMA_NAME},
    )

    death_illness = relationship("DeathIllness", back_populates="measurements")
    province = relationship("Province", back_populates="measurements")


class CountryPopulation(BaseHealth):
    """
    CountryPopulation model display total population data at the country level and year.
    """

    __tablename__ = "country_population"

    year = Column(Integer, primary_key=True)
    people_total = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("year > 0", name="check_year_positive"),
        CheckConstraint("people_total >= 0", name="check_population_positive"),
        {"schema": SCHEMA_NAME},
    )


class ProvincePopulation(BaseHealth):
    """
    ProvincePopulation model display total population data at the province level and year.
    """

    __tablename__ = "province_population"

    id_population = Column(Integer, primary_key=True, autoincrement=True)
    id_province = Column(
        String(255), ForeignKey(f"{SCHEMA_NAME}.province.id_province"), nullable=False
    )
    year = Column(Integer, nullable=False)
    people_total = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("id_province", "year", name="uq_province_population"),
        CheckConstraint("year > 0", name="check_year_positive"),
        CheckConstraint("people_total >= 0", name="check_population_positive"),
        {"schema": SCHEMA_NAME},
    )

    province = relationship("Province", back_populates="province_population")
