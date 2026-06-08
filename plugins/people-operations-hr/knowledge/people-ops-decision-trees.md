# People Operations & HR — Decision Trees + 2026 Capability Map

> Canonical knowledge bank for `people-operations-hr`. **Traverse the relevant Mermaid tree
> top-to-bottom before choosing** a system, a level, a performance model, or a comp architecture.
> Volatile product/version/pricing facts in the capability map carry a retrieval date and a
> re-verify-at-use rider.

---

## Decision Tree 1: Level and Comp-Band Placement

Use when: placing a candidate at offer stage, assessing a promotion request, or resolving a
leveling dispute.

```mermaid
flowchart TD
  A[What is the primary question?] --> B{Placing a candidate at offer?}
  A --> C{Assessing a promotion request?}
  A --> D{Resolving a leveling dispute?}

  B --> B1{Do you have a published leveling rubric for this family?}
  B1 -->|No| B2[Build or borrow a rubric first — see leveling-matrix template]
  B1 -->|Yes| B3[Match candidate evidence to scope/impact/autonomy rubric for each level]
  B3 --> B4{Clear fit at one level?}
  B4 -->|Yes| B5[Assign that level — set offer within band at P50 or comp-ratio 0.90-1.05]
  B4 -->|Borderline between two levels| B6[Lean lower level, higher in band — avoid over-leveling]
  B6 --> B5

  C --> C1{Has the person operated at the next level's scope AND impact for ≥3 months?}
  C1 -->|No| C2[Not ready yet — document specific gaps; set a 3-month milestone]
  C1 -->|Yes| C3{Is the evidence documented in calibration or a mid-cycle check-in?}
  C3 -->|No| C4[Gather evidence; bring to next calibration before deciding]
  C3 -->|Yes| C5[Approve promotion — trigger comp adjustment to new band minimum or 0.90 comp ratio]

  D --> D1[Anchor the discussion to the rubric — scope, impact, autonomy for the disputed level]
  D1 --> D2{Is the dispute about current performance or future potential?}
  D2 -->|Future potential| D3[Future potential is not a leveling criterion — level current evidence only]
  D2 -->|Current performance| D4[Run a calibration with evidence summaries — use the rubric as arbiter]
```

**Leaf rule:** level decisions must be anchored to observable, documented scope and impact —
not tenure, credentials, title at a prior company, or manager advocacy. A promotion requires
sustained evidence at the next level, not a single strong project. Over-leveling at hire creates
a comp and expectations problem that is expensive to unwind.

---

## Decision Tree 2: Build-vs-Buy ATS / HRIS

Use when: choosing a new ATS or HRIS, or assessing whether the current system fits the company's
stage.

```mermaid
flowchart TD
  A[What system are you selecting?] --> ATS[ATS — Applicant Tracking System]
  A --> HRIS[HRIS — HR Information System]

  ATS --> A1{How many open reqs at peak?}
  A1 -->|<10 open reqs| A2[Lightweight tool adequate: Notion + typeform, Ashby Starter, or Lever Lite]
  A1 -->|10-50 open reqs| A3{Is structured hiring and scorecard workflow critical?}
  A3 -->|Yes| A4[Ashby or Greenhouse — both purpose-built for structured hiring]
  A3 -->|No — basic pipeline tracking| A5[Lever or Workable — simpler, lower cost]
  A1 -->|50+ open reqs| A6{Enterprise HRIS already selected with built-in recruiting?}
  A6 -->|Yes, Workday| A7[Workday Recruiting — accept lower UX in exchange for single-system integration]
  A6 -->|No or non-Workday| A4

  HRIS --> H1{Company size?}
  H1 -->|<25 employees| H2[Gusto — best payroll-first SMB system; low admin overhead]
  H1 -->|25-150 employees| H3{Is IT/device management + HR in one system valuable?}
  H3 -->|Yes| H4[Rippling — strongest IT+HR+payroll integration at mid-market]
  H3 -->|No — HR only| H5{Strong employee engagement/experience focus?}
  H5 -->|Yes| H6[HiBob or Bamboo — both strong mid-market UX; HiBob stronger on engagement]
  H5 -->|No| H7[BambooHR — solid HR workflow at reasonable cost]
  H1 -->|150-750 employees| H8{Multi-country payroll needed?}
  H8 -->|Yes| H9[Rippling Global or Workday — Rippling Global easier to stand up; Workday more configurable]
  H8 -->|No| H4
  H1 -->|750+ employees| H10[Workday HCM — enterprise standard; accept high implementation cost and timeline]
```

**Leaf rule:** buy before you build; adopt before you customize. The right HRIS is the one
the People team will actually use and maintain, not the most feature-rich one available.
HRIS migration is expensive — think one stage ahead. ATS and HRIS are often separate purchase
decisions; don't conflate them unless an enterprise suite (Workday) genuinely covers both well
for your stage.

---

## Decision Tree 3: Performance Model Selection

Use when: designing or redesigning a performance review cycle, or selecting a rating approach.

```mermaid
flowchart TD
  A[What is the company's primary goal for the performance system?] --> B{Differentiate performance for merit/promotion?}
  A --> C{Drive continuous feedback culture?}
  A --> D{Reduce manager bias and calibration inconsistency?}

  B --> B1{Company size?}
  B1 -->|<100 employees| B2[3-point scale — simple enough to calibrate consistently; enough signal for merit]
  B1 -->|100-500 employees| B3[5-point scale with strong rubric — more merit differentiation; requires robust calibration]
  B1 -->|500+ employees| B4[5-point or narrative + summary rating — enterprise tooling often drives this; invest in calibration]

  C --> C1{Is there an existing 1:1 and check-in culture?}
  C1 -->|Yes| C2[Add quarterly structured check-ins as a formal artifact; make them the primary record]
  C1 -->|No| C3[Start with bi-weekly 1:1s + a simple template before adding a formal review layer]
  C3 --> C2

  D --> D1{When are ratings calibrated?}
  D1 -->|After ratings are written and communicated| D2[Wrong order — calibration must happen BEFORE ratings are communicated]
  D1 -->|Before ratings are communicated| D3{Are calibration sessions evidence-first?}
  D3 -->|No — manager advocacy is driving outcomes| D4[Redesign: submit evidence summaries before the session; go reverse-seniority]
  D3 -->|Yes| D5[Calibration model is sound — monitor for distribution drift and recency bias]

  B2 --> E[Pair the rating scale with a calibration pre-work packet and a debrief facilitation guide]
  B3 --> E
  B4 --> E
  C2 --> E
  D5 --> E
```

**Leaf rule:** no rating scale prevents bias by itself — the discipline is in the calibration
process. Pre-calibrate (before communication), use evidence summaries, go reverse-seniority in
the session, and document recalibrations. A 5-point scale without calibration is noisier than a
3-point scale with it.

---

## 2026 Capability Map — HR Tech Platforms

_Retrieved 2026-06-08. Product positioning, pricing tiers, and feature coverage are volatile —
re-confirm at time of use. This is orientation, not a procurement recommendation._
_[verify-at-use]_

### ATS — Applicant Tracking Systems

| Platform | Best fit | Notes |
|----------|----------|-------|
| **Greenhouse** | Mid-market to enterprise, structured hiring focus | Strong scorecard workflows, strong integrations, market leader for 100–2000 person companies. Higher cost than lighter tools. |
| **Ashby** | Growth-stage startups, analytics-first TA teams | Modern UX, built-in analytics, strong structured-interview support. Growing market share in Series A–C companies. |
| **Lever** | Mid-market, CRM-first recruiting | Good candidate relationship management, reasonable structured hiring. Less analytics depth than Ashby. |
| **Workday Recruiting** | Enterprise (1000+ employees already on Workday HCM) | Accept UX trade-offs for single-system integration. Not recommended as a standalone ATS. |
| **Workable** | SMB, <50 open reqs | Easy to use, reasonable cost, limited structured-hiring depth. |

### HRIS — Human Resources Information Systems

| Platform | Best fit | Notes |
|----------|----------|-------|
| **Gusto** | <150 employees, payroll-first | Best-in-class payroll UX for SMB. Benefits administration strong for US companies. Limited HR workflow depth. |
| **Rippling** | 50–750 employees, IT + HR integration | Strongest IT/device management + HRIS + payroll combo. Mid-market sweet spot. Global payroll available. |
| **BambooHR** | 50–500 employees, HR workflow focus | Clean UX, solid performance and onboarding modules, no native payroll. Requires payroll integration. |
| **HiBob** | 50–500 employees, engagement + modern UX | Strong employee experience / engagement features. Popular in Europe and with remote-first companies. |
| **Workday HCM** | 750+ employees, enterprise | The enterprise standard. High implementation cost (typically $200K–$1M+ for mid-enterprise). Highly configurable; requires dedicated admin. |
| **Personio** | European companies, SMB–mid-market | Strong for EU compliance and multi-country European payroll. Less relevant for US-primary companies. |
| **Carta Total Comp** | Startup equity + cash benchmarking | Not a full HRIS; useful for comp benchmarking for venture-backed companies, especially for equity data. |

### Performance & Engagement Platforms

| Platform | Best fit | Notes |
|----------|----------|-------|
| **Lattice** | 100–1000 employees, performance + engagement | Strong performance review, OKR, and engagement survey workflows. Widely adopted in Series B–D companies. |
| **CultureAmp** | 200+ employees, engagement-first | Best-in-class engagement survey and analytics. Benchmarks are strong. Performance module exists but engagement is the primary strength. |
| **Leapsome** | 100–500 employees, learning + performance | Strong for companies wanting performance + learning in one tool. European origin; strong EU customer base. |
| **15Five** | 50–500 employees, continuous feedback focus | Focus on manager effectiveness and continuous feedback. Good for building 1:1 culture. |
| **Workday Peakon Employee Voice** | Enterprise (already on Workday) | Integrated engagement signal within Workday. Accept a less best-of-breed survey product for single-system convenience. |

> Provenance: vendor positioning derived from public documentation, G2/Capterra review landscapes,
> and TA/HR community benchmarks as of 2026-06-08. Market shares, pricing tiers, and feature
> coverage are volatile — re-verify at use. No invented products.

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — team constitution and seams.
- [`../best-practices/README.md`](../best-practices/README.md) — the named, citable rules.
- [`../skills/comp-bands-and-leveling/SKILL.md`](../skills/comp-bands-and-leveling/SKILL.md) —
  deep comp and leveling playbook.
- [`../skills/structured-hiring/SKILL.md`](../skills/structured-hiring/SKILL.md) — deep
  structured hiring playbook.
- Neighbor decision trees: `finance` (merit budget), `data-platform` (people data pipeline),
  `applied-statistics` (significance on attrition/pay-equity data).

_Last reviewed: 2026-06-08 by `claude`._
