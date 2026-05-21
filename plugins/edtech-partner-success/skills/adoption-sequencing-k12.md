# Skill: adoption-sequencing-k12

> **Invoked by:** `learning-analytics-analyst` (when interpreting an adoption signal), `success-playbook-designer` (when authoring an adoption / activation / low-engagement play), `partner-success-manager` (when responding to "why is adoption stalled?").
>
> **When to invoke:** any question of the shape "how should this K-12 partner sequence their feature/role/school rollout?" or "is this adoption pattern a problem or just the expected calendar shape?"
>
> **Output:** a partner-stage-aware, school-year-aware adoption sequencing plan (or signal-interpretation) that distinguishes *expected-slow* from *actually-broken*.

## The core insight this skill encodes

K-12 adoption does NOT follow a generic SaaS adoption curve. It follows the school year. A flat August week is not a problem; a flat October week is. A teacher-facing feature adopted at 20% in week 1 of the year is on-pace; the same number in week 12 is alarming. **Without the calendar overlay, the same adoption signal gets misdiagnosed half the time.**

This skill pairs the calendar overlay (from [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md)) with a sequencing framework that respects partner stage, product surface (teacher vs admin vs student vs family-facing), and segment depth.

## The flow

When invoked, the agent should:

1. **Establish partner stage** — newly-implemented (first 90 days) / first-year sustaining / multi-year mature / pre-renewal. Each has different adoption-priority maps.
2. **Establish product surface** — teacher-facing / admin-facing / student-facing / family-facing. Each adopts on a different rhythm.
3. **Establish where in the school year the partner is** — opening (Aug-Sep) / settling (Oct-Nov) / mid-year (Dec-Feb minus dead-zones) / spring (Mar-Apr minus state-testing) / closing (May-Jun).
4. **Cross-reference the K-12 arc knowledge file** to check whether the current adoption signal is on-pace, ahead, or behind.
5. **If behind:** run the adoption-diagnostic flow (from [`../templates/adoption-diagnostic-worksheet.md`](../templates/adoption-diagnostic-worksheet.md)) to identify root cause BEFORE recommending a play.
6. **Sequence the next adoption activities** — what should the partner be focused on adopting NEXT, given where they are.

## The sequencing rules

### Stage 1 — Newly-implemented (first 90 days)

Adopt in this order:

1. **Core access** for all rostered users (login works, can find the product, can see their content)
2. **Trained champions running training waves** (per [`../templates/train-the-trainer-curriculum.md`](../templates/train-the-trainer-curriculum.md)) — not vendor-direct training of every teacher
3. **One workflow used 80%+ by intended-users** — pick the single most-load-bearing workflow and drive it before broadening
4. **Admin-side reporting** so the partner can self-serve their own usage data

**DO NOT** push feature-breadth in stage 1. A partner with 20% adoption across 10 features is not as healthy as one with 80% adoption of 2 features.

### Stage 2 — First-year sustaining (months 3-12)

Adopt in this order:

1. **Second workflow** (rooted in the success-plan stated outcomes)
2. **Admin dashboards** for the named decision-maker
3. **Family-facing surface** (if applicable) — but ONLY after teacher-side workflows are at 80%+
4. **Cross-school replication** (if multi-school) — schools that adopted early carry the pattern to schools that haven't started

### Stage 3 — Multi-year mature

Adopt in this order:

1. **Power-user features** — the 10-15% of usage that drives 50% of value (when the partner is ready for depth)
2. **Integration depth** — additional data sources, more roles, deeper rostering
3. **Outcome instrumentation** — closing the loop on the success-plan stated outcomes

### Stage 4 — Pre-renewal

This is NOT primarily an adoption-sequencing stage. It's a measurement-and-narrative stage. The PSM should be:

1. **Surfacing the outcomes-vs-stated-goals story** (per [`../templates/renewal-decision-memo.md`](../templates/renewal-decision-memo.md))
2. **Identifying the 1-2 expansion adopters** within the partner (which schools, which roles, which use cases earned value worth doubling down on)
3. **NOT pushing brand-new feature adoption in the pre-renewal window** — late adoption surge looks like vendor-driven adoption-padding to a renewal-skeptical CFO

## Surface-by-surface adoption rhythm (within a school year)

### Teacher-facing

- **Strong adoption window:** weeks 3-8 of school year (post-setup, pre-grading-crunch)
- **Weak adoption window:** week 1-2 (setup), Thanksgiving week, winter break, end of grading periods, state testing
- **Sustained-engagement signal:** mid-October monthly active rate

### Admin-facing

- **Strong adoption window:** continuous, with a spike in early September (setup) and February (mid-year reporting)
- **Weak adoption window:** late August setup overload, end-of-year wrap

### Student-facing

- **Strong adoption window:** weeks 4-12 of school year (after teacher introduces the product)
- **Weak adoption window:** week 1-3 of year, holidays, summer

### Family-facing (parent comms, family-engagement products)

- **Strong adoption window:** early in school year (welcome window) + early Nov (conferences) + early February (mid-year)
- **Weak adoption window:** state-testing window, end-of-year wrap, summer
- **Multilingual overlay:** non-English-primary families adopt on different rhythms; community-school events drive bursts

## Anti-patterns this skill flags

- **Pushing feature-breadth too early.** A partner that's at week 6 of implementation and being pushed to adopt 5 features is being sabotaged by the PSM.
- **Misreading the calendar dip as a problem.** A January engagement drop that's actually just winter break + new-year-startup-friction gets a "yellow" health score and a Recovery play that the partner doesn't need.
- **Adopting admin features before teacher features hit 80%.** Admins want reports; admins won't have reports if teachers aren't using the product yet.
- **Late-renewal-window adoption surge** that reads as vendor-padding.
- **Bottom-quartile-school within a multi-school partner getting the same intervention as the whole partner.** The intervention should fire at the school level, not the partner level.

## When NOT to invoke

- The adoption signal is broken (rostering issue, telemetry gap). Diagnose the signal first via [`rostering-data-quality.md`](rostering-data-quality.md) before sequencing.
- The partner is in active recovery (red health). Adoption sequencing assumes a stable relationship; recovery plays come first.
- The partner-stated outcome is "use the product less" — the sequencing framework assumes the partner is trying to adopt MORE, not LESS.

## Refresh triggers

- A major product release changes the surface (e.g., a new family-facing module changes the sequencing)
- K-12 calendar conventions shift (rare)
- Real-engagement signal contradicts the sequence (the `/wrap` slash command surfaces scenarios where this skill's recommendations went sideways)

## References

- [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md) — the calendar-overlay knowledge
- [`../knowledge/k12-psm-operating-cadence.md`](../knowledge/k12-psm-operating-cadence.md) — the broader operating-cadence (dead zones, signals-by-rhythm)
- [`../knowledge/partner-health-score-drift.md`](../knowledge/partner-health-score-drift.md) — the score-vs-reality discipline
- [`../templates/adoption-diagnostic-worksheet.md`](../templates/adoption-diagnostic-worksheet.md) — the diagnostic-before-intervention artifact
- [`rostering-data-quality.md`](rostering-data-quality.md) — signal-trust check
- [`partner-health-scoring.md`](partner-health-scoring.md) — the broader health-score pattern
