# Applied-statistics — best-practice docs

Named, citable rules for the `applied-statistics` plugin's `applied-statistician`. Each file is **one rule**, grounded in this plugin's knowledge bank and the agent's house opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3) or the automated smell checks in the advisory hook (§7). They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`check-assumptions-before-the-test.md`](./check-assumptions-before-the-test.md) | Absolute rule | About to report a parametric test (t-test / ANOVA / OLS) — run its assumption checks first, or take the named nonparametric fallback |
| [`effect-size-and-ci-not-bare-p.md`](./effect-size-and-ci-not-bare-p.md) | Absolute rule | Reporting any "is this difference / lift / trend real?" result — lead with effect size + 95% CI tied to the decision; the p-value is secondary, and an underpowered null is not "no effect" |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — applied-statistics team constitution (§3 house opinions, §4 anti-patterns, §6 Output Contract, §7 smell hook).
- [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) — the decision tree + assumption gate + fallback table the assumptions rule leans on.
- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — the 9-pitfall guardrail both docs cite.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs and the `_TEMPLATE.md` these follow.
