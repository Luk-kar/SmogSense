"""
This asset:
- Fetches indicator data from `air_quality_dim_annual_statistics.indicator` and `air_quality_dim_sensor.indicator`.
- Preserves id_indicator, formula, and name from the sensor schema where possible.
- Augments these with descriptions from the annual_statistics schema.
- Adds new indicators (found only in annual_statistics) by assigning new id_indicators and creating a consistent formula and name.
- Inserts the unified data into `air_quality_dim_integrated.indicator`.
"""

# Dagster
from dagster import asset, OpExecutionContext

# Third-party
import pandas as pd
import numpy as np

# SQLAlchemy
from sqlalchemy import text, UniqueConstraint
from sqlalchemy.orm import Session

# Pipelines
from air_quality.models.annual_statistics_models import (
    Indicator as AnnualStatisticsIndicator,
    Measurement as AnnualStatisticsMeasurement,
)

from air_quality.models.sensor_models import (
    Indicator as SensorIndicator,
    Sensor,
)
from air_quality.models.unification_models import (
    Indicator as IntegratedIndicator,
)
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    UnificationGroups,
)
from common.utils.database.session_handling import (
    get_database_session,
)
from common.utils.database.schema_operations import (
    get_table_name,
)
from common.utils.database.data_ingestion import upload_data_and_log_materialization
from common.utils.logging import log_dataframe_info, log_dataframe


@asset(
    group_name=UnificationGroups.DATABASE_UNIFICATION,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        "upload_data_sensor_indicator",
        "upload_data_indicator",
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_UNIFICATION,
        )
    },
)
def create_table_unified_indicator(context: OpExecutionContext) -> pd.DataFrame:
    """
    Fetches indicator data from `sensor` and `annual_statistics` schemas.
    """

    with get_database_session(context) as session:

        df_combined = _fetch_sensor_and_annual_data(context, session)

        log_dataframe(context, "➡️ Rendering the unified indicator data...", df_combined)

        df_sanitized = _sanitize_indicator_dataframe(df_combined)

        log_dataframe(
            context, "➡️ Rendering the sanitized unified indicator data...", df_sanitized
        )

        df_with_common_ids = _assign_common_ids(df_sanitized)
        log_dataframe(
            context,
            "➡️ Rendering the unified indicator data with common IDs...",
            df_with_common_ids[
                [
                    "sensor_id_indicator",
                    "annual_id_indicator",
                    "common_id_indicator",
                    "formula",
                ]
            ],
        )

        integrated_df = _finalize_integrated_df(context, df_with_common_ids)
        log_dataframe(
            context,
            "➡️ Rendering integrated indicator data with missing names filled...",
            integrated_df,
        )

        context.log.info("➡️ Uploading integrated indicator data to the database...")

        df_mapping_annual_id_indicator = _prepare_indicator_keys_map(df_sanitized)

        upload_data_and_log_materialization(
            context=context,
            data_frame=integrated_df,
            model_class=IntegratedIndicator,
            asset_key_str="create_table_unified_indicator",
            description="Integrated indicator data from `annual_statistics` and `sensor` schemas.",
        )

    return df_mapping_annual_id_indicator


def _prepare_indicator_keys_map(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares a DataFrame with the mapping between annual_id_indicator and common_id_indicator.
    """

    return df[["annual_id_indicator", "common_id_indicator", "formula"]].rename(
        columns={"common_id_indicator": "replacement_id_indicator"}
    )


def _finalize_integrated_df(
    context: OpExecutionContext, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Creates the integrated DataFrame (id_indicator, formula, name, description),
    fills missing names based on a known mapping, and returns the final DF.
    """

    integrated_df = df[["common_id_indicator", "formula", "name", "description"]]

    integrated_df = integrated_df.rename(
        columns={"common_id_indicator": "id_indicator"}
    )

    context.log.info("➡️ Rendering integrated indicator data...")
    context.log.info(f"\n{integrated_df.to_markdown(index=False)}")

    null_formulas = tuple(integrated_df[integrated_df["name"].isnull()]["formula"])

    missing_names_mapping = {
        "BjF(dust_deposition)": "benzo[j]fluoranthene (dust deposition)",
        "K+(PM2.5)": "potassium (PM2.5)",
        "BaP(PM10)": "benzo[a]pyrene (PM10)",
        "Cd(dust_deposition)": "cadmium (dust deposition)",
        "OC(PM2.5)": "organic carbon (PM2.5)",
        "As(PM10)": "arsenic (PM10)",
        "Cd(PM10)": "cadmium (PM10)",
        "SO42_(PM2.5)": "sulfate (PM2.5)",
        "IP(PM10)": "indeno[1,2,3-cd]pyrene (PM10)",
        "NH4+(PM2.5)": "ammonium (PM2.5)",
        "BaA(dust_deposition)": "benzo[a]anthracene (dust deposition)",
        "BkF(dust_deposition)": "benzo[k]fluoranthene (dust deposition)",
        "BaA(PM10)": "benzo[a]anthracene (PM10)",
        "Hg(TGM)": "mercury (total gaseous mercury)",
        "DBahA(dust_deposition)": "dibenz[a,h]anthracene (dust deposition)",
        "Ca2+(PM2.5)": "calcium (PM2.5)",
        "BaP(dust_deposition)": "benzo[a]pyrene (dust deposition)",
        "NOx": "nitrogen oxides",
        "Cl_(PM2.5)": "chloride (PM2.5)",
        "EC(PM2.5)": "elemental carbon (PM2.5)",
        "formaldehyde": "formaldehyde",
        "NO3_(PM2.5)": "nitrate (PM2.5)",
        "Ni(dust_deposition)": "nickel (dust deposition)",
        "IP(dust_deposition)": "indeno[1,2,3-cd]pyrene (dust deposition)",
        "BbF(dust_deposition)": "benzo[b]fluoranthene (dust deposition)",
        "BjF(PM10)": "benzo[j]fluoranthene (PM10)",
        "DBahA(PM10)": "dibenz[a,h]anthracene (PM10)",
        "As(dust_deposition)": "arsenic (dust deposition)",
        "Hg(dust_deposition)": "mercury (dust deposition)",
        "Na+(PM2.5)": "sodium (PM2.5)",
        "Ni(PM10)": "nickel (PM10)",
        "BkF(PM10)": "benzo[k]fluoranthene (PM10)",
        "BbF(PM10)": "benzo[b]fluoranthene (PM10)",
        "Pb(PM10)": "lead (PM10)",
        "Mg2+(PM2.5)": "magnesium (PM2.5)",
    }

    if set(null_formulas) != set(missing_names_mapping.keys()):
        raise ValueError(
            (
                "❌ Formulas with missing names do not match the expected keys.\n"
                "Differences:\n"
                f"{set(null_formulas) ^ set(missing_names_mapping.keys())}"
            )
        )

    integrated_df["name"] = integrated_df["name"].fillna(
        integrated_df["formula"].map(missing_names_mapping)
    )

    return integrated_df


def _assign_common_ids(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Uses existing sensor_id_indicator where possible;
    for rows without sensor_id_indicator, assigns new integer IDs incrementally.
    """

    data_frame["common_id_indicator"] = data_frame["sensor_id_indicator"]

    # Generate a set of existing sensor IDs
    existing_sensor_ids = set(data_frame["sensor_id_indicator"].dropna().astype(int))

    # Generate new IDs to fill gaps
    next_available_id = 1
    generated_ids = []
    for id_candidate in range(
        1, len(data_frame) + 1
    ):  # Start from 1 up to the length of the DataFrame
        if next_available_id not in existing_sensor_ids:
            generated_ids.append(next_available_id)
        existing_sensor_ids.add(next_available_id)
        next_available_id += 1

    # Fill gaps in common_id_indicator
    generated_id_index = 0
    for index, row in data_frame.iterrows():
        if pd.isna(row["sensor_id_indicator"]):
            data_frame.at[index, "common_id_indicator"] = generated_ids[
                generated_id_index
            ]
            generated_id_index += 1

    # Convert common_id_indicator back to integers
    data_frame["common_id_indicator"] = data_frame["common_id_indicator"].astype(int)

    return data_frame


def _sanitize_indicator_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renames relevant columns for clarity and extracts a subset of relevant columns.
    Returns a DataFrame with standardized columns.
    """

    df = df.rename(
        columns={
            "sensor_id_indicator": "sensor_id_indicator",
            "annual_id_indicator": "annual_id_indicator",
            "sensor_name": "name",
            "annual_name": "formula",
            "annual_description": "description",
        }
    )

    # Select only the relevant columns for display
    df = df[
        [
            "sensor_id_indicator",
            "annual_id_indicator",
            "name",
            "formula",
            "description",
        ]
    ]

    df["sensor_id_indicator"] = df["sensor_id_indicator"].replace({np.nan: None})

    return df


def _fetch_sensor_and_annual_data(
    context: OpExecutionContext, session: Session
) -> pd.DataFrame:
    """
    Fetches data from SensorIndicator and AnnualStatisticsIndicator.
    Joins on matching formulas (sensor.formula == annual_stats.name).
    Returns a raw DataFrame containing both sets of data.
    """

    context.log.info(
        "➡️ Fetching `indicator` data from `annual_statistics` and `sensor` schemas..."
    )

    unified_data = (
        session.query(
            SensorIndicator.id_indicator.label("sensor_id_indicator"),
            SensorIndicator.name.label("sensor_name"),
            SensorIndicator.formula.label("sensor_formula"),
            AnnualStatisticsIndicator.id_indicator.label("annual_id_indicator"),
            AnnualStatisticsIndicator.name.label("annual_name"),
            AnnualStatisticsIndicator.description.label("annual_description"),
        )
        .join(
            AnnualStatisticsIndicator,
            SensorIndicator.formula == AnnualStatisticsIndicator.name,
            full=True,
        )
        .all()
    )

    data = [
        {
            "sensor_id_indicator": row.sensor_id_indicator,
            "sensor_name": row.sensor_name,
            "sensor_formula": row.sensor_formula,
            "annual_id_indicator": row.annual_id_indicator,
            "annual_name": row.annual_name,
            "annual_description": row.annual_description,
        }
        for row in unified_data
    ]

    # Create DataFrame
    df = pd.DataFrame(data)
    return df


@asset(
    group_name=UnificationGroups.DATABASE_UNIFICATION,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        "upload_data_measurement",
        "upload_data_sensor",
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_UNIFICATION,
        )
    },
)
def add_foreign_keys_unified_indicator(
    context: OpExecutionContext, create_table_unified_indicator: pd.DataFrame
) -> None:
    """
    Adds foreign key constraints to the `annual_statistics_measurement` and `sensor` tables.
    """

    keys_to_update = create_table_unified_indicator

    log_dataframe_info(context, keys_to_update, "Keys to update")

    with get_database_session(context) as session:

        unification_indicator_table = get_table_name(IntegratedIndicator)

        update_measurement_constraints(
            context, keys_to_update, session, unification_indicator_table
        )

        update_sensor_constraints(context, session, unification_indicator_table)


def update_measurement_constraints(
    context: OpExecutionContext,
    keys_to_update: pd.DataFrame,
    session: Session,
    unification_indicator_table: str,
):
    """
    Updates the foreign key constraints for the `id_indicator`
    column in the `annual_statistics_measurement` table.
    """

    measurement_table = get_table_name(AnnualStatisticsMeasurement)

    measurement_id_indicator_fkey = "measurement_id_indicator_fkey"
    measurement_unique_constrain_name = "uq_measurement_key"

    _validate_unique_constraint(
        context, measurement_table, measurement_unique_constrain_name
    )

    _drop_existing_constraints(
        context,
        session,
        measurement_table,
        [measurement_id_indicator_fkey, measurement_unique_constrain_name],
    )

    _update_id_indicator(context, session, measurement_table, keys_to_update)

    tables = {
        "target_table": measurement_table,
        "reference_table": unification_indicator_table,
    }

    constrains = {
        "fkey_name": measurement_id_indicator_fkey,
        "unique_constrain": {
            "name": measurement_unique_constrain_name,
            "columns": [
                "year",
                "id_station",
                "id_indicator",
                "id_time_averaging",
            ],
        },
    }

    _add_constraints(context, session, tables, constrains)


def _validate_unique_constraint(
    context: OpExecutionContext, measurement_table: str, constraint_name: str
):
    """
    Validates the existence of a unique constraint in the ORM model.
    """
    measurement_unique_constraints = [
        constraint
        for constraint in AnnualStatisticsMeasurement.__table_args__
        if isinstance(constraint, UniqueConstraint)
        and constraint.name == constraint_name
    ]

    if not measurement_unique_constraints:
        raise ValueError(
            (
                f"❌ Unique constraint `{constraint_name}` not found in"
                f"`{measurement_table}` table definition."
            )
        )

    context.log.info(
        f"✅ Validated unique constraint `{constraint_name}` exists in `{measurement_table}`."
    )


def _drop_existing_constraints(
    context: OpExecutionContext,
    session: Session,
    measurement_table: str,
    constraints: list,
):
    """
    Drops the specified constraints from the measurement table.
    """
    try:
        for constraint in constraints:
            drop_constraint(context, session, measurement_table, constraint)

        session.commit()
        context.log.info(
            f"✅ Dropped constraints `{constraints}` from `{measurement_table}`."
        )
    except Exception as e:
        session.rollback()
        context.log.error("❌ Error during DROP constraints. Rolling back...")
        raise e


def _update_id_indicator(
    context: OpExecutionContext,
    session: Session,
    measurement_table: str,
    keys_to_update: pd.DataFrame,
):
    """
    Updates the `id_indicator` column in the measurement table using the provided mapping.
    """
    try:
        context.log.info(
            (
                f"➡️ Updating `id_indicator` in `{measurement_table}` based on"
                "the `keys_to_update` mapping..."
            )
        )

        case_statement = " ".join(
            [
                f"WHEN id_indicator = {annual_id_indicator} THEN {replacement_id_indicator}"
                for annual_id_indicator, replacement_id_indicator in zip(
                    keys_to_update["annual_id_indicator"],
                    keys_to_update["replacement_id_indicator"],
                )
            ]
        )

        unique_annual_ids = ", ".join(
            map(str, keys_to_update["annual_id_indicator"].unique())
        )

        update_query = text(
            f"""
            UPDATE {measurement_table}
            SET id_indicator = CASE {case_statement} ELSE id_indicator END
            WHERE id_indicator IN ({unique_annual_ids});
            """
        )

        session.execute(update_query)
        session.commit()
        context.log.info(
            f"✅ `id_indicator` successfully updated in `{measurement_table}`."
        )

    except Exception as e:
        session.rollback()
        context.log.error("❌ Error occurred during UPDATEs. Rolling back...")
        raise e


def _add_constraints(
    context: OpExecutionContext,
    session: Session,
    tables: dict,
    constrains: dict,
):
    """
    Adds foreign key and unique constraints to the measurement table.
    """

    try:

        constraint_fkey = {
            "name": constrains["fkey_name"],
            "table_column": "id_indicator",
            "reference_column": "id_indicator",
        }

        add_foreign_key(context, session, tables, constraint_fkey)

        constraint_unique_names = {
            "name": constrains["unique_constrain"]["name"],
            "columns": constrains["unique_constrain"]["columns"],
        }

        add_unique_constraint(
            context,
            session,
            tables["target_table"],
            constraint_unique_names,
        )

        session.commit()
        context.log.info(
            f"✅ All constraints successfully added to `{tables['target_table']}`."
        )
    except Exception as e:
        session.rollback()
        context.log.error(
            f"❌ Error during ADD constraints for `{tables['target_table']}`. Rolling back..."
        )
        raise e


def update_sensor_constraints(
    context: OpExecutionContext, session: Session, unification_indicator_table: str
):
    """
    Updates the foreign key constraints for the `id_indicator` column in the `sensor` table.
    """

    sensor_table = get_table_name(Sensor)

    sensor_id_indicator_fkey = "sensor_id_indicator_fkey"

    try:
        drop_constraint(context, session, sensor_table, sensor_id_indicator_fkey)

        tables = {
            "target_table": sensor_table,
            "reference_table": unification_indicator_table,
        }

        constraint_fkey = {
            "name": sensor_id_indicator_fkey,
            "table_column": "id_indicator",
            "reference_column": "id_indicator",
        }

        add_foreign_key(context, session, tables, constraint_fkey)

        session.commit()
        context.log.info(
            f"✅ All constraints successfully updated for `{sensor_table}`."
        )

    except Exception as e:
        session.rollback()
        context.log.error(
            f"❌ Error during UPDATE constraints for `{sensor_table}`. Rolling back..."
        )
        raise e


def drop_constraint(
    context: OpExecutionContext, session: Session, table_name: str, constraint_name: str
) -> None:
    """
    Drops a specified constraint from the given table.
    """
    context.log.info(
        f"➡️ Dropping constraint `{constraint_name}` in `{table_name}` table..."
    )
    session.execute(
        text(
            f"""
            ALTER TABLE {table_name}
            DROP CONSTRAINT IF EXISTS {constraint_name};
            """
        )
    )


def add_foreign_key(
    context: OpExecutionContext,
    session: Session,
    tables: dict,
    constraint_fkey: dict,
) -> None:
    """
    Adds a foreign key constraint to the given table.
    """

    context.log.info(
        f"➡️ Adding foreign key `{constraint_fkey['name']}` in `{tables['target_table']}` table..."
    )
    session.execute(
        text(
            f"""
            ALTER TABLE {tables["target_table"]}
            ADD CONSTRAINT {constraint_fkey["name"]}
            FOREIGN KEY ({constraint_fkey["table_column"]})
            REFERENCES {tables["reference_table"]}({constraint_fkey["reference_column"]});
            """
        )
    )


def add_unique_constraint(
    context: OpExecutionContext, session: Session, table_name: str, constraint: dict
) -> None:
    """
    Adds a unique constraint to the given table on the specified columns.
    """

    context.log.info(
        f"➡️ Adding unique constraint `{constraint['name']}` in `{table_name}` table..."
    )
    session.execute(
        text(
            f"""
            ALTER TABLE {table_name}
            ADD CONSTRAINT {constraint['name']}
            UNIQUE ({", ".join(constraint["columns"])});
            """
        )
    )


@asset(
    group_name=UnificationGroups.DATABASE_UNIFICATION,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        "add_foreign_keys_unified_indicator",
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_UNIFICATION,
        )
    },
)
def drop_duplicated_tables_indicator(context: OpExecutionContext) -> None:
    """
    Drops the redundant `indicator` tables from the `sensor` and `annual_statistics` schemas.
    """

    with get_database_session(context) as session:

        context.log.info(
            (
                "➡️ Dropping redundant `indicator` tables from `sensor`"
                "and `annual_statistics` schemas..."
            )
        )

        sensor_indicator_table = get_table_name(SensorIndicator)
        annual_statistics_indicator_table = get_table_name(AnnualStatisticsIndicator)

        session.execute(text(f"DROP TABLE IF EXISTS {sensor_indicator_table} CASCADE;"))

        session.execute(
            text(f"DROP TABLE IF EXISTS {annual_statistics_indicator_table} CASCADE;")
        )

        session.commit()

        context.log.info(
            "✅ Redundant `indicator` tables have been successfully dropped!"
        )
