---
name: comp-bands-and-leveling
description: "Build a defensible compensation band framework and leveling rubric from scratch: market data sourcing, band construction, leveling criteria, merit-cycle mechanics, and pay-equity guardrails."
---

# Compensation Bands and Leveling

**Purpose:** replace ad-hoc comp decisions with a documented, market-anchored, internally
consistent framework where every role has a level, every level has a band, every band has a
midpoint tied to a market percentile, and every offer and merit decision can be traced back to
a defensible methodology.

## The operating loop

### 1. Build the job architecture

Before you set a single comp figure, establish the taxonomy:

**Job families** — groups of roles with related skills and career progression (e.g., Engineering,
Product, Design, Sales, G&A). Typically 6–12 families for a company of 50–500.

**Levels** — the rungs in each family:
- Individual contributor track: typically IC1 (entry) through IC6–7 (principal/fellow). Most
  companies start with IC1–IC5 and add senior levels as the company matures.
- Management track: typically M1 (team lead/manager) through M5–6 (VP/C-suite). IC and
  management tracks are parallel — not a promotion from IC into management.

**Level rubric** — for each level, define **scope**, **impact**, and **autonomy**:
- **Scope:** what is this person responsible for? (individual task → project → program → org)
- **Impact:** what level of organizational impact do they have? (team → department → company →
  industry)
- **Autonomy:** how much direction do they need? (detailed guidance → general direction →
  self-directed → setting direction for others)

Template: [`../../templates/leveling-matrix.md`](../../templates/leveling-matrix.md).

### 2. Source market data

Use at least two market data sources for any band. Common sources [verify-at-use]:

| Source | Best for | Access |
|--------|----------|--------|
| **Radford / Aon** | Large-company benchmarks, tech | Paid survey participation |
| **Mercer** | Cross-industry, international | Paid subscription |
| **Levels.fyi** | Tech engineering roles, equity comp | Free / public |
| **Glassdoor / LinkedIn Salary** | Broad signal, less precise | Free / public |
| **Culpepper** | Mid-market + smaller company benchmarks | Paid subscription |
| **Carta Total Comp** | Startup equity + cash benchmarks | Free (Carta customers) |

For startups without survey access, Levels.fyi + Glassdoor + peer company job postings (where
comp is disclosed) are a defensible starting point — document the methodology.

**Choose a market percentile anchor:**
- **P50 (median)** — pay at market, no premium or discount. Common for companies with strong
  non-cash differentiation (equity, mission, brand).
- **P65–P75** — above-market cash; used by companies competing on cash (late-stage, public).
- **P25–P40** — below-market cash; must be offset by above-market equity or mission premium.
  Requires honest communication.

**Geo-differentials:** if the company has remote employees, decide on a geo-tiering policy:
- **Single band (national)** — everyone paid on the same scale; simplest, potentially
  expensive in LCOL markets.
- **Geo-tiered** — e.g., Tier 1 (SF/NY/Seattle at 100%), Tier 2 (Austin/Denver at 90%),
  Tier 3 (rest at 80%). Common; requires a maintenance process as employees move.
- **Local market** — each employee's comp anchored to their location. Complex to administer.

### 3. Construct the bands

For each level in each job family:

1. **Midpoint** = the market percentile anchor (e.g., P50 for this level and family).
2. **Band range** = typically 50–80% range spread around the midpoint.
   - Formula: `minimum = midpoint / (1 + range_spread/2)`, `maximum = midpoint * (1 + range_spread/2)`.
   - A 60% range spread at a $120,000 midpoint → minimum $96,000, maximum $144,000.
3. **Band overlap** — adjacent levels should overlap by ~15–25%. Overlap enables a newly
   promoted employee to start the new band above the minimum. Zero overlap means a promotion
   always requires an immediate pay increase.

**Comp ratio** = `employee_salary / band_midpoint`. A comp ratio of 1.0 = exactly at midpoint.
- Typical healthy distribution: 0.85–1.15.
- Below 0.80: likely underpaid; attrition risk.
- Above 1.20: likely above the band; requires a band refresh or a promotion path.

See `scripts/people_calc.py` for a comp-ratio calculator.

### 4. Design the leveling rubric

Write a level rubric for each family × level combination. The rubric answers: "what does
someone at this level demonstrably do, own, and deliver?" Rubric dimensions:

| Dimension | IC3 example | IC4 example |
|-----------|-------------|-------------|
| Scope | Owns a component or feature | Owns a significant subsystem or workstream |
| Impact | Team-level | Team + adjacent team; influences product direction |
| Autonomy | Works from well-defined requirements; asks when uncertain | Scopes own work from goals; unblocks others |
| Collaboration | Primary collaborator is immediate team | Collaborates across functions; manages up |
| Craft | Produces quality work within established patterns | Extends patterns; improves team practices |

### 5. Administer the merit cycle

1. **Set the merit pool** — typically 2–5% of total compensation budget. Calibrate to market
   movement + company performance.
2. **Build the merit matrix** — performance rating × position in band:

   | Position in Band / Rating | Meets | Exceeds | Far Exceeds |
   |---------------------------|-------|---------|-------------|
   | Below midpoint (comp ratio <0.95) | 4% | 6% | 8% |
   | At midpoint (0.95–1.05) | 3% | 5% | 7% |
   | Above midpoint (>1.05) | 2% | 3.5% | 5% |

   Adjust matrix values to stay within the pool. A "flat" matrix (same % across all cells)
   signals the performance rating system is decorative.
3. **Promotion increases** — handle separately from merit. A promotion to the next level
   typically brings comp to the midpoint of the new level, or to a comp ratio of 0.90–1.0
   in the new band.
4. **Exception budget** — reserve 10–15% of the pool for equity adjustments (employees
   identified as below-band relative to peers) and counter-offer situations.

### 6. Run pay equity analysis

After each merit cycle:

1. **Unadjusted gap** — median comp by gender, race/ethnicity, and other protected
   characteristics. Report this number; suppressing it is selective disclosure.
2. **Adjusted gap** — control for level, tenure-in-level, location, and performance rating.
   The adjusted gap tests whether pay practices within-level are equitable.
3. **Remediation** — employees identified as materially below peers at the same level on the
   adjusted analysis get an off-cycle equity adjustment. Prioritize before the next merit cycle
   opens, not afterward.

## Anti-patterns

- Setting comp for a role after a finalist has been identified — anchoring is already active.
- A merit matrix that is functionally flat (2.5–3% for everyone regardless of rating or
  position in band).
- Bands without documented midpoints — "a range of $X to $Y" without a midpoint is
  unanchored.
- Reporting only the adjusted pay equity gap and suppressing the unadjusted one.
- Promotion increases applied inconsistently ("we only promote to the minimum of the new band"
  for some, "we match the counter-offer" for others).

## Output

A complete comp framework: job architecture (families × levels), sourced band table with
midpoints and range spreads, geo-differential policy, leveling rubric per family, merit matrix,
and a pay-equity analysis design. Use [`../../templates/leveling-matrix.md`](../../templates/leveling-matrix.md)
for the rubric artifact.
