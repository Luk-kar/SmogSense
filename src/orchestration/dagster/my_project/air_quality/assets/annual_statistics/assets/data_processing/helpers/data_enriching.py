"""Data enriching functions for the 'Time averaging' column."""

# Python
import re

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
)


def add_time_columns_based_on_averaging(
    context: AssetExecutionContext, data: pd.DataFrame
) -> pd.DataFrame:
    """Adds 'minutes', 'hours', 'days', 'weeks' columns based on the 'Time averaging' column."""

    data_enriched = data.copy()

    time_averaging_column = data_enriched["Czas uśredniania"]

    context.log.info(
        ("Current 'Time averaging' column:\n" f"{time_averaging_column.unique()}")
    )

    data_enriched["minutes"] = time_averaging_column.apply(
        lambda x: calculate_minutes(context, x)
    )

    context.log.info(
        f"The added 'minutes' column:\n{data_enriched['minutes'].unique().tolist()}"
    )

    context.log.info("Adding 'hours' column for 'Time averaging' column")
    data_enriched["hours"] = data_enriched["minutes"] / 60

    context.log.info(
        f"The added 'hours' column:\n{data_enriched['hours'].unique().tolist()}"
    )

    context.log.info("Adding 'days' column for 'Time averaging' column")

    # `/ (60 * 24)` to avoid the error of double rounding in division
    data_enriched["days"] = data_enriched["minutes"] / (60 * 24)

    context.log.info(
        f"The added 'days' column:\n{data_enriched['days'].unique().tolist()}"
    )

    return data_enriched


def calculate_minutes(context: AssetExecutionContext, value: str) -> int:
    """Converts the various 'Time averaging' value to minutes."""

    minutes_hour = 60

    # Time periods for the 'Time averaging' column:
    # "24g","1g" ,"1m" ,"2t" ,"1t"
    suffix_to_hours = {"g": minutes_hour, "m": 1, "t": 7 * (minutes_hour * 24)}

    try:
        # Check if each value follow the pattern if not raise an error
        match = re.fullmatch(r"(\d+)([gmt])", value.strip())
        if not match:
            raise ValueError(
                f"Invalid format for 'Czas uśredniania'/'Time averaging': {value}"
            )

        # Extract numeric part and suffix
        num_part = int("".join(filter(str.isdigit, value)))
        suffix_part = "".join(filter(str.isalpha, value))

        # Convert to minutes using the map
        return num_part * suffix_to_hours.get(suffix_part, 0)
    except Exception as e:
        context.log.error(f"Failed to process value '{value}': {e}")
        return None
