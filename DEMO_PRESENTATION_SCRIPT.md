# CYCLOPS: 5-Minute Team Demo Presentation Script
**Target:** Ministry of Earth Sciences (MoES) / India Meteorological Department (IMD)  
**Format:** 4 Speakers | Strictly 5 Minutes (~75 seconds each) | Clean Spoken English  

---

## Quick Reference Timing Summary

| Speaker | Role | Timing | Screen Action |
|---|---|---|---|
| **Speaker 1** | **Overall Architecture & Console** | 0:00 – 1:15 (75s) | Full map view, wind particles, top HUD, data provenance |
| **Speaker 2** | **Identification (Center-Fixing)** | 1:15 – 2:30 (75s) | Storm eye crosshair, Attention Viewer thermal slider |
| **Speaker 3** | **Classification (Objective Dvorak)** | 2:30 – 3:45 (75s) | Intensity panel, ESCS badge, sustained wind, -93.3°C top |
| **Speaker 4** | **Nowcasting (24h Quantile Cone)** | 3:45 – 5:00 (75s) | Forecast table (+6h to +24h), dynamic cone, alert broadcast |

---

## SPEAKER 1: Overall Architecture & Console Walkthrough
* **Duration:** 0:00 – 1:15 (75 Seconds)
* **Goal:** Hook the judges, establish real-world MoES/IMD relevance, and introduce the workstation.

### What to Click / Show on Screen:
1. Open the console at `http://localhost:5180` in full screen.
2. Point out the top header: **Cyclone Fani (ESCS - Extremely Severe Cyclonic Storm)**.
3. Pan across the Bay of Bengal showing the satellite layer and the animated wind streamlines.
4. Point to the right sidebar: Intensity panel, Attention viewer, and Forecast table.

### Spoken Script:
> "Respected judges, welcome to CYCLOPS — our end-to-end meteorological decision-support workstation built for the Ministry of Earth Sciences and the India Meteorological Department.
>
> During a tropical cyclone in the North Indian Ocean, operational forecasters face three high-stakes questions:
> Where is the exact center?
> How intense is the storm right now?
> And where will it strike over the next 24 hours?
>
> CYCLOPS answers all three in real time. Crucially, our system operates on a strict Zero-Fake Data Standard. There are no mock numbers or synthetic sine waves. We ingest genuine ISRO MOSDAC INSAT-3DR 10.8-micrometer thermal infrared granules, NOAA IBTrACS historical best tracks, and Google DeepMind's WeatherNext 3 atmospheric model.
>
> On the screen, you are looking at an offline high-resolution vector basemap. Draped directly over it is the calibrated infrared satellite scan of Cyclone Fani, combined with 1,400 physics-driven wind particles showing asymmetric cyclonic inflow.
>
> In the next three minutes, our team will walk you through the exact engines powering Identification, Classification, and Nowcasting.
>
> I will now hand over to [Speaker 2 Name] for Cyclone Identification."

---

## SPEAKER 2: Identification (Center-Fixing Engine)
* **Duration:** 1:15 – 2:30 (75 Seconds)
* **Goal:** Explain the mathematics of eye detection, sub-pixel accuracy, and noise rejection.

### What to Click / Show on Screen:
1. Point to the center crosshair / eye indicator on the map.
2. Slide the Attention Viewer (thermal focus) back and forth to show concentric cloud organization.
3. Highlight the storm center coordinates badge: (15.48°N, 84.82°E).

### Spoken Script:
> "Thank you. I will now explain our Identification Engine, implemented in our center-fixing module.
>
> Accurately pinpointing the storm center from satellite imagery is notoriously hard when cloud shields obscure the eye. Rather than using fragile edge detection, CYCLOPS uses an optimization method called Radial Axisymmetry.
>
> For every candidate point within the search area, the algorithm samples brightness temperatures in concentric circular rings from 15 kilometers out to 250 kilometers, at 5-kilometer intervals.
>
> It then computes the Axisymmetry Score, S:
>
> Score S = Between-Ring Variance divided by (Between-Ring Variance plus Within-Ring Variance)
>
> Between-ring variance captures the steep temperature drop from the warm eye into the freezing eyewall. Within-ring variance measures azimuthal irregularity or lumpiness along each ring. The coordinate that maximizes this score is mathematically fixed as the circulation center.
>
> When an eye exists, the algorithm refines the position to the local warm brightness peak with sub-pixel precision.
>
> Best of all, if you feed CYCLOPS clear sky or random noise, there is no concentric pattern, the score collapses below 0.15, and the system outputs 'detected: false' with zero false alarms.
>
> Once the center is locked, we pass it to Classification, which [Speaker 3 Name] will now demonstrate."

---

## SPEAKER 3: Classification (Objective Dvorak Technique)
* **Duration:** 2:30 – 3:45 (75 Seconds)
* **Goal:** Explain objective intensity estimation, IMD wind conversion, and convective core thermodynamics.

### What to Click / Show on Screen:
1. Point to the Intensity Panel on the right sidebar.
2. Highlight the IMD Category Badge: ESCS (Extremely Severe Cyclonic Storm).
3. Point to the 3-minute Sustained Wind: 115 to 125 knots, and Coldest Cloud Top: -93.3°C.
4. Point to the 90% Confidence Interval Bar and the comparison with IBTrACS truth.

### Spoken Script:
> "Thank you. Moving to Classification, implemented in our Dvorak module.
>
> Traditional Dvorak analysis relies on manual inspection by human forecasters, which can lead to subjective variance between shifts. CYCLOPS automates the Enhanced-Infrared Objective Dvorak Technique.
>
> First, it analyzes the cloud structure — determining whether the storm presents an Eye pattern, a Central Dense Overcast (CDO), or a Shear pattern.
>
> Second, it extracts thermodynamic measurements directly from physical Kelvin temperatures: for Cyclone Fani, our coldest convective cloud top drops to minus 93.3 degrees Celsius, showing violent updrafts. It measures the diameter of the dense overcast shield colder than minus 70 degrees Celsius.
>
> The raw T-number is computed from:
>
> T-number = 3.5 + (CDO Diameter minus 150) / 100 + Coldest Top Adjustment
>
> Finally, CYCLOPS converts the T-number directly into the official IMD standard — 3-minute sustained wind speed in knots:
>
> Wind Speed in knots = 14.17 multiplied by (T-number raised to the power of 1.12)
>
> For Fani at peak intensity, this yields T6.5, equating to 125 knots, officially classifying it as an Extremely Severe Cyclonic Storm within 5 knots of post-storm ground truth.
>
> Now, [Speaker 4 Name] will present our 24-hour Nowcasting Engine."

---

## SPEAKER 4: Nowcasting (24-Hour Quantile Projections & Cones)
* **Duration:** 3:45 – 5:00 (75 Seconds)
* **Goal:** Explain the ML model, WeatherNext 3 steering flow, persistence residuals, calibrated cones, and alert broadcast.

### What to Click / Show on Screen:
1. Click on the dynamic Uncertainty Cone on the map to show the expanding track swath.
2. Point to the Forecast Table showing the +6h, +12h, +18h, and +24h projections with 10th, 50th, and 90th percentile wind bands.
3. Show the automated bulletin generation badge (ready for NDMA and Navy dissemination).

### Spoken Script:
> "Thank you. Finally, our Nowcasting Engine.
>
> Numerical supercomputer forecasts take 6 to 12 hours to run. CYCLOPS produces instantaneous 24-hour nowcasts using 36 Quantile Gradient-Boosted Decision Trees.
>
> We predict across 4 lead horizons: plus 6, 12, 18, and 24 hours. For each horizon, we forecast 3 physical targets: latitude change, longitude change, and wind speed change, across 3 quantiles: 10th percentile lower bound, 50th percentile median, and 90th percentile upper bound.
>
> The model ingests 21 causal features: storm kinematic momentum, past 6-hour displacement, distance to the coast, and environmental variables from Google DeepMind's WeatherNext 3 — specifically 500 hPa steering winds, 850-to-200 hPa vertical wind shear, and Sea Surface Temperatures.
>
> Instead of unconstrained guessing, our trees predict residuals from linear persistence:
>
> Residual = Actual Target minus Linear Persistence
>
> This guarantees that forecasts obey the physical conservation of momentum.
>
> Our dynamic uncertainty cones are empirically calibrated to 67th-percentile historical errors: 36 km at 6 hours, expanding to 157 km at 24 hours. On held-out validation storms, 68.2 percent of all true track coordinates fell strictly inside our cone, satisfying the operational standard.
>
> Every 30 minutes, CYCLOPS generates machine-readable JSON bulletins ready for immediate broadcast to NDMA, the Indian Navy, and coastal ports.
>
> Thank you, judges. We are now ready for your questions!"

---

## Tips for Presentation Delivery:
1. **Handoffs:** Keep transitions under 2 seconds (e.g., "Passing over to Rahul for Identification").
2. **Synchronized Gestures:** When Speaker 2 says "concentric rings", the person controlling the mouse should circle the eye on screen.
3. **Key Numbers to Remember:**
   * Coldest cloud top: **-93.3°C**
   * Trees: **36 Quantile Decision Trees**
   * Horizons: **+6h, +12h, +18h, +24h**
   * Cone validation coverage: **68.2%** (Target: >= 67%)
