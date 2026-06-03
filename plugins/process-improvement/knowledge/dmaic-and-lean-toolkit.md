# DMAIC & Lean toolkit

> The methodology backbone for the `process-improvement` plugin: DMAIC phase-by-phase with the canonical tool at each phase, the DMAIC vs DMADV vs Kaizen/PDCA distinction, and the Lean overlay (the 8 wastes / DOWNTIME, value-add vs non-value-add). The agents traverse [`process-improvement-decision-trees.md`](process-improvement-decision-trees.md) to *select* a methodology/tool; this file is the *reference* for what each tool is and when it applies. Implements house opinions #2 (DMAIC backbone), #3 (Lean+Six Sigma complementary), and #6 (root cause before fix) from [`../CLAUDE.md`](../CLAUDE.md).

**Last verified:** 2026-06-03 against published Lean Six Sigma practice (DMAIC/DMADV/PDCA comparison; the DOWNTIME 8-wastes acronym). Methodology structure is stable, long-established body of knowledge; sources cited inline. Process-specific numbers are illustrative and domain-neutral.

---

## 1. DMAIC — the default backbone for improving an existing process

DMAIC is a **data-driven, five-phase** improvement cycle used to enhance, improve, and stabilize an *existing* process: **D**efine → **M**easure → **A**nalyze → **I**mprove → **C**ontrol. Each phase has a tollgate (a review the project passes before advancing). It is the default for "this process exists but underperforms" — verified 2026-06-03 (BusinessMap, KAIZEN™).

> **House rule (CLAUDE.md #6):** the phases are *sequential for a reason* — you cannot Improve before you've Analyzed root cause, and you cannot Analyze before you've Measured a baseline. Skipping Measure ("we know what's wrong") or Control ("the team will remember") are the two most common DMAIC failures.

### Define — "what problem, for whom, and how big?"

| Tool | What it produces |
|---|---|
| **Project charter** | Problem statement, goal statement (specific + measurable), scope (in/out), business case, team, timeline. The anchor for the whole arc. (skill: `dmaic-project-charter`) |
| **Voice of the Customer (VOC)** | The raw customer/stakeholder needs the process must satisfy. |
| **CTQ tree** | VOC → **Critical-to-Quality** requirements → measurable spec/target. **A defect is a failure to meet a CTQ** (CLAUDE.md #7) — define it here, before counting. |
| **SIPOC** | Suppliers → Inputs → Process → Outputs → Customers. Sets the boundaries before detailed mapping. (driven by `process-analyst`) |

### Measure — "how does it perform today?"

| Tool | What it produces |
|---|---|
| **Data-collection plan** | Operational definitions (start/stop events, units), what/where/how/who/frequency, sampling window, stratification factors. |
| **Measurement System Analysis (MSA) / Gage R&R** | Confirms the *measurement* is trustworthy before the *process* is judged. Repeatability (same appraiser) + reproducibility (across appraisers). Details: [`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md) §5. |
| **Baseline capability / sigma** | DPMO, sigma level (with the 1.5σ-shift convention stated), Cp/Cpk/Pp/Ppk. **Confirm the process is in statistical control before judging capability.** Details: [`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md). |

### Analyze — "what's the proven root cause?"

| Tool | What it produces |
|---|---|
| **Fishbone (Ishikawa, 6M)** | Candidate causes grouped by Method, Machine, Material, Measurement, Mother-nature (Environment), Manpower (People). A *hypothesis* generator, not proof. |
| **5 Whys** | Drills a single cause chain to the systemic root. |
| **Pareto** | The vital few (≈80/20) — which causes/defect categories dominate. (driven by `process-analyst`) |
| **Hypothesis test / regression / DOE** | **The confirmatory step — routed to `applied-statistics`** (CLAUDE.md #4). Fishbone/5 Whys propose; the inferential test *proves*. Don't change the process on an unproven cause. |

### Improve — "design, pilot, prove the fix"

| Tool | What it produces |
|---|---|
| **Solution selection** | Impact/effort or weighted-criteria ranking of candidate fixes. |
| **Poka-yoke (mistake-proofing)** | Design that makes the defect impossible (or immediately visible) rather than relying on vigilance. |
| **FMEA (Failure Mode & Effects Analysis)** | Screens the new design for failure modes by Severity × Occurrence × Detection (RPN); a forward-looking risk screen. |
| **Pilot** | A bounded trial; the before/after comparison is **sized and analyzed by `applied-statistics`** (effect size + CI, not a bare p-value). |
| **Future-state map** | The to-be process the pilot validates. |

### Control — "lock the gain so it sticks"

| Tool | What it produces |
|---|---|
| **Control plan** | The document binding each CTQ to its measurement, spec, monitoring method, sampling, and **response plan + named owner**. (skill: `control-plan-and-sustain`) |
| **SPC (control chart)** | Ongoing monitoring with the right chart + out-of-control rules (Western Electric / Nelson). Chart selection + rules: [`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md) §3-4. |
| **Standard work** | The documented best-known method so the gain doesn't decay with staff turnover. |
| **Response plan** | What to do, and who acts, when the chart signals out-of-control. |

> **House rule (CLAUDE.md #5):** *a control plan or it didn't happen.* An improvement with no Control phase regresses.

---

## 2. DMAIC vs DMADV vs Kaizen / PDCA — pick the right vehicle

Verified 2026-06-03 (BusinessMap; Learn Lean Sigma; KAIZEN™).

| Methodology | Phases | Use when | Tooling depth |
|---|---|---|---|
| **DMAIC** | Define, Measure, Analyze, Improve, Control | Improving an **existing** process with a clear problem + measurable gap. **The default.** | Heavy — full statistical toolkit per phase |
| **DMADV** (a.k.a. **DFSS**, Design for Six Sigma) | Define, Measure, Analyze, **Design**, **Verify** | **No existing process to improve**, or the current process is fundamentally incapable of meeting the requirement — you're *designing new*. | Heavy — design-focused (QFD, simulation, DOE) |
| **PDCA** | Plan, Do, Check, Act | A simple, iterative loop for implementing a **predefined** improvement; the engine inside Lean/Kaizen. | Light — fast, low-ceremony |
| **Kaizen** | (event/loop, PDCA-driven) | A focused, time-boxed continuous-improvement event on a small, well-understood problem. | Light — team-driven, rapid |

**Decision shorthand:** existing process + unknown cause + worth the rigor → **DMAIC**; brand-new process / design from scratch → **DMADV**; small, understood, just-go-do-it → **Kaizen/PDCA**. (The full tree is in [`process-improvement-decision-trees.md`](process-improvement-decision-trees.md) §1.)

> **Note:** DMAIC's advanced analytical depth (statistical tools at each phase) is what distinguishes it from the lighter PDCA loop; DMADV designs *to a target from the start* rather than *correcting an existing process* — verified 2026-06-03.

---

## 3. The Lean overlay — remove the waste

Lean and Six Sigma are **complementary, not rival** (CLAUDE.md #3): **Lean removes waste** (non-value-add activity that lengthens lead time), **Six Sigma reduces variation** (defects/inconsistency). A real engagement does both.

### Value-add vs non-value-add

A step is **value-add (VA)** only if all three hold: (1) the customer would pay for it, (2) it physically/informationally transforms the thing, (3) it's done right the first time. Everything else is:

- **Non-value-add (NVA)** — pure waste; eliminate.
- **Business-non-value-add (BNVA)** — required by current business/legal constraints (e.g. a compliance check) but adds no customer value; minimize.

**Flow efficiency** = value-add time ÷ total lead time. In most office/service processes this is strikingly low (the work spends most of its life *waiting*), which is exactly where the opportunity sits.

### The 8 wastes — DOWNTIME

The classic Toyota Production System identified **7 wastes** (TIMWOOD — Taiichi Ohno); Western adaptation in the 1990s added an 8th (**Non-utilized talent**), giving the modern **DOWNTIME** acronym — verified 2026-06-03 (Process Excellence Network; MoreSteam; Lean Enterprise Institute).

| Letter | Waste | Domain-neutral example |
|---|---|---|
| **D** | **Defects** | A support ticket reopened because the first resolution was wrong; an invoice with the wrong amount. |
| **O** | **Overproduction** | Generating reports nobody reads; onboarding paperwork for steps later skipped. |
| **W** | **Waiting** | A hire's offer stuck awaiting a single approver; a deploy blocked on a manual sign-off. |
| **N** | **Non-utilized talent** | A skilled analyst doing manual copy-paste a script could do; ideas from frontline staff never solicited. |
| **T** | **Transportation** | A request emailed between five inboxes before anyone owns it; files moved between systems by hand. |
| **I** | **Inventory** | A backlog of unprocessed claims; half-finished onboarding accounts piling up. |
| **M** | **Motion** | Toggling between seven tabs/systems to complete one task; hunting for a document. |
| **E** | **Extra-processing** | Re-keying the same data into multiple systems; approvals that add no risk reduction. |

(Driven by `process-analyst` via the `lean-waste-analysis` skill — tag each step of the value-stream map against DOWNTIME, then Pareto the biggest contributors.)

---

## 4. How the toolkit seams to the neighbors

- **Inferential statistics** (hypothesis tests, DOE, regression, sample-size, capability *inference*) → `applied-statistics/applied-statistician`. This file names the *method per phase*; that plugin runs the *math*. (CLAUDE.md #4)
- **The capability / SPC reference** (sigma↔DPMO↔yield, Cp/Cpk/Pp/Ppk, control-chart selection + out-of-control rules, MSA) → [`six-sigma-statistics-and-spc.md`](six-sigma-statistics-and-spc.md).
- **Project delivery** (charter-as-PM-baseline, schedule, RAID, status) → `project-management`.
- **Instrumentation** (the data pipeline + control-chart dashboard the control plan watches) → `data-platform`.

---

## Sources

- DMAIC overview + 5 phases — [BusinessMap: What Is DMAIC?](https://businessmap.io/lean-management/six-sigma/dmaic); [KAIZEN™: DMAIC](https://kaizen.com/insights/continuous-improvement-dmaic-six-sigma/) — retrieved 2026-06-03.
- DMAIC vs DMADV vs PDCA — [Learn Lean Sigma: DMAIC vs DMADV](https://www.learnleansigma.com/improvement-methodology/dmaic-vs-dmadv/); [KAIZEN™: DMAIC or DMADV](https://in.kaizen.com/blog/post/2015/06/19/dmaic-or-dmadv-which-one-to-use) — retrieved 2026-06-03.
- 8 wastes / DOWNTIME (and TIMWOOD origin) — [Process Excellence Network: The 8 Deadly Lean Wastes — DOWNTIME](https://www.processexcellencenetwork.com/lean-six-sigma-business-performance/articles/the-8-deadly-lean-wastes-downtime); [MoreSteam: The 8 Wastes & DOWNTIME](https://www.moresteam.com/toolbox/8-wastes); [Lean Enterprise Institute: The Eight Wastes of Lean](https://www.lean.org/the-lean-post/articles/the-eight-wastes-of-lean/) — retrieved 2026-06-03.
- Fishbone/5 Whys/Pareto/FMEA/poka-yoke as the canonical per-phase tools is long-established Lean Six Sigma body of knowledge `[unverified — training knowledge]` for the exact per-phase mapping; the DMAIC phase structure itself is verified above.
