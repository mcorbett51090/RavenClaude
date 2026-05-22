---
name: sanctions-hit-disposition
description: Disposition framework for sanctions screening alerts — true-match vs false-positive triage, secondary-match evidence chain, escalation criteria, documented-rationale template, list-version capture, and the audit-trail requirements that survive examiner review. Reach for this skill when designing the disposition process or training analysts on hit clearance. Used by `aml-kyc-analyst` (primary).
---

# Skill: sanctions-hit-disposition

**Purpose:** A disposition is what an analyst does with a screening alert. "Cleared" vs "escalated to true-match" — and the *documented rationale* in between — is where most firms fail an examiner's sanctions-program review. This skill is the binary-disposition framework house opinion #8 demands. Used by `aml-kyc-analyst` (primary).

## When to use

- Designing or refreshing the firm's hit-disposition procedure
- Training analysts on hit clearance discipline
- Sampling cleared dispositions for QC / second-line monitoring
- Pre-exam sanctions-program review (examiners *will* request a cleared-hit sample)
- After a near-miss or true-match incident — root-cause the disposition process

## House opinion #8 in three words

**Cleared or escalated.** Every alert ends in one of two states, with a documented rationale, a named clearer, and a captured list-version. "Looks fine" is not a disposition. "Probably a false positive" is not a disposition. A blank disposition field is not a disposition.

## Lists in scope

The firm's screening universe should be declared in writing, with each list's source and refresh cadence. Typical:

| List | Source | Cadence | Notes |
|---|---|---|---|
| **OFAC SDN** | US Treasury — Office of Foreign Assets Control | Daily; OFAC publishes list changes intra-day for material updates | The single most-examined list |
| **OFAC CAPTA / sectoral / non-SDN consolidated** | US Treasury | Daily | Sectoral sanctions (SSI, NS-PLC, etc.) often missed |
| **EU consolidated financial sanctions list** | EU Council | Daily | Refresh on amendment publication |
| **UK OFSI consolidated list** | HM Treasury — Office of Financial Sanctions Implementation | Daily | Mandatory for UK-nexus customers |
| **UN Security Council Consolidated List** | UN | On amendment | Baseline for all firms; jurisdictionally adopted |
| **Bermuda — MFAA (Money Laundering and Financial Assistance Act)** | Bermuda Government / BMA | On amendment | Local-law triggers under Bermuda's sanctions regime |
| **Local PEP lists** | Vendor + local sources | Per cadence agreed with vendor | Distinguish PEP screening from sanctions screening — different purpose |
| **Adverse-media lists** | Vendor-curated | Continuous | Same hygiene applies: rationale on every hit |

The customer (and every beneficial owner / agent / counterparty in fan-out screening) must be screened against the *full* in-scope set, not just one. A common audit finding is "customer screened only against the SDN; sectoral lists missed."

## Match strength — the dimensions

A screening hit fires on a name match (usually fuzzy). Disposition strength comes from secondary data:

| Dimension | Strong evidence | Weak evidence |
|---|---|---|
| **Full name match** | Exact match, including middle name, full transliteration | Surname + initial; transliteration variant |
| **Date of birth** | Exact match on full DOB | Year only; nearby year |
| **Nationality / citizenship** | Multiple matched nationalities | Single nationality; unmatched |
| **National ID / passport** | Exact match | Format match but different number |
| **Address / known location** | Sanctioned-party's last known address matches | Same country only |
| **Affiliation / role** | Confirmed role at sanctioned entity | Reportedly associated |
| **Photo / biometric** | Visual match against published photo | None available |

A typical disposition uses several dimensions. **The match-quality tier comes from the combination of dimensions, not the name-match score alone.**

## Match-quality tiers — recommended firm standard

| Tier | Definition | Default disposition |
|---|---|---|
| **Exact** | Full name + DOB + at least one ID document or address match | Escalate as true-match; route to AML Officer + counsel + senior management; freeze pending guidance |
| **Strong** | Full name + DOB match, or full name + multiple corroborating dimensions | Escalate; document investigation steps; possible true-match |
| **Partial** | Name match + 1 corroborating dimension (often nationality or address country only) | Investigate; document why cleared or escalated; require checker sign-off |
| **Weak** | Name-only match; no corroborating dimensions; common name | Cleared with documented rationale; analyst-level sign-off |

The tier is a starting point, not a conclusion. Document the dimensions actually checked, not just the tier assigned.

## False-positive vs true-hit logic

A hit is a **false positive** when, after due investigation, the matched profile is **not** the sanctioned person. Document:

- Which name dimensions did NOT match (and the alternative-name analysis if names were similar but not identical)
- Which secondary dimensions confirmed a different person (different DOB, different nationality, different ID, different address)
- The sources consulted (open-source, customer-provided documents, internal KYC file)
- The screening-tool match score (for the audit trail, not as the decision)
- The screening list version date at the moment of the disposition
- The named clearer + their role + the timestamp

A hit is a **true match** (or possible true match — the standard sanctions framework treats "reason to believe" as actionable) when the dimensions point to the sanctioned party. Escalate **immediately**:

- Do not contact the customer ("tipping"-equivalent issues apply)
- Do not move the funds in either direction without senior-management + AML Officer sign-off
- Engage counsel for any onward action
- File the required report (OFAC blocking / rejected-transaction report, EU equivalent, local equivalent) within the statutory window
- Lock the customer record from further outgoing activity pending resolution

## Escalation thresholds — written, not implicit

The firm's procedure should specify, in writing:

- Which tier triggers which escalation level (analyst → senior analyst → AML Officer → senior management + counsel)
- Time limits per tier (e.g., Strong-tier hits escalated within 4 hours; Exact within 1 hour)
- Out-of-hours escalation path (on-call AML Officer; backup approver)
- The reporting-line if the AML Officer is the subject of a personal hit (independent escalation path; common gap)

## What evidence to capture — the audit trail

A cleared hit's audit trail should survive examiner review without further explanation. Capture:

1. **Alert ID** — from the screening tool
2. **List in scope** — which list(s) produced the hit; specific entry / SDN number
3. **List version date** — the date of the list version against which the screening ran (this is the single most-missed item)
4. **Customer / party screened** — customer ID, role (customer / UBO / agent / counterparty / beneficiary)
5. **Name-match score** — from the screening tool, captured as displayed (not editorialized)
6. **Dimensions checked** — DOB, nationality, ID, address, role, affiliation; for each, **match / mismatch / unknown** with the supporting source
7. **Sources consulted** — every external source named (corporate registry, news article, court record); links + access date
8. **Documented rationale** — narrative paragraph explaining the conclusion ("cleared as false positive because..." / "escalated as possible true-match because...")
9. **Disposition** — Cleared / Escalated (no third option)
10. **Named clearer** — analyst name + role + timestamp
11. **Checker sign-off** — required for Partial and above; named + timestamp
12. **Re-screening cadence** — when this disposition will be re-evaluated (lists change; today's false positive is tomorrow's hit)

## Documented-rationale template

```
Alert ID: <id>
List(s) in scope: <list + version date>
Party screened: <name + role + customer ID>
Tool match score: <as displayed>
Dimensions assessed:
  - Name: <match/mismatch + note>
  - DOB: <match/mismatch + source>
  - Nationality: <match/mismatch + source>
  - ID (passport/national): <match/mismatch + source>
  - Address: <match/mismatch + source>
  - Affiliation/role: <match/mismatch + source>
Sources consulted: <list with URLs + access date>
Rationale:
  <narrative paragraph — why this is cleared OR why escalated. Reference dimensions and sources by name.>
Disposition: Cleared | Escalated
Clearer: <name, role, timestamp>
Checker (where required): <name, role, timestamp>
Next re-screening: <date or trigger>
```

This rationale block is what an examiner samples. A file without one is a finding; a file with a one-word disposition is a finding; a file with rationale but no list-version date is a finding.

## Fan-out screening — what to screen beyond the customer

Common audit finding: "screened the customer; missed the beneficial owners." For a complete screening universe per customer / transaction:

- **Customer** (natural person or legal entity)
- **Each beneficial owner** above threshold (and ideally controllers below threshold for higher-risk customers)
- **Directors / senior managing officials** of legal entities
- **Authorized signatories / power-of-attorney holders**
- **Counterparties** on transactions — payee/beneficiary on outgoing wires; payor on incoming wires
- **Beneficiary bank** and **correspondent banks** on cross-border wires
- **Agents / intermediaries / introducers**
- **Vessels / cargo** in trade finance (specialized lists; ship-screening tools)
- **Crypto wallet addresses** where applicable (chain-analytics tooling)

The screening procedure should specify fan-out scope per product / channel, not leave it implicit.

## Continuous re-screening — not just at onboarding

The customer base is screened against every list update, not just at onboarding. Vendor screening tools usually handle this; verify:

- Cadence matches the list cadence (daily for OFAC/EU/UK/UN)
- New customer additions enter the screening universe immediately
- Customer attribute updates (new DOB, new nationality, address change) trigger re-screening
- A retired/closed customer's records remain in scope for the regulator-required retention window
- Vendor-list-cadence reports are reviewed monthly; gaps in list-update receipt are findings

## Common findings on examination

- Cleared hits with no documented rationale — just a status flag
- List-version date not captured on disposition
- Customer screened; beneficial owners not screened
- Sectoral / non-SDN OFAC lists not in scope
- "Escalated" sitting in a queue for weeks with no decision
- Same analyst as maker and checker on Strong-tier dispositions
- "Common name" used as a one-line rationale with no analysis of why
- Adverse-media hits routed through the same disposition process as sanctions hits with no distinction
- The AML Officer never sampled the cleared-hit population
- A true-match handled procedurally without filing the required blocking/rejected-transaction report

## Anti-patterns

- A free-text disposition with no structured fields — examiners can't sample what they can't tabulate
- Bulk-cleared screening alerts (one disposition record per batch, not per alert)
- Disposition completed by a person who reports to the relationship manager who onboarded the customer
- Quality assurance done by the same team that did the disposition
- Vendor scoring trusted as the disposition (the score is a *starting point*, not the answer)
- Re-screening cadence "annual" — the lists update daily

## See also

- Skill: [`./kyc-edd-review.md`](./kyc-edd-review.md)
- Skill: [`./aml-program-review.md`](./aml-program-review.md)
- Skill: [`./sar-narrative-drafting.md`](./sar-narrative-drafting.md)
- Skill: [`./control-testing.md`](./control-testing.md)
- Template: [`../templates/kyc-edd-workpaper.md`](../templates/kyc-edd-workpaper.md)
- Agent: [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md)
