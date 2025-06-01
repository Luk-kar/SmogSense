"""
Consolidates 'province' data from the annual_statistics and station schemas into an integrated schema.
This asset:
- Depends on previously uploaded data in `air_quality_dim_annual_statistics.province` and `air_quality_dim_station.province`.
- Compares and identifies any discrepancies between the two sets of data.
- Unifies them into a new `air_quality_dim_integrated.province` table.
- Updates foreign keys in the `zone` and `area` tables to reference `air_quality_dim_integrated.province`.
- Removes redundant `province` tables from the annual_statistics and station schemas after integration.

This asset depends on keys:
- upload_data_province_annual_statistics
- upload_data_province
"""

# Dagster
from dagster import asset, Output, OpExecutionContext

# Third-party
import pandas as pd

# SQLAlchemy
from sqlalchemy import text
from sqlalchemy.orm import Session


# Pipelines
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    UnificationGroups,
)
from common.utils.database.session_handling import get_database_session
from common.utils.database.data_ingestion import upload_data_asset
from common.utils.database.schema_operations import get_table_name
from common.utils.logging import log_asset_materialization
from air_quality.models.unification_models import (
    Province as IntegratedProvince,
)
from air_quality.models.station_models import (
    Province as StationProvince,
    Area as StationArea,
)
from air_quality.models.annual_statistics_models import (
    Province as AnnualStatisticsProvince,
    Zone as AnnualStatisticsZone,
)


@asset(
    group_name=UnificationGroups.DATABASE_UNIFICATION,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        "upload_data_province_annual_statistics",
        "upload_data_province",
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
def create_table_unified_province(context: OpExecutionContext):
    """
    "Unifies province data from `annual_statistics` and `station` schemas into an integrated schema.
    """

    with get_database_session(context) as session:

        context.log.info(
            "➡️ Comparing `province` data from `annual_statistics` and `station` schemas..."
        )

        annual_stats_data, station_data = fetch_province_data(context, session)

        station_dict, annual_stats_dict = convert_province_data_to_dicts(
            annual_stats_data, station_data
        )

        compare_province_data(context, station_dict, annual_stats_dict)

        verify_data_consistency(context, station_dict, annual_stats_dict)

        station_df = pd.DataFrame(
            station_dict.items(), columns=["id_province", "province"]
        )

        upload_data_asset(
            context=context,
            data_frame=station_df,
            model_class=IntegratedProvince,
            mode="copy",
        )

    log_asset_materialization(
        context=context,
        asset_key="create_table_unified_province",
        data_frame=station_df,
        description="Integrated province data from the `annual_statistics` and `station` schemas.",
    )


def convert_province_data_to_dicts(
    annual_stats_data: list[AnnualStatisticsProvince],
    station_data: list[StationProvince],
):
    """
    Converts province data from `annual_statistics` and `station` schemas into dictionaries.
    """

    station_dict = {
        row.id_province: row.province.strip().lower() for row in station_data
    }
    annual_stats_dict = {
        row.id_province: row.province.strip().lower() for row in annual_stats_data
    }

    return station_dict, annual_stats_dict


def verify_data_consistency(
    context: OpExecutionContext, station_dict, annual_stats_dict
):
    """
    Verifies data consistency between the province ids in `annual_statistics`
    and `station` schemas.
    """
    context.log.info(
        (
            "➡️ Verifying province data consistency between `annual_statistics`"
            "and `station` schemas..."
        )
    )

    discrepancies_id = pd.DataFrame(
        columns=["id", "province_stats", "province_station"]
    )

    for _id, province_stats in annual_stats_dict.items():
        province_station: str = station_dict[_id]

        if province_station is None or province_stats != province_station:
            new_row = pd.DataFrame(
                [
                    {
                        "id": _id,
                        "province_stats": province_stats,
                        "province_station": province_station,
                    }
                ]
            )
            discrepancies_id = pd.concat([discrepancies_id, new_row], ignore_index=True)

        # Log any discrepancies
    if discrepancies_id.empty:
        context.log.info("No discrepancies found in province ids.")
    else:
        context.log.error(f"Discrepancies found in province ids:\n{discrepancies_id}")
        raise ValueError(
            "❌ Discrepancies found in province ids. Please review the logs."
        )


def fetch_province_data(context: OpExecutionContext, session: Session):
    """
    Fetches province data from both `annual_statistics` and `station` schemas.
    """
    context.log.info(
        "➡️ Fetching `province` data from `annual_statistics` and `station` schemas..."
    )
    annual_stats_data = session.query(AnnualStatisticsProvince).all()
    station_data = session.query(StationProvince).all()
    return annual_stats_data, station_data


def compare_province_data(
    context: OpExecutionContext, station_dict: dict, annual_stats_dict: dict
):
    """
    Compares province data between `annual_statistics` and `station` schemas.
    """
    context.log.info(
        "➡️ Comparing `province` data from `annual_statistics` and `station` schemas..."
    )

    # Check for discrepancies
    provinces_station = set(station_dict.values())
    provinces_stats = set(annual_stats_dict.values())
    differed_provinces = provinces_stats.symmetric_difference(provinces_station)

    if differed_provinces:
        context.log.error(
            f"Discrepancies found in unique provinces:\n{differed_provinces}"
        )
        raise ValueError(
            "❌ Discrepancies found in unique provinces. Please review the logs."
        )
    else:
        context.log.info("No discrepancies found in unique provinces.")


@asset(
    group_name=UnificationGroups.DATABASE_UNIFICATION,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        "create_table_unified_province",
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_UNIFICATION,
        )
    },
)
def add_foreign_keys_unified_province(context: OpExecutionContext) -> Output[None]:
    """
    Updates foreign keys in the `zone` and `area` tables to
    reference the integrated `province` table.
    """

    with get_database_session(context) as session:

        context.log.info(
            (
                "➡️ Updating foreign keys in the `zone` and `area` tables to"
                "reference the integrated `province` table..."
            )
        )

        area_table_name = get_table_name(StationArea)
        zone_table_name = get_table_name(AnnualStatisticsZone)
        integrated_province = get_table_name(IntegratedProvince)

        # Update the foreign key for `area` table
        update_foreign_key(
            session,
            table_name=area_table_name,
            constraint_name="area_id_province_fkey",
            integrated_table=integrated_province,
            context=context,
        )

        # Update the foreign key for `zone` table
        update_foreign_key(
            session,
            table_name=zone_table_name,
            constraint_name="zone_id_province_fkey",
            integrated_table=integrated_province,
            context=context,
        )

        session.commit()

    return Output(
        None,
    )


def update_foreign_key(
    session: Session,
    table_name: str,
    constraint_name: str,
    integrated_table: str,
    context: OpExecutionContext,
):
    """
    Helper function to drop and add a foreign key constraint.
    """

    context.log.info(
        (
            f"• Updating foreign keys in the `{table_name}` table to"
            f"reference the integrated `{integrated_table}` table..."
        )
    )

    # Drop the existing constraint if it exists
    session.execute(
        text(
            f"""
            ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name};
            """
        )
    )

    # Add the new constraint
    session.execute(
        text(
            f"""
            ALTER TABLE {table_name}
            ADD CONSTRAINT {constraint_name}
            FOREIGN KEY (id_province) REFERENCES {integrated_table}(id_province);
            """
        )
    )

    context.log.info(
        f"✅ The foreign key in the `{table_name}` table has been successfully updated!"
    )


@asset(
    group_name=UnificationGroups.DATABASE_UNIFICATION,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        "add_foreign_keys_unified_province",
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_UNIFICATION,
        )
    },
)
def drop_duplicated_tables_province(context: OpExecutionContext) -> Output[None]:
    """
    Drops redundant `province` tables from the `annual_statistics` and
    `station` schemas after integration.
    """

    with get_database_session(context) as session:

        context.log.info(
            (
                "➡️ Dropping redundant `province` tables from the"
                "`annual_statistics` and `station` schemas after integration..."
            )
        )

        station_province_table = get_table_name(StationProvince)
        stats_province_table = get_table_name(AnnualStatisticsProvince)

        session.execute(text(f"DROP TABLE IF EXISTS {station_province_table} CASCADE;"))

        session.execute(text(f"DROP TABLE IF EXISTS {stats_province_table} CASCADE;"))

        session.commit()

        context.log.info(
            "✅ Redundant `province` tables have been successfully dropped!"
        )

    return Output(
        None,
    )


@asset(
    group_name=UnificationGroups.DATABASE_UNIFICATION,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        "create_table_unified_province",
        "upload_data_health_provinces",
        "drop_duplicated_tables_province",
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH,
            Categories.DATABASE,
            Categories.DATABASE_UNIFICATION,
        )
    },
)
def integrate_health_province_data(
    context: OpExecutionContext,
) -> Output[None]:
    """
    Integrates health_dim.province_population and health_dim.measurement into the air_quality_dim_integrated.province schema,
    updates foreign keys, and performs cleanup.
    """
    with get_database_session(context) as session:
        context.log.info(
            "Starting integration of health_dim data into air_quality_dim_integrated.province..."
        )

        try:
            HEALTH_SCHEMA = "health_dim"
            INTEGRATED_SCHEMA = IntegratedProvince.__table__.schema
            PROVINCE_TABLE = "province"
            POPULATION_TABLE = "province_population"
            MEASUREMENT_TABLE = "measurement"
            ID_PROVINCE_COLUMN = "id_province"
            PROVINCE_COLUMN = "province"

            drop_foreign_keys(
                context, session, HEALTH_SCHEMA, POPULATION_TABLE, MEASUREMENT_TABLE
            )

            update_province_id(
                context,
                session,
                HEALTH_SCHEMA,
                INTEGRATED_SCHEMA,
                PROVINCE_TABLE,
                POPULATION_TABLE,
                MEASUREMENT_TABLE,
                ID_PROVINCE_COLUMN,
                PROVINCE_COLUMN,
            )

            convert_province_id_to_integer(
                context,
                session,
                HEALTH_SCHEMA,
                POPULATION_TABLE,
                MEASUREMENT_TABLE,
                ID_PROVINCE_COLUMN,
            )

            readd_foreign_keys_to_health_tables(
                context,
                session,
                HEALTH_SCHEMA,
                INTEGRATED_SCHEMA,
                PROVINCE_TABLE,
                POPULATION_TABLE,
                MEASUREMENT_TABLE,
                ID_PROVINCE_COLUMN,
            )

            # Cleanup
            drop_province_table(context, session, HEALTH_SCHEMA, PROVINCE_TABLE)

            session.commit()
            context.log.info(
                f"Successfully integrated {HEALTH_SCHEMA} data into {INTEGRATED_SCHEMA}.{PROVINCE_TABLE}!"
            )

        except Exception as e:
            session.rollback()
            context.log.error(f"An error occurred during integration: {str(e)}")
            raise

    return Output(None)


def drop_province_table(context, session, HEALTH_SCHEMA, PROVINCE_TABLE):
    session.execute(
        text(f"DROP TABLE IF EXISTS {HEALTH_SCHEMA}.{PROVINCE_TABLE} CASCADE;")
    )
    context.log.info(f"Dropped {HEALTH_SCHEMA}.{PROVINCE_TABLE} table")


def readd_foreign_keys_to_health_tables(
    context,
    session,
    HEALTH_SCHEMA,
    INTEGRATED_SCHEMA,
    PROVINCE_TABLE,
    POPULATION_TABLE,
    MEASUREMENT_TABLE,
    ID_PROVINCE_COLUMN,
):
    session.execute(
        text(
            f"""
                ALTER TABLE {HEALTH_SCHEMA}.{POPULATION_TABLE}
                ADD CONSTRAINT province_population_id_province_fkey
                FOREIGN KEY ({ID_PROVINCE_COLUMN}) REFERENCES {INTEGRATED_SCHEMA}.{PROVINCE_TABLE}({ID_PROVINCE_COLUMN});
            """
        )
    )
    context.log.info(f"Added foreign key to {HEALTH_SCHEMA}.{POPULATION_TABLE}")

    session.execute(
        text(
            f"""
                ALTER TABLE {HEALTH_SCHEMA}.{MEASUREMENT_TABLE}
                ADD CONSTRAINT measurement_id_province_fkey
                FOREIGN KEY ({ID_PROVINCE_COLUMN}) REFERENCES {INTEGRATED_SCHEMA}.{PROVINCE_TABLE}({ID_PROVINCE_COLUMN});
            """
        )
    )

    context.log.info(f"Added foreign key to {HEALTH_SCHEMA}.{MEASUREMENT_TABLE}")


def convert_province_id_to_integer(
    context,
    session,
    HEALTH_SCHEMA,
    POPULATION_TABLE,
    MEASUREMENT_TABLE,
    ID_PROVINCE_COLUMN,
):
    session.execute(
        text(
            f"""
                    ALTER TABLE {HEALTH_SCHEMA}.{POPULATION_TABLE}
                    ALTER COLUMN {ID_PROVINCE_COLUMN} TYPE INTEGER USING {ID_PROVINCE_COLUMN}::integer;
                    """
        )
    )
    context.log.info(
        f"Converted {ID_PROVINCE_COLUMN} to INTEGER in {HEALTH_SCHEMA}.{POPULATION_TABLE}"
    )

    session.execute(
        text(
            f"""
                ALTER TABLE {HEALTH_SCHEMA}.{MEASUREMENT_TABLE}
                ALTER COLUMN {ID_PROVINCE_COLUMN} TYPE INTEGER USING {ID_PROVINCE_COLUMN}::integer;
            """
        )
    )
    context.log.info(
        f"Converted {ID_PROVINCE_COLUMN} to INTEGER in {HEALTH_SCHEMA}.{MEASUREMENT_TABLE}"
    )


def update_province_id(
    context,
    session,
    HEALTH_SCHEMA,
    INTEGRATED_SCHEMA,
    PROVINCE_TABLE,
    POPULATION_TABLE,
    MEASUREMENT_TABLE,
    ID_PROVINCE_COLUMN,
    PROVINCE_COLUMN,
):
    session.execute(
        text(
            f"""
                    UPDATE {HEALTH_SCHEMA}.{MEASUREMENT_TABLE} AS m
                    SET {ID_PROVINCE_COLUMN} = sub.new_id::text
                    FROM (
                        SELECT hp.{ID_PROVINCE_COLUMN} AS old_id,
                            aq.{ID_PROVINCE_COLUMN} AS new_id,
                            hp.{PROVINCE_COLUMN} AS province_name
                        FROM {HEALTH_SCHEMA}.{PROVINCE_TABLE} AS hp
                        JOIN {INTEGRATED_SCHEMA}.{PROVINCE_TABLE} AS aq
                        ON hp.{PROVINCE_COLUMN} = aq.{PROVINCE_COLUMN}
                    ) AS sub
                    WHERE m.{ID_PROVINCE_COLUMN} = sub.old_id;
                    """
        )
    )
    context.log.info(
        f"Updated {ID_PROVINCE_COLUMN} in {HEALTH_SCHEMA}.{MEASUREMENT_TABLE} using mapping from province names"
    )

    session.execute(
        text(
            f"""
                UPDATE {HEALTH_SCHEMA}.{POPULATION_TABLE} AS pp
                SET {ID_PROVINCE_COLUMN} = aq.{ID_PROVINCE_COLUMN}::text
                FROM {HEALTH_SCHEMA}.{PROVINCE_TABLE} AS hp
                JOIN {INTEGRATED_SCHEMA}.{PROVINCE_TABLE} AS aq ON hp.{PROVINCE_COLUMN} = aq.{PROVINCE_COLUMN}
                WHERE pp.{ID_PROVINCE_COLUMN} = hp.{ID_PROVINCE_COLUMN};
            """
        )
    )
    context.log.info(
        f"Updated {ID_PROVINCE_COLUMN} in {HEALTH_SCHEMA}.{POPULATION_TABLE}"
    )


def drop_foreign_keys(
    context, session, HEALTH_SCHEMA, POPULATION_TABLE, MEASUREMENT_TABLE
):
    session.execute(
        text(
            f"""
                ALTER TABLE {HEALTH_SCHEMA}.{POPULATION_TABLE}
                DROP CONSTRAINT IF EXISTS province_population_id_province_fkey;
                """
        )
    )
    context.log.info(
        f"Dropped foreign key constraint from {HEALTH_SCHEMA}.{POPULATION_TABLE}"
    )

    # Drop foreign key constraint from measurement
    session.execute(
        text(
            f"""
                ALTER TABLE {HEALTH_SCHEMA}.{MEASUREMENT_TABLE}
                DROP CONSTRAINT IF EXISTS measurement_id_province_fkey;
            """
        )
    )
    context.log.info(
        f"Dropped foreign key constraint from ALTER TABLE {HEALTH_SCHEMA}.{MEASUREMENT_TABLE}"
    )


@asset(
    group_name=UnificationGroups.DATABASE_UNIFICATION,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        "create_table_unified_province",
        "upload_data_province_territory",
        "drop_duplicated_tables_province",
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.TERRITORY,
            Categories.DATABASE,
            Categories.DATABASE_UNIFICATION,
        )
    },
)
def integrate_territory_province_data(
    context: OpExecutionContext,
) -> Output[None]:
    """
    Integrates territory_dim.province into air_quality_dim_integrated.province schema,
    updates foreign keys in territory_dim dependent tables, and performs cleanup.
    """
    try:

        with get_database_session(context) as session:
            context.log.info("1. Starting province data integration...")

            # Parametrize recurring variables
            TERRITORY_SCHEMA = "territory_dim"
            AIR_QUALITY_INTEGRATED_SCHEMA = IntegratedProvince.__table__.schema
            PROVINCE_TABLE = "province"
            ID_PROVINCE_COLUMN = "id_province"
            PROVINCE_COLUMN = "province"

            # Enable unaccent extension if not exists
            session.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))
            context.log.info("2. Ensured unaccent extension is available")

            # Disable foreign key constraints
            drop_constraints = [
                f"ALTER TABLE {TERRITORY_SCHEMA}.{PROVINCE_TABLE} DROP CONSTRAINT IF EXISTS province_id_province_fkey",
                f"ALTER TABLE {TERRITORY_SCHEMA}.{PROVINCE_TABLE} DROP CONSTRAINT IF EXISTS province_pkey",
            ]

            for stmt in drop_constraints:
                session.execute(text(stmt))
            context.log.info("3. Dropped foreign key and primary key constraints")

            # Update province IDs in dependent tables

            session.execute(
                text(
                    f"""
                    UPDATE {TERRITORY_SCHEMA}.{PROVINCE_TABLE} AS tp
                    SET {ID_PROVINCE_COLUMN} = aq.{ID_PROVINCE_COLUMN}
                    FROM {TERRITORY_SCHEMA}.{PROVINCE_TABLE} AS t
                    JOIN {AIR_QUALITY_INTEGRATED_SCHEMA}.{PROVINCE_TABLE} AS aq
                        ON public.unaccent(lower(t.{PROVINCE_COLUMN})) = public.unaccent(lower(aq.{PROVINCE_COLUMN}))
                    WHERE tp.{ID_PROVINCE_COLUMN} = t.{ID_PROVINCE_COLUMN}
                    """
                )
            )
            context.log.info(
                f"4. Updated province IDs in {TERRITORY_SCHEMA}.{PROVINCE_TABLE}"
            )
            # Optionally, drop the now-redundant province column.
            session.execute(
                text(
                    f"""
                    ALTER TABLE {TERRITORY_SCHEMA}.{PROVINCE_TABLE} DROP COLUMN IF EXISTS {PROVINCE_COLUMN}
                    """
                )
            )
            context.log.info("4. Dropped province column from territory_dim.province")

            # Reintroduce the primary key constraint on id_province.
            add_constraints = [
                f"ALTER TABLE {TERRITORY_SCHEMA}.{PROVINCE_TABLE} ADD CONSTRAINT province_pkey PRIMARY KEY ({ID_PROVINCE_COLUMN})",
                f"ALTER TABLE {TERRITORY_SCHEMA}.{PROVINCE_TABLE} ADD CONSTRAINT province_id_province_fkey "
                f"FOREIGN KEY ({ID_PROVINCE_COLUMN}) REFERENCES {AIR_QUALITY_INTEGRATED_SCHEMA}.{PROVINCE_TABLE}({ID_PROVINCE_COLUMN})",
            ]

            for stmt in add_constraints:
                session.execute(text(stmt))
            context.log.info("6. Reintroduced primary and foreign key constraints")

            session.commit()
            context.log.info("7. Province data integration completed successfully")
            return Output(None)

    except Exception as e:
        session.rollback()
        context.log.error(f"Integration failed: {str(e)}")
        raise
