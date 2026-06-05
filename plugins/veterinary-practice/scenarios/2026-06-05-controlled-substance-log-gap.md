---
scenario_id: 2026-06-05-controlled-substance-log-gap
contributed_at: 2026-06-05
plugin: veterinary-practice
product: clinical-compliance
product_version: "n/a"
scope: likely-general
tags: [dea, controlled-substance, biennial-inventory, compliance, aaha]
confidence: medium
reviewed: false
---

## Problem

During a pre-acquisition operational review, a 2-DVM practice could not produce a defensible controlled-substance audit trail. They logged Schedule II administrations in a paper notebook, had no separate opened/unopened container logs, and could not locate any record of a biennial inventory. The owner believed "we write everything down" was sufficient. A DEA inspection (or an acquirer's diligence) would have flagged this immediately — and **clinical-protocol-specialist** must frame this as decision-support, never as legal advice (CLAUDE.md §2).

## Context

- Segment: general-practice, independent, single DEA registration.
- Constraint: this is a **regulatory recordkeeping** gap, not a diversion finding — but the inability to reconcile is exactly what turns an inspection into a problem. The plugin does not store records or issue treatment orders; it standardizes the *practice's* logging discipline as decision-support for the licensed DVM/DEA registrant.
- The team confused "we have notes" with "we have reconcilable, retention-compliant records."

## Attempts

- Tried: mapped current practice against the AAHA controlled-substance log structure. Identified the missing pieces: (1) a per-drug log for each Schedule II–V substance, (2) separate **unopened** and **opened** container logs, (3) an **Authorized Personnel** log, (4) an **Initial + Biennial Inventory** record. Outcome: gap list, not a fix yet.
- Tried: confirmed the two recordkeeping anchors against authoritative sources rather than memory — (a) after the initial inventory, a **new complete inventory every two years (biennial)** is required; (b) DEA requires controlled-substance records be **retained at least two years** for inspection, **and many states require longer (up to five years or more)** — so the retention rule is the stricter of federal and the practice's state. Outcome: grounded the two volatile facts that gate the recommendation.
- Tried (the move that worked): recommended the practice adopt the **AAHA Controlled Substance Logs** set (built to meet DEA recordkeeping across all 50 states + Canada) as the standardized log structure, plus a written SOP for daily reconciliation and a calendared biennial-inventory date. Outcome: a defensible, reconcilable trail and a named owner + recurring date.

## Resolution

The gap was **structure and reconciliation discipline**, not effort — paper notes don't satisfy DEA recordkeeping. Standardizing on a DEA-reviewed log set (per-drug + opened/unopened + authorized-personnel + initial/biennial inventory) with a written reconciliation SOP and a calendared biennial inventory closed it.

**Action for the next consultant hitting this pattern:** confirm the **state** retention period (federal floor is 2 years; several states are longer — verify the specific state board rule at use), confirm a **biennial** inventory is on the calendar with a named owner, and check that **opened vs unopened** containers are logged separately. Frame every output as decision-support for the licensed DEA registrant — this plugin is not a licensing authority and issues no legal advice (CLAUDE.md §2). Route anything touching diversion, PII, or regulated records to `ravenclaude-core` `security-reviewer`.

**Sources (retrieved 2026-06-05):**
- AAHA Controlled Substance Logs Resources & FAQs — https://www.aaha.org/resources/aahas-controlled-substance-logs-resources/ and https://www.aaha.org/resources/aahas-controlled-substance-logs-resources/additional-resources-for-controlled-substance-logs/controlled-substance-faqs/
- AAHA DEA compliance — https://www.aaha.org/resources/compliance/

These are public benchmark/standards sources; DEA and state-board rules are volatile — `[verify-at-use]` against the current regulation and the practice's specific state board before any deliverable.
