# A SAR/STR narrative answers *why* it looks suspicious — name the typology, not the transaction

**Status:** Absolute rule
**Domain:** AML / KYC — suspicious-activity reporting
**Applies to:** `regulatory-compliance`

---

## Why this exists

A SAR/STR narrative that names the customer and recites the transaction — "Customer wired $X to Y on date Z" — tells the financial-intelligence unit *what* happened but not *why* it was reported. The reporting standard is the *why*: the typology (layering, structuring, trade-based laundering, funnel account, third-party funding via a high-risk jurisdiction) and the facts that make the activity inconsistent with the customer's known profile and expected activity. A narrative without the typology is a transaction log; the FIU cannot triage it, and at the next exam the firm cannot show it understood its own filing. The discipline is the five W's plus the typology plus an explicit note of what was deliberately omitted and why.

## How to apply

Draft to the W's, lead with the typology, and record the sign-off chain:

```
Who      subject(s) + role in the pattern (sender, receiver, intermediary, beneficial owner)
What     the activity, in amounts and instruments
When     the timeframe; flag continuing activity for a continuing-activity report
Where    accounts, jurisdictions, channels — name the high-risk geography if one is in play
Why      THE TYPOLOGY: why this is inconsistent with expected activity / known profile
Omit     state what was left out and the basis (e.g. unverified rumor, privileged material)
Sign-off preparer -> reviewer -> filer, each recorded
```

**Do:**
- Name the typology in plain terms — "appears to be layering across three related shell entities".
- File a continuing-activity report when a known pattern continues — don't let a live typology go un-refreshed.
- Default `Confidentiality: regulator-only`; SAR/STR drafts never leave the working directory unencrypted (constitution §2, §7).

**Don't:**
- Write "the transaction looks suspicious" — that is a conclusion, not a narrative.
- Editorialize beyond the facts or speculate about intent the evidence doesn't support.
- Commit any real customer PII — the pre-write hook flags these; for SAR work flip the hook to blocking (§7).

## Edge cases / when the rule does NOT apply

- **No-file decisions** are still documented — a rationale-to-not-file is itself a record an examiner may ask for.
- **Defensive filing** ("file it to be safe" without an articulable typology) is a smell, not a strategy — if you cannot name the *why*, re-examine whether the threshold to report is actually met.
- **Tipping-off** — the existence/content of a SAR is confidential; never disclose to the subject. Any disclosure question routes to counsel.

## See also

- [`./aml-reportability-before-you-file.md`](./aml-reportability-before-you-file.md) — deciding *whether* to file before you draft.
- [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md) — `## Decision Tree: Is this reportable — SAR, threshold report, or none`.
- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — "SAR/STR narratives answer *why*"; the `sar-narrative-drafting` skill.

## Provenance

Codifies the `aml-kyc-analyst` opinion "SAR/STR narratives answer *why*" ([`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md)), constitution anti-pattern "a SAR/STR narrative that names the customer without explaining the typology", and the §2 routing rule that SAR/STR drafts stay encrypted in-directory in [`../CLAUDE.md`](../CLAUDE.md).

---

_Last reviewed: 2026-05-30 by `claude`_
