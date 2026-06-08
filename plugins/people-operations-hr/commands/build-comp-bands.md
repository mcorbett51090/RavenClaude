---
description: "Build a compensation band framework for a company: establish job architecture, source market data, construct bands with midpoints and range spreads, design a leveling rubric, and produce a merit matrix."
argument-hint: "[company stage and size, e.g. 'Series B, 120 employees, fully remote US' or '500-person public company, 3 geo tiers']"
---

You are running `/people-operations-hr:build-comp-bands`. Use the
`performance-and-comp-analyst` discipline and the `comp-bands-and-leveling` skill.

## Steps

1. **Confirm company context.** Extract from the argument (or ask): company stage, headcount,
   remote/office/hybrid footprint, geo spread, job families in scope, current comp philosophy
   (if any), and available market data sources.

2. **Traverse the comp-bands-and-leveling skill.** Read
   [`../skills/comp-bands-and-leveling/SKILL.md`](../skills/comp-bands-and-leveling/SKILL.md)
   and follow the operating loop.

3. **Build the job architecture.** Define job families and a level taxonomy (IC + management
   tracks). Name the scope/impact/autonomy criteria for each level. Use
   [`../templates/leveling-matrix.md`](../templates/leveling-matrix.md) for the leveling rubric.

4. **Source and document market data.** Identify which sources are available (Radford, Levels.fyi,
   Glassdoor, Carta, Culpepper, Mercer — see skill §2 for the comparison table). Document
   sources and their confidence level. Flag: "verify percentile figures at time of use — market
   data ages quickly."

5. **Choose the market percentile anchor.** Recommend P50, P65, or P25–P40 based on company
   stage, equity richness, and competitive position. State the rationale.

6. **Construct the bands.** Produce a band table: Job Family × Level → Minimum / Midpoint /
   Maximum. Show range spread. Include geo-differential tiers if applicable.

7. **Design the merit matrix.** Build a performance-rating × position-in-band matrix. Show
   sample % increases. Flag if the matrix is functionally flat.

8. **Pay equity check design.** Describe the unadjusted and adjusted gap methodology and
   recommend an audit cadence (post-merit-cycle minimum, annually otherwise).

9. **Emit the Structured Output block.** Include: job families covered, levels defined, market
   data sources, percentile anchor chosen, band table summary, merit matrix, and handoff
   recommendations (finance for merit-pool budget; people-analytics-engineer for pay-equity
   analysis; talent-acquisition-strategist for offer-stage application).
