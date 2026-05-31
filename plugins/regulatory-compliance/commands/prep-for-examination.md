---
description: Prep for a regulator examination the way it is actually tested — scope the regime first, attach the full evidence stack (policy→procedure→operating evidence→MI→minutes) to every PBC item, rehearse walkthroughs against actual practice, classify any finding's severity before responding, and track remediation with an independent tester.
argument-hint: "[the exam + regime, e.g. 'a BMA exam for a Bermuda insurer' or 'post-exam remediation']"
---

# Prep for an examination

You are running `/regulatory-compliance:prep-for-examination`. Prepare for (or respond to) the examination the user described (`$ARGUMENTS`), following this plugin's `examination-prep-specialist` discipline. An exam is won or lost on whether each request is answered with the evidence, not the assertion.

## When to use this

An upcoming regulator exam, PBC/walkthrough preparation, or post-exam remediation planning. Not for internal-audit or second-line control-test findings (the severity tree is for regulator-written findings only) and not for consent-order / enforcement matters where counsel leads.

## Steps

1. **Scope the jurisdiction and regime first** (`scope-the-jurisdiction-before-you-map`): a BMA/Bermuda exam uses different vocabulary and request shapes than a US exam — route to `bermuda-insurance-specialist` before applying any US-anchored posture or severity ladder.
2. **Attach the full evidence stack to every PBC item** (`exam-evidence-on-every-pbc-item`): policy → procedure → **operating evidence the procedure is followed** (the load-bearing layer) → management reporting → board/committee minutes → supporting data. Mark an item "complete" only with evidence attached; sending the policy when the request is for operating evidence is the classic gap. Log every request as an audit trail (asked/answered/sent/signed, second pair of eyes outside the examined team).
3. **Rehearse walkthroughs against actual practice** (`exam-evidence-on-every-pbc-item`): rehearse what people actually do, not the policy text — the rehearsal exists to find the policy/practice gap and fix it before fieldwork. Answer the question asked fully; don't volunteer unrequested issues and don't visibly withhold (pattern-of-evasion is the worst finding).
4. **Classify any finding's severity before you respond** (`classify-severity-before-you-respond`): traverse the severity tree on the document's *language*, not its title — consent order vs MRIA (immediate, 30-60 day, board reporting) vs MRA (90-180 day) vs self-identified issue. When a branch could go either way, default to the higher severity.
5. **Track remediation with an owner, a date, and an independent tester** (`exam-remediation-has-an-owner-date-and-independent-tester`): root-cause the finding (not the symptom), name an accountable owner and a real target date, and have the fix verified by someone other than its designer. Send the regulator a rolling update the moment a milestone slips — silence on an open past-target item is the worst posture.

## Guardrails

- "Remediation in progress" with no date or owner re-raises at the next exam; "remediated" without independent evidence it operates predictably recurs.
- A consent order or C&D is counsel-led — the legal-advice gate flips to counsel-required; privileged material in a response routes through counsel while the non-privileged evidence pack continues.
- The evidence has to still exist when the exam asks for it (records retention on a schedule); cite the regulator's primary source, and route any PII handling through `ravenclaude-core/security-reviewer`.
