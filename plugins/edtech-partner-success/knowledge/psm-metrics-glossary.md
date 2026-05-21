# PSM metrics glossary — definitions, formulas, pitfalls, EdTech overlays

> **Last reviewed:** 2026-05-21. Research-distilled glossary covering ~25 customer-success metrics with definitions, formulas, common pitfalls, when-to-use guidance, current benchmarks (sourced + dated), and EdTech-specific adaptation notes. Sources: HBR (NPS, CES origins), JAMS (Baehre 2021 NPS critique), KeyBanc/Sapphire 2024, OpenView/High Alpha 2024, Bessemer Cloud Computing Metrics, EdWeek MarketBrief, LearnPlatform. Refresh when: (a) SaaS benchmark medians shift materially in a new annual report, (b) a peer-reviewed paper changes the academic consensus on NPS / CES predictive validity, (c) an EdTech-specific NRR/GRR benchmark finally surfaces from Tyton Partners / HolonIQ, or (d) license-utilization data in K-12 moves significantly from the EdWeek MarketBrief baseline.

This file is the **glossary the PSM and analyst point to** when a metric definition is ambiguous, a formula is contested, or someone asks "which metric should we lead with?" Companion to [`customer-success-frameworks.md`](customer-success-frameworks.md) (which names the frameworks the metrics serve) and [`partner-health-score-drift.md`](partner-health-score-drift.md) (which handles the recalibration playbook).

**Confidence notation:** **High** = primary source verified or multi-source consensus; **Medium** = single credible source or practitioner consensus; **Low** = directional only or single vendor source.

---

## Revenue and retention

### 1. NRR — Net Revenue Retention

- **Definition.** Percentage of recurring revenue retained from an existing customer cohort over a period, *including* expansion, contraction, and churn.
- **Formula.** NRR = (Starting MRR/ARR + Expansion − Contraction − Churn) / Starting MRR/ARR × 100. Use the same cohort at both endpoints; do **not** include new logos acquired during the period.
- **Convention.** Rolling 12-month cohort. Dollar-based, not logo-based. Recurring only — exclude one-time and services revenue. Report constant-currency for cross-period comparison.
- **Pitfalls.** (a) Cohort handling — new logos inflate the metric. (b) Currency effects can move NRR by several points. (c) Including one-time / services revenue overstates.
- **Benchmark (2024-2025).** Public SaaS median ~110%, best-in-class >120% (High Alpha 2024). Private SaaS median ~101%, top quartile 108-110% (KeyBanc/Sapphire 2024, n=104). By ACV: Enterprise (>$100K ACV) ~118%, Mid-Market ($25-100K) ~108%, SMB (<$25K) ~97% — *single-source aggregation, treat as directional*. **Confidence: High** on public-SaaS median; **Medium** on segment splits.
- **EdTech note.** No clean public EdTech-segment NRR benchmark exists as of 2026-05. Treat horizontal SaaS as the floor; adjust for annual-renewal-dominance, enrollment-capped expansion ceilings, summer-trough effects, and ESSER-cliff K-12 budget pressure.

> Sources: High Alpha 2024 (https://www.highalpha.com/saas-benchmarks/2024); SaaSletter KeyBanc 2024 (https://www.saasletter.com/p/2024-keybanc-sapphire-saas-benchmarks).

### 2. GRR — Gross Revenue Retention

- **Definition.** Same cohort as NRR, but excludes expansion. Caps at 100%.
- **Formula.** GRR = (Starting MRR/ARR − Contraction − Churn) / Starting MRR/ARR × 100.
- **What it reveals that NRR hides.** A company with NRR 120% but GRR 80% is masking heavy churn with concentrated expansion in a few big accounts — fragile growth.
- **Benchmark.** KeyBanc 2024 private SaaS median GRR ~87%, top quartile >92%. Public SaaS commonly 90%+. **Confidence: High.**
- **EdTech note.** Annual K-12 budget cycles and board-political risk pressure GRR structurally. A 5-point GRR drop in one year is not automatically a product problem in EdTech — it can be a budget event. Pair with logo retention to disambiguate.

### 3. Logo retention

- **Definition.** Percentage of customer accounts retained period-over-period, dollars-agnostic. Caps at 100%.
- **Formula.** Logo Retention = (Logos at end of period from starting cohort) / (Logos at start of period) × 100.
- **When it's the honest signal.** When dollar retention is propped up by expansion in a few big accounts. A 92% logo / 115% NRR company is *losing* customers but growing dollars from the rest — fine if intentional (moving upmarket), alarming if accidental.
- **EdTech note.** A district loss is *one logo* but often hundreds-to-thousands of users. Logo retention is the leading indicator of segment-wide trouble (a competitor winning a state, a state-level procurement change).

> Source: Churnkey (https://churnkey.co/blog/gross-retention-vs-net-retention-vs-logo-retention-what-they-are-how-to-optimize-them/).

### 4. Renewal rate

- **Definition.** Per-event metric: of contracts up for renewal in the window, what % renewed.
- **Formula.** Renewal Rate = (# of renewed contracts) / (# of contracts up for renewal) × 100.
- **Difference from retention.** Retention is *cohort-period* (did the customer base survive the year?); renewal is *per-event* (when given the chance to leave, did they re-sign?).
- **Pitfall.** Mixing auto-renewals with active-decision renewals overstates the metric. Segment by renewal type, especially in EdTech where auto-renewal is rare.
- **EdTech note.** Renewal rate is *the* CS metric for K-12 because most contracts are annual and require active board / admin re-approval; very few auto-renew. Higher-ed varies by contract type; corporate L&D often auto-renews unless cancelled.

### 5. CLV / LTV — Customer Lifetime Value

- **Heuristic formula.** LTV = ARPA × Gross Margin % / Churn Rate. ARPA = average revenue per account; annualize.
- **Cohort-based formula.** Sum the actual revenue from a cohort over its observed lifetime, discounted for time value; project only after cohorts mature (12-18 months SMB, 24-36 months enterprise).
- **Trade-off.** Heuristic assumes steady-state churn — overstates LTV for new customers (early churn is higher) and understates for long-tenured. Cohort is more accurate but data-hungry.
- **Why LTV/CAC is the popular ratio.** Industry rule: target LTV/CAC ≥ 3.0x.
- **EdTech note.** District contracts are typically multi-year with rolling re-signs; cohort approach is more honest than heuristic. K-12 churn curves are *seasonal* (clustered at year-end), not smooth — single-rate heuristics distort.

### 6. CAC payback period

- **Definition.** Months for gross profit from a new customer to cover their acquisition cost.
- **Formula.** CAC Payback (months) = CAC / (ARPA × Gross Margin %).
- **Why increasingly preferred over LTV/CAC.** Cash matters more in a high-rate environment. LTV/CAC hides capital-tied-up duration; CAC payback measures it directly.
- **Benchmark (Bessemer).** <18 months "good," <12 months "better," <6 months "best." David Skok's classic SaaS rule: <12 months. **Confidence: High.**
- **EdTech note.** Adjust working assumptions **upward 6-12 months** vs. horizontal SaaS, because of longer procurement cycles, lower K-12 ACVs, and seasonal sales windows.

> Source: Bessemer, "Cloud Computing Metrics" (https://www.bvp.com/atlas/cloud-computing-metrics).

---

## Engagement and experience

### 7. NPS — Net Promoter Score

- **Origin.** Reichheld, "The One Number You Need to Grow," HBR December 2003 (verified primary source).
- **Calculation.** Single question 0-10 scale: "How likely is it that you would recommend [product] to a friend or colleague?" Promoters = 9-10; Passives = 7-8; Detractors = 0-6. **NPS = %Promoters − %Detractors.** Range: −100 to +100.
- **Update (2021).** Reichheld, Darnell & Burns, "Net Promoter 3.0," HBR Nov-Dec 2021, introduced **Earned Growth Rate** — accounting-audited revenue from existing customers + their referrals — as a CFO-validatable complement.
- **Academic critique.** Baehre, O'Dwyer, O'Malley & Lee (2021, *Journal of the Academy of Marketing Science*) — only the *brand-health* NPS variant (surveys potential customers, not just existing) predicts sales growth; the original customer-only NPS does not robustly predict growth. Methodological concerns: arbitrary cut points, large passive group ignored, single-question fragility.
- **Pitfalls.** (a) Sample bias — only happy customers respond. (b) Cultural variance — cross-region comparisons mislead. (c) Single-question fragility.
- **EdTech note.** Survey *who*? K-12 has three personas — student, teacher, administrator. Each gives wildly different NPS. Always segment. NPS as "recommend to a friend" is structurally weak in K-12 where teachers and admins don't have peer-purchasing-power. CSAT and CES travel better.

> Sources: HBR (https://hbr.org/2003/12/the-one-number-you-need-to-grow); HBR (https://hbr.org/2021/11/net-promoter-3-0); Baehre et al. 2021 JAMS (https://link.springer.com/article/10.1007/s11747-021-00790-2).

### 8. CSAT — Customer Satisfaction

- **Calculation.** CSAT = (# positive responses, typically top-2-box on a 5-point scale) / (total responses) × 100.
- **Scales.** 1-5 (dominant) or 1-7 (finer granularity).
- **Transactional by default.** Triggered post-interaction ("How satisfied were you with this support ticket?").
- **When to use.** Quality control on specific interactions — support tickets, onboarding milestones, training sessions.
- **Pitfall.** Top-box-only vs. top-2-box — same survey produces different headline numbers. Pick one and hold.
- **EdTech note.** Use post-PD-session CSAT to gauge teacher-training quality; post-support-ticket CSAT like any vendor. Don't conflate transactional CSAT with relational outcome.

### 9. CES — Customer Effort Score

- **Origin.** Dixon, Freeman & Toman, "Stop Trying to Delight Your Customers," HBR Jul-Aug 2010 (CEB/Gartner research, n=75,000+).
- **Calculation.** Modern variant — 7-point agreement scale: "[Company] made it easy to handle my issue" (Strongly Disagree → Strongly Agree). Higher = better.
- **Why CES outperforms NPS for retention in service contexts.** Dixon's research: effort dissatisfiers drive disloyalty more than satisfiers drive loyalty.
- **When to use.** Post-support-interaction, post-onboarding-task, post-renewal-process. Diagnostic for friction.
- **EdTech note.** Apply to teacher-side workflows (rostering, content authoring, gradebook integration). *Effort-to-set-up-a-class* is the kind of metric that predicts whether the teacher will use you next year.

> Source: HBR (https://hbr.org/2010/07/stop-trying-to-delight-your-customers).

### 10. TTV / TTFV — Time-to-Value / Time-to-First-Value

- **Definitions.** TTFV = time from purchase/sign-up to *first* meaningful outcome. TTV = time to realize *full* anticipated value.
- **Vendor-side vs partner-side.** Vendor-side instrumented (user completed first key action). Partner-side defined by the partner's success criterion. They often disagree; the partner's definition drives renewal.
- **Pitfall.** Activation as a proxy for value — logging in is not value.
- **EdTech note.** Define **persona-specific TTFV**. For a teacher: first formative-assessment insight (perhaps 6 weeks). For a student: a single productive class period. For a district admin (the buyer): the first usage report. Day-0-from-signup cohorting misleads — anchor cohorts to in-service / PD week or first day of term.

### 11. Adoption breadth vs depth

- **Breadth.** How widely the product is adopted across the customer's user base. Operationalized as % of licenses activated, DAU/MAU/WAU counts.
- **Depth.** How intensively activated users use the product. Operationalized as % of features used, frequency of use per active user, time-in-product per active user.
- **Why both matter.** Many fringe users = weak renewal position; few deep users = single point of failure on champion loss. Want both.
- **EdTech note.** EdTech breadth often looks healthy (rostered users) while depth is hollow (most never log in twice). **Always report seats actively used, not seats activated.**

### 12. DAU / WAU / MAU and stickiness

- **Definitions.** Distinct active users in a day / week / month. "Active" must be defined per product (logged in? performed a key action?).
- **Stickiness ratio.** DAU / MAU × 100 — "of users who used the product this month, what % used it on an average day."
- **Why misleading for B2B.** (a) B2B dips on weekends. (b) Infrequent-use tools (monthly reporting, quarterly planning) *should* have low stickiness by design. (c) Mature AI tools show low stickiness because users accomplish more per session.
- **EdTech-specific stickiness gotcha.** School calendars. DAU/MAU collapses in summer, weekends, holidays, testing windows. **Always report school-day-DAU** (DAU on days school is in session) or WAU during the school year.

### 13. Time-on-task / engagement minutes (EdTech-specific)

- **Definition.** Cumulative minutes a student spends *actively engaged* — excludes idle time, background tabs, passive consumption.
- **Common gaming patterns.** (a) "Open the tab and walk away" — many platforms require periodic interaction. (b) Click-spamming on gamified elements. (c) Easy-question farming for points/badges. (d) Group accounts (one student does the work, others ride). *Practitioner-observed gaming patterns; peer-reviewed citations not in this pass.*
- **What counts as engagement.** No industry standard. Define product-by-product: typically requires active interaction within a rolling window (e.g., keystroke or click every 60s).
- **No clean per-student weekly benchmark exists publicly** as of 2026-05. LearnPlatform's EdTech Top 40 is district-level. Single-vendor "average engagement minutes" claims are marketing, not benchmark.

---

## Health and risk

### 14. Customer health score

- **Single vs multi-component.** Single = one composite number. Multi-component = sub-scores (usage, support, sentiment, billing, business outcomes) rolled up to one with weights and surfaced individually.
- **0-100 vs RYG.** 0-100 enables trending and ML; RYG (Red <40, Yellow 40-74, Green ≥75) enables fast triage. Mature stacks publish both — 0-100 for analysts, RYG for executives.
- **Decay design.** Recent activity must count more than old activity. Exponential decay on recency (scores drop sharply after 7-14 days of inactivity). Without decay, a great-onboarding + 6-months-of-silence customer still looks green.
- **Pitfalls.** Single-dimension scores miss qualitative signals (champion departure, board change). Composite weights set once and never re-tuned drift out of predictive value.
- **Common claim:** Multi-component scores are ~34% more accurate than single-dimension (Gainsight-cited). **Confidence: Low** — vendor source, not peer-reviewed.
- **EdTech note.** Standard SaaS decay breaks in K-12 because of the academic calendar. A flat July customer is not unhealthy; a flat October customer is. **Calendar-aware decay is non-negotiable in EdTech.** See [`partner-health-score-drift.md`](partner-health-score-drift.md) for recalibration.

### 15. Churn rate

- **Logo (customer) churn.** Customers Lost / Customers at Start × 100.
- **Revenue churn.** Gross revenue churn excludes expansion; net revenue churn includes expansion (can be negative).
- **Monthly → annual.** Annual Churn ≈ 1 − (1 − Monthly Churn)^12. Do **not** multiply monthly × 12 — overstates at higher rates.
- **Voluntary vs involuntary.** Voluntary = customer chose to leave. Involuntary = payment / billing failure. Different problems, different fixes.
- **Benchmark.** B2B SaaS annual churn ~3.5% (Recurly 2025, single vendor source). **Confidence: Medium.**
- **EdTech note.** Involuntary churn is rare in K-12 (district POs don't bounce). Voluntary churn concentrates at fiscal-year-end. Monthly churn is meaningless in K-12 — use annual cohort.

### 16. Renewal risk score

- **Definition.** Probability of *non-renewal* at the next renewal date. Time-bounded and renewal-event-specific.
- **Distinct from health score.** Health is "are they in a good state generally?"; renewal risk is "will this specific contract close?" A green-health customer can have high renewal risk (champion just left, budget cut announced). A yellow customer can have low renewal risk (multi-year mid-term).
- **Best practice.** Maintain both. Surface disagreements as the action signal.
- **Pitfall.** Calibration drift without quarterly backtesting against actual renewals — score becomes a vibe.

---

## Operational

### 17. CSM book size

- **Typical ratios** (Gainsight enterprise sample). High-touch ~22 accounts/CSM; mid-touch ~49; low-touch ~144. ARR per CSM: median $1.4M, top quartile $4.2M. MuleSoft historically targeted $5M, scaled to $8M+ as automation matured. **Confidence: Medium** (vendor sources).
- **Tech-touch.** Up to 1,000:1 customer-to-CSM for pure tech-touch.
- **EdTech note.** EdTech ratios are lower in *seats-per-CSM* but higher in *accounts-per-CSM* — one district = one account but hundreds-to-thousands of users. **Calibrate by ARR per CSM, not account count, for cross-segment comparison.**

> Source: Gainsight (https://www.gainsight.com/blog/gainsight-horizon-ai-labs-what-is-the-right-csm-to-customer-ratio/).

### 18. First Response Time (FRT) and Resolution Time

- **FRT.** Time from ticket creation to first *human* response (not auto-acknowledgment).
- **Resolution Time.** Time from ticket creation to ticket closure.
- **B2B SaaS benchmarks.** Email FRT 4-6 hours target, top quartile <4 hours. Live chat FRT 30-60 seconds. Average resolution ~82 hours / 3.4 days across industries; B2B SaaS simple tickets 24-48 hours.
- **EdTech note.** Resolution time *during the school day* is far more load-bearing than 24/7. A broken login at 8:30 AM Monday is an outage; the same issue at 8:30 PM is not. **Track school-hours SLA separately.**

### 19. QBR / EBR cadence

- **QBR (Quarterly Business Review).** Operational, day-to-day stakeholders, every 3 months. Focus: usage, adoption, near-term objectives.
- **EBR (Executive Business Review).** Strategic, executive-level, semi-annual or annual. Focus: partnership strategy, business outcomes, multi-year roadmap.
- **Tiered approach.** Tier 1 (enterprise / strategic): fully customized; executive participation. Tier 2 (mid-market): semi-customized template. Tier 3 (SMB): automated dashboards or async briefings.
- **EdTech note.** Schedule the EBR ahead of the budget-build window (typically Jan-Mar for July-1 fiscal year) so the success story enters the budget conversation. See [`../templates/qbr-deck-outline.md`](../templates/qbr-deck-outline.md).

### 20. Touchpoint cadence

- **High-touch.** Weekly during onboarding, monthly steady-state, quarterly QBR, annual EBR.
- **Low-touch.** Monthly automated check-in + scheduled milestone touches; quarterly review at most.
- **Tech-touch.** In-product nudges + automated email; no scheduled human touch by default; trigger-based escalation.
- **EdTech note.** Add **term-aligned** touches: pre-school-year readiness call (Aug), mid-semester check (Oct), assessment-window support (varies), renewal conversation (Mar-May for July fiscal year). Calendar-driven, not just cadence-driven.

---

## EdTech-specific metrics

### 21. License utilization (seats purchased / activated / actively used)

Three numbers, three meanings:

- **Seats purchased** — contract count.
- **Seats activated** — % of purchased seats with at least one login ever.
- **Seats actively used** — % of purchased seats meeting a usage threshold (e.g., 10+ hours per semester, or weekly use during school year).

**The K-12 gulf.** EdWeek MarketBrief / LearnPlatform reporting: **~37% of K-12 licenses never activated**, **~30% of licenses never used (median)**, and only **~5% of student licenses are "fully used"** (10+ hours between assessments per LearnPlatform). Mid-sized districts waste $200K-$400K/year on unused licenses. **Confidence: High** on these figures.

**Pitfall.** Reporting activation-only utilization to a district renewal — they have access to the same data via their LMS/SIS dashboards. Will be caught.

**EdTech note.** This is the metric that most differs from horizontal SaaS — and because of the gulf, it's the **lead indicator for renewal risk in K-12**.

> Sources: EdWeek MarketBrief, "More than $1 billion in K-12 Ed-Tech Licensing Fees Go to Waste" (https://marketbrief.edweek.org/education-market/more-than-1-billion-in-k-12-ed-tech-licensing-fees-go-to-waste/2019/11); Evelyn Learning analysis (https://www.evelynlearning.com/blog/the-hidden-cost-of-edtech-sprawl-how-k-12-districts-are-drowning-in-unused-software-and-what-it-leaders-can-do-about-it).

### 22. Rostering health

- **Definition.** Health of the SIS → product roster sync. Two components:
  - **Roster completeness** — % of expected students / teachers / classes present in the product vs. district's source-of-truth roster.
  - **Last-sync age** — time since last successful sync from Clever / ClassLink / direct OneRoster API.
- **Standards.** OneRoster (1EdTech) is the dominant interoperability standard. Clever and ClassLink dominate US K-12 rostering. Daily sync is the common pattern.
- **Pitfall.** A "successful" sync that imported a *partial* roster (vendor-side filter mismatch) reports green when it's red. Reconcile counts, not just sync-job status.
- **EdTech note.** Rostering health is *invisible to product analytics* but lethal. A broken sync silently drops adoption; the vendor doesn't know until the teacher complains. **Check rostering health before declaring a partner red on engagement** (see [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md)).

### 23. Outcome metrics (the partner cares about)

- **Examples.** Proficiency growth (pre/post-assessment delta), mastery rate (% of standards mastered), normalized score gains, certification completion rate, course completion rate, knowledge retention (spaced-repetition retention checks).
- **Why they matter more than engagement in EdTech.** Engagement is the vendor's leading indicator; outcomes are the buyer's renewal criterion. A high-engagement, low-outcome customer churns at renewal regardless of usage data.
- **Pitfall.** Self-reported outcome metrics (the product grades the product) lack credibility. Pair with external validation (state-test correlation, third-party-assessment correlation) where possible.

### 24. Family / parent engagement metrics (K-12)

- **Definition.** Engagement of the parent / guardian persona, distinct from the student persona.
- **Metrics.** Parent-portal logins, message open rates, conference attendance, % of parents logged in at least once per term, response rates to parent surveys.
- **Why separate.** Parent engagement is a leading indicator of student outcomes (well-documented in education research) but a *different* CS lever.
- **EdTech note.** Parent personas often use a different interface (parent app, weekly digest email). Measure separately; report separately in the EBR.

### 25. License-to-active-student ratio (LSR)

- **Definition.** Active students / licenses purchased — a single utilization-density indicator.
- **Why useful.** Combines breadth and density into one number renewal conversations can hang on.
- **EdTech note.** Often more conversational at the EBR table than two separate numbers. "We're at 28% LSR — typical of new-tool year-one — here's the play to get to 50% by next renewal."

---

## Decision aid — which metric to lead with

| Question the PSM / analyst is answering | Lead with | Pair with |
|---|---|---|
| Are we growing healthy revenue from existing customers? | **NRR** | GRR (to reveal whether expansion is masking churn) |
| Are customers leaving us? | **Logo retention + GRR** | Renewal rate (segments active-decision from auto-renew) |
| Will this specific customer renew? | **Renewal risk score** | Health score (look for disagreement) |
| Is the customer in a good state generally? | **Customer health score** (RYG for triage, 0-100 for trend) | Last QBR notes |
| Are we acquiring efficiently? | **CAC payback period** | LTV/CAC (long-horizon view) |
| Is the product getting used? | **Adoption breadth + depth** (seats activated + seats actively used) | DAU/MAU only if usage is intended-daily |
| Is the product working for the partner (EdTech)? | **Outcome metrics** (proficiency / mastery) | Engagement minutes (vendor-side leading indicator) |
| Are we delivering value early enough? | **TTFV** (persona-specific in EdTech) | Onboarding-stage CSAT |
| Is support delivering? | **FRT + Resolution Time + CSAT** | First-contact resolution rate |
| Is the partner happy with us as a vendor? | **NPS** (relational; segment by persona) | CES on key transactions |
| Where's the friction? | **CES** (transactional) | Top-deflection-driver analysis |
| (K-12) Are we at risk of district non-renewal? | **License utilization** (seats actively used) **+ outcome metrics** | Logo retention trend, renewal risk, rostering health |
| (K-12) Are we connected to the district properly? | **Rostering health** (completeness + last-sync age) | License activation rate |

---

## Refresh triggers for this document

Re-read and update when:

- A new annual SaaS benchmark report (KeyBanc / OpenView / High Alpha / Bessemer) publishes — NRR / GRR / CAC payback medians shift.
- A peer-reviewed paper materially shifts academic consensus on NPS / CES / CSAT predictive validity.
- An EdTech-specific NRR/GRR benchmark dataset surfaces from Tyton Partners, HolonIQ, or similar EdTech research firm.
- LearnPlatform / EdWeek MarketBrief publish updated K-12 license-utilization data.
- 1EdTech ships a new OneRoster version with breaking changes that shift rostering-health norms.
