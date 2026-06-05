---
scenario_id: 2026-06-05-third-party-vendor-risk-retiering
contributed_at: 2026-06-05
plugin: regulatory-compliance
product: third-party-risk
product_version: "n/a"
scope: likely-general
tags: [third-party-risk, vendor, due-diligence, ongoing-monitoring, concentration]
confidence: medium
reviewed: false
---

## Problem

An institution ran the same vendor due-diligence questionnaire on every third party — the office-supplies vendor got the same package as the cloud provider hosting the core banking system. The result was both over- and under-control: low-risk vendors burned scarce diligence capacity, while a genuinely **critical** provider (a fintech doing customer-facing activity on the bank's behalf) had no deeper diligence, no contractual right-to-audit, and no ongoing monitoring proportionate to its criticality. A regulator exam was approaching. `risk-and-controls-specialist` was asked to re-tier the vendor population and right-size diligence to risk.

## Context

- Sector: US-supervised banking organization (so the June 2023 interagency third-party guidance is the anchor — but proportionate, risk-based third-party risk management is a near-universal supervisory expectation; the *specific* guidance differs by regulator/jurisdiction).
- Constraint: the firm had ~300 third parties and a flat, one-size process. The fix is not "more diligence on everyone" — it is **proportionality**: depth scaled to the relationship's risk and criticality.
- The team conflated "we did due diligence on every vendor" with "we did *risk-appropriate* due diligence." Uniform depth is not the same as adequate depth where it matters.

## Attempts

- Tried: deepen the questionnaire for all 300 vendors. Outcome: rejected — this multiplies effort without targeting it, and still under-controls the critical relationships relative to their risk. Volume of diligence is not the supervisory expectation; *proportionality* is.
- Tried: grounded the framework against the regulator's primary guidance rather than memory. The **Interagency Guidance on Third-Party Relationships: Risk Management** (Federal Reserve, FDIC, OCC), final **June 6, 2023**, frames sound third-party risk management as proportionate to "the level of risk, complexity, and size" of the organization and the nature of the relationship, and structures it across the **third-party relationship life cycle**: planning, **due diligence and third-party selection**, contract negotiation, **ongoing monitoring**, and termination. It places particular weight on **critical activities** — those that could cause significant risk if the third party fails to perform. Outcome: gave a defensible basis for tiering by criticality and for scaling diligence + monitoring to tier, rather than running a flat process.
- Tried (the move that worked): built a **criticality tier** for each vendor (does failure of this third party pose significant risk to operations, customers, or compliance?), then mapped diligence depth, contract terms (right-to-audit, breach notification, subcontractor/concentration disclosure), and ongoing-monitoring cadence to tier. Surfaced a **concentration** flag where multiple critical activities ran through one provider. Each tiering decision and its rationale was documented (CLAUDE.md §3 #6, default-to-written). Outcome: critical relationships got proportionate depth + monitoring + contractual protections; low-risk vendors got a light-touch path; the exam had a defensible, risk-based methodology to point at.

## Resolution

The error was uniform diligence depth — treating "we assessed every vendor" as adequate when the supervisory expectation is *proportionate* assessment. The fix: tier the vendor population by criticality (significant-risk-if-they-fail), then scale due diligence, contract terms, and ongoing monitoring to tier across the relationship life cycle — and document the tiering rationale so the methodology, not just the conclusions, survives the exam.

**Action for the next analyst hitting this pattern:** don't run a flat process. Tier by **criticality** first (the interagency guidance's "critical activities" lens), then scale diligence + contract protections + ongoing-monitoring cadence to tier, and check for **concentration** (multiple critical activities through one provider — and concentration *across* providers in one sector). The June 2023 interagency guidance is **US-banking-specific** (`[verify-at-use]`); a non-US or non-banking firm has its own outsourcing/third-party regime (e.g. EBA outsourcing guidelines, DORA for EU financial entities) — name the applicable one (CLAUDE.md §3 #12). This is compliance/risk analysis, not legal advice; contract terms (right-to-audit clauses, liability) need counsel before execution.

**Sources (retrieved 2026-06-05):**
- OCC Bulletin 2023-17 — Third-Party Relationships: Interagency Guidance on Risk Management: https://www.occ.gov/news-issuances/bulletins/2023/bulletin-2023-17.html
- Federal Register — Interagency Guidance on Third-Party Relationships: Risk Management (final, June 9, 2023): https://www.federalregister.gov/documents/2023/06/09/2023-12340/interagency-guidance-on-third-party-relationships-risk-management

These describe the **US banking** interagency guidance; third-party/outsourcing regimes differ by jurisdiction and sector. The criticality definition, required contract terms, and monitoring cadence are `[verify-at-use]` against the applicable regulator's guidance and the firm's own framework before any deliverable.
