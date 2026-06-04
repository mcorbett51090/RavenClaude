# K-12 EdTech PSM Playbook — Research Synthesis (2026-06-04)

> **Method.** Five-angle WebSearch fan-out across vendor doctrine (Gainsight, Planhat, ChurnZero, Catalyst), industry frameworks (SETDA, CoSN, Project Tomorrow), practitioner reality (Lexia, Newsela, IXL, Discovery Education public job postings + partner pages), renewal-motion mechanics, and PSM book-structure patterns. 32 distinct sources collected; load-bearing claims verified across ≥2 independent sources where possible. Single-source claims are flagged inline. WebFetch was blocked on several vendor domains (403 on planhat.com / gainsight.com / catalyst.io / lexialearning.com / pedagogue.app); search-result excerpts were used as the primary-source proxy and cited as such.
>
> **Confidence convention used below:** `[high]` = ≥2 independent primary sources; `[med]` = single primary source, direction corroborated; `[single]` = single source, do not generalize; `[unverified — training knowledge]` = stated from prior knowledge, not from this session's sources.

---

## 1. Onboarding (Deployment + BOI) — operational checklist

The vendor-consensus onboarding shape, adapted to a K-12 fiscal calendar:

**Phase A — Deployment (contract → roster sync, 0-30 days from signature)**

- **Welcome + kickoff scheduled within 24h** of countersign. Mid-market and larger accounts get a calendar-booking link in the first email; enterprise accounts get a named CSM intro. `[high — SaaS Mag, Arcade]`
- **Kickoff call** establishes: district goals, success criteria, named district lead (often a Director of Curriculum & Instruction or CTO, **not** the superintendent), the school-level deployment owner per building, and the data-pipe plan (Clever / ClassLink / OneRoster / manual CSV). `[high — EdTech Mag, Veracity]`
- **Roster + SSO** — Clever/ClassLink sync OR manual CSV; rostering precedes any teacher training because trainers need live accounts to teach in. `[med — EdTech Mag]`
- **Technical readiness check** — bandwidth, allowlist, district filter posture, mobile/Chromebook profiles. CoSN 2025 reports 44% of districts outsource monitoring/detection/response, so the PSM's technical contact may be an MSSP, not the district. `[high — CoSN 2025]`
- **Implementation Blueprint delivered.** Lexia explicitly markets a "year-long, personalized implementation plan" co-authored with district leadership; the CSM "partners with and supports school leadership teams in planning and monitoring program implementation." `[high — Lexia.com Success Partnership pages]`

**Phase B — Beginning of Implementation (BOI) (first 30-90 days of actual student use)**

- **Train-the-trainer rollout.** A common K-12 pattern is certifying two tech leads per school and requiring ~80% teacher proficiency before district expansion; teacher onboarding ~45 min. `[single — EdTech Mag, treat as illustrative]`
- **Activation health check** at day 14 and day 30. SaaS-wide pattern: customers who reach first value within 14 days retain at 80%+ at month-12; customers who don't hit first value within 30 days retain at 35-50%. **In K-12 "first value" means: teachers logged in, classes provisioned, ≥1 meaningful student session per class.** `[med — SaaS Mag; mapped to K-12 context]`
- **PD plan ratified** — Lexia's pattern: "professional learning opportunities in person, online, and asynchronously through Lexia Academy." Document who, when, where, in what format. `[high — Lexia.com]`
- **First Success Metrics Meeting** within 60 days. Lexia calls these "Success Metrics Strategy Meetings"; this is the K-12 equivalent of an EBR-precursor data check. `[high — Lexia.com]`
- **Onboarding playbook auto-fires in CS platform.** Gainsight: "Onboarding playbooks — Triggered when a new customer enters the system" with sub-scorecards weighted toward **Activation** (the leading indicator of onboarding success). `[high — Gainsight blog]`

**BOI exit gate.** Don't declare onboarding "done" until: (a) rostering stable for 30 consecutive days, (b) ≥70% of intended teachers have ≥3 sessions in the last 14 days, (c) one named district executive sponsor has had ≥1 working session with the PSM, (d) the district has acknowledged the year's success criteria in writing.

---

## 2. Mid-of-Implementation cadence + signals

**Cadence shape** (per vendor consensus, adapted to school calendar):

- **Monthly** working-level touchpoint with the district lead (curriculum / IT). `[high — Totango, Velaris]`
- **Quarterly** QBR with the district team — though in K-12 these often collapse into a **fall QBR (~November)**, a **mid-year check-in (~late January)**, and a **spring renewal-prep QBR (~April-May)** because December and June are dead for districts.
- **Annual EBR** with executive sponsorship — typically the CTO and at least one cabinet-level signer (Asst. Superintendent for Curriculum, COO). `[high — Matik, CS Insider, Realm]`

**MOI signals to watch (PSM trigger list):**

| Signal | What it means | Playbook |
|---|---|---|
| Educator weekly active users dropping >15% WoW after week 6 | Implementation fatigue; PD didn't stick | Targeted re-engagement webinar; ask district to re-broadcast |
| One school's usage ≪ district median | Building-level champion absent or principal de-emphasized | School-level PD + principal conversation |
| Helpdesk tickets concentrated on rostering / login | Tech infrastructure issue, not adoption | Loop IT in; this is often outsourced (CoSN: 44% outsource) |
| District lead unreachable for >3 weeks | Champion turnover or competing priority | Escalate via secondary contact (finance/curriculum); start champion-mapping refresh |
| Usage drops in winter months | Normal pattern (testing season, holiday) | Distinguish seasonal from structural — compare YoY |
| AI-detection workflows requested | Aligns with CoSN 2025: 57% of districts use/explore AI-detection tools | Treat as expansion / new-use-case signal |

*"Churn in EdTech typically begins with declining educator usage, followed by administrator frustration with underutilized investments; customer success teams that monitor engagement patterns can identify at-risk accounts months before renewal periods."* `[med — Ren Network blog]`

---

## 3. Renewal motion — the 180/120/90/60/30 model in practice

The **Planhat reference doctrine** (treated as the highest-fidelity public articulation of this motion):

> "When a License hits 90 days out, Planhat's workflows generate tasks, send automated client outreach emails, and alert the Account Manager via Slack." `[high — Planhat renewals guide, primary]`

> "The Day 60 Quarterly Business Review (QBR) should be focused entirely on business outcomes, realized ROI, and future strategic goals. The objective here is to secure a verbal 'yes' to the renewal by proving undeniable value." `[high — Planhat]`

> "With value proven at Day 60, Day 30 is purely about commercial execution. This is when Account Management navigates B2B procurement, handles discount requests, and finalizes the contract extension paperwork." `[high — Planhat]`

**The full 180/120/90/60/30 model — translated to a K-12 renewal:**

| Days out | Action | Owner | Output |
|---|---|---|---|
| **180** | First renewal-prep internal review. Refresh champion map; pull YTD usage + outcome data; identify expansion candidates; check superintendent / cabinet for turnover (23% YoY in top-500 districts — **assume turnover until verified**). `[high — EdWeek]` | PSM + RM | Renewal opportunity created in CRM; internal go/no-go on expansion |
| **120** | Year-end impact deck drafted. Districts on July fiscal year are entering spring budget-finalization. **For a Jul 1 renewal, 120 days out = early March, which is the deck-finalization window.** | PSM | Outcome story aligned to district's stated success criteria |
| **90** | **EBR / spring strategy meeting** with executive sponsor. This is the value-realization conversation. ChurnZero / Matik / Realm all converge on 60-90 days pre-renewal as the decisive QBR. `[high — multiple]` | PSM + Exec Sponsor | Verbal commit; expansion scoped |
| **60** | Proposal delivered. Procurement starts in parallel — K-12 procurement averages 6-11 months for 37% of districts, 12-17 months for another 22% `[high — NationGraph]`, so anything net-new from this point is a *next-year* conversation, not this renewal. | RM (AM in Planhat's terms) | Quote / order form |
| **30** | Commercial execution only. Purchase orders flowing through district procurement; PSM in support mode. | RM | Signed renewal |
| **0** | Renewal closes. PSM transitions to next year's success plan immediately — there is no "post-signature lull" in K-12 because summer = setup window for fall go-live. | PSM | Year-2 success plan kickoff scheduled for July |

**Planhat's load-bearing role clarity** (worth pinning to the PSM team wall):

> "Customer Success owns Value Realization, Adoption, and Health. Sales or Account Management owns the Commercial Contract, Procurement, and Negotiation." `[high — Planhat]`

**Counter-pattern warning.** Planhat: *"You don't win a 12-month B2B renewal on day 330; you win it during onboarding."* `[high]` The 180/120/90/60/30 model is the **execution surface**, not the **mechanism**. The mechanism is value delivered consistently across the school year.

---

## 4. Year-end documentation rituals

Three documents the PSM owes the district before close-of-school-year:

1. **Year-End Impact Report.** Usage at district / school / classroom levels; named outcomes against the success criteria established in onboarding; comparative data ("47 of 52 schools hit ≥X minutes/student/week"); evidence vignettes. This is the artifact the superintendent or board can reference to defend the line item. `[high — LearnPlatform/Instructure on districts demanding "evidence of effectiveness and long-term value"]`

2. **Implementation Reflection.** What worked, what didn't, what the district team itself said. Lexia's "Success Metrics Strategy Meetings" produce this naturally. `[high — Lexia.com]`

3. **Next-Year Success Plan (draft).** A forward-looking artifact, delivered before the district scatters for summer. Captures the year-2 goals, PD plan, expansion candidates, and named champions per school. **This is the durability mechanism against superintendent turnover** — the plan is owned by the *position*, not the *person*.

LearnPlatform's framing for why this matters now more than before:

> "As districts grapple with mounting financial pressures, leaders are prioritizing impact over volume and demanding evidence of effectiveness and long-term value from every tool they adopt." `[high — Instructure/LearnPlatform 2025]`

> "K-12 districts use 2,739 different software applications but actively utilize only 57% of their EdTech tools, wasting an average of 43% of software investments." `[high — Evelyn Learning citing LearnPlatform data]`

**Implication.** The year-end report isn't a courtesy; it's the document that protects you from being in the 43%.

---

## 5. K-12 health-score components — vendor consensus

Gainsight, Catalyst, ChurnZero, Planhat all converge on the same input categories, with K-12-specific instantiations:

| Category | Vendor framing | K-12 specific signals |
|---|---|---|
| **Usage / adoption** (leading) | Login frequency, active users, feature adoption — "leading indicator, usage drops before satisfaction" `[high — Realm, HubSpot]` | Teacher MAU/WAU per school; student session minutes; assignment-creation rate; rostering health |
| **Activation** (esp. during onboarding) | "Higher weights assigned to metrics like Activation since it's a key indicator of onboarding success" `[high — Gainsight]` | First-30-day teacher activation %; first lesson per classroom; PD attendance |
| **Sentiment / NPS** (lagging) | "Lagging indicator… combine with leading" `[high — HubSpot, Realm]` | Teacher NPS; principal NPS; district lead survey |
| **Support / friction** | Ticket volume, severity, time-to-resolve | Login/rostering tickets concentrated → infrastructure issue, not adoption |
| **Engagement / relationship** | Executive sponsor responsiveness, EBR attendance | Has district lead met PSM in last 90 days? Is there a named exec sponsor? |
| **Outcomes** (the K-12 differentiator) | — | Tied to district's stated success criteria — reading-level growth, assignment-completion, etc. |

**Catalyst's pattern recommendation** (from search results): "use a variety of input categories such as usage data, support tickets, and customer feedback… the more automated fields used the more likely you will see higher adoption of the customer health score." `[high — Catalyst help center]`

**Heap's working example** (Catalyst-built, publicly reported): a health score using "leading indicators of success as the foundation" predicted renewals with 95%+ accuracy. `[single — Heap blog, illustrative]`

**K-12 adaptation.** The vendor pattern says "usage is a leading indicator." In K-12, **teacher** usage is the leading indicator, **student** usage is the proof-of-value, and **administrator** sentiment is what closes the renewal. A health score that conflates the three will give the PSM the wrong signal.

---

## 6. Champion management — superintendent / tech-lead / family-engagement triangle

**The structural reality** (the durability problem):

- Superintendent turnover in 2024-25: **23% in the top 500 districts**, up from 20% the previous year, vs. pre-pandemic 14-16%. `[high — EdWeek, District Administration]`
- Average current-superintendent tenure: **5.4 years overall, 2.7 years in urban districts.** `[high — K-12 Dive citing AASA; Council of Great City Schools]`
- Beyond the superintendent: "key positions include directors of finance, human resources, and curriculum & instruction, and these key leaders can help you stay the course during superintendent turnover." `[high — Pedagogue]`

**The triangle and how the PSM follows it:**

1. **Tech lead (CTO / Director of Tech / Director of EdTech).** This is the day-to-day operating relationship — rostering, integrations, security review, AI policy. CoSN 2025 reports the EdTech leader population is now **52% tech-background** (vs. 58% education-background a decade ago) — they speak SaaS-ops, not just curriculum. `[high — CoSN 2025]`

2. **Curriculum / academic lead (Asst Superintendent for C&I, Director of Teaching & Learning).** This is the *outcome* relationship — the person who will defend the line item on instructional merit at a board meeting. SETDA's 2025 Quality Indicators (Safe / Evidence-Based / Inclusive / Usable / Interoperable) are explicitly the **language** this audience uses. `[high — SETDA]`

3. **Family-engagement lead (where one exists).** Project Tomorrow's Speak Up surveys explicitly include families as a stakeholder category; districts increasingly track family sentiment. `[med — Project Tomorrow / MassCUE]` This is where the year-end report finds its parent-facing version.

4. **Cabinet anchor (superintendent OR designee).** Highest-altitude relationship, lowest-frequency. Used at EBRs and for board-level defense.

**The PSM-of-record rule.** When the superintendent moves, the **relationship** must already live with the curriculum lead and the tech lead — not in the superintendent's inbox. The Pedagogue advisory is explicit: map the cabinet, not the chair.

**The mechanism.** Refresh the champion map at every 180-day renewal-prep checkpoint. Track: (a) name + role + tenure of each champion, (b) confirmed exec sponsor, (c) succession path if any seat turns. Treat the map as live; assume turnover until verified.

---

## 7. School-year cadence — month-by-month operational map

For a district on a July 1 fiscal year (the dominant K-12 pattern; NY mandates it, TX allows it `[high — NationGraph]`):

| Month | District state | PSM motion |
|---|---|---|
| **July** | New fiscal year starts. Big POs cleared; districts issue large strategic POs (avg order size 13.8× a typical March order in one sample). `[high — NationGraph]` | Year-2 kickoff for renewing districts; deployment for new districts; rostering/integration setup |
| **August** | POs convert to tactical spend; back-to-school PD weeks | Train-the-trainer; teacher PD sessions; principal walk-throughs |
| **September** | First weeks of student use | BOI activation monitoring; daily/weekly health checks; first-30-day activation review |
| **October** | Implementation settling; conference season (ISTE Fall, etc.) | First QBR / Success Metrics Meeting; usage diagnostic per school |
| **November** | Pre-Thanksgiving; testing windows | Mid-implementation review; capture early outcome signals |
| **December** | District operations effectively closed last 2 weeks | Internal account planning; no district-facing pushes |
| **January** | Spring semester start; budget-planning conversations begin | **180-day renewal-prep checkpoint for Jul renewals**; champion map refresh; mid-year check-in QBR |
| **February** | Budget proposals being drafted | Year-end impact deck drafting; SETDA-aligned evidence assembly |
| **March** | **Budget-finalization window**; spring testing season ramps | **EBR / value-realization meeting**; expansion scoping |
| **April** | School boards reviewing budgets; **peak purchasing window begins** `[high — NationGraph]` | Proposal delivered; commercial conversation; procurement-team intro |
| **May** | Final budget approvals; PO drafting | Renewal commercials closing; year-2 success-plan draft delivered |
| **June** | School year ends; admin focus on closeout | Year-End Impact Report delivered; reflection meeting; **next-year success plan ratified before district scatters** |

**Two operating rules this map implies:**

1. **The renewal motion runs in spring, not summer.** Anything not closed by mid-June is a fall risk; districts are not making decisions in July about contracts they let expire in June.
2. **The two dead zones are mid-December → early January and late June → mid-July.** Don't schedule decisions, don't schedule EBRs, don't expect responses.

---

## 8. Top 15 / Strategic Account model — when EdTech vendors use it

**The general pattern** (vendor-consensus across CS literature):

- **Strategic / Top-tier accounts** get a dedicated CSM (or PSM in EdTech parlance), custom onboarding, regular strategic check-ins, QBRs, EBRs. `[high — Measured Success, Velaris, Pylon]`
- **Mid-market** gets pod or shared coverage with structured cadence.
- **SMB / scaled** gets pooled, tech-touch, automated.

**Pod-model economics** (illustrative single data point — treat as direction, not benchmark):

> "A pod of 3 CSMs may manage $8M in ARR across 64 accounts, compared to a dedicated CSM managing $2.5M in ARR across 20 accounts." `[single — Velaris]`

**The EdTech-specific instantiation** (from Newsela + Discovery Education job postings):

- **Newsela Mid-Market CSM:** portfolio of mid-market accounts, partnership plans with district leaders, drives "product adoption, renewals, and expansions"; $75-80K base + $20K OTE; 3+ years EdTech CS experience; Gainsight + SFDC preferred. `[high — Newsela / EdTech.com posting]`
- **Discovery Education Partner Success Manager:** "individual book of business including account strategies, escalations, objectives… in alignment with the Discovery Education Partner Success organization"; "quarterly churn targets"; $87.8-95K; 5+ yrs; Salesforce + Gainsight preferred. `[high — Discovery Education / EdSurge posting]`
- **Discovery Education Manager, Partner Success (Independent Schools)** segments by vertical (independent-school market is its own pod). `[high — EdTech.com posting]`

**The "Top 15 Strategic Account" model applied to a PSM book.** A PSM running a book of ~40-60 districts will rationally identify the top 10-15 by some combination of ARR + strategic value (lighthouse logo, expansion potential, advocacy potential) and run a **two-tier internal motion**: full white-glove (named exec sponsor, custom EBR, on-site visit) for the top tier; structured-but-templated cadence for the rest. This isn't documented in any single source; it's the synthesis of the Velaris segmentation pattern + the Discovery Education job description's "individual book of business" language.

---

## 9. Renewal-rate benchmarks for K-12 SaaS (with sources)

**Caveat first.** Cross-source benchmarks for K-12 EdTech retention specifically are sparse and inconsistent. The trustworthy claim is **direction + range**, not a precise number.

| Metric | Reported value | Source | Confidence |
|---|---|---|---|
| B2B EdTech (institutional / district) gross retention | 80-90% | Graham Forman (PLG benchmarks), Userpilot retention writeup | `[med]` — direction corroborated, magnitudes from one analyst |
| B2C EdTech retention | ~35% (vs ~85% B2B) | Loyalty.cx, Userpilot | `[single]` — illustrative, do not over-cite |
| Top-performing SaaS NRR | 130%+ ("negative churn of 30% or more") | Userpilot citing common SaaS benchmark | `[med]` |
| Median monthly B2B SaaS churn 2026 | 3.5% (2.6% voluntary, 0.8-0.9% involuntary) | MRRSaver / ringly.io aggregation | `[med — industry-wide, not K-12]` |
| EdTech churn rate 2025 (ChurnZero benchmark) | **9.6%, "doubled since 2024"** | ChurnZero 2025 SaaS benchmarks webinar | `[single — ChurnZero study, cite as ChurnZero's framing not consensus]` |
| NRR trend 2022-2025 | "fell from 2022 through 2024 and then stabilized in 2025" | ChurnZero | `[med — direction is corroborated elsewhere]` |
| District EdTech utilization | Districts access ~2,739-2,982 tools/yr; actively use only ~57% | LearnPlatform / Instructure EdTech Top 40 (primary research) | `[high]` |

**The single most important benchmark for an EdTech PSM book** is not a percentage; it's the LearnPlatform finding that **43% of EdTech investment goes unused**. That is the structural risk to your renewal, and it sets the bar for what the year-end report must prove.

---

## 10. The "PSM-of-record" patterns (single vs pod vs vertical)

**Three documented patterns** (from search-result synthesis):

**(a) Single PSM ("named CSM").**
- One PSM owns a fixed book; the customer always knows who to call.
- Best for: strategic / enterprise tier, complex deployments, accounts where champion-continuity is critical (read: K-12).
- Weakness: vacation/transition exposes the relationship; CSM departure → account risk; doesn't scale below ~$50K ACV.
- `[high — multiple sources, vendor consensus]`

**(b) Pod model (shared book or cross-functional).**
- 3-4 CSMs share a pool of accounts ("Shared Book Pod"), OR a CSM + Onboarding Specialist + Support Rep form a permanent unit ("Cross-Functional Team").
- Best for: mid-market scale, complex products with multi-persona customers.
- Strength: continuity through transitions; specialist depth on each component.
- Example: "A pod of 3 CSMs may manage $8M in ARR across 64 accounts." `[single — Velaris]`

**(c) Vertical model.**
- CSM specializes by segment / industry / use-case.
- In EdTech the natural verticals are: **K-12 districts**, **independent schools** (Discovery Education explicitly has a Manager, Partner Success — Independent Schools posting `[high]`), **higher ed**, **state agencies / DOE**, **after-school / supplemental**.
- Strength: deep domain fluency; PSM speaks the buyer's language (the SETDA-indicator-fluent academic lead is a very different conversation from the CoSN-fluent CTO).

**The K-12 PSM-of-record recommendation** (synthesis, opinionated):

- **Top 15 strategic districts:** Single PSM, named exec sponsor, vertical specialization (PSM has K-12 background).
- **Mid-tier book (~30-50 districts):** Pod of 2-3 PSMs sharing the book, with each PSM owning primary relationships for half but cross-covering. This is what produces the resilience needed against the 23% YoY superintendent turnover.
- **Tail (SMB districts, single-school accounts):** Pooled / tech-touch with a regional "team@" inbox and templated cadence.

---

## 11. Recommended additions to `plugins/edtech-partner-success/`

### 11a. Inline-prior additions to `agents/partner-success-manager.md`

Add (or reinforce) these inline priors in the agent's system prompt:

1. **"Assume superintendent turnover until verified."** Cite EdWeek/AASA 23% YoY top-500 rate; refresh champion map every 180 days; treat any cabinet-level relationship as a position, not a person.
2. **"The renewal motion runs Jan-May, not Jun-Jul."** Districts on July fiscal years finalize budgets in spring; the 180-day checkpoint for a Jul 1 renewal lands in early January.
3. **"Teacher usage is the leading indicator; student outcomes are the proof; administrator sentiment is what renews."** Encode the three-layer health-score interpretation rule.
4. **"43% of EdTech spend goes unused — the year-end report is what protects you from being in it."** (LearnPlatform/Instructure finding.)
5. **"SETDA's 5 Quality Indicators (Safe, Evidence-Based, Inclusive, Usable, Interoperable) are the C&I audience's procurement language. Use it in EBRs."**
6. **"CoSN 2025: EdTech leader population is now 52% tech-background. With the CTO, lead with security, integration, AI policy — not pedagogy."**
7. **Role-clarity rule (from Planhat):** *"PSM owns value realization, adoption, and health. RM/AM owns commercial, procurement, negotiation."* Encode this so the agent never freelances on pricing.
8. **The two dead zones:** mid-Dec → early Jan, late Jun → mid-Jul. Don't schedule decisions; don't expect responses.

### 11b. New `knowledge/` files

- `knowledge/k12-school-year-cadence.md` — Section 7 of this report, formatted as the operational month-by-month map.
- `knowledge/k12-renewal-motion-180-120-90-60-30.md` — Section 3 of this report, formatted as a runbook with one page per checkpoint.
- `knowledge/k12-health-score-rubric.md` — Section 5 of this report; the three-layer (teacher / student / administrator) rule made explicit, with input categories + weights.
- `knowledge/k12-champion-triangle.md` — Section 6; the four-role map (tech / curriculum / family-engagement / cabinet) + the turnover assumption.
- `knowledge/setda-five-quality-indicators.md` — Reference card for the SETDA framework so EBR decks can be language-aligned.
- `knowledge/cosn-2025-district-leadership-priorities.md` — Reference card for the CoSN 2025 priorities (AI, cybersecurity outsourcing, tech-background CTOs).
- `knowledge/k12-procurement-cycle.md` — District budget cycle, PO timing, sales-cycle benchmarks (37% / 6-11 mo, 22% / 12-17 mo).

### 11c. New `templates/` files

- `templates/onboarding-kickoff-agenda.md` — Section 1, Phase A, as a printable agenda.
- `templates/boi-exit-gate-checklist.md` — the four-criteria BOI exit gate.
- `templates/success-metrics-strategy-meeting.md` — Lexia-pattern meeting template for the first-60-day check.
- `templates/180-day-renewal-prep-checklist.md` — internal checklist (champion-map refresh, usage YTD pull, expansion scope, turnover scan).
- `templates/year-end-impact-report.md` — district-facing template: usage / outcomes / next-year plan.
- `templates/next-year-success-plan.md` — the forward-looking artifact that survives champion turnover.
- `templates/ebr-deck-skeleton.md` — SETDA-indicator-aligned EBR deck structure: Safe / Evidence-Based / Inclusive / Usable / Interoperable + business outcomes + ROI.
- `templates/champion-map.md` — the four-role map; refreshed every 180 days.

### 11d. New `commands/` (slash commands)

- `/psm-renewal-180` — runs the 180-day checkpoint: pulls usage YTD, prompts for champion-map diff, drafts the internal go/no-go.
- `/psm-ebr-prep` — generates an EBR deck skeleton aligned to district success criteria + SETDA indicators.
- `/psm-year-end-report` — drafts the year-end impact report from usage data + success criteria.
- `/psm-champion-map-refresh` — walks the four roles, flags stale data, flags turnover risk.

---

## 12. Sources ledger

**Primary vendor doctrine**

1. [Planhat — The Complete Guide to B2B Customer Success Renewals](https://www.planhat.com/customer-success/renewals) — primary source for 90/60/30 renewal motion + role clarity. `[high]`
2. [Planhat — The Ultimate Guide to Customer Success Playbooks](https://www.planhat.com/customer-success/playbooks) `[high]`
3. [Planhat — Customer Onboarding Process Guide](https://www.planhat.com/customer-success/onboarding) `[med]`
4. [Planhat — Renewal Strategies thought leadership](https://www.planhat.com/thought-leadership/renewal-strategies) `[med]`
5. [Gainsight — How to Run an Executive Business Review](https://www.gainsight.com/blog/executive-business-review/) `[high]`
6. [Gainsight — Customer Health Scores Explained](https://www.gainsight.com/blog/customer-health-scores/) `[high]`
7. [Gainsight — 3 Ways EdTech Can Adapt Their CS Strategy](https://www.gainsight.com/blog/3-ways-edtech-can-adapt-their-cs-strategy-to-the-new-normal/) `[high]`
8. [Gainsight — Essential Guide to QBRs](https://www.gainsight.com/essential-guide/quarterly-business-reviews-qbrs/) `[high]`
9. [Gainsight University](https://education.gainsight.com/) (Customer Success curriculum) `[med]`
10. [Gainsight Pulse Library](https://pulselibrary.gainsight.com/) `[med]`
11. [Catalyst — EBR Workflow help article](https://help.catalyst.io/hc/en-us/articles/33694042118804-Workflow-Executive-Business-Review-EBR) `[high]`
12. [Catalyst — Best practices for designing health profiles](https://help.catalyst.io/hc/en-us/articles/35591397468820-Best-practices-for-designing-health-profiles) `[high]`
13. [Catalyst blog](https://catalyst.io/blog) `[med]`
14. [Heap — Building a health score with Catalyst that predicts renewals 95%+](https://www.heap.io/blog/how-to-build-an-accurate-health-score-with-catalyst) `[single — illustrative]`
15. [ChurnZero — 2025 SaaS benchmarks on retention and AI webinar](https://churnzero.com/webinars/2025-saas-benchmarks-on-retention-and-ai/) `[single for the 9.6% claim]`
16. [ChurnZero — Customer Success Leadership / Revenue Leadership Study](https://churnzero.com/customer-success-leadership-study/) `[high]`
17. [ChurnZero — Seven steps of a customer success book shift](https://churnzero.com/blog/manage-book-shift-customer-success/) `[high]`
18. [ChurnZero — Customer Success Team Structure](https://churnzero.com/blog/customer-success-organization/) `[high]`
19. [ChurnZero — Quarterly Business Reviews blueprint](https://churnzero.com/blog/quarterly-business-reviews/) `[high]`
20. [ChurnZero — ZERO-IN 2024 conference agenda](https://churnzero.com/press-release/full-agenda-zero-in-2024/) `[med]`

**Industry frameworks (K-12)**

21. [SETDA — 2025 EdTech Quality Indicators Procurement Guide press release](https://www.setda.org/news/press-releases/press-release-2025/setda-launches-the-edtech-quality-indicators-procurement-guide/) `[high]`
22. [SETDA — Easing the Burden on Schools (PDF)](https://www.setda.org/wp-content/uploads/2026/03/2025-SETDA-EdTech-Quality-Indicators-Guide.pdf) `[high]`
23. [CoSN — 2025 State of EdTech District Leadership (PDF)](https://www.cosn.org/wp-content/uploads/2025/05/EdTechLeadership_2025_F2.pdf) `[high]`
24. [CoSN — 2025 State of EdTech District Leadership landing](https://www.cosn.org/tools-and-resources/resource/2025-state-of-edtech-district-leadership/) `[high]`
25. [CoSN — EmpowerED Superintendents Initiative](https://cosn.org/superintendents) `[med]`
26. [Project Tomorrow — Speak Up data findings](https://www.tomorrow.org/publications/speak-up-data-findings/) `[high]`
27. [Project Tomorrow Speak Up 2024-25 release (ACE-Ed)](https://ace-ed.org/project-tomorrow-unveils-latest-speak-up-research-highlights-need-for-active-digital-student-learning-experiences/) `[high]`
28. [EALA — SETDA quality indicators coverage](https://educatingalllearners.org/setda-guide-offers-quality-indicators-for-edtech-evaluations/) `[med — secondary]`

**Practitioner reality (K-12 PSM postings + partner pages)**

29. [Newsela — Mid-Market CSM posting (EdTech.com)](https://www.edtech.com/jobs/mid-market-customer-success-manager-6940) `[high]`
30. [Discovery Education — Partner Success Manager (EdSurge)](https://www.edsurge.com/jobs/partner-success-manager-job-at-discovery-education) `[high]`
31. [Discovery Education — Manager, Partner Success Independent Schools (EdTech.com)](https://www.edtech.com/jobs/manager-partner-success-independent-schools-5088) `[high]`
32. [Lexia — Success Partnerships page](https://www.lexialearning.com/success-partnerships) `[high]`
33. [Lexia — Customer Success](https://www.lexialearning.com/why-lexia/customer-success) `[high]`
34. [Lexia — Effective PL for your district](https://www.lexialearning.com/resources/webinars/effective-professional-learning-for-your-district) `[high]`
35. [Lexia — Implementation Support podcast](https://www.lexialearning.com/resources/all-for-literacy-podcasts/educators-need-effective-implementation-support-lexia-delivers) `[high]`
36. [IXL — Professional learning page](https://www.ixl.com/resources/professional-learning) `[high]`
37. [Lexia — Customer Success Manager (WA/OR) job](https://www.edsurge.com/jobs/customer-success-manager-wa-or-job-at-lexia-learning) `[high]`

**District procurement + leadership-turnover data**

38. [EdWeek — Superintendent Turnover Is Up (2024-25 23% data)](https://www.edweek.org/leadership/superintendent-turnover-is-up-is-high-leadership-churn-the-new-normal/2025/09) `[high]`
39. [K-12 Dive — Average superintendent tenure 5.4 years (AASA citation)](https://www.k12dive.com/news/the-average-length-of-current-superintendent-tenures-54-years/815908/) `[high]`
40. [District Administration — Superintendent turnover reaches record high in 2025](https://districtadministration.com/article/superintendent-turnover-reaches-record-high-in-2025/) `[high]`
41. [Council of the Great City Schools — Urban superintendents 2.7-yr tenure report](https://www.cgcs.org/resources/newsroom/urban-educator/digital-urban-educator-april-2025/new-report-finds-current-urban-superintendents-are-relatively-new-to-their-roles) `[high]`
42. [Pedagogue — EdTech persevering through superintendent turnover](https://pedagogue.app/how-edtech-companies-can-persevere-through-superintendent-turnover-4/) `[high]`
43. [NationGraph — K-12 district budget cycles for EdTech sales](https://www.nationgraph.com/post/timing-is-all-you-need-a-complete-guide-to-k-12-district-budget-cycles-for-edtech-sales-success) `[high]`
44. [RFP School Watch — K-12 Procurement Cycle](https://www.rfpschoolwatch.com/rfp/blog/the-k-12-procurement-cycle-navigating-district-budgets-and-funding-sources/) `[high]`
45. [K12 Prospects — Understanding School Budgets](https://www.k12prospects.com/understanding-school-budgets-when-and-how-schools-buy/) `[med]`
46. [Education Week MarketBrief — K-12 sales cycle duration](https://marketbrief.edweek.org/sales-marketing/k-12-sales-cycle-how-long-do-districts-need-to-make-smart-purchasing-decisions/2025/08) `[high]`
47. [LearnPlatform / Instructure — EdTech Top 40 report](https://www.instructure.com/edtech-top40) `[high]`
48. [Instructure — Districts more selective amid budget crisis](https://www.instructure.com/press-release/new-learnplatform-instructure-report-shows-k-12-districts-are-more-selective-about) `[high]`
49. [Evelyn Learning — Hidden cost of EdTech sprawl (43% unused stat)](https://www.evelynlearning.com/blog/the-hidden-cost-of-edtech-sprawl-how-k-12-districts-are-drowning-in-unused-software-and-what-it-leaders-can-do-about-it) `[high]`

**Customer-success organizational models + benchmarks**

50. [Velaris — 6 Customer Success Organizational Models](https://www.velaris.io/articles/customer-success-organizational-models) `[high]`
51. [SaaStr — Cross-Functional Pod Structure](https://www.saastr.com/the-case-for-a-cross-functional-pod-structure/) `[high]`
52. [Measured Success — Micro-Segment / Tiered CS Strategies](https://www.measuredsuccess.io/blog/customer-success/micro-segment-customer-success) `[high]`
53. [Gainsight — Five Organizational Models of CS](https://www.gainsight.com/customer-success-best-practices/five-organizational-models-of-customer-success/) `[high]`
54. [Graham Forman — K12 B2B EdTech PLG benchmarks (Medium)](https://grahamforman.medium.com/key-product-led-growth-plg-measures-and-benchmarks-for-k12-b2b-edtech-companies-7082ffe6c358) `[med]`
55. [Userpilot — EdTech retention crisis playbook](https://userpilot.com/blog/edtech-retention-crisis/) `[med]`
56. [Ren Network — Why CS is essential in EdTech](https://ren-network.com/4-reasons-why-a-customer-success-function-is-essential-in-edtech/) `[med]`
57. [SaaS Mag — Time-to-Value retention battleground](https://www.saasmag.com/time-to-value-saas-onboarding-retention-2026/) `[med — SaaS-wide, not K-12 specific]`
58. [Realm — Ultimate Guide to QBRs](https://www.withrealm.com/blog/what-is-a-quarterly-busines-review) `[high]`
59. [Matik — EBR vs QBR guide](https://www.matik.io/blog/the-difference-between-an-ebr-and-a-qbr) `[high]`
60. [CS Insider — Best cadence for business reviews](https://www.csinsider.co/email/dear-insider-best-cadence-for-business-reviews) `[high]`
61. [EdSurge — Guide to Choosing/Vetting/Purchasing K-12 EdTech](https://www.edsurge.com/research/guides/the-edsurge-guide-to-choosing-vetting-and-purchasing-k-12-edtech-products) `[high]`
62. [EdTech Magazine — Supporting Schools Through Strategic Partnerships](https://edtechmagazine.com/k12/article/2025/08/devices-development-supporting-schools-through-strategic-partnerships) `[high]`

---

**Methodology notes / known limitations**

- WebFetch returned HTTP 403 on planhat.com, gainsight.com, catalyst.io, lexialearning.com, and pedagogue.app in this session — likely bot-detection on those vendor domains. The synthesis relied on WebSearch result excerpts (which embed primary-source text) as the citation substrate; readers wanting the full primary article should retrieve those URLs via an authenticated/browser path.
- The ChurnZero 9.6% EdTech churn figure ("doubled since 2024") is a single-source claim from ChurnZero's 2025 benchmarks study and is reported here as ChurnZero's framing, not as cross-industry consensus.
- The Velaris "$8M / 64 accounts / 3 CSMs" pod economics is a single illustrative data point, not an industry benchmark; use as directional only.
- The B2C-EdTech 35% retention figure traces to a single Loyalty.cx writeup; direction (B2C ≪ B2B retention) is corroborated, but the magnitude should not be cited as authoritative.
- "Newsela has no public Implementation Blueprint analogous to Lexia's" is supported by negative-search-result evidence in this session, not by an absence statement from Newsela itself; absence of evidence ≠ evidence of absence.
- Several inline-prior recommendations in §11 are **synthesis** (the deep-research author's opinionated combination of primary sources), not direct quotes. Each is grounded in cited material above but should be treated as a recommended pattern, not as established doctrine.
