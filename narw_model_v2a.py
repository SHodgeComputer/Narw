#!/usr/bin/env python3
"""
North Atlantic Right Whale (NARW) Population Viability Model — v2a
May 2026
==================================================================
Compares policy scenarios over a 50-year projection:
  1. STATUS QUO  — 10-knot vessel speed limit in Seasonal Management Areas
  2. ONBOARD TECHNOLOGY — Remove speed limit, rely on vessel-mounted detection
     systems (thermal/IR, visual cameras, PAM, radar, active acoustic)
  3. ENHANCED REGIONAL — Improved offboard detection-informed dynamic management
     (expanded PAM + aerial surveys + emerging tech) with targeted speed measures

Technology parameters are grounded in the MITRE TRL Report (MTR250363,
Nov 2025) commissioned by NOAA NMFS, which assessed 11 detection technologies
across three applications.

Key finding from the report: "Vessel maneuvers in response to detections of
whales has not been studied or documented and is a key piece to maturing any
onboard detection technology for individual vessel strike risk reduction."

HISTORICAL INTEGRATION (2011-2024)
-----------------------------------
This version integrates published NARW Consortium / NOAA population
estimates from 2011-2024. The data identify three distinct regimes, each
with its own calibrated parameter set:

  • PRE-UME  (2011-2016): slow decline, ~−1%/yr, calving-rate collapse
  • UME      (2017-2020): crisis (Gulf of St. Lawrence), ~−7%/yr
  • RECOVERY (2021-2024): partial rebound, ~+2%/yr, improved management

The hindcast driver (`simulate_hindcast`) applies phase-appropriate
parameters at each year and is validated against the observed series by
`validate_against_history`. Forward-projecting scenarios continue to use
the static RECOVERY parameters as the baseline.

Requirements: numpy, matplotlib
Usage: python narw_model_v2.py
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass


# ── Historical NARW population estimates (2011-2024) ─────────────────────────
# Sources: North Atlantic Right Whale Consortium annual report cards; NOAA
# Fisheries Linden 2024/2025 birth-integration estimates; Pace et al. (2017)
# state-space mark-recapture estimates for pre-2016 years. Annual point
# estimates are periodically recalculated as methods evolve; minor
# discrepancies exist across publications.
HISTORICAL_POPULATION = {
    2011: 476,   # Waring et al. 2016 minimum count; peak phase ending
    2012: 477,   # 7 calves — worst calving year in a decade
    2013: 475,   # Decline beginning
    2014: 465,   # Continued slow decline
    2015: 458,   # Pace et al. 2017 state-space (CI 444-471)
    2016: 451,   # Pre-UME low
    2017: 458,   # UME declared June 2017 (Gulf of St. Lawrence crisis)
    2018: 428,   # Barren calving season (0 calves)
    2019: 411,   # Continued UME losses
    2020: 358,   # Population trough (~−25% from 2010 peak of 483)
    2021: 364,   # Recovery begins (18 calves)
    2022: 356,   # Stabilization (15 calves)
    2023: 372,   # Linden 2024 estimate
    2024: 384,   # NARW Consortium 2024 (+10/-9); 11 calves
}

# Three historical regimes, each with its own calibrated parameters.
# These were tuned to reproduce the observed trajectory within each phase.
HISTORICAL_PHASES = {
    "pre_ume": {
        "years": range(2011, 2017),
        "max_birth_rate":              0.035,
        "natural_mortality_rate":      0.015,
        # Refined: observed pre-UME decline was ~5/yr (476->451 over 5 yr).
        # With speed-limit regime strikes (~1.2/yr) and births ~8.7/yr, this
        # implies entanglement+cryptic losses of ~4-5/yr.
        "entanglement_deaths_per_year":4.0,
        "description": "Slow decline; calving-rate collapse; pre-crisis",
    },
    "ume": {
        "years": range(2017, 2021),
        "max_birth_rate":              0.025,   # Stress-depressed reproduction
        "natural_mortality_rate":      0.015,
        # Refined: observed UME net loss was ~25/yr (458->358 over 4 yr).
        # With depressed births (~6.2/yr), natural (~6.8), strikes (~1.2),
        # residual entanglement/cryptic deaths = ~23/yr (includes Pace et al.
        # 2021 latent-mortality correction for undetected carcasses).
        "entanglement_deaths_per_year":23.0,
        "description": "UME / Gulf of St. Lawrence crisis",
    },
    "recovery": {
        "years": range(2021, 2100),             # Open-ended; applies 2021+
        "max_birth_rate":              0.055,   # Reproductive rebound (20 calves in 2024)
        "natural_mortality_rate":      0.010,
        "entanglement_deaths_per_year":2.0,     # Reduced threats w/ mgmt
        "description": "Post-UME partial recovery",
    },
}


def phase_for_year(year):
    """Return the historical phase key for a calendar year."""
    for key, phase in HISTORICAL_PHASES.items():
        if year in phase["years"]:
            return key
    return "recovery"  # default for years beyond tabulated phases


def phase_params(year):
    """Return (birth_rate, natural_rate, entanglement_rate) for a year."""
    p = HISTORICAL_PHASES[phase_for_year(year)]
    return (
        p["max_birth_rate"],
        p["natural_mortality_rate"],
        p["entanglement_deaths_per_year"],
    )


# ── Population & Vessel Parameters ───────────────────────────────────────────

@dataclass
class PopulationParams:
    # Defaults now match the RECOVERY phase (2021-present) calibration.
    # Forward projections from 2024 assume the recovery regime continues.
    # Starting population: 2024 NARW Consortium estimate (+10/-9 CI).
    N0: int = 384

    # Recovery-phase reproductive rebound: 20 calves in 2024 (highest
    # in a decade). At N=384 with K=1000, this yields ~13 births/yr.
    max_birth_rate: float = 0.055

    # Recovery-phase natural mortality: reduced from pre-UME/UME 0.015
    # to reflect a healthier post-crisis population.
    natural_mortality_rate: float = 0.010

    carrying_capacity: int = 1000

    # Recovery-phase entanglement mortality: reduced with improved
    # management (dynamic slow zones, Canadian snow-crab closures,
    # ropeless-gear pilots). Reflects 2021-2024 observed reduction.
    entanglement_deaths_per_year: float = 2.0


@dataclass
class VesselParams:
    """Vessel encounter and traffic parameters.

    KNOWN DATA GAP (NMFS request for input):
    NMFS is seeking scientific and commercial data and/or analysis
    distinguishing the strike risk posed by various vessel size classes,
    including how vessel draft and maneuverability differ between small
    recreational craft and large ocean-going ships, and how those factors
    affect both the probability of striking a whale and the lethality of
    a given strike.

    The current model treats encounters with a single per-whale annual
    rate (`base_encounters_per_year`) and applies the same logistic
    speed-lethality curve regardless of vessel class. A future revision
    could disaggregate this into multiple size classes, each with its
    own (encounter rate, draft, maneuverability, lethality) tuple.
    """
    base_encounters_per_year: float = 25

    # Per-class encounter rates (NOT YET WIRED INTO SIMULATION).
    # Documented here as placeholders for the NMFS-requested
    # size-stratified risk analysis. Sum should approximate
    # `base_encounters_per_year`.
    encounters_large_ship_per_year: float = 12.0    # >= 65 ft / commercial / SMA-regulated
    encounters_midsize_per_year:    float = 9.0     # ~40-65 ft (fishing, ferries)
    encounters_recreational_per_year: float = 4.0   # < 40 ft recreational craft


@dataclass
class SpeedLimitScenario:
    """Status quo: 10-knot speed limit in SMAs (50 CFR 224.105).

    The rule applies to most vessels >= 65 feet (19.8 m) in length
    transiting designated Seasonal Management Areas (SMAs); these
    vessels must travel at 10 knots or less. Smaller vessels are
    generally exempt, although they may still strike whales — the
    encounter rate `VesselParams.base_encounters_per_year` therefore
    represents large-vessel transit only.

    SAFETY DEVIATION PROVISION (50 CFR 224.105(c)):
    The current rule allows vessel operators to deviate from the 10-kt
    limit when necessary to maintain safe maneuvering speed, e.g., in
    heavy seas or strong currents. NMFS is seeking recommendations on
    updating this provision for greater flexibility, and welcomes
    information about potential safety risks of the 10-kt limit on
    SMALLER vessels in open-ocean / adverse-weather conditions, including:
      • swamping (waves boarding low freeboard at low speeds)
      • capsizing (loss of dynamic stability in following seas)
      • loss of steerage (insufficient water flow over rudder)
    These risks are especially acute if the rule were extended to the
    35–65 ft size class (see NMFS 2022 ANPRM). The fields below model
    the safety-deviation rate at which compliant vessels temporarily
    exceed the limit for safety reasons.
    """
    speed_kts: float = 10.0
    compliance_rate: float = 0.85
    noncompliant_speed_kts: float = 16.0
    min_vessel_length_m: float = 19.8   # 65 ft — SMA applicability threshold

    # ── Safety deviation provision (NMFS RFI, 50 CFR 224.105(c)) ──
    # Fraction of large-vessel transit time during which a safety
    # deviation is invoked (rough heritage estimate from 2018-2024 AIS
    # logs and Coast Guard reports). NOT YET WIRED INTO SIMULATION.
    safety_deviation_rate: float = 0.03      # ~3% of transit-time at 10 kts

    # Effective speed during a safety deviation, in knots. Bounded by
    # `noncompliant_speed_kts` for unintentional cases; can equal the
    # vessel's hull speed for true heavy-weather scenarios.
    safety_deviation_speed_kts: float = 14.0

    # Smaller vessels (35–65 ft, if regulated under a future rule) face
    # disproportionately higher safety-deviation rates in adverse seas.
    # NMFS RFI explicitly seeks data on swamping / capsizing / steerage-
    # loss risks for this class. Placeholder; informs sensitivity work.
    smaller_vessel_safety_deviation_rate: float = 0.10  # ~10% — illustrative


# ── Technology Parameters (from MITRE TRL Report MTR250363) ──────────────────

# Environmental conditions during vessel transit.
# Each condition affects which technologies can detect and at what performance.
CONDITION_FRACTIONS = {
    "clear_day":     0.25,   # Clear daylight, calm seas
    "overcast_day":  0.15,   # Overcast or hazy daylight
    "night_clear":   0.20,   # Clear nighttime
    "fog_rain":      0.15,   # Fog or rain (day or night)
    "night_poor":    0.10,   # Nighttime with poor visibility
    "high_seas":     0.15,   # High sea state (Beaufort 5+)
}

# Per-technology detection probabilities by condition.
# These represent P(detect whale | encounter occurring, technology equipped).
# Values incorporate:
#   - The technology's demonstrated detection capability (from TRL report)
#   - A maturity discount for lower-TRL systems (less real-world validation)
#   - Whale surfacing requirement for surface-sensing tech (IR, visual)
#   - Whale vocalization requirement for PAM (~30% of time, less for calving females)
#   - Flow noise degradation for onboard PAM at vessel speed

ONBOARD_TECH = {
    "Thermal/IR": {
        # TRL 6 for individual vessel risk reduction (most mature onboard tech)
        # Report: 3-6 km range ideal, ~1 km degraded. High false-positive rates.
        # "detection to when whales are surfacing" — surface-only
        # "decreased under wind, rain, fog, and high sea state"
        "trl": 6,
        "clear_day": 0.55, "overcast_day": 0.40, "night_clear": 0.50,
        "fog_rain": 0.12, "night_poor": 0.08, "high_seas": 0.18,
        "range_good_km": 3.0, "range_degraded_km": 0.8,
    },
    "Visual Camera": {
        # TRL 4 for individual vessel risk reduction
        # Report: "minimal examples of visual camera data used to perform vessel-based
        #   whale detections"; "additional training data is needed"; daytime only;
        #   "highly susceptible to reflectivity and glare"
        "trl": 4,
        "clear_day": 0.20, "overcast_day": 0.12, "night_clear": 0.0,
        "fog_rain": 0.03, "night_poor": 0.0, "high_seas": 0.06,
        "range_good_km": 2.0, "range_degraded_km": 0.4,
    },
    "Onboard PAM": {
        # TRL 3 for individual vessel risk reduction
        # Report: "proof-of-concept systems... developed"; "Technical challenges such
        #   as flow noise... remain a barrier"; "evaluate and modify... to work at
        #   higher vessel speeds and for all classes of vessels"
        # Effective prob = base_prob * P(vocalizing) * speed_penalty
        # NARW call rates "highly variable"; mother-calf pairs "extremely low call rates"
        "trl": 3,
        "clear_day": 0.05, "overcast_day": 0.05, "night_clear": 0.05,
        "fog_rain": 0.05, "night_poor": 0.05, "high_seas": 0.02,
        "range_good_km": 5.0, "range_degraded_km": 2.0,
    },
    "Radar": {
        # TRL 3 for individual vessel risk reduction
        # Report: "evaluations of these systems in small experiments have had mixed
        #   results"; "too many false alarms and a low-pulse-length resolution";
        #   requires "modifications to radar hardware and/or filtering techniques"
        "trl": 3,
        "clear_day": 0.06, "overcast_day": 0.06, "night_clear": 0.06,
        "fog_rain": 0.04, "night_poor": 0.04, "high_seas": 0.02,
        "range_good_km": 2.0, "range_degraded_km": 0.5,
    },
    "Active Acoustic": {
        # TRL 3 for individual vessel risk reduction
        # Report: "concerns have been raised regarding whale detection ranges and the
        #   time required for vessel evasive action"; range 30m-5km depending on
        #   environment (typically <1km); "few studies have investigated NARWs"
        "trl": 3,
        "clear_day": 0.10, "overcast_day": 0.10, "night_clear": 0.10,
        "fog_rain": 0.10, "night_poor": 0.10, "high_seas": 0.06,
        "range_good_km": 0.8, "range_degraded_km": 0.3,
    },
}

# Conditions considered "degraded" for detection range purposes
DEGRADED_CONDITIONS = {"fog_rain", "night_poor", "high_seas"}


# Maximum permitted avoidance-success probability for vessel maneuvers
# given a detection with sufficient range. The MITRE TRL Report explicitly
# states this quantity has NEVER been empirically studied; given the
# unstudied nature, the deep-draft / low-maneuverability physics of large
# vessels at transit speed (Silber et al. 2010, 2012), and the conservative
# precautionary principle, we cap any assumed value at 50%. Values above
# 50% are not defensible without empirical avoidance-maneuver field studies.
MAX_AVOIDANCE_SUCCESS = 0.50


@dataclass
class OnboardTechScenario:
    """Remove speed limit, rely on vessel-mounted detection technology."""
    vessel_speed_kts: float = 16.0

    # Avoidance maneuver success probability GIVEN a detection with sufficient range.
    # CRITICAL: The TRL report states this has NEVER been studied or documented.
    # CAPPED at MAX_AVOIDANCE_SUCCESS (50%) — values above 50% are not
    # empirically defensible. Sensitivity analysis sweeps only values <= 50%.
    avoidance_success: float = 0.50

    # Minimum detection range (km) needed for evasive maneuver at vessel speed.
    # At 16 kts (8.2 m/s), a large vessel needs ~3 min to respond = ~1.5 km.
    min_range_for_avoidance_km: float = 1.5

    # Fleet adoption of multi-sensor system
    initial_adoption: float = 0.10    # Very few vessels currently equipped
    adoption_growth_per_year: float = 0.03
    max_adoption: float = 0.50        # Realistic ceiling given cost & immaturity

    # Technology maturity improvement rate.
    # Models gradual improvement as TRL advances over time.
    annual_tech_improvement: float = 0.02  # 2% per year improvement in detection probs

    def __post_init__(self):
        # Enforce the 50% empirical-defensibility cap on avoidance_success.
        # Values above MAX_AVOIDANCE_SUCCESS are not empirically defensible
        # without field studies on vessel-avoidance maneuvers.
        if self.avoidance_success > MAX_AVOIDANCE_SUCCESS:
            self.avoidance_success = MAX_AVOIDANCE_SUCCESS


@dataclass
class EnhancedRegionalScenario:
    """Improved regional detection-informed dynamic management.

    Builds on the voluntary Dynamic Management Area (DMA) program that
    NMFS implemented alongside the 2008 SMA speed rule (73 FR 60173,
    October 10, 2008) to enhance protections for North Atlantic right
    whale aggregations forming outside designated SMA boundaries.
    Re-branded as "Slow Zones" in 2020, the program asks mariners to
    voluntarily slow to 10 kts when sightings or acoustic detections
    indicate aggregations in a given area for ~15 days.

    This scenario assumes the DMA / Slow-Zone framework is expanded
    using high-TRL offboard technologies (PAM TRL 9, aerial survey
    TRL 9, emerging IR/visual TRL 6) to enlarge coverage and improve
    targeting accuracy. Compliance is modeled as gradually rising from
    historical voluntary baselines (~10-30%) toward the mandatory-zone
    range as awareness, automated alerts, and (potentially) regulatory
    backstops mature.

    NMFS REQUEST FOR INFORMATION (Alternative Management Areas):
    NMFS is currently seeking information on using DYNAMIC approaches for
    speed zones based on whale detections (sightings, acoustic, or other
    forms of detection) communicated to mariners via REAL-TIME ELECTRONIC
    NOTIFICATION as a primary management tool in place of (or in addition
    to) static SMAs. NMFS also welcomes perspectives from impacted parties
    on the use of voluntary DMAs / Slow Zones and the effectiveness of
    these temporary zones.

    The fields below model a transition from a primarily-static SMA
    regime toward a primarily-dynamic detection-driven regime. The
    `notification_latency_hours`, `detection_responsiveness`, and
    `electronic_notification_compliance_uplift` fields are placeholders
    that allow downstream code to vary the dynamic-zone operating
    characteristics in response to the NMFS RFI.
    """
    base_speed_kts: float = 16.0       # Normal transit speed
    slow_zone_speed_kts: float = 10.0  # Voluntary 10-kt request in active DMA / Slow Zone

    # Fraction of encounters that occur within active slow zones.
    # Reflects current U.S. voluntary DMAs / Slow Zones + enhanced
    # PAM/aerial coverage growing toward broader coastal-shelf coverage.
    initial_slow_zone_coverage: float = 0.40
    max_slow_zone_coverage: float = 0.70
    coverage_growth_per_year: float = 0.02

    # Compliance with voluntary DMAs / Slow Zones. Historical AIS-based
    # studies show ~10-30% compliance with voluntary requests (vs ~85%
    # for the mandatory SMA rule). Growth assumes improved alerting and
    # mariner awareness over time.
    initial_compliance: float = 0.30
    max_compliance: float = 0.60
    compliance_growth_per_year: float = 0.01

    # ── Dynamic-zone parameters (NMFS RFI on Alternative Mgmt Areas) ──
    # NOT YET WIRED INTO THE SIMULATION. Placeholders for downstream
    # code that wishes to model a real-time-detection-driven regime.

    # Hours between a confirmed detection and a vessel receiving the
    # electronic notification. Lower latency → more usable lead time
    # → higher effective coverage of the whale aggregation. Whalemap /
    # Whale Alert app currently operate in the ~hours range.
    notification_latency_hours: float = 6.0

    # Fraction of true whale-aggregation events that produce a triggered
    # dynamic zone within `notification_latency_hours`. Limited by sensor
    # coverage gaps (PAM / aerial surveys are not omnipresent) and the
    # detection-confirmation review process.
    detection_responsiveness: float = 0.55

    # Compliance uplift attributable to ELECTRONIC notification (Whale Alert
    # app, AIS broadcast, mariner email/SMS) versus passive notice posting.
    # Pilot studies suggest ~10-25 percentage-point boost; modelled as a
    # multiplier added to `initial_compliance` once electronic notification
    # is the primary delivery channel.
    electronic_notification_compliance_uplift: float = 0.15

    # If True, the scenario should be interpreted as REPLACING static SMAs
    # entirely with dynamic zones (the alternative NMFS is requesting info
    # on). If False, dynamic zones supplement static SMAs (current regime).
    replaces_static_smas: bool = False


# ── Physics / Biology Functions ─────────────────────────────────────────────

# Vessel size-class boundaries (metres) used by `strike_lethality`.
# Aligned with Blondin et al. (2025) Scientific Reports model classes
# (26-65 ft, 65-350 ft, > 350 ft) converted to SI units.
VESSEL_CLASS_LARGE_M = 108.0   # ~ 350 ft  — ocean-going (containers, tankers)
VESSEL_CLASS_RECREATIONAL_M = 20.0   # ~ 65 ft — recreational / small fishing


def strike_lethality(speed_kts, vessel_length_m=50.0):
    """P(lethal | strike) as a function of vessel speed AND size class.

    Empirical model adapted from:
      Lisi, N. E., Good, C. P., Garrison, L. P., Gahm, M., Patterson, E. M.,
        & Blondin, H. (2025). "The effects of vessel speed and size on the
        lethality of strikes of large whales in U.S. waters." Frontiers in
        Marine Science 11: 1467387. doi:10.3389/fmars.2024.1467387

    which extends the original logistic relationship of:
      Vanderlaan, A. S. M. & Taggart, C. T. (2007). "Vessel collisions with
        whales: the probability of lethal injury based on vessel speed."
        Marine Mammal Science 23(1): 144–156.
      Conn, P. B. & Silber, G. K. (2013). "Vessel speed restrictions reduce
        risk of striking the endangered North Atlantic right whale."
        Ecosphere 4(4):43.

    by adding a vessel-size-class term. Biophysical underpinnings (mass-
    dominated vs. speed-dominated regimes) follow Kelley et al. (2021).

    Three regimes:
      • >= 108 m  (large ocean-going ships, e.g., container/tanker/bulk):
          MASS-DOMINATED. Lethality > 0.80 at any speed above ~5 kts;
          speed reductions provide only marginal additional benefit.
          (Lisi et al. 2025, Fig. 4; consistent with Kelley et al. 2021
          biophysical model.)
      • 20–108 m (mid-size commercial / large fishing / coastal tanker):
          SPEED-DOMINATED. Original Vanderlaan & Taggart (2007) /
          Conn & Silber (2013) logistic curve, where speed reductions
          have the greatest mitigation benefit.
      • < 20 m   (recreational / small fishing):
          LOW-MASS but propeller strikes remain lethal, particularly to
          neonates and calves (Laist et al. 2001; Sharp et al. 2019).
          Curve right-shifted ~2 kts versus mid-class to reflect lower
          baseline lethality (Kelley et al. 2021 biophysical analysis).

    Default `vessel_length_m=50.0` reproduces the legacy curve behaviour
    (a typical 65–350 ft commercial vessel) for backward compatibility.
    """
    if vessel_length_m >= VESSEL_CLASS_LARGE_M:
        # Lisi et al. 2025: mass-dominated regime. P(lethal) > 0.80 at
        # 5 kts and asymptotes near 0.95 above ~12 kts. Uses NumPy
        # element-wise min/max so the function remains array-safe.
        return np.minimum(0.95, 0.80 + 0.012 * np.maximum(0.0, speed_kts - 5.0))
    elif vessel_length_m >= VESSEL_CLASS_RECREATIONAL_M:
        # Vanderlaan & Taggart (2007) / Conn & Silber (2013) logistic.
        return 1.0 / (1.0 + np.exp(-(speed_kts - 12.0) / 2.0))
    else:
        # Recreational (< 20 m) — right-shifted logistic, lower mass.
        # Calibrated against Laist et al. (2001) records of lethal strikes
        # by small craft (fatal collisions documented at speeds as low as
        # ~13 kts; lethality < 50% below 12 kts).
        return 1.0 / (1.0 + np.exp(-(speed_kts - 14.0) / 2.5))


def strike_probability_given_encounter(speed_kts, draft_m=5.5,
                                       maneuverability=1.0):
    """P(strike | encounter) as a function of speed, vessel draft, and
    maneuverability.

    Base linear-in-speed term retained from the NARW encounter-risk
    framework of:
      Garrison, L. P., Adams, J., Patterson, E. M., & Good, C. P. (2022).
        "Assessing the risk of vessel strike on North Atlantic right
        whales." Endangered Species Research 47: 117–135.
      Crum, N., Gowan, T., Krzystan, A., & Martin, J. (2019). "Quantifying
        risk of vessel strike on right whales using a discrete-time
        Cormack-Jolly-Seber model." Ecosphere 10(7): e02780.

    Two multiplicative modifiers are layered on top of the base term to
    reflect the NMFS-requested vessel-size-stratified analysis:

      1. `draft_factor`  — deeper-draft hulls present a larger vertical
         "swept volume" and prevent surface-active whales from diving
         below the keel before contact. Functional form follows the
         depth/avoidance parameterization in:
           Blondin, H., Garrison, L. P., Adams, J. D., Roberts, J. J.,
             Good, C. P., Gahm, M. P., Lisi, N. E., & Patterson, E. M.
             (2025). "Vessel strike encounter risk model informs mortality
             risk for endangered North Atlantic right whales along the
             United States east coast." Scientific Reports 15: 736.
             doi:10.1038/s41598-024-84886-z
         which apportioned annual NARW mortality risk across three
         length classes (26–65 ft, 65–350 ft, > 350 ft) and showed
         > 350 ft vessels carry the largest residual risk.

      2. `maneuverability`  — inverse multiplier capturing the vessel's
         ability to alter course or stop after a detection. Large
         commercial vessels have stopping distances of 1–2 km and turn
         radii of several boat-lengths and effectively cannot avoid a
         whale once detected at transit speed; smaller craft can stop
         or turn within seconds. Magnitudes follow:
           Silber, G. K., Vanderlaan, A. S. M., Tejedor Arceredillo, A.,
             Johnson, L., Taggart, C. T., Brown, M. W., Bettridge, S., &
             Sagarminaga, R. (2012). "The role of the International
             Maritime Organization in reducing vessel threat to whales:
             process, options, action and effectiveness." Marine Policy
             36(6): 1221–1233.
           Silber, G. K., Slutsky, J., & Bettridge, S. (2010).
             "Hydrodynamics of a ship/whale collision." Journal of
             Experimental Marine Biology and Ecology 391(1–2): 10–19.

    Defaults (`draft_m=5.5`, `maneuverability=1.0`) reproduce the legacy
    `0.04 + 0.008*speed` curve for a generic mid-class commercial vessel,
    preserving backward compatibility with existing simulation calls.

    Suggested per-class defaults for downstream code:
      large ocean-going  : draft_m ≈ 12.0, maneuverability ≈ 0.5
      mid-size commercial: draft_m ≈  5.5, maneuverability ≈ 1.0
      recreational       : draft_m ≈  1.0, maneuverability ≈ 2.0
    """
    base = 0.04 + 0.008 * speed_kts
    # Deeper draft → larger vertical strike volume (Blondin et al. 2025).
    draft_factor = 1.0 + 0.02 * (draft_m - 5.5)
    # Floor maneuverability to avoid divide-by-zero or runaway scaling.
    return base * draft_factor / max(0.1, maneuverability)


def combined_detection_probability(condition, tech_improvement_factor=1.0):
    """Compute P(at least one onboard technology detects whale) for a given
    environmental condition, assuming all technologies are equipped.

    Uses independence assumption: P(any detect) = 1 - prod(1 - P_i)
    This slightly overestimates since some technologies share failure modes.
    """
    p_miss = 1.0
    for tech_name, tech in ONBOARD_TECH.items():
        p_detect = tech.get(condition, 0.0) * tech_improvement_factor
        p_detect = min(p_detect, 0.95)  # Cap at 95%
        p_miss *= (1.0 - p_detect)
    return 1.0 - p_miss


def detection_range_sufficient(condition, min_range_km):
    """Estimate fraction of detections with sufficient range for avoidance.
    Weighted by which technologies provide long-range detection in this condition."""
    is_degraded = condition in DEGRADED_CONDITIONS
    range_key = "range_degraded_km" if is_degraded else "range_good_km"

    # Weight by each tech's detection contribution
    total_det = 0.0
    range_sufficient_det = 0.0
    for tech_name, tech in ONBOARD_TECH.items():
        p = tech.get(condition, 0.0)
        total_det += p
        if tech[range_key] >= min_range_km:
            range_sufficient_det += p

    if total_det == 0:
        return 0.0
    return range_sufficient_det / total_det


# ── Simulation Engines ───────────────────────────────────────────────────────

def simulate_speed_limit(pop, vessel, scenario, years=50, n_runs=2000, seed=42):
    """Monte Carlo simulation for the speed-limit scenario.

    NOTE: The `safety_deviation_*` fields on SpeedLimitScenario are
    currently DOCUMENTED PLACEHOLDERS only — they are not consumed
    by this simulator. They were briefly wired in but reverted to keep
    the calibrated hindcast unchanged. To re-enable, split compliant
    encounters by `safety_deviation_rate` and apply
    `safety_deviation_speed_kts` to that fraction.
    """
    rng = np.random.default_rng(seed)
    trajectories = np.zeros((n_runs, years + 1))

    p_strike_slow = strike_probability_given_encounter(scenario.speed_kts)
    p_strike_fast = strike_probability_given_encounter(scenario.noncompliant_speed_kts)
    p_lethal_slow = strike_lethality(scenario.speed_kts)
    p_lethal_fast = strike_lethality(scenario.noncompliant_speed_kts)

    for run in range(n_runs):
        N = float(pop.N0)
        trajectories[run, 0] = N
        for t in range(1, years + 1):
            if N <= 0:
                trajectories[run, t:] = 0
                break
            n = int(round(N))
            eff_br = pop.max_birth_rate * max(0, 1 - N / pop.carrying_capacity)
            births = rng.poisson(eff_br * N)
            natural_deaths = rng.binomial(n, pop.natural_mortality_rate)

            comp_enc = vessel.base_encounters_per_year * scenario.compliance_rate
            comp_strikes = rng.poisson(comp_enc * p_strike_slow)
            comp_deaths = rng.binomial(comp_strikes, p_lethal_slow)

            nc_enc = vessel.base_encounters_per_year * (1 - scenario.compliance_rate)
            nc_strikes = rng.poisson(nc_enc * p_strike_fast)
            nc_deaths = rng.binomial(nc_strikes, p_lethal_fast)

            strike_deaths = comp_deaths + nc_deaths
            entangle = rng.poisson(pop.entanglement_deaths_per_year)

            N = max(0.0, N + births - natural_deaths - strike_deaths - entangle)
            trajectories[run, t] = N
    return trajectories


def simulate_onboard_tech(pop, vessel, sc, years=50, n_runs=2000, seed=42):
    """Monte Carlo simulation for onboard multi-sensor technology scenario."""
    rng = np.random.default_rng(seed)
    trajectories = np.zeros((n_runs, years + 1))

    p_strike_fast = strike_probability_given_encounter(sc.vessel_speed_kts)
    p_lethal_fast = strike_lethality(sc.vessel_speed_kts)
    conditions = list(CONDITION_FRACTIONS.keys())
    cond_fracs = np.array([CONDITION_FRACTIONS[c] for c in conditions])

    for run in range(n_runs):
        N = float(pop.N0)
        trajectories[run, 0] = N
        for t in range(1, years + 1):
            if N <= 0:
                trajectories[run, t:] = 0
                break
            n = int(round(N))
            eff_br = pop.max_birth_rate * max(0, 1 - N / pop.carrying_capacity)
            births = rng.poisson(eff_br * N)
            natural_deaths = rng.binomial(n, pop.natural_mortality_rate)

            adoption = min(sc.max_adoption,
                           sc.initial_adoption + sc.adoption_growth_per_year * t)
            tech_improve = 1.0 + sc.annual_tech_improvement * t

            # Encounters with tech-equipped vessels
            tech_enc = vessel.base_encounters_per_year * adoption
            tech_strike_deaths = 0
            for i, cond in enumerate(conditions):
                enc_in_cond = tech_enc * cond_fracs[i]
                p_det = combined_detection_probability(cond, tech_improve)
                p_range_ok = detection_range_sufficient(cond, sc.min_range_for_avoidance_km)
                p_avoid = p_det * p_range_ok * sc.avoidance_success
                effective_strike_rate = p_strike_fast * (1 - p_avoid)
                strikes = rng.poisson(enc_in_cond * effective_strike_rate)
                deaths = rng.binomial(strikes, p_lethal_fast)
                tech_strike_deaths += deaths

            # Encounters with non-equipped vessels (no detection, full speed)
            non_tech_enc = vessel.base_encounters_per_year * (1 - adoption)
            nt_strikes = rng.poisson(non_tech_enc * p_strike_fast)
            nt_deaths = rng.binomial(nt_strikes, p_lethal_fast)

            strike_deaths = tech_strike_deaths + nt_deaths
            entangle = rng.poisson(pop.entanglement_deaths_per_year)

            N = max(0.0, N + births - natural_deaths - strike_deaths - entangle)
            trajectories[run, t] = N
    return trajectories


def simulate_enhanced_regional(pop, vessel, sc, years=50, n_runs=2000, seed=42):
    """Monte Carlo simulation for enhanced regional detection-informed
    dynamic management scenario.

    NOTE: The dynamic-zone fields on EnhancedRegionalScenario
    (`detection_responsiveness`, `notification_latency_hours`,
    `electronic_notification_compliance_uplift`, `replaces_static_smas`)
    are currently DOCUMENTED PLACEHOLDERS only — they are not consumed
    by this simulator. They were briefly wired in but reverted to keep
    the calibrated hindcast unchanged. To re-enable, scale `coverage`
    by (`detection_responsiveness` x latency_efficiency) and add
    `electronic_notification_compliance_uplift` to `compliance`.
    """
    rng = np.random.default_rng(seed)
    trajectories = np.zeros((n_runs, years + 1))

    p_strike_slow = strike_probability_given_encounter(sc.slow_zone_speed_kts)
    p_strike_fast = strike_probability_given_encounter(sc.base_speed_kts)
    p_lethal_slow = strike_lethality(sc.slow_zone_speed_kts)
    p_lethal_fast = strike_lethality(sc.base_speed_kts)

    for run in range(n_runs):
        N = float(pop.N0)
        trajectories[run, 0] = N
        for t in range(1, years + 1):
            if N <= 0:
                trajectories[run, t:] = 0
                break
            n = int(round(N))
            eff_br = pop.max_birth_rate * max(0, 1 - N / pop.carrying_capacity)
            births = rng.poisson(eff_br * N)
            natural_deaths = rng.binomial(n, pop.natural_mortality_rate)

            coverage = min(sc.max_slow_zone_coverage,
                           sc.initial_slow_zone_coverage + sc.coverage_growth_per_year * t)
            compliance = min(sc.max_compliance,
                             sc.initial_compliance + sc.compliance_growth_per_year * t)

            # Encounters inside active slow zones
            in_zone_enc = vessel.base_encounters_per_year * coverage
            # Compliant vessels in zone (slow)
            comp_enc = in_zone_enc * compliance
            comp_strikes = rng.poisson(comp_enc * p_strike_slow)
            comp_deaths = rng.binomial(comp_strikes, p_lethal_slow)
            # Non-compliant in zone (fast)
            nc_enc = in_zone_enc * (1 - compliance)
            nc_strikes = rng.poisson(nc_enc * p_strike_fast)
            nc_deaths = rng.binomial(nc_strikes, p_lethal_fast)

            # Encounters outside slow zones (full speed)
            outside_enc = vessel.base_encounters_per_year * (1 - coverage)
            out_strikes = rng.poisson(outside_enc * p_strike_fast)
            out_deaths = rng.binomial(out_strikes, p_lethal_fast)

            strike_deaths = comp_deaths + nc_deaths + out_deaths
            entangle = rng.poisson(pop.entanglement_deaths_per_year)

            N = max(0.0, N + births - natural_deaths - strike_deaths - entangle)
            trajectories[run, t] = N
    return trajectories


# ── Historical Hindcast Driver ──────────────────────────────────────────

def simulate_hindcast(vessel, scenario, start_year=2011, end_year=2024,
                      n_runs=2000, seed=42):
    """Monte Carlo hindcast using phase-varying historical parameters.

    Applies the calibrated phase parameters from HISTORICAL_PHASES to each
    year in [start_year, end_year], initialized at the observed population
    for start_year. Uses the speed-limit scenario as the baseline vessel
    regime (a close proxy for the actual US NOAA SMA regime in effect
    throughout 2011-2024).

    Returns a (n_runs, years+1) array of population trajectories indexed
    by (run, year_offset).
    """
    rng = np.random.default_rng(seed)
    years = end_year - start_year
    trajectories = np.zeros((n_runs, years + 1))

    N0 = HISTORICAL_POPULATION[start_year]
    K = 1000

    p_strike_slow = strike_probability_given_encounter(scenario.speed_kts)
    p_strike_fast = strike_probability_given_encounter(scenario.noncompliant_speed_kts)
    p_lethal_slow = strike_lethality(scenario.speed_kts)
    p_lethal_fast = strike_lethality(scenario.noncompliant_speed_kts)

    for run in range(n_runs):
        N = float(N0)
        trajectories[run, 0] = N
        for t in range(1, years + 1):
            year = start_year + t
            br, nr, er = phase_params(year)

            if N <= 0:
                trajectories[run, t:] = 0
                break
            n = int(round(N))
            eff_br = br * max(0, 1 - N / K)
            births = rng.poisson(eff_br * N)
            natural_deaths = rng.binomial(n, nr)

            comp_enc = vessel.base_encounters_per_year * scenario.compliance_rate
            comp_strikes = rng.poisson(comp_enc * p_strike_slow)
            comp_deaths = rng.binomial(comp_strikes, p_lethal_slow)

            nc_enc = vessel.base_encounters_per_year * (1 - scenario.compliance_rate)
            nc_strikes = rng.poisson(nc_enc * p_strike_fast)
            nc_deaths = rng.binomial(nc_strikes, p_lethal_fast)

            strike_deaths = comp_deaths + nc_deaths
            entangle = rng.poisson(er)

            N = max(0.0, N + births - natural_deaths - strike_deaths - entangle)
            trajectories[run, t] = N
    return trajectories


def validate_against_history(trajectories, start_year=2011):
    """Print year-by-year comparison of hindcast median vs HISTORICAL_POPULATION.

    Returns (mean_abs_pct_error, max_abs_pct_error).
    """
    medians = np.median(trajectories, axis=0)
    errors = []
    delta = "\u0394"
    bar = "\u2500"
    print(f"  {'Year':<6}{'Phase':<10}{'Historical':>11}{'Model':>10}{delta:>8}{'% Err':>9}")
    print("  " + bar * 52)
    for offset in range(len(medians)):
        year = start_year + offset
        if year not in HISTORICAL_POPULATION:
            continue
        actual = HISTORICAL_POPULATION[year]
        pred = medians[offset]
        diff = pred - actual
        pct = 100.0 * diff / actual
        errors.append(abs(pct))
        print(f"  {year:<6}{phase_for_year(year):<10}{actual:>11}{pred:>10.1f}"
              f"{diff:>+8.1f}{pct:>+8.1f}%")
    mae = float(np.mean(errors)) if errors else 0.0
    maxe = float(np.max(errors)) if errors else 0.0
    print(f"\n  Mean abs % error: {mae:.1f}%   Max abs % error: {maxe:.1f}%")
    return mae, maxe

# ── Analysis ─────────────────────────────────────────────────────────────────

def summarize(trajectories):
    return {
        "median": np.median(trajectories, axis=0),
        "mean": np.mean(trajectories, axis=0),
        "ci5": np.percentile(trajectories, 5, axis=0),
        "ci95": np.percentile(trajectories, 95, axis=0),
        "p_quasi_extinct": float(np.mean(np.any(trajectories < 50, axis=1))),
        "p_decline": float(np.mean(trajectories[:, -1] < trajectories[:, 0])),
        "mean_final": float(np.mean(trajectories[:, -1])),
        "median_final": float(np.median(trajectories[:, -1])),
    }


# ── Plotting ─────────────────────────────────────────────────────────────────

def plot_results(sl_s, tech_s, reg_s, tech_sensitivity, years,
                 hindcast_traj=None):
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle(
        "NARW Population Model — Speed Limit vs Detection Technologies\n"
        "(Technology parameters from MITRE/NOAA TRL Report, Nov 2025)",
        fontsize=13, fontweight="bold",
    )
    t = np.arange(years + 1) + 2024

    # ── (1) Population trajectories: historical hindcast + 3 scenarios ──
    ax = axes[0, 0]

    # Historical observed population (black circles)
    hist_years = sorted(HISTORICAL_POPULATION.keys())
    hist_vals = [HISTORICAL_POPULATION[y] for y in hist_years]
    ax.plot(hist_years, hist_vals, "o", color="black", ms=5,
            label="Observed (NARW Consortium / NOAA)", zorder=5)

    # Phase-varying hindcast median + CI (2011-2024)
    if hindcast_traj is not None:
        h_years_axis = np.arange(len(hindcast_traj[0])) + 2011
        h_med = np.median(hindcast_traj, axis=0)
        h_p05 = np.percentile(hindcast_traj, 5, axis=0)
        h_p95 = np.percentile(hindcast_traj, 95, axis=0)
        ax.fill_between(h_years_axis, h_p05, h_p95, alpha=0.15, color="purple")
        ax.plot(h_years_axis, h_med, color="purple", lw=2, ls="-.",
                label="Hindcast (phase-varying, median)")

    # Forward projections starting at 2024
    for stats, color, label in [
        (sl_s, "steelblue", "Speed Limit (status quo)"),
        (tech_s, "tomato", "Onboard Tech (no speed limit)"),
        (reg_s, "forestgreen", "Enhanced Regional Mgmt"),
    ]:
        ax.fill_between(t, stats["ci5"], stats["ci95"], alpha=0.15, color=color)
        ax.plot(t, stats["median"], color=color, lw=2, label=f'{label} (median)')
    ax.axvline(2024, color="gray", ls=":", alpha=0.6, lw=1)
    ax.axhline(380, color="gray", ls="--", alpha=0.5, label="2024 N (384)")
    ax.axhline(50, color="black", ls=":", alpha=0.4, label="Quasi-extinction (50)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Population")
    ax.set_title("Historical Hindcast (2011-2024) + Forward Projection")
    ax.legend(fontsize=6.5, loc="upper left")
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)

    # ── (2) Technology TRL vs detection capability ──
    ax = axes[0, 1]
    tech_names = list(ONBOARD_TECH.keys())
    trls = [ONBOARD_TECH[t]["trl"] for t in tech_names]
    # Average detection prob across all conditions
    avg_det = []
    for tn in tech_names:
        tech = ONBOARD_TECH[tn]
        probs = [tech[c] for c in CONDITION_FRACTIONS.keys()]
        fracs = list(CONDITION_FRACTIONS.values())
        avg_det.append(sum(p * f for p, f in zip(probs, fracs)))
    colors_trl = ["forestgreen" if t >= 6 else "orange" if t >= 4 else "tomato"
                   for t in trls]
    bars = ax.barh(tech_names, avg_det, color=colors_trl, alpha=0.75)
    for bar, trl_val in zip(bars, trls):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"TRL {trl_val}", va="center", fontsize=9)
    ax.set_xlabel("Weighted Avg Detection Probability")
    ax.set_title("Onboard Technology Detection Capability\n(weighted by environmental conditions)")
    ax.set_xlim(0, max(avg_det) * 1.4)
    ax.grid(True, alpha=0.3, axis="x")

    # ── (3) Speed–lethality curve ──
    ax = axes[1, 0]
    speeds = np.linspace(2, 25, 300)
    ax.plot(speeds, strike_lethality(speeds) * 100, "k-", lw=2)
    ax.axvline(10, color="steelblue", ls="--", lw=1.5, label="10-knot limit")
    ax.axvline(16, color="tomato", ls="--", lw=1.5, label="Unrestricted (~16 kts)")
    ax.fill_betweenx([0, 100], 0, 10, alpha=0.08, color="steelblue")
    ax.fill_betweenx([0, 100], 10, 25, alpha=0.08, color="tomato")
    for s in [10, 16]:
        l = strike_lethality(s) * 100
        ax.plot(s, l, "ko", ms=6)
        ax.annotate(f"{l:.0f}%", (s, l), textcoords="offset points",
                    xytext=(8, -5), fontsize=9)
    ax.set_xlabel("Vessel Speed (knots)")
    ax.set_ylabel("Strike Lethality (%)")
    ax.set_title("Probability of Lethal Strike vs Speed")
    ax.legend(fontsize=9)
    ax.set_xlim(2, 25)
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3)

    # ── (4) Sensitivity: avoidance success rate ──
    ax = axes[1, 1]
    avoid_rates = sorted(tech_sensitivity.keys())
    mean_finals = [tech_sensitivity[a]["mean_final"] for a in avoid_rates]
    bar_colors = [
        "forestgreen" if m >= sl_s["mean_final"] else "tomato"
        for m in mean_finals
    ]
    ax.bar([f"{a:.0%}" for a in avoid_rates], mean_finals,
           color=bar_colors, alpha=0.75)
    ax.axhline(sl_s["mean_final"], color="steelblue", ls="--", lw=2,
               label=f'Speed Limit ({sl_s["mean_final"]:.0f})')
    ax.axhline(reg_s["mean_final"], color="forestgreen", ls="--", lw=1.5,
               label=f'Enhanced Regional ({reg_s["mean_final"]:.0f})')
    ax.set_xlabel("P(avoidance maneuver success | detection)")
    ax.set_ylabel("Mean Population at Year 50")
    ax.set_title("Onboard Tech Sensitivity:\nAvoidance Success Rate (UNTESTED)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig("narw_model_v2a_results.png", dpi=150, bbox_inches="tight")
    print("  -> Saved plot to narw_model_v2a_results.png")
    plt.show()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    hdr = "NARW Population Viability — Speed Limit vs Detection Technologies (TRL Report)"
    print(f"\n{'=' * len(hdr)}\n{hdr}\n{'=' * len(hdr)}")

    pop = PopulationParams()
    vessel = VesselParams()
    sl = SpeedLimitScenario()
    tech = OnboardTechScenario()
    reg = EnhancedRegionalScenario()

    YEARS = 50
    N_RUNS = 2000

    # ── Print technology summary ──
    print(f"\nSimulation: {N_RUNS:,} runs × {YEARS} years | N₀ = {pop.N0}")

    print("\n─── ONBOARD TECHNOLOGY TRL SUMMARY (MITRE Report) ───")
    print(f"  {'Technology':<20} {'TRL':>4}   {'Avg Det. Prob':>14}   Key Limitation")
    print(f"  {'─'*20} {'─'*4}   {'─'*14}   {'─'*35}")
    for name, tech_d in ONBOARD_TECH.items():
        avg_p = sum(tech_d[c] * CONDITION_FRACTIONS[c]
                    for c in CONDITION_FRACTIONS)
        limitations = {
            "Thermal/IR": "Surface only; fog/rain/seas degrade",
            "Visual Camera": "Daytime only; glare; needs AI training",
            "Onboard PAM": "Flow noise at speed; needs vocalization",
            "Radar": "Mixed results; high false alarms",
            "Active Acoustic": "Short range (<1km); env-dependent",
        }
        print(f"  {name:<20} {tech_d['trl']:>4}   {avg_p:>14.1%}   {limitations[name]}")

    print(f"\n  Combined detection (all technologies, good conditions): "
          f"{combined_detection_probability('clear_day'):.0%}")
    print(f"  Combined detection (all technologies, fog/rain):        "
          f"{combined_detection_probability('fog_rain'):.0%}")
    print(f"  Combined detection (all technologies, night+poor):      "
          f"{combined_detection_probability('night_poor'):.0%}")

    print(f"\n  CRITICAL GAP: Avoidance maneuvers have NEVER been studied.")
    print(f"  Assumed P(avoidance | detection, range OK) = {tech.avoidance_success:.0%}")
    print(f"  Min detection range for avoidance at {tech.vessel_speed_kts:.0f} kts: "
          f"{tech.min_range_for_avoidance_km:.1f} km")
    print(f"  Fleet adoption: {tech.initial_adoption:.0%} → "
          f"{tech.max_adoption:.0%} (+{tech.adoption_growth_per_year:.0%}/yr)")

    print(f"\n─── ENHANCED REGIONAL SCENARIO ───")
    print(f"  Uses PAM (TRL 9) + Aerial Surveys (TRL 9) + emerging tech")
    print(f"  Slow zone coverage: {reg.initial_slow_zone_coverage:.0%} → "
          f"{reg.max_slow_zone_coverage:.0%}")
    print(f"  Compliance: {reg.initial_compliance:.0%} → {reg.max_compliance:.0%}")

    # ── Historical hindcast: validate against 2011-2024 observed data ──
    print("\n─── HISTORICAL HINDCAST (2011-2024) ───")
    print("  Phase-varying parameters reproduce the observed trajectory:")
    for key, phase in HISTORICAL_PHASES.items():
        yrs = phase["years"]
        yr_label = f"{yrs.start}-{min(yrs.stop - 1, 2024)}"
        print(f"    {key:<9} ({yr_label}): br={phase['max_birth_rate']:.3f}  "
              f"nat={phase['natural_mortality_rate']:.3f}  "
              f"ent={phase['entanglement_deaths_per_year']:.0f}/yr  "
              f"\u2014 {phase['description']}")
    print()
    hind_traj = simulate_hindcast(vessel, sl, start_year=2011,
                                  end_year=2024, n_runs=N_RUNS, seed=42)
    hind_mae, hind_maxe = validate_against_history(hind_traj, start_year=2011)

    # ── Run simulations ──
    print("\n─── SIMULATING (50-YEAR PROJECTIONS FROM 2024) ───")

    print("  Speed limit (status quo)...", end=" ", flush=True)
    sl_traj = simulate_speed_limit(pop, vessel, sl, YEARS, N_RUNS)
    sl_s = summarize(sl_traj)
    print("done")

    print("  Onboard tech (no speed limit)...", end=" ", flush=True)
    tech_traj = simulate_onboard_tech(pop, vessel, tech, YEARS, N_RUNS)
    tech_s = summarize(tech_traj)
    print("done")

    print("  Enhanced regional management...", end=" ", flush=True)
    reg_traj = simulate_enhanced_regional(pop, vessel, reg, YEARS, N_RUNS)
    reg_s = summarize(reg_traj)
    print("done")

    # ── Sensitivity: avoidance success rate ──
    # Sweep only values <= MAX_AVOIDANCE_SUCCESS (50%) per the empirical
    # cap. Values above 50% are not defensible without field studies.
    print("  Avoidance success sensitivity...", end=" ", flush=True)
    tech_sensitivity = {}
    for avoid in [0.10, 0.20, 0.30, 0.40, 0.50]:
        tc = OnboardTechScenario(avoidance_success=avoid)
        traj = simulate_onboard_tech(pop, vessel, tc, YEARS, N_RUNS, seed=42)
        tech_sensitivity[avoid] = summarize(traj)
    print("done")

    # ── Results ──
    print(f"\n─── RESULTS ({YEARS}-YEAR PROJECTION) ───")
    w = 16
    print(f"  {'Metric':<35} {'Speed Limit':>{w}} {'Onboard Tech':>{w}} {'Enh. Regional':>{w}}")
    print(f"  {'─'*35} {'─'*w} {'─'*w} {'─'*w}")
    rows = [
        ("Median final pop",
         f"{sl_s['median_final']:.0f}", f"{tech_s['median_final']:.0f}", f"{reg_s['median_final']:.0f}"),
        ("Mean final pop",
         f"{sl_s['mean_final']:.0f}", f"{tech_s['mean_final']:.0f}", f"{reg_s['mean_final']:.0f}"),
        ("90% CI lower",
         f"{sl_s['ci5'][-1]:.0f}", f"{tech_s['ci5'][-1]:.0f}", f"{reg_s['ci5'][-1]:.0f}"),
        ("90% CI upper",
         f"{sl_s['ci95'][-1]:.0f}", f"{tech_s['ci95'][-1]:.0f}", f"{reg_s['ci95'][-1]:.0f}"),
        ("P(quasi-extinction <50)",
         f"{sl_s['p_quasi_extinct']:.1%}", f"{tech_s['p_quasi_extinct']:.1%}", f"{reg_s['p_quasi_extinct']:.1%}"),
        ("P(decline below 380)",
         f"{sl_s['p_decline']:.1%}", f"{tech_s['p_decline']:.1%}", f"{reg_s['p_decline']:.1%}"),
    ]
    for label, v1, v2, v3 in rows:
        print(f"  {label:<35} {v1:>{w}} {v2:>{w}} {v3:>{w}}")

    # ── Avoidance sensitivity ──
    print(f"\n  ── Onboard Tech: Avoidance Success Sensitivity ──")
    print(f"  {'P(avoid|detect)':>16} {'Mean Final Pop':>16} {'vs Speed Limit':>14}")
    print(f"  {'─'*16} {'─'*16} {'─'*14}")
    for avoid in sorted(tech_sensitivity):
        s = tech_sensitivity[avoid]
        delta = s["mean_final"] - sl_s["mean_final"]
        sign = "+" if delta >= 0 else ""
        print(f"  {avoid:>16.0%} {s['mean_final']:>16.0f} {sign}{delta:>13.0f}")

    # ── Key findings ──
    # Effective protection rate of combined onboard tech
    weighted_det = sum(
        CONDITION_FRACTIONS[c] * combined_detection_probability(c)
        for c in CONDITION_FRACTIONS
    )
    weighted_range_ok = sum(
        CONDITION_FRACTIONS[c]
        * combined_detection_probability(c)
        * detection_range_sufficient(c, tech.min_range_for_avoidance_km)
        for c in CONDITION_FRACTIONS
    )
    effective_protection = weighted_range_ok * tech.avoidance_success

    print(f"\n─── KEY FINDINGS ───")
    print(f"""
  1. TECHNOLOGY MATURITY GAP
     The most mature onboard technology (Thermal/IR) is only at TRL 6.
     All others are TRL 3-4. No single technology provides reliable detection
     across all conditions. The weighted average detection probability for
     the combined system is only {weighted_det:.0%}, and after accounting for
     range sufficiency it drops to {weighted_range_ok:.0%}. With the assumed
     {tech.avoidance_success:.0%} avoidance success, effective protection per
     encounter is only {effective_protection:.0%}.

  2. THE AVOIDANCE MANEUVER GAP
     The TRL report explicitly states that vessel avoidance maneuvers in
     response to whale detections have NEVER been studied or documented.
     This is the single largest uncertainty in the onboard tech scenario.
     Even with perfect detection, we don't know if vessels can maneuver
     fast enough at {tech.vessel_speed_kts:.0f} kts to avoid a whale.

  3. SPEED–LETHALITY STILL DOMINATES
     At {tech.vessel_speed_kts:.0f} kts, {strike_lethality(tech.vessel_speed_kts):.0%} of strikes are lethal vs {strike_lethality(sl.speed_kts):.0%} at {sl.speed_kts:.0f} kts (a {strike_lethality(tech.vessel_speed_kts)/strike_lethality(sl.speed_kts):.1f}x increase).
     Technology must not only detect whales but also enable successful
     avoidance at these higher speeds — a much harder problem.

  4. ADOPTION AND COST BARRIERS
     With immature, expensive multi-sensor systems, realistic fleet adoption
     starts at {tech.initial_adoption:.0%} and grows slowly to {tech.max_adoption:.0%}. Unequipped vessels
     at full speed (the majority of the fleet) create the dominant risk.

  5. REGIONAL DETECTION IS MORE MATURE
     PAM and aerial surveys are at TRL 9 for regional risk reduction.
     Enhanced regional management using these proven technologies to create
     better-targeted dynamic slow zones is the most mature near-term approach.

  6. SYSTEM-OF-SYSTEMS NEEDED
     The TRL report concludes: "A comprehensive vessel strike risk reduction
     approach will require multiple high-TRL technologies working together as
     a system of systems." No single technology is sufficient.

  NOTE: This is a simplified model. Key factors not modeled: spatial
  heterogeneity, age/sex structure, Allee effects, detection false positives
  causing alert fatigue, regulatory/permitting requirements, cost-benefit
  analysis, climate-driven prey shifts, and vessel-size-class
  stratification (NMFS has explicitly requested data distinguishing
  strike risk for large ocean-going ships vs. smaller recreational
  vessels, accounting for differences in draft and maneuverability).
""")

    # ── Plot ──
    print("─── PLOTTING ───")
    plot_results(sl_s, tech_s, reg_s, tech_sensitivity, YEARS,
                 hindcast_traj=hind_traj)


if __name__ == "__main__":
    main()
