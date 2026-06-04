---
target_path: plugins/edtech-partner-success/knowledge/ai-training-prohibition-clauses.md
last_reviewed: 2026-06-04
refresh_triggers:
  - SDPC publishes a new NDPA version
  - An LLM vendor changes its ZDR / training policy (Anthropic Aug 2025 consumer-shift pattern)
  - A new state passes an AI-specific student-data rule
  - A district AI policy creates a new contract pattern
audience: [psm, dpa-author, security-reviewer, ferpa-comms-translator]
status: field guidance — NOT legal advice
sources:
  - /tmp/research-ferpa-decision-tree.md §6 (research ledger sources [35]-[43])
---

# AI training prohibition clauses — no-training, no-improvement-carveout, subprocessor flow-down

> **Status.** The five contractual instruments that must be in any EdTech DPA touching AI/ML. Anchored to NDPA v2.2 (Nov 19, 2025) + the 2025 PTAC vendor-FAQ + the 2026 enforcement landscape.
> **Field guidance, not legal advice.** Specific contract language routes through counsel.

---

## 1. The clear-line rule (2025 consensus)

> A vendor cannot use student PII (or data derived from student PII, including model weights fine-tuned on it) to train models that serve any customer other than the LEA that contributed the data — **unless the DPA expressly authorizes it.**

Source: research §6, corroborated across PTAC vendor guidance, SDPC NDPA v2.2, Common Sense Privacy, and emerging district AI policies.

---

## 2. The five required clauses

Every DPA touching AI/ML must put these in writing:

| # | Clause | What it forbids | Why |
|---|---|---|---|
| **1** | **No training on customer data** | Neither base-model pretraining, fine-tuning, nor RLHF on this LEA's data unless explicit opt-in | FERPA § 99.31(a)(1)(i)(B)(4) authorized-purpose limit |
| **2** | **No "improvement" carveout** | Removes or narrows "to improve the Services" language | PTAC vendor-FAQ reads this narrowly; CA SOPIPA + NY 2-d + IL SOPPA prohibit non-educational profiling |
| **3** | **No retention past contract termination + wind-down** | Standard 30-90 day deletion window; written deletion certification | NY § 2-d Part 121; IL SOPPA 60-day rule; CA SOPIPA right to delete |
| **4** | **Subprocessor flow-down** | Every AI vendor in the stack (OpenAI, Anthropic, Pinecone, Cohere, Mistral) on the SOPPA subprocessor list AND bound to the same no-training restriction | IL SOPPA published-list requirement; NDPA v2.2 Exhibit H mandatory disclosure |
| **5** | **De-identified data carveout, if used, defined to PTAC standard** | Vendor cannot rely on its own marketing-style de-identification definition | PTAC FAQ — "aggregation alone is not de-identification" |

---

## 3. The consumer-Claude vs enterprise-ZDR distinction (load-bearing)

**The asymmetry the vendor's DPA does NOT cover** [source: research §6, [41][42][43]]:

| Surface | Training posture | FERPA exposure for LEA |
|---|---|---|
| **OpenAI Enterprise / API ZDR** | Inputs/outputs never used for training; abuse-screening only | Covered by vendor enterprise contract |
| **Anthropic Claude for Education / API ZDR** | Same — never used for training under enterprise contract | Covered by vendor enterprise contract |
| **Consumer Claude (Aug 2025 policy shift)** | **Trains on opted-in conversations; 5-year retention** | **A teacher pasting student work into a personal Claude consumer account creates FERPA exposure that the vendor's enterprise contract does NOT cover** |
| **Consumer ChatGPT** | Trains on opted-in conversations by default | Same exposure pattern |
| **Microsoft Copilot (consumer)** | Same | Same |

### The pattern the ferpa-comms-translator and security-reviewer must flag

When a teacher or admin says *"I asked Claude to summarize Jamie's writing"* or *"I use ChatGPT to grade essays"* — confirm which surface:

- **Enterprise / school-licensed seat** → covered by DPA
- **Personal / consumer account** → **STOP** — FERPA exposure; the vendor's no-training clause doesn't reach a personal account

This is the gap that catches districts off-guard: the contract is correct, the architecture is correct, but the teacher's habit creates a parallel data flow the contract was never designed to govern.

---

## 4. The pre-built clause library

### Clause A — No training

> **No Use for Model Training.** Vendor shall not use Customer Data (including any data, content, prompts, completions, embeddings, fine-tunes, model weights derived from Customer Data, or telemetry containing Customer Data) for any base-model pretraining, fine-tuning, reinforcement learning, RLHF, or any other model-improvement activity that benefits Vendor's other customers, products, or services. This restriction applies whether or not the Customer Data has been "aggregated," "de-identified," or "anonymized." This restriction binds Vendor's subprocessors via Section [Subprocessor Flow-Down].

### Clause B — No "improvement" carveout

> **No General "Improvement" Carveout.** "Improvement of the Services" is limited to (i) telemetry necessary to debug Customer's own instance, (ii) security and abuse-screening necessary to protect Customer Data, and (iii) aggregate operational metrics that do not contain Customer Data and are not derived from a single Customer. Any use of Customer Data to build features, train models, or improve experiences for other Customers requires Customer's prior written opt-in via [Order Form / Amendment].

### Clause C — Deletion at termination

> **Deletion at Termination.** Within [30 / 60 / 90] days after termination or expiration, Vendor shall (i) delete all Customer Data from production systems, (ii) delete all backups containing Customer Data within Vendor's standard backup-rotation window not exceeding [N] days, (iii) require each subprocessor to do the same, and (iv) provide written certification of deletion to Customer.

### Clause D — Subprocessor flow-down

> **Subprocessor Flow-Down.** Vendor shall not engage a Subprocessor (including any third-party LLM provider, vector database, or AI inference service) to Process Customer Data unless: (i) the Subprocessor is listed on Exhibit [H] (Subprocessor List), (ii) Vendor has bound the Subprocessor in writing to data-protection obligations no less protective than this Agreement, including the No Training and No Improvement Carveout restrictions, and (iii) Vendor has verified the Subprocessor's Zero Data Retention enterprise contract status where applicable.

### Clause E — Audit rights

> **Audit Rights.** Upon [N] days' written notice, Customer (or its authorized auditor) may audit Vendor's compliance with this Agreement once per twelve-month period, including: (i) review of Vendor's Subprocessor list and contracts, (ii) review of Vendor's ZDR posture with each LLM provider, (iii) review of deletion certifications, and (iv) review of any incidents within the audit period.

---

## 5. Vendor-side decision matrix (which LLM provider for which posture)

| Provider | ZDR enterprise contract available? | Trains on inputs by default? | Recommended for student-touching workloads? |
|---|---|---|---|
| **OpenAI Enterprise / API (ZDR-enabled)** | Yes | No on Enterprise / API | Yes, with signed ZDR + DPA listing |
| **Anthropic Claude for Education / API (ZDR-enabled)** | Yes | No on enterprise contract | Yes, with signed ZDR + DPA listing |
| **Anthropic Claude (consumer)** | N/A | **Yes if opted in; 5-year retention** | **No — gap in DPA coverage** |
| **OpenAI ChatGPT (consumer)** | N/A | Yes by default | **No — gap in DPA coverage** |
| **Microsoft Copilot (commercial)** | Yes via Microsoft 365 enterprise | No on commercial seat | Yes if licensed to the LEA |
| **Self-hosted (open-weights model on LEA infrastructure)** | N/A (no third-party) | No | Yes — strongest posture; check operational capacity |
| **Mistral / Cohere / etc. (API)** | Per vendor — check | Per vendor — check | Only with signed enterprise + ZDR + DPA listing |

---

## 6. The contractual instruments to anchor on

| Instrument | What it gives you |
|---|---|
| **SDPC NDPA v2.2** (Nov 19, 2025) | National model DPA; Exhibit E mandatory; Exhibit H subprocessor disclosure mandatory; includes de-identified data + sub-processor restrictions |
| **PTAC Vendor FAQ** | Federal floor for school-official exception; authorized-purpose limit |
| **2025 DOE FERPA FAQ** (37-question update) | TOS clauses requiring FERPA-rights waiver are invalid |
| **Common Sense Privacy Seal** | Rubric for evaluating vendor privacy posture |
| **Charlotte-Mecklenburg AI policy** (Oct 2025); **Washington County UT policy 3750** | District-side AI-committee review pattern; "prohibits Confidential/Protected Data with AI tools unless approved" |

---

## 7. The pre-publication checklist

Before any DPA touching AI signs:

- [ ] All five clauses (No Training / No Improvement Carveout / Deletion / Subprocessor Flow-Down / De-identified Data) are present
- [ ] Subprocessor list (Exhibit H) is current and includes every LLM provider, vector DB, and AI inference vendor
- [ ] Each LLM-provider subprocessor's ZDR enterprise contract is verified (not assumed)
- [ ] Consumer-AI gap is closed in the LEA-side AI policy: explicit prohibition on staff using personal-account ChatGPT / Claude / Copilot with student work
- [ ] State-law overlay satisfied (see [`state-privacy-law-matrix.md`](state-privacy-law-matrix.md))
- [ ] FERPA decision tree walked for any AI-fed dashboard field (see [`ferpa-aggregate-threshold-defaults.md`](ferpa-aggregate-threshold-defaults.md))

---

## 7. Biometric-identifier overlay (post-COPPA amendment) — added 2026-06-04

The Apr 22 2025 final COPPA Rule (full-compliance deadline **Apr 22, 2026 — now passed**) added **biometric identifiers (face / fingerprint / voice) and government-issued identifiers** to the PI definition for under-13. This materially changes the AI-training prohibition calculus:

- **Face / fingerprint / voice from under-13 = COPPA-PI.** Training an AI model on K-5 voice-assessment audio, face-recognition login images, or fingerprint biometrics requires direct VPC (verifiable parental consent) — school authorization is **insufficient**.
- **Edmodo and IXL precedents extend here** — the school-authorization line is maximally narrow for biometric collection. The FTC's two IXL amicus briefs (Aug 13, 2024 + post-interlocutory-appeal) reaffirm that schools cannot bind parents to vendor TOS arbitration for non-educational uses.

**PSM checklist for K-5 AI features:**
- [ ] Any AI feature using face / fingerprint / voice from K-5 → STOP-needs-counsel.
- [ ] Any AI feature using government-ID (SSN-suffix, immigration linkage, Medicaid binding) from K-5 → STOP-needs-counsel.
- [ ] Vendor DPA explicitly excludes biometric audio/image/text from training corpus.
- [ ] Vendor written cybersecurity program present (now a Rule requirement, not best-practice).
- [ ] Retention is purpose-limited (no indefinite retention) per amended Rule.

See [`coppa-2025-amendment-edtech-implications.md`](./coppa-2025-amendment-edtech-implications.md) for the full operational checklist.

---

## 8. Federal AI EO + COPPA Apr 2026 enforcement window — added 2026-06-04

The convergence of the **federal AI Executive Order (Dec 2025)** with the **COPPA Apr 22 2026 full-compliance deadline** creates an enforcement-risk peak in **2026-Q2-Q4**. Practitioner consensus 2026:

- **AI-feature subprocessor disclosure is the most common 2026 audit finding.** Any AI feature added since Apr 22, 2026 needs a fresh DPA addendum + subprocessor flow-down review.
- **NDPA v2.2 (Nov 19, 2025) is the current contract substrate** — there is no v2.3 / v3.0 yet as of 2026-06-04. AI-training restrictions are now first-class clauses, not optional addenda.
- **The bright-line trip wire**: *EdTech vendor uses an AI sub-processor that retains data for training* → triggers no-improvement-carveout + NDPA v2.2 Exhibit H subprocessor flow-down + (in NY/IL/CA) non-educational profiling prohibition simultaneously.

`[verify-at-use — 2026-06-04 — federal AI EO citations + NDPA v2.2 publication]`

---

## Sources

[35] SDPC *NDPA v2.2* announcement (Nov 19, 2025) — https://privacy.a4l.org/national-dpa/
[36] Future of Privacy Forum *The First National Model Student Data Privacy Agreement Launches*
[37] Common Sense Education *Introducing the Common Sense Privacy Seal*
[38] Captain Compliance *AI, Privacy & Schools: The Coming Storm*
[39] SDPC *NDPA v2 Usage Guidance and Development Processes*
[40] EdWeek *How School Districts Are Crafting AI Policy on the Fly* (Charlotte-Mecklenburg + Washington County UT)
[41] Anarlog *Anthropic Claude Data Retention Policy 2026*
[42] TechCrunch *Anthropic users face a new choice* (Aug 28, 2025; 5-year retention if opted in)
[43] OpenAI Developer Community *Zero Data Retention Information*

Full ledger: `/tmp/research-ferpa-decision-tree.md` §Sources.
