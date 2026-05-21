# EdTech segment fundamentals — K-12, higher-ed, corporate L&D

> **Last reviewed:** 2026-05-21. Research-distilled reference covering how K-12, higher education, and corporate L&D differ as buying segments — decision-makers, calendars, contracts, regulation, funding, procurement, and 2024-2026 macro context. Sources: McKinsey, K-12 Dive, CBPP, NCES IPEDS, SHEEO, EDUCAUSE, SaltyCloud HECVAT guide, ATD State of the Industry reports, NYSED, FTC COPPA materials, AI for Education state-policy tracker. Refresh when: (a) a major federal funding event shifts the K-12 or higher-ed budget picture, (b) HECVAT, FERPA, COPPA, or major state student-privacy law materially changes, or (c) ATD or LinkedIn Learning publishes a new annual L&D survey.

Three segments, all EdTech, three materially different PSM jobs. This file captures the operational reality of each so the team doesn't import K-12 instincts into a higher-ed engagement or treat a corporate L&D buyer like a district CTO. Where a claim is well-sourced it carries the citation inline; where consensus is practitioner-folk it's flagged.

---

## 1. K-12

### Decision-maker map

K-12 buying is **committee-driven**, with a clear role split:

| Role | Owns |
|---|---|
| Superintendent | Ultimate signature; veto; school-board liaison |
| Curriculum director / Chief Academic Officer / Asst. Supt. for Instruction | Instructional fit — sets the framework before procurement opens |
| CTO / IT director | Technical fit; security; integration; rostering |
| Purchasing / procurement | Process compliance; competitive-bid execution |
| Principals | Building-level adoption; teacher buy-in |
| Board | Approval above thresholds; political layer |

Significant K-12 tech purchases typically involve **5-7 stakeholders**. **Real influence runs ahead of formal authority** — the curriculum director often sets what kind of solution the district wants *before* procurement opens. Engaging only with signers means entering after the eligibility criteria are baked.

> Source: RFP School Watch, "The K-12 Procurement Cycle" (https://www.rfpschoolwatch.com/rfp/blog/the-k-12-procurement-cycle-key-decision-makers-and-influencers/).

**Title variance:** Chief Academic Officer exists in larger districts; in smaller districts it collapses into "Assistant Superintendent for Instruction." For PSM segmentation, "instructional-side senior leader" is the more reliable label than CAO specifically.

### Buying cycle

- **6+ month sales cycles** typical. Competitive bidding required above state/local thresholds — commonly **$5,000-$50,000** depending on state and policy.
- **Peak PO volume in July.** July POs run ~14× typical-month volume; aligned to the July 1 fiscal-year start in most states.
- **Contract length:** 1-3 years typical, fiscal-year-aligned. Multi-year is the exception in K-12, not the norm.

> Sources: EdWeek MarketBrief, "K-12 Sales Cycle" (https://marketbrief.edweek.org/sales-marketing/k-12-sales-cycle-how-long-do-districts-need-to-make-smart-purchasing-decisions/2025/08); NationGraph, "K-12 District Budget Cycles" (https://www.nationgraph.com/post/timing-is-all-you-need-a-complete-guide-to-k-12-district-budget-cycles-for-edtech-sales-success).

### Calendar dead zones

Don't push QBRs, renewal decisions, or major touchpoints during:

- **First 2-3 weeks of school** (late August through mid-September in most districts)
- **State testing windows** (commonly March-May; varies by state)
- **Winter break stretch** (mid-December through New Year's)
- **End-of-school-year** (late May / June) when districts are closing books

Calendar-driven cadence matters more in K-12 than in any other EdTech segment. A QBR scheduled in week 1 of school will be ghosted; a renewal conversation in the last week of June will hit a desk that's already cleared.

### Success metrics the district measures itself against

Federal ESEA requires every state to publish an annual school / district report card. State accountability systems are multi-measure:

- Academic achievement (state assessments)
- Academic growth
- Graduation rate
- English-learner progress
- **Chronic absenteeism** (≥10% of enrolled days absent — ~18 days in a 180-day year) — included in 36+ state accountability systems
- **College and Career Readiness (CCR)** — included in 37+ states + DC

The national chronic-absenteeism rate dropped to **23.5% in 2024**, down from a 2022 peak of 28.5% — but **still ~75% above pre-pandemic levels**.

> Sources: Education Commission of the States, "50-State Comparison: School Accountability Systems" (https://www.ecs.org/50-state-comparison-school-accountability-systems-2024/); SchoolStatus K-12 Attendance Data 2024-25 (https://www.schoolstatus.com/blog/new-k-12-attendance-data-2024-25); The 74 (https://www.the74million.org/article/k-12-chronic-absenteeism-rates-down-from-peak-but-remain-persistently-high/).

**Implication for the PSM**: any EdTech product whose value story can be hung on attendance, growth, or CCR has a credible board-level story. Hang outcomes on the categories the state report card already names.

### Regulation

- **Federal floor:** FERPA (records access / disclosure) + COPPA (online data on under-13).
- **COPPA 2024 amendments** — opt-in required for AI training and third-party sharing. New rule effective June 23, 2025; full compliance by April 22, 2026. *Confidence: Medium on the exact effective dates (secondary source).*
- **State layer is dense and growing.** 121+ state laws layer on FERPA / COPPA. The load-bearing ones for PSMs:
  - **New York Education Law §2-d** — Parents' Bill of Rights, signed Data Privacy Agreement (NYSED model DPA template), encryption in transit and at rest, **7 calendar-day breach notification** to the educational agency, no sale of student PII, no commercial advertising or marketing.
  - **Illinois SOPPA** — signed DPA required; no targeted ads; no profiling; published vendor list; 30-day breach notification; 60-day data deletion at contract end.
  - **California SOPIPA** — applies to operators regardless of whether a contract exists (unusual). Bans targeted advertising and data sale on K-12 student information; required security practices.
  - **A growing list** — CT (similar to NY 2-d), CO (HB 16-1423), TX (SB 820), VA, WA, UT, FL — most follow the SOPPA / Ed Law 2-d template.

> Sources: NYSED Data Privacy and Security Policy (https://www.nysed.gov/data-privacy-security/nysed-data-privacy-and-security-policy); Cybernut summaries of Ed Law §2-d and SOPPA (https://www.cybernut.com/blog/all-about-new-yorks-education-law-2-d-student-data-privacy-explained, https://www.cybernut.com/blog/all-about-soppa-what-illinois-schools-must-know-about-student-data-protections); FTC COPPA amendment (https://files.a4l.org/privacy/Resources/2025_04_FTC_finalizes_amendments_to_COPPA_rule.pdf).

**Illinois consortium model:** the Illinois Student Privacy Alliance via the Learning Technology Center provides a single statewide DPA — sign once, covers participating districts. Useful PSM efficiency lever in IL.

> Source: Learning Technology Center / SDPC Illinois (https://www.ltcillinois.org/services/sdpc/).

### Funding sources and what gets cut first

**The ESSER cliff is the dominant 2024-25 story.** ESSER III (ARP) obligation deadline was **September 30, 2024**. Spend-down deadlines and late-liquidation extensions varied by state. McKinsey estimated **5-8% average district budget declines** absent state/local backfill; ~$1,200 per-student cuts in 2024-25. ESSER had represented **4-17% of total revenue** for many districts, with wide state-by-state variance.

> Sources: K-12 Dive, "ESSER fiscal cliffs" (https://www.k12dive.com/news/esser-budget-cuts-begin-2024-2025-2026-federal-aid/712534/); McKinsey, "Bracing for the ESSER funding cliff" (https://www.mckinsey.com/industries/education/our-insights/when-the-money-runs-out-k-12-schools-brace-for-stimulus-free-budgets); CBPP analysis (https://www.cbpp.org/research/state-budget-and-tax/expiration-of-federal-k-12-emergency-funds-could-pose-challenges-for).

Recurring federal sources to know: Title I (high-poverty schools), Title II (educator development), Title III (English learners), **Title IV-A (Student Support and Academic Enrichment — flexible, ed-tech-eligible)**, IDEA Part B (special ed). Title IV-A is the most ed-tech-friendly bucket.

**FY2026 federal budget dynamics:** White House FY2026 proposal eliminates / consolidates ~$5B across Titles I/II/III/IV/V (Title I-A preserved); Senate version mostly flat. Significant uncertainty in the K-12 federal funding picture as of 2026-05.

> Source: Learning Policy Institute, "$5 Billion in Federal K-12 Formula Funding Hangs in the Balance" (https://learningpolicyinstitute.org/blog/5-billion-federal-k-12-formula-funding-hangs-balance-between-white-house-and-senate-proposals).

**What gets cut first** (practitioner observation, not survey data): discretionary tech subscriptions, summer programming, contracted services, conference travel. ESSER-funded staff positions that need to be backfilled push these to the front of the queue.

### Vendor-procurement bear traps

- **State-by-state DPA requirements** — each significant student-privacy regime has its own contract rider. NYSED Model DPA; IL Student Privacy Alliance consortium; CA SOPIPA covenants.
- **Approved-products lists** — many states maintain catalogs for instructional materials and assessments that gate eligibility.
- **Procurement-stage privacy disqualification** — districts increasingly disqualify vendors mid-procurement for privacy-compliance gaps.

### 2024-2026 macro context

- **ESSER cliff** — above.
- **State AI guidance explosion** — at least 28 states had published K-12 AI guidance by April 2025; more than half by mid-2025. State approaches vary materially (prohibited / permitted with caution / encouraged with attribution). Mississippi was first to enact legislation creating a state AI task force (S.B. 2426).
- **December 2025 federal AI executive order** — Trump administration EO to block state AI regulations; legal and political durability uncertain. Treat as evolving 2025-2026 territory; state guidance remains the operating regime through at least mid-2026 unless a definitive federal pre-emption survives court challenge.

> Sources: AI for Education state-policy tracker (https://www.aiforeducation.io/ai-resources/state-ai-guidance); Ballotpedia state AI guidance tracker (https://ballotpedia.org/AI_guidance_issued_by_state_departments_of_education); EdWeek December 2025 (https://www.edweek.org/technology/k-12-world-reacts-to-trumps-executive-order-to-block-state-ai-regulations/2025/12).

---

## 2. Higher Education

### Decision-maker map — two parallel motions

Higher ed has **two structurally different buying motions** that the same PSM has to navigate at the same institution:

**(a) Central IT / procurement** — institution-wide systems (LMS, SIS, identity, security tools). Gated by:

- CIO (technical fit + roadmap alignment)
- Procurement office (RFP execution + compliance)
- Faculty senate input (academic-affecting changes)
- Provost / CFO (strategic + financial sign-off)
- Information security team (HECVAT)

**(b) Departmental "shadow IT"** — tools paid from departmental or grant budgets, often without central IT involvement. The same product can sell to 50 departments at one university and never trigger an enterprise contract.

> Sources: GovTech, "Going Rogue — Shadow IT in Higher Education" (https://www.govtech.com/education/higher-ed/going-rogue-how-to-manage-and-even-embrace-shadow-it-in-higher-education.html); EDUCAUSE 2025 Top 10 (https://www.educause.edu/research-and-publications/research/top-10-it-issues-technologies-and-trends/2025).

**PSM implication:** renewal motions are correspondingly fragmented. "Single contact at the university" is often a fiction at large research universities. Map your installed base across both motions before any renewal cycle.

### Buying cycle

- **57-day average for public-sector RFPs** from posting to award (single source — directional). Add months for RFP-prep.
- Higher-ed RFPs commonly pull faculty committees, IT security, legal, procurement, senior administrators into the loop. Multi-month total cycles are normal.
- **Thresholds vary by institution.** SUNY system administration requires RFPs above $125,000 (primary source confirmed); other systems differ.

> Sources: E&I Cooperative, "RFP Contract Meaning" (https://www.eandi.org/resources/ei-blog/rfp-contract-meaning-ed-procurement/); SUNY System Purchasing (https://system.suny.edu/purchasing/rfp/rfp-procedures/).

### Calendar dead zones (practitioner consensus)

- **Finals weeks** (early-to-mid December; late April / early May at most institutions)
- **Winter break**
- **Summer** for faculty-side roles (mid-May through mid-August)
- **Fiscal year-end** (June 30 in most public institutions) slows central IT and admin

Central IT and admin staff run year-round but slow noticeably in late June / July at fiscal-year-close.

### Success metrics

**IPEDS** is the primary federal data system, with mandated reporting under Student Right-to-Know Act 1990 and HEA 2008 amendments. The key metrics:

- **Graduation Rate (GR)** — 6-year graduation rate for first-time, full-time freshmen
- **Graduation Rates 200%** (GR200) — 12-year version
- **Outcome Measures (OM)** — broader cohort including part-time and transfer students
- **Fall-to-fall retention rate**

> Sources: NCES IPEDS, "Measuring Student Success" (https://nces.ed.gov/ipeds/use-the-data/measuring-student-success-in-ipeds); IPEDS Graduation Rates component (https://nces.ed.gov/ipeds/survey-components/9).

**Accreditation cycles** — regional / institutional accreditors operate on 5-10 year cycles (HLC ~10 years; MSCHE ~8 years; NWCCU ~7 years). **Re-accreditation years are when leadership pays sharpest attention to evidence-of-improvement claims and data infrastructure** — high-leverage windows for a PSM whose product produces accreditation-relevant evidence.

> Source: Ithaka S+R, "Regional Accreditation Standards" (https://sr.ithaka.org/publications/regional-accreditation-standards/).

**EDUCAUSE 2025 Top 10** named "data-empowered institution," enrollment race, student journey, and "matter of trust" (privacy / security) as dominant CIO concerns. Products touching data, AI, retention, or student experience can hang outcomes on those themes credibly.

### Regulation

- **FERPA rights transfer to the student** at age 18 or upon enrollment in any postsecondary institution at any age (whichever comes first). This is the central differentiator from K-12 FERPA. Tax-dependent exception allows disclosure to parents without consent when the student is claimed as a tax dependent, but most institutions don't disclose by default policy.
- **Title IX** — sex discrimination and athletics
- **Clery Act** — campus crime reporting
- **ADA** — accessibility; WCAG 2.1 AA is effectively the standard

> Source: U.S. DOE Student Privacy, "Eligible Student" (https://studentprivacy.ed.gov/content/eligible-student).

### Funding

Higher-ed funding stack: tuition + fees + state and local appropriation + federal research funding + endowment income + philanthropic. State support varies enormously by state.

**SHEEO FY25 (the key 2025 finding):** state/local higher-ed appropriations hit a record **$130.7 billion** — but **per-FTE funding declined 1.0%** ($12,205 → $12,082). This is **the first per-student decline since 2012**. Enrollment grew faster than appropriations. **24 states still fund higher education below pre-Great-Recession levels** as of FY25.

> Source: SHEEO FY25 release (https://sheeo.org/shef_fy25_release/) — verified 2026-05-21.

FY2024 saw the largest decline in tuition revenue per FTE since the SHEF dataset began in 1980 (source: SHEEO FY24).

### Procurement bear trap — HECVAT

**HECVAT 4.1.5** (released February 10, 2025) is the current Higher Education Community Vendor Assessment Toolkit. It consolidated Full, Lite, and On-Premise into a **single unified workbook** with:

- **321 questions across 7 sections** (general data + 7 primary risk-coverage sections)
- **A new conditional AI/ML domain (32 questions)** — triggered by the Start Here tab when AI/ML features are in the product
- Alignment with NIST 800-53, HIPAA, PCI DSS, plus FERPA, GLBA, and WCAG 2.1 AA

The HECVAT 4 AI/ML domain distinguishes ML from LLM implementations and probes AI governance, risk management, training-data practices, and operational controls. **Any AI-touching product entering higher-ed procurement after February 2025 answers 32 additional questions.**

**EDUCAUSE retired the Community Broker Index (CBI) on July 31, 2025.** Vendors and institutions now exchange HECVAT responses directly — there's no central broker layer anymore.

> Sources: SaltyCloud, "The HECVAT: Complete Guide [2026]" (https://www.saltycloud.com/blog/what-is-the-hecvat/), verified 2026-05-21; SaltyCloud HECVAT updates (https://www.saltycloud.com/blog/hecvat-updates/); EDUCAUSE HECVAT (https://www.educause.edu/higher-education-community-vendor-assessment-toolkit).

### 2024-2026 macro context

- **The demographic cliff begins fall 2025.** Birth-rate decline after 2007 produces a projected **~15% drop in college-age students between 2025 and 2029** (Carleton economist Nathan Grawe's modeling — ~576,000 fewer students by 2029). Differential impact: community colleges projected ~14pp decline in entering 18-year-old class 2025-2030; regional comprehensives ~11pp; national universities ~9pp; elite universities ~6pp.
- **First per-FTE state funding decline since 2012** (above).
- **HECVAT 4 AI domain added February 2025** (above).

> Sources: RC Strategies summary of Grawe (https://rcstrat.com/research-and-insights/higher-education-demographic-cliff-enrollment-decline-2029); Inside Higher Ed (https://www.insidehighered.com/news/admissions/traditional-age/2024/12/11/college-age-demographics-begin-steady-projected-decline).

---

## 3. Corporate L&D

### Decision-maker map

The **CLO** (Chief Learning Officer) owns L&D strategy, budget, and technology selection. Typically reports to CEO or CHRO. **CLO is concentrated in Fortune 500 / 1000;** mid-market substitutes **CHRO + L&D director / VP HR + L&D director**. For PSM segmentation: enterprise = CLO lane; mid-market = CHRO-with-L&D-director lane.

Typical decision motion: CLO / L&D director identifies need → business unit sponsor validates problem and co-funds (or refuses to) → IT runs security review (SOC 2, often SSO / SCIM / data-residency checks) → procurement runs commercial negotiation and legal redlines → CLO / CHRO signs (or CEO above threshold).

> Sources: Training Industry, "Chief Learning Officer Job Description" (https://trainingindustry.com/wiki/professional-development/chief-learning-officer-clo-job-description/); AIHR, "Chief Learning Officer" (https://www.aihr.com/blog/chief-learning-officer/).

### Buying cycle

- SaaS-industry-wide contract length: ~18-24 month average; ~42% monthly, ~45% annual, balance multi-year. Enterprise LMS contracts often 2-3 years with multi-year discount.
- Multi-year discounts typically add ~5% per additional year.
- Procurement timeline: 30 days for small departmental SaaS up to 6-12 months for enterprise platforms with full security review.

> Sources: AlexanderJarvis (https://www.alexanderjarvis.com/what-is-average-contract-length-in-saas/); Disprz LMS pricing guide (https://disprz.ai/blog/lms-pricing).

### Calendar dead zones

Corporate is the **most variable** segment for calendar:

- End-of-year close (mid-December through New Year's)
- Summer-vacation stretches (varies by industry — retail / financial-services Q4 is locked; consumer goods Q2 push)
- Fiscal-year-end (often Dec 31 or June 30 depending on company)

**PSM rule:** unlike K-12 (uniform July 1 fiscal year) and higher-ed (mostly July 1), corporate fiscal-year-end varies. **Confirm per account before scheduling renewal conversations.**

### Success metrics — Kirkpatrick + Phillips

Two dominant evaluation frameworks for corporate training:

- **Kirkpatrick's Four Levels** — Reaction → Learning → Behavior → Results.
- **Phillips ROI Methodology** — adds a fifth level: ROI (monetize the Level 4 business impact and compare to fully-loaded program cost including learner time). Phillips published the extension in 1980.

> Sources: Whatfix, "Phillips ROI Model" (https://whatfix.com/blog/phillips-roi-model/); CommLabIndia, "Integrating Phillips ROI and Kirkpatrick" (https://www.commlabindia.com/blog/kirkpatrick-philips-model-part4).

Common business-outcome KPIs: sales-rep ramp time, certification rates (compliance, technical), turnover correlation with development access, internal mobility / promotion rate from L&D programs.

**ATD State of the Industry — current numbers (2024-2025):**

- ATD 2024 SOIR: average direct learning expenditure **$1,283 / employee in 2023**, ~17.4 formal learning hours / employee.
- ATD 2025 SOIR: average direct learning expenditure **$1,054 / employee in 2024**, with organizations investing **2.9% of revenue — highest ratio in 5 years**.

The per-employee figure *decreased* while % of revenue *rose* — likely reflects headcount growth outpacing budget growth rather than retrenchment, but ATD's own framing is "resilience."

> Source: ATD, "Optimism Remains Strong for Future of Learning in Organizations" (https://www.td.org/content/press-release/atd-research-optimism-remains-strong-for-future-of-learning-in-organizations); HRTechEdge summary of 2024 SOIR (https://hrtechedge.com/2024-state-of-the-industry-report-workplace-learning-spending-increases-and-key-insights/).

### Regulation

- **GDPR Article 88** (EU) — Member States can set more specific rules for processing employee data, including training. Works councils and country-level rules can constrain LMS rollouts.
- **U.S. state privacy laws** — CCPA / CPRA (CA), VCDPA (VA), CPA (CO), and a growing list — increasingly apply to employee data; HR / L&D systems are in scope.
- **OFCCP / EEOC** — equal-opportunity training and federal-contractor obligations create training-record-retention and content-review requirements for some employers.

### Funding sources and what gets cut first

- **L&D budgets are historically among the first cuts in downturns.** 2008-09 saw >50% of orgs cut training. 2023 Corndel survey: 75% of senior HR leaders said economic uncertainty was impacting L&D strategy; 49% planning to spend less. Recent: 71% of orgs expect to cut L&D if economy worsens, even though 82% recognize leadership development as competitive advantage.

> Sources: AIHR, "Recession-Proof Your L&D Strategies" (https://www.aihr.com/blog/recession-proof-learning-and-development/); Training Industry, "Why Cutting L&D in Economic Uncertainty is a Costly Mistake" (https://trainingindustry.com/articles/strategy-alignment-and-planning/why-cutting-ld-in-economic-uncertainty-is-a-costly-mistake/); People Management, "Half of organisations looking to cut L&D" (https://www.peoplemanagement.co.uk/article/1812542/half-organisations-looking-cut-l-d-costs-amid-economic-difficulty-survey-reveals).

### Vendor-procurement bear traps

- **SOC 2 Type II** is table-stakes for enterprise SaaS L&D procurement.
- **FedRAMP** required only when selling to federal agencies (or federal contractors handling federal data). 325+ controls, $500K-$1M+ investment, 12-24 month authorization. SOC 2 by comparison: ~64 controls, 3-6 months. *Specific cost/time numbers from single vendor source; treat as ballpark.*
- **Legal redlines** — IP indemnification (especially for AI: who owns model outputs, training-data warranties), data-residency, deletion/return-on-termination, audit rights, sub-processor disclosure.

> Source: LowerPlane, "FedRAMP vs SOC 2" (https://lowerplane.com/blog/fedramp-vs-soc-2/).

### 2024-2026 macro context

- **Skills-based hiring gap.** 85% of employers claim skills-based hiring; McKinsey shows adoption rising 40% (2020) → 60% (2024). But Harvard research shows **fewer than 1 in 700 actual hires are affected** by dropped degree requirements — a sharp gap between corporate signaling and operational reality. L&D vendors selling on the skills-based-hiring narrative should know the rhetoric-vs-execution gap.
- **AI-skills urgency** — ATD reports ~2/3 of orgs expect to increase AI practical-skills and AI technical-skills training going forward.
- **LinkedIn 2025 Workplace Learning Report**: 49% of L&D pros agree employees lack the skills to execute business strategy.

> Sources: The Interview Guys, "State of Skills-Based Hiring 2025" (https://blog.theinterviewguys.com/the-state-of-skills-based-hiring/); LinkedIn Learning (https://learning.linkedin.com/resources/workplace-learning-report); ATD 2025 SOIR (above).

---

## Cross-segment comparison

| Dimension | K-12 | Higher-Ed | Corporate L&D |
|---|---|---|---|
| **Top signer** | Superintendent (board above threshold) | CIO + procurement (central) OR dept chair (shadow) | CLO / CHRO (CEO above threshold) |
| **Real influencer** | Curriculum / C&I director | Faculty senate, dept chairs, security team | Business-unit sponsor; security review owner |
| **Buying cycle** | 6+ months; peak July (POs ~14× avg) | RFP 57 days post-to-award + months of prep | 1-12 months, highly variable by spend |
| **Typical contract** | 1-3y, FY-aligned (July 1 start) | Multi-year for core; annual for departmental | 18-24 mo avg SaaS; 2-3y enterprise LMS |
| **Dead zones** | First weeks of school; Dec; testing windows; June close | Finals (Dec, May); summer for faculty; June FY-end | Year-end close; depends on industry FY |
| **Success metric** | State report card: achievement, growth, grad rate, chronic absenteeism, CCR | IPEDS retention / grad rates, OM; enrollment; accreditor cycles | Kirkpatrick L1-L4, Phillips ROI L5; business-unit KPIs |
| **Federal regs** | FERPA, COPPA, IDEA, Title IX, Title I/IV | FERPA (transfers to student), Title IX, Clery, ADA | GDPR Art. 88 (EU), state privacy laws, OFCCP/EEOC |
| **Key state / contract layer** | NY Ed Law 2-d, IL SOPPA, CA SOPIPA + 121+ state laws | HECVAT 4.1.5 (321 Qs + 32 AI Qs) | SOC 2 Type II table-stakes; FedRAMP for gov |
| **Money source** | Federal Titles + state per-pupil + local levy + ESSER (rolled off) | Tuition + state appropriation + endowment + federal research | Operating budget; ~2.9% of revenue (ATD 2025) |
| **First cut in downturn** | Discretionary tech subs; summer programs (practitioner observation) | Hiring freezes; new-program launches | L&D historically among first cuts (>50% in 08-09) |
| **2024-26 macro story** | ESSER cliff; 28+ states with K-12 AI guidance by April 2025 | Demographic cliff begins fall 2025; first per-FTE funding drop since 2012 | AI-skills urgency; skills-based hiring rhetoric vs. <1-in-700 actual hire impact |

---

## Refresh triggers for this document

Re-read and update when:

- A federal funding event materially shifts K-12 or higher-ed budgets (post-ESSER replacement, federal Title funding restructure).
- HECVAT, FERPA, COPPA, or major state student-privacy law materially changes.
- A new ATD State of the Industry Report or LinkedIn Workplace Learning Report publishes.
- New IPEDS reporting requirements or a major accreditor's standards change.
- Grawe demographic-cliff modeling is updated against actual enrollment data 2025-2026.
- State AI policy landscape consolidates (or the December 2025 federal EO either holds or is struck down).
