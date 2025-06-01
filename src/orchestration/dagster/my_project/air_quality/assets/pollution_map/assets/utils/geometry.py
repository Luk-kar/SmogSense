"""
Contains utility functions for extracting and analyzing geometry data.
"""

# Python
from typing import Any, Union

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
)

# Pipeline
from common.utils.logging import (
    log_unique_values,
)
from common.utils.geometry import convert_to_wkt

# fmt: off
from air_quality.assets.\
pollution_map.assets.utils.data_builders import (
    build_dataframe_from_pollutants,
)
# fmt: on


def extract_geometry_data(context: AssetExecutionContext, data: dict) -> pd.DataFrame:
    """
    Extracts geometry data from the given data.
    """

    context.log.info("➡️ Extracting geometry data...")

    def build_geometry_rows(pollutant_name: str, characteristics: dict) -> list:
        """
        Builds geometry rows from the given pollutant name and characteristics.
        """

        year = characteristics.get("year")
        geometry_data = get_geometry_data(characteristics)
        return [
            {
                "year": year,
                "pollutant_name": pollutant_name,
                "geometry": coords,
                "value": val,
            }
            for coords, val in geometry_data
        ]

    df_geometry = build_dataframe_from_pollutants(data, build_geometry_rows)

    return df_geometry


def analyze_geometry_features(
    context: AssetExecutionContext, df_geometry: pd.DataFrame
):
    """
    Analyzes the features and structure of the geometry data.
    """

    context.log.info("➡️ Analyzing the 'features' of the geometry data...")

    log_unique_values(context, df_geometry["pollutant_name"], "pollutants")
    log_unique_values(context, df_geometry["year"], "years")

    context.log.info("➡️ Analyzing the 'structure' of the geometry data...")

    df_hashable = pd.DataFrame(columns=["geometry"])

    df_hashable["geometry"] = df_geometry["geometry"].apply(
        convert_nested_lists_to_tuples
    )

    context.log.info(
        f"Geo-polygons 'structure' statistics:\n"
        f" • Number of unique geometries: {df_hashable['geometry'].nunique()}\n"
        f" • Min number of points: {df_hashable['geometry'].apply(len).min()}\n"
        f" • Max number of points: {df_hashable['geometry'].apply(len).max()}\n"
        f" • Median number of points: {df_hashable['geometry'].apply(len).median()}"
    )

    # Identify geometry with maximum points
    max_geometry_points = find_max_points_count(df_hashable)
    max_geometry_row = generate_lengths_report(df_hashable, max_geometry_points)

    context.log.info(
        (
            f"Example of 'max points geometry' (len={max_geometry_points}):"
            f"\n{max_geometry_row['geometry']}"
        )
    )

    depth_element_report = generate_depth_report(max_geometry_row)

    context.log.info(
        f"Depth elements in the example 'max points geometry':\n{depth_element_report}"
    )

    context.log.info("➡️ Analyzing the structure of all 'geometry points'...")

    max_depth_in_geometry = find_max_depth(df_hashable)

    lengths_report = generate_length_report_by_depth(max_geometry_row)

    context.log.info(
        f"Max lengths at each depth in all 'geometry points':\n{max_depth_in_geometry}"
    )

    context.log.info(
        "Unique lengths at each depth in the 'geometry points'.\n"
        "(Providing insight into the structure's complexity\n"
        "and helping identify if certain depths might be overly nested or simplified):\n"
        f"{lengths_report}"
    )

    df_hashable["depth"] = df_hashable["geometry"].apply(check_depth)

    depths = df_hashable["depth"].unique()

    # Show unique depths
    unique_depths = df_hashable["depth"].unique()
    # Adjusted for readability (depth starts from 0)
    adjusted_depths = [depth - 1 for depth in unique_depths]

    context.log.info(
        f"Unique depths in the 'geometry points' (adjusted):\n{adjusted_depths}"
    )

    for depth in depths:
        min_depth_row = df_hashable[df_hashable["depth"] == depth].iloc[0]

        context.log.info(
            f"Example of depth={depth - 1} geometry:\n" f"{min_depth_row['geometry']}"
        )

    # drop depth column
    df_hashable = df_hashable.drop(columns=["depth"])

    context.log.info("➡️ Analyzing 'values' in the geometry data...")

    context.log.info(
        f"Value statistics:\n"
        f" • Number of unique 'values': {df_geometry['value'].nunique()}\n"
        f" • Min 'value': {df_geometry['value'].min()}\n"
        f" • Max 'value': {df_geometry['value'].max()}\n"
        f" • Median 'value': {df_geometry['value'].median()}"
    )


def convert_nested_lists_to_tuples(nested_structure: Any) -> Any:
    """
    Recursively converts all nested lists in a given object to tuples.

    This is useful for handling data structures where lists need to be
    converted into tuples, such as preparing data for tasks like
    comparing geometry or creating hashable objects for uniqueness checks.
    """

    if isinstance(nested_structure, list):
        return tuple(convert_nested_lists_to_tuples(item) for item in nested_structure)
    return nested_structure


def check_depth(_list: Any, depth: int = 0):
    """
    Recursively check the depth of a nested list.
    """

    if isinstance(_list, (list, tuple)):
        return max((check_depth(item, depth + 1) for item in _list), default=depth)
    return depth


def count_elements_at_each_depth(
    obj: Union[tuple, list], depth: int = 0, counts: dict = None
):
    """
    Recursively count the number of elements at each depth.
    """

    if counts is None:
        counts = {}

    if isinstance(obj, (list, tuple)):

        counts[depth] = counts.get(depth, 0) + len(obj)

        for el in obj:
            count_elements_at_each_depth(el, depth + 1, counts)

    return counts


def collect_unique_lengths_by_depth(
    obj: Union[tuple, list], depth: int = 0, lengths_by_depth: dict = None
):
    """
    Recursively gather unique lengths at each depth.
    """

    if lengths_by_depth is None:
        lengths_by_depth = {}

    if isinstance(obj, (tuple, list)):

        lengths_by_depth.setdefault(depth, set()).add(len(obj))

        for el in obj:
            collect_unique_lengths_by_depth(el, depth + 1, lengths_by_depth)

    return lengths_by_depth


def format_depth_lengths_report(lengths_by_depth: dict) -> str:
    """
    Create a formatted string for unique lengths by depth.
    """

    lines = []

    for depth in sorted(lengths_by_depth.keys()):

        sorted_lengths = sorted(lengths_by_depth[depth])
        lines.append(f"Depth {depth}: {sorted_lengths}")

    return "\n".join(lines)


def find_max_depth(df_hashable: pd.DataFrame) -> int:
    """
    Determine the maximum nesting depth across all geometries.
    """

    return (
        df_hashable["geometry"]
        .apply(lambda geom: max(count_elements_at_each_depth(geom).keys()))
        .max()
    )


def generate_depth_report(max_geometry_sample: pd.Series) -> str:
    """
    Produce a readable report of how many elements exist at each depth.
    """

    depth_counts = count_elements_at_each_depth(max_geometry_sample["geometry"])

    report_lines = []
    for d in sorted(depth_counts.keys()):
        report_lines.append(f"Depth {d}: {depth_counts[d]} elements")

    return "\n".join(report_lines)


def find_max_points_count(df_hashable: pd.DataFrame) -> int:
    """
    Retrieve a geometry example that has the maximum number of points.
    """

    return df_hashable["geometry"].apply(len).max()


def generate_lengths_report(df_hashable, max_geometry_points: int) -> pd.Series:
    """
    Produce a report of all unique lengths at each depth for a given geometry.
    """

    return df_hashable[df_hashable["geometry"].apply(len) == max_geometry_points].iloc[
        0
    ]


def generate_length_report_by_depth(max_geometry_sample: pd.Series) -> str:
    """
    Generates a report on the unique lengths at each depth in the given geometry row.
    """

    lengths_info = collect_unique_lengths_by_depth(max_geometry_sample["geometry"])

    return format_depth_lengths_report(lengths_info)


def convert_geometry_to_wkt(
    context: AssetExecutionContext, df_geometry: pd.DataFrame
) -> pd.DataFrame:
    """
    Converts the geometry data to WKT format.
    """

    context.log.info(
        "➡️ Converting tuple to WKT (Well-known text representation of geometry)..."
    )

    df_geometry["geometry"] = df_geometry["geometry"].apply(convert_to_wkt)

    context.log.info(f"Example of WKT geometry:\n{df_geometry['geometry'].iloc[0]} ")

    return df_geometry


def get_geometry_data(characteristics: dict) -> list:
    """
    Extract geometry coordinates and values from 'features'.
    """
    geometry_rows = []
    indicators = characteristics.get("indicator", [])

    for ind in indicators:

        features = ind.get("features", [])

        for f in features:

            geometry_data = f.get("geometry", {})
            properties = f.get("properties", {})
            coordinates = geometry_data.get("coordinates")
            value = properties.get("wartosc")

            if coordinates is not None and value is not None:
                geometry_rows.append((coordinates, value))

    return geometry_rows
