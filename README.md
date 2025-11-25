# skyglow-anomaly

Project for detecting long-term changes in local sky brightness across a given set of grid tiles. Requires `pandas`, `numpy`, `matplotlib` and `rasterio`. Can be run on a variety of satellite data but is currently set up for a VIIRS multi-band cutout of given latitude and longitude. Details on getting a suitable dataset tbd. 

ETL will require fine-tuning for different datasets, unfortunately. This is something I may fix in future.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Place exported multi-band GeoTIFF here:
#   data/raw/viirs_locals_monthly.tif

python run_pipeline.py
