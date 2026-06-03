# Process-improvement decision trees

> Canonical decision trees for the `process-improvement` craft — which improvement **methodology**, which **control chart**, which **root-cause tool**, the **capable-vs-in-control** triage, which **Lean countermeasure** for a waste, and the **measurement-trust (MSA / Gage R&R)** gate. The agents traverse the matching tree **top-to-bottom before selecting a method** — they do not keyword-match on the user's phrasing (CLAUDE.md §5, the Capability Grounding Protocol). Format follows [`../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md).

These trees implement house opinions #2 (DMAIC backbone), #3 (Lean + Six Sigma complementary), #5 (control plan), and #6 (root cause before fix) from [`../CLAUDE.md`](../CLAUDE.md). Reference facts behind the leaves live in [`dmaic-and-lean-toolkit.md`](dmaic-and-lean-toolkit.md) and [`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md). Volatile/threshold facts carry inline markers per the Capability Grounding Protocol.

---

## Decision Tree: Which improvement methodology?

**When this applies:** Someone says "fix this process" / "improve this" and you must choose the *vehicle* — DMAIC, DMADV, Kaizen/PDCA, or a just-do-it — before doing any work. The observable trigger is a stated improvement goal whose *shape* (existing vs new process; cause known vs unknown; effort warranted) can be named.

**Last verified:** 2026-06-03 against the DMAIC/DMADV/PDCA comparison in [`dmaic-and-lean-toolkit.md`](dmaic-and-lean-toolkit.md) §2 (sources cited there).

```text
Improvement goal stated
│
├─ Does a process already exist?
│       │
│       ├─ No — designing something new
│       │   → DMADV / DFSS (Define-Measure-Analyze-Design-Verify)
│       │
│       └─ Yes — improving existing
│               │
│               ├─ Is the root cause already known AND the fix obvious?
│               │       │
│               │       ├─ Yes — small, understood, low-risk
│               │       │       │
│               │       │       ├─ Trivial / reversible?
│               │       │       │       ├─ Yes — minutes to do, easily undone
│               │       │       │       │   → Just-do-it (implement + a quick check)
│               │       │       │       └─ No — worth a structured loop
│               │       │       │           → Kaizen / PDCA (fast iterative loop)
│               │       │
│               │       └─ No — cause unknown OR fix non-obvious
│               │               │
│               │               ├─ Is the process important enough to justify the rigor?
│               │               │       ├─ Yes — measurable gap, matters to the business
│               │               │       │   → DMAIC (Define-Measure-Analyze-Improve-Control)
│               │               │       └─ Marginal — small but recurring
│               │               │           → Kaizen / PDCA (fast iterative loop)
```

**Rationale per leaf:**
- *DMADV / DFSS* — no existing process to measure-and-improve; you're designing to a target from the start ([`dmaic-and-lean-toolkit.md`](dmaic-and-lean-toolkit.md) §2).
- *DMAIC* — the default for an existing process with an unknown cause or a non-obvious fix, where the rigor pays off; the full statistical toolkit per phase.
- *Kaizen / PDCA* — a small, understood problem worth a fast structured loop, not a multi-week project.
- *Just-do-it* — trivial + reversible: fixing it costs less than analyzing it. Still confirm the fix held.

**Tradeoffs summary:**

| Leaf | Ceremony / cost | Best for | Fails when |
|---|---|---|---|
| DMADV | Highest | New design; incapable legacy process | Used to "improve" a fixable existing process (overkill) |
| DMAIC | High | Existing process, unknown cause | Used on a trivial fix (analysis paralysis) |
| Kaizen / PDCA | Low | Small, understood, recurring | Used where the cause is genuinely unknown (you'll guess) |
| Just-do-it | Minimal | Trivial + reversible | Used on an irreversible / high-blast change |

---

## Decision Tree: Which control chart?

**When this applies:** You're in the Measure or Control phase and need to chart a metric over time. The observable trigger is a metric + its data type (measured vs counted) and how it's grouped.

**Last verified:** 2026-06-03 against the control-chart selection guidance in [`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md) §3 (SPC for Excel; Six Sigma Study Guide; Minitab).

```text
Metric to chart over time
│
├─ Variable — continuous measurement (time, cost, length)
│       │
│       └─ Subgroup size?
│               ├─ 1 — individual readings → I-MR chart
│               ├─ 2 to ~9              → Xbar-R chart
│               └─ ~9+ (10 or more)    → Xbar-S chart
│
└─ Attribute — counted
        │
        ├─ Counting defectIVES (a unit is good or bad)
        │       │
        │       └─ Subgroup size constant?
        │               ├─ Constant → np chart
        │               └─ Variable → p chart
        │
        └─ Counting defectS (several possible per unit)
                │
                └─ Opportunity / area constant?
                        ├─ Constant → c chart
                        └─ Variable → u chart
```

**Rationale per leaf:**
- *I-MR* — one reading per time point (long cycle time, or no natural subgroup); the moving range estimates short-term spread.
- *Xbar-R* — small subgroups; the **range** estimates within-subgroup spread well at n ≤ ~9.
- *Xbar-S* — larger subgroups; the **standard deviation (S)** estimates spread better than the range once n ≥ ~10.
- *p / np* — **defectives** (a unit passes or fails): np when subgroup size is constant (plot counts), p when it varies (plot proportion).
- *c / u* — **defects** (a unit can carry several flaws): c when the inspection area/opportunity is constant (plot counts), u when it varies (plot defects-per-unit).

**Reminder:** control limits are computed from the data (±3σ), **not** the customer spec limits. A chart proves *stability*, capability indices (Cpk/Ppk) prove *meeting spec* — different questions ([`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md) §2-3).

---

## Decision Tree: Which root-cause tool?

**When this applies:** You're in Analyze and need to drive to a *proven* cause. The observable trigger is the shape of the problem (many candidate causes vs a single deep chain vs needing confirmation).

**Last verified:** 2026-06-03 against [`dmaic-and-lean-toolkit.md`](dmaic-and-lean-toolkit.md) §1 (Analyze). The fishbone→5-Whys→Pareto→hypothesis-test sequence is long-established Lean Six Sigma practice; the confirmatory-test handoff is the CLAUDE.md #4 seam.

```text
Problem to diagnose
│
├─ Many possible causes — need to brainstorm broadly
│   → Fishbone / Ishikawa (group by 6M: Method / Machine / Material /
│                           Measurement / Environment / People)
│       │
│       └─ (continues below)
│
└─ One suspected chain — drill the why
    → 5 Whys (drill to the systemic root)
        │
        └─ (continues below)

[Both Fishbone and 5 Whys feed here:]
│
└─ Several candidate causes survive — which matter most?
        │
        └─ Need to rank by frequency / impact → Pareto (find the vital few)
                │
                └─ Is the candidate cause PROVEN, or just plausible?
                        │
                        ├─ Plausible — not yet proven with data
                        │   → Route confirmatory test to applied-statistics
                        │     (hypothesis test / regression / DOE)
                        │
                        └─ Proven — data confirms it
                            → Root cause verified — proceed to Improve
```

**Rationale per leaf:**
- *Fishbone (6M)* — opens the cause space broadly when many factors could be at play; a *hypothesis generator*, not proof.
- *5 Whys* — drills a single suspected chain to the systemic (not symptomatic) root.
- *Pareto* — ranks the surviving candidates so the team targets the vital few (≈80/20).
- *Route to applied-statistics* — **the gate before any fix** (CLAUDE.md #6): a plausible cause is not a proven cause. The confirmatory inference is `applied-statistics`' lane ([`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md) §6).

> **Anti-pattern this tree prevents: solution-jumping.** Never exit to *Improve* from a fishbone or a 5-Whys alone — pass through the proof gate first.

---

## Decision Tree: Is this process capable / in control? (triage)

**When this applies:** You have process data and are asked "how good is this process?" / "is it meeting spec?". The observable trigger is data + a spec/target, and the need to decide *control first, capability second*.

**Last verified:** 2026-06-03 against [`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md) §2-4. Thresholds (Cpk ≥ 1.33 capable) cited there.

```text
Process data + a spec/target
│
└─ Is the process in statistical CONTROL? (no WE/Nelson signals on the chart)
        │
        ├─ No — special-cause signals present
        │   → Process is UNSTABLE. Capability is meaningless here.
        │     Find + remove the special cause first.
        │
        └─ Yes — only common-cause variation
                │
                └─ Compute Cpk / Ppk vs spec. Where does it land?
                        │
                        ├─ Cpk < 1.0
                        │   → NOT capable — spread exceeds spec.
                        │     Reduce variation and/or recenter.
                        │
                        ├─ 1.0 to 1.33
                        │   → Marginal — capable only if centered + stable;
                        │     little margin. Improve.
                        │
                        ├─ 1.33 to 1.67
                        │   → Capable — meets the common baseline.
                        │     Hold with a control plan.
                        │       └─ → Control phase: control plan + SPC +
                        │              standard work + owner
                        │
                        └─ 1.67+
                            → Highly capable — critical-characteristic grade.
                              Hold with a control plan.
                                └─ → Control phase: control plan + SPC +
                                       standard work + owner
```

**Rationale per leaf:**
- *Control before capability* — capability indices assume a stable process; computing Cpk on an out-of-control process gives a meaningless number (CLAUDE.md anti-pattern). The WE/Nelson rules ([`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md) §4) decide "in control?".
- *Cpk bands* — `< 1.0` not capable; `1.0–1.33` marginal; `≥ 1.33` capable (general/automotive baseline, ~63 PPM); `≥ 1.67` critical-characteristic grade (~0.6 PPM) — verified 2026-06-03.
- *Always exit to a control plan* — a capable process still regresses without the Control phase (CLAUDE.md #5).

> **Reminder:** "in control" (stable, predictable) and "capable" (meets spec) are **independent**. A process can be perfectly stable *and* consistently out-of-spec (in control, not capable), or meet spec on average while wildly unstable (capable-looking, not in control — and not trustworthy). Always establish control first.

---

## Decision Tree: Which Lean countermeasure for this waste?

**When this applies:** a Lean waste analysis (the `lean-waste-analysis` skill) found a *dominant* waste among the 8 (DOWNTIME) and you need the standard countermeasure family to attack it. The observable trigger is a named waste with the most non-value-add time/cost attached.

**Last verified:** 2026-06-03 against the 8-wastes (DOWNTIME) overlay in [`dmaic-and-lean-toolkit.md`](dmaic-and-lean-toolkit.md) §3 (Lean Enterprise Institute; MoreSteam). The countermeasure families are long-established Lean practice.

```text
Dominant waste identified
│
└─ Which of the 8 wastes (DOWNTIME)?
        │
        ├─ Defects
        │   → Poka-yoke mistake-proofing + standard work + root-cause the defect
        │
        ├─ Overproduction
        │   → Pull / just-in-time — produce to takt, not to capacity
        │
        ├─ Waiting
        │   → Balance the line to takt; attack the bottleneck / constraint
        │
        ├─ Non-utilized talent
        │   → Push decisions + skills down; kaizen participation
        │
        ├─ Transportation
        │   → Re-layout / co-locate; shorten the physical / handoff path
        │
        ├─ Inventory
        │   → Cut batch size; pull; cap WIP
        │
        ├─ Motion
        │   → 5S the workplace; tools + info at the point of use
        │
        └─ Extra-processing
            → Remove non-value-add steps; match precision to the CTQ, don't gold-plate
```

**Rationale per leaf:** each waste has a *characteristic* countermeasure family — but confirm the waste is genuinely the constraint first (a countermeasure on a non-bottleneck waste doesn't speed the whole process; see the best-practice on optimizing the constraint). Defects route back through the root-cause tree before mistake-proofing.

> **Pairs with the constraint rule:** removing a waste that isn't on the critical path/bottleneck improves a sub-process, not the system. Find the constraint (the *Waiting* leaf) before investing elsewhere.

---

## Decision Tree: Can I trust this measurement? (MSA / Gage R&R triage)

**When this applies:** you are about to baseline (or have baselined) on measured data and must confirm the *measurement system itself* isn't the source of the variation you're chasing. The observable trigger is "we have numbers" — **before** you trust them. This is the gate that protects house opinion #1 (measure before you change) from being built on sand.

**Last verified:** 2026-06-03 against the MSA / Gage R&R section in [`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md) §5. The %R&R acceptance bands are the standard AIAG convention `[unverified — training knowledge; confirm before quoting a client]`; the inference itself routes to `applied-statistics`.

```text
About to baseline on measured data
│
└─ Is the metric operationally DEFINED?
   (same input → same recorded value, any person)
        │
        ├─ No — ambiguous
        │   → STOP. Write the operational definition first.
        │     An ambiguous metric makes every later number noise.
        │
        └─ Yes
                │
                └─ Variable measurement or attribute / judgment?
                        │
                        ├─ Variable — a measured value
                        │   → Gage R&R study — route the %R&R inference to applied-statistics
                        │           │
                        │           └─ %R&R band?
                        │                   ├─ < 10% — acceptable
                        │                   │   → Measurement trustworthy — baseline on it
                        │                   ├─ 10–30% — marginal
                        │                   │   → Conditionally usable;
                        │                   │     improve if it gates a key decision
                        │                   └─ > 30% — unacceptable
                        │                       → Fix the measurement system
                        │                         BEFORE collecting more data
                        │
                        └─ Attribute — pass/fail judgment
                            → Attribute agreement analysis —
                              do appraisers agree with the standard + each other?
```

**Rationale per leaf:**

- *Operational definition first* — if two people measuring the same thing record different values, the spread you see is measurement noise masquerading as process variation. No study fixes an undefined metric.
- *Gage R&R vs attribute agreement* — variable data gets a Gage R&R (repeatability + reproducibility); pass/fail judgment data gets an attribute agreement analysis. Both ask: is the gauge the problem?
- *Route the inference out* — computing and defending the %R&R is `applied-statistics`' lane (house opinion #5); this tree decides *that you need it* and *what to do with the band*.

> **Why this tree exists:** a 30%+ Gage R&R means up to a third of your "process variation" is the ruler, not the process. Baselining and "improving" on top of an untrustworthy gauge burns the whole DMAIC. Trust the measurement before you trust the data.

---

## Sources

The reference facts behind these trees — DMAIC/DMADV/PDCA, the 8 wastes, control-chart selection, WE/Nelson rules, Cp/Cpk/Pp/Ppk thresholds — are cited with retrieval dates in [`dmaic-and-lean-toolkit.md`](dmaic-and-lean-toolkit.md) and [`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md). All retrieved 2026-06-03.
