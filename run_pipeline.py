from pathlib import Path

from src.skyglow.etl import load_viirs_timeseries
from src.skyglow.anomalies import detect_anomalies
from src.skyglow.plotting import plot_timeseries_with_anomalies

def main() -> None:
    raw_tif = Path("data/raw/viirs_local_monthly.tif")
    if not raw_tif.exists():
        raise FileNotFoundError(
            f"Expected multi-band GeoTIFF at {raw_tif}."
        )

    # for generic geospatial data, use the following instead: 
    # data_dir = Path("data/raw")
    # bbox = (-2.2, 51.3, -2.0, 51.5)  # defines RoI (lon_min, lat_min, lon_max, lat_max)

    ts_df = load_viirs_timeseries(raw_tif)

    # ts = build_brightness_timeseries(data_dir, bbox)
    # df = detect_anomalies(ts["mean_radiance"]

    result = detect_anomalies(ts_df["mean_radiance"], window=12, z_thresh=2.5)

    # save and export for plotting
    out_csv = Path("data/processed/brightness_anomalies.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv)

    out_png = Path("data/processed/brightness_anomalies.png")
    plot_timeseries_with_anomalies(result, out_png) # replace result with df if using bbox

    print(f"Wrote: {out_csv}")
    print(f"Wrote: {out_png}")

if __name__ == "__main__":
    main()

