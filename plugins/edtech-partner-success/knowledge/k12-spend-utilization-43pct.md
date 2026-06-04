---
name: k12-spend-utilization-43pct
description: LearnPlatform / Instructure finding — K-12 districts access ~2,739 tools/year but actively use only ~57%, wasting ~43% of EdTech investment. The year-end impact report is not courtesy; it is the document that protects the partner from being in the 43%. CFOs and superintendents in 2025-26 prioritize impact over volume and demand evidence of effectiveness.
last_reviewed: 2026-06-04
confidence: high
---

# K-12 EdTech spend utilization — the 43%-unused finding

> **Last reviewed:** 2026-06-04. Sources: LearnPlatform / Instructure — *EdTech Top 40 report* (primary, `[high]`); Instructure press release — *Districts more selective amid budget crisis* (`[high]`); Evelyn Learning — *The hidden cost of EdTech sprawl* citing the LearnPlatform data (`[high — secondary]`). Refresh when: (a) the next LearnPlatform / Instructure EdTech Top 40 report ships (annual cadence — typically Q1 release with prior-year data), (b) the underlying methodology changes (LearnPlatform Chrome-extension panel is the data source — methodology shifts would update [`enhancement-k12-signal-taxonomy.md`](enhancement-k12-signal-taxonomy.md) too), or (c) the ESSER-cliff effect on district spending posture normalizes.
>
> **Scope.** Why year-end impact reporting is a *renewal-defense* artifact, not a courtesy artifact. The renewal-motion sequence itself lives in [`k12-renewal-motion-90-60-30.md`](k12-renewal-motion-90-60-30.md); the year-end impact report template lives at [`../templates/k12-year-end-impact-report.md`](../templates/k12-year-end-impact-report.md).

---

## 1. The numbers

| Metric | Value | Source |
|---|---|---|
| Distinct software applications accessed per district per year | **~2,739** (range ~2,739-2,982 across years) | LearnPlatform / Instructure EdTech Top 40 `[high]` |
| Fraction of those actively used | **~57%** | LearnPlatform / Instructure `[high]` |
| EdTech investment wasted (unused tools) | **~43%** | LearnPlatform / Instructure, per Evelyn Learning citation `[high]` |

LearnPlatform's own framing of the implication:

> "As districts grapple with mounting financial pressures, leaders are prioritizing impact over volume and demanding evidence of effectiveness and long-term value from every tool they adopt." — Instructure / LearnPlatform 2025 `[high — primary]`

---

## 2. The structural risk this represents to your renewal

**You don't know which side of 57/43 you're on until renewal — unless you produce evidence first.**

The 43% is not random. It accumulates by mechanism:

1. **Pilot-never-scaled.** A district piloted a tool with one department or one school; never rolled out broader; the license is still active. Looks like adoption in your CRM; reads as waste in the district's audit.
2. **Champion-departure-after-purchase.** The signer left; the successor never knew the tool was theirs to use; the line item lives on inertia until the next contract review.
3. **Feature-overlap.** The district bought your tool *and* an adjacent tool; the use cases overlapped; one of them is now the default. If yours isn't the default, you're in the 43%.
4. **Onboarding-failure-never-recovered.** Implementation hit a rostering / SSO / training failure; the district never re-launched; the tool sits dormant.
5. **Outcome-never-measured.** The district can't tell whether the tool worked, so the CFO defaults to "cut if uncertain" at the next budget review.

Mechanisms 1, 2, 4, and 5 are detectable by the PSM **months before** they show up in a renewal conversation. Mechanism 3 is what the EBR's competitive-positioning slide exists for.

---

## 3. Why the year-end impact report is renewal-defense

**The year-end impact report is the artifact the superintendent or board can reference to defend the line item.** Without it, the district's audit conversation about the 43% includes your tool — by default, because there's no evidence to the contrary.

With it, the conversation is:

> "Vendor X showed us 47 of 52 schools hit ≥X minutes/student/week; reading-level growth was 1.3 grade-levels on cohort A; family activation hit 89% (above the 75-90% [Edsby benchmark](https://www.edsby.com/school-apps-for-parent-engagement-k12-data/commentary/)). They are in the 57%, not the 43%. Renew."

The report needs to do three things — none of them optional:

1. **Tie measured outcomes to the district's stated success criteria** (the ones established in onboarding; refreshed at the 180-day checkpoint). Not the vendor's preferred metrics.
2. **Provide comparative framing** — within-district (47 of 52 schools), within-cohort (vs. peer districts), within-history (vs. last year's baseline). One of these three at minimum; ideally all three.
3. **Speak SETDA's 5 Quality Indicators language** (Safe / Evidence-Based / Inclusive / Usable / Interoperable — see [`setda-quality-indicators-procurement-language.md`](setda-quality-indicators-procurement-language.md)) so the academic-side champion can translate the report directly to the board narrative.

A report that does the first two without the third is functional. A report that does the third without the first two is marketing. A report that does all three is renewal-defense.

---

## 4. The bottom-quartile case — when the report would prove you ARE in the 43%

**Hard rule.** If the partner is bottom-quartile on adoption / outcomes by your own measurement, a year-end impact report that papers over that is worse than no report — it surfaces in the next year's audit as "vendor sent a report claiming X; usage data showed Y."

The bottom-quartile case requires a different artifact: a **recovery + restart plan** (not an impact report), routed through the recovery-play designer. The honest framing — "year 1 didn't land for these reasons; here's the restart plan we co-author with the district" — is more renewable than a defensive impact report. The district's CFO recognizes both.

See [`partner-health-decline-which-play.md`](partner-health-decline-which-play.md) for the play-selection traversal; route SUPPRESS → IMPL → SPONSOR → RECOVERY_THEN_RENEW before defaulting to a renewal-prep impact report.

---

## 5. The PSM's calendar discipline

The year-end impact report has a **hard delivery deadline**: before the district scatters in late June. The two dead zones (per [`k12-renewal-calendar-jan-may.md`](k12-renewal-calendar-jan-may.md)) bracket this:

- **Latest acceptable delivery date:** ~June 15-20 (state-variable; before end-of-year wrap)
- **Drafting starts:** February (120-day checkpoint window per [`k12-renewal-motion-90-60-30.md`](k12-renewal-motion-90-60-30.md))
- **Reviewed with exec sponsor at:** the 90-day EBR (March / early April)
- **Final district-facing delivery:** May / early June, ratified before next-year success plan handoff

A report delivered July 15 is a report no one reads.

---

## 6. What an agent should do differently

- The `partner-success-manager` agent, when running the 120-day checkpoint or drafting the year-end impact report, must **lead with the 43%-unused framing** in internal PSM-RM conversations (it sets the stakes correctly) and **end with the 57%-evidence framing** in district-facing artifacts (it lands the value claim without being smug about peer-vendors' failures).
- The `qbr-composer` agent, when composing the 90-day EBR deck, includes a slide template that previews the year-end impact report structure — the EBR is where the district sees the evidence-stack first, then the report is the durable artifact.
- The `learning-analytics-analyst` agent must surface the **license-utilization metric** (per [`psm-metrics-glossary.md`](psm-metrics-glossary.md)) explicitly — "what % of provisioned seats / licenses / classrooms had ≥N meaningful sessions in the last 90 days" — as the leading indicator of whether the partner is on the 57% or 43% side.
- The `success-playbook-designer` agent maintains a **year-end impact report play** with the SETDA-aligned outcome-evidence structure; the bottom-quartile-detected branch routes to the recovery-restart play instead.

---

## 7. References

- [`k12-renewal-motion-90-60-30.md`](k12-renewal-motion-90-60-30.md) — the 120-day deck-drafting checkpoint
- [`k12-renewal-calendar-jan-may.md`](k12-renewal-calendar-jan-may.md) — the delivery deadline + the two dead zones
- [`setda-quality-indicators-procurement-language.md`](setda-quality-indicators-procurement-language.md) — the procurement vocabulary the report must use
- [`psm-metrics-glossary.md`](psm-metrics-glossary.md) — license-utilization definition + EdTech overlay
- [`partner-health-decline-which-play.md`](partner-health-decline-which-play.md) — when the impact report is the wrong artifact (bottom-quartile / recovery path)
- [`../templates/k12-year-end-impact-report.md`](../templates/k12-year-end-impact-report.md) — the template implementing this discipline
- [`../templates/k12-ebr-template.md`](../templates/k12-ebr-template.md) — the 90-day EBR that previews the report's evidence stack
