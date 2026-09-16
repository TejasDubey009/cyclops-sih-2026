# CYCLOPS: Data, Models, Algorithms, and APIs Architecture Guide

This guide provides a complete, clear breakdown of the exact **Data Sources**, **Models and Algorithms**, **Backend APIs**, and **Code Modules** powering the three core capabilities of the CYCLOPS Meteorological Decision-Support Workstation.

---

## 1. IDENTIFICATION (Storm Center-Fixing & Eye Detection)

### A. Data Used
* **Primary Sensor:** ISRO MOSDAC INSAT-3DR / INSAT-3DS
  * **Channel:** Thermal Infrared Band 1 (TIR-1, central wavelength: 10.8 micrometers).
  * **File Format:** Level-1B Standard HDF5 granules (`data/raw/insat/*.h5`).
  * **Cadence & Resolution:** 30-minute geostationary refresh; 4 km native resolution at nadir.
  * **Radiometric Calibration:** Raw 10-bit sensor counts are converted to physical Kelvin brightness temperatures (180 Kelvin to 310 Kelvin, or -93°C to +37°C) using onboard calibration tables.
* **Secondary / Fallback Sensor:** NASA GIBS MODIS Band 31 (11.0 micrometer thermal infrared, 1 km resolution, polar-orbiting).

---

### B. Model & Mathematical Algorithm
* **Governing Method:** Radial Axisymmetry Variance Optimization (based on the published ARCHER scheme by Wimmers & Velden, and the center-fixing step in the Advanced Dvorak Technique / ADT).
* **Step-by-Step Logic:**
  1. A mature cyclone naturally organizes as a circularly symmetric (axisymmetric) vortex around its eye.
  2. The algorithm searches candidate center coordinates within a 600 km bounding box.
  3. For every candidate point, it samples temperatures along concentric circular rings from 15 km out to 250 km, spaced 5 km apart.
  4. It computes the **Axisymmetry Score (S)**:
     ```text
     Score S = Between-Ring Variance / (Between-Ring Variance + Within-Ring Variance)
     ```
     * **Between-Ring Variance:** Measures the radial temperature contrast from the warm eye to the freezing eyewall.
     * **Within-Ring Variance:** Measures azimuthal irregularity or clumpiness along each single ring.
  5. The point that maximizes Score S is mathematically locked as the cyclone center.
* **Sub-Pixel Eye Refinement:**
  * If a warm depression is enclosed by a complete cold eyewall ring (temperatures below -60°C), the center is refined to the local peak temperature with sub-pixel precision.
* **False-Alarm Noise Rejection:**
  * If the input is clear sky or disorganized clouds, the concentric symmetry disappears and Score S drops below 0.15. The system outputs `detected: false` with low confidence (< 20%), preventing false alerts.
* **Why this approach instead of a neural network?**
  * It has **zero fitted weights or parameters**. It cannot hallucinate coordinates, requires no training data, and provides 100% reproducible, physically grounded results.

---

### C. APIs & Code Modules
* **Core Algorithm File:** `src/cyclops/analysis/centre_fix.py`
  * Main class: `CentreFix` (outputs: latitude, longitude, symmetry score, eye detected flag, confidence).
  * Main functions: `find_centre()`, `score_candidate()`, `_refine_eye()`.
* **Backend API Endpoints:**
  * `GET /v1/cases/{case_id}/frames/{iso_time}?georef=1` — returns the georeferenced satellite raster, bounding box, and center coordinate.
  * `WebSocket /v1/live?session_id=...` — streams real-time center fixes and satellite frames every 30 minutes.
* **Frontend Visualization:** `console/src/components/MapView.tsx` (renders the crosshair and pulsing eye indicator).

---

## 2. CLASSIFICATION (Objective Dvorak & Intensity Estimation)

### A. Data Used
* **Input Imagery:** Calibrated 10.8 micrometer geostationary brightness temperature grid from ISRO INSAT-3DR (a 128x128 pixel crop centered on the storm eye).
* **Ground Truth Validation Archives:**
  * NOAA NCEI IBTrACS v04r01 (`data/raw/ibtracs.NI.list.v04r01.csv`).
  * Field: `NEWDELHI_WIND` (official IMD 3-minute sustained wind standard in knots, strictly avoiding 1-minute US JTWC wind mixing).
  * Covers 301 historical North Indian Ocean cyclones (1990 to 2025, comprising 5,187 fixes).

---

### B. Model & Mathematical Algorithm
* **Governing Method:** Automated Enhanced-Infrared (EIR) Objective Dvorak Technique (Dvorak 1984; Velden et al. 2006).
* **Step-by-Step Logic:**
  1. **Pattern Categorization:** Analyzes cloud morphology into one of four patterns: Eye, Central Dense Overcast (CDO), Shear, or Embedded Center.
  2. **Thermal Convective Extraction:**
     * Extracts the coldest cloud-top temperature in the convective core (for Cyclone Fani: -93.3°C / 179.85 Kelvin).
     * Measures the equivalent circular diameter of the dense overcast shield colder than -70°C (203.15 Kelvin).
  3. **T-Number Formulation:**
     * For CDO patterns:
       ```text
       T-number = 3.5 + (CDO Diameter in km - 150) / 100 + Coldest Top Adjustment
       ```
     * For Eye patterns: Computes temperature contrast between the warm eye peak and the surrounding cold eyewall ring.
  4. **Official IMD Operational Wind Conversion:**
     * Converts the objective T-number to 3-minute sustained wind speed in knots using the official IMD operational power-law formula:
       ```text
       Wind Speed (knots) = 14.17 * (T-number ^ 1.12)
       ```
     * Example: T4.5 yields 68 knots (Very Severe Cyclonic Storm); T6.5 yields 125 knots (Extremely Severe Cyclonic Storm).
* **Secondary Deep Learning Parity Check:**
  * ResNet-18 vision backbone fused with kinematic features (`src/cyclops/models/intensity_fusion.py`) exported to ONNX (`models/cyclops_intensity.onnx`) for cross-model validation.

---

### C. APIs & Code Modules
* **Core Logic Modules:**
  * `src/cyclops/analysis/dvorak.py` (`estimate_dvorak()`, `_classify_pattern()`, `_measure_cdo()`).
  * `src/cyclops/domain/imd.py` (`t_number_to_wind()`, `to_imd_category()`).
* **Backend API Endpoints:**
  * `POST /v1/classify` — takes a satellite image crop and returns T-number, wind speed, confidence interval, and pattern type.
  * `GET /v1/cases/{case_id}/lifecycle` — returns the full historical trajectory across IMD categories.
* **Frontend Visualization:**
  * `console/src/components/IntensityPanel.tsx` (renders the IMD Category badge, sustained wind, and 90% confidence interval bar).
  * `console/src/components/CamViewer.tsx` (convective core thermal focus viewer with opacity controls).

---

## 3. NOWCASTING (24-Hour Prediction & Calibrated Uncertainty Cones)

### A. Data Used
* **Historical Kinematic Archives:**
  * NOAA IBTrACS v04r01 (past coordinates, 3-minute sustained winds, translation speed, motion direction).
* **Foundation Atmospheric Environment:**
  * Google DeepMind WeatherNext 3 / ERA5 Foundation Reanalysis (`data/raw/weathernext/nio_subset.zarr`).
  * 8 ensemble members on a 0.5-degree spatial grid across the North Indian Ocean (0° to 30° North, 40° to 100° East).
  * **Key Atmospheric Variables:**
    * **500 hPa Synoptic Steering Winds:** Governs deep atmospheric advection that drives the storm's forward motion.
    * **850-to-200 hPa Vertical Wind Shear:** Determines whether the cyclone can intensify or will get ripped apart.
    * **Sea Surface Temperature (SST):** Quantifies the oceanic thermal energy fueling the convective engine.

---

### B. Model & Mathematical Algorithm
* **Architecture:** 36 Quantile Gradient-Boosted Decision Trees (`HistGradientBoostingRegressor` via `scikit-learn`).
* **Model Breakdown:**
  * **4 Lead Horizons:** +6 hours, +12 hours, +18 hours, +24 hours.
  * **3 Forecast Targets:** Change in Latitude, Change in Longitude, and Change in Wind Speed.
  * **3 Quantiles per Target:** 
    * 10th percentile (conservative lower bound)
    * 50th percentile (median / most likely path)
    * 90th percentile (worst-case upper bound)
  * Total models: 4 horizons * 3 targets * 3 quantiles = 36 models.
* **21 Causal Input Features:**
  * *Kinematics:* Current latitude, longitude, sustained wind, translation speed, bearing angle.
  * *Historical Momentum:* Past 6h, 12h, and 24h displacements and intensity changes.
  * *WeatherNext 3 Atmosphere:* Sea Surface Temperature, vertical wind shear magnitude, 500 hPa steering winds (u and v components).
  * *Geographic Anchors:* Distance to coastline in kilometers, Day-of-Year seasonal cycle harmonics.
  * *Persistence Anchors:* Extrapolated linear momentum endpoints.
* **Predicting Residuals from Linear Persistence:**
  * The trees do not guess raw unconstrained coordinates. Instead, they predict the deviation (residual) from linear persistence:
    ```text
    Residual = Actual Future Position - Linear Extrapolated Position
    ```
  * This physically guarantees that the forecast respects the storm's current momentum.
* **Calibrated Empirical Uncertainty Cones (`models/cone_radii.json`):**
  * Uncertainty cone radii are calculated from the empirical 67th-percentile error distributions of historical out-of-sample test storms:
    * **+6h Lead:** 36.3 km radius
    * **+12h Lead:** 71.4 km radius
    * **+18h Lead:** 116.1 km radius
    * **+24h Lead:** 157.4 km radius
  * **Measured Coverage:** 68.2% of all out-of-sample validation positions fall strictly inside the cone (meeting the official NHC/IMD 67% requirement).

---

### C. APIs & Code Modules
* **Core Logic Modules:**
  * `src/cyclops/models/nowcast_gbm.py` (GBM model structure, quantile objectives, inference).
  * `src/cyclops/data/features.py` (builds the 21 causal features).
  * `src/cyclops/providers/weathernext_local.py` (extracts environmental steering from the WeatherNext Zarr store).
  * Saved models: `models/nowcast_gbm.joblib` and `models/cone_radii.json`.
* **Backend API Endpoints:**
  * `POST /v1/nowcast` — accepts current storm state and returns +6h to +24h positions, wind quantiles, and cone radii.
  * `GET /v1/cases/{case_id}/track?until=...` — serves historical track fixes up to a specific hour without leaking future data.
* **Frontend Visualization:**
  * `console/src/components/ForecastTable.tsx` (renders the +6h to +24h projection table).
  * `console/src/components/MapView.tsx` (draws the dynamic uncertainty cone and forecast track on the map).
  * `console/src/components/WindParticles.tsx` (animates 1,400 wind particles using Rankine vortex + WeatherNext 3 winds).

---

## Summary Matrix

| Capability | Raw Data Used | Model / Algorithm Used | Key Code File | API Endpoint | Output to Forecaster |
|---|---|---|---|---|---|
| **1. Identification** | ISRO INSAT-3DR 10.8 micrometer TIR-1 HDF5 | Radial Axisymmetry Optimization | `src/cyclops/analysis/centre_fix.py` | `GET /v1/cases/.../frames` | Precise Eye Coordinates (Lat/Lon), Symmetry Score, Sub-pixel Eye Fix |
| **2. Classification** | INSAT-3DR Brightness Temps + NOAA IBTrACS | Automated EIR Objective Dvorak | `src/cyclops/analysis/dvorak.py` | `POST /v1/classify` | Dvorak T-number, IMD Category (e.g. ESCS), 3-min Sustained Wind (kt) |
| **3. Nowcasting** | NOAA IBTrACS + Google WeatherNext 3 Zarr | 36 Quantile Gradient-Boosted Trees (`NowcastGBM`) | `src/cyclops/models/nowcast_gbm.py` | `POST /v1/nowcast` | +6h to +24h Track Coordinates, 10th-to-90th Percentile Wind Bands, 67% Error Cones |
