# Public Comment on the NMFS Advance Notice of Proposed Rulemaking
## North Atlantic Right Whale Vessel Strike Reduction Rule (50 CFR 224.105)

**Federal Register Docket:** NOAA-NMFS-2026-XXXX (ANPRM, March 2026)

**Submitting Author:** Steven Hodge, shodge@computer.org

**Date:** May 23, 2026

**Comment Period Closes:** June 2, 2026

 ## Executive Summary

The empirical evidence and population-modeling results analyzed support
**retaining and expanding the existing mandatory speed rule** rather than
replacing it with a primarily technology-based or voluntary dynamic
regime. Available detection technologies could augment but not replace
the successful speed rule in a **supportive regulatory architecture**
that:

1. Retains the mandatory 10-knot speed limit in Seasonal Management Areas (SMAs)
2. Extends mandatory speed restrictions to vessels ≥ 35 ft (10.7 m) per the
   2022 Preferred Alternative
3. Layers a mandatory Dynamic Speed Zone (DSZ) program atop static SMAs,
   triggered by TRL-9 offboard detection (PAM, aerial surveys) and delivered
   via real-time electronic notification
4. Codifies a calibrated safety-deviation provision (50 CFR 224.105(c)) with
   class-specific parameters and standardized reporting
5. Funds the unstudied vessel-avoidance-maneuver research gap as a near-term
   agency priority
6. Incentivizes onboard detection technology adoption as a complement, not a
   replacement

The North Atlantic right whale population numbered an estimated **384
individuals at the start of 2024** (NARW Consortium, +10/-9 CI), a modest 7%
recovery from the 2020 trough of 358 but well below biologically safe levels.
Population viability modeling calibrated to the observed 2011–2024 trajectory
(mean absolute error 2.0%) indicates the species has no margin for regulatory
experimentation that depends on unproven detection-and-avoidance assumptions.

---

## 1. Background and Method

### 1.1 The 2008 Speed Rule

Under 50 CFR 224.105, most vessels ≥ 65 ft (19.8 m) piloting through designated
Seasonal Management Areas (SMAs) along the U.S. East Coast must travel at
10 knots or less during specified seasonal periods. National Marine Fisheries Service
(NMFS) implemented the rule in 2008 (73 FR 60173) and removed the five-year
sunset provision in 2013 (78 FR 73726).

### 1.2 The 2008 Voluntary DMA / 2020 Slow Zone Program

Concurrent with the speed rule, NMFS implemented a voluntary Dynamic
Management Area (DMA) program, rebranded as Slow Zones in 2020, requesting
voluntary 10-knot transits when sightings or acoustic detections indicate NARW
aggregations outside SMA boundaries.

### 1.3 Analytical Framework

The analysis that follows uses a Monte Carlo population viability model (`narw_model_v2a.py`)
calibrated to:

- **Population estimates 2011–2024** (NARW Consortium / NOAA Linden 2024 model)
- **MITRE/NOAA TRL Report MTR250363 (Nov 2025)** for technology parameters
- **Vanderlaan & Taggart (2007), Conn & Silber (2013), Lisi et al. (2025)**
  for speed–size–lethality
- **Blondin et al. (2025)** for vessel-class encounter risk apportionment

The model reproduces the observed 2011–2024 trajectory with **mean absolute
error 2.0% and maximum error 6.6%** across three regimes before, during, and after
the North American Right Whale Unusual Mortality Event (UME) between 2017-2020.
The three regimes are labeled pre-UME 2011–2016; UME 2017–2020; recovery 2021–2024.

---

## 2. Findings

### 2.1 Speed-Rule Efficacy

| Period | Documented vessel-strike deaths/serious injuries |
|---|---|
| 1998–2007 (pre-rule) | 12 |
| 2008–2017 (post-rule) | 8 |

Inside-SMA effectiveness has been demonstrated by Laist et al. (2014) and
van der Hoop et al. (2015) — vessel-strike mortalities effectively dropped to
near-zero **inside** active SMAs after 2008. Outside-SMA mortalities continued
at roughly the pre-rule rate, demonstrating that protection is bounded by SMA
geographic and temporal extent rather than whale presence.

The variables of speed and size of the vessel compose the following conditional
probabilities of lethality given that the vessel strikes a North American right whale.
 

| Speed |  Size 20–108 m<br/>P(lethal \| strike),  | Size ≥ 108 m <br/>P(lethal \| strike) |
|---|-------------------------------------------|---------------------------------------|
| 10 kts | **27%**                                   | 86%                                   |
| 14 kts | 73%                                       | 91%                                   |
| 16 kts | **88%**                                   | 93%                                   |

For mid-class commercial vessels, the 10-knot limit converts a strike from
~88% lethal to ~27% lethal — **a 3.3× reduction per encounter**. Large
ocean-going ships (≥ 108 m) operate in a mass-dominated regime in which
speed reductions provide only marginal benefit (Lisi et al. 2025; Kelley et
al. 2021); for these vessels, **routing changes are the only means to protect the population of the whales**.

### 2.2 Compliance Performance

| Regime | Approximate Compliance |
|---|---|
| Mandatory SMA rule (2008–2009) | ~50% |
| Mandatory SMA rule (2018–2019) | **~81%** |
| Voluntary DMA / Slow Zones | **~10–30%** |
| Largest commercial vessels at four SE port entrances | **< 25%** |

The 50–60 percentage-point gap between mandatory and voluntary compliance gives
the strongest empirical evidence **against** replacing the static SMA rule with a
primarily voluntary dynamic regime. Mandatory SMA compliance has steadily
improved (50% → 81%) over the rule's first decade, indicating cultural
normalization. That compliance  **is not at a hard ceiling**.

### 2.3 Detection Technology Maturity (MITRE TRL Report)

| Layer | Technology | TRL | Avg detection<br/> probability | Key limitation |
|---|---|---|--------------------------------|---|
| Onboard | Thermal/IR | 6 | 35%                            | Surface-only; degrades in fog/rain/seas |
| Onboard | Visual Camera | 4 | 8%                             | Daytime only;<br/> AI-training gap |
| Onboard | Radar | 3 | 5%                             | High false-alarm rate |
| Onboard | Active Acoustic | 3 | 9%                             | Range < 1 km; <br/>few NARW studies |
| Onboard | PAM | 3 | 5%                             | Flow noise at speed;<br/> vocalization-dependent |
| **Offboard** | **PAM (regional)** | **9** | n/a (zone trigger)             | **Mature** |
| **Offboard** | **Aerial survey** | **9** | n/a (zone trigger)             | **Mature** |

Combined onboard detection probability:
- Clear daylight: 71%
- Fog/rain: 30%
- Night/poor visibility: 24%

After applying the 1.5 km range-sufficiency filter (the minimum warning distance needed
to maneuver at 16 kts), **effective detection drops to ~35%**. With 50%
assumed avoidance success, **effective per-encounter protection is ~18%** —
substantially below the 73% lethality reduction the speed rule already
delivers for mid-class vessels.

### 2.4 The Avoidance-Maneuver Research Gap

The MITRE report's most consequential finding is that **vessel maneuvers in
response to whale detections have never been studied or documented**. The
model therefore caps assumed avoidance-success probability at
`MAX_AVOIDANCE_SUCCESS = 50%`; values above 50% are not empirically
defensible as field studies do not yet exist. Across the entire
defensible 10%–50% sensitivity range, our simulation shows onboard
technology underperforms the speed rule by **12–14% on long-run population**:

The model emits the conditional probabilities of avoiding a whale once detected
and the projected final population after 50 years and the difference compared to
keeping the current speed limit.

| P(avoid\|detect) | Mean final pop | Δ vs Speed Limit |
|---|---|---|
| 10% | 546 | −88 |
| 20% | 548 | −86 |
| 30% | 552 | −82 |
| 40% | 555 | −79 |
| **50%** (cap) | **560** | **−74** |


The policy gap varies by only ~14 whales across this entire band, indicating
the speed rule's superiority is **robust to uncertainty in the unstudied
avoidance parameter**. This finding holds because the detect-then-maneuver
chain has multiple failure modes (detection probability, range-sufficiency,
decision time, hydrodynamic constraints, deep-draft / low-maneuverability
physics) that speed reduction sidesteps simultaneously — an advantage that
no level of avoidance success in the defensible range can recover.

### 2.5 Parametric Uncertainties Lead to Higher Final Population Means.

* The model optimistically assumes no UMEs that would disrupt the recovery rates.
* The model partitions the historical data into a shorter UME ending 2020 and the recovery period commencing in 2021. NOAA's current endpoint for the UME is set at 2026, therefore the model may produce higher estimates of North Atlantic right whales abundance.



### 2.6 50-Year Population Projections

With recovery-phase parameters (the regime that has held since 2021),
calibrated to reproduce 2011–2024 within 2.0% MAE:

| Scenario | Median final pop | P(quasi-extinction < 50) |
|---|---|---|
| Status-quo Speed Rule | **635** | 0% |
| Onboard Tech (no speed limit) | 560 | 0% |
| Enhanced Regional (DMA + emerging tech) | 583 | 0% |

The status-quo speed rule produces the highest long-run population. Removing
the speed rule and substituting onboard detection technology costs ~75 whales
over 50 years — a 12% reduction. The Enhanced Regional scenario sits between
the two: better than removing the rule, but worse than universal 10-knot
enforcement.



---

## 3. Responses to Specific NMFS RFI Topics

### 3.1 Vessel-Size-Specific Risk Assessment

**Position:** The available evidence argues *against* loosening the rule for
any vessel class.

- **≥ 108 m (≈ 350 ft) ocean-going ships** (Lisi et al. 2025) operate in a
  mass-dominated lethality regime where speed reductions provide diminishing
  returns. Strike probability is also elevated by deep draft (10–15 m) that
  prevents whale dive-avoidance and by stopping distances of 1–2 km that
  preclude evasive maneuvering, thus routing changes and DSZs are the principal avoidance options.
- **20–108 m (65–350 ft) commercial vessels** are in a speed-dominated
  lethality regime where the existing rule provides its largest absolute
  benefit (3.3× per-encounter lethality reduction).
- **< 20 m recreational and small-fishing vessels** are currently exempt but
  contribute documented strike mortality (Laist et al. 2001; Sharp et al.
  2019), particularly to neonates and calves on the SE U.S. calving grounds
  (Montes et al. 2020). Strike risk for this class is severely
  under-quantified due to Automatic Identification System (AIS) coverage gaps that NMFS should address by
  extending AIS carriage requirements to ≥ 35 ft (Blondin et al. 2025
  applied an explicit AIS under-representation correction factor for the
  26–65 ft class of vessls).

**Recommendation:** Extend mandatory speed restrictions to most vessels
 35 ft - 65 feet per the proposed rule  87 FR 46921 proposed in 2022 but withdrawn January 8, 2025.

### 3.2 Alternative Management Areas (Dynamic, Real-Time Notification)

**Position:** Dynamic management should be implemented as a **mandatory layer
over** the existing static SMAs, not as a replacement.

Rationale: voluntary DMA / Slow Zone compliance has remained at 10–30%
despite a decade of outreach, while mandatory SMA compliance has reached 81%.
Replacing the static rule with a voluntary compliance would decrease **the chances of the species survival by
in erasing the 50–60 percentage-point compliance.**

**Specific recommendations:**

1. Make Dynamic Speed Zones **mandatory** when triggered by confirmed visual
   or acoustic detections.
2. Use real-time electronic notification (Whale Alert, AIS broadcast,
   mariner email/SMS). Pilot data suggest a 10–25 percentage-point
   compliance uplift from electronic over passive notification.
3. Set notification latency targets ≤ 6 hours from confirmed detection to
   mariner alert.
4. Continue investing in TRL-9 offboard detection (PAM, aerial surveys) to
   drive zone triggering and improve detection responsiveness toward 0.7+.
5. Define minimum DSZ activation criteria by vessel size class to prevent
   unintended exclusion of smaller, AIS-invisible craft.

### 3.3 Voluntary DMAs / Slow Zones Effectiveness

The voluntary program serves a useful adjunctive role and should be retained
where mandatory measures are not yet feasible. However, its demonstrated
voluntary compliance (10–30%) is too low to serve as a primary management
tool. AIS-based effectiveness studies (2018–2024) consistently show voluntary
measures produce marginal speed-distribution shifts in active zones.

**Recommendation:** Maintain voluntary DMAs / Slow Zones as an adjunct, not a
substitute for the mandatory speed rule. Track compliance via AIS
metrics-of-record published quarterly.

### 3.4 Safety Deviation Provision (50 CFR 224.105(c))

**Position:** Provide greater clarity and operational flexibility while
preserving the core protective intent.

**Specific recommendations:**

1. **Codify objective deviation criteria** to include explicit weather-based
   triggers (Beaufort sea state ≥ 5, sustained winds ≥ 25 kts, demonstrable
   swamping/capsizing/loss-of-steerage hazard) rather than the current
   open-ended "safe maneuvering speed" language.
2. **Standardize deviation reporting** through a 48-hour electronic filing
   requirement to enable longitudinal analysis of deviation rates and
   circumstances.
3. **Differentiate by vessel class.** If the rule is extended to 35–65 ft
   vessels, the deviation rate is expected to be substantially higher
   (~10% vs. ~3% for ≥ 65 ft) due to dynamic-stability and freeboard
   limitations of small craft. This class-specific calibration is essential
   to balance crew safety and whale protection.
4. **Define a maximum deviation speed.** During permissible deviations,
   vessels should not exceed an upper bound (we suggest 14 kts) to retain
   partial lethality reduction even during heavy-weather operation.
5. **Sunset and review.** Build in a 5-year review cycle to assess
   deviation-rate trends against documented strike incidents.

### 3.5 Technological Interventions

**Position:** No onboard technology, individually or combined, can replace
the speed rule at present TRL maturity. Onboard technology should be
incentivized as a **complement** that fills gaps the static rule cannot
reach.

**Highest-leverage near-term interventions (TRL 9, deployable now):**

| Intervention | TRL | Status |
|---|---|---|
| Whale Alert / Whalemap electronic notification scale-up | 9 | Operational |
| Mandatory AIS for 35–65 ft vessels | 9 | Regulatory |
| Expanded PAM + aerial survey coverage | 9 | Operational |
| Mandatory Dynamic Speed Zones triggered by 1–3 above | 9 | Pilot-ready |

**Medium-term interventions (TRL 5–7 with investment):**

| Intervention | TRL | Status |
|---|---|---|
| Thermal/IR onboard cameras as complement to SMA rule | 6 | Demonstrating |
| Real-time bow-mounted detection alerting | 5–6 | Demonstrating |
| Smart routing (AIS + Whalemap + weather fusion) | 6–7 | Pilots underway |


**Long-term R&D priorities:**

| Research priority | Why |
|---|---|
| Avoidance-maneuver field studies | **Closes the single largest model uncertainty** |
| NARW-specific active-acoustic detection validation | Few NARW-specific studies exist |
| Flow-noise mitigation for onboard PAM at speed | Unlocks acoustic detection per vessel |
| Multi-sensor fusion algorithms with quantified false-alarm rates | Enables alert-fatigue management |
| Climate-prey-shift coupled distribution models | Forecasts future SMA boundaries |

**Economic incentives for adoption:** We recommend NMFS coordinate with USCG and Customs
to provide port-fee discounts, reduced inspection burdens, or insurance
credits for vessels equipped with multi-sensor detection systems and
operating in high-risk corridors, while maintaining the speed rule as the
mandatory baseline.

---

## 4. Recommended Hybrid Regulatory Architecture

```text path=null start=null
                  ┌────────────────────────────────────────┐
                  │  HYBRID NARW VESSEL-STRIKE FRAMEWORK   │
                  └────────────────────────────────────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
       ┌────────▼─────────┐    ┌───────▼────────┐    ┌────────▼─────────┐
       │   STATIC SMAs    │    │  DYNAMIC DSZs  │    │   ONBOARD TECH   │
       │    (mandatory)   │    │   (mandatory)  │    │  (complement)    │
       │   ≥ 35 ft, 10kt  │    │  PAM + Aerial  │    │   Thermal/IR +   │
       │   85% compliance │    │  triggered;    │    │   Multi-sensor;  │
       │   (proven)       │    │  electronic    │    │   incentivized;  │
       │                  │    │  notification  │    │   not mandatory  │
       └──────────────────┘    └────────────────┘    └──────────────────┘
                │                      │                      │
                └──────────────────────┼──────────────────────┘
                                       │
                            ┌──────────▼──────────┐
                            │ SAFETY DEVIATION    │
                            │ Calibrated by class │
                            │ 48-hr e-reporting   │
                            │ Max 14 kts          │
                            └─────────────────────┘
```

**Six-point program:**

1. Retain the mandatory 10-knot SMA rule, expanded to vessels ≥ 35 ft per
   the 2022 Preferred Alternative.
2. Layer mandatory Dynamic Speed Zones triggered by TRL-9 offboard
   detection (PAM, aerial surveys), delivered via real-time electronic
   notification.
3. Codify a calibrated safety-deviation provision with class-specific
   parameters, weather triggers, and standardized 48-hour reporting.
4. Fund the avoidance-maneuver research gap as a near-term agency priority.
5. Incentivize onboard technology adoption as a complement, not a
   substitute.
6. Maintain voluntary DMAs / Slow Zones as an adjunct in unregulated areas
   while the mandatory framework expands.

---

## 5. Closing Statement

The North Atlantic right whale population reached an estimated **384
individuals at the start of 2024** — a 7% recovery from the 2020 trough of
358 but well below the levels needed for resilience against climate-driven
prey shifts, episodic mortality events (such as the 2017 Gulf of St.
Lawrence crisis), and stochastic environmental variability. Population
viability modeling indicates that **only sustained recovery-phase
parameters** (low entanglement mortality, elevated calving rate, low strike
mortality) yield positive 50-year trajectories under any management
scenario.

Weakening the speed rule's mandatory scope or compliance reach lead to risks
of declining population to UME-era rates, losing approximately 25
whales per year — an unrecoverable trajectory for a population of this
size.

The species has no margin for regulatory experimentation that depends on
unproven detection-and-avoidance assumptions. We urge NMFS to **retain the
speed rule's protective effect, expand its scope to more vessel classes,
layer mandatory dynamic zones on top, and treat technology as a complement
that fills gaps the static rule cannot reach**.

Respectfully submitted,

**[Submitter name]**
[Affiliation]
[Email] · [Phone] · [Mailing address]

---

## References

1. Blondin, H., Garrison, L. P., Adams, J. D., Roberts, J. J., Good, C. P.,
   Gahm, M. P., Lisi, N. E., & Patterson, E. M. (2025). Vessel strike
   encounter risk model informs mortality risk for endangered North
   Atlantic right whales along the United States east coast. *Scientific
   Reports* 15: 736. doi:10.1038/s41598-024-84886-z

2. Conn, P. B. & Silber, G. K. (2013). Vessel speed restrictions reduce
   risk of striking the endangered North Atlantic right whale. *Ecosphere*
   4(4):43. doi:10.1890/ES13-00004.1

3. Crum, N., Gowan, T., Krzystan, A., & Martin, J. (2019). Quantifying risk
   of vessel strike on right whales using a discrete-time Cormack-
   Jolly-Seber model. *Ecosphere* 10(7): e02780.

4. Garrison, L. P., Adams, J., Patterson, E. M., & Good, C. P. (2022).
   Assessing the risk of vessel strike on North Atlantic right whales.
   *Endangered Species Research* 47: 117–135.

5. Kelley, D. E., Vlasic, J. P., & Brillant, S. W. (2021). Assessing the
   lethality of ship strikes on whales using simple biophysical models.
   *Marine Mammal Science* 37(1): 251–267.

6. Laist, D. W., Knowlton, A. R., Mead, J. G., Collet, A. S., & Podesté, M.
   (2001). Collisions between ships and whales. *Marine Mammal Science*
   17(1): 35–75.

7. Laist, D. W., Knowlton, A. R., & Pendleton, D. (2014). Effectiveness of
   mandatory vessel speed limits for protecting North Atlantic right
   whales. *Endangered Species Research* 23: 133–147.

8. Linden, D. W. (2024). Population size estimation of North Atlantic right
   whales from 1990–2023. NOAA Technical Memorandum.

9. Lisi, N. E., Good, C. P., Garrison, L. P., Gahm, M., Patterson, E. M., &
   Blondin, H. (2025). The effects of vessel speed and size on the
   lethality of strikes of large whales in U.S. waters. *Frontiers in
   Marine Science* 11: 1467387. doi:10.3389/fmars.2024.1467387

10. Kirsch, C. C., Weber, T., & Adams, M. MITRE Corporation (2025). Technology Readiness Level Report (TRL) for 
    North Atlantic Right Whale Detection and Vessel Strike Risk Reduction. MTR250363. November 2025

11. Montes, N. L., Swett, R., & Gowan, T. A. (2020). Risk of encounters
    between North Atlantic right whales and recreational vessel traffic
    in the southeastern United States. *Ecology and Society* 25(4):12.
    doi:10.5751/ES-11923-250412

12. NMFS. (2020). North Atlantic Right Whale Vessel Speed Rule Assessment.
    NOAA Office of Protected Resources, June 2020.

13. NMFS. (2022). Draft Environmental Assessment for Amendments to the
    North Atlantic Right Whale Vessel Strike Reduction Rule. NOAA Office
    of Protected Resources, July 2022.

14. Pace, R. M. III, Corkeron, P. J., & Kraus, S. D. (2017). State–space
    mark–recapture estimates reveal a recent decline in abundance of
    North Atlantic right whales. *Ecology and Evolution* 7(21): 8730–8741.

15. Pace, R. M. III, Williams, R., Kraus, S. D., Knowlton, A. R., & Pettis,
    H. M. (2021). Cryptic mortality of North Atlantic right whales.
    *Conservation Science and Practice* 3(2): e346.

16. Sharp, S. M., McLellan, W. A., Rotstein, D., et al. (2019). Gross
    and histopathologic diagnoses from North Atlantic right whale
    *Eubalaena glacialis* mortalities between 2003 and 2018. *Diseases of
    Aquatic Organisms* 135(1): 1–31.

17. Silber, G. K., Slutsky, J., & Bettridge, S. (2010). Hydrodynamics of a
    ship/whale collision. *Journal of Experimental Marine Biology and
    Ecology* 391(1–2): 10–19.

18. Silber, G. K., Vanderlaan, A. S. M., Tejedor Arceredillo, A., Johnson,
    L., Taggart, C. T., Brown, M. W., Bettridge, S., & Sagarminaga, R.
    (2012). The role of the International Maritime Organization in
    reducing vessel threat to whales: process, options, action and
    effectiveness. *Marine Policy* 36(6): 1221–1233.

19. Vanderlaan, A. S. M. & Taggart, C. T. (2007). Vessel collisions with
    whales: the probability of lethal injury based on vessel speed.
    *Marine Mammal Science* 23(1): 144–156. doi:10.1111/j.1748-7692.2006.00098.x

20. van der Hoop, J. M., Vanderlaan, A. S. M., Cole, T. V. N., Henry, A.
    G., Hall, L., Mase-Guthrie, B., Wimmer, T., & Moore, M. J. (2015).
    Vessel strikes to large whales before and after the 2008 Ship Strike
    Rule. *Conservation Letters* 8(1): 24–32.

---

## Appendix A — Population Viability Modeling Methodology

The quantitative claims in this comment are supported by a Monte Carlo
population viability model implemented in `narw_model_v2a.py`. Key
methodological elements:

- **Demographic structure:** Logistic births capped by carrying capacity
  K=1000; binomial natural and entanglement mortality; Poisson encounter
  and strike processes.
- **Strike lethality:** Three-regime function (`strike_lethality`) following
  Lisi et al. (2025) with vessel-size-class branches: ≥ 108 m
  (mass-dominated), 20–108 m (Vanderlaan & Taggart 2007 logistic),
  < 20 m (right-shifted recreational).
- **Strike probability:** Linear-in-speed term with multiplicative draft and
  maneuverability modifiers (`strike_probability_given_encounter`)
  parameterized from Blondin et al. (2025).
- **Hindcast calibration:** Phase-varying parameters (pre-UME 2011–2016,
  UME 2017–2020, recovery 2021–2024) reproduce the observed NARW
  Consortium / NOAA series within mean absolute error 2.0% and maximum
  error 6.6%.
- **Forward projections:** 50-year horizons starting from 2024 N₀=384, with
  2,000 Monte Carlo runs per scenario.
- **Sensitivity analysis:** Avoidance-success rate swept across the
  empirically defensible range [10%, 20%, 30%, 40%, 50%]. Values above
  50% (`MAX_AVOIDANCE_SUCCESS`) are not reported because the unstudied
  status of vessel-avoidance maneuvers (MITRE 2025) does not support them.
  The cap is enforced via dataclass `__post_init__` so any caller passing
  values > 50% receives the capped value, preventing accidentally
  indefensible runs.

Source code, calibrated parameters, and full reference bibliography are
available at: https://github.com/SHodgeComputer/Narw

