---
description: "Scope a sustainability disclosure: select the applicable framework(s), run the materiality test (double vs financial), fix the reporting boundary, crosswalk overlapping frameworks, and produce the disclosure roadmap."
argument-hint: "[jurisdictions + listings + size + who's asking (regulator/insurer/customer)]"
---

You are running `/esg-sustainability-reporting:scope-esg-report`. Use `esg-reporting-architect` + the `framework-selection-and-materiality` skill.

## Steps
1. Determine framework applicability per standard (CSRD/ESRS, ISSB IFRS S1/S2, GRI, SEC) by jurisdiction, listing, size, and counterparty demand. `[verify-at-build]` the effective status of each.
2. Run the correct materiality test — double materiality for CSRD/ESRS, financial for ISSB/SEC, impact for GRI. Name the governance and the evidence per material topic (a survey is not a determination).
3. Fix the reporting boundary: consolidation approach (equity share / financial / operational control) and value-chain scope; name the deltas from the financial consolidation.
4. Crosswalk the overlapping data points across the applicable frameworks so each shared figure is sourced once and disclosed against each.
5. Route: the inventory → `ghg-accounting-analyst`; drafting + assurance → `disclosure-and-assurance-lead`; the audited number → `finance`; the filing mechanic → `regulatory-compliance`.
6. Emit the materiality-assessment template + the Structured Output block (with `Framework & clause:` and `Assurance posture:`).
