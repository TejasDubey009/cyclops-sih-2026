"""
Prefetch genuine Google DeepMind WeatherNext data from live Google Cloud Storage
and save a regional North Indian Ocean (NIO) Zarr slice locally for Cyclone Fani.

Bounding box:
  - Lat: 0.0 to 30.0 N
  - Lon: 40.0 to 100.0 E
  - Target: Cyclone Fani window (2019-04-25 to 2019-05-05)
  - Levels: 200, 500, 850 hPa
"""
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import gcsfs
import google.auth
import google.auth.transport.requests
import numpy as np
import xarray as xr

from cyclops.config import DATA_RAW

LIVE_GCS_2019_PATH = (
    "weathernext/weathernext_gen_research_2019/00_12_init/119772718/1/"
    "forecasts_15d/date_range_2019-01-01_2020-01-01_12_hours.zarr"
)

def prefetch_fani_nio(out_dir: Path | None = None) -> Path:
    out = Path(out_dir or (DATA_RAW / "weathernext" / "nio_subset.zarr"))
    out.parent.mkdir(parents=True, exist_ok=True)

    print("1. Refreshing Google Application Default Credentials...")
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    fs = gcsfs.GCSFileSystem(token=creds.token)

    print(f"2. Connecting to live Google DeepMind store: gs://{LIVE_GCS_2019_PATH}...")
    mapper = fs.get_mapper(LIVE_GCS_2019_PATH)
    ds = xr.open_zarr(mapper, consolidated=True)

    print("3. Cropping to North Indian Ocean spatial box (0-30°N, 40-100°E) and Fani storm window...")
    # Note: in WeatherNext, lat runs -90 to +90 or +90 to -90
    lat_step = 1 if ds.lat.values[1] > ds.lat.values[0] else -1
    lat_slice = slice(0.0, 30.0) if lat_step == 1 else slice(30.0, 0.0)
    lon_slice = slice(40.0, 100.0)

    # Cyclone Fani storm window: 2019-04-25 to 2019-05-05
    start_t = np.datetime64("2019-04-25T00:00:00")
    end_t = np.datetime64("2019-05-05T12:00:00")

    sub_t = ds.sel(time=slice(start_t, end_t))
    sub_geo = sub_t.sel(lat=lat_slice, lon=lon_slice)

    # Select levels 200, 500, 850 hPa
    levels = [200, 500, 850]
    sub_winds = sub_geo[["u_component_of_wind", "v_component_of_wind", "geopotential", "temperature"]].sel(level=levels)

    # Unpack levels into flat variable names expected by CYCLOPS
    print("4. Structuring atmospheric variables for CYCLOPS...")
    # We take prediction_timedelta=12h (first lead step of 12-hour init cycle)
    p_step = sub_winds.prediction_timedelta.values[0]
    
    u200 = sub_winds["u_component_of_wind"].sel(level=200, prediction_timedelta=p_step).drop_vars(["level", "prediction_timedelta", "lead_time_secs"], errors="ignore").rename("u_component_of_wind_200")
    v200 = sub_winds["v_component_of_wind"].sel(level=200, prediction_timedelta=p_step).drop_vars(["level", "prediction_timedelta", "lead_time_secs"], errors="ignore").rename("v_component_of_wind_200")
    u500 = sub_winds["u_component_of_wind"].sel(level=500, prediction_timedelta=p_step).drop_vars(["level", "prediction_timedelta", "lead_time_secs"], errors="ignore").rename("u_component_of_wind_500")
    v500 = sub_winds["v_component_of_wind"].sel(level=500, prediction_timedelta=p_step).drop_vars(["level", "prediction_timedelta", "lead_time_secs"], errors="ignore").rename("v_component_of_wind_500")
    u850 = sub_winds["u_component_of_wind"].sel(level=850, prediction_timedelta=p_step).drop_vars(["level", "prediction_timedelta", "lead_time_secs"], errors="ignore").rename("u_component_of_wind_850")
    v850 = sub_winds["v_component_of_wind"].sel(level=850, prediction_timedelta=p_step).drop_vars(["level", "prediction_timedelta", "lead_time_secs"], errors="ignore").rename("v_component_of_wind_850")

    sst = sub_geo["sea_surface_temperature"].sel(prediction_timedelta=p_step).drop_vars(["prediction_timedelta", "lead_time_secs"], errors="ignore").rename("sea_surface_temperature")
    msl = sub_geo["mean_sea_level_pressure"].sel(prediction_timedelta=p_step).drop_vars(["prediction_timedelta", "lead_time_secs"], errors="ignore").rename("mean_sea_level_pressure")

    # Rename sample -> number, lat -> latitude, lon -> longitude
    out_ds = xr.Dataset(
        data_vars={
            "u_component_of_wind_200": u200.rename({"sample": "number", "lat": "latitude", "lon": "longitude"}),
            "v_component_of_wind_200": v200.rename({"sample": "number", "lat": "latitude", "lon": "longitude"}),
            "u_component_of_wind_500": u500.rename({"sample": "number", "lat": "latitude", "lon": "longitude"}),
            "v_component_of_wind_500": v500.rename({"sample": "number", "lat": "latitude", "lon": "longitude"}),
            "u_component_of_wind_850": u850.rename({"sample": "number", "lat": "latitude", "lon": "longitude"}),
            "v_component_of_wind_850": v850.rename({"sample": "number", "lat": "latitude", "lon": "longitude"}),
            "sea_surface_temperature": sst.rename({"sample": "number", "lat": "latitude", "lon": "longitude"}),
            "mean_sea_level_pressure": msl.rename({"sample": "number", "lat": "latitude", "lon": "longitude"}),
        },
        attrs={
            "description": "Genuine Google DeepMind WeatherNext Regional North Indian Ocean slice",
            "model": "WeatherNext (Google DeepMind)",
            "source": f"gs://{LIVE_GCS_2019_PATH}",
            "case": "Cyclone Fani (2019116N02090)",
            "license": "CC BY 4.0",
            "is_proxy": False,
        }
    )

    print("5. Materializing genuine array to local Zarr store...")
    if out.exists():
        shutil.rmtree(out)

    out_ds.compute().to_zarr(out, mode="w")
    print(f" [SUCCESS] Written genuine WeatherNext store to: {out}")

    meta = {
        "source": f"gs://{LIVE_GCS_2019_PATH}",
        "model": "Google DeepMind WeatherNext",
        "provenance": "100% Genuine GCS Download",
        "license": "CC BY 4.0",
        "storm": "Cyclone Fani (2019)",
        "lat_range": [float(out_ds.latitude.min()), float(out_ds.latitude.max())],
        "lon_range": [float(out_ds.longitude.min()), float(out_ds.longitude.max())],
        "time_range": [str(out_ds.time.min().values), str(out_ds.time.max().values)],
        "members": int(out_ds.number.count()),
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
    }
    (out.parent / "PREFETCH.json").write_text(json.dumps(meta, indent=2))
    print(f" [SUCCESS] Wrote metadata to {out.parent / 'PREFETCH.json'}")
    return out

if __name__ == "__main__":
    prefetch_fani_nio()
