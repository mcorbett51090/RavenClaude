# RegTech on Power Platform — building compliance & regulatory solutions

> **Read when** you're about to design or build a **compliance / regulatory solution** on Power Platform — a Dataverse data model for a regulatory regime, a Power Automate flow that drives a filing calendar or an alert/escalation, a Power BI compliance-scoring report (risk-rating a population against a rubric), or a Copilot Studio agent that guides a regulated intake. Owned by `power-platform-admin` (governance posture) + `dataverse-architect` (data model); secondary `flow-engineer`, `power-bi-engineer`, `copilot-studio-engineer`. Dated 2026-06-04.
>
> **This file is self-contained Power Platform guidance and assumes nothing about other installed plugins.** It covers how to *build* compliance solutions on the platform. The **domain expertise** — what a regime actually requires (BMA licensing classes, Basel capital ratios, AML/KYC thresholds, the filing deadlines, the severity of a finding) — is a *separate* competency. If the `regulatory-compliance` plugin is installed alongside, route the domain questions there (see §6); if it isn't, **this file flags every point where a regulatory subject-matter expert must sign off the substance** — the platform builds what the SME specifies, it does not invent the regulatory truth.

---

## 1. The pattern — what a Power Platform compliance solution is made of

A regulatory/compliance solution on the platform is almost always some composition of four building blocks, mapped to the platform's natural homes:

| Compliance need | Power Platform home | Owner agent |
|---|---|---|
| **System of record** for entities, obligations, controls, findings, evidence | **Dataverse** (tables + relationships + business rules + auditing) | `dataverse-architect` |
| **Process** — filing calendar, periodic attestation, finding remediation, escalation, maker-checker | **Power Automate** (scheduled + event flows) and/or **business process flows** | `flow-engineer` |
| **Measurement** — risk-scoring a population against a rubric; supervisory dashboards; trend over time | **Power BI** (semantic model + report) | `power-bi-engineer` |
| **Guided intake / Q&A** — structured questionnaire, classification helper, policy lookup | **Power Apps** (canvas/model-driven) and/or **Copilot Studio** | `model-driven-engineer`, `copilot-studio-engineer` |

> **Production lineage (this is not hypothetical):** the **BMA CSP Thematic Review / BMA-CSP-Risk-Scoring** work already captured across this plugin's `knowledge/` (see [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md), [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md), [`pbir-m-query-pitfalls.md`](pbir-m-query-pitfalls.md)) is exactly this pattern: a **Dataverse-backed questionnaire** → **Power BI risk-scoring report** rating CSP licensees against a weighted rubric for a **BMA** (Bermuda Monetary Authority) supervisory review. The pitfalls those files document (silent-zero DAX from category-string mismatch, load-stage silent drops) are *the* characteristic failure modes of compliance-scoring builds — re-read them before building another.

---

## 2. Dataverse data model — the compliance backbone

The recurring shape for a regulatory solution:

- **Regulated entity** (the licensee / customer / counterparty) — the subject.
- **Obligation / requirement** — the rule the entity is measured against (a licence condition, a filing, a control objective). Often hierarchical (regime → part → requirement).
- **Assessment / response** — the entity's answer or the reviewer's determination against each obligation (the questionnaire row).
- **Finding / issue** — a gap, with **severity**, owner, remediation, due date, status.
- **Evidence** — documents/attachments supporting a response or closing a finding.
- **Score / rating** — derived, usually in the BI layer, **not** stored as the source of truth (recompute from responses so the rubric stays auditable).

**Load-bearing build rules (hard-won):**

- **Decouple DAX/logic from data-source strings.** Map raw category/requirement strings to a **stable short domain key** in a calculated column (Dataverse or the TMDL `Domain` column pattern) and reference *that* everywhere — see [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md). A hardcoded `Category = "Core"` filter that silently matches zero rows is the #1 compliance-scoring bug, and it fails *silently* (renders `0`, no error) — catastrophic when the number is a regulatory risk rating.
- **Turn on Dataverse auditing** for the entity/response/finding tables from day one. A compliance system's change history *is* part of its evidence; retrofitting auditing loses the trail you most need.
- **Model the requirement hierarchy explicitly** (don't flatten a regime into one string column) so the rubric weighting (§3) and the supervisory roll-up are queryable.
- **A score is a *view*, not a fact** — store the responses + the rubric; compute the rating. Storing a frozen score invites silent drift when the rubric changes.

---

## 3. Scoring / rating — the rubric layer

Compliance scoring rates a population against a **weighted rubric**. The traps are arithmetic and silent:

- **Weighting across a multi-category domain is a SUM of constituents, not a MAX** — see the multi-category-domain trap in [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md).
- **Score-scale discipline** — if weights are fractional (0–1) and thresholds are 0–100, you are silently 100× off. Pin the scale once and assert it.
- **A build/deploy verification step must run the `SUMMARIZE`/`SUMMARIZECOLUMNS` diagnosis against the live model** and confirm the filter strings match real data *before* anyone trusts a rating — REST-first, per [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md). "Deploy succeeded" ≠ "the numbers are right."
- **The rubric itself is a regulatory artefact** — the weights, thresholds, and pass/fail bands encode a supervisory judgement. **A regulatory SME owns the rubric; the platform implements it.** Do not invent or "tidy" weights to make a distribution look nicer.

---

## 4. Process — filing calendars, attestations, escalation

Power Automate is the natural home for the *time* and *workflow* dimension of compliance:

- **Filing-calendar / deadline reminders** — scheduled flows that read obligation due-dates from Dataverse and notify owners on a lead-time ladder (T-30 / T-7 / overdue). The **deadlines and lead-times are regulatory facts** — source them from the regime, not a guess.
- **Periodic attestation / re-certification** — recurring flows that re-open a response cycle.
- **Finding remediation + escalation** — event flows on finding status; maker-checker on closure; escalation on overdue/high-severity.
- **Build flows programmatically** via the Dataverse Web API `workflow`-entity path (category=5, ComponentType=29) when scripting at scale — see [`programmatic-flow-creation.md`](programmatic-flow-creation.md). The PA Management API is usually SPN-blocked; don't start there.

---

## 5. Governance — regulated data needs the strict posture

Compliance solutions hold **sensitive, often supervisory or personal data**. The governance posture is not optional:

- **Managed Environments** for any environment holding regulated data — the proactive in-product controls (Managed security + Managed governance). See [`managed-environments-and-governance-2026.md`](managed-environments-and-governance-2026.md).
- **DLP policies** that prevent the compliance data from crossing into unsanctioned connectors — model the connector classification deliberately; a compliance app exfiltrating via an unmanaged connector is the nightmare scenario.
- **Microsoft Purview** for data classification, retention, and eDiscovery over the Dataverse data where the regime mandates retention/records management.
- **Least-privilege Dataverse security roles** — supervisory data is need-to-know; model row-level/business-unit security, don't blanket-grant.
- **Audit + retention are part of the deliverable, not an afterthought** — a regulator examining the *solution* will ask how its own change-history and access are controlled.
- **Out-of-notebook service-principal secret use mandates a `ravenclaude-core/security-reviewer` pass** (consistent with the `sempy-fabric-reference.md` rule).

> **Decision Tree: where does a compliance-solution component belong?**
>
> 1. **Is it the system of record (entities, obligations, findings, evidence)?** → **Dataverse**, auditing on, in a **Managed Environment** with DLP. Not SharePoint lists for anything supervisory.
> 2. **Is it time/workflow-driven (deadlines, attestation cycles, escalation)?** → **Power Automate** (+ business process flow for staged human review).
> 3. **Is it measurement/rating against a rubric?** → **Power BI** semantic model + report; the rubric is SME-owned; verify the numbers REST-first before trusting them.
> 4. **Is it guided human intake or Q&A?** → **Power Apps** (structured form/maker-checker) or **Copilot Studio** (conversational intake / policy lookup) — with DLP + Purview governance per [`copilot-agents-2026.md`](copilot-agents-2026.md).
> 5. **Does answering it require knowing what the *regime* requires (a licence class, a capital ratio, an AML threshold, a finding's regulatory severity)?** → **that is a domain question, not a platform question** — route to a regulatory SME / the `regulatory-compliance` plugin (§6). The platform builds to the SME's spec; it does not author the regulatory truth.

---

## 6. The seam to the `regulatory-compliance` plugin (graceful degradation)

**Two competencies, deliberately separate:** *building the solution* (this plugin) and *knowing the regulatory substance* (the `regulatory-compliance` plugin). They compose cleanly when both are installed, and each stands alone when only one is.

| The question is about… | Belongs to | Example |
|---|---|---|
| **How to build it on the platform** | **this plugin** (power-platform) | "Model the CSP questionnaire in Dataverse"; "why is every risk score rendering 0?"; "schedule the filing-deadline reminders" |
| **What the regime requires** | **`regulatory-compliance`** (if installed) | "Which BMA licence class is this CSP?"; "what's the Basel CET1 minimum + buffer?"; "is this a high-severity finding?"; "what are the actual filing deadlines?" |

**If `regulatory-compliance` IS installed:** route the domain questions to its agents — `bma-financial-institutions-specialist` (Bermuda classification/licensing/capital), the `basel-framework.md` knowledge file (capital ratios for a banking-scoring build), `aml-kyc-analyst` (KYC/EDD rubrics), `risk-and-controls-specialist` (control-to-citation mapping that becomes your obligation model), `regulatory-reporting-analyst` (the filing calendar your flows automate). The SME specifies the rubric/obligations/deadlines; this plugin builds them.

**If `regulatory-compliance` is NOT installed:** this plugin still builds the solution correctly — **but every regulatory fact (a rubric weight, a threshold, a deadline, a severity band, a licence-class rule) must be supplied and signed off by a human regulatory SME.** Do not infer regulatory substance from the platform side; flag the dependency explicitly in the build and treat any regime-specific value as `[needs SME sign-off]` until confirmed. This is the same accuracy discipline the rest of the plugin applies to platform facts, extended to the domain layer.

**No hard dependency exists in either direction** — neither plugin `requires` the other; this is a soft, install-time-optional bridge per the marketplace's cross-plugin-references convention ([`../../../docs/best-practices/cross-plugin-references.md`](../../../docs/best-practices/cross-plugin-references.md)).

---

## 7. Cross-references

- **Within this plugin:** [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md), [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md), [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md), [`pbir-m-query-pitfalls.md`](pbir-m-query-pitfalls.md) (the BMA-CSP scoring-build lessons); [`managed-environments-and-governance-2026.md`](managed-environments-and-governance-2026.md), [`copilot-agents-2026.md`](copilot-agents-2026.md) (governance); [`programmatic-flow-creation.md`](programmatic-flow-creation.md) (flow automation at scale).
- **Across plugins (soft, optional):** the `regulatory-compliance` plugin for all domain substance — see §6. The convention governing this reference style: [`../../../docs/best-practices/cross-plugin-references.md`](../../../docs/best-practices/cross-plugin-references.md).
