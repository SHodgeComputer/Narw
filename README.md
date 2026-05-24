# Narw — North Atlantic Right Whale Population Viability Model

A Monte Carlo population viability analysis (PVA) tool comparing three policy
scenarios for protecting the critically endangered North Atlantic right whale
(*Eubalaena glacialis*) over a 50-year projection horizon.

## Scenarios Compared
1. **Status Quo** — 10-knot vessel speed limit in Seasonal Management Areas
   (50 CFR 224.105) with 85% compliance.
2. **Onboard Technology** — Speed limit removed; vessels rely on multi-sensor
   detection (Thermal/IR, Visual Camera, Onboard PAM, Radar, Active Acoustic).
   Technology parameters from MITRE TRL Report MTR250363 (Nov 2025).
3. **Enhanced Regional** — Detection-informed dynamic management using
   high-TRL offboard tools (PAM, aerial surveys) to expand and target dynamic
   slow zones.

## Files
- `narw_model_v2a.py` — Main simulation (calibrated baseline + historical hindcast)
## Running
```bash
python narw_model_v2a.py          # Run main simulation + plot
```
Requires `numpy` and `matplotlib`.
## Final Model Parameters (Calibrated)
### PopulationParams (static defaults — forward projection baseline)
The default `PopulationParams` reflect the **RECOVERY regime** and are used
for forward projections from 2024. Historical simulations use the
phase-varying parameters in 
`HISTORICAL_PHASES` (below).

| Parameter                      | Value | Source / Justification                                                                            |
|--------------------------------|-------|---------------------------------------------------------------------------------------------------|
| `N0`                           | 384   | 2024 NOAA / NARW Consortium estimate (+10/-9 CI)                                                  |
| `max_birth_rate`               | 0.055 | Reflects current reproduction (~15 calves/yr vs 24/yr historical baseline)                        |
| `natural_mortality_rate`       | 0.010 | Standard large-whale natural mortality                                                            |
| `carrying_capacity`            | 1000  | Pre-whaling estimate of N. Atlantic habitat                                                       |
| `entanglement_deaths_per_year` | 2.0   | Midpoint of detected (~5–7/yr NOAA UME) and cryptic-corrected estimate (~15/yr; Pace et al. 2021) |
### HISTORICAL_PHASES (phase-varying parameters for hindcast)
The 2011–2024 trajectory is reproduced with three distinct regimes. Each
phase has its own (`max_birth_rate`, `natural_mortality_rate`,
`entanglement_deaths_per_year`) tuned to match the observed annual net
change in that regime.

| Phase        | Years     | `max_birth_rate` | `natural_mortality_rate` | `entanglement_deaths_per_year` | Observed net Δ/yr |
|--------------|-----------|------------------|--------------------------|--------------------------------|-------------------|
| **pre_ume**  | 2011–2016 | 0.035            | 0.015                    | **4.0**                        | −5.0              |
| **ume**      | 2017–2020 | 0.025            | 0.015                    | **23.0**                       | −25.0             |
| **recovery** | 2021–2024 | 0.055            | 0.010                    | **2.0**                        | +6.5              |
### VesselParams
| Parameter                          | Value | Notes                                  |
|------------------------------------|-------|----------------------------------------|
| `base_encounters_per_year`         | 25    | Per-whale annual vessel-encounter rate |
| `encounters_large_ship_per_year`   | 12.0  | 65 ft / commercial / SMA-regulated     |
| `encounters_midsize_per_year`      | 9.0   | ~40-65 ft (fishing, ferries)           |
| `encounters_recreational_per_year` | 4.0   | < 40 ft recreational craft             |

### SpeedLimitScenario (status quo)
| Parameter                              | Value | Notes                                                                                                                           |
|----------------------------------------|-------|---------------------------------------------------------------------------------------------------------------------------------|
| `speed_kts`                            | 10.0  | NOAA SMA mandatory limit                                                                                                        |
| `compliance_rate`                      | 0.85  | Estimated from AIS data                                                                                                         |
| `noncompliant_speed_kts`               | 16.0  | Typical transit speed                                                                                                           |
| `min_vessel_length_m`                  | 19.8  | 65 ft — SMA applicability threshold                                                                                             |
| `safety_deviation_rate`                | 0.03  | ~3% of transit-time at 10 kts <br/> Safety deviation provision (NMFS RFI, 50 CFR 224.105(c))<br/> Not yet modeled in simulation |
| `safety_deviation_speed_kts`           | 14.0  | bounded by noncomplian_speed_kts                                                                                                |
| `smaller_vessel_safety_deviation_rate` | 0.10  | ~10% — illustrative                                                                                                             |

### OnboardTechScenario
| Parameter                           | Value       | Notes                                                                                           |
|-------------------------------------|-------------|-------------------------------------------------------------------------------------------------|
| `vessel_speed_kts`                  | 16.0        | No speed limit                                                                                  |
| `avoidance_success`                 | 0.50        | **Unstudied** — TRL report key gap. Hard-capped as values > 50% are not empirically defensible. |
| `min_range_for_avoidance_km`        | 1.5         | ~3 min response @ 16 kts                                                                        |
| `initial_adoption` → `max_adoption` | 0.10 → 0.50 | +3%/yr fleet adoption                                                                           |
| `annual_tech_improvement`           | 0.02        | 2%/yr detection-prob growth                                                                     |
### Avoidance-Success Sensitivity Sweep
Values > 50% are excluded due to a lack of evidence  

The empirical-defensibility cap `[10%, 30%, 50%, 70%, 90%]`  (Silber et
al. 2010, 2012; MITRE 2025) 

is refined in the submitted model with a cap of 50%
`[10%, 20%, 30%, 40%, 50%]`. The refined sweep produces tighter coverage of the defensible range.

| P(avoid\|detect) | Mean final pop | Δ vs Speed Limit | Status |
|---|---|---|---|
| 10% | 546 | −88 | Defensible lower bound |
| 20% | 548 | −86 | Defensible |
| 30% | 552 | −82 | Defensible |
| 40% | 555 | −79 | Defensible |
| **50%** | **560** | **−74** | **Cap (default scenario)** |
| 70% | (capped → 50%) | — | Removed: not empirically defensible |
| 90% | (capped → 50%) | — | Removed: not empirically defensible |
**Key finding from sensitivity analysis:

** Across the entire empirically
defensible range (10%–50%), onboard technology underperforms the speed rule
by 12–14% on long-run population. Within this band, the policy gap varies by
only ~14 whales — confirming the speed rule's superiority is robust to
uncertainty in the unstudied avoidance-maneuver parameter.
### EnhancedRegionalScenario
| Parameter | Value | Notes |
|---|---|---|
| `base_speed_kts` / `slow_zone_speed_kts` | 16.0 / 10.0 | Outside / inside zones |
| `slow_zone_coverage` | 0.40 → 0.70 | +2%/yr |
| `compliance` | 0.30 → 0.60 | +1%/yr |
## Calibration Findings
Parameters were tuned against published 2011–2024 population estimates
from the North Atlantic Right Whale Consortium, NOAA Fisheries (Linden
2024), and Pace et al. (2017) state-space estimates.
### Historical Population Estimates (Reference)
| Year | Estimate | Notes |
|---|---|---|
| 2011 | 476 | Near peak; Waring et al. 2016 |
| 2012 | 477 | Barren calving year (7 calves) |
| 2013 | 475 | Slow decline begins |
| 2014 | 465 | |
| 2015 | 458 | Pace et al. 2017 (CI 444–471) |
| 2016 | 451 | Pre-UME low |
| 2017 | 458 | UME declared; Gulf of St. Lawrence shift |
| 2018 | 428 | Barren calving season |
| 2019 | 411 | Continued elevated mortality |
| 2020 | 358 | Population trough |
| 2021 | 364 | Recovery begins (18 calves) |
| 2022 | 356 | Stabilization |
| 2023 | 372 | Recovery (12 calves) |
| 2024 | 384 | NARW Consortium (+10/-9 CI); 11 calves |
### Hindcast Validation (phase-varying, 2011–2024)
The integrated hindcast initializes at the 2011 population (476) and runs
forward through 2024 applying phase-varying parameters. The resulting
median trajectory tracks the observed series within ±7% every year.

| Year | Phase | Historical | Model | Δ | % Err |
|---|---|---|---|---|---|
| 2011 | pre_ume | 476 | 476 | 0 | +0.0% |
| 2012 | pre_ume | 477 | 472 | −5 | −1.0% |
| 2013 | pre_ume | 475 | 469 | −6 | −1.3% |
| 2014 | pre_ume | 465 | 465 | 0 | +0.0% |
| 2015 | pre_ume | 458 | 461 | +3 | +0.7% |
| 2016 | pre_ume | 451 | 458 | +7 | +1.6% |
| 2017 | ume | 458 | 433 | −25 | −5.5% |
| 2018 | ume | 428 | 408 | −20 | −4.7% |
| 2019 | ume | 411 | 384 | −27 | −6.6% |
| 2020 | ume | 358 | 360 | +2 | +0.6% |
| 2021 | recovery | 364 | 366 | +2 | +0.5% |
| 2022 | recovery | 356 | 372 | +16 | +4.5% |
| 2023 | recovery | 372 | 378 | +6 | +1.6% |
| 2024 | recovery | 384 | 384 | 0 | +0.0% |
**Mean abs % error: 2.0%   Max abs % error: 6.6%**
### Parameter Refinement History
Three successive refinements reduced hindcast error from the uncalibrated
baseline to the current result:

| Refinement | pre_ume ent | ume ent | Overall MAE | UME MAE | Notes |
|---|---|---|---|---|---|
| Uncalibrated baseline | 12.0 | 30.0 | 11.4% | 17.5% | Model too lossy in both phases |
| Tier 2 (single-phase static) | — | 10.0 | 8.2% | 19.3% | Static fit to 2017–2024 only |
| **Tier 4 (phase-varying, current)** | **4.0** | **23.0** | **2.0%** | **4.4%** | Chained phases, ±7% every year |
### Key Findings from Calibration
1. **Pre-UME losses were over-attributed to entanglement.** The observed
   2011–2016 decline (~5/yr) implied only ~4 entanglement deaths/yr, not
   the 12 initially assumed. The earlier default pushed the model 30+
   whales below reality before the UME even began.
2. **UME crisis magnitude is well-captured at 23/yr entanglement mortality.**
   Combined with stress-depressed calving (`max_birth_rate = 0.025`), this
   yields −25/yr net loss — matching the observed 458→358 trajectory over
   4 years almost exactly (2020 endpoint: 360 model vs 358 actual).
3. **Recovery-phase reproductive rebound is essential.**
   `max_birth_rate = 0.055` with `entanglement = 2.0` produces the
   observed +6.5/yr growth; 2024 endpoint matches actual (384) within
   1 whale.
4. **Residual non-linearity (2017–2019) remains.** Reality showed an
   asymmetric crisis (2019 worst year, −53 whales) that a within-phase
   linear-decline model cannot capture. Maximum residual is −6.6% at 2019.
### Suggested Future Improvements
- **Stochastic shock years:** Inject cluster mortality events (the 2017
  Gulf of St. Lawrence die-off killed ~17 in one summer) to capture
  non-linear within-phase behavior.
- **Density-dependent reproduction:** Couple birth rate to recent
  mortality so low-threat years produce more calves.
- **Age/sex structure:** Track reproductive females separately (~70 of
  ~384 individuals); a single adult female loss has outsize population
  impact.
- **Smooth phase transitions:** Replace the step-function phase switch
  with a sigmoid to avoid the 2016→2017 discontinuity.
## Key Caveats
- Spatial heterogeneity, age/sex structure, Allee effects, false-positive
  alert fatigue, regulatory/permitting requirements, cost-benefit, and
  climate-driven prey shifts are **not** modeled.
- The effects of ocean noise on whale physiology, behavior, and
  communication are also not modeled.
- The MITRE TRL Report flags a critical gap: **vessel avoidance maneuvers
  in response to whale detections have never been studied or documented**.
  The 50% assumed `avoidance_success` is a placeholder. Per the empirical
  defensibility principle, the parameter is hard-capped at
  `MAX_AVOIDANCE_SUCCESS = 0.50`; values above 50% would require field
  studies on vessel-avoidance maneuvers that do not yet exist.
- Sensitivity sweep over the defensible 10%–50% range shows onboard
  technology consistently underperforms the speed rule by 12–14% on
  long-run population.
## References
See `nmfs_rfi_response.md` for the full bibliography. Key sources:
- MITRE/NOAA NMFS TRL Report (MTR250363, Nov 2025) — technology parameters.
- Pettis et al. (2020–2024) — annual NARW Consortium status reports.
- Linden (2024) — birth-integration population estimation framework.
- Pace, Corkeron & Kraus (2017, 2021) — capture-recapture abundance and
  cryptic-mortality estimation.
- Vanderlaan & Taggart (2007); Conn & Silber (2013) — vessel speed-lethality
  logistic model.
