# Regulatory-compliance — best-practice docs

Named, citable rules for the `regulatory-compliance` plugin's specialists. Each file is **one rule**, grounded in this plugin's knowledge bank and agent opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3) or the automated PII / confidentiality checks in the pre-write hook (§7). They take one opinion each and make it a standalone, exception-documented rule.

> **This plugin produces analysis and documentation, not legal advice.** Every rule below stops at the compliance lane; legal opinions route to counsel (house opinion #10).

---

## Index

_24 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`aml-document-the-no-file-decision.md`](./aml-document-the-no-file-decision.md) | Absolute rule | When an alert, a referral, or an EDD review resolves to *no report*, the work is not finished — the decision-not-to-file is a record an examiner is en… |
| [`aml-reportability-before-you-file.md`](./aml-reportability-before-you-file.md) | Primary diagnostic | "Reportable" is not one thing. |
| [`aml-risk-rate-before-you-choose-cdd-depth.md`](./aml-risk-rate-before-you-choose-cdd-depth.md) | Absolute rule | Due diligence depth is an **output of a risk rating**, not a starting assumption. |
| [`aml-sanctions-screening-hygiene.md`](./aml-sanctions-screening-hygiene.md) | Absolute rule | A sanctions screen is only as defensible as the list it ran against and the trail it left. |
| [`aml-sar-narrative-answers-why.md`](./aml-sar-narrative-answers-why.md) | Absolute rule | A SAR/STR narrative that names the customer and recites the transaction — "Customer wired $X to Y on date Z" — tells the financial-intelligence unit *… |
| [`aml-tune-transaction-monitoring-with-data.md`](./aml-tune-transaction-monitoring-with-data.md) | Absolute rule | Transaction-monitoring rules drift out of calibration the moment they ship and are rarely re-tuned. |
| [`bermuda-state-the-capital-regime-before-you-model.md`](./bermuda-state-the-capital-regime-before-you-model.md) | Absolute rule — modeling a Bermuda (re)insurer's capital before fixing its class and regime computes against the wrong yardstick. | The registration class drives the BMA capital framework (BSCR/ECR/MMS, EBS); it's the first decision, not a discovered input. |
| [`classify-severity-before-you-respond.md`](./classify-severity-before-you-respond.md) | Primary diagnostic | When a regulator delivers a finding, the most expensive mistake is misreading **severity** before deciding how to respond. |
| [`controls-classify-the-control-type-before-you-rate-it.md`](./controls-classify-the-control-type-before-you-rate-it.md) | Primary diagnostic | The kind of control you have determines what evidence proves it works, how its failure shows up, and how much residual risk it actually removes — yet … |
| [`controls-inherent-residual-target-are-three-ratings.md`](./controls-inherent-residual-target-are-three-ratings.md) | Absolute rule | A risk register exists to answer one question: is the firm over- or under-controlled against its appetite? |
| [`controls-one-control-one-requirement-traceable.md`](./controls-one-control-one-requirement-traceable.md) | Absolute rule | Control-to-obligation mapping breaks when a single control is stretched to "cover" a cluster of requirements, or when one requirement is silently assu… |
| [`edd-is-depth-not-document-count.md`](./edd-is-depth-not-document-count.md) | Absolute rule | The most common EDD failure is treating "enhanced" as "more documents". |
| [`exam-evidence-on-every-pbc-item.md`](./exam-evidence-on-every-pbc-item.md) | Absolute rule | A regulator examination is won or lost on whether each request can be answered with the *evidence*, not the assertion. |
| [`exam-remediation-has-an-owner-date-and-independent-tester.md`](./exam-remediation-has-an-owner-date-and-independent-tester.md) | Absolute rule | A remediation commitment without a named owner and a target date is, in the constitution's words, a finding waiting to be re-raised at the next exam —… |
| [`filing-explain-the-variance-before-you-submit.md`](./filing-explain-the-variance-before-you-submit.md) | Absolute rule | The regulator reads this period's return next to last period's — and so should the firm, before it submits. |
| [`filing-fix-the-source-not-the-return.md`](./filing-fix-the-source-not-the-return.md) | Absolute rule | When source data is wrong, the tempting shortcut is to "fix" the number in the return — an override in the workbook cell, a plug to make the schedule … |
| [`filing-maker-checker-is-two-people.md`](./filing-maker-checker-is-two-people.md) | Absolute rule | Maker-checker is the single most relied-on control over filing accuracy, and it collapses the instant the same person fills both roles. |
| [`filing-source-trace-every-load-bearing-cell.md`](./filing-source-trace-every-load-bearing-cell.md) | Absolute rule | A regulatory return is a chain of numbers, and any number a reviewer or examiner can ask about must be reproducible from its source on demand. |
| [`no-control-without-a-cite-and-evidence.md`](./no-control-without-a-cite-and-evidence.md) | Absolute rule | A control statement with no regulatory citation, or one that describes the *policy* rather than what people *actually do*, fails the moment an examine… |
| [`policy-frame-conduct-and-consumer-outcomes.md`](./policy-frame-conduct-and-consumer-outcomes.md) | Pattern | Conduct and consumer-protection regimes `[verify-at-build — e.g. |
| [`policy-separate-policy-from-procedure.md`](./policy-separate-policy-from-procedure.md) | Absolute rule | Policy and procedure answer different questions, move at different speeds, and are approved by different people — so binding them into one document gu… |
| [`records-retention-on-a-schedule-not-on-disposal-instinct.md`](./records-retention-on-a-schedule-not-on-disposal-instinct.md) | Absolute rule | Compliance evidence is only useful if it still exists when the regulator asks for it — and the firm can only prove it kept the right things for the ri… |
| [`reporting-classify-the-entity-before-you-file.md`](./reporting-classify-the-entity-before-you-file.md) | Absolute rule — filing the wrong return, or the right return on a wrong entity classification, is a reportable error; classification is the upstream decision. | FATCA/CRS entity status (FI vs active/passive NFE) decides which return is owed; the filing-hygiene rules assume it's already right. |
| [`scope-the-jurisdiction-before-you-map.md`](./scope-the-jurisdiction-before-you-map.md) | Absolute rule | The same word means different things across regulators, and the same control answers to different cites in different regimes. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — compliance team constitution (§3 house opinions, §4 anti-patterns, §6 Output Contract, §7 PII hook).
- [`../knowledge/regulator-finding-severity-triage.md`](../knowledge/regulator-finding-severity-triage.md) — the severity tree + BMA carve-out these docs lean on.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs and the `_TEMPLATE.md` these follow.
