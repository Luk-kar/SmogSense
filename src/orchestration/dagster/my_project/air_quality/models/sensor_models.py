# SQLAlchemy imports
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


SCHEMA_NAME = "air_quality_dim_sensor"
metadata_sensor = MetaData(schema=SCHEMA_NAME)
BaseSensor = declarative_base(metadata=metadata_sensor)


class Indicator(BaseSensor):
    """
    Indicator model for the 'indicator' table in the 'air_quality_dim_sensor' schema.
    """

    __tablename__ = "indicator"
    __table_args__ = (
        UniqueConstraint(
            "id_indicator", "name", "code", name="uq_indicator_id_name_code"
        ),
        CheckConstraint("TRIM(name) != ''", name="check_name_not_empty"),
        CheckConstraint("TRIM(formula) != ''", name="check_formula_not_empty"),
        CheckConstraint("TRIM(code) != ''", name="check_code_not_empty"),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"name": "asc"}

    # Columns
    id_indicator = Column(Integer, primary_key=True, autoincrement=False)

    # NOTE: The name and formula have been for now the same
    # but due to the external data sources, we need to keep both if they differ
    # with a new data

    name = Column(String(255), nullable=False, unique=True)
    formula = Column(String(255), nullable=False)

    code = Column(String(255), nullable=False, unique=True)

    # Relationships
    sensors = relationship("Sensor", back_populates="indicator")


class Sensor(BaseSensor):
    """
    Sensor model for the 'sensor' table in the 'air_quality_dim_sensor' schema.
    """

    __tablename__ = "sensor"
    __table_args__ = (
        UniqueConstraint(
            "id_sensor",
            "id_station",
            "id_indicator",
            name="uq_sensor_station_indicator",
        ),
        {"schema": SCHEMA_NAME},
    )
    __default_order_by__ = {"id_station": "asc", "id_indicator": "asc"}

    # Columns
    id_sensor = Column(Integer, primary_key=True, autoincrement=False)
    id_station = Column(
        Integer,
        # NOTE: The `id_station` column ideally references
        # `air_quality_dim_station.station.id_station` to establish a foreign key relationship.
        # However, issues with the current dataset—specifically,
        # `id_station` values in `sensor` lacking corresponding entries in `station`,
        # prevent the foreign key constraint from being applied.
        nullable=False,
    )
    id_indicator = Column(
        Integer,
        ForeignKey(f"{SCHEMA_NAME}.indicator.id_indicator"),
        nullable=False,
    )

    # Relationships
    indicator = relationship("Indicator", back_populates="sensors")
