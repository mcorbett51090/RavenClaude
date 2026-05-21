# Adoption diagnostic worksheet — `<partner_name>`

> **What this is.** A fillable worksheet the PSM completes (with `learning-analytics-analyst` providing the signal layer) when a partner's adoption is underperforming and the root cause isn't obvious. Forces enumeration of the candidate diagnoses before any intervention play fires.
>
> **When to fill in.** Adoption signal dropped or never lifted past baseline; new-feature adoption is < peer benchmark; a school/segment within a multi-school partner is the bottom-quartile of an otherwise-healthy partner; mid-implementation engagement stalls.
>
> **Pair with:** [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md) for K-12-specific patterns (what's *expected* to be slow when), and [`../knowledge/partner-health-score-drift.md`](../knowledge/partner-health-score-drift.md) for the score-vs-reality diagnostic.

---

## Section 1 — The signal

- **Adoption metric in question:** `<DAU/MAU, license utilization, feature-X adoption, rostering completeness, etc.>`
- **Current value:** `<value, as of YYYY-MM-DD>`
- **Comparison point:** `<peer-segment median / partner's own 6-mo prior / target>`
- **Gap magnitude:** `<+/- X% vs comparison>`
- **Confidence in the signal itself:** `<high / medium / low>` — is the underlying telemetry trustworthy? See [`../knowledge/rostering-data-quality-typology.md`](../knowledge/rostering-data-quality-typology.md).

## Section 2 — Calendar overlay

- **Where is the partner in their school year?** `<implementation / first-30-days / sustained / pre-renewal / dead-zone>`
- **Is the current dip *expected* per the K-12 arc?** Cross-reference [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md). If yes → consider whether intervention adds value or just creates noise. If no → proceed to root-cause section.

## Section 3 — Candidate root causes (rank by likelihood)

Don't intervene without diagnosing. The same low-adoption signal can have wildly different fixes. Enumerate at least 3:

| Candidate root cause | Evidence for | Evidence against | Test to confirm |
|---|---|---|---|
| **1. Rostering / sync issue** — engagement is fine, the data isn't measuring it | `<users complaining of "I logged in but I'm not in the system">` | `<rostering report shows complete sync>` | Check sync logs + spot-check a user |
| **2. Trainer-the-trainer gap** — features exist but training never landed | `<feature X used by 5%, feature Y (which was trained) by 80%>` | `<all features evenly low>` | Survey teachers on training awareness |
| **3. Curriculum-misfit** — the product solves a problem the partner doesn't have at the relevant grade/subject | `<high-school usage strong, K-5 weak even though K-5 is the buyer's stated priority>` | `<usage is segment-distributed evenly>` | Talk to the curriculum director |
| **4. Champion departure** — the person who drove adoption left | `<usage drop coincides with role change>` | `<champion still in role>` | Profile check (see `partner-profile-curator`) |
| **5. Competing tool** — another vendor's product is doing what we expected to do | `<usage drop coincides with another vendor's deployment>` | `<no competing tool>` | Ask in QBR |
| **6. Calendar-suppression false positive** — the "drop" is the K-12 calendar dead zone (per operating-cadence file) | `<happened during a known dead zone>` | `<happened outside dead zones>` | Wait for end of dead zone; re-measure |
| **7. Feature surface change** — recent release moved or removed the feature the partner was using | `<release date aligns with drop>` | `<no relevant release>` | Release notes audit |
| **8. UX friction** — feature exists, users abandon mid-flow | `<funnel data shows drop-off at step N>` | `<no funnel telemetry>` | Funnel telemetry deep-dive |

## Section 4 — Diagnosis

- **Most likely root cause:** `<from table above>`
- **Confidence:** `<high / medium / low>`
- **Evidence summary (2-3 sentences):** `<...>`
- **Risk if wrong:** `<what's the cost of misdiagnosing? Intervening on the wrong cause may worsen the partner relationship.>`

## Section 5 — Intervention recommendation

- **Recommended play (from `success-playbook-designer`):** `<play name>`
- **Why this play matches this diagnosis:** `<...>`
- **Calendar suppression check:** `<is the partner in a dead zone? If so, defer to end of dead zone.>`
- **Expected outcome + measurement:** `<what signal recovery looks like, in what timeframe>`
- **Escalation path if intervention fails:** `<see cross-functional-partnership-map.md>`

## References

- [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md) — what's expected to be slow when
- [`../knowledge/partner-health-score-drift.md`](../knowledge/partner-health-score-drift.md) — score-vs-reality diagnostic
- [`../knowledge/rostering-data-quality-typology.md`](../knowledge/rostering-data-quality-typology.md) — first-stop for "is the signal trustworthy"
- [`../knowledge/k12-psm-operating-cadence.md`](../knowledge/k12-psm-operating-cadence.md) — dead-zone suppression
- [`../skills/adoption-sequencing-k12.md`](../skills/adoption-sequencing-k12.md) — the broader skill this worksheet operates within
