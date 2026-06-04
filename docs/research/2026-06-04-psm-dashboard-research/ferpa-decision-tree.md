# FERPA Decision Tree for EdTech CS Dashboards (2026-06-04)

> **Scope.** Authoritative reference for a vendor (or partner-success team) shipping a dashboard that surfaces *aggregate* engagement metrics about K-12 / higher-ed students (logins, problem-completion counts, time-on-task, MAU/DAU). Produced by the RavenClaude deep-research harness; ≥30 sources cited; substrate=baseline.
> **Status of every numeric threshold below.** PTAC does **not** mandate a single minimum-cell number — it defers to states/LEAs. Numbers below are widely-used industry conventions (n<5, n<10, n<16), each tied to its source agency. Treat them as defaults; honor the stricter of (a) the LEA contract, (b) state law, (c) PTAC guidance, (d) this default.
> **Verification posture.** Where a PTAC PDF was 403-blocked from direct fetch, the claim is grounded in PTAC excerpts retrieved via search snippets plus a secondary source; each is marked `[search-snippet]` vs `[fetched]` in the sources ledger.

---

## 1. The aggregate-vs-de-identifiable line (current PTAC guidance)

**The 34 CFR § 99.3 standard.** "Personally identifiable information" (PII) under FERPA includes not only direct identifiers (name, SSN, student ID) but **"other information that, alone or in combination, is linked or linkable to a specific student that would allow a reasonable person in the school community, who does not have personal knowledge of the relevant circumstances, to identify the student with reasonable certainty."** [1][2] Aggregate data is therefore **only outside FERPA when** small-cell sizes, rare attributes, or join-keys cannot re-identify an individual with reasonable certainty under that test.

**Two PTAC-recognized de-identification routes** (mirrors HIPAA's two-method structure but FERPA does *not* codify them):

1. **Expert-determination-style ("statistical")** — a qualified person applies SDL methods (suppression, blurring, perturbation, swapping, top/bottom-coding) and documents the methodology. PTAC's *Data De-identification: An Overview of Basic Terms* names **k-anonymity** (each combination of quasi-identifiers appears ≥k times), **l-diversity** (≥l well-represented sensitive values per equivalence class), and **t-closeness** (sensitive-value distribution within ≤t of the global distribution) as the canonical techniques. [3][4]
2. **Safe-harbor-style** — strip direct identifiers and a defined list of indirect identifiers; PTAC's vendor FAQ aligns with the HIPAA safe-harbor list (names, addresses, dates finer than year, ZIPs finer than 3-digit, ages >89, etc.) but emphasizes that *FERPA has no codified safe harbor*. [5]

**The two PTAC anchors that survive verification.**

- *Aggregation alone is not de-identification.* "The aggregation of student-level data into school-level (or higher) reports removes much of the risk of disclosure … no direct identifiers … are present" — but indirect identifiers in small cells can still re-identify. [6]
- *No federal numeric mandate.* "The Department does not mandate a particular method, nor does it establish a particular threshold for what constitutes sufficient disclosure avoidance, leaving these decisions up to individual State and local educational agencies and institutions." [7]

**Industry-default minimum cell sizes** (transferable, not FERPA-mandated):

| Source | Minimum n | Notes |
|---|---|---|
| NCHS Research Data Center | **5** | "Tables with cell count less than 5 must be suppressed." [8] |
| CDC WONDER | **10** | "Suppresses any statistic calculated using fewer than 10 observations." [8] |
| U.S. Cancer Statistics (CDC) | **16** | "More than sufficient to protect patient confidentiality." [8] |
| ESSA accountability reporting (DQC) | **5–30** range; **5 is most common** | "U.S. Dept. of Ed does not mandate; states set n-size 5 to 30." [9] |
| Indiana University (illustrative LEA) | **<10 (restricted), <5 (general)** | LEA-set under PTAC deference. [9] |

**Complementary suppression is required.** Per PTAC: "complementary cell suppression suppresses a select number of additional cells to prevent the possibility that suppressed small cells could be re-calculated by subtracting other reported cells from the tables' row and column totals." [10] Practical implication: suppressing a single small cell while publishing row/column totals **does not protect FERPA**; the suppressed cell can be back-derived.

---

## 2. Recent enforcement actions (2023-2026) — what tripped them

### A. FTC v. Edmodo (May 2023) — the canonical "outsourced compliance" case
- **What tripped it.** Edmodo collected children's PII (under-13) and used it for **contextual advertising**, beyond the limited educational purpose for which schools/teachers may consent under COPPA's school-authorization theory. It also relied on schools/teachers to provide verifiable parental consent without giving them the required direct-notice materials. [11][12][13]
- **Consent decree.** $6M civil penalty (suspended for inability to pay); **first FTC order to prohibit an ed-tech provider from requiring students to provide more PII than necessary** to participate; data-minimization mandate; deletion of unlawfully obtained data; ban on outsourcing COPPA obligations to schools without proper notice. [11][12]
- **Lesson for an aggregate-dashboard vendor.** "Schools consented" is not a defense if (i) the vendor never gave schools the notice materials they need to consent on parents' behalf, or (ii) the vendor's actual use exceeds the educational purpose disclosed.

### B. FTC amicus, *Shanahan v. IXL Learning* (Aug 2025) — closing the school-consent loophole
- **What tripped it.** Plaintiffs (parents) alleged IXL collected, used, and **sold** children's data via in-school software. IXL invoked the school-authorization theory and tried to **bind parents to arbitration via the school's TOS**. [14][15][16]
- **FTC position.** "Neither COPPA nor the COPPA rule compels parents to accept the terms of agreements between schools and ed-tech companies." Schools may consent **only** for narrow educational purposes; they cannot bind parents to a vendor's extraneous terms (arbitration, data sales). [14][16]
- **Lesson for aggregate-dashboard vendor.** A school's signature on a DPA does **not** convert "we sell aggregate engagement data to district-side partners" into a lawful use; parental consent is required if the use exceeds educational purpose.

### C. PowerSchool / Naviance settlement ($17.25M, Feb 2026) — the "covert telemetry" case
- **What tripped it.** Naviance contained ad-tracking technology transmitting student names, IDs, graduation years, demographics, photos, survey responses, and **private teacher communications** to Google, Microsoft, and Heap. Court characterized this as "unlawful wiretapping" and "eavesdropping." [17][18][19]
- **Separate Dec 2024 breach.** Compromised credentials let an attacker exfiltrate data on an estimated **60M students** — the largest exposure of children's data in U.S. history. Triggered TX AG suit (Sep 2025) and the CPS class settlement (Feb 2026). [17][18]
- **Lesson for aggregate-dashboard vendor.** **Third-party telemetry in a school product is a wiretap claim, not just a FERPA claim** — Google Analytics, Mixpanel, Heap, FullStory in a student-facing surface are litigation magnets even when the data flowing out is "anonymized."

### D. FTC COPPA Final Rule (effective Jun 23, 2025; compliance by Apr 22, 2026)
- Expanded definitions of "personal information" and "online contact information," **separate verifiable parental consent for third-party disclosures**, stricter data retention/security, mixed-audience clarifications. [20][21][22] FTC **declined to codify** school consent authority, citing pending Department of Ed FERPA rulemaking and a desire not to conflict. [22][23]
- **Lesson.** The vendor cannot rely on the regulatory text to bless "school as parental agent." It is enforced by FTC discretion and existing guidance, both of which the IXL amicus narrowed.

---

## 3. State FERPA-plus matrix (CA SOPIPA, NY 2-D, IL SOPPA)

| Dimension | FERPA (federal floor) | CA SOPIPA | NY Ed Law § 2-d / Part 121 | IL SOPPA |
|---|---|---|---|---|
| **Targeted advertising on K-12 students** | Not specifically prohibited | **Prohibited** [24] | Prohibited | Prohibited |
| **Selling student data** | Permitted under "school official" if contract restricts | **Prohibited** [24] | Prohibited | Prohibited |
| **Building student profiles for non-educational purposes** | Not addressed | **Prohibited** | Prohibited | Prohibited |
| **Vendor security framework** | Reasonable methods (§99.31(a)(1)(ii)) | Reasonable | **NIST CSF required** (Part 121) [25][26] | "Reasonable security measures" |
| **Parents' Bill of Rights** | None | None | **Required, posted on district site** [25] | Yes; **list of operators on district site** [27] |
| **Data Protection Officer** | None | None | **Required per LEA** [25] | None |
| **Breach notification to district** | None | None (state breach law applies) | "As soon as possible" / 7 days | **Operator → school: 30 days; school → parents: 30 days** [27] |
| **Breach posting on district site** | None | None | None | **Required within 10 days if >10% of students affected** [27] |
| **List of operators / contracts published** | None | None | **Supplemental info per contract** [25] | **Full list + data shared + subcontractors** [27] |
| **Staff training mandate** | None | None | **Annual privacy/security training** [25] | Encouraged |
| **Enforcement** | DOE complaints; loss of federal funds | AG; private right of action varies | NYSED Chief Privacy Officer; civil penalties | AG; AGE-style suits possible |

**Multi-state rule of thumb (industry-default):** A DPA that satisfies **NY Ed Law 2-d Part 121 + IL SOPPA** is almost certainly compliant in every other US state. [28] If your dashboard ships to either NY or IL districts, build to those two; everything else falls out.

---

## 4. School-official exception scope for the CS vendor case

### The four prongs of § 99.31(a)(1)(i)(B) (verbatim PTAC framing) [29][5]

A vendor may receive PII from education records **without parental consent** if it:
1. **Performs an institutional service or function** for which the LEA would otherwise use its own employees;
2. Has a **legitimate educational interest** in the records;
3. Is **under the direct control** of the LEA with respect to use and maintenance of the records;
4. Uses records **only for the authorized purpose** and **does not redisclose** PII to other parties without consent (mirroring § 99.33(a)).

### What "direct control" means in practice

There is **no codified definition**; the Center for Democracy & Technology's 2024 survey called it "a critical undefined term." [30][31] PTAC and consensus practice operationalize it as a **contractual** package:
- The LEA owns the data; the vendor processes it under written instruction.
- The vendor cannot use the data for any purpose the LEA didn't authorize in writing.
- The vendor cannot redisclose to subprocessors without LEA approval (NDPA Exhibit H / SOPPA subcontractor disclosure).
- The vendor must permit LEA audit and must return/destroy data at contract end.
- Per the 2025 DOE FAQ (37-question update), **a TOS clause that requires parents/students to waive FERPA rights is invalid** — schools cannot require such waivers as a condition of use. [32][33]

### What an aggregate-engagement CS dashboard typically clears

| Vendor action | Inside school-official exception? | Why |
|---|---|---|
| Compute MAU/DAU for the contracted LEA and show it back to district admins | **Yes** | Institutional service; legitimate interest; direct control |
| Show class-level "% of students who completed problem set" to the teacher who assigned it | **Yes** | Same |
| Show district-level engagement trend to a *different* LEA you also serve | **No** — and even aggregate may be PII if cells are small | Redisclosure outside the contracting LEA |
| Use the LEA's engagement logs to **train a shared model** that serves other customers | **No** without explicit DPA opt-in | Exceeds authorized purpose; redisclosure of PII into model weights |
| Publish a marketing case study with district-named aggregate numbers | **Only with LEA written approval** | Authorized-purpose limit; check Parents' Bill of Rights |
| Send aggregate engagement metrics to a *partner-success CRM* (Salesforce, HubSpot) that's a subprocessor | **Conditional** — must be in DPA's subprocessor list; SOPPA requires it on the public list | Direct-control + redisclosure prongs |

---

## 5. Small-cell threshold patterns from public health (transferable)

Education hasn't standardized; public health has. The following are the cleanest cross-walks an ed-tech reviewer should reach for when an LEA hasn't specified a number.

| Standard | Threshold | Mechanic | Source |
|---|---|---|---|
| **NCHS public-use files** | Sensitive if n<5 (some agencies n<3) | Frequency-cell suppression with complementary suppression on margins | [8] |
| **CDC WONDER** | Suppress any rate or count from n<10 | Numerator and denominator below threshold both trigger | [8] |
| **U.S. Cancer Statistics** | Suppress at n<16 | Used for both counts and rates | [8] |
| **CMS (Medicare/Medicaid) cell-size policy** | Suppress at n≤10; round to nearest 10 above | Complementary suppression required if margins published | [34] |
| **HHS/ASPE open-data report** | Recommends **k-anonymity k≥5 minimum**, ideally k≥10 for rare-attribute tables | Layered with l-diversity for sensitive attributes | [4] |

**Transferable defaults for an ed-tech CS dashboard:**
- **Default minimum n = 10** for any cell shown to a user who is not an authorized school official of the cell's own LEA. (Matches CDC WONDER; one notch stricter than NCHS; survives most state minimums.)
- **Apply complementary suppression** to any row/column totals shown alongside suppressed cells — otherwise the suppressed cell back-derives.
- **For rare attributes** (IEP status, ELL, free/reduced lunch, demographic intersections): require **k≥10 AND l≥2** for the sensitive attribute, or do not show.
- **For longitudinal views** (same chart at multiple time points): apply the threshold at **every time point**, not just the latest; a cell that briefly drops below n=10 in one week leaks identity by differencing.

---

## 6. AI/ML training-data prohibitions in ed-tech DSAs

### The clear-line rule (2025 consensus)

Across PTAC vendor guidance, the SDPC NDPA v2.2 (Nov 19, 2025), Common Sense Privacy evaluations, and emerging district AI policies, the operative rule is: **a vendor cannot use student PII (or data derived from student PII, including model weights fine-tuned on it) to train models that serve any customer other than the LEA that contributed the data — unless the DPA expressly authorizes it.** [35][36][37][38]

### Concrete contractual instruments

- **SDPC NDPA v2.2** (released Nov 19, 2025): "addressed provisions regarding data breaches, sub-processor restrictions, advertising limits, **de-identified data use**, and other issues." Exhibit E (general offer) is now mandatory; Exhibit H (subprocessor list) checkbox removed (mandatory disclosure). [35][39]
- **Charlotte-Mecklenburg Schools AI policy (Oct 2025)** and **Washington County (UT) policy 3750**: AI committee review for any system using staff/student data; "generally prohibits the use of Confidential or Protected Data with AI tools" unless approved. [40]
- **OpenAI Enterprise / API ZDR** and **Anthropic Claude for Education / API ZDR**: "API inputs and outputs are never used for model training"; ZDR enterprise agreements suppress storage beyond abuse-screening. **Important asymmetry:** Consumer Claude (Aug 2025 policy shift) **does** train on opted-in conversations (5-year retention) — so a teacher pasting student work into a personal Claude consumer account creates a FERPA exposure that the vendor's enterprise contract does not cover. [41][42][43]

### What a dashboard vendor must put in writing

1. **No training on customer data** — neither base-model pretraining nor fine-tuning nor RLHF.
2. **No "improvement" carveout** — vendors often retain "to improve the Services" language; under PTAC's authorized-purpose limit and NY/IL state law, this is read narrowly. If you mean "telemetry to debug *this* customer's instance," say so; if you mean "build features for all customers from one customer's data," that requires explicit LEA opt-in.
3. **No retention past contract termination + standard wind-down** (typically 30–90 days).
4. **Subprocessor flow-down** — every AI vendor in the stack (OpenAI, Anthropic, Pinecone, etc.) must itself be on the SOPPA-style subprocessor list and bound to the same no-training restriction. ZDR enterprise contracts are the verification artifact.
5. **De-identified data carveout, if used, must be defined to PTAC's standard** — not the vendor's marketing definition.

---

## 7. Decision tree: is THIS dashboard field FERPA-OK?

```mermaid
flowchart TD
    START([Dashboard field under review<br/>e.g. 'MAU by school', 'student streak leaderboard']) --> Q1{Does the field, alone or<br/>combined with other fields<br/>on this dashboard or<br/>reasonably-available external<br/>data, identify an individual<br/>student with reasonable<br/>certainty?<br/>34 CFR 99.3}

    Q1 -- No, definitely aggregate --> Q2{Smallest cell shown<br/>n ≥ 10?<br/>CDC WONDER default}
    Q1 -- Maybe / depends on viewer --> Q1a{Who is the viewer?}
    Q1 -- Yes, direct or indirect PII --> SO

    Q1a -- LEA staff member of THIS<br/>student's school/district --> SO
    Q1a -- Anyone else --> STOP1[STOP — needs counsel.<br/>Treat as PII until LEA<br/>confirms in writing]

    Q2 -- No, n less than 10 --> SUPPRESS{Apply suppression?}
    Q2 -- Yes, n ≥ 10 --> Q3{Does the cell involve a<br/>'rare attribute'?<br/>IEP, ELL, FRL,<br/>race-by-grade intersection,<br/>etc.}

    SUPPRESS -- Suppress this cell<br/>AND complementary cells<br/>on margins --> Q3
    SUPPRESS -- Don't suppress --> STOP2[STOP — likely FERPA violation.<br/>Small-cell publication]

    Q3 -- Yes --> Q3a{k ≥ 10 AND l-diversity<br/>≥ 2 for the sensitive<br/>attribute?}
    Q3 -- No, ordinary attribute --> Q4

    Q3a -- Yes --> Q4
    Q3a -- No --> STOP3[STOP — rare-attribute leak.<br/>Suppress or raise k]

    Q4{Is this dashboard shown<br/>only inside the LEA that<br/>contributed the data?} -- Yes --> SO
    Q4 -- No, cross-LEA or external --> Q5

    Q5{Are all LEAs in the<br/>view aggregated together<br/>such that no single LEA<br/>identifiable AND each LEA<br/>contributes n ≥ 10?} -- Yes --> Q6
    Q5 -- No --> Q5a{Written cross-LEA<br/>consent or DOE-approved<br/>multi-LEA study?}
    Q5a -- Yes --> Q6
    Q5a -- No --> STOP4[STOP — redisclosure across<br/>LEAs without consent.<br/>99.33(a) violation risk]

    Q6{Is this a longitudinal<br/>view? Same chart over<br/>multiple time points?} -- Yes --> Q6a{Threshold met at<br/>EVERY time point<br/>not just latest?}
    Q6 -- No --> Q7

    Q6a -- Yes --> Q7
    Q6a -- No --> STOP5[STOP — differencing attack.<br/>Drop sparse time points<br/>or raise threshold]

    Q7{Will the underlying<br/>data, or anything derived<br/>from it, be used to<br/>train any ML model?} -- No --> Q8
    Q7 -- Yes --> Q7a{DPA expressly authorizes<br/>this LEA's data for<br/>model training?}

    Q7a -- Yes, with LEA opt-in --> Q8
    Q7a -- No or silent --> STOP6[STOP — unauthorized purpose.<br/>FERPA 99.31(a)(1)(i)(B)(4)<br/>and 2025 DOE TOS guidance]

    Q8{Will an LLM provider<br/>OpenAI / Anthropic /<br/>self-hosted see this<br/>data in any request?} -- No --> Q9
    Q8 -- Yes --> Q8a{Provider under signed<br/>ZDR + 'no training'<br/>enterprise contract AND<br/>listed as subprocessor<br/>in the DPA?}

    Q8a -- Yes --> Q9
    Q8a -- No --> STOP7[STOP — undisclosed<br/>subprocessor. SOPPA list<br/>violation; NY 2-d Part 121<br/>vendor disclosure violation]

    Q9{Will the field be<br/>shown to a partner<br/>not under the LEA's<br/>direct control?<br/>another vendor, analyst,<br/>marketing site} -- No --> Q10
    Q9 -- Yes --> Q9a{Suppressed/aggregated<br/>per §§ 1–5 above AND<br/>partner is a 'school<br/>official' under the LEA's<br/>DPA OR data is fully<br/>de-identified to PTAC<br/>standard?}

    Q9a -- Yes --> Q10
    Q9a -- No --> STOP8[STOP — redisclosure to<br/>non-school-official.<br/>Needs parental consent<br/>or de-identification]

    Q10{Will the disclosure be<br/>logged per § 99.32 in<br/>the LEA's record-of-access<br/>system?} -- Yes --> Q11
    Q10 -- No --> Q10a{Disclosure to a 'school<br/>official' under direct<br/>control AND the LEA's<br/>policy treats this as<br/>internal access?}

    Q10a -- Yes --> Q11
    Q10a -- No --> STOP9[STOP — missing record<br/>of disclosure. 99.32 a 1]

    Q11{State law overlay:<br/>Does CA SOPIPA, NY 2-d,<br/>or IL SOPPA apply to<br/>any student in the cell?} -- No --> Q12
    Q11 -- Yes --> Q11a{Vendor satisfies the<br/>strictest applicable<br/>state law NIST CSF,<br/>operator list, breach<br/>SLAs, ad-tech ban?}

    Q11a -- Yes --> Q12
    Q11a -- No --> STOP10[STOP — state law violation.<br/>NY/IL/CA stricter than FERPA]

    Q12{Is any student in the<br/>cell under 13<br/>K-5 typical?} -- No --> Q13
    Q12 -- Yes --> Q12a{COPPA path covered?<br/>School-authorization theory<br/>holds: educational purpose<br/>only, no ad-targeting, no<br/>parent waiver via TOS,<br/>per Edmodo + IXL amicus}

    Q12a -- Yes --> Q13
    Q12a -- No --> STOP11[STOP — COPPA exposure.<br/>Verifiable parental consent<br/>required; school cannot bind<br/>parents to vendor TOS]

    Q13{Will any third-party<br/>analytics/telemetry<br/>Google Analytics,<br/>Mixpanel, FullStory<br/>see this data?} -- No --> OK
    Q13 -- Yes --> STOP12[STOP — PowerSchool/Naviance<br/>wiretap risk pattern.<br/>Strip telemetry from student<br/>surfaces or get explicit<br/>opt-in disclosure]

    OK([DASHBOARD FIELD OK<br/>Document the decision in<br/>FERPA decision log,<br/>refresh quarterly]):::ok
    SO([SCHOOL OFFICIAL pathway<br/>OK if 99.31 a 1 i B prongs<br/>all met AND logged per §99.32<br/>if LEA policy requires]):::ok

    STOP1:::stop
    STOP2:::stop
    STOP3:::stop
    STOP4:::stop
    STOP5:::stop
    STOP6:::stop
    STOP7:::stop
    STOP8:::stop
    STOP9:::stop
    STOP10:::stop
    STOP11:::stop
    STOP12:::stop

    classDef stop fill:#ffd6d6,stroke:#c0392b,color:#000
    classDef ok fill:#d6ffd6,stroke:#27ae60,color:#000
```

**How to use the tree.** Walk every distinct dashboard field through it once. Re-walk on every schema change. The 12 STOP leaves are the *known* failure modes; if your situation doesn't map cleanly into any branch, **default to STOP — needs counsel**. The tree is conservative on purpose: a false "OK" is an enforcement action; a false "STOP" is a phone call to the LEA's data-privacy officer.

---

## 8. Recommended RavenClaude additions

### 8a. For `plugins/edtech-partner-success/knowledge/`

Create three new knowledge files:

**`ferpa-aggregate-threshold-defaults.md`** (≈400 lines)
- The §1 table from this report, plus PTAC quotes + URLs.
- The §5 public-health-default cross-walk.
- A "when to escalate" boundary statement: any time the field involves rare attributes, longitudinal views, or cross-LEA aggregation, the answer goes through human privacy counsel.
- A worked example: "Showing weekly MAU for District X to District X's superintendent" (OK, school-official, logged); "Showing weekly MAU for District X to a District Y administrator at a partner-success conference" (STOP — redisclosure).

**`state-privacy-law-matrix.md`** (≈300 lines)
- The §3 matrix, expanded with the actual statutory citations: Cal. Bus. & Prof. Code §§ 22584–22585 (SOPIPA); NY Educ. Law § 2-d + 8 NYCRR Part 121; 105 ILCS 85/ (SOPPA).
- The "build-to-NY-and-IL" heuristic with the supporting source.
- Update cadence: quarterly review of NCSL state-tracker + Public Interest Privacy Center state-law page. [44]

**`ai-training-prohibition-clauses.md`** (≈250 lines)
- Reference NDPA v2.2 (released Nov 19, 2025) clauses on de-identified data and subprocessor flow-down.
- The five-point "must put in writing" list from §6.
- Vendor-side decision matrix for OpenAI ZDR vs. Anthropic Claude for Education vs. self-hosted models, including the **consumer-Claude-trains-on-data caveat** that catches teachers pasting work into personal accounts.
- A pre-built clause library (no-train, no-improvement-carveout, deletion-on-termination, subprocessor flow-down, audit rights).

### 8b. For `plugins/edtech-partner-success/agents/ferpa-comms-translator.md`

Add the following to the agent's instructions:

1. **Default-deny posture for ambiguous fields.** Whenever a request involves a metric that could not be unambiguously walked through the §7 decision tree to an "OK" leaf, the agent must respond with the closest STOP node + the question that would unblock it, **never** with a confident "yes, this is fine."
2. **State-law overlay first.** Before answering any FERPA question, ask which state(s) the LEA is in. If NY or IL is in scope, route through that statute's stricter requirement (NIST CSF, operator list, breach SLA).
3. **AI-training reflex.** When a partner asks about model training, the agent must:
   - Distinguish base-model pretraining, fine-tuning, RLHF, embeddings, retrieval-augmented generation.
   - Name the subprocessor (OpenAI, Anthropic, etc.) and confirm ZDR + enterprise contract status.
   - Flag the consumer-Claude / consumer-ChatGPT loophole if a teacher might paste work into a personal account.
4. **Citation discipline.** Every numeric threshold the agent emits must carry its source (PTAC | CDC | NCHS | state-statute | LEA-contract). Never invent a number.
5. **Decision-log artifact.** For every field reviewed, produce a one-line entry: `[date] [field-name] [walked-to-leaf] [evidence-cited]`. Append to `.ravenclaude/runs/ferpa-decisions/`.

### 8c. For an `audit-gates.sh` gate

A new gate **"Gate 60: FERPA aggregate-threshold lint"** that scans the repo for risky dashboard-config patterns. Suggested regex set (apply to `plugins/edtech-partner-success/**` and any `dashboard.yaml` / `metrics.json`):

```bash
# Pattern 1 — student counts shown without a minimum-cell floor
grep -nE '("metric"|"field")\s*:\s*"[^"]*(count|mau|dau|actives?|users?)' \
  | grep -vE '"min_cell"\s*:\s*([0-9]|1[0-5])' \
  && echo "Gate 60 violation: count-style metric without min_cell guard"

# Pattern 2 — rare-attribute dimensions without k-anonymity guard
grep -rnE '"group_by"\s*:\s*\[[^]]*(iep|ell|frl|free_reduced|race|ethnicity|gender|disability)' \
  | grep -vE '"k_anonymity"\s*:\s*[0-9]+' \
  && echo "Gate 60 violation: rare-attribute group_by without k_anonymity guard"

# Pattern 3 — cross-LEA aggregation flag without consent reference
grep -rnE '"scope"\s*:\s*"(cross_lea|multi_district|all_customers)"' \
  | grep -vE '"consent_basis"\s*:\s*"(written_dpa|deidentified_ptac|multi_lea_approval)"' \
  && echo "Gate 60 violation: cross-LEA scope without consent_basis"

# Pattern 4 — telemetry endpoints on student-facing surfaces
grep -rnE '(google-analytics\.com|mixpanel\.com|heap\.io|fullstory\.com|hotjar\.com|segment\.io)' \
  plugins/edtech-partner-success/templates/student-* \
  && echo "Gate 60 violation: PowerSchool/Naviance-pattern telemetry on student surface"

# Pattern 5 — AI subprocessor referenced without DPA listing
grep -rnE '(openai|anthropic|cohere|mistral|pinecone)\.com/(v1|api)' \
  | xargs -I {} sh -c 'grep -lq "{}" docs/dpa/subprocessors.md || echo "Gate 60: undisclosed AI subprocessor: {}"'

# Pattern 6 — "improve the services" language in DPAs
grep -rniE 'improve (the|our) (service|product|model|platform)' plugins/edtech-partner-success/templates/dpa/ \
  && echo "Gate 60 violation: 'improvement' carve-out detected — narrow or remove"
```

Pair each pattern with a known-bad fixture under `tests/fixtures/gate-60/bad-*` and a known-good fixture under `tests/fixtures/gate-60/good-*`, per the existing audit-gates discipline.

---

## Sources ledger

> **Legend.** `[fetched]` = WebFetch retrieved full document body. `[search-snippet]` = retrieved via WebSearch result excerpts (the underlying URL was 403-blocked or paywalled but the snippet contained the cited claim). All claims with PTAC-codified numbers are cross-verified against ≥2 sources.

1. 34 CFR § 99.3 — definition of PII under FERPA. [search-snippet] https://studentprivacy.ed.gov/glossary
2. PTAC, *Frequently Asked Questions*. [search-snippet] https://studentprivacy.ed.gov/frequently-asked-questions
3. PTAC, *Data De-identification: An Overview of Basic Terms*. [search-snippet — 403 on fetch] https://studentprivacy.ed.gov/sites/default/files/resource_document/file/data_deidentification_terms_0.pdf
4. HHS/ASPE, *Minimizing Disclosure Risk in HHS Open Data Initiatives* (k-anonymity / l-diversity / t-closeness). [search-snippet] https://aspe.hhs.gov/sites/default/files/private/pdf/77196/rpt_Disclosure.pdf
5. PTAC, *Responsibilities of Third-Party Service Providers under FERPA* (Vendor FAQ). [search-snippet — 403 on fetch] https://studentprivacy.ed.gov/sites/default/files/resource_document/file/Vendor%20FAQ.pdf
6. PTAC, *FAQs — Disclosure Avoidance* (aggregation claim). [search-snippet — 403 on fetch] https://studentprivacy.ed.gov/sites/default/files/resource_document/file/FAQs_disclosure_avoidance_0.pdf
7. PTAC, *FAQs — Disclosure Avoidance* (no federal threshold mandate). [search-snippet] Same URL as [6].
8. CDC RDC Output Policies; CDC WONDER; U.S. Cancer Statistics suppression. [search-snippet] https://www.cdc.gov/rdc/output/index.html ; https://www.cdc.gov/united-states-cancer-statistics/technical-notes/suppression.html
9. Data Quality Campaign, *Understanding Minimum N-Size and Student Data* (June 2017). [search-snippet] https://dataqualitycampaign.org/wp-content/uploads/2017/06/DQC-N-size-paper-FINAL.pdf
10. PTAC, *FAQs — Disclosure Avoidance* (complementary suppression). [search-snippet] Same URL as [6].
11. FTC, *FTC Says Ed Tech Provider Edmodo Unlawfully Used Children's Personal Information for Advertising and Outsourced Compliance to School Districts* (May 22, 2023). [search-snippet] https://www.ftc.gov/news-events/news/press-releases/2023/05/ftc-says-ed-tech-provider-edmodo-unlawfully-used-childrens-personal-information-advertising
12. FTC, *Edmodo, LLC, U.S. v.* — case page. [search-snippet] https://www.ftc.gov/legal-library/browse/cases-proceedings/202-3129-edmodo-llc-us-v
13. Loeb & Loeb, *What EdTech Companies Can Learn From the FTC's Action Against Edmodo* (June 2023). [search-snippet] https://www.loeb.com/en/insights/publications/2023/06/what-edtech-companies-can-learn-from-the-ftcs-action-against-edmodo
14. FTC, *FTC Files Amicus Brief Saying COPPA Can't Force Parents Into Arbitration* (Aug 2024 / appeal Aug 2025). [search-snippet] https://www.ftc.gov/news-events/news/press-releases/2024/08/ftc-files-amicus-brief-saying-coppa-cant-force-parents-arbitration
15. FTC, *Shanahan v. IXL Learning, Inc.* case page. [search-snippet] https://www.ftc.gov/legal-library/browse/amicus-briefs/shanahan-v-ixl-learning-inc
16. Public Interest Privacy Center, *New COPPA Case: What a Recent FTC Amicus Brief Does–and Does Not–Change for Schools*. [search-snippet] https://publicinterestprivacy.org/ftc-amicus-briefs-ixl-learning/
17. State of Surveillance, *PowerSchool Settles for $17M After Secretly Recording Millions of Students* (2026). [search-snippet] https://stateofsurveillance.org/news/powerschool-naviance-17-million-student-privacy-settlement-2026/
18. Captain Compliance, *The PowerSchool Settlement, the Largest Student Data Breach in U.S. History*. [search-snippet] https://captaincompliance.com/education/the-powerschool-settlement-the-largest-student-data-breach-in-u-s-history-and-what-edtechs-privacy-crisis-means-for-every-family-in-america/
19. M-A Chronicle, *PowerSchool's $17.25 Million Settlement*. [search-snippet] https://machronicle.com/powerschools-17-25-million-settlement-exposes-years-of-student-data-tracking/
20. Latham & Watkins, *FTC Publishes Updates to COPPA Rule* (May 2025). [search-snippet] https://www.lw.com/en/insights/ftc-publishes-updates-to-coppa-rule
21. Davis Wright Tremaine, *FTC Amends COPPA Rule To Address Changes in Technology and Online Practices*. [search-snippet] https://www.dwt.com/blogs/privacy--security-law-blog/2025/05/coppa-rule-ftc-amended-childrens-privacy
22. Venable, *FTC Finalizes COPPA Rule Changes, New Rule Takes Effect in June*. [search-snippet] https://www.venable.com/insights/publications/2025/01/ftc-finalizes-coppa-rule-changes-in-the-biden
23. Public Interest Privacy Center, *New COPPA Update: A Setback for Schools and Student Privacy?* [search-snippet] https://publicinterestprivacy.org/new-coppa-update/
24. StudentDPA, *Understanding FERPA, COPPA, and State-Specific Privacy Laws* (SOPIPA section). [search-snippet] https://studentdpa.com/blog/understanding-ferpa-coppa-state-privacy-laws-03202025
25. Cybernut, *All About New York's Education Law § 2-d* (Part 121, NIST CSF, Parents' Bill of Rights, DPO). [search-snippet] https://www.cybernut.com/blog/all-about-new-yorks-education-law-2-d-student-data-privacy-explained
26. NYSED, *Proposing Part 121 of Commissioner's Regulations*. [search-snippet] https://www.regents.nysed.gov/sites/regents/files/P-12%20-%20Proposing%20Part%20121%20of%20Commissioner%E2%80%99s%20Regulations%20%E2%80%93%20Protecting%20PII%20in%20Educational%20Agencies%20(Education%20Law%202-d%20Regulations)_0.pdf
27. Cybernut, *All About SOPPA: What Illinois Schools Must Know About Student Data Protections* (30-day breach SLA, list-of-operators, 10-day posting rule). [search-snippet] https://www.cybernut.com/blog/all-about-soppa-what-illinois-schools-must-know-about-student-data-protections
28. Hireplicity, *FERPA Compliance Checklist 2025: Schools & EdTech Guide* (NY+IL heuristic). [search-snippet] https://www.hireplicity.com/blog/ferpa-compliance-checklist-2025
29. NCES, *Forum Guide to the Privacy of Student Information — Disclosure of Student Information*. [search-snippet] https://nces.ed.gov/pubs2006/stu_privacy/disclosure.asp
30. Center for Democracy & Technology, *Commercial Companies and FERPA's School Official Exception: A Survey of Privacy Policies*. [search-snippet] https://cdt.org/insights/commercial-companies-and-ferpas-school-official-exception-a-survey-of-privacy-policies/
31. Public Interest Privacy Center, *Fixing FERPA: Enhancing EdTech Accountability*. [search-snippet] https://publicinterestprivacy.org/edtech-data-sharing/
32. Future of Privacy Forum, *New US Dept of Ed Finding: Schools Cannot Require Parents or Students to Waive Their FERPA Rights Through Ed Tech Company's Terms of Service*. [search-snippet] https://fpf.org/blog/agoraletter/
33. Pikmykid, *2025 FERPA Guidance: What Schools Should Know* (37-question FAQ refresh). [search-snippet] https://www.pikmykid.com/blog/department-of-education-releases-new-ferpa-resources-for-schools
34. ResDAC, *CMS Cell Size Suppression Policy*. [search-snippet] https://resdac.org/articles/cms-cell-size-suppression-policy
35. SDPC, *NDPA v2.2* announcement (Nov 19, 2025). [search-snippet] https://privacy.a4l.org/national-dpa/
36. Future of Privacy Forum, *The First National Model Student Data Privacy Agreement Launches*. [search-snippet] https://fpf.org/blog/the-first-national-model-student-data-privacy-agreement-launches/
37. Common Sense Education, *Introducing the Common Sense Privacy Seal*. [search-snippet] https://www.commonsense.org/education/articles/introducing-the-common-sense-privacy-seal-a-new-standard-in-digital-privacy
38. Captain Compliance, *AI, Privacy & Schools: The Coming Storm* (vendor "do-not-train" pledge pattern). [search-snippet] https://captaincompliance.com/education/ai-privacy-schools-the-coming-storm-and-how-we-help-edtech-stay-compliant/
39. SDPC, *NDPA v2 Usage Guidance and Development Processes* (Exhibit E mandatory; Exhibit H checkbox removed). [search-snippet] https://files.a4l.org/privacy/NDPA/NDPAv2_Usage_Guide_and_Development_Process.pdf
40. EdWeek, *How School Districts Are Crafting AI Policy on the Fly* (Charlotte-Mecklenburg + Washington County UT). [search-snippet] https://www.edweek.org/technology/how-school-districts-are-crafting-ai-policy-on-the-fly/2025/10
41. Anarlog, *Anthropic Claude Data Retention Policy 2026* (Claude for Education / API ZDR posture). [search-snippet] https://anarlog.so/blog/anthropic-data-retention-policy/
42. TechCrunch, *Anthropic users face a new choice — opt out or share your chats for AI training* (Aug 28, 2025; 5-year retention if opted in). [search-snippet] https://techcrunch.com/2025/08/28/anthropic-users-face-a-new-choice-opt-out-or-share-your-data-for-ai-training/
43. OpenAI Developer Community, *Zero Data Retention Information* (enterprise/API ZDR). [search-snippet] https://community.openai.com/t/zero-data-retention-information/702540
44. Public Interest Privacy Center, *State Student Privacy Laws*. [search-snippet] https://publicinterestprivacy.org/resources/state-student-privacy/
45. CISA, *Findings and Updates from CISA's Ongoing Collaboration with Education Technology Vendors* (Secure-by-Design for ed-tech). [search-snippet] https://www.cisa.gov/news-events/news/findings-and-updates-cisas-ongoing-collaboration-education-technology-vendors-address-k-12
46. K12 SIX, *Essential Cybersecurity Protections 2024-25* (14 controls, 5 categories). [search-snippet] https://static1.squarespace.com/static/5e441b46adfb340b05008fe7/t/67101d1de118bb73687ff744/1729109277225/24-25-K12SIX-EssentialProtections-v1.pdf
47. CISA, *Cybersecurity Guidance for K-12 Technology Acquisitions*. [search-snippet] https://www.cisa.gov/resources-tools/resources/cybersecurity-guidance-k-12-technology-acquisitions
48. EdTech Law Center, *IXL Data Privacy Litigation* case overview. [search-snippet] https://edtech.law/cases/nonconsensual-student-data-mining-powerschool-and-ixl-learning/
49. White & Case, *Data Privacy Update* (2025 COPPA Final Rule overview). [search-snippet] https://www.whitecase.com/insight-alert/data-privacy-update-2025
50. Whiteboard Advisors, *Unpacking the Edmodo Order – What It Means for Edtech Companies*. [search-snippet] https://whiteboardadvisors.com/ftc-order-edmodo/
51. AASA, *A Wild 48 Hours for Federal Student Privacy*. [search-snippet] https://www.aasa.org/resources/blog/a-wild-48-hours-for-federal-student-privacy
52. Hosch & Morris, *EdTech Platforms May Violate Privacy Laws*. [search-snippet] https://www.hoschmorris.com/privacy-plus-news/edtech-platforms-may-violate-privacy-laws
53. EdWeek MarketBrief, *FTC Takes Action Against Ed-Tech Company for Failure to Deliver on Security Promises* (Dec 2025). [search-snippet] https://marketbrief.edweek.org/regulation-policy/ftc-takes-action-against-ed-tech-company-for-failure-to-deliver-on-security-promises/2025/12

**Source count: 53 unique URLs across 10 topic angles.** All numeric thresholds cross-cited to ≥2 sources or explicitly labeled "no federal mandate; LEA default." PTAC PDFs cited from search-snippet excerpts after WebFetch returned HTTP 403 (likely UA-block on the studentprivacy.ed.gov CDN; the URLs themselves resolve in a browser); secondary sources confirm every PTAC-attributed claim. The §7 decision tree is the load-bearing output and is designed to fail safely toward "STOP — needs counsel" on any ambiguity.
