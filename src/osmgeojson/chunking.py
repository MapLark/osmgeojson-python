"""Bounding-box utilities: splitting large bboxes into chunks and merging results."""

from __future__ import annotations

import math
from typing import Any


# Degrees-per-metre at the equator (approximate, sufficient for splitting)
_DEG_PER_METRE_LAT = 1.0 / 111_320.0


def parse_bbox(bbox: str) -> tuple[float, float, float, float]:
    """Parse ``"min_lon,min_lat,max_lon,max_lat"`` -> ``(min_lon, min_lat, max_lon, max_lat)``."""
    parts = bbox.split(",")
    if len(parts) != 4:
        raise ValueError(
            f"Invalid bbox format {bbox!r}. Expected 'min_lon,min_lat,max_lon,max_lat'."
        )
    min_lon, min_lat, max_lon, max_lat = (float(p) for p in parts)
    return min_lon, min_lat, max_lon, max_lat


def bbox_area_deg2(bbox: str) -> float:
    """Return the area of *bbox* in square degrees."""
    min_lon, min_lat, max_lon, max_lat = parse_bbox(bbox)
    return (max_lon - min_lon) * (max_lat - min_lat)


def split_bbox(bbox: str, max_area_deg2: float) -> list[str]:
    """Split *bbox* into a grid of chunks each with area <= *max_area_deg2*.

    Returns a list of ``"min_lon,min_lat,max_lon,max_lat"`` strings.  If the
    input bbox already fits within the limit, it is returned as-is (single
    element list).
    """
    if max_area_deg2 <= 0:
        raise ValueError("max_area_deg2 must be positive.")

    min_lon, min_lat, max_lon, max_lat = parse_bbox(bbox)
    lon_span = max_lon - min_lon
    lat_span = max_lat - min_lat
    total_area = lon_span * lat_span

    if total_area <= max_area_deg2:
        return [bbox]

    # Choose the number of columns and rows so each cell <= max_area_deg2.
    # We split both axes proportionally.
    n = math.ceil(total_area / max_area_deg2)
    # Distribute n across rows and cols proportionally to span
    n_cols = max(1, round(math.sqrt(n * lon_span / lat_span)))
    n_rows = max(1, math.ceil(n / n_cols))

    chunks: list[str] = []
    col_width = lon_span / n_cols
    row_height = lat_span / n_rows

    for row in range(n_rows):
        for col in range(n_cols):
            c_min_lon = min_lon + col * col_width
            c_max_lon = min_lon + (col + 1) * col_width
            c_min_lat = min_lat + row * row_height
            c_max_lat = min_lat + (row + 1) * row_height
            chunks.append(f"{c_min_lon},{c_min_lat},{c_max_lon},{c_max_lat}")

    return chunks


def merge_features(feature_lists: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Merge multiple feature lists, deduplicating by ``feature["id"]``."""
    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    for lst in feature_lists:
        for feat in lst:
            fid = feat.get("id", "")
            if fid not in seen:
                seen.add(fid)
                merged.append(feat)
    return merged


def around_to_bbox(lon: float, lat: float, radius_m: float) -> str:
    """Convert a radius search to a bounding-box string (approximation).

    Useful when you want to use bbox-chunking logic on an ``around`` query
    area.  The result is a square bbox that fully contains the circle.
    """
    delta_lat = radius_m * _DEG_PER_METRE_LAT
    delta_lon = radius_m * _DEG_PER_METRE_LAT / max(math.cos(math.radians(lat)), 1e-9)
    return f"{lon - delta_lon},{lat - delta_lat},{lon + delta_lon},{lat + delta_lat}"


def shapely_to_bbox(geometry: Any) -> str:
    """Convert a Shapely geometry to a ``"min_lon,min_lat,max_lon,max_lat"`` bbox string.

    Requires the ``[geo]`` extra (``pip install osmgeojson[geo]``).
    """
    try:
        from shapely.geometry.base import BaseGeometry  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "shapely is required for geometry input. "
            "Install it with: pip install osmgeojson[geo]"
        ) from exc

    if isinstance(geometry, BaseGeometry):
        min_x, min_y, max_x, max_y = geometry.bounds
        return f"{min_x},{min_y},{max_x},{max_y}"

    # Accept a plain (min_lon, min_lat, max_lon, max_lat) tuple/list as well
    if hasattr(geometry, "__len__") and len(geometry) == 4:
        return f"{geometry[0]},{geometry[1]},{geometry[2]},{geometry[3]}"

    raise TypeError(
        f"Unsupported geometry type {type(geometry).__name__}. "
        "Expected a shapely geometry or a (min_lon, min_lat, max_lon, max_lat) tuple."
    )
