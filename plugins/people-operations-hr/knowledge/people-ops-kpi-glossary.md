# People-Ops KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges below are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current salary survey or HR-benchmark source before using in a deliverable (§3 #8).

## Attrition & retention

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Annualized turnover %** | (Separations in period ÷ average headcount) × (12 ÷ months in period) | Rolling 12 mo | Always annualize a partial-period rate before comparing. |
| **Regretted vs non-regretted** | Regretted = departure the org wanted to keep; non-regretted = managed-out / performance | Per separation | The headline split — total turnover without it is noise (§3 #1). |
| **Voluntary vs involuntary** | Employee-initiated vs employer-initiated | Per separation | Different cause, different fix; never blend. |
| **First-year / early attrition** | Separations within 12 mo of hire ÷ hires | Hire cohort | A hiring-quality signal — route to TA (§3 #3). |
| **Replacement cost** | Recruiting + onboarding + ramp-to-productivity + lost productivity during vacancy | Per backfill | Commonly cited as a meaningful fraction of annual salary; **cite a dated source** before quoting a multiple (§3 #8). |
| **Cost of vacancy** | Daily value of the unfilled role × days open | Per open req | Makes "time-to-fill" a dollar number. |

## Hiring funnel

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Time-to-fill** | Req opened → offer accepted | Per req / median | Use median, not mean — a few stuck reqs skew the average. |
| **Time-to-hire** | First contact → offer accepted (candidate experience clock) | Per candidate | Distinct from time-to-fill; don't conflate. |
| **Funnel conversion** | Stage-to-stage pass rate: sourced→screen→onsite→offer→accept | Per req / cohort | The leaking stage localizes the bottleneck (§3 #3). |
| **Offer-accept rate** | Offers accepted ÷ offers extended | Rolling | Low accept rate often signals comp band or process, not sourcing. |
| **Quality-of-hire** | Composite: ramp speed + early-attrition + performance rating at N months | Hire cohort | Must be defined measurably or it's an assertion. |
| **Source-of-hire mix** | Share of hires by channel (referral / inbound / agency / sourced) | Rolling | Referral hires often outperform — segment quality by source. |

## Compensation

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Compa-ratio** | Salary ÷ band midpoint | Point-in-time | <0.8 or >1.2 flags an outlier worth a look. |
| **Range penetration** | (Salary − band min) ÷ (band max − band min) | Point-in-time | Position-in-range; clusters at min/max signal banding issues. |
| **Band spread** | (Max − min) ÷ min | Per band | Typical professional bands span a meaningful range; cite the survey. |
| **Pay compression** | New hires / counteroffers paid at/above tenured peers | Point-in-time | The cost of paying to the counteroffer (§3 #2). |
| **Raw pay gap** | Mean/median pay difference between groups, **uncontrolled** | Point-in-time | Not the finding on its own (§3 #5). |
| **Residual (controlled) pay gap** | Gap remaining after controlling for level/role/tenure/location/performance | Point-in-time | The actionable number; legal determination is counsel's (§2). |

## Engagement & performance

| Metric | Definition | Window | Note |
|---|---|---|---|
| **eNPS** | % promoters − % detractors on "would recommend as a place to work" | Per survey | Read segmented (team / tenure / manager), not company-wide (§3 #4). |
| **Engagement favorability** | % favorable on engagement-index items | Per survey | Pair with attrition risk; it's a leading indicator. |
| **Manager effectiveness** | Manager-index favorability + team-level attrition/engagement delta | Per survey | Localizes the largest controllable retention driver (§3 #7). |
| **Span of control** | Direct reports per manager | Point-in-time | Extreme spans correlate with engagement/attrition risk. |
| **Internal mobility rate** | Internal moves ÷ headcount | Rolling 12 mo | A growth-opportunity signal that suppresses regretted exits. |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
