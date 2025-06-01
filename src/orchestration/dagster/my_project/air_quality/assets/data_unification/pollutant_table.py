"""
This module defines a Dagster asset for adding the id_indicator column to the map_pollutants table, 
including data retrieval, validation, column creation, and constraint application. 
It also contains helper functions for these operations.
"""

# Dagster
from dagster import asset, AssetExecutionContext

# Third-party
import pandas as pd

# SQLALchemy
from sqlalchemy import text
from sqlalchemy.orm import Session

# Pipelines
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    UnificationGroups,
)
from air_quality.models.unification_models import (
    Indicator as IntegratedIndicator,
)
from air_quality.models.map_pollution_models import (
    Pollutant as MapPollutant,
)
from common.utils.database.session_handling import (
    get_database_session,
)
from common.utils.logging import log_dataframe
from common.utils.database.schema_operations import get_table_name
from common.utils.logging import (
    log_asset_materialization,
)


@asset(
    group_name=UnificationGroups.DATABASE_UNIFICATION,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        "upload_data_map_pollutants",
        "create_table_unified_indicator",
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_UPDATE_CONSTRAINTS,
            Categories.DATABASE_UNIFICATION,
        )
    },
)
def map_pollutants_table_add_id_indicator_column(context: AssetExecutionContext):
    """
    Adds the id_indicator column to the map_pollutants table.
    """
    with get_database_session(context) as session:

        indicators_to_match, pollutants_to_match = retrieve_data(context, session)

        pollutant_mapping = validate_data(
            context, indicators_to_match, pollutants_to_match
        )

        context.log.info(
            "➡️ STEP 3: Preparing references to map_pollutants and integrated_indicator tables..."
        )

        map_pollutant_table: str = get_table_name(MapPollutant)
        integrated_indicator_table: str = get_table_name(IntegratedIndicator)

        foreign_key_column = "id_indicator"
        foreign_key_constraint = f"fk_{foreign_key_column}"
        unique_id_constraint = f"unique_{foreign_key_column}"

        tables = {
            "map_pollutant": map_pollutant_table,
            "integrated_indicator": integrated_indicator_table,
        }

        constraints = {
            "foreign_key": foreign_key_constraint,
            "foreign_key_column": foreign_key_column,
            "unique_id": unique_id_constraint,
        }

        try:
            create_and_populate_column(
                context,
                session,
                pollutant_mapping,
                tables,
                foreign_key_column,
            )

            apply_constraints(context, session, tables, constraints)

            session.commit()
            context.log.info("✅ All changes successfully committed to the database.")

        except Exception as e:
            session.rollback()
            context.log.error(f"❌ An error occurred: {str(e)}. Changes rolled back.")
            raise

        context.log.info(
            f"➡️ STEP 8: Querying up to 50 rows from {map_pollutant_table} to confirm changes..."
        )
        table_result_rows = session.execute(
            text(
                f"""
            SELECT *
            FROM {map_pollutant_table}
            LIMIT 50
            """
            )
        ).fetchall()

        query_data_for_validation(
            context, session, foreign_key_column, table_result_rows
        )

        log_asset_materialization(
            context=context,
            data_frame=pd.DataFrame(table_result_rows),
            asset_key="map_pollutants_table_add_id_indicator_column",
            description="Map pollutants table with id_indicator column added",
        )


def query_data_for_validation(
    context: AssetExecutionContext,
    session: Session,
    foreign_key_column: str,
    table_result_rows: list,
):
    """
    Query the database to validate the changes made to the map_pollutants table.
    """

    log_dataframe(
        context,
        f"Pollutant data after adding {foreign_key_column} column:",
        pd.DataFrame(
            table_result_rows,
            columns=[
                "id_pollutant",
                "pollutant_name",
                "indicator_type",
                f"{foreign_key_column}",
            ],
        ),
    )

    context.log.info("➡️ STEP 9: Checking the updated schema from the database...")
    schema_info = session.execute(
        text(
            f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = '{MapPollutant.__table__.schema}'
            AND table_name = '{MapPollutant.__tablename__}'
            """
        )
    ).fetchall()

    df_schema = pd.DataFrame(schema_info, columns=["column_name", "data_type"])

    log_dataframe(
        context,
        "Schema information:",
        pd.DataFrame(df_schema),
    )


def apply_constraints(
    context: AssetExecutionContext,
    session: Session,
    tables: dict,
    constraints: dict,
):
    """
    Apply constraints to the map_pollutants table.
    """

    context.log.info(
        f"➡️ STEP 5: Applying NOT NULL and UNIQUE constraints"
        f"on {constraints['foreign_key_column']}..."
    )

    session.execute(
        text(
            f"""
                    ALTER TABLE {tables["map_pollutant"]}
                    ALTER COLUMN {constraints["foreign_key_column"]} SET NOT NULL
                    """
        )
    )

    session.execute(
        text(
            f"""
                    ALTER TABLE {tables["map_pollutant"]}
                    ADD CONSTRAINT {constraints["unique_id"]} 
                    UNIQUE ({constraints["foreign_key_column"]})
                    """
        )
    )

    context.log.info(
        f"➡️ STEP 6: Adding foreign key constraint '{constraints['foreign_key']}'..."
    )
    session.execute(
        text(
            f"""
                ALTER TABLE {tables["map_pollutant"]}
                ADD CONSTRAINT {constraints["foreign_key"]}
                FOREIGN KEY ({constraints["foreign_key_column"]})
                REFERENCES {tables["integrated_indicator"]} ({constraints["foreign_key_column"]})
                """
        )
    )


def create_and_populate_column(
    context: AssetExecutionContext,
    session: Session,
    pollutant_mapping: dict,
    tables: dict,
    foreign_key_column: str,
):
    """
    Create and populate the id_indicator column in the map_pollutants table.
    """

    context.log.info(
        (
            f"➡️ STEP 4: Creating and populating the {foreign_key_column} column"
            f"in {tables['map_pollutant']}..."
        )
    )

    session.execute(
        text(
            f"""
                ALTER TABLE {tables["map_pollutant"]}
                ADD COLUMN {foreign_key_column} INTEGER
                """
        )
    )

    case_conditions = " ".join(
        (
            f"WHEN pollutant_name = '{pollutant}' "
            f"THEN (SELECT {foreign_key_column} FROM {tables['integrated_indicator']} "
            f"WHERE formula = '{formula}')"
        )
        for pollutant, formula in pollutant_mapping.items()
    )

    session.execute(
        text(
            f"""
                UPDATE {tables["map_pollutant"]}
                SET {foreign_key_column} = CASE
                    {case_conditions}
                END
                """
        )
    )


def validate_data(
    context: AssetExecutionContext, indicators_to_match: list, pollutants_to_match: list
) -> dict:
    """
    Validate the data retrieved from the database.
    """

    context.log.info("➡️ STEP 2: Validating pollutant and formula consistency...")

    pollutant_mapping = {
        "O3_avg_3_yearly": "O3",
        "PM25_avg_yearly": "PM2.5",
        "NO2_avg_yearly": "NO2",
    }

    pollutant_names = [row[0] for row in pollutants_to_match]  # row.pollutant_name
    indicator_formulas = [row[1] for row in indicators_to_match]  # row.formula

    for key in pollutant_mapping:
        if key not in pollutant_names:
            raise ValueError(f"Pollutant '{key}' not found in pollutants_to_match")

    for key, formula in pollutant_mapping.items():
        if formula not in indicator_formulas:
            raise ValueError(
                f"Pollutant formula '{formula}' not found in indicators_to_match"
            )

    context.log.info("✅ All pollutants and formulas found in the respective tables.")

    return pollutant_mapping


def retrieve_data(context: AssetExecutionContext, session: Session) -> tuple:
    """
    Retrieve data from the database.
    """

    context.log.info(
        "➡️ STEP 1: Retrieving indicator and pollutant data from the database..."
    )

    indicators_to_match = session.query(
        IntegratedIndicator.id_indicator, IntegratedIndicator.formula
    ).all()

    log_dataframe(
        context,
        "Indicators to match:",
        pd.DataFrame(indicators_to_match),
    )

    pollutants_to_match = session.query(MapPollutant.pollutant_name).all()

    log_dataframe(
        context,
        "Pollutants to match:",
        pd.DataFrame(pollutants_to_match),
    )

    return indicators_to_match, pollutants_to_match
