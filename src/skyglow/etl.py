from pathlib import Path
from typing import Tuple, List, Union
import re
import numpy as np
import pandas as pd
import rasterio

# Simple filename parser, expecting something like vnl_2015_01.tif
# Currently requires manual editing for different datasets
# DATE_RE = re.compile(r".*?(\d{4})[_-](\d{2}).*\.tif$") # for non-VIIRS timeseries

BAND_DATE_RE = re.compile(r"viirs_(\d{4})_(\d{2})")

def parse_date_from_band_name(name: str) -> pd.Timestamp:
    m = BAND_DATE_RE.fullmatch(name)
    if not m:
        raise ValueError(f"Cannot parse date from band: {name}")
    year, month = map(int, m.groups())
    return pd.Timestamp(year=year, month=month, day=1)

def load_viirs_timeseries(geotiff_path: Union[str, Path]) -> pd.DataFrame:
    """
    Reads a multi-band VIIRS GeoTIFF from Earth Engine and computes
    mean radiance per band (1 band = 1 month), and returns a time-indexed
    dataframe. This function is specific to pre-downloaded VIIRS cutouts.
    """
    geotiff_path = Path(geotiff_path)
    records = []

    with rasterio.open(geotiff_path) as src:
    # grabs band names (descriptions) from Earth Engine
        band_names = src.descriptions

    # if no descriptions can be imported
    if not any(band_names):
        band_names = [f"band_{i}" for i in range(1, src.count + 1)]

    for band_index in range(1, src.count + 1):
        name = band_names[band_index - 1]

        # get date and time from band name
        date = parse_date_from_band_name(name)

        # reads bands as masked array and drops relevant pixels (see readme for more info)
        arr = src.read(band_index, masked=True)
        data = arr.compressed() 
        data > data[data > 0] # remove if zeros or negatives aren't used for backgroud

        if data.size == 0:
            mean_rad = np.nan
        else:
            mean_rad = float(data.mean())

        records.append({"date":date, "band_name": name, "mean_radiance": mean_rad})

    df = pd.DataFrame.from_records(records).sort_values("date")
    df.set_index("date", inplace=False)    # I mean, it's up to you, but... 

# The following is not necessary with VIIRS; it applies to generic geospatial extraction
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

