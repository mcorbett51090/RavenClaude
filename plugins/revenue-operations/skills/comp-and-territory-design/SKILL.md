---
description: "Design a sales compensation plan (OTE split, quota multiple, accelerators, SPIFs, clawbacks) with explicit behavioral-consequence analysis; design a data-driven territory model (segmentation, potential scoring, assignment algorithm, equity analysis); model headcount capacity."
---

# Comp and Territory Design

**Purpose:** produce a comp plan and territory model that encode the GTM strategy in incentives —
and name the behavioral consequence of every mechanic before it is designed.

## When to use this skill

- Designing or redesigning a sales compensation plan.
- Allocating territories and named accounts for a new fiscal year.
- Setting quota from first principles.
- Modeling headcount capacity against a revenue target.
- Diagnosing behavioral problems traceable to comp design.
- Filling in the `templates/comp-plan-spec.md` template.

## Step 1: Define the strategy the plan must encode

Before touching any mechanic:

1. What is the primary revenue motion? (New logo, expansion, renewal, cross-sell, or a blend?)
2. What deal type / segment is the strategic priority? (Enterprise, mid-market, SMB, product-led?)
3. What behavior problem needs to be fixed (if this is a redesign)? (Sandbagging? Discounting?
   Segment avoidance? Customer neglect post-close?)
4. What behaviors is the current plan accidentally rewarding?

**Do not design any mechanic until you can answer these four questions.**

## Step 2: Set quota

### Top-down (plan-derived)

```
Individual quota = (Team revenue target ÷ quota-to-plan ratio) ÷ number of quota-carrying reps
```

The quota-to-plan ratio accounts for attrition, ramp, and the distribution of attainment:
typically 110-130% of plan for new-logo teams (not all reps hit 100%). Source the ratio from
historical attainment distribution or from peer benchmarks [cite source + date].

### Bottom-up (territory-potential)

```
Individual quota = Territory TAM × expected penetration rate × average ACV
```

Triangulate top-down and bottom-up; resolve the gap explicitly. If top-down quota exceeds
bottom-up territory potential for a rep's territory, fix the territory, reduce the quota, or
document the assumption being made.

### Stress test

Run the attainment distribution: at P10 (low performer), P50 (median), P90 (high performer) —
what is total company revenue? Does the P50 scenario hit plan? Flag if P50 < plan.

## Step 3: Design OTE and the comp plan mechanics

### OTE structure

| Role | Typical base/variable split | Notes |
| --- | --- | --- |
| AE (new logo) | 50/50 | High variable; pure hunting |
| AE (expansion) | 60/40 or 65/35 | More predictable motion |
| SDR | 70/30 | Activity-based; shorter cycle |
| SE / Solution Consultant | 80/20 | Support role; team plan often appropriate |
| Manager | 70/30 | Team performance; avoid individual quota |

### Quota multiple

```
Quota multiple = Annual quota ÷ OTE variable component
```

Common range: 4-6× for mid-market AEs; 3-5× for enterprise (longer cycle, higher ACV).
[Source: industry benchmarks — verify-at-use against current peer data.]

### Accelerators and decelerators

| Attainment | Rate | Purpose |
| --- | --- | --- |
| 0-50% | 0.5× or straight-line | Threshold to avoid paying full rate on low performance |
| 50-100% | 1.0× (straight-line) | Standard rate |
| 100-125% | 1.5-2.0× | Reward overperformance |
| 125%+ | 2.0-3.0× | Superlinear reward for significant overperformance |

**Behavioral consequence:** uncapped accelerators with no decelerator threshold → reps sandbag
to smooth earnings across quarters. Design consciously.

### SPIFs

A SPIF should have: a named target behavior, a defined measurement period (start and end date),
and a predefined evaluation plan. A SPIF with no end date becomes a permanent fixture and
stops driving incremental behavior.

### Clawback policy

Minimum: clawback for customer churn within 90 days of close (catches misrepresentation). Document
the trigger, the recovery mechanism, and the exception process.

## Step 4: Design territories

### Segmentation

Define the segmentation criteria:
- Firmographic: company size (employee count / revenue band), industry vertical.
- Geographic: region, metro, country (for field sales).
- Named vs. pooled: named accounts (assigned to a specific rep), pooled territory (any rep in
  the geo can work them).

### Potential scoring

For each account/territory, calculate:

```
Potential score = TAM estimate × penetration factor × propensity-to-buy score
```

Propensity-to-buy inputs: existing product signals (free trial, PLG usage), technographic fit
(uses complementary tools), engagement signals (marketing activity, website visits). Source the
model inputs; do not use "gut feel" as a propensity input.

### Assignment algorithm

Assign accounts to reps to equalize potential (not account count or revenue). Run the equity
analysis:

```
Gini coefficient of potential distribution across reps
```

A Gini > 0.3 indicates materially unequal territory distribution. Document any departure from
equal potential with an explicit rationale (new rep in ramp, strategic named account, etc.).

### Seniority is not a data point

A senior rep "earning" a premium territory because of tenure is a seniority tax on that account's
revenue potential. If a senior rep gets a preferred assignment, document the rationale in terms
of skill-match to account complexity — not tenure.

## Step 5: Model headcount capacity

```
Quota-carrying headcount needed = Team revenue target ÷ (average individual quota × expected attainment rate)
```

Layer in:
- Ramp schedule: a new hire is productive at N% in months 1-3, M% in months 4-6, 100% in month 7+.
- Attrition buffer: historical annual attrition × lead time to backfill (typically 3-6 months).
- Backfill lead time: average time from vacancy to productive rep; model this explicitly.

## Anti-patterns

- A comp plan designed without first naming the strategy it must encode.
- A hard-coded quota, OTE, or commission rate with no source, date, or methodology.
- Territory assignments that favor tenure over market potential without a documented rationale.
- SPIFs with no defined end date or success metric — they become noise.
- OTE set before quota is set (puts cart before horse; quota × quota multiple = OTE variable).
- No clawback policy — creates an incentive to close deals at any cost, including misrepresentation.

## Output

A completed `comp-plan-spec.md` with: behavioral-strategy mapping, OTE structure, quota
methodology (top-down + bottom-up reconciled), comp mechanics with behavioral-consequence notes,
territory model with equity analysis, and capacity model. Pass to `revops-lead` for operating
model fit; pass to `pipeline-forecast-engineer` for coverage sizing.
