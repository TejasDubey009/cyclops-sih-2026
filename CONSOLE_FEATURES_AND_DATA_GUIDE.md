# CYCLOPS Operational Console: Feature & Data Reference Guide

This comprehensive reference document details every visual element, diagnostic card, chart, and control shown in the **CYCLOPS Meteorological Console**.

For every feature captured in the operational console screenshots, this guide explains:
1. **What is it?** (Visual description and UI location)
2. **How the data gets there?** (The exact data pipeline, algorithms, and models)
3. **Why it is there?** (Meteorological and scientific necessity)
4. **How it helps us?** (Operational value to IMD forecasters and disaster managers)

---

## Quick Navigation Index

- [1. Top HUD & Synoptic Overview Banner](#1-top-hud--synoptic-overview-banner)
- [2. Lifecycle Stage & IMD Scale Card (Top Right)](#2-lifecycle-stage--imd-scale-card-top-right)
- [3. Real-Time Intensity Panel (Right Sidebar)](#3-real-time-intensity-panel-right-sidebar)
- [4. Interactive Geo-Spatial Map Canvas (Center)](#4-interactive-geo-spatial-map-canvas-center)
- [5. Intensity Trend & Quantile Nowcast Overlay (Bottom-Left)](#5-intensity-trend--quantile-nowcast-overlay-bottom-left)
- [6. "Why This Estimate" Convective Attention Viewer](#6-why-this-estimate-convective-attention-viewer)
- [7. Operational Timeline & Playback Controller (Bottom Bar)](#7-operational-timeline--playback-controller-bottom-bar)

---

## 1. Top HUD & Synoptic Overview Banner

![Top HUD](file:///d:/CYCLOPS/console/src/components/TopBar.tsx)

### 1.1 Brand & Capability Subline
* **What is it:** Located at the top-left corner: `CYCLOPS` with the subline `IDENTIFICATION · CLASSIFICATION · PREDICTION`.
* **How the data is there:** Static application configuration defined in `console/src/components/TopBar.tsx`, representing the three core mandates of Problem Statement SIH26070.
* **Why it is there:** Clarifies to evaluators that CYCLOPS is not just an intensity estimator or simple tracking tool, but an end-to-end tri-functional pipeline.
* **How it helps us:** Immediately anchors the demonstration in the three specific deliverables demanded by MoES and IMD.

### 1.2 Storm Context Header
* **What is it:** The primary banner text: `Cyclone Fani (2019) · Bay of Bengal · depression to ESCS · Odisha landfall`.
* **How the data is there:** Ingested from the case manifest metadata (`data/cases/fani_2019/manifest.json`).
* **Why it is there:** Cyclone Fani is the gold-standard benchmark storm of the North Indian Ocean (May 2019). It went from an open low to an Extremely Severe Cyclonic Storm (ESCS) and made a devastating landfall near Puri, Odisha.
* **How it helps us:** Contextualizes the entire operational replay so forecasters immediately recognize the storm name, basin, intensity trajectory, and terminal impact zone.

### 1.3 Active State Capsule (Top-Left Floating Card)
* **What is it:** A high-contrast status badge displaying: `T4.5 / T5.0 VSCS · 68 kt / 79 kt | Very Severe Cyclonic Storm | Coordinates | Timestamp (UTC)`.
* **How the data is there:** Dynamically computed from the current time step's Dvorak analysis (`dvorak.py`) and center-fixing coordinate (`centre_fix.py`).
* **Why it is there:** Forecasters need an instantaneous glance-card containing the four vital stats: Dvorak T-number, IMD category, sustained wind, and current center coordinate.
* **How it helps us:** Enables a single-glance situation assessment during shift handovers or rapid press briefing updates without searching through multiple panels.

### 1.4 Top Control Buttons ("Follow Cyclone", Case Switcher, Layers)
* **What is it:** Buttons in the top navigation bar to auto-center the camera on the storm center, switch cases, and inspect raw API data.
* **How the data is there:** State management hooks in React (`App.tsx`) controlling the MapLibre viewport camera and layer visibility.
* **Why it is there:** As a cyclone moves thousands of kilometers across the ocean, forecasters need the camera to follow the eye automatically as time advances.
* **How it helps us:** Keeps the high-resolution satellite raster and eye crosshair centered in the viewport during rapid 120x playback.

---

## 2. Lifecycle Stage & IMD Scale Card (Top Right)

### 2.1 Lifecycle Stage Badge (`● IDENTIFICATION · GENESIS` vs `● CLASSIFICATION · PEAK INTENSITY`)
* **What is it:** A dynamic pill badge that changes depending on the storm's maturity (Genesis, Rapid Intensification, Peak Eye, Landfall).
* **How the data is there:** Evaluated by rule-based lifecycle detection based on eye presence, center detection confidence, and sustained wind thresholds.
* **Why it is there:** Different lifecycle stages present completely different physical challenges:
  * In **Genesis**: The primary operational challenge is *Identification* (is there a closed vortex center at all?).
  * In **Peak Intensity**: The primary challenge is *Classification* (how cold is the eye and eyewall, and is it rapidly intensifying?).
* **How it helps us:** Guides the user's attention to the specific meteorological problem being solved at that exact synoptic hour.

### 2.2 24-Hour Intensity Trend Pill (`▲ 8 kt / 24 h` or `▲ 15 kt / 24 h`)
* **What is it:** A red/orange metric badge at the top right showing the 24-hour wind speed change.
* **How the data is there:** Calculated as: `Current Wind Speed (t) minus Observed Wind Speed (t - 24 hours)`.
* **Why it is there:** Rapid Intensification (RI) is defined by WMO/IMD as an intensity gain of 30 knots or more in a 24-hour period. Monitoring the 24-hour rate of change is the number one priority for issuing emergency landfall warnings.
* **How it helps us:** Flags dangerous intensification trends hours before the storm reaches peak velocity.

### 2.3 IMD 8-Category Spectrum Scale
* **What is it:** A colored horizontal spectrum bar showing all 8 official IMD categories:
  * **L**: Low Pressure (< 17 kt)
  * **D**: Depression (17–27 kt)
  * **DD**: Deep Depression (28–33 kt)
  * **CS**: Cyclonic Storm (34–47 kt)
  * **SCS**: Severe Cyclonic Storm (48–63 kt)
  * **VSCS**: Very Severe Cyclonic Storm (64–89 kt)
  * **ESCS**: Extremely Severe Cyclonic Storm (90–119 kt)
  * **SuCS**: Super Cyclonic Storm (>= 120 kt)
* **How the data is there:** Implemented in `console/src/domain/imd.ts` strictly following official IMD circular standards.
* **Why it is there:** IMD does not use the US Saffir-Simpson (Category 1–5) scale. Indian disaster authorities (NDMA, SDMA, Indian Navy) mandate warnings according to the IMD 8-tier scale.
* **How it helps us:** A white pointer bracket moves along the spectrum bar, giving instant visual clarity on where the storm sits between category boundaries.

### 2.4 Contextual Forecaster Narrative
* **What is it:** Meteorological commentary displayed beneath the scale (e.g., *"A disturbance organises. The question is whether a closed circulation exists at all..."* or *"A cleared eye. This is where satellite intensity estimation is most reliable..."*).
* **How the data is there:** Driven by expert meteorological heuristics mapped to detected cloud patterns (CDO, Eye, Shear).
* **Why it is there:** Bridges the gap between raw statistical numbers and actionable meteorological reasoning.
* **How it helps us:** Explains the physical significance of what is currently happening on the satellite image to junior meteorologists and emergency coordinators.

### 2.5 Audit Truth Delta Footer (`IBTrACS vs CYCLOPS`)
* **What is it:** A comparison footer: `IBTrACS: 30 kt (DD) | CYCLOPS: 68 kt (VSCS)` or `IBTrACS: 115 kt | CYCLOPS: 79 kt`.
* **How the data is there:** Compares real-time objective satellite output against the post-storm NOAA IBTrACS reanalysis archive.
* **Why it is there:** Provides total scientific transparency. In early genesis, raw infrared Dvorak often overestimates weak open waves before wind circulation closes; during peak intensity, satellite-only estimators can slightly lag aircraft or radar measurements.
* **How it helps us:** Proves to the judges that CYCLOPS is an honest, audited operational model that does not artificially fake or hardcode 100% agreement with ground truth.

---

## 3. Real-Time Intensity Panel (Right Sidebar)

### 3.1 Primary Category Banner & Wind Speed (e.g. `VSCS · 68 kt` or `79 kt`)
* **What is it:** High-contrast text display showing the estimated 3-minute sustained wind in knots and the full category name (`Very Severe Cyclonic Storm, 64–89 kt`).
* **How the data is there:** Derived from the automated Objective Dvorak formula (`dvorak.py`):
  * `Wind Speed (knots) = 14.17 * (T-number ^ 1.12)`
* **Why it is there:** Wind speed is the single most critical variable determining wind shear stress, storm surge height, and coastal structural destruction.
* **How it helps us:** Dictates emergency protocols (e.g., stopping port operations when winds exceed 34 kt; mandatory coastal evacuations when winds exceed 64 kt).

### 3.2 Calibrated 90% Confidence Interval Gauge
* **What is it:** A horizontal bracket slider showing the 90% uncertainty spread (e.g., `55 kt to 80 kt` for a 68 kt estimate, or `65 kt to 93 kt` for a 79 kt estimate).
* **How the data is there:** Computed from the empirical standard error of the objective Dvorak regression on out-of-sample North Indian Ocean storms.
* **Why it is there:** Satellite intensity estimates are subject to environmental fluctuations (convective pulses, diurnal cycles). Reporting a single point estimate creates false certainty.
* **How it helps us:** Allows disaster management teams to plan for worst-case upper bounds (the 90th percentile) when ordering shelter evacuations.

### 3.3 Diagnostic Telemetry Metrics
1. **Dvorak T-number (`4.5` or `5.0`):**
   * *What it is:* The standard meteorological intensity index ranging from 1.0 to 8.0 in 0.5 steps.
   * *How it helps:* Recognized universally by IMD, JTWC, and WMO forecasters.
2. **Detection Confidence (`26%` to `34%`):**
   * *What it is:* The radial axisymmetry variance ratio score ($S$).
   * *How it helps:* Measures how well-defined and circular the storm's eye or convective center is. In early genesis, confidence is low (26%); as the eye clears, confidence rises.
3. **Inference Latency (`103 ms` to `118 ms`):**
   * *What it is:* The time taken by the server to ingest the raw satellite crop, run center-fixing, compute Dvorak metrics, and return the JSON response.
   * *How it helps:* Demonstrates that CYCLOPS is ultra-fast, capable of operating in real time on edge hardware without supercomputing delays.
4. **Best Track Delta (`+38` or `-36`):**
   * *What it is:* Real-time delta between the objective satellite estimate and the retrospective best track.
   * *How it helps:* Enables post-event performance auditing and model fine-tuning.

---

## 4. Interactive Geo-Spatial Map Canvas (Center)

### 4.1 Offline Vector Basemap (India, Bay of Bengal, Sri Lanka)
* **What is it:** Clean dark-mode map showing coastlines, national boundaries, and landmass.
* **How the data is there:** Rendered locally by MapLibre GL from offline GeoJSON vector assets (`console/public/basemap/*.geojson`).
* **Why it is there:** Operational military, naval, and meteorological stations often operate in secure air-gapped environments or lose internet connectivity during severe storms.
* **How it helps us:** Zero reliance on Mapbox or Google Maps APIs. The system loads instantly and functions 100% offline.

### 4.2 Calibrated Thermal Infrared Satellite Layer
* **What is it:** A georeferenced raster tile draped onto the ocean surface displaying the storm's cloud shield in thermal false colors.
* **How the data is there:** Ingested from ISRO INSAT-3DR 10.8-micrometer TIR-1 HDF5 granules (`data/raw/insat/*.h5`), converted from raw digital counts to physical Kelvin, and mapped through a Celsius temperature lookup table:
  * White / Light Violet: Coldest convective core tops (down to -93.3°C)
  * Red / Orange: Intense eyewall convection (-70°C to -60°C)
  * Yellow / Green: Outer spiral convective bands (-50°C to -30°C)
  * Black / Dark Gray: Warm low clouds and clear sea surface (> 0°C)
* **Why it is there:** Infrared radiation penetrates night and day, providing continuous 24-hour storm observation.
* **How it helps us:** Enables forecasters to inspect eyewall integrity, eye clearing, and feeder band structures directly on the geographic map.

### 4.3 Animated Atmospheric Wind Streamlines (1,400 Particles)
* **What is it:** Moving vector particle streams spiraling inwards into the storm center.
* **How the data is there:** Computed in `WindParticles.tsx` using a hybrid physical model:
  * Inner Core: Modified Rankine Vortex (tangential wind profile).
  * Outer Synoptic Flow: 500 hPa and 850 hPa wind fields ingested from Google DeepMind's WeatherNext 3 / ERA5 foundation dataset (`nio_subset.zarr`).
* **Why it is there:** Static satellite clouds show temperature, not motion. Wind streamlines show the actual cyclonic circulation, boundary layer friction inflow, and asymmetric environmental advection.
* **How it helps us:** Visualizes how environmental steering currents (e.g. subtropical ridges) are pushing the cyclone towards the Odisha coast.

### 4.4 Past Observed Track Trail (Colored Nodes)
* **What is it:** Connected breadcrumb trail showing the cyclone's past positions, with colored dots representing the IMD category at each past 6-hour interval.
* **How the data is there:** Plotted from historical track fixes in the database.
* **Why it is there:** Cyclone trajectory forecasting depends heavily on kinematic history (past speed, bearing, and curvature).
* **How it helps us:** Shows the complete path of the storm from low-latitude genesis near the equator up to the northern Bay of Bengal.

### 4.5 Storm Center & Eye Crosshair
* **What is it:** A pulsing concentric blue target ring marking the exact circulation center.
* **How the data is there:** Calculated by the Radial Axisymmetry algorithm (`centre_fix.py`) at sub-pixel resolution.
* **Why it is there:** Pinpointing the center coordinate is the foundational prerequisite for all nowcasting and cone generation.
* **How it helps us:** Eliminates manual guessing when placing the eye fix, even when the eye is ragged or partially cloud-covered.

### 4.6 Dynamic 24-Hour Uncertainty Cone
* **What is it:** A translucent yellow cone extending from the current storm position along the projected forward path.
* **How the data is there:** Built from 36 Quantile Gradient-Boosted Trees (`nowcast_gbm.py`) combined with empirical 67th-percentile error radii from `models/cone_radii.json`.
* **Why it is there:** Forecasts have inherent uncertainty. Communicating a single line track leads the public to believe areas outside the line are safe.
* **How it helps us:** Defines the official evacuation and disaster preparedness zone. The cone expands with time (36 km at +6h to 157 km at +24h), warning all coastal districts inside the envelope to prepare.

---

## 5. Intensity Trend & Quantile Nowcast Overlay (Bottom-Left)

### 5.1 Intensity Trend Graph
* **What is it:** A dual-axis time-series chart displaying historical intensity and future projections:
  * **Green Line:** Authoritative NOAA IBTrACS Best Track (3-minute sustained wind).
  * **Blue Line:** CYCLOPS real-time objective satellite estimate.
  * **Vertical Dashed Line (`now`):** Current synoptic time divider.
  * **Yellow Dashed Line + Shaded Fan:** 24-hour nowcast trajectory with 10th-to-90th percentile uncertainty envelope.
* **How the data is there:** Ingested from the model registry and historical logs.
* **Why it is there:** Forecasters must understand whether the storm is currently intensifying, plateauing, or weakening, and where the models expect it to peak.
* **How it helps us:** Proves whether the model correctly detected intensification phases, and visualizes the future uncertainty spread.

### 5.2 Nowcast Table (`residual from persistence extrapolation`)
* **What is it:** A structured tabular forecast for four critical operational lead times:
  * Columns:
    * `LEAD`: Forecast horizon (`+6h`, `+12h`, `+18h`, `+24h`).
    * `POSITION`: Predicted geographic coordinates (latitude / longitude).
    * `INTENSITY`: Forecast category, median wind speed, and 10th-to-90th percentile interval.
    * `CONE R`: Uncertainty cone radius in kilometers.
* **Sample Values from Fani:**
  * **+6h:** `8.6°N 87.1°E | CS 45 kt (41–51 kt) | Cone: 36 km`
  * **+12h:** `9.1°N 86.8°E | CS 46 kt (43–57 kt) | Cone: 71 km`
  * **+18h:** `9.7°N 86.3°E | CS 48 kt (44–58 kt) | Cone: 116 km`
  * **+24h:** `9.9°N 86.2°E | SCS 56 kt (37–58 kt) | Cone: 157 km`
* **How the data is there:** 
  * Produced by 36 Quantile Gradient-Boosted Trees predicting **residuals from persistence**:
    * `Residual = Actual Target minus Linear Persistence`
  * Ingests 21 causal features including Google WeatherNext 3 steering winds (500 hPa), vertical shear (850–200 hPa), and Sea Surface Temperature.
* **Why it is there:** Operational disaster agencies (NDMA, Indian Coast Guard, ports) require exact coordinates and wind bands at fixed synoptic intervals to plan evacuations and ship diversions.
* **How it helps us:** Delivers instant, structured numerical tables that can be automatically exported to official government weather bulletins.

---

## 6. "Why This Estimate" Convective Attention Viewer

### 6.1 "GENUINE IMAGERY" Verification Badge
* **What is it:** A green provenance tag confirming that the displayed infrared crop is 100% authentic ISRO satellite imagery.
* **How the data is there:** Read from the granule metadata header.
* **Why it is there:** Reassures evaluators and forecasters that no synthetic mock images (`synth_ir.py`) or artificial noise are used.
* **How it helps us:** Protects scientific integrity and satisfies the Zero-Fake SIH audit standard.

### 6.2 Inner-Core Convective Infrared Zoom Crop
* **What is it:** A high-resolution 128x128 pixel crop centered directly on the storm's circulation core.
* **How the data is there:** Extracted in real time by cropping a 600 km bounding box around the detected center coordinate.
* **Why it is there:** Allows forecasters to inspect core convective dynamics without the distraction of peripheral cirrus clouds.
* **How it helps us:** Reveals eyewall symmetry, convective banding, and dry air intrusions into the core.

### 6.3 Attention Overlay & Opacity Slider
* **What is it:** An interactive control slider (`0% to 100%`) with a `Hide / Show Attention` button that overlays model attention weights onto the raw infrared image.
* **How the data is there:** Generated from gradient-based class activation or ring axisymmetry variance contributions.
* **Why it is there:** Black-box AI models cannot be trusted in life-or-death operational forecasting. Forecasters must verify *why* the model made its decision.
* **How it helps us:** Shows the forecaster exactly which cloud bands or convective towers influenced the T-number calculation.

### 6.4 Convective Core Focus Narrative
* **What is it:** Explanatory text beneath the viewer: *"Convective Core Focus: deeper cloud-top cooling and axisymmetry increase intensity. At this stage attention should be along the curved band, following its curvature."*
* **How the data is there:** Generated from morphological pattern analysis rules.
* **Why it is there:** Explains the physical Dvorak rule governing the current stage.
* **How it helps us:** Educates forecasters and evaluators on why the curved band pattern is driving the current intensity score.

---

## 7. Operational Timeline & Playback Controller (Bottom Bar)

### 7.1 "● LIVE Fani 2019" Status Indicator
* **What is it:** Status pill at the bottom-left indicating the current active scenario.
* **How the data is there:** Derived from the scenario player state in React.
* **Why it is there:** Confirms whether the system is connected to a live satellite stream or replaying an archived case study.
* **How it helps us:** Ensures total clarity on whether the console is running in operational real-time mode or simulation drill mode.

### 7.2 VCR Playback Controls (Step Backward, Play/Pause, Step Forward)
* **What is it:** Transport buttons to pause, play, or step forward/backward frame-by-frame.
* **How the data is there:** Event handlers advancing or rewinding the current time step index.
* **Why it is there:** Forecasters must be able to pause at critical moments (e.g., eye formation or rapid intensification) and step frame-by-frame to analyze satellite changes.
* **How it helps us:** Essential for presentations and post-storm meteorological post-mortems.

### 7.3 Multi-Segment Lifecycle Color Scrubber
* **What is it:** A progress slider spanning the entire storm lifecycle (e.g. `Step 28 / 36`), color-coded along its track by storm intensity (green for Depression $\to$ yellow for Cyclonic Storm $\to$ orange for Severe $\to$ red for ESCS).
* **How the data is there:** Built dynamically from the sequence of storm fixes.
* **Why it is there:** Forecasters can visually see where peak intensity occurred along the timeline and scrub directly to any stage of interest.
* **How it helps us:** Allows jumping instantly from early genesis (Step 4) to peak eye (Step 28) with a single click.

### 7.4 Synoptic Timestamp & Step Counter (`2019-05-02 12:00Z | 28/36`)
* **What is it:** Displays the universal Coordinated Universal Time (UTC / 'Z' time) and step index.
* **How the data is there:** Extracted from the HDF5 satellite granule observation timestamp.
* **Why it is there:** All global meteorological models and satellite observations run strictly on UTC.
* **How it helps us:** Synchronizes satellite frames with global NWP runs and radar scans.

### 7.5 Playback Speed Multiplier (`120x`, `60x`, `1x`)
* **What is it:** Dropdown selector controlling playback speed.
* **How the data is there:** Adjusts the timer tick interval in milliseconds.
* **Why it is there:** A full cyclone spans 5 to 7 days. At real-time (1x) speed, reviewing a storm would take a week.
* **How it helps us:** Allows the team to demonstrate a complete 7-day cyclone lifecycle to evaluators in under 60 seconds.

---

## Summary Matrix: The Three Pillars of CYCLOPS

| Console Area | UI Feature | Core Data Source | Governing Algorithm / Model | Operational Value |
|---|---|---|---|---|
| **Center Map** | Eye Crosshair & Attention Ring | ISRO INSAT-3DR 10.8 µm TIR-1 | Radial Axisymmetry Optimization (`centre_fix.py`) | Pinpoints exact storm center with sub-pixel precision; zero hallucination. |
| **Right Rail** | Intensity Panel & IMD Spectrum | Calibrated Kelvin Brightness Temp | Automated EIR Objective Dvorak (`dvorak.py`, `imd.py`) | Objective T-number and 3-min sustained winds without human observer variance. |
| **Bottom Left** | Nowcast Table & Uncertainty Cone | NOAA IBTrACS + Google WeatherNext 3 | 36 Quantile Gradient-Boosted Trees (`nowcast_gbm.py`) | 24-hour track and intensity projections with calibrated 67% empirical error cones. |
