---
name: kyc-edd-review
description: KYC file + EDD review playbook — risk-rating logic, BOI / UBO verification, source-of-wealth vs source-of-funds, EDD trigger conditions, file completeness checklist, sign-off chain. Reach for this skill when reviewing a single customer file, designing the firm's KYC standard, or training analysts. Used by `aml-kyc-analyst` (primary).
---

# Skill: kyc-edd-review

**Purpose:** Review an individual KYC file (or a sample of files) against the firm's standard and the regulator's expectations. Same playbook used in reverse to *design* the standard, or to train new analysts on what "good" looks like. Used by `aml-kyc-analyst` (primary).

## When to use

- Reviewing a single customer file before onboarding sign-off
- Sampling for periodic QC / second-line monitoring
- Designing or refreshing the firm's KYC standard
- Building EDD trigger logic for a new product / channel / geography
- Training analysts — this is the canonical "what good looks like"
- Pre-exam KYC-file sample preparation

## Frameworks in scope (cite the right one)

- **FATF Recommendation 10** (Customer Due Diligence) and Recommendation 12 (PEPs) — the global baseline.
- **US: BSA / FFIEC BSA-AML Examination Manual** — "Customer Identification Program" (CIP) and "Customer Due Diligence" sections; **FinCEN CDD Rule (31 CFR §1010.230)** for beneficial-ownership requirements.
- **Bermuda: AMLR 2008** — regulations 6–11 (CDD / EDD / source-of-funds / PEPs / reliance).
- **EU: 4AMLD / 5AMLD / 6AMLD** — implemented locally; check the transposing national rule.
- **UK: MLR 2017 (as amended)** — regulations 27–35.

Pick the citation that governs the customer's relationship with the firm, not the one most convenient. House opinion #1: section + subsection + paragraph.

## Risk-rating logic — the five dimensions

Every customer gets an inherent risk rating at onboarding and at refresh. The dimensions:

| Dimension | What you assess | Examples of higher risk |
|---|---|---|
| **Customer type** | Natural person / legal entity / trust / fund / nominee / PEP | PEP, complex trust, nominee director arrangement |
| **Geography** | Domicile, citizenship, business activity location, source-of-funds origin | FATF-listed jurisdictions, sanctions-adjacent, secrecy havens |
| **Product / service** | What the customer is buying | Private banking, correspondent, MSB, crypto on/off-ramp, bearer instruments |
| **Channel** | How the relationship was established | Non-face-to-face, introduced (reliance), digital onboarding |
| **Delivery / activity** | Expected volume, velocity, counterparties, cash intensity | High-cash, high-velocity, frequent third-party transactions |

The output is a tier: **Low / Medium / High** (some firms use 4-tier; map). The tier drives both EDD trigger and refresh cadence (see below). Document the *weighting* of dimensions in the firm's KYC standard so analysts don't reinvent it per file.

## CDD vs EDD — the trigger conditions

**Standard CDD** applies to every customer. **EDD** is triggered (and must be documented as such) when any of the following is present:

1. **High-risk rating** from the five-dimension matrix above
2. **PEP** — domestic, foreign, or international-organization, including close associates and family members (FATF Rec. 12)
3. **High-risk geography** — FATF-listed (call-for-action or under-monitoring), or sanctions-adjacent jurisdictions
4. **Higher-risk products** — private banking, correspondent banking, trade finance with red-flag counterparties, crypto on/off-ramp
5. **Non-face-to-face onboarding** without compensating digital-identity controls
6. **Complex / opaque ownership** — multi-layer entities, nominee arrangements, bearer-share jurisdictions
7. **Adverse media** or **negative sanctions screening secondary match** that didn't escalate to true-hit
8. **Reliance** on a third party for CDD components (introducer banks, regulated intermediaries)
9. **Trigger event during the relationship** — material change in activity, change of beneficial ownership, new red flag

**EDD is not "CDD with more pages."** EDD adds *new content*: senior-management approval (named, dated), enhanced source-of-wealth (not just source-of-funds), enhanced ongoing monitoring with documented frequency, and richer adverse-media / open-source review with primary-source citations.

## BOI / UBO verification — the most-fudged step

Beneficial ownership identification (BOI) / ultimate beneficial owner (UBO) verification is where most KYC files quietly fail.

**Threshold:** the FATF baseline is **25% ownership or control** (FATF Rec. 10 + 24). Some regimes (e.g., 5AMLD post-amendment, certain sectoral rules) push it lower for higher-risk situations. **Always confirm the applicable threshold in writing.**

**Acceptable verification methods, in order of strength:**

1. **Corporate registry extract** from an authoritative public source (Companies House, BMA registers, equivalents) — dated within an acceptable window (typically 3 months).
2. **Notarized / apostilled ownership certificate** from the corporate secretary or registered agent.
3. **Audited financial statements** showing the ownership structure on a related-party note.
4. **Beneficial-ownership register** filing from the entity's jurisdiction (where one exists — UK PSC, Bermuda's central register for designated entities, etc.).
5. **Customer attestation** of UBO — **acceptable only as a supporting document, never as the sole source for higher-risk customers.** A signed UBO attestation alone is not BOI verification.
6. **Independent investigation** — corporate-research vendor reports, public-records aggregators — used as cross-check, not primary source.

**The chain must terminate in natural persons.** A UBO of "ABC Holdings Limited" is not a UBO. Trace until you reach humans or document why you can't (publicly listed parent above a certain threshold, regulated fund with disclosed structure, etc. — and even then, document the stop-condition).

**Sanctions-screen the beneficial owners individually** — not just the legal entity. This is a common audit finding (see also `sanctions-hit-disposition`).

## Source of wealth vs source of funds — the most-confused topic

These are different. The standard analyst confusion: they collect "source of funds" and treat the file as complete.

| | Source of funds (SoF) | Source of wealth (SoW) |
|---|---|---|
| **Question answered** | Where did this specific transaction / deposit come from? | How did the customer accumulate their overall wealth? |
| **Time horizon** | Immediate (this wire, this deposit) | Lifetime / multi-decade |
| **Evidence** | Bank statement, contract, settlement statement, sale agreement | Career history, business sale documentation, inheritance documents, investment-return history |
| **When required** | Always (CDD) | EDD / higher-risk customers, PEPs |
| **Failure mode** | "Salary" with no employer evidence | "Family wealth" with no documentation of how the family acquired it |

For PEPs and high-risk customers, **SoW must be plausible relative to the customer's profile and activity.** A 28-year-old PEP with $50M in cumulative deposits whose declared SoW is "salary" fails on plausibility before evidence is even considered.

## Periodic refresh cadence by risk tier

The refresh cadence should be in the firm's KYC standard, documented, and enforced (not aspirational). Typical:

| Tier | Refresh cadence | Trigger-event refresh? |
|---|---|---|
| Low | Every 3 years | Yes, on any material change |
| Medium | Every 2 years | Yes |
| High / PEP | Every year | Yes, plus enhanced ongoing monitoring throughout |

Trigger events that force refresh regardless of cadence: change of beneficial ownership, change of activity pattern (TM alerts), adverse media, sanctions list update affecting the customer, regulator request, related-party SAR.

## File completeness checklist

For every file, all present + dated + signed:

- [ ] Customer identification documents (government-issued ID, certified where required)
- [ ] Proof of address (within acceptable age — typically 3 months)
- [ ] Entity organizational documents (where applicable): certificate of incorporation, memorandum & articles, certificate of good standing
- [ ] BOI / UBO documentation per the chain above, terminating in natural persons
- [ ] Sanctions screening — customer + every UBO + relevant counterparties — with list version date and cleared / escalated disposition for every hit
- [ ] PEP screening — customer + immediate family + close associates
- [ ] Adverse-media screening with documented rationale on hits
- [ ] Source-of-funds documentation
- [ ] Source-of-wealth documentation (for EDD / PEP / high-risk)
- [ ] Risk-rating worksheet: dimensions assessed, rating recorded, rationale
- [ ] EDD memorandum (where EDD triggered): senior-management approval, enhanced monitoring plan, documented trigger
- [ ] Maker-checker sign-off: analyst (maker) + reviewer (checker), both named and dated
- [ ] Senior-management approval where required (PEPs, correspondent, certain EDD cases)
- [ ] Next refresh date recorded and ticklered

## Sign-off chain

- **Maker** (analyst) — collects, verifies, drafts risk-rating + recommendation.
- **Checker** (independent reviewer, typically a senior in same team) — verifies completeness and the rating logic.
- **Approver** — for higher-risk / EDD / PEP cases: the AML Officer or senior-management designate; named and dated approval in the file.
- **Escalation override** — any reviewer can escalate up; document the dissent and the resolution.

House opinion #6: default to written. A verbal "yeah, file looks fine" sign-off does not exist.

## Common findings on review

- BOI chain terminates at a legal entity ("XYZ Holdings owns 100%") with no natural person identified or documented stop-condition
- SoF documented; SoW not addressed at all for a PEP file
- Sanctions screening covers the customer but not the beneficial owners
- High-risk rating recorded with no rationale; or a low-risk rating that ignores a clear higher-risk dimension (geography, channel)
- EDD memo present but identical in content to a standard CDD write-up; no enhanced anything
- Periodic-refresh date set but never triggered a real refresh — the same documents from onboarding still in the file 4 years later
- Reliance on an introducer with no documented assessment of the introducer's CDD standard
- Customer attestation of UBO presented as the sole BOI source for a high-risk customer
- PEP screening present, but family-member and close-associate screening absent
- Risk-rating worksheet not present at all; rating exists only as a database field with no rationale

## Anti-patterns

- A "tick-box" file: every section has *something*, but nothing actually verifies anything
- "We trust the introducer's KYC" without a reliance assessment
- EDD package that lengthens existing CDD documents instead of adding new content
- Plausibility step skipped: SoW documented but never compared to activity
- Risk-rating logic that always lands on "Medium" — sign of a weighting that doesn't differentiate
- Periodic refresh treated as a recalculate-the-risk-rating exercise without re-verifying any of the underlying documents
- BOI verification deferred ("we'll get the registry extract later") and never closed

## See also

- Skill: [`./aml-program-review.md`](./aml-program-review.md)
- Skill: [`./sanctions-hit-disposition.md`](./sanctions-hit-disposition.md)
- Skill: [`./sar-narrative-drafting.md`](./sar-narrative-drafting.md)
- Template: [`../templates/kyc-edd-workpaper.md`](../templates/kyc-edd-workpaper.md)
- Template: [`../templates/aml-program-outline.md`](../templates/aml-program-outline.md)
- Agent: [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md)
