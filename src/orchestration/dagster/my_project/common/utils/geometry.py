"""
This module provides utility functions for handling geometric data, 
specifically for converting nested coordinate structures into Well-Known Text (WKT) format.
"""

# Third-party imports
from shapely.geometry import Polygon, MultiPolygon


def convert_to_wkt(geom_nested) -> str:
    """
    Converts a nested structure of coordinates into a valid WKT string.
    Ensures all geometries are stored as MultiPolygon for consistency.
    The input `geom_nested` can represent:
    - A Polygon (outer ring and optional holes): (( (x,y), (x,y), ... ), ( (x,y), (x,y), ... ) ...)
    - A MultiPolygon (multiple polygons, each with outer ring and optional holes):
      ( (( (x,y), ... ), ( (x,y), ... ) ... ), (( (x,y), ... ), ... ), ... )

    Returns a WKT string representing the input geometry always as a MultiPolygon.

    https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
    """

    # Helper functions to determine the geometry type

    def is_coordinate_pair(obj):
        return (
            isinstance(obj, (tuple, list))
            and len(obj) == 2
            and all(isinstance(c, (float, int)) for c in obj)
        )

    def is_ring(obj):

        # A ring should be a sequence of coordinate pairs forming a closed linear ring
        # Here we assume the input is already well-formed and closed.

        return (
            isinstance(obj, (tuple, list))
            and len(obj) > 2
            and all(is_coordinate_pair(pt) for pt in obj)
        )

    def is_polygon(obj):

        # A polygon is a tuple/list of rings: the first one is the outer boundary,
        # subsequent ones are holes.

        return (
            isinstance(obj, (tuple, list))
            and len(obj) > 0
            and all(is_ring(r) for r in obj)
        )

    def is_multipolygon(obj):

        # A multipolygon is a tuple/list of polygons

        return (
            isinstance(obj, (tuple, list))
            and len(obj) > 0
            and all(is_polygon(p) for p in obj)
        )

    # Normalize the input to a multipolygon structure
    if is_polygon(geom_nested):

        # Wrap a single polygon as a multipolygon
        polygons_data = [geom_nested]

    elif is_multipolygon(geom_nested):

        # If it's already a multipolygon, keep it as is
        polygons_data = geom_nested

    else:

        # If it's just a single ring (no holes), treat it as a single polygon
        if is_ring(geom_nested):
            polygons_data = [(geom_nested,)]

        else:

            # If the structure is unexpected, fallback to treating as a single polygon
            polygons_data = [geom_nested]

    polygons = []

    for polygon_data in polygons_data:
        # polygon_data is a polygon: (outer_ring, hole1, hole2, ...)

        outer_ring = polygon_data[0]
        holes = polygon_data[1:] if len(polygon_data) > 1 else None
        polygon = Polygon(outer_ring, holes)
        polygons.append(polygon)

    multi_polygon = MultiPolygon(polygons)

    return multi_polygon.wkt
