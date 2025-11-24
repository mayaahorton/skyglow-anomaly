from pathlib import Path
from typing import Tuple, List
import re
import numpy as np
import pandas as pd
import rasterio

# Simple filename parser, expecting something like vnl_2015_01.tif
# Currently requires manual editing for different datasets
DATE_RE = re.compile(r".*?(\d{4})[_-](\d{2}).*\.tif$")

def parse_date_from_filename(path: Path) -> pd.Timestamp:
    m = DATE_RE.match(path.name)
    if not m:
        raise ValueError(f"Cannot parse date from {path.name}")
    year, month = map(int, m.groups())
    return pd.Timestamp(year=year, month=month, day=1)

def load_raster(path: Path):
    ds = rasterio.open(path)
    data = ds.read(1)  # assume first band is average radiance
    transform = ds.transform
    return data, transform, ds.crs

def mask_bbox(data: np.ndarray, transform, bbox: Tuple[float, float, float, float]) -> np.ndarray:
    """
    bbox = (min_lon, min_lat, max_lon, max_lat) in EPSG:4326
    """
    min_lon, min_lat, max_lon, max_lat = bbox

    # Transform row/col <-> lon/lat
    # Using rasterio's index() and transform() helpers:
    import rasterio

    # Top-left and bottom-right pixel indices
    row_min, col_min = rasterio.transform.rowcol(transform, min_lon, max_lat)
    row_max, col_max = rasterio.transform.rowcol(transform, max_lon, min_lat)

    # Ensure ordering
    row_start, row_end = sorted((row_min, row_max))
    col_start, col_end = sorted((col_min, col_max))

    window = data[row_start:row_end+1, col_start:col_end+1]
    return window

def build_brightness_timeseries(
    data_dir: Path,
    bbox: Tuple[float, float, float, float]
) -> pd.DataFrame:
    """
    Loop through all GeoTIFFs in data_dir, extract mean radiance in bbox,
    and return a DataFrame with one row per month.
    """
    records: List[dict] = []

    for path in sorted(data_dir.glob("*.tif")):
        date = parse_date_from_filename(path)
        arr, transform, crs = load_raster(path)

        # Assumes EPSG:4326; v1 uses  VNL/BlackMarble
        window = mask_bbox(arr, transform, bbox)

        # Mask invalid values if needed (e.g. negative radiance or zeros)
        valid = window[np.isfinite(window)]
        # Clips products use 0 as background; this is also dataset-dependent
        valid = valid[valid > 0]

        if valid.size == 0:
            mean_rad = np.nan
        else:
            mean_rad = float(valid.mean())

        records.append({"date": date, "mean_radiance": mean_rad})

    df = pd.DataFrame.from_records(records).sort_values("date")
    df.set_index("date", inplace=True)
    return df

