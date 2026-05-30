# Every PBC item ships with its evidence pack — "complete" with nothing attached is not complete

**Status:** Absolute rule
**Domain:** Examination readiness — evidence packs
**Applies to:** `regulatory-compliance`

---

## Why this exists

A regulator examination is won or lost on whether each request can be answered with the *evidence*, not the assertion. The recurring failure is a PBC (provided-by-client / prepared-by-client) tracker where items are marked "complete" but nothing is attached, or where what's attached is the policy when the examiner asked for proof the policy is followed. Regulators want a specific stack, in order: the **policy**, the **procedure**, the **evidence the procedure is followed**, the **management reporting**, and the **board/committee minutes that show oversight** — plus the **data that supports specific assertions**. A PBC item that produces only the top of that stack (a policy) when the examiner is testing the middle (operating evidence) is the same gap as a control with no evidence, surfacing at the worst possible moment. Every information request is also an audit trail in its own right: what was asked, when, what was sent, by whom, when.

## How to apply

For each PBC item, attach the full evidence stack and log the request as an audited transaction:

```
PBC item          the request, in the examiner's words
Policy            the governing policy (cite the regulator's section it implements)  [verify-at-build]
Procedure         the procedure that operationalizes it
OPERATING EVIDENCE the proof the procedure is FOLLOWED (logs, sign-offs, dispositions) — the load-bearing layer
Management reporting the MI that shows the control is monitored
Oversight          board/committee minutes evidencing oversight
Supporting data    the data behind any specific assertion
Audit trail        date received · date answered · what was sent · who signed · second pair of eyes (not the team examined)
```

Rehearse the walkthrough against *actual practice*, not the policy text — the rehearsal exists to find the policy/practice gap and fix it before fieldwork, not to perform a clean script.

**Do:**
- Attach operating evidence to every PBC item — the proof the procedure is followed, not just the policy that says it should be.
- Log every information request as an audit trail (asked/answered/sent/signed) with a second pair of eyes outside the examined team.
- Rehearse walkthroughs against what people actually do; fix the gaps before fieldwork.

**Don't:**
- Mark a PBC item "complete" with no evidence attached — that is a flagged anti-pattern and an opening for the examiner.
- Send the policy when the request is for operating evidence.
- Volunteer unrequested issues *or* visibly withhold — answer the question asked, fully; pattern-of-evasion is the worst possible finding.

## Edge cases / when the rule does NOT apply

- **Genuinely new controls** with no operating history yet can't show period evidence — disclose the go-live date and the interim assurance honestly, rather than presenting an empty "complete."
- **BMA / Bermuda exams** use different vocabulary and request shapes — route to `bermuda-insurance-specialist` for the BMA-specific PBC and filing-history expectations before applying a US exam posture.
- **Privileged material** in a response routes through counsel and the `Legal-advice gate:` flips; the operational evidence pack continues for the non-privileged items.

## See also

- [`./classify-severity-before-you-respond.md`](./classify-severity-before-you-respond.md) — when a finding lands, classify severity before the response playbook.
- [`./no-control-without-a-cite-and-evidence.md`](./no-control-without-a-cite-and-evidence.md) — the same evidence-over-assertion discipline, control-side.
- [`./records-retention-on-a-schedule-not-on-disposal-instinct.md`](./records-retention-on-a-schedule-not-on-disposal-instinct.md) — the evidence has to still exist when the exam asks for it.
- [`../agents/examination-prep-specialist.md`](../agents/examination-prep-specialist.md) — "Walkthroughs reflect actual practice, not the policy"; "Every information request gets an audit trail."

## Provenance

Codifies the `examination-prep-specialist` opinions "Walkthroughs reflect actual practice, not the policy," "Every information request gets an audit trail," "Don't volunteer / Don't withhold either," and the PBC surface-area note that "regulators want the policies, the procedures, the evidence the procedures are followed, the management reporting, and the board/committee minutes" ([`../agents/examination-prep-specialist.md`](../agents/examination-prep-specialist.md)), plus the `examination-readiness` skill in [`../CLAUDE.md`](../CLAUDE.md) §8.

---

_Last reviewed: 2026-05-30 by `claude`_
