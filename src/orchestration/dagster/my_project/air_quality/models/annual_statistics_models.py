"""
Defines SQLAlchemy models for the 'air quality annual statistics' data,
including Province, ZoneType, Zone, Station, Indicator, TimeAveraging, and Measurement.

It also includes a custom Query class for applying default ordering to queries.

Based on the provided database schema and data columns.
"""

# SQLAlchemy imports
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

SCHEMA_NAME = "air_quality_dim_annual_statistics"
metadata_statistics = MetaData(schema=SCHEMA_NAME)
BaseStatistics = declarative_base(metadata=metadata_statistics)


# Define SQLAlchemy models matching the PostgreSQL tables
class Province(BaseStatistics):
    """
    Province model for the 'województwa' table.
    """

    __tablename__ = "province"
    __table_args__ = (
        CheckConstraint("TRIM(province) != ''", name="check_province_not_empty"),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"province": "asc"}

    id_province = Column(Integer, primary_key=True, autoincrement=True)
    province = Column(String(255), nullable=False, unique=True)

    zones = relationship("Zone", back_populates="province")


class ZoneType(BaseStatistics):
    """
    ZoneType model for the 'zone_type' table.
    """

    __tablename__ = "zone_type"
    __table_args__ = (
        CheckConstraint("TRIM(zone_type) != ''", name="check_zone_type_not_empty"),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"zone_type": "asc"}

    id_zone_type = Column(Integer, primary_key=True, autoincrement=True)
    zone_type = Column(String(255), nullable=False, unique=True)

    zones = relationship("Zone", back_populates="zone_type")


class Zone(BaseStatistics):
    """
    Zone model for the 'strefy' table.
    """

    __tablename__ = "zone"
    __table_args__ = (
        UniqueConstraint(
            "zone_code",
            "zone_name",
            "id_zone_type",
            "id_province",
            name="uq_zone_type_name_province",
        ),
        CheckConstraint("TRIM(zone_code) != ''", name="check_zone_code_not_empty"),
        CheckConstraint("TRIM(zone_name) != ''", name="check_zone_name_not_empty"),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"zone_name": "asc"}

    id_zone = Column(Integer, primary_key=True, autoincrement=True)
    zone_code = Column(String(255), nullable=False, unique=True)
    zone_name = Column(String(255), nullable=False)
    id_zone_type = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.zone_type.id_zone_type"),
        nullable=False,
    )
    id_province = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.province.id_province"),
        nullable=False,
    )

    # Relationships
    province = relationship("Province", back_populates="zones")
    zone_type = relationship("ZoneType", back_populates="zones")
    stations = relationship("Station", back_populates="zone")


class Station(BaseStatistics):
    """
    Station model for the 'stacje' table.
    """

    __tablename__ = "station"
    __table_args__ = (
        UniqueConstraint("station_code", "id_zone", name="uq_station_code_zone"),
        CheckConstraint(
            "TRIM(station_code) != ''", name="check_station_code_not_empty"
        ),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"station_code": "asc"}

    id_station = Column(Integer, primary_key=True, autoincrement=True)

    station_code = Column(
        String(255), nullable=False
    )  # For some unknown reason, the codes are not unique, maybe due to:
    # - station relocations
    # - station upgrades or replacements
    # - administrative changes
    # - seasonal stations
    # - legacy stations and code reuse
    # - just good old fashioned data entry errors

    id_zone = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.zone.id_zone"),
        nullable=False,
    )

    # Relationships
    zone = relationship("Zone", back_populates="stations")
    measurements = relationship("Measurement", back_populates="station")


class Indicator(BaseStatistics):
    """
    Indicator model for the 'wskaźniki' table.
    """

    __tablename__ = "indicator"
    __table_args__ = (
        CheckConstraint("TRIM(name) != ''", name="check_name_not_empty"),
        CheckConstraint(
            "TRIM(description) != ''",
            name="check_description_not_empty",
        ),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"name": "asc"}

    id_indicator = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=False, unique=True)

    # Relationships
    measurements = relationship("Measurement", back_populates="indicator")


class TimeAveraging(BaseStatistics):
    """
    TimeAveraging model for the 'czas_usrednienia' table.
    """

    __tablename__ = "time_averaging"
    __table_args__ = (
        UniqueConstraint(
            "time_averaging", "minutes", "hours", "days", name="uq_time_averaging"
        ),
        CheckConstraint(
            "TRIM(time_averaging) != ''", name="check_time_averaging_not_empty"
        ),
        CheckConstraint(
            (
                "minutes IS NOT NULL "
                "OR minutes > 0 "
                "OR hours IS NOT NULL "
                "OR hours >= 0 "
                "OR days IS NOT NULL "
                "OR days >= 0 "
            )
        ),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"time_averaging": "asc"}

    id_time_averaging = Column(Integer, primary_key=True, autoincrement=True)
    time_averaging = Column(String(255), nullable=False, unique=True)
    minutes = Column(Integer, nullable=True, unique=True)
    hours = Column(Float, nullable=True, unique=True)
    days = Column(Float, nullable=True, unique=True)

    # Relationships
    measurements = relationship("Measurement", back_populates="time_averaging")


class Measurement(BaseStatistics):
    """
    Measurement model for the 'pomiary' table.
    """

    __tablename__ = "measurement"
    __table_args__ = (
        UniqueConstraint(
            "year",
            "id_station",
            "id_indicator",
            "id_time_averaging",
            name="uq_measurement_key",
        ),
        CheckConstraint(
            "number_of_measurements >= 0", name="check_number_of_measurements_natural"
        ),
        CheckConstraint(
            "valid_measurements_count >= 0",
            name="check_valid_measurements_count_natural",
        ),
        CheckConstraint(
            "s1_exceedances_200 >= 0", name="check_s1_exceedances_200_natural"
        ),
        CheckConstraint(
            "s1_exceedances_350 >= 0", name="check_s1_exceedances_350_natural"
        ),
        CheckConstraint(
            "s24_exceedances_50 >= 0", name="check_s24_exceedances_50_natural"
        ),
        CheckConstraint(
            "s24_exceedances_125 >= 0", name="check_s24_exceedances_125_natural"
        ),
        CheckConstraint(
            "s8max_days_above_120 >= 0", name="check_s8max_days_above_120_natural"
        ),
        CheckConstraint(
            "summer_complete_months_count_april_september >= 0",
            name="check_summer_complete_months_count_april_september_natural",
        ),
        CheckConstraint(
            '"winter_completeness_%" BETWEEN 0 AND 100',
            name="check_winter_completeness_%_range",
        ),
        CheckConstraint(
            '"summer_completeness_%" BETWEEN 0 AND 100',
            name="check_summer_completeness_%_range",
        ),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"year": "asc"}

    # Identifiers and metadata
    id_measurement = Column(
        BigInteger, primary_key=True, autoincrement=False
    )  # id provided by the database
    year = Column(Integer, nullable=False)
    id_station = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.station.id_station"),
        nullable=False,
    )
    id_indicator = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.indicator.id_indicator"),
        nullable=False,
    )

    # Time averaging information
    id_time_averaging = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.time_averaging.id_time_averaging"),
        nullable=False,
    )

    # Measurement counts and completeness
    number_of_measurements = Column(Integer)
    valid_measurements_count = Column(Integer)
    completeness_percent = Column(Float, nullable=False, name="completeness_%")

    # General measurement statistics (averages, minimums, maximums)

    # µg m3
    avg_µg_m3 = Column(Float)
    min_µg_m3 = Column(Float)
    max_µg_m3 = Column(Float)

    # mg m3
    avg_mg_m3 = Column(Float)
    min_mg_m3 = Column(Float)
    max_mg_m3 = Column(Float)

    # µg m2 day
    avg_µg_m2_day = Column(Float)
    min_µg_m2_day = Column(Float)
    max_µg_m2_day = Column(Float)

    # ng m3
    avg_ng_m3 = Column(Float)
    min_ng_m3 = Column(Float)
    max_ng_m3 = Column(Float)

    # Exceedances and percentiles for s1
    s1_exceedances_200 = Column(Integer)
    s1_exceedances_350 = Column(Integer)
    s1_19th_max_µg_m3 = Column(Float)
    s1_25th_max_µg_m3 = Column(Float)
    s1_percentile_99_7_µg_m3 = Column(Float)
    s1_percentile_99_8_µg_m3 = Column(Float)

    # Exceedances and percentiles for s24
    s24_exceedances_50 = Column(Integer)
    s24_exceedances_125 = Column(Integer)
    s24_4th_max_µg_m3 = Column(Float)
    s24_36th_max_µg_m3 = Column(Float)
    s24_max_µg_m3 = Column(Float)
    s24_percentile_90_4_µg_m3 = Column(Float)
    s24_percentile_99_2_µg_m3 = Column(Float)

    # Exceedances and percentiles for s8max
    s8max_max_mg_m3 = Column(Float)
    s8max_max_26th_µg_m3 = Column(Float)
    s8max_percentile_93_2_µg_m3 = Column(Float)
    s8max_days_above_120 = Column(Integer)

    # Seasonal averages and completeness
    winter_avg_µg_m3 = Column(Float)

    # NOTE: Yes, they are whole numbers
    winter_completeness_percent = Column(Integer, name="winter_completeness_%")
    summer_completeness_percent = Column(Integer, name="summer_completeness_%")

    summer_complete_months_count_april_september = Column(Integer)
    summer_winter_count = Column(Float)
    summer_winter = Column(Float)

    # Other measurements and indices
    aot40_may_july_µg_m3_h = Column(Float)
    somo35_µg_m3_d = Column(Float)

    # Relationships
    station = relationship("Station", back_populates="measurements")
    indicator = relationship("Indicator", back_populates="measurements")
    time_averaging = relationship("TimeAveraging", back_populates="measurements")
