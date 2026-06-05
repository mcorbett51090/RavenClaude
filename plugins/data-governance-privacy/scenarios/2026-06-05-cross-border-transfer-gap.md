---
scenario_id: 2026-06-05-cross-border-transfer-gap
contributed_at: 2026-06-05
plugin: data-governance-privacy
product: gdpr
product_version: "n/a"
scope: likely-general
tags: [cross-border, scc, adequacy, dpf, transfer-mechanism, sub-processor]
confidence: medium
reviewed: false
---

## Problem

An EU-based SaaS company onboarded a US analytics vendor and a US-hosted support tool, sending EU customers' personal data to both. A data-mapping exercise (prompted by a customer's DPA questionnaire) surfaced the gap: **personal data was flowing to the US with no documented transfer mechanism in place for either vendor.** The team's belief was "the US is fine now, there's a framework" — but neither US vendor was certified under the EU-US Data Privacy Framework, and one of them sub-processed to a *fourth* country with no adequacy decision at all. The transfers were happening; the GDPR Chapter V basis for them did not exist on paper.

## Constraints context

- GDPR Chapter V requires a transfer mechanism for personal data leaving the EEA to a country without an adequacy decision: an adequacy finding, or an Article 46 safeguard (Standard Contractual Clauses / Binding Corporate Rules), or a narrow derogation.
- The **EU-US Data Privacy Framework adequacy decision (adopted 10 July 2023) only covers US organizations that are *certified* under it** — it is **not** a blanket US adequacy finding. Transfers to a *non-certified* US recipient still need SCCs or another Art. 46 safeguard. (Verified 2026-06-05; the DPF survived an annulment challenge dismissed by the EU General Court on 3 Sept 2025, but its durability remains politically contested — `[verify-at-use]`.)
- SCCs are **not a rubber stamp**: post-*Schrems II*, the exporter must also run a **Transfer Impact Assessment** (TIA) on whether the destination's law lets the importer actually honor the SCCs.
- The legal *interpretation* — which clauses, which TIA conclusion, whether a derogation applies — routes to legal / `regulatory-compliance` (§3). This team engineers the *capability*: knowing the data flows, the recipients, and the sub-processor chain.

## Attempts

- Tried: rely on the DPF as if it were general US adequacy. Failed on the facts — neither vendor was on the active DPF certification list, so the adequacy decision simply didn't apply to them.
- Tried: paper one set of SCCs with the direct vendor and stop there. Failed to cover the **sub-processor** in the no-adequacy fourth country — the transfer chain is only as covered as its weakest link, and the onward transfer needed its own mechanism.
- Tried (the move that worked): build a **transfer register driven by the data map** — for each flow of personal data crossing a border, record the destination country, the recipient, **the recipient's onward sub-processors and their countries**, and the **mechanism per leg** (adequacy / DPF-certified / SCCs+TIA / derogation). Where the mechanism was "DPF," **verify the recipient is actually on the certification list**; where it was "SCCs," confirm a TIA exists. The register made the gaps visible and gave legal a concrete per-leg worklist instead of a vague "are we okay on transfers?"

## Resolution

The gap was **assuming a mechanism existed** ("there's a framework") instead of **enumerating each transfer leg and its actual basis**. The DPF only helps for *certified* recipients; everything else needs SCCs+TIA or a derogation, and the **sub-processor chain** is the leg teams miss. The engineering deliverable is the transfer register keyed off the data map; the legal sufficiency of each chosen mechanism is legal's call.

**Action for the next engineer:** never accept "the US is adequate now" at face value — confirm the specific recipient's **DPF certification status** at use, treat SCCs as requiring a TIA (not a signature), and **follow the sub-processor chain to its end country**, because the onward transfer needs its own basis. Build the transfer register from the data map so every cross-border leg has a named mechanism; hand the per-leg gaps to legal/`regulatory-compliance` for the interpretation. Privacy law and adequacy/DPF status vary by jurisdiction and change — date every fact.

Cross-reference: complements the **transfer-mechanism choice** tree in [`../knowledge/dgp-transfer-mechanism-decision-tree.md`](../knowledge/dgp-transfer-mechanism-decision-tree.md) and the [`data-inventory`](../templates/data-inventory.md) template (the data map the register is built from).

**Sources (retrieved 2026-06-05):**
- European Commission — adequacy decision for the EU-US Data Privacy Framework (10 Jul 2023): https://ec.europa.eu/commission/presscorner/detail/en/ip_23_3721
- EDPB — EU-US Data Privacy Framework FAQ for businesses (v2.0, 2026): https://www.edpb.europa.eu/our-work-tools/our-documents/other-guidance/eu-us-data-privacy-framework-faq-european-individuals-0_en
- EU General Court dismissal of the DPF annulment action (3 Sept 2025): https://www.workforcebulletin.com/adequacy-of-the-eu-u-s-data-privacy-framework-survives-challenge

Adequacy decisions, DPF certification, and SCC/TIA requirements are jurisdiction-specific and politically volatile — `[verify-at-use]` against current EU Commission / EDPB guidance and the recipient's live certification before any deliverable.
