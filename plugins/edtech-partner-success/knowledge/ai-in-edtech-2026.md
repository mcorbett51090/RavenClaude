# AI in EdTech — the 2026 landscape

> **Last reviewed:** 2026-05-21. Sources: vendor pricing pages (Khanmigo + MagicSchool primary-verified 2026-05-21), EdWeek Research Center + RAND American Teacher Panel (adoption stats), Common Sense Media + Pew Research (parent/teen surveys), Federal Register (COPPA amendments), White House EO archive, Ballotpedia + Stateline (state guidance tracker), EdWeek + EdSource (LAUSD/AllHere case), Magnolia Tribune (Mississippi pilot), Houston Public Media (Houston ISD), Akin Gump + Alston & Bird + DLA Piper (legal analysis of December 2025 federal EO). Refresh when: (a) a new major federal AI executive order ships, (b) state student-privacy law with AI-specific provisions passes (CA AB 1159 most likely), (c) COPPA enforcement actions surface a pattern, (d) a marquee deployment publishes outcome data (NH Khanmigo, MS pilot, Newark), or (e) any vendor in the table below makes a material pricing change.

This file is the **PSM-side situational awareness** on AI in EdTech as of mid-2026. The field is moving fast; pricing and policy claims carry retrieval dates. Confidence notation: **High** = primary source verified, **Medium** = single credible source or practitioner consensus, **Low** = directional only.

---

## 1. The vendor landscape (three tiers)

The market has solidified into three tiers in 2026:

### Tier 1 — General-purpose chatbots with school SKUs

| Vendor | Offering | Pricing / availability |
|---|---|---|
| **OpenAI** | ChatGPT for Teachers | **Free** for verified US K-12 educators through June 2027 (GPT-5.1, walled-off educator environment with student-data + training protections). **Confidence: High** [EdWeek](https://www.edweek.org/technology/more-teachers-are-using-ai-in-their-classrooms-heres-why/2026/01) retrieved 2026-05-21 |
| **Anthropic** | Claude for Education | Launched April 2025. Higher-ed first (Learning Mode, Socratic tutoring); K-12 support "on the horizon" as of early 2026. Powers Khanmigo via Khan Academy + Anthropic partnership. **Confidence: High** for higher-ed; **Medium** for K-12 timing [Anthropic](https://claude.com/solutions/education) |
| **Microsoft** | Microsoft 365 Copilot for Education | **$18/user/month academic SKU** from December 2025; teen Copilot Chat access enabled by tenant admins from late July 2025; "Teach" feature launched Oct 2025 generates standards-aligned lesson plans for 35+ countries. **Confidence: High** on features [Microsoft Education Blog](https://www.microsoft.com/en-us/education/blog/2025/06/empowering-educators-with-ai-innovation-and-insights/) |
| **Google** | Gemini for Education + NotebookLM | No published per-seat education pricing surfaced. Confirmed K-12 traction via the Mississippi statewide pilot (Dec 2025). **Confidence: Medium** |

**PSM tell:** when a partner asks "what about ChatGPT?", they often mean the free educator tier — they're not necessarily evaluating a paid vendor.

### Tier 2 — EdTech-vertical AI startups (teacher-tool layer)

| Vendor | Pricing | Key fact |
|---|---|---|
| **Khanmigo** (Khan Academy + Anthropic) | **Free for teachers worldwide; $4/mo or $44/yr for individual learners + families** (no separate family-tier price). **Verified 2026-05-21** [khanmigo.ai/pricing](https://www.khanmigo.ai/pricing) | NH statewide contract: $2.3M federal COVID-relief, ~5,000 educators, ~40,000 students, 50 districts |
| **MagicSchool** | **Free / Plus $8.33/user/mo annual ($12.99 monthly) / Enterprise custom**. **Verified 2026-05-21** [magicschool.ai/pricing](https://www.magicschool.ai/pricing) | Vendor claims usage in "nearly every U.S. school district." Treat as marketing — the verified data point is brand recognition, not blanket coverage. |
| **SchoolAI** | Free for individual teachers; school/district plans custom (no public price page) | Differentiator: "Spaces" — pre-configured AI activity environments students engage with under teacher monitoring |
| **Brisk Teaching** | Free / Brisk Pro ~$9.99/mo list / school district custom | Chrome extension on Google Docs/Slides; notable feature: student-writing-history view for integrity |
| **Curipod** | Free tier / Premium ~$7.50/mo annual ($9 monthly) / school site licenses | AI-feedback engine returns rubric-aligned feedback |
| **Eduaide.Ai** | Free (15 generations/mo) / Pro ~$5.99/mo unlimited | "Erasmus" differentiation assistant; vendor claims "rooted in 1,000+ peer-reviewed articles" |

**Pricing-claim discipline:** Khanmigo + MagicSchool are primary-verified on this file's last-reviewed date. The others are sourced from secondary aggregators (vendor pricing pages were not all accessible at fetch time). **Verify on the vendor's page before quoting in a client engagement.**

### Tier 3 — LMS-embedded AI

| LMS | AI posture | Pricing model |
|---|---|---|
| **Canvas (Instructure)** | Global partnership with OpenAI (InstructureCon 2025); LLM-Enabled Assignments + Khanmigo widgets embed at no add-on cost — **but the institution provides its own LLM API key** so the AI usage cost passes through to the district / university. Advanced "IgniteAgent" tooling is a paid add-on (undisclosed pricing). | BYO-API-key + Canvas license; IgniteAgent custom |
| **D2L Brightspace** | "Lumi" student-facing tutor + Brightspace Virtual Assistant for in-product help | Consultative; third-party reports cite ~$30K/year for 500 users as a rough anchor (secondary) |
| **Blackboard / Schoology / Moodle** | All shipping AI features in 2025 (grading assistants, content generation, discussion summarization) | Consultative — no consistently-published add-on pricing |

**For higher-ed engagements:** the 2025 norm is now **"AI policy required in every syllabus"** (UNC mandates, Penn State recommends, Cornell publishes guidance). The conversation has shifted from blanket bans to explicit per-course rules.

### Corporate L&D AI (briefly)

- **Cornerstone Galaxy** (2025) — AI agents (learner/admin/content) embedded across the platform; Salesforce partnership ("agentic enterprise"); skills-gap analytics tied to Workday
- **Workday + Degreed** integration — bidirectional skills-graph data
- **Honest framing:** "AI-driven personalized learning paths" is real as a *feature* but ROI vs. well-designed traditional curriculum is **not independently established** as of mid-2026. Treat as feature claim, not outcome claim, in PSM conversations.

---

## 2. The regulatory + policy state of play (May 2026)

### Federal — two executive orders, one in active turmoil

**April 23, 2025 — "Advancing Artificial Intelligence Education for American Youth"**
- Directed Sec. of Education to prioritize AI in grant programs + issue guidance within 90 days
- US DOE confirmed AI uses are allowable under existing federal programs subject to FERPA / IDEA / Title programs
- **Status:** in effect, broadly uncontested
- Source: [whitehouse.gov](https://www.whitehouse.gov/presidential-actions/2025/04/advancing-artificial-intelligence-education-for-american-youth/) + [ed.gov](https://www.ed.gov/about/news/press-release/us-department-of-education-issues-guidance-artificial-intelligence-use-schools-proposes-additional-supplemental-priority)

**December 11, 2025 — "Eliminating State Law Obstruction of National AI Policy"**
- Aims to preempt state AI laws via (a) DOJ AI Litigation Task Force challenging state laws on Commerce-Clause / preemption grounds, (b) discretionary federal grant conditioning on states not enforcing conflicting laws, (c) administrative reinterpretation
- **Status as of May 2026:** in effect but actively contested — state AGs (notably California) have signaled litigation; no resolution yet
- Source: [whitehouse.gov](https://www.whitehouse.gov/presidential-actions/2025/12/eliminating-state-law-obstruction-of-national-artificial-intelligence-policy/) + legal analysis from [Alston & Bird](https://www.alston.com/en/insights/publications/2025/12/trump-executive-order-state-ai-regulation) + [DLA Piper](https://www.dlapiper.com/en-us/insights/publications/2025/12/new-executive-order-aims-to-preempt-state-ai-regulation)

**PSM defensible posture:** comply with the strictest applicable state law until at least 12 months after a definitive court ruling on preemption. Telling a district CIO "the federal EO preempts your state law" is a way to lose a renewal.

### COPPA amendments — full enforcement April 22, 2026

Material changes for EdTech AI vendors:

1. **Separate opt-in parental consent required** to share / use under-13 personal info with advertisers OR for AI training. The FTC explicitly states **AI training is "not integral" to a service** so it cannot be bundled with general consent.
2. **Biometric data added to personal info:** fingerprints, faceprints, voiceprints, DNA.
3. **Indefinite retention banned.**
4. **Penalties up to $51,744 per violation per day.**

Source: [Federal Register, April 22, 2025](https://www.federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule) + [Akin Gump COPPA + AI tracker](https://www.akingump.com/en/insights/ai-law-and-regulation-tracker/new-coppa-obligations-for-ai-technologies-collecting-data-from-children).

### FERPA + AI vendors — school-official exception, with higher diligence

For an AI vendor to operate under the school-official exception, the district must:
- (a) be performing a function the school employee would otherwise do
- (b) demonstrate direct control via contract
- (c) limit further sharing
- (d) tie data use to a legitimate educational interest

The Department of Education in 2025 reinforced these requirements + added a state-agency FERPA compliance certification requirement (deadline April 30, 2025). Source: [NEA federal AI policy overview](https://www.nea.org/sites/default/files/2025-06/5.1-ai-policy-overview-of-federal-regulations-final.pdf).

### State-level K-12 AI guidance — ~33-35 states + PR by April 2026

Most are **non-binding guidance documents**; legislated AI-in-schools mandates are a smaller subset. Counts vary by source (Ballotpedia vs CDT/SPC vs Stateline) — confidence is **High** on "majority of states have guidance"; **Low** on any specific count without naming the snapshot date.

Source: [Ballotpedia state AI guidance tracker](https://ballotpedia.org/AI_guidance_issued_by_state_departments_of_education) + [Stateline majority finding](https://stateline.org/2025/07/15/more-than-half-the-states-have-issued-ai-guidance-for-schools/).

### State student-privacy laws + AI-specific provisions

- **California AB 1159** — moving to ban student information from being used for commercial AI training
- **Indiana, Kentucky, Rhode Island** — added universal opt-out mechanisms + neural-data protections (secondary source; verify statute text before relying on)
- **NY Ed Law §2-d, IL SOPPA, CA SOPIPA** — existing laws continue to apply; data-protection riders need re-attachment at renewal (see [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md))

---

## 3. Teacher / parent / student perception (the verified survey data)

### Teacher adoption — the big jump in 2025

- **EdWeek Research Center: 61% of teachers said they used AI in some capacity in 2025**, up from 34% (2023) and 32% (2024)
- **RAND American Teacher Panel (n=2,232, weighted nationally representative, March-April 2025): 53% of ELA / math / science teachers used AI in 2025.** Instructional-planning use jumped from 25% (2024) to 53% (2025).
- **Pre-K teachers lag:** RAND n=1,586 — only **29% used GenAI in 2024-25**
- **Teacher PD on AI:** ~50% reported at least one PD session in 2025 (up from 29% early 2024)

Sources: [EdWeek](https://www.edweek.org/technology/more-teachers-are-using-ai-in-their-classrooms-heres-why/2026/01) + [RAND main report](https://www.rand.org/pubs/research_reports/RRA4180-1.html) + [RAND pre-K commentary](https://www.rand.org/pubs/commentary/2025/12/pre-k-teachers-are-hesitant-to-use-artificial-intelligence-why.html)

### Parent + teen split — the academic-integrity divide

Common Sense Media "Dawn of the AI Era" (n=1,045 parent/teen pairs, fielded March-May 2024):
- **52% of parents** call AI for schoolwork **"unethical"**
- **52% of teens** say it should be **encouraged**
- **84% of parents** worry about AI misusing kids' data (**76% of teens agree**)

Pew Research (Sept 25 - Oct 9, 2025): **54% of teens used chatbots for schoolwork**, 57% for information search. **Acceptability varies sharply by task:** 54% say research is acceptable, **29% for math, only 18% for essays.**

Sources: [Common Sense Media](https://www.commonsensemedia.org/research/the-dawn-of-the-ai-era-teens-parents-and-the-adoption-of-generative-ai-at-home-and-school) + [Pew December 2025](https://www.pewresearch.org/internet/2025/12/09/teens-social-media-and-ai-chatbots-2025/)

### AI-detection reliability — the equity finding that matters

| Tool | Accuracy on AI text | False-positive on human text |
|---|---|---|
| GPTZero | ~92.4% (vendor claim) | 0.24% vendor / 1-2% independent |
| Turnitin | 84-95% | 5-7% on native English / **up to ~50% on ESL writing** |
| Humanizer tools (Quillbot, Undetectable.ai) | reduce detection to ~55-65% | n/a |

**The ESL false-positive rate is the single hardest equity data point in the AI-in-EdTech conversation.** Detection alone is not defensible evidence in an honor-code case; the consensus emerging in higher-ed AI syllabus policy is **"detection is *signal*, not *evidence*" — integrity charges require process-level evidence** (drafts, edit history, in-class writing samples).

Sources: [Hastewire benchmark](https://hastewire.com/blog/gptzero-vs-turnitin-vs-originalityai-test-results-accuracy-breakdown) + [EyeSift 2026 benchmark](https://www.eyesift.com/blog/ai-detector-accuracy-benchmarks-2026/)

---

## 4. Implementation realities — what worked, what failed

### LAUSD / AllHere — the cautionary tale

- **5-year contract ~$6M signed 2024**
- Chatbot **pulled within months** after AllHere furloughed staff
- CEO Joanna Smith-Griffin later **charged with securities fraud, wire fraud, aggravated identity theft**
- A company official allegedly flagged student-data exposure risks before the rollout

**The takeaway among large-district CIOs is now:** *"AI procurement requires vendor financial diligence, not just feature diligence."* Sub-processor lists, SOC 2 reports, financial-health attestations, and pilot-before-scale are now table stakes — a posture-change that affects every renewal conversation through 2027+.

Sources: [EdWeek](https://www.edweek.org/technology/los-angeles-unifieds-ai-meltdown-5-ways-districts-can-avoid-the-same-mistakes/2024/07) + [EdSource](https://edsource.org/2024/communities-demand-transparency-after-ed-lausds-ai-chatbot-fails/717772)

### NH Khanmigo statewide — the success pattern

- $2.3M federal COVID-relief funded, 50 districts, ~5,000 educators, ~40,000 students
- **Extended at no additional cost through 2025-26**
- **Caveat: outcome data (test-score impact) not yet published** — the rollout exists; whether it works pedagogically is unverified

Source: [NH Department of Education](https://www.education.nh.gov/news-and-media/khan-academy-extend-its-ai-services-no-cost-new-hampshire-educators-and-students)

### Mississippi state-led pilot — December 2025

- 15-district teacher-AI pilot using **Gemini + NotebookLM**
- State has invested >$37M (grants, RESTORE Act, Microsoft / C Spire / AWS / NVIDIA partnerships)
- **Deliberately teacher-facing, not student-facing**

Source: [Magnolia Tribune](https://magnoliatribune.com/2025/12/23/mississippi-dept-of-education-launches-ai-pilot-program-in-15-school-districts/)

### Houston ISD "Future 2" — pre-announced, not yet launched

- Nine AI-focused campuses planned for 2026-27
- Expanding to 25 → 100 by 2031
- **No failure case yet — the program hasn't started**

Source: [Houston Public Media](https://www.houstonpublicmedia.org/articles/education/2026/04/29/550493/houston-isd-future-2-schools-ai-focus/)

### Total cost — the honest framing

- **No clean per-student AI-spend benchmark** exists in the public record as of mid-2026
- Best anchor: CoSN 2024 IT Leadership Survey — total district ed-tech spending **~$621/student/year**, and **AI is currently being funded from inside that envelope** rather than as an additive budget line

This means: when a partner asks "what should we budget for AI?", the honest answer is "AI is replacing things in your existing $621/student stack, not adding to it — unless you're piloting at significant scale, in which case talk to CoSN."

---

## 5. Accuracy, hallucination, and bias

- **Subject-matter accuracy varies sharply by domain.** A 2025 nationally representative survey found math/science teachers split on GenAI's impact: 34% negative, 36% no effect, 30% positive. Hallucination is empirically worse with general web access vs. a constrained domain index.
- **Curricular alignment to state standards is uneven.** Vendor-purpose-built tools (MagicSchool, Curipod, Khanmigo) advertise standards alignment but **independent third-party verification of alignment accuracy is rare.** No "EdReports for AI tools" authority exists yet.
- **Bias and equity:** AI inherits training-data biases. EdTrust frames it as "promise and peril" — disproportionately likely to help with personalization, also disproportionately likely to misjudge non-standard English as low-quality. The **up to ~50% false-positive rate on ESL writing in AI-detection tools** is the canonical equity data point.

Sources: [arXiv K-12 GenAI patterns](https://arxiv.org/abs/2509.10747) + [EdTrust](https://edtrust.org/blog/navigating-the-promise-and-peril-of-ai-for-students-of-color/) + [NEA on AI bias](https://www.nea.org/nea-today/all-news-articles/does-ai-have-bias-problem)

---

## 6. PSM implications (the practical synthesis)

These follow from the findings above; treat as practitioner synthesis, not primary research.

### Competitor AI features are now a renewal-conversation topic in 2026

Partners are expecting their existing EdTech vendor to either (a) ship AI features integrated into the workflow they already use, or (b) explain why not. **The PSM needs a prepared "What's your AI strategy?" 1-pager** keyed to:
- What's shipped (with screenshots / demo)
- What's on the roadmap with dates
- What data the AI does and does not touch (the FERPA / COPPA-aware version)

### The FERPA/COPPA conversation must be vendor-led, not partner-led

District CIOs in 2026 are operating under amended-COPPA full enforcement (April 22, 2026), the post-LAUSD trauma, and the unsettled state-AG fight over the federal EO. **The PSM walks in with:**
1. The vendor's data-flow diagram for the AI feature
2. Whether under-13 data is used for any model training (with the answer being "no, unless we have separate opt-in consent")
3. Sub-processor list
4. FERPA "direct control" contract language
5. Data-deletion SLAs

### Pilot patterns that work in 2026

- **Teacher-facing first, student-facing second** (Mississippi's choice)
- **Small district sample, measure outcomes, publish results before expansion** (the inverse of LAUSD)
- **Limit AI to a constrained domain** (reduces hallucinations)
- **District-administered SSO + per-teacher visibility** (procurement table stakes)

### Partner-profile-curator additions (per partner)

What the durable partner record should capture about a partner's AI posture:

- **Stated AI policy** at district / institution level — exists? written? aligns with state guidance?
- **Incumbent AI vendors** already in use (incumbent-threat / partner-of-partner mapping)
- **Stance on student-facing vs. teacher-facing AI**
- **Procurement triggers** — does AI require board approval? superintendent? CIO?
- **Privacy posture** — which state laws apply, any DPA addenda the partner requires
- **History of vendor-failure exposure** — did this district get burned by AllHere / Ed?
- **Pilot capacity** — does the partner have a dedicated pilot framework, or treat every new vendor as production-day-one?

See [`../agents/partner-profile-curator.md`](../agents/partner-profile-curator.md) — the AI-posture additions belong in §"Surface area" alongside the existing jurisdiction line.

### "Detection is signal, not evidence" — the academic-integrity boundary

When a partner asks about academic-integrity tooling (Turnitin AI detector, GPTZero, Originality.ai), the PSM should know:
- ESL students may face ~50% false-positive rates in detection
- Detection alone has been ruled non-defensible in academic-integrity charges in multiple higher-ed contexts
- The consensus 2026 framing is "detection + process evidence" (drafts, edit history, in-class samples), not detection alone

Recommend partners use detection as one signal in a broader rubric, not the deciding evidence.

---

## 7. Refresh triggers for this document

- New major federal AI executive order or state preemption-EO court ruling
- COPPA enforcement action surfaces a pattern (FTC actions, settlements)
- CA AB 1159 (or successor) bans student data for commercial AI training
- A marquee deployment publishes outcome data (NH Khanmigo test scores, MS pilot results, Newark)
- Any vendor in §1 makes a material pricing change (verify Khanmigo + MagicSchool prices quarterly)
- A new tier-1 vendor enters the EdTech AI space
- Houston ISD "Future 2" launches and produces public outcome data

## 8. References

- Production-lesson knowledge file: [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md) — the broader FERPA/COPPA/state-law framing
- Foundation file: [`customer-success-frameworks.md`](customer-success-frameworks.md) — the methodology lens
- Companion v0.4.0 file: [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md) — where the AI conversation lands at renewal time
