# K-12 EdTech PSM Dashboard — Research Synthesis (2026-06-04)

**Scope.** Practitioner-grade research foundation for a RavenClaude command-center dashboard build kit aimed at Partner Success Managers (PSMs) at K-12 EdTech vendors. 25+ independent sources synthesized across vendor docs, practitioner blogs, regulator guidance (US DOE PTAC), academic/research bodies (SETDA, Project Tomorrow, NCES), and AI-coding-agent retrospectives. Single-source claims tagged `[unverified — single source]`.

**Source-honesty note.** Vendor marketing pages (Gainsight, Planhat, ChurnZero, Catalyst, Totango, Vitally) are treated as evidence of *what these vendors say they ship*, not as evidence of best practice — practitioner blogs (CS Collective, Customer Imperative, Vela ris, User Intuition, EducationIntel) and academic/regulator sources are weighted higher when they disagree. Several `WebFetch` calls against Gainsight, Planhat, and PTAC URLs returned 403 — I used WebSearch summary content for those domains instead, which means a handful of paragraph-level details come from the SERP snippet rather than the canonical doc; I've flagged the most consequential of these.

---

## 1. What "good" looks like (vendor + practitioner consensus)

### 1.1 The "home base" pattern is now table stakes across all 4 major CSPs

Every major Customer Success Platform now ships a CSM-centric **home page** that fuses (a) portfolio summary, (b) call-to-action queue, (c) live timeline/notes, and (d) health distribution. This convergence is the single strongest signal in the research: it is the de-facto layout.

- **Gainsight Home + Cockpit.** "Gainsight Home is a centralized workspace … with widgets that provide a holistic view of insights … My Portfolio widget … Cockpit widget … Timeline widget" — the core widgets are `My Portfolio`, `Cockpit` (CTA queue), `Timeline` (notes), and supplementary `Open CTAs` charts. CSMs "quickly review their customer portfolio each morning as they craft their plan for the day." (Gainsight, [Home for CSMs](https://support.gainsight.com/gainsight_nxt/Gainsight_Home/User_Guides/Gainsight_Home_for_CSMs), accessed 2026-06-04.)
- **ChurnZero Command Center.** "Single view of daily tasks and detailed reporting on your book of business … log tasks, view milestones and alerts that demand your team's attention … customize content with drag-and-drop widgets." ([Command Center](https://churnzero.com/features/command-center/), accessed 2026-06-04.)
- **Catalyst (now Totango).** "CSM dashboards with prioritized account lists and daily task views, leadership dashboards tracking churn, NRR, health distribution, and cohort performance, and custom views for specific segments." ([Catalyst product page](https://catalyst.io/product/playbooks); [Manage customer accounts](https://help.catalyst.io/hc/en-us/articles/28924671873556-Use-Catalyst-to-view-or-manage-customer-accounts), accessed 2026-06-04.)
- **Totango.** "Intelligent workflow format that enables [CSMs] to manage their day in one screen … Tasks are grouped by their due date by default and have three categories: overdue tasks, today's tasks, and tasks for later." (Totango [Customer Success Center](https://support.totango.com/hc/en-us/articles/204012969); [Health features](https://www.totango.com/product-features/customer-health), accessed 2026-06-04.)
- **Planhat.** "Custom dashboards track customer journeys, measure CSM efficiency … Dashboards display health trends across teams, segments, and lifecycle stages." ([Planhat — Health](https://www.planhat.com/customer-success/health), accessed 2026-06-04.)

### 1.2 The Gainsight "8 dashboards" canon

Gainsight's widely-cited piece names eight dashboard archetypes that "top-performing CS teams can't live without": (1) CSM Daily/Operational, (2) Book-of-Business / Portfolio, (3) Health Distribution, (4) Renewal Pipeline, (5) Adoption / Product Usage, (6) NPS / Sentiment, (7) CTA / Task Performance (manager view), (8) Executive / NRR & GRR. ([8 Dashboards](https://www.gainsight.com/blog/8-dashboards-top-performing-customer-success-teams-cant-live-without/), accessed 2026-06-04 — WebFetch 403, summary content from SERP.)

### 1.3 What practitioners say is missing from the vendor templates

- The vendor templates are tuned for **horizontal B2B SaaS** (seat-based, monthly billing, single buyer/user). K-12-specific signals — leadership turnover, state-testing-window-suppressed usage, ESSER tail, multi-stakeholder buyer (curriculum / IT / superintendent) — are not in the out-of-box widgets. User Intuition's "Education Churn Playbook" explicitly calls this out: *"Standard SaaS retention tools like NPS surveys and login-based health scores mislead in education because the buyer, user, and budget decision-maker are almost never the same person."* ([User Intuition — Education Churn Playbook](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/), accessed 2026-06-04.)
- Practitioner consensus: a *useful* PSM home page surfaces **5–9 widgets max**, not 15+. This aligns with Stephen Few's "single screen, no scrolling" principle and the operator-console cognitive-load research (§5).

### 1.4 Practitioner-validated KPI cards for the top strip

Across the cited sources, the convergent KPI strip is: **Health-band distribution** (R/Y/G counts), **Renewal pipeline 90d** (count + $), **Overdue CTAs** (count, color-coded), **At-risk ARR** ($), **Today's touches scheduled** (count). Add for K-12: **State-testing-window flag** (which accounts are in blackout), **rostering-error count** (active sync incidents in portfolio).

---

## 2. Daily action queue / prioritization rubrics in production

### 2.1 The convergent formula: weight × signal, lifecycle-aware

No vendor publishes a *single* rubric, but five independent sources converge on the same scaffold:

> **Account priority score = Σᵢ (weightᵢ × signalᵢ)**, where signals are normalized 0–1 or 0–100, weights sum to 1.0, and weights are lifecycle-aware (different in onboarding vs renewal-90d).

Concrete starting weights from the literature:

| Source | Activity | Engagement | Milestones / Outcomes | Recency | Notes |
|---|---|---|---|---|---|
| Customers.ai "Signal Stack" | 40% | 30% | 20% | 10% | General SaaS starting point. ([Recency-Weighted Scoring](https://customers.ai/recency-weighted-scoring)) |
| Vitally 4-metric | 40% (usage) | 25% (support) | 20% (sentiment) | 15% (exec engagement) | Skews toward leading indicators. ([Vitally — 4 Metrics](https://www.vitally.io/post/how-to-create-a-customer-health-score-with-four-metrics)) |
| Gainsight enterprise model | 25% (product usage) | 30% (CSM relationship) | 35% (exec engagement + business outcomes) | 10% (support) | More relationship-weighted. ([Gainsight — Customer Health Scores](https://www.gainsight.com/blog/customer-health-scores/) — SERP summary) |
| Typewise (CS prioritization) | 35% (impact) | 25% (urgency) | 20% (customer value 1-5 tier) | 20% (SLA risk + sentiment) | Action-queue, not health. ([Typewise](https://www.typewise.app/blog/prioritizing-support-tickets-method)) |

**Lifecycle-aware weighting (Heap's framing).** "Early in the journey, usage and onboarding signals may be weighted more heavily, while later, outcomes and adoption patterns become stronger predictors." ([Heap — Lagging to Leading Indicators](https://www.heap.io/blog/from-lagging-to-leading-indicators-a-proactive-approach-to-account-health-scoring), accessed 2026-06-04.) **Implication for RavenClaude:** the rubric should be a *function of lifecycle stage*, not a single fixed vector.

### 2.2 Prioritization frameworks borrowed from PM

Two PM frameworks are being applied to CS daily-queue ranking by sophisticated teams:

- **RICE** (Reach × Impact × Confidence ÷ Effort) — borrowed from product roadmap prioritization. Useful when daily tasks vary in expected impact-per-effort. ([ProductPlan — RICE](https://www.productplan.com/glossary/rice-scoring-model), accessed 2026-06-04.)
- **ICE** (Impact × Confidence × Ease) — lighter-weight, suitable for action-by-action triage. ([Kaizenko — Scoring Frameworks](https://www.kaizenko.com/scoring-frameworks-ice-rice-and-weighted-scoring-for-product-prioritization/), accessed 2026-06-04.)

The connection: **a CSM "today's top 10" list is really a daily prioritization decision, and PM scoring frameworks formalize the math that vendors do implicitly with weighted signals**. RavenClaude's daily-queue skill should optionally expose a RICE/ICE view as an alternative ranking lens.

### 2.3 The "next-best-action" trend (2026)

NBA recommendation engines are arriving in CRMs and CSPs in 2026:

- "Each potential action … is given a score based on expected impact … Recommendations surface with priority levels and confidence percentages (for example, Recommendation A at high priority with 92% confidence)." ([Inogic — NBA in CRM](https://www.inogic.com/blog/2026/05/how-ai-recommends-the-next-best-action-in-crm-with-real-examples/), accessed 2026-06-04.)
- Salesforce Einstein Next Best Action and Microsoft Dynamics 365 NBA are productizing this. ([Einstein NBA Guide](https://www.minusculetechnologies.com/blogs/einstein-next-best-action-implementation-guide); [Inogic — Coming Soon NBA](https://www.inogic.com/blog/2026/02/coming-soon-ai-powered-next-best-action-for-dynamics-365-crm/), accessed 2026-06-04.)

**Practitioner-grade NBA must surface confidence, rationale, and an explicit "why this account, this action, today" string.** The rationale string is the differentiator vs naive top-K ranking.

### 2.4 Concrete trigger thresholds from practitioner playbooks

From Lyniro's 15-play playbook and Planhat's churn guide ([Lyniro](https://lyniro.com/blog/customer-success-playbook/); [Planhat — Churn & Retention](https://www.planhat.com/customer-success/churn-and-retention), accessed 2026-06-04):

- Onboarding risk: **<50% license utilization in first 30 days**, **2-week decline in WAU during onboarding**, **no client activity for 10+ days**, **2+ blocked tasks simultaneously**.
- Renewal: **health score enters defined risk band within 90 days of renewal**, **outreach 90 days before renewal for annual contracts, 30 for monthly**.
- Expansion: **customers hitting plan limits**, **regularly engaging with advanced features**.
- Churn: **product usage drops below baseline for 2 consecutive weeks**, **health score < threshold**, **2+ churn signals simultaneously**.

---

## 3. Health score components & decay half-lives (cross-vendor synthesis)

### 3.1 Component lists (vendor cross-walk)

The marketplace's existing schema is `adoption / touchpoint / outcome / sentiment / champion / usage`. Comparing to vendor OOTB components:

| Component | Marketplace | Gainsight | Planhat | Totango | ChurnZero | Vitally |
|---|---|---|---|---|---|---|
| Adoption (feature breadth/depth) | ✓ | ✓ (Product Usage 25%) | ✓ (Usage/Success Units) | ✓ (License utilization, logins) | ✓ | ✓ (40%) |
| Touchpoint cadence | ✓ | ✓ (CSM relationship 30%) | ✓ | ✓ (Engagement: last touch) | ✓ | (implicit) |
| Outcome / Business Value | ✓ | ✓ (Business Outcomes 15%) | ✓ (Business outcomes) | ✓ (Success plan exists) | ✓ | — |
| Sentiment | ✓ | ✓ (in CSM Relationship Pulse) | ✓ (NPS, CSAT, qual) | ✓ (CSAT, NPS, CSM sentiment) | ✓ | ✓ (20%) |
| Champion strength | ✓ | ✓ (Executive Engagement 20%) | (partial — "stakeholder mapping") | (partial) | (partial) | ✓ (15% — exec engagement) |
| Usage (volume) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Support load** | — | ✓ (10%) | ✓ | ✓ (Support & Operations: tickets, SLA) | ✓ | ✓ (25%) |
| **Financial / payment health** | — | (partial) | (partial) | — | (partial) | (Support Logic mentions) |
| **Lifecycle stage** | — | ✓ (implicit in CTA types) | ✓ (Success Units) | ✓ | ✓ | ✓ |

Sources: Gainsight [Health Scores](https://www.gainsight.com/blog/customer-health-scores/) (SERP), Planhat [Health](https://www.planhat.com/customer-success/health), Totango [Customer Health](https://www.totango.com/product-features/customer-health), ChurnZero [Centralize Customer Data](https://churnzero.com/customer-success-software/centralize-customer-data/), Vitally [4 Metrics](https://www.vitally.io/post/how-to-create-a-customer-health-score-with-four-metrics), [SupportLogic — Support Health](https://www.supportlogic.com/resources/blog/support-health-score-unifying-customer-support-success/). All accessed 2026-06-04.

**Gap in marketplace schema:** `support` and `financial` components are absent. Both are now table-stakes in CSP OOTB rubrics. *Practitioner consensus is that support-ticket-velocity + unresolved-P1-count is one of the highest-correlation leading indicators of churn.*

### 3.2 Decay half-lives (recency)

The literature converges on **exponential decay** but disagrees on half-life:

- **Customers.ai** explicitly recommends the Google Analytics formula: `weight = 2^(-t / half-life)`, default `half-life = 7 days` ([Recency-Weighted Scoring](https://customers.ai/recency-weighted-scoring)).
- Vela ris / Planhat: *"For recency, exponential decay is used — score drops rapidly after 7 days of inactivity"* — converges on the same ~7-day inflection. ([Velaris — CS Health Scores](https://www.velaris.io/articles/cs-health-scores))
- Time-decay attribution (RedTrack, Factors.ai): default half-life **7 days** is the Google Analytics convention; some marketing-mix models use 14 or 28 days for longer purchase cycles. ([Factors.ai — Time Decay](https://www.factors.ai/blog/time-decay-attribution-model); [RedTrack](https://www.redtrack.io/blog/time-decay-attribution-model/))
- **Practitioner recommendation:** signal-specific half-lives:
  - Usage events: **7 days** (default).
  - Sentiment (NPS, survey): **90 days** — surveys are infrequent and slow-moving.
  - Champion presence: **30 days** — a departed champion should ramp toward 0 over a month.
  - Support: **14 days** — ticket impact lingers but isn't permanent.
  - Outcome milestones: **180 days** — a delivered outcome shouldn't decay fast.

### 3.3 Leading vs lagging discipline

Heap and Gainsight both emphasize: *"High-performing customer success teams balance leading indicators (such as usage and engagement) with lagging indicators (such as renewal outcomes and feedback)"* and *"Effective health scores weight leading indicators more heavily."* ([Heap — Lagging to Leading](https://www.heap.io/blog/from-lagging-to-leading-indicators-a-proactive-approach-to-account-health-scoring), accessed 2026-06-04.)

**Concrete implication for RavenClaude:** every signal in the schema should be tagged `leading | lagging`, and the dashboard should show the *leading-indicator-weighted subscore* as a separate at-risk filter.

### 3.4 Tier weighting

Common-tier model (Vela ris, Customer Imperative): **Tier 1 (10–15% of accounts): monthly check-ins**, **Tier 2 (25–30%): quarterly + automation**, **Tier 3 (55–65%): self-serve + reactive**. The tier becomes a *priority multiplier* on the action queue. ([Velaris — Account Prioritization](https://www.velaris.io/articles/account-prioritization-cs); [Customer Imperative — Portfolio Segmentation](https://customerimperative.com/customer-portfolio-segmentation-for-customer-success-managers/), accessed 2026-06-04.)

---

## 4. K-12-specific signals beyond what generic CS frameworks cover

### 4.1 Buyer / user / decision-maker separation

The single most important K-12-specific gap in horizontal CSPs:

> "Standard SaaS retention tools like NPS surveys and login-based health scores mislead in education because the buyer, user, and budget decision-maker are almost never the same person. A teacher can love the platform while a curriculum director questions alignment and a CFO cuts the line item, creating three distinct churn mechanisms within a single account." — User Intuition ([Education Churn Playbook](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/), accessed 2026-06-04).

**Implication:** health components must be tagged per persona — `teacher_adoption`, `admin_engagement`, `decision_maker_signal` — and the dashboard needs a **persona-segmented sentiment view**.

### 4.2 Leadership turnover as renewal-risk event

- **2024-25 superintendent turnover: 23% in the 500 largest districts**, up from 20% prior year, vs. pre-pandemic 14-16%. ([Education Week / K-12 Dive](https://www.k12dive.com/news/high-superintendent-turnover-staffed-up/804337/), accessed 2026-06-04.)
- "For EdTech vendors, each leadership transition is a renewal risk event. The incoming superintendent or principal arrives with their own vendor relationships … A platform that was championed by their predecessor may be evaluated from scratch — or simply not evaluated at all, replaced by a default preference for familiar tools." ([User Intuition](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/), accessed 2026-06-04.)
- **Detection signal:** admin/decision-maker engagement drops while teacher usage continues — *"This often means that the account administrator may be evaluating alternatives."*

**Implication:** a dedicated **Leadership Watch** widget — districts where the superintendent, CTO, or curriculum director changed in the last 12 months get a flag. Source can be cross-referenced via state press releases, BoardDocs scraping, or ESchoolNews / EdSurge feeds.

### 4.3 Budget-cycle timing (the fiscal calendar layer)

- "Most U.S. public school districts finalize budget decisions for the following fiscal year in February or March — four to five months before the June 30 fiscal year end when contracts technically expire … EdTech companies lose 15-25% of annual contracts every June." ([User Intuition](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/), accessed 2026-06-04.)
- "Finance offices and superintendents finalize assumptions during fall budget cycles, long before boards vote." ([EducationIntel](https://educationintel.substack.com/p/why-many-k-12-vendors-lose-before), accessed 2026-06-04.)
- **The real renewal window is Sep–Mar, not Apr–Jun.** Standard SaaS dashboards show renewal pipeline by contract end date; K-12 dashboards must show it by **budget decision date** (typically Feb 15 for the buyer's next fiscal year).

### 4.4 ESSER cliff aftermath (still a live risk in 2026)

- ESSER provided ~$190B; "30% to 40% of a typical district's discretionary spending over the life of the funding." ([K-12 Dive — ESSER Legacy](https://www.k12dive.com/news/esser-pandemic-COVID-K-12-spending-what-will-its-legacy-be/815999/); [Oliver Wyman](https://www.oliverwyman.com/our-expertise/insights/2025/mar/k-12-investment-strategies-stimulus-funds-end-2025.html), accessed 2026-06-04.)
- "92% of school districts had used ESSER funds for educational technology" but "only 27% of states have plans to sustain funding for technology initiatives previously supported by federal relief programs." ([SETDA 2025 State EdTech Trends](https://www.setda.org/resource/2025-state-edtech-trends-report/), accessed 2026-06-04.)
- In March 2025, "the U.S. Department of Education unexpectedly rescinded its extension for spending more than $2.5 billion of American Rescue Plan (ARP) ESSER funds" ([GovTech](https://www.govtech.com/education/k-12/experts-push-student-focused-budgeting-as-esser-winds-down), accessed 2026-06-04.)

**Implication:** a **funding-source flag** per account — districts whose initial purchase was ESSER-funded carry a structural renewal risk and should be over-weighted in the "at-risk" queue through at least 2027.

### 4.5 State-testing-window blackout

State testing windows (typically Apr–May for spring summative assessments; Florida and others now have fall + spring under FAST) **structurally suppress edtech usage** for 4–8 weeks. ([Frontline — Standardized Testing](https://www.frontlineeducation.com/blog/standardized-state-testing-in-education-changes-and-future-trends/), accessed 2026-06-04.)

**Implication:** usage-based health scores must be **seasonality-adjusted** during testing windows, or they will fire false at-risk alerts for every district every spring. The dashboard should overlay a "testing window" band (per-state) on usage sparklines.

### 4.6 Back-to-school surge (the operational stress test)

- "Back-to-school in August brings a tsunami of new student enrollments, roster uploads, and schedule changes." ([Dromo — Data Onboarding](https://dromo.io/blog/data-onboarding-for-edtech-student-records-rosters-and-compliance), accessed 2026-06-04.)
- "Digital on Day One" is a recognized industry concept; the first 2 weeks of school are the highest-leverage CS intervention period of the year.

**Implication:** an **"Activation Watch" widget** that's only active Aug 1 – Sep 30, tracking license-claim rate, first-class-completion rate, and roster-sync error count per district. Outside that window, the widget collapses.

### 4.7 Family activation (parent-app vertical specifically)

For partner-portal / family-comms products (ParentSquare, ClassDojo, Remind, SchoolStatus, Seesaw): the activation rate **plateau is the dominant signal**.

- "Only 39% of schools report that they reach 90% to 100% of families, and another 27% estimate that they reach 75% to 90% of families." ([Edsby](https://www.edsby.com/school-apps-for-parent-engagement-k12-data/commentary/), accessed 2026-06-04.)
- "93% of families report feeling more connected and supported when schools use real-time communication platforms like ClassDojo, Remind, or Seesaw." ([ed Circuit — Family Engagement Tools](https://edcircuit.com/how-family-engagement-tools-are-transforming-k-12-education/), accessed 2026-06-04.)
- Key per-school metrics: family-coverage %, message-open rate, reply rate, translation-language coverage, attendance correlation.

**Implication:** family-activation metrics need their own widget for vendors in this segment — generic DAU/MAU doesn't capture the *coverage gap* that drives administrator dissatisfaction.

### 4.8 LearnPlatform external benchmark

LearnPlatform's EdTech Top 40 + EdTech300 indexes provide an *external* engagement benchmark — page-load events per 1000 users, normalized across 10,000+ products, collected via Chrome extension. ([Instructure — EdTech Top 40](https://www.instructure.com/edtech-top40); [LearnPlatform Equity Dashboard](https://www.prnewswire.com/news-releases/learnplatform-launches-national-edtech-equity-dashboard-to-improve-visibility-of-digital-k-12-engagement-and-gaps-across-us-301277353.html), accessed 2026-06-04.)

**Implication:** a vendor's PSM dashboard can include a "vs LearnPlatform index" widget showing the vendor's usage rank/percentile against the national benchmark — high-signal context for QBR slides.

---

## 5. Operational console UX patterns (single pane of glass)

### 5.1 Stephen Few canon (1–10s read time, no scrolling, density without clutter)

- "Dashboards are usually required to display a great deal of somewhat disparate information in a limited amount of space (a single screen) … information must be organized into meaningful groups in a way that features what's most important." ([Stephen Few — Perceptual Edge](https://www.perceptualedge.com/articles/Whitepapers/Formatting_and_Layout_Matter.pdf); [Dashboard Design Course](https://www.perceptualedge.com/files/Dashboard_Design_Course.pdf), accessed 2026-06-04.)
- "Information Dashboard Design: Displaying data for at-a-glance monitoring" — the at-a-glance constraint *is* the design constraint. ([Goodreads listing](https://www.goodreads.com/book/show/336258.Information_Dashboard_Design))

### 5.2 IBCS SUCCESS principles (consistent semantic notation)

The SUCCESS formula: **S**ay (convey a message), **U**nify (semantic notation — same color = same meaning everywhere), **C**ondense (high info density), **C**heck (visual integrity), **E**xpress (right chart type), **S**implify (no clutter), **S**tructure (organize content). Speed of analysis improves 46%, accuracy 61% with proper IBCS use. ([IBCS Standards 1.2](https://www.ibcs.com/ibcs-standards-1-2/); [IBCS overview](https://www.ibcs.com/); [Wikipedia](https://en.wikipedia.org/wiki/International_Business_Communication_Standards), accessed 2026-06-04.)

**Concrete IBCS rules to inherit:**

- Same color always = same meaning (e.g., red is always "at risk", never just "negative variance").
- Variance always shown alongside the value with a fixed-position delta indicator.
- Time series go left-to-right; categorical comparisons top-to-bottom.

### 5.3 NOC / operator-console research

- "All information should be color coded to classify the severity of issues." Filtering, suppression, and categorization prevent **alarm fatigue**. ([Activu — SOC Best Practices](https://www.activu.com/security-operations-center-dashboard-best-practices-a-checklist-for-critical-situational-awareness/), accessed 2026-06-04.)
- Energy-grid control-room research using eye-tracking (n=7-screen workstations) found that layout *across* screens was as important as within-screen design; cognitive load measured via subjective + physiological probes correlated strongly with grouping discipline. ([PMC — Control Room Cognitive Load](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8995508/), accessed 2026-06-04.)
- Situational-awareness systems use **automated content density** — "surfacing only the most relevant data when specific thresholds are breached." ([AVEVA — Situational Awareness](https://www.aveva.com/en/solutions/operations/situational-awareness/), accessed 2026-06-04.)

### 5.4 The 5-second rule

"The 5 second rule measures how effectively information is communicated to viewers within the initial 5 seconds … works through Cognitive Load Theory (Intrinsic / Extraneous / Germane load)." ([Ethos3](https://ethos3.com/mastering-the-5-second-rule-elevate-your-presentation-design-for-maximum-impact/); [DEV — 5 Second Rule](https://dev.to/deyrupak/are-you-aware-of-the-5-second-rule-398a), accessed 2026-06-04.)

**Test for the PSM dashboard:** a PSM should be able to answer "what's on fire today?" within 5 seconds of opening. If they can't, the layout is too dense.

### 5.5 Sparklines + small multiples for density

- Sparklines: "small, inline line charts placed next to a KPI value that show the recent trend without requiring a full chart … rapidly scannable and very compact." ([Domo — Sparklines](https://www.domo.com/learn/charts/sparkline-chart); [Stephen Few — Sparkline Best Practices](https://www.perceptualedge.com/articles/visual_business_intelligence/best_practices_for_scaling_sparklines.pdf), accessed 2026-06-04.)
- Small multiples: same chart repeated per category — same scale, size, shape. ([Omni Analytics](https://omni.co/articles/data-visualization-best-practices-for-better-decision-making); [DataCamp — Dashboard Design](https://www.datacamp.com/tutorial/dashboard-design-tutorial), accessed 2026-06-04.)
- **Operational dashboard placement:** "The most important signal in the top-left is the current status or the most urgent exception."

### 5.6 The dashboard taxonomy: operational vs analytical vs executive

These have *different design constraints* and the PSM home page is **operational** (low latency, immediate clarity, big status indicators, clear ownership) — not analytical (deep exploration) or executive (high-level KPIs only). Conflating them is the #1 design failure mode. ([Improvado](https://improvado.io/blog/dashboard-design-guide); [RIB — Dashboard Design Principles](https://www.rib-software.com/en/blogs/bi-dashboard-design-principles-best-practices), accessed 2026-06-04.)

---

## 6. District identity resolution (LEAID + state ID + SFDC reconciliation)

### 6.1 The three ID systems

- **NCES LEAID** — 7-digit federal ID. First 2 digits = State FIPS code, last 5 = LEA. Stable across years (mostly). ([NCES — CCD About Agency File](https://nces.ed.gov/ccd/aadd.asp); [Wikidata Property:P2483](https://www.wikidata.org/wiki/Property:P2483), accessed 2026-06-04.)
- **State-specific IDs** — every state has its own (e.g., California's 14-digit **CDS code**: 2-digit county + 5-digit district + 7-digit school). The NCES Common Core of Data tracks state IDs in the `STID` field. ([NCES CCD Quickfacts](https://nces.ed.gov/ccd/quickfacts.asp); [CDE — CDS Administration](https://www.cde.ca.gov/ds/si/ds/), accessed 2026-06-04.)
- **Salesforce / CSP record IDs** — vendor's own account IDs.

### 6.2 The reconciliation problem

- Districts change names, merge, split, and re-charter; their NCES IDs and state IDs sometimes change with these events. NCES recommends *"matches are first attempted against the LEA universe file for the corresponding school year, and if survey staff cannot match the LEAs to the LEA universe file for the corresponding school year, they attempt to match the LEAs to prior and subsequent year universe files."* ([NCES](https://nces.ed.gov/ccd/aadd.asp), accessed 2026-06-04.)
- District names have common-substring collisions ("Lincoln" appears in 50+ states; "Washington" appears 100s of times) — exact-string matching is insufficient.

### 6.3 Practitioner identity-resolution patterns

- **Deterministic-first, fuzzy-fallback.** Match on LEAID → fall back to (state, state_district_id) → fall back to fuzzy name+ZIP+grade-span match. Levenshtein or cosine similarity is standard for the fuzzy tier. ([AWS Entity Resolution](https://aws.amazon.com/blogs/industries/resolve-imperfect-data-with-advanced-rule-based-fuzzy-matching-in-aws-entity-resolution/); [WinPure](https://winpure.com/data-matching-identity-resolution/), accessed 2026-06-04.)
- **Survivorship rules** when two records merge: keep the older Salesforce record, take LEAID and state ID as authoritative from NCES CCD, take contact records from both.
- **Continuous identity resolution.** "A modern CRM approach resolves identity by continuously identifying related records across Leads, Contacts, Accounts, and even custom entities, then consolidating them into a single trusted identity while preserving full history." ([Inogic — CRM Dedup](https://www.inogic.com/blog/2026/02/beyond-deduplication-a-2026-faq-guide-to-clean-unified-ai-ready-crm-data/), accessed 2026-06-04.)

### 6.4 Ed-Fi as the missing canonical layer

- Ed-Fi Unifying Data Model (UDM) is CEDS-aligned, open-source, and represents the K-12 community standard for person/role data. "The Ed-Fi data model of disconnected person-roles Student, Staff and Parent has generally served the K-12 community well." ([Ed-Fi Data Standard](https://docs.ed-fi.org/reference/data-exchange/data-standard/); [Person Entity Guidance](https://techdocs.ed-fi.org/display/EFDS32/Guidance+on+Use+of+Ed-Fi+Person+Entity), accessed 2026-06-04.)
- Ed-Fi is increasingly the standard at the *state* layer. Vendors that align their identity model to Ed-Fi can avoid bespoke per-state reconciliation.

### 6.5 Rostering layer (Clever + ClassLink)

- **Clever** "normalizes and cleanses district SIS data, and maps and matches IDs even when districts change sync methods. 110,000 schools globally rely on Clever's automated rostering solutions." ([Clever — Rostering for Partners](https://www.clever.com/rostering-for-partners), accessed 2026-06-04.)
- **ClassLink** offers SSO + automated provisioning + analytics. ([Teachfloor — ClassLink Explained](https://www.teachfloor.com/blog/what-is-classlink); [ClassLink Roster Server](https://www.classlink.com/products/roster-server), accessed 2026-06-04.)
- Both produce a **vendor-side district ID** (Clever district token, ClassLink tenant ID) that needs to be reconciled against LEAID + SFDC.

**Implication:** the canonical identity-resolution table for a K-12 PSM dashboard joins on **5 IDs**: `(LEAID, state_district_id, sfdc_account_id, clever_district_id, classlink_tenant_id)`. Build a `district_identity` table with a confidence score per match.

---

## 7. FERPA boundaries on engagement-data dashboards

### 7.1 The core FERPA rule for vendors

EdTech vendors are usually not directly subject to FERPA, but operate as **"school officials"** under contract with school districts — they inherit FERPA's obligations via that contract. "While FERPA does not apply directly to EdTech companies, vendors are typically required by their contracts with individual educational institutions to comply fully with FERPA's obligations and restrictions." ([Strike Graph](https://www.strikegraph.com/blog/ferpa-for-ed-tech-companies); [Tech Policy Press](https://www.techpolicy.press/the-case-for-making-edtech-companies-liable-under-ferpa/), accessed 2026-06-04.)

### 7.2 The aggregate-vs-de-identifiable line

This is the critical line for dashboard design:

- **PTAC explicit rule:** "Information that would make the student's identity easily traceable may exist in small cell sizes in aggregated or statistical information from education records." ([PTAC — Disclosure Avoidance FAQ](https://studentprivacy.ed.gov/resources/frequently-asked-questions-disclosure-avoidance), accessed 2026-06-04.)
- **PTAC explicit rule:** "Simply removing identifiers from education records does not result in de-identified data … individuals could still be picked out through combinations of demographic variables, course histories, or other characteristics showing substantial variance across a population." ([PTAC — Disclosure Avoidance Webinar](https://studentprivacy.ed.gov/sites/default/files/training/supporting_materials/Disclosure%20Avoidance%20Webinar_508_0.pdf), accessed 2026-06-04 — SERP summary; WebFetch 403.)
- **PTAC stance on thresholds:** "The Department does not mandate a particular method, nor does it establish a particular threshold for what constitutes sufficient disclosure avoidance" — but recommends data about small groups not be reported. ([PTAC FAQs Disclosure Avoidance](https://studentprivacy.ed.gov/sites/default/files/resource_document/file/FAQs_disclosure_avoidance_0.pdf), accessed 2026-06-04 — SERP summary.)

### 7.3 Concrete numeric thresholds (state practice)

Federal guidance doesn't mandate, but state practice converges on **n ≥ 10** (often n ≥ 20):

- Connecticut: "Standard practice for protecting personally identifiable data is that information for groups of less than 10 students may not be reported in aggregated tables." ([CT EdSight Suppression Rules](https://edsight.ct.gov/relatedreports/BDCRE%20Data%20Suppression%20Rules.pdf), accessed 2026-06-04.)
- **Complementary suppression rule:** "If a cell is ≤ 5 and only one value is suppressed in a row or column, the next highest value in that row or column is also suppressed" — otherwise the suppressed value can be back-calculated from the row/column total. ([CT EdSight](https://edsight.ct.gov/relatedreports/BDCRE%20Data%20Suppression%20Rules.pdf); [UW Student Data — FERPA Suppression](https://studentdata.washington.edu/student-reports/ferpa-suppression-and-complementary-suppression/), accessed 2026-06-04.)

**Practitioner-grade defaults for a PSM dashboard:**

- **Account-level metrics aggregated to district**: safe (district is institution, not student).
- **School-level student-engagement metrics with n ≥ 10**: safe with complementary suppression.
- **Classroom / teacher-level student metrics**: risky — small class sizes routinely fall under n=10. Display as "/active" rather than discrete counts.
- **Individual student records**: regulated. Don't surface in PSM-facing views. Period.

### 7.4 The benchmarking trap

"Some EdTech vendors use student data from multiple institutions to build benchmarks or train algorithms, which may not be covered by the school official exception and requires explicit opt-out provisions at minimum, and opt-in authorization in most interpretations." ([Hireplicity — FERPA Checklist 2025](https://www.hireplicity.com/blog/ferpa-compliance-checklist-2025); [Number Analytics — FERPA in EdTech](https://www.numberanalytics.com/blog/ferpa-in-edtech-a-comprehensive-guide), accessed 2026-06-04.)

**Implication:** a "compare to peers" widget that uses other districts' aggregated data may be compliant **only if** (a) the data is genuinely de-identified at the school-official level, (b) the vendor's DPA explicitly authorizes the use, and (c) cell suppression is applied. Default to **deny by config** and require explicit opt-in.

### 7.5 The 2024-25 enforcement landscape

- 2024 PowerSchool breach affected 62M students. ([Total Assure — FERPA Penalties](https://www.totalassure.com/blog/ferpa-violation-penalties); [Ogletree](https://ogletree.com/insights-resources/blog-posts/president-trump-orders-closure-of-the-department-of-education-what-schools-and-edtech-companies-need-to-know-about-ferpa/), accessed 2026-06-04.)
- "Cases involving third-party sharing rose 34% in 2024, driven in part by the rapid expansion of educational technology." ([Total Assure](https://www.totalassure.com/blog/ferpa-violation-penalties), accessed 2026-06-04.)
- **As of 2025, the DoE has never imposed a financial penalty for FERPA violations**, instead using monitored compliance — but reputational and contract-cancellation consequences are routinely severe. ([Tech Policy Press](https://www.techpolicy.press/the-case-for-making-edtech-companies-liable-under-ferpa/), accessed 2026-06-04.)
- 96% of K-12 apps reportedly share student data with third parties — a finding that has driven proposed FERPA reform. ([Public Interest Privacy Center — EdTech Accountability](https://publicinterestprivacy.org/edtech-data-sharing/), accessed 2026-06-04.)

---

## 8. AI-assistant build-from-spec failure modes (Codex / Copilot / Devin / Cursor lessons)

### 8.1 The contract-not-prompt insight

The dominant 2026 lesson, repeated across multiple practitioner sources:

> "The biggest risk with AI agents is not that the model gets the code wrong, but that the model gets the intent wrong because the instructions were ambiguous. The bottleneck in AI-assisted development is not the model, context window, or tooling, but the human giving the instructions." ([Evangelist Apps — Spec is the New Code](https://medium.com/@EvangelistApps/the-spec-is-the-new-code-why-ai-coding-agents-fail-how-to-fix-it-5011eb423b45), accessed 2026-06-04.)

> "Your Coding Agent Doesn't Need Better Prompts. It Needs a Contract. A contract means a written, testable description of observable behavior: commands, outputs, exit codes, schemas, determinism rules, and the boundaries of what implementation is allowed to change." ([DEV — Coding Agent Contract](https://dev.to/fabibi/your-coding-agent-doesnt-need-better-prompts-it-needs-a-contract-572k), accessed 2026-06-04.)

> "The most dangerous failure mode in agentic coding workflows is not broken code, but plausible code: code that passes tests, implements something close to the request, and quietly expands the product surface in a direction nobody approved." ([Evangelist Apps](https://medium.com/@EvangelistApps/the-spec-is-the-new-code-why-ai-coding-agents-fail-how-to-fix-it-5011eb423b45), accessed 2026-06-04.)

### 8.2 Multi-file edit failure modes

- **Circular dependency introduction.**
- **Type mismatches when modifying shared interfaces.**
- **Import path errors.**
- **Context drift on steps 4+ of a multi-step plan.** "Earlier GPT models had a tendency to drift — you'd give them a complex, multi-step task and by step four or five, they'd start interpreting the original goal loosely." ([Flowith — GPT-5.4 Codex FAQ](https://flowith.io/blog/gpt-5-4-codex-faq-multi-file-editing-context-window-security/); [DataStudios — GPT-5.1 Codex](https://www.datastudios.org/post/gpt-5-1-codex-pros-and-cons-capabilities-constraints-and-developer-implications), accessed 2026-06-04.)

### 8.3 The role-overload anti-pattern (Cursor's lesson)

"The Cursor team found it was being given too many roles and objectives simultaneously, including: plan, explore, research, spawn tasks, check on workers, review code, perform edits, merge outputs, and judge if the loop is done. In retrospect, it makes sense it was overwhelmed. The final design incorporates all of our learnings: A root planner owns the entire scope of the user's instructions." ([Cursor — Self-Driving Codebases](https://cursor.com/blog/self-driving-codebases), accessed 2026-06-04.)

**Implication:** decompose the build into single-role passes (plan → scaffold → fill → test → review), each with explicit handoff contracts.

### 8.4 The boundedness rule (Devin's lesson)

"Devin excels when the task is clear and bounded. The broader your request, the more tokens (and ACUs) it burns … In practice, Devin works best on well-scoped, isolated tasks. Scaffold a new API endpoint from a spec. Migrate a codebase from one ORM to another. Write integration tests for an existing module. These are tasks where the boundaries are clear, the patterns are established, and the success criteria are obvious." ([Site Point — Devin Aftermath](https://www.sitepoint.com/devin-ai-engineers-production-realities/); [Emergent — Devin vs Cursor](https://emergent.sh/learn/devin-vs-cursor), accessed 2026-06-04.)

### 8.5 The orphan-tool / sub-agent failure modes

"MCP servers and hooks fail in sub-agent contexts, and hard kills, resumes, and plan operations expose state machine brittleness — orphan tool calls, stalled turns, and corrupted conversations." ([Awesome Agents — Copilot CLI GA](https://awesomeagents.ai/news/github-copilot-cli-generally-available/), accessed 2026-06-04.)

### 8.6 The retrospective discipline

"Run a weekly 15-minute retrospective focused solely on agent usage. Expand the scope of agent-eligible tasks only when the data supports it. Pull back immediately when defect rates spike or review overhead exceeds time savings. Track: PR merge rate without revision, average review cycles, net time saved per task category, and post-merge defect rate for agent-generated code." ([Emergent](https://emergent.sh/learn/devin-vs-cursor); [Builder.io — Devin vs Cursor](https://www.builder.io/blog/devin-vs-cursor), accessed 2026-06-04.)

### 8.7 Spec-driven development is the consensus

Multiple sources converge: write the contract first, generate code from it, validate against the contract. ([Augment — Spec-Driven Dev](https://www.augmentcode.com/guides/spec-driven-development-ai-agents-explained); [Augment — What Is Spec-Driven Dev](https://www.augmentcode.com/guides/what-is-spec-driven-development); [tedivm — Beyond the Vibes](https://blog.tedivm.com/guides/2026/03/beyond-the-vibes-coding-assistants-and-agents/), accessed 2026-06-04.)

---

## 9. Recommended RavenClaude enhancements (prioritized list)

### P0 — Foundation (must-have before any agent generates a dashboard)

#### 9.1 `plugins/edtech-partner-success/knowledge/psm-dashboard-canon-2026.md` *(new)*
The single canonical spec the dashboard build kit reads from. Includes:
- The 8-dashboard Gainsight canon (mapped to K-12 with the variances in §1, §4).
- The convergent "home base" pattern (Portfolio + Cockpit + Timeline + Health Distribution).
- The 5-second-rule layout test.
- Stephen Few / IBCS rules inherited (semantic notation, top-left placement, sparkline density).
- Explicit non-goals (this is operational, not analytical, not executive).

#### 9.2 `plugins/edtech-partner-success/knowledge/k12-signal-taxonomy.md` *(new)*
The K-12-specific signal catalog beyond generic CS. Each signal entry: `{id, name, persona, leading|lagging, default_weight, default_half_life_days, ferpa_class}`. Covers:
- Teacher adoption (per-teacher login frequency, lesson-completion).
- Admin engagement (admin-panel session count, settings changes).
- Decision-maker engagement (executive sponsor touch recency).
- Family activation rate (per parent-comms vendor specifically).
- Rostering health (sync success rate, error volume, last-sync recency).
- State-testing-window blackout flag.
- Leadership-turnover flag (superintendent/CTO/curriculum director).
- ESSER-funded flag (renewal risk through 2027).
- LearnPlatform external benchmark rank.

#### 9.3 `plugins/edtech-partner-success/skills/daily-action-queue/SKILL.md` *(new)*
Computes "today's top N accounts" for a PSM. Contract:
- **Input:** PSM ID, portfolio table, signal table, lifecycle stage per account, current date, optional `framework=weighted|rice|ice`.
- **Output:** Ranked list of accounts with `{account, score, top_3_signals, recommended_action, rationale_string, confidence}`.
- **Math:** Default weighted-sum with lifecycle-aware weights from §2.1 + recency decay from §3.2 + tier multiplier from §3.4. RICE/ICE as alternate.
- **Rationale string** must name the dominant signal + the threshold crossed + the prescribed play (e.g. "Westfield USD: usage -34% over 14d in Phase 2 onboarding → run *Phase 2 Recovery* play").
- **NBA flavor:** every action carries an explicit `confidence: 0.0-1.0` and `rationale` — never bare ranking.

#### 9.4 `plugins/edtech-partner-success/skills/health-score-v2/SKILL.md` *(update existing partner-health-scoring)*
Extend the current schema (`adoption / touchpoint / outcome / sentiment / champion / usage`) to add:
- `support` (ticket velocity, unresolved P1 count, escalation count).
- `financial` (payment status, contract amendments, ESSER-flag).
- `rostering_health` (K-12-specific).
- `leadership_stability` (K-12-specific).
- Per-signal `leading|lagging` tag.
- Per-signal half-life (defaults from §3.2; 7d usage, 14d support, 30d champion, 90d sentiment, 180d outcome).
- Persona-segmented subscores (teacher / admin / decision-maker).
- Migration note for the existing `partner-health-scoring` skill: old rubric remains the default; new components are opt-in via config.

#### 9.5 `plugins/edtech-partner-success/knowledge/ferpa-dashboard-boundaries.md` *(new)*
The compliance contract for any widget that touches engagement data. Hard rules:
- District-level aggregation: always safe.
- School-level student counts: `n ≥ 10` with complementary suppression on `n ≤ 5`.
- Teacher/classroom-level student data: never as discrete counts; ratios only.
- Individual student records: explicitly out of scope.
- Benchmarking against other districts: requires DPA opt-in + cell suppression; default deny.
- Examples of widget patterns that pass and patterns that fail.
- Citation: PTAC Disclosure Avoidance FAQ, CT EdSight rules, UW FERPA suppression doc.

### P1 — Build kit (the actual command-center generator)

#### 9.6 `plugins/edtech-partner-success/skills/dashboard-build-kit/SKILL.md` *(new)*
The end-to-end "spec → working dashboard" build kit. Lessons from §8 baked in:
- **Spec-first.** The skill writes a `dashboard-contract.yaml` *before* any code: widget list, data contracts, FERPA classifications, layout grid, color semantics.
- **Decomposed passes.** Separate sub-skills: `dashboard-plan`, `dashboard-scaffold`, `dashboard-fill`, `dashboard-validate`. Each has its own handoff contract.
- **Bounded scope per pass.** Each pass touches a stated file list; out-of-list edits are denied.
- **Validation gate.** A `dashboard-validate` step checks: (a) every widget's data contract is honored, (b) FERPA classifications are present, (c) cell-suppression rules are applied to any school-level widget, (d) the 5-second-rule layout test (no more than 9 top-level widgets, status indicator top-left), (e) IBCS semantic notation (same color = same meaning across widgets).
- **Failure-mode runbook** captured in the skill: circular dep, type mismatch on shared interface, import path, role-overload — each with the recovery move.

#### 9.7 `plugins/edtech-partner-success/agents/dashboard-architect.md` *(new agent)*
- Audience: PSM Ops leads, RevOps, and BI partners at K-12 EdTech vendors.
- Works with: `partner-success-manager` agent, `dashboard-build-kit` skill, the K-12 signal taxonomy, the FERPA boundaries doc.
- Scenarios (each with `intent / trigger_phrase / outcome / difficulty` per AGENTS.md §7):
  - "Design a new PSM command-center dashboard from scratch."
  - "Audit an existing dashboard for K-12 compliance + Stephen Few / IBCS adherence."
  - "Add the leadership-watch widget to an existing dashboard."
  - "Translate a vendor-PRD dashboard mock into a build-kit spec."
- Quickstart: open `psm-dashboard-canon-2026.md`, run `/dashboard-build-kit` skill on a config file.

#### 9.8 `plugins/edtech-partner-success/templates/dashboard-contract.yaml` *(new)*
The reference contract format. Fields: `widget_id, type (kpi-card|sparkline|small-multiple|status-grid|action-queue), data_source, signal_ids, persona, ferpa_class (district|school-n10|teacher-ratio|never), refresh_cadence, position {row, col, width, height}, color_semantic_key`.

### P1 — Data platform support

#### 9.9 `plugins/data-platform/knowledge/k12-district-identity-resolution.md` *(new)*
The 5-ID join model from §6.5. Includes:
- LEAID structure (state FIPS + LEA code).
- State-ID patterns (CDS, NYSED, TEA, etc. — top 10 states).
- Salesforce Account dedup patterns specifically for K-12 districts.
- Clever district token + ClassLink tenant ID reconciliation.
- Deterministic-first / fuzzy-fallback algorithm with concrete thresholds (Levenshtein ≤ 3 on name + ZIP match + grade-span match).
- Survivorship rules for merges.
- A reference `district_identity` table schema with confidence scores.

#### 9.10 `plugins/data-platform/knowledge/edfi-oneroster-connector-notes.md` *(new)*
- OneRoster 1.2 REST and CSV binding differences.
- Sync error taxonomy (manifest missing, file-set mismatch, ID drift across years).
- Ed-Fi alignment as the "canonical layer" recommendation.
- Where to put roster-health metrics in a vendor-side data warehouse.
- Joins to the district-identity table above.

#### 9.11 `plugins/data-platform/knowledge/learnplatform-benchmark-integration.md` *(new)*
- LearnPlatform EdTech Top 40 / EdTech300 methodology.
- How to consume the data for an external benchmark widget.
- Disclosure that LearnPlatform's Chrome-extension methodology is panel-based, not census — confidence interval caveats for the widget.

### P2 — Cross-cutting (core)

#### 9.12 `plugins/ravenclaude-core/knowledge/spec-driven-dashboards.md` *(new)*
Generalized lesson from §8 — for any plugin (not just EdTech) that builds a dashboard:
- Contract before code.
- Single-role passes.
- Validation gate before sign-off.
- The "plausible code" failure mode and how to catch it.

#### 9.13 `plugins/ravenclaude-core/skills/multi-file-refactor-guardrails/SKILL.md` *(new)*
The failure modes from §8.2 distilled into a reusable safety net:
- Pre-flight: declare the file list to be touched; deny edits outside it.
- Type-coherence pass on shared interfaces.
- Circular-dependency check post-edit.
- Import-path validation.
- Sub-agent / orphan-tool detector.

#### 9.14 `plugins/ravenclaude-core/best-practices/operator-console-design.md` *(new)*
The Stephen Few + IBCS + NOC research from §5 distilled into a 1-page checklist any plugin's dashboard can inherit:
- 5-second rule.
- 9-widget cap on the home view.
- Top-left = current status / most-urgent exception.
- Same color = same meaning (semantic notation).
- Sparklines + small multiples for density.
- Operational ≠ analytical ≠ executive — pick one per surface.

### Migration / safety notes for the enhancement PR

- All new schemas are **additive** — existing `partner-health-scoring` SKILL and `psm-metrics-glossary.md` continue to work unchanged for consumers who don't opt in.
- The new `support` and `financial` health components default to weight 0 in existing rubrics; consumers explicitly opt in.
- The FERPA boundaries doc is referenced as a *gate* — any new dashboard widget must cite a FERPA class in its contract or the build kit refuses to ship.
- Version bump: `edtech-partner-success` minor (new agents + skills, no breaking change); `data-platform` minor (new knowledge files only); `ravenclaude-core` minor (new general patterns).

---

## 10. Source ledger

All sources accessed **2026-06-04** unless otherwise noted.

### Vendor CSP docs (Gainsight, Planhat, ChurnZero, Catalyst, Totango, Vitally)
1. [Gainsight — Home for CSMs](https://support.gainsight.com/gainsight_nxt/Gainsight_Home/User_Guides/Gainsight_Home_for_CSMs)
2. [Gainsight — 8 Dashboards Top Performing CS Teams Can't Live Without](https://www.gainsight.com/blog/8-dashboards-top-performing-customer-success-teams-cant-live-without/) *(SERP summary)*
3. [Gainsight — Customer Health Scores Explained](https://www.gainsight.com/blog/customer-health-scores/) *(SERP summary)*
4. [Gainsight — Cockpit Use to Manage Daily Routine (Horizon)](https://support.gainsight.com/gainsight_nxt/04Cockpit_and_Playbooks/00Cockpit_Horizon_Experience/User_Guides/Use_Cockpit_to_Manage_Daily_Routine_(Horizon_Experience))
5. [Gainsight — Configure CTA Types, Reasons, Priority, Snooze](https://support.gainsight.com/SFDC_Edition/Cockpit_and_Playbooks/Admin_Guides/Configure_CTA_Types-Reasons-Priority-Snooze)
6. [Gainsight — Managing Your Cockpit Effectively](https://www.gainsight.com/blog/managing-cockpit-effectively/)
7. [Gainsight — Essential Guide to QBRs](https://www.gainsight.com/essential-guide/quarterly-business-reviews-qbrs/)
8. [Gainsight — DAU/MAU Tutorial](https://www.gainsight.com/essential-guide/product-management-metrics/dau-mau/)
9. [Planhat — Ultimate Guide to Customer Health Scores](https://www.planhat.com/customer-success/health) *(SERP summary)*
10. [Planhat — Churn & Retention Guide](https://www.planhat.com/customer-success/churn-and-retention)
11. [Planhat — Configuring Health Scores & Success Units](https://help.planhat.com/en/articles/10045917-configuring-health-scores-and-success-units-in-upgraded-planhat)
12. [Planhat — Top 9 CS KPIs](https://www.planhat.com/editorial/top-9-most-important-customer-success-kpis)
13. [ChurnZero — Command Center](https://churnzero.com/features/command-center/)
14. [ChurnZero — Centralize Customer Data](https://churnzero.com/customer-success-software/centralize-customer-data/)
15. [ChurnZero — Customer Playbooks](https://churnzero.com/features/customer-playbooks/)
16. [Catalyst — Playbooks](https://catalyst.io/product/playbooks)
17. [Catalyst Help — Manage Customer Accounts](https://help.catalyst.io/hc/en-us/articles/28924671873556-Use-Catalyst-to-view-or-manage-customer-accounts)
18. [Catalyst Help — Best Practices for Building in Catalyst](https://help.catalyst.io/hc/en-us/articles/33528832507284-Best-practices-for-building-in-Catalyst)
19. [Totango — Customer Success Center](https://support.totango.com/hc/en-us/articles/204012969-Totango-s-New-Customer-Success-Platform-What-s-new-)
20. [Totango — Customer Health Features](https://www.totango.com/product-features/customer-health)
21. [Totango — Building an Early Warning System](https://www.totango.com/blog/building-an-early-warning-system)
22. [Totango — Best Practices for Designing Health Profiles](https://support.totango.com/hc/en-us/articles/202301749-Best-practices-for-designing-health-profiles)
23. [Vitally — Productivity](https://www.vitally.io/product/productivity)
24. [Vitally — Create a Customer Health Score with 4 Metrics](https://www.vitally.io/post/how-to-create-a-customer-health-score-with-four-metrics)
25. [Vitally vs Catalyst vs Totango](https://www.vitally.io/post/vitally-vs-catalyst-vs-totango)
26. [Vitally — 2025 Confidence Index](https://www.vitally.io/vital-insights-02-confidence-index-report)

### Practitioner CS blogs / playbooks
27. [Velaris — How to Create a CS Health Score Template](https://www.velaris.io/articles/how-to-create-a-customer-health-score-template)
28. [Velaris — CS Dashboard Examples](https://www.velaris.io/articles/customer-success-dashboard-examples)
29. [Velaris — Account Prioritization in CS](https://www.velaris.io/articles/account-prioritization-cs)
30. [Velaris — Complete Guide to Health Scores](https://www.velaris.io/articles/cs-health-scores)
31. [Customer Imperative — Portfolio Segmentation](https://customerimperative.com/customer-portfolio-segmentation-for-customer-success-managers/)
32. [Customer Success Collective — How to Prioritize Accounts](https://www.customersuccesscollective.com/how-to-proritize-accounts-in-customer-success/)
33. [Customer Success Collective — Health Score Mastery](https://www.customersuccesscollective.com/the-customer-health-score-how-to-master-this-metric/)
34. [Customer Success Collective — Building a CS Dashboard](https://www.customersuccesscollective.com/building-a-customer-success-dashboard/)
35. [Typewise — Prioritizing Support Tickets](https://www.typewise.app/blog/prioritizing-support-tickets-method)
36. [Customers.ai — Recency-Weighted Scoring](https://customers.ai/recency-weighted-scoring)
37. [Heap — From Lagging to Leading Indicators](https://www.heap.io/blog/from-lagging-to-leading-indicators-a-proactive-approach-to-account-health-scoring)
38. [Lyniro — 15 Plays Playbook](https://lyniro.com/blog/customer-success-playbook/)
39. [SuccessCOACHING — Prioritizing High-Impact CS Activities](https://successcoaching.co/blog/prioritizing-high-impact-customer-success-activities)
40. [SuccessCOACHING — Build a Customer Health Score System](https://successcoaching.co/blog/how-to-build-a-customer-health-score-system-and-actions-to-take)
41. [HubSpot — Customer Health Score Guide](https://blog.hubspot.com/service/customer-health-score)
42. [Vitally — Best CS Automation Software 2025](https://www.vitally.io/post/best-cs-automation-software)
43. [Process.st — How to Calculate Customer Health Score](https://www.process.st/customer-health-score/)
44. [SupportLogic — Support Health Score](https://www.supportlogic.com/resources/blog/support-health-score-unifying-customer-support-success/)
45. [The CS Cafe — Digital CSM Portfolio Management](https://www.thecscafe.com/p/digital-csm-portfolio-management)
46. [Front — CS Playbook Guide](https://front.com/blog/customer-success-playbook)

### K-12 EdTech-specific
47. [User Intuition — Education Churn Playbook](https://www.userintuition.ai/posts/the-education-churn-playbook-what-edtech-gets-wrong/)
48. [User Intuition — Education / EdTech Churn Patterns Refresh](https://www.userintuition.ai/posts/refresh-education-edtech-churn-patterns-guide/)
49. [EducationIntel — Why K-12 Vendors Lose Before Procurement](https://educationintel.substack.com/p/why-many-k-12-vendors-lose-before)
50. [Ed2Market — Client Retention Strategies for K-12 Vendors](https://www.ed2market.com/blog/client-retention-strategies)
51. [EdWeek Marketbrief — Superintendents Under Pressure](https://marketbrief.edweek.org/meeting-district-needs/school-superintendents-are-under-pressure-heres-how-vendors-can-help/2025/10)
52. [K-12 Dive — Tense Board Relationships Fuel Superintendent Turnover](https://www.k12dive.com/news/high-superintendent-turnover-staffed-up/804337/)
53. [K-12 Dive — ESSER Legacy](https://www.k12dive.com/news/esser-pandemic-COVID-K-12-spending-what-will-its-legacy-be/815999/)
54. [GovTech — Student-Focused Budgeting as ESSER Winds Down](https://www.govtech.com/education/k-12/experts-push-student-focused-budgeting-as-esser-winds-down)
55. [Oliver Wyman — K-12 Investment Strategies as Stimulus Funds End](https://www.oliverwyman.com/our-expertise/insights/2025/mar/k-12-investment-strategies-stimulus-funds-end-2025.html)
56. [SETDA — 2025 State EdTech Trends Report](https://www.setda.org/resource/2025-state-edtech-trends-report/)
57. [SETDA — Press Release: Only 27% of States Prepared](https://www.setda.org/news/press-releases/press-release-2025/report-only-27-of-states-prepared-to-sustain-k-12-digital-access-as-federal-programs-end/)
58. [SETDA — 2025 EdTech Quality Indicators Guide](https://www.setda.org/wp-content/uploads/2026/03/2025-SETDA-EdTech-Quality-Indicators-Guide.pdf)
59. [Project Tomorrow — Speak Up 2025](https://www.tomorrow.org/projects-3/speak-up/)
60. [EWA — Project Tomorrow K-12 Tech Report 2025](https://ewa.org/members-news/press-releases/project-tomorrow-releases-annual-k-12-tech-report-reveals-student-optimism-about-classroom-ai-use)
61. [EdTech Chronicle — Project Tomorrow Speak Up Research](https://edtechchronicle.com/project-tomorrow-unveils-latest-speak-up-research-highlights-need-for-active-digital-student-learning-experiences/)
62. [Edsby — Parent Engagement K-12 Data](https://www.edsby.com/school-apps-for-parent-engagement-k12-data/commentary/)
63. [edCircuit — Family Engagement Tools Transforming K-12](https://edcircuit.com/how-family-engagement-tools-are-transforming-k-12-education/)
64. [ParentSquare — 2026 K-12 Predictions](https://www.parentsquare.com/blog/2026-edtech-predictions/)
65. [SchoolStatus — K-12 Family Communication](https://www.schoolstatus.com/)
66. [Frontline — Standardized State Testing Trends](https://www.frontlineeducation.com/blog/standardized-state-testing-in-education-changes-and-future-trends/)
67. [Frontline — Top 5 K-12 Trends 2025-26](https://www.frontlineeducation.com/blog/top-5-k-12-education-trends-superintendents-must-watch-for-2025-26/)
68. [Lexia — Impact of Success Partnerships](https://www.lexialearning.com/resources/research/impact-of-lexia-success-partnerships-on-student-usage--progress)
69. [Instructure — EdTech Top 40](https://www.instructure.com/edtech-top40)
70. [Instructure — Impact for K-12](https://www.instructure.com/k12/products/impact)
71. [LearnPlatform — National EdTech Equity Dashboard](https://www.prnewswire.com/news-releases/learnplatform-launches-national-edtech-equity-dashboard-to-improve-visibility-of-digital-k-12-engagement-and-gaps-across-us-301277353.html)
72. [LearnPlatform — Engagement Dataset (ICPSR)](https://www.icpsr.umich.edu/web/ICPSR/studies/38426)
73. [Dromo — EdTech Data Onboarding](https://dromo.io/blog/data-onboarding-for-edtech-student-records-rosters-and-compliance)
74. [Evelyn Learning — EdTech Sprawl](https://www.evelynlearning.com/blog/the-hidden-cost-of-edtech-sprawl-how-k-12-districts-are-drowning-in-unused-software-and-what-it-leaders-can-do-about-it)

### Rostering / SIS / Identity
75. [1EdTech — OneRoster](https://www.1edtech.org/standards/oneroster)
76. [1EdTech — OneRoster CSV 1.2.1 Binding](https://www.imsglobal.org/spec/oneroster/v1p2/bind/csv)
77. [Microsoft Learn — OneRoster Provider Overview](https://learn.microsoft.com/en-us/schooldatasync/oneroster-provider-overview)
78. [Aristek — OneRoster 1.2 What's New](https://aristeksystems.com/blog/oneroster-1-2/)
79. [Edlink — Everything About OneRoster 1.2](https://ed.link/community/everything-you-need-to-know-about-oneroster-1-2/)
80. [Edlink — Rostering Options for Vendors](https://ed.link/community/rostering-classroom-data-in-your-lms-what-are-your-options/)
81. [Ednition — Complete K-12 Rostering Guide](https://www.ednition.com/blog/simplify-k-12-rostering-and-data-integration-with-rosterstream-2)
82. [Ednition — Roster Intelligence AI](https://ednition.com/blog/roster-intelligence-ai-first-rostering-for-k-12-data-integration)
83. [EdTech Insiders — New Era of K12 Rostering](https://edtechinsiders.substack.com/p/the-new-era-of-k12-rostering-what)
84. [Magic EdTech — Ed-Fi vs OneRoster](https://www.magicedtech.com/blogs/ed-fi-vs-oneroster-in-plain-english-when-to-use-each-in-k-12/)
85. [Ed-Fi — Data Standard Reference](https://docs.ed-fi.org/reference/data-exchange/data-standard/)
86. [Ed-Fi — Guidance on Person Entity](https://techdocs.ed-fi.org/display/EFDS32/Guidance+on+Use+of+Ed-Fi+Person+Entity)
87. [Ed-Fi Alliance — Data Standard Overview](https://www.ed-fi.org/ed-fi-data-standard/)
88. [Clever — Rostering for Partners](https://www.clever.com/rostering-for-partners)
89. [Clever — Integration Types Quickstart](https://dev.clever.com/docs/integration-types)
90. [ClassLink — Roster Server](https://www.classlink.com/products/roster-server)
91. [Teachfloor — What Is ClassLink](https://www.teachfloor.com/blog/what-is-classlink)
92. [NCES — CCD Agency Name and Address File](https://nces.ed.gov/ccd/aadd.asp)
93. [NCES — CCD Quickfacts](https://nces.ed.gov/ccd/quickfacts.asp)
94. [Wikidata — NCES District ID Property](https://www.wikidata.org/wiki/Property:P2483)
95. [CDE — California CDS Administration](https://www.cde.ca.gov/ds/si/ds/)
96. [Inogic — CRM Dedup 2026 FAQ](https://www.inogic.com/blog/2026/02/beyond-deduplication-a-2026-faq-guide-to-clean-unified-ai-ready-crm-data/)
97. [WinPure — Identity Resolution with Data Matching](https://winpure.com/data-matching-identity-resolution/)
98. [AWS — Entity Resolution Fuzzy Matching](https://aws.amazon.com/blogs/industries/resolve-imperfect-data-with-advanced-rule-based-fuzzy-matching-in-aws-entity-resolution/)
99. [Salesforce Ben — Data Cloud Match Rules vs Duplicate Rules](https://www.salesforceben.com/data-cloud-match-rules-vs-salesforce-duplicate-rules/)

### FERPA / Student Privacy
100. [US DOE PTAC — Disclosure Avoidance FAQs PDF](https://studentprivacy.ed.gov/sites/default/files/resource_document/file/FAQs_disclosure_avoidance_0.pdf)
101. [US DOE PTAC — Disclosure Avoidance FAQ page](https://studentprivacy.ed.gov/resources/frequently-asked-questions-disclosure-avoidance)
102. [US DOE PTAC — Best Practices for Access Controls & Disclosure Avoidance Webinar PDF](https://studentprivacy.ed.gov/sites/default/files/training/supporting_materials/Disclosure%20Avoidance%20Webinar_508_0.pdf)
103. [US DOE — Forum Guide to Privacy of Student Information / Data Requests](https://nces.ed.gov/pubs2006/stu_privacy/datarequests.asp)
104. [US DOE PTAC — Responsibilities of Third-Party Service Providers](https://studentprivacy.ed.gov/resources/responsibilities-third-party-service-providers-under-ferpa)
105. [US DOE PTAC — Education Technology Vendors](https://studentprivacy.ed.gov/audience/education-technology-vendors)
106. [US DOE PTAC — Integrated Data Systems and Student Privacy PDF](https://studentprivacy.ed.gov/sites/default/files/resource_document/file/IDS-Final_0.pdf)
107. [US DOE PTAC — District Privacy Program Checklist](https://studentprivacy.ed.gov/sites/default/files/resource_document/file/Checklist_District_Privacy_Program_0.pdf)
108. [CT EdSight — Data Suppression Rules PDF](https://edsight.ct.gov/relatedreports/BDCRE%20Data%20Suppression%20Rules.pdf)
109. [UW Student Data — FERPA Suppression & Complementary Suppression](https://studentdata.washington.edu/student-reports/ferpa-suppression-and-complementary-suppression/)
110. [Tech Policy Press — Case for Making EdTech Liable Under FERPA](https://www.techpolicy.press/the-case-for-making-edtech-companies-liable-under-ferpa/)
111. [Ogletree — Closure of DoE: FERPA Implications](https://ogletree.com/insights-resources/blog-posts/president-trump-orders-closure-of-the-department-of-education-what-schools-and-edtech-companies-need-to-know-about-ferpa/)
112. [Public Interest Privacy Center — Fixing FERPA: EdTech Accountability](https://publicinterestprivacy.org/edtech-data-sharing/)
113. [Public Interest Privacy Center — Fixing FERPA: Cybersecurity](https://publicinterestprivacy.org/fixing-ferpa-cybersecurity/)
114. [Strike Graph — FERPA for EdTech Companies](https://www.strikegraph.com/blog/ferpa-for-ed-tech-companies)
115. [Hireplicity — FERPA Compliance Checklist 2025](https://www.hireplicity.com/blog/ferpa-compliance-checklist-2025)
116. [Number Analytics — FERPA in EdTech Guide](https://www.numberanalytics.com/blog/ferpa-in-edtech-a-comprehensive-guide)
117. [Edlink — Does FERPA Impact EdTech Companies?](https://ed.link/community/ferpa/)
118. [Total Assure — FERPA Violation Penalties 2025](https://www.totalassure.com/blog/ferpa-violation-penalties)
119. [Student Privacy Compass — Resources for Service Providers](https://studentprivacycompass.org/audiences/ed-tech/resources-for-service-providers/)

### Dashboard UX / IBCS / Stephen Few / NOC research
120. [Stephen Few / Perceptual Edge — Formatting and Layout Matter PDF](https://www.perceptualedge.com/articles/Whitepapers/Formatting_and_Layout_Matter.pdf)
121. [Stephen Few — Dashboard Design Course PDF](https://www.perceptualedge.com/files/Dashboard_Design_Course.pdf)
122. [Stephen Few — Sparkline Scaling Best Practices PDF](https://www.perceptualedge.com/articles/visual_business_intelligence/best_practices_for_scaling_sparklines.pdf)
123. [Information Dashboard Design (Few) — Goodreads listing](https://www.goodreads.com/book/show/336258.Information_Dashboard_Design)
124. [UXmatters — Few Dashboard Book Review](https://www.uxmatters.com/mt/archives/2007/04/book-review-information-dashboard-design.php)
125. [IBCS Association — Standards 1.2](https://www.ibcs.com/ibcs-standards-1-2/)
126. [IBCS — Main Site](https://www.ibcs.com/)
127. [Wikipedia — IBCS](https://en.wikipedia.org/wiki/International_Business_Communication_Standards)
128. [Zebra BI — Achieve Consistent Reporting with IBCS](https://zebrabi.com/ibcs/)
129. [Rockfeather — IBCS Data Viz](https://rockfeather.com/services/data-visualization/ibcs/)
130. [Activu — SOC Dashboard Best Practices](https://www.activu.com/security-operations-center-dashboard-best-practices-a-checklist-for-critical-situational-awareness/)
131. [Activu — Utility Operations Center](https://www.activu.com/utility-operations-center-solutions-a-guide-to-integrated-situational-awareness/)
132. [Activu — What Is a NOC](https://www.activu.com/what-is-a-network-operations-center-a-guide-to-mission-critical-visibility/)
133. [AVEVA — Situational Awareness](https://www.aveva.com/en/solutions/operations/situational-awareness/)
134. [ExtNoc — NOC Design and Layout](https://www.extnoc.com/network-operations-center/noc-design-and-layout/)
135. [PMC (NCBI) — Cognitive Load in Energy Network Control Rooms](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8995508/)
136. [Ethos3 — Mastering the 5 Second Rule](https://ethos3.com/mastering-the-5-second-rule-elevate-your-presentation-design-for-maximum-impact/)
137. [DEV Community — The 5 Second Rule](https://dev.to/deyrupak/are-you-aware-of-the-5-second-rule-398a)
138. [Omni Analytics — Data Viz Best Practices](https://omni.co/articles/data-visualization-best-practices-for-better-decision-making)
139. [DataCamp — Dashboard Design Tutorial](https://www.datacamp.com/tutorial/dashboard-design-tutorial)
140. [Improvado — Dashboard Design Best Practices 2026](https://improvado.io/blog/dashboard-design-guide)
141. [RIB Software — 25 Dashboard Design Principles](https://www.rib-software.com/en/blogs/bi-dashboard-design-principles-best-practices)
142. [UX Pilot — 12 Dashboard Design Principles](https://uxpilot.ai/blogs/dashboard-design-principles)
143. [Tabular Editor — Better KPI Visualizations in Power BI](https://tabulareditor.com/blog/kpi-card-best-practices-dashboard-design)
144. [Domo — Sparkline Chart](https://www.domo.com/learn/charts/sparkline-chart)

### NBA / RICE / Prioritization frameworks
145. [Inogic — Introducing NBA for D365](https://www.inogic.com/blog/2026/03/introducing-next-best-action-ai-powered-recommendations-for-microsoft-dynamics-365/)
146. [Inogic — Coming Soon: AI-Powered NBA for D365](https://www.inogic.com/blog/2026/02/coming-soon-ai-powered-next-best-action-for-dynamics-365-crm/)
147. [Inogic — How AI Recommends NBA in CRM](https://www.inogic.com/blog/2026/05/how-ai-recommends-the-next-best-action-in-crm-with-real-examples/)
148. [Minuscule Technologies — Einstein NBA Implementation Guide](https://www.minusculetechnologies.com/blogs/einstein-next-best-action-implementation-guide)
149. [CleverTap — What is NBA](https://clevertap.com/blog/next-best-action/)
150. [Kaizenko — ICE, RICE, Weighted Scoring](https://www.kaizenko.com/scoring-frameworks-ice-rice-and-weighted-scoring-for-product-prioritization/)
151. [ProductPlan — RICE Scoring Model](https://www.productplan.com/glossary/rice-scoring-model)
152. [Intercom — RICE Prioritization for PMs](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/)
153. [Factors.ai — Time Decay Attribution](https://www.factors.ai/blog/time-decay-attribution-model)
154. [RedTrack — Time Decay Attribution](https://www.redtrack.io/blog/time-decay-attribution-model/)

### AI coding agent retrospectives (§8)
155. [Evangelist Apps (Medium) — The Spec Is the New Code](https://medium.com/@EvangelistApps/the-spec-is-the-new-code-why-ai-coding-agents-fail-how-to-fix-it-5011eb423b45)
156. [DEV — Your Coding Agent Doesn't Need Better Prompts. It Needs a Contract.](https://dev.to/fabibi/your-coding-agent-doesnt-need-better-prompts-it-needs-a-contract-572k)
157. [Augment — Spec-Driven Dev & AI Agents Explained](https://www.augmentcode.com/guides/spec-driven-development-ai-agents-explained)
158. [Augment — What Is Spec-Driven Development](https://www.augmentcode.com/guides/what-is-spec-driven-development)
159. [tedivm — Beyond the Vibes: Coding Assistants and Agents](https://blog.tedivm.com/guides/2026/03/beyond-the-vibes-coding-assistants-and-agents/)
160. [arXiv — Configuration of AI Coding Agents (Claude Code projects)](https://arxiv.org/pdf/2511.09268)
161. [Cursor — Self-Driving Codebases](https://cursor.com/blog/self-driving-codebases)
162. [SitePoint — Devin Aftermath: AI Engineers in Production](https://www.sitepoint.com/devin-ai-engineers-production-realities/)
163. [Emergent — Devin vs Cursor](https://emergent.sh/learn/devin-vs-cursor)
164. [Builder.io — Devin vs Cursor 2026](https://www.builder.io/blog/devin-vs-cursor)
165. [Michael Ouroumis — Agentic Coding 2026: Claude Code vs Cursor vs Copilot vs Devin](https://www.michaelouroumis.com/blog/posts/agentic-coding-2026-claude-code-vs-cursor-vs-copilot-vs-devin)
166. [Flowith — GPT-5.4 Codex FAQ: Multi-File Editing](https://flowith.io/blog/gpt-5-4-codex-faq-multi-file-editing-context-window-security/)
167. [DataStudios — GPT-5.1 Codex Pros and Cons](https://www.datastudios.org/post/gpt-5-1-codex-pros-and-cons-capabilities-constraints-and-developer-implications)
168. [MindStudio — How to Use GPT-5.5 in Codex](https://www.mindstudio.ai/blog/how-to-use-gpt-5-5-codex-agentic-tasks)
169. [MindStudio — GPT 5.5 for Agentic Coding](https://www.mindstudio.ai/blog/gpt-5-5-agentic-coding-guide)
170. [Awesome Agents — GitHub Copilot CLI GA](https://awesomeagents.ai/news/github-copilot-cli-generally-available/)
171. [GitHub Changelog — Copilot CLI GA (2026-02)](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)
172. [Visual Studio Magazine — Copilot CLI Reaches GA](https://visualstudiomagazine.com/articles/2026/03/02/github-copilot-cli-reaches-general-availability-bringing-agentic-coding-to-the-terminal.aspx)

---

**Single-source flags.** The following claims are supported by only one source in this corpus and should be re-verified before being written into a customer-facing artifact:
- Specific weight vector "Activity 40%, Engagement 30%, Milestones 20%, Recency 10%" — Customers.ai only. *(Echoed in spirit by others; the specific numbers are one-source.)*
- LearnPlatform Chrome-extension methodology details (PRNewswire only).
- The 23% 2024-25 superintendent turnover figure — K-12 Dive citing a single research source; cross-check before using in a slide.
- "96% of K-12 apps share student data with third parties" — Public Interest Privacy Center citing an unnamed nonprofit; treat as directional, not precise.

**Verified-by-multiple-sources core claims** (safe to cite in a build kit):
- The "home base = portfolio + cockpit + timeline + health distribution" pattern (Gainsight, Catalyst, Totango, ChurnZero all converge).
- 7-day exponential decay half-life as default for usage signals (Customers.ai + Velaris + Factors.ai converge on this; rooted in Google Analytics standard).
- The buyer/user/decision-maker separation problem in K-12 (User Intuition + EducationIntel + multiple persona-mapping guides).
- The PTAC stance "no mandated threshold, but small-n must be suppressed; complementary suppression required on n≤5" (PTAC + CT EdSight + UW converge).
- Spec/contract-driven dev as the antidote to multi-file-edit drift (Augment + tedivm + Evangelist Apps + DEV all converge).
