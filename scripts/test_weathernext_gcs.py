"""
Probe script to verify Google Cloud Storage access to Google DeepMind WeatherNext datasets.
Run after executing: gcloud auth application-default login
"""
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("CYCLOPS: Google WeatherNext GCS Access Verification")
    print("=" * 60)

    try:
        import gcsfs
        import xarray as xr
        print(" [OK] gcsfs and xarray are installed.")
    except ImportError as e:
        print(f" [ERROR] Missing dependency: {e}")
        sys.exit(1)

    print("\n1. Initializing Google Cloud Storage filesystem (token='google_default')...")
    try:
        fs = gcsfs.GCSFileSystem(token="google_default")
        print(" [OK] GCSFileSystem initialized with Application Default Credentials.")
    except Exception as e:
        print(f" [ERROR] Failed to load credentials: {e}")
        print("\n -> Please run in your terminal: gcloud auth application-default login")
        sys.exit(1)

    targets = [
        ("WeatherNext 3 (Latest)", "gs://weathernext/weathernext_3_0_0/zarr"),
        ("WeatherNext 2 Ensemble", "gs://weathernext/weathernext_2_0_0/zarr"),
        ("WeatherNext 2 Mean", "gs://weathernext/weathernext_2_0_0_mean/zarr"),
    ]

    success = False
    for label, uri in targets:
        bucket_path = uri.replace("gs://", "")
        print(f"\n2. Testing access to {label} ({uri})...")
        try:
            ls_result = fs.ls(bucket_path, detail=False)
            print(f" [SUCCESS] Read access confirmed! Found {len(ls_result)} root entries.")
            print(f" Sample entries: {ls_result[:5]}")
            
            print(f" Inspecting schema via xarray...")
            ds = xr.open_zarr(uri, consolidated=True, storage_options={"token": "google_default"})
            print(f" Coordinates: {list(ds.coords)}")
            print(f" Variables: {list(ds.data_vars)}")
            print(f" Dataset summary:\n{ds}")
            success = True
            break
        except Exception as e:
            print(f" [INFO] Could not open {uri}: {e}")

    print("\n" + "=" * 60)
    if success:
        print(">>> ALL CHECKS PASSED: Live WeatherNext Access Confirmed! <<<")
    else:
        print(">>> PENDING: GCS returned access denied or path not found. <<<")
        print("Note: If you just submitted the ADC login, ensure the email matches the approved account.")
    print("=" * 60)

if __name__ == "__main__":
    main()
