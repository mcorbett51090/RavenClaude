# Higher-ed administration decision trees + capability map

Decision support for the `higher-education-administration` specialists. Traverse top-to-bottom; pick
the smallest-scope leaf that fits. Frame student-success decisions by entering cohort; resolve
enrollment/aid decisions to net tuition revenue.

---

## 1. Enrollment investment — "recruit more or retain more?"

```
Compare cost per outcome and the net revenue each carries:
├─ Cost per NEW enrolled student (recruitment + leveraging aid) is HIGH
│   and year-1→year-2 attrition is also high
│     → Invest in RETENTION first — you're filling a leaking bucket
├─ Retention is already strong (year-1→year-2 high) and the funnel is the constraint
│     → Invest in RECRUITMENT / yield
└─ Both weak
      → Retention first (cheaper, multi-year net revenue), then funnel
```

Rule: a retained student carries years of net revenue a new admit hasn't earned; default to the
retention lever unless retention is already strong.

## 2. Funnel leak — "where are we losing students?"

```
Steepest drop in: inquiry → applicant → admit → deposit → enroll → matriculated
├─ inquiry → applicant   → weak nurture / unclear fit → segmented outreach
├─ applicant → admit      → review capacity / criteria → process & criteria
├─ admit → deposit         → price perception / competing offers → yield events, aid timing, fit msg
└─ deposit → enroll (melt) → summer melt / doubts → melt-prevention outreach, onboarding
```

## 3. Discount rate — "should we discount more?"

```
Model net tuition revenue across discount scenarios.
├─ Marginal aid dollar still adds enrolled NET revenue → discount can rise (toward the optimum)
├─ Marginal aid dollar adds volume but lowers net revenue → STOP; past diminishing returns
└─ Aid is flat across segments → segment first (price- vs fit-sensitive) before changing the rate
```

## 4. Retention diagnosis — "why is retention low?"

```
Frame by entering cohort, then segment the year-1→year-2 drop:
├─ Concentrated in academically underprepared → gateway-course support, tutoring
├─ Concentrated in first-gen / belonging        → advising, belonging interventions
├─ Concentrated in financial-need / holds        → aid gaps, financial-hold intervention
└─ Diffuse across all                            → first-year experience redesign (advising touchpoints)
```

## 5. FERPA data flow — "can we build this dashboard?"

```
Is the data an "education record" (personally identifiable, maintained by the institution)?
├─ No (de-identified / aggregate) → lower constraint; still verify aggregation thresholds
└─ Yes → who is accessing it?
     ├─ Has a legitimate educational interest → permitted; scope access to that interest
     └─ No legitimate educational interest → not permitted without consent/exception
   → Design access control around legitimate-educational-interest BEFORE building; flag for counsel
```

---

## 2026 capability map (verify before quoting specifics)

- **Title IV / financial-aid rules** — federal aid packaging and disclosure rules change frequently;
  treat any specific rule as `[unverified — confirm against current federal regulation]`.
- **FERPA** — the legitimate-educational-interest and directory-information framework is stable, but
  institutional policy and state law vary; flag for counsel. `[unverified — training knowledge]`
- **Early-alert / SIS platforms** — common student-success platforms integrate LMS + SIS signals;
  the funnel and risk-score logic here is platform-independent. Treat platform-feature claims as `[unverified]`.
- **Accreditation standards** — vary by accreditor and change on review cycles; map to your
  accreditor's current standards, not a generic list.

> Per the core Claim-Grounding protocol, date and verify any regulation-, aid-, or
> accreditation-specific claim before it gates a decision.
