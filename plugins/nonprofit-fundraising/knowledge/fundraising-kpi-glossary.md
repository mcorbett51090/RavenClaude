# Fundraising KPI glossary

The metrics a development office is judged on — formulas, the misreads, and where a benchmark needs a date. Benchmark figures are sector ranges that move yearly and vary by org size/maturity; each carries a source + retrieval date below or an `[unverified — training knowledge]` mark at point of use (§3 #8).

## Donor metrics

- **Donor retention rate** — % of donors who gave in period N who also gave in N+1. Overall sector retention sits ~43-45% (top performers 60%+); **first-time** retention runs ~20-30% vs **repeat** ~60-70% — the first-time-to-repeat cliff is where most donors are lost. Retention is the cheapest dollar (§3 #1). [verify-at-use]
- **LYBUNT** — **L**ast **Y**ear **B**ut **U**nfortunately **N**ot **T**his year: a donor who gave in the *immediately prior* year and not the current one. Highest-probability reactivation target (still warm). [verify-at-use]
- **SYBUNT** — **S**ome **Y**ear But Unfortunately Not This year: gave in *any* prior year, not the current one. Larger pool, lower reactivation probability, needs a distinct win-back track before the lapse window closes. [verify-at-use]
- **Donor lifetime value (LTV)** — `average gift × gifts per year × donor lifespan`. Lifespan can be derived from retention: `lifespan ≈ 1 / (1 − retention rate)` (convex — a small retention gain compounds LTV sharply). The [`../scripts/fundraising_calc.py`](../scripts/fundraising_calc.py) `donor-ltv` mode computes this and the retain-vs-acquire payback. [verify-at-use]
- **Average gift, donor count, new vs repeat split, RFM segments** — segment by **R**ecency, **F**requency, **M**onetary to direct cultivation hours (§3 #3).

## Efficiency metrics

- **Cost-to-raise-a-dollar (CRD)** — `fundraising spend ÷ revenue`, read **by channel, never blended** (§3 #4). Sector ranges: major gifts ~$0.05-0.10; grants ~$0.20; direct-mail renewal ~$0.20; events ~$0.30-0.50; direct-mail acquisition ~$1.00-1.25; overall blended often quoted ~$0.20. A channel above the blend is being subsidized by a cheaper one. [verify-at-use]
- **Return on fundraising investment (ROI)** — `revenue ÷ spend` (the inverse of CRD); the `cost-per-dollar` calculator mode prints both per channel.
- **Gift-processing cost** — the back-office cost per gift; relevant when small-gift volume is high relative to gift size.

## Pipeline & campaign metrics

- **Grant win rate, major-gift pipeline value, moves-management velocity** — velocity through identification → qualification → cultivation → solicitation → stewardship is the leading indicator of near-term major gifts, not meeting count (§3 #5).
- **Restricted / unrestricted mix** — over-indexing on restricted revenue starves the operating core; track the mix as a sustainability question (§3 #6).
- **Gift range chart (gift pyramid)** — the top-down feasibility tool for a campaign/annual-fund goal: the **lead (top) gift is conventionally ~10-25% of the goal**, and the **top ~10-20% of gifts carry ~50-80%+ of the total** (the 80/20 of campaign giving). A pyramid the rated prospect pool can't fill is a feasibility flag. The `gift-pyramid` calculator mode builds the table. [verify-at-use]
- **Officer portfolio size** — a full-time major-gifts officer can actively manage ~100-150 *qualified* prospects (fewer if each is deeply cultivated); an unqualified name list is a research backlog, not a portfolio. [verify-at-use]

## CRM / donor-database landscape (context, not endorsement)

The team is **CRM-neutral** (§2 — stores no donor records). Common nonprofit CRMs a development office may run include Blackbaud Raiser's Edge NXT, Bloomerang, Neon CRM, DonorPerfect, Salesforce Nonprofit Cloud (NPSP successor), Kindful, and Little Green Light. Metrics above are computed *from* whichever CRM the org uses; the plugin reads the org's reported numbers, it does not connect to the database.

## Sources (retrieved 2026-06-05)

- AFP — Fundraising Effectiveness Project (overall retention ~43-45%; donor-count trends): https://afpglobal.org/news/fundraising-effectiveness-project-data-q1-2025-shows-increases-dollars-raised-declining
- Bloomerang — Donor Retention Guide (first-time vs repeat retention; cost-to-retain vs cost-to-acquire): https://bloomerang.com/blog/donor-retention/
- Neon One — LYBUNTs and SYBUNTs explained (definitions): https://neonone.com/resources/blog/lybunts-and-sybunts-explained/
- Kindsight — Understanding donor lifetime value (LTV formula, retention→lifespan): https://kindsight.io/resources/blog/donor-lifetime-value/
- RallyUp — Calculating your cost-per-dollar raised (per-channel CRD ranges): https://rallyup.com/blog/fundraising-metrics-cost-per-dollar-raised/
- Bonterra — Nonprofit fundraising metrics and benchmarks (CRD, the ~$0.20 overall figure): https://www.bonterratech.com/blog/fundraising-metrics
- CapitalCampaignPro — gift range chart (lead gift 10-25% of goal; 80/20 concentration): https://capitalcampaignpro.com/capital-campaign-gift-range-chart/
- DonorSearch — gift range chart guide + calculator (pyramid structure, prospects-per-gift): https://www.donorsearch.net/resources/gift-range-chart-guide/

## Sourcing note

Benchmark figures above are sector ranges, dated and cited; figures elsewhere in the knowledge bank not carrying a source are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source and the org's own data before putting any figure in a client deliverable (§3 cite-or-mark rule).
