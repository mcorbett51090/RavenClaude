# Regulatory-compliance — best-practice docs

Named, citable rules for the `regulatory-compliance` plugin's specialists. Each file is **one rule**, grounded in this plugin's knowledge bank and agent opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3) or the automated PII / confidentiality checks in the pre-write hook (§7). They take one opinion each and make it a standalone, exception-documented rule.

> **This plugin produces analysis and documentation, not legal advice.** Every rule below stops at the compliance lane; legal opinions route to counsel (house opinion #10).

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`classify-severity-before-you-respond.md`](./classify-severity-before-you-respond.md) | Primary diagnostic | A regulator delivered a written finding and you are about to pick a response playbook — resolve MRA / MRIA / consent order / SII from the document's language, not its title |
| [`no-control-without-a-cite-and-evidence.md`](./no-control-without-a-cite-and-evidence.md) | Absolute rule | Writing or reviewing a control statement / walkthrough — it carries the regulator's primary-source cite, a named owner, a frequency, and a pointer to evidence it actually operates |
| [`scope-the-jurisdiction-before-you-map.md`](./scope-the-jurisdiction-before-you-map.md) | Absolute rule | Mapping a control, classifying a finding, or using a threshold word ("material") — name the regulator + regime first so no term or timeline is mis-applied across a jurisdiction boundary |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — compliance team constitution (§3 house opinions, §4 anti-patterns, §6 Output Contract, §7 PII hook).
- [`../knowledge/regulator-finding-severity-triage.md`](../knowledge/regulator-finding-severity-triage.md) — the severity tree + BMA carve-out these docs lean on.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs and the `_TEMPLATE.md` these follow.
