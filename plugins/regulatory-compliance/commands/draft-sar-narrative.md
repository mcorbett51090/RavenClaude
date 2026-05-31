---
description: "Decide reportability then draft a SAR/STR that survives regulator review — classify suspicion-based vs threshold-based vs no-report first, draft the narrative to the W's leading with the typology (the why), record the maker-reviewer-filer chain, and document a no-file decision when nothing fires."
argument-hint: "[the activity, e.g. 'a structuring pattern flagged at a mid-sized bank']"
---

# Draft a SAR / STR narrative

You are running `/regulatory-compliance:draft-sar-narrative`. Triage and draft the suspicious-activity report for the activity the user described (`$ARGUMENTS`), following this plugin's `aml-kyc-analyst` discipline. A narrative that names the customer and recites the transaction is a transaction log; the reporting standard is the *why*.

## When to use this

A transaction-monitoring alert, a referral, or an EDD finding needs a reportability decision and, where warranted, a filed narrative. Not for a sanctions-hit disposition (clear/escalate — that's the KYC review) and not for the legal question of whether a disclosure obligation is triggered in a genuinely ambiguous case (route to counsel).

## Steps

1. **Decide reportability before you draft** (`aml-reportability-before-you-file`): classify the obligation first — articulable suspicion → SAR/STR; crosses a value/cash threshold with no suspicion → threshold report only; both → file both; neither → no report (and document why). Thresholds and report families are jurisdiction-specific — confirm the regime's current amounts before relying on a number.
2. **Draft the narrative to the W's, leading with the typology** (`aml-sar-narrative-answers-why`): Who (role in the pattern), What (amounts + instruments), When (flag continuing activity), Where (accounts, jurisdictions, channels), and **Why** — the typology (layering, structuring, funnel account, trade-based, third-party funding via a high-risk jurisdiction) and why it is inconsistent with the customer's known profile. Note what was deliberately omitted and the basis.
3. **Record the sign-off chain** (`aml-sar-narrative-answers-why`): preparer → reviewer → filer, each recorded; file a continuing-activity report when a known pattern continues.
4. **Document the no-file decision when nothing fires** (`aml-document-the-no-file-decision`): a decision-not-to-report is itself a record an examiner is entitled to see — name the trigger, the typology considered (even when rejecting it), the decision, the basis, and the author/date.
5. **Treat defensive filing as a smell** (`aml-document-the-no-file-decision`): if you cannot name the *why*, the honest output is a documented no-file, not a hollow SAR.

## Guardrails

- SAR/STR work is `regulator-only` confidentiality — drafts never leave the working directory unencrypted; for SAR drafting, flip the PII-scrub hook to blocking and never commit real customer PII.
- Tipping-off: the existence and content of a SAR are confidential — never disclose to the subject; any disclosure question routes to counsel.
- Don't write "the transaction looks suspicious" (a conclusion, not a narrative) or editorialize beyond the facts; route PII handling through `ravenclaude-core/security-reviewer`.
