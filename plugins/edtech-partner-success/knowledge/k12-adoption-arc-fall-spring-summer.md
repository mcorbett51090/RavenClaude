# K-12 adoption arc — fall / spring / summer

> **Last reviewed:** 2026-05-21. Status: pre-engagement-draft (synthesis from existing v0.2.0 + v0.3.0 + v0.4.0 + v0.4.1 knowledge files + practitioner consensus; refresh on first real engagement signal). Sources: AASA "School Budgets 101" (calendar references), CoSN K-12 IT calendar conventions, EdWeek Research Center teacher-time-use surveys, [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md), [`edtech-segment-fundamentals.md`](edtech-segment-fundamentals.md), [`partner-health-score-drift.md`](partner-health-score-drift.md). Refresh when: (a) K-12 calendar conventions shift (rare), (b) state-level assessment-window changes affect spring testing patterns, (c) live engagement signals via `/wrap` contradict the patterns here.

This file is the **K-12 calendar overlay for adoption signal interpretation**. The [`../skills/adoption-sequencing-k12.md`](../skills/adoption-sequencing-k12.md) skill consults this file to distinguish *expected-slow* from *actually-broken*. The [`../templates/adoption-diagnostic-worksheet.md`](../templates/adoption-diagnostic-worksheet.md) template uses this file's calendar in its Section 2.

This file complements [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md) — that file covers WHEN to schedule touchpoints; this file covers WHAT adoption patterns to expect at each calendar phase.

---

## The annual arc (school year, not calendar year)

US K-12 school year runs ~late August through ~mid-June. The adoption arc has distinct phases:

| Phase | When | What's happening in adoption |
|---|---|---|
| **0. Pre-launch setup** | mid-Aug to Day 1 of school | Rostering / SSO / district setup; teachers preparing classrooms; **no end-user product usage**; engagement-signal floor is expected |
| **1. Opening rush** | Day 1 through ~week 3 | Teacher first-uses; technical-issue surfacing; **broad-but-shallow** engagement; bursty signal |
| **2. Settling** | Weeks 4-8 (~Sep-Oct) | Sustained adoption begins; the workflows that will be used all year are picked here; **the most-informative period for "will this partner succeed?"** |
| **3. First reporting wave** | ~Oct-Nov | Mid-quarter reporting; admin engagement spikes; teachers start using analytics features; first parent-teacher conferences (parent comms spike) |
| **4. Thanksgiving + winter slowdown** | Mid-Nov through ~Jan 2 | Dead-zone dominated; expect engagement collapse; **do not draw conclusions from December numbers** |
| **5. New-year settling** | Early Jan through ~mid-Feb | Reset rush; new-semester adoption can be a 2nd "opening rush" for late-implementing partners; **second-chance window** for adoption that didn't land in fall |
| **6. Mid-year peak** | ~mid-Feb through ~mid-Mar | Highest sustained-engagement window of the year; data-informed conversations land best here |
| **7. State testing window** | ~mid-Mar through ~mid-May (state-variable) | District attention shifts to assessments; **non-assessment products see engagement drop**; do not push new features |
| **8. Closing** | Last 4-6 weeks of school year | Grading, end-of-year events, summer planning; **expansion conversations land worst here** |
| **9. Summer** | mid-Jun through mid-Aug | Most teacher-facing products go cold; admin-facing products may see spikes (planning, reporting, summer-rostering); **vendor decisions about next-year strategy happen in this window** |

## What a healthy adoption pattern looks like (by phase)

These are *expectation rules of thumb*, not benchmarks. Treat as calibration for the diagnostic worksheet.

### Phase 1 — Opening rush (Days 1-21)
- **Teacher-facing:** 50-80% of rostered teachers log in within first 14 days
- **Student-facing:** 30-60% of rostered students access via teacher introduction within first 30 days
- **Admin-facing:** Setup-mode; admin engagement is mostly configuration, not usage
- **Family-facing:** Welcome-message wave; high response rates expected here (this is "the announcement")

### Phase 2 — Settling (Weeks 4-8)
- **Teacher-facing:** Sustained-weekly-active rate plateaus; 60-80% of active teachers settle into 2-3 core workflows
- **Student-facing:** Driven by teacher activity; varies by product surface
- **Admin-facing:** First rounds of usage reporting requested
- **Family-facing:** Day-to-day communication pattern emerges; response rates moderate

**THIS IS THE SINGLE MOST PREDICTIVE PERIOD** for whether a partner will succeed in year 1. The pattern set here usually persists.

### Phase 3 — First reporting wave (Oct-Nov)
- **Admin-facing:** spike — first mid-quarter reporting; admin engagement is highest of fall
- **Family-facing:** parent-teacher conference comms spike — typically 2-3 weeks of elevated activity around conferences
- **Teacher-facing:** stable usage continues
- Pre-Thanksgiving slowdown begins ~last week of November

### Phase 4 — Thanksgiving + winter slowdown
- **All surfaces:** expect engagement collapse
- A 60-80% drop in active-user metrics from Phase 3 peak is NORMAL
- Do NOT diagnose adoption problems based on Phase 4 data
- The score-drift discipline in [`partner-health-score-drift.md`](partner-health-score-drift.md) needs this overlay

### Phase 5 — New-year settling
- **Teacher-facing:** ~2-3 week reset, then back to Phase 2 patterns
- This is the **second-chance window** for adoption that didn't land in fall — partners who came in late, or who had Phase 1-2 rough patches, can recover here
- **Implementation playbook note:** late-fall implementations should target Phase 5 (early Jan) as their "real Phase 1" rather than fighting the December dead zone

### Phase 6 — Mid-year peak
- **Highest sustained engagement window of the year**
- Best window for: QBRs, expansion conversations, data-driven recommendations, new-feature rollouts
- Most adoption-signal trends visible here are real (not noise from settling or dead zones)

### Phase 7 — State testing window
- **Non-assessment products:** expect 20-40% engagement drop during the partner's specific testing window
- **Assessment / test-prep products:** engagement may spike instead
- District attention is on testing; don't push roadmap conversations or expansion asks here
- State-variable — confirm the partner's specific testing schedule

### Phase 8 — Closing
- **Teacher-facing:** declines through the period; grading and wrap consume attention
- **Admin-facing:** spike for end-of-year reporting
- **Family-facing:** end-of-year comms (final grades, summer programs) drive bursts
- **Renewal conversations:** if the K-12 120-180-day clock pointed here, it's too late (see [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md))

### Phase 9 — Summer
- **Teacher-facing:** very low engagement; expected
- **Admin-facing:** planning-mode spikes (registering for next year, capacity planning, reporting)
- **Vendor-side action:** internal post-school-year retrospective; expansion conversations for next school year; pricing-conversation prep for the July-1-fiscal-year renewal cycle

## Surface-by-surface adoption rhythm (compact reference)

| Surface | Strong adoption windows | Weak adoption windows |
|---|---|---|
| Teacher-facing | Weeks 3-8 of school year + mid-Feb to mid-Mar | Week 1-2 setup, Thanksgiving week, winter break, state testing, end-of-year |
| Admin-facing | Continuous; spikes early Sep + Oct-Nov reporting + Feb mid-year + end-of-year wrap | Late August setup overload |
| Student-facing | Weeks 4-12 of school year (post teacher introduction) | Weeks 1-3, holidays, summer |
| Family-facing (parent comms) | Early school year (welcome) + early Nov (conferences) + early Feb (mid-year) | State testing window, end-of-year wrap, summer |

## Multi-school adoption-distribution patterns

When a multi-school partner has uneven adoption:

- **Early-adopter / late-adopter spread is normal** — expect 1-2 schools to lead, 1-2 to lag
- The spread is **wider in newly-implemented partners** and **narrower in mature partners**
- A school that's NEVER adopted by Phase 5 is a school-level problem, not a partner-level problem (intervention should fire at the school)
- A partner whose ALL schools are below benchmark is a partner-level problem (root cause is usually rostering, district-IT, or champion absence — not adoption)

## Anti-patterns this knowledge file flags

- **Diagnosing adoption-failure from December data.** It's a dead zone. The data doesn't mean what it looks like.
- **Pushing breadth in Phase 2.** Partner settles into 2-3 workflows in Phase 2; pushing 5 more features dilutes adoption rather than expanding it.
- **Treating multi-school spread as a partner problem.** It's almost always a school-level problem; the intervention should be at the right level.
- **End-of-year expansion asks.** Phase 8 is the worst expansion window of the year.
- **Late-implementation fighting December.** A November-go-live partner is fighting the dead zone immediately; better to push implementation to January if possible.
- **Spring-testing-window roadmap conversations.** District attention is elsewhere; the conversation won't land.
- **Summer "is this partner OK?"** questions for teacher-facing products. They're not using it; they're on vacation. The signal is meaningless.

## Refresh triggers

- K-12 calendar conventions materially shift (rare; school-year-shape is stable nationally)
- A state changes its assessment-window timing significantly
- A district shifts to a year-round calendar (some districts use modified schedules; pattern this file describes is the traditional ~180-day school year)
- Live engagement signal via `/wrap` shows a Phase / surface pattern this file doesn't anticipate

## References

- [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md) — the WHEN-to-schedule complement (this file is WHAT-to-expect)
- [`partner-health-score-drift.md`](partner-health-score-drift.md) — score-decay rules need this calendar overlay
- [`edtech-segment-fundamentals.md`](edtech-segment-fundamentals.md) — broader K-12 calendar / regulatory framework
- [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md) — Q3 (Feb-Apr) renewal-build window
- [`../skills/adoption-sequencing-k12.md`](../skills/adoption-sequencing-k12.md) — the playbook this knowledge serves
- [`../templates/adoption-diagnostic-worksheet.md`](../templates/adoption-diagnostic-worksheet.md) — diagnostic that uses this file's overlay
