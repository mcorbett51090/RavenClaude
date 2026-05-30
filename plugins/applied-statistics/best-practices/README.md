# Applied-statistics — best-practice docs

Named, citable rules for the `applied-statistics` plugin's `applied-statistician`. Each file is **one rule**, grounded in this plugin's knowledge bank and the agent's house opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3) or the automated smell checks in the advisory hook (§7). They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

_16 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`causal-correlation-is-not-causation.md`](./causal-correlation-is-not-causation.md) | Absolute rule | A regression coefficient, a correlation, or an A/B difference *without randomization* tells you that X and Y move together — not that intervening on X… |
| [`causal-pick-the-identification-strategy.md`](./causal-pick-the-identification-strategy.md) | Pattern (strong default; deviate only with a written reason) | When a causal claim is warranted (the causal-verb check passed) but you can't run a clean A/B test, the answer is not "a richer regression" — it's a *… |
| [`causal-watch-confounders-and-colliders.md`](./causal-watch-confounders-and-colliders.md) | Primary diagnostic (when an "effect of X" estimate looks off, check what was controlled for) | "Control for everything you can measure" is a folk rule that is actively wrong. |
| [`check-assumptions-before-the-test.md`](./check-assumptions-before-the-test.md) | Absolute rule | A parametric test handed over with no assumption check is a result you cannot defend. |
| [`data-handle-missingness-by-its-mechanism.md`](./data-handle-missingness-by-its-mechanism.md) | Primary diagnostic (when a result depends on which rows survived, check how missingness was handled) | The two reflex moves for missing data — **listwise deletion** (drop any row with a gap) and **mean/mode imputation** (fill the gap with the column ave… |
| [`design-power-and-sample-size-before-collecting.md`](./design-power-and-sample-size-before-collecting.md) | Absolute rule | Sample size is a design decision, not an analysis decision. |
| [`design-pre-register-to-avoid-p-hacking.md`](./design-pre-register-to-avoid-p-hacking.md) | Pattern (strong default; deviate only with a written reason) | Most "false discoveries" aren't fraud — they're **researcher degrees of freedom** exercised after seeing the data: trying a few subgroups, a few cutof… |
| [`effect-size-and-ci-not-bare-p.md`](./effect-size-and-ci-not-bare-p.md) | Absolute rule | A bare p-value answers "is this distinguishable from chance?" — it does not answer "is it big enough to matter to the decision?" On large n, a trivial… |
| [`regression-pick-the-model-family.md`](./regression-pick-the-model-family.md) | Absolute rule | Linear regression (OLS) is the reflex, and for a continuous, roughly-symmetric outcome it is right. |
| [`regression-run-the-diagnostics-before-trusting-coefficients.md`](./regression-run-the-diagnostics-before-trusting-coefficients.md) | Absolute rule | An OLS fit always returns coefficients, standard errors, p-values, and an R² — whether or not its assumptions hold. |
| [`report-communicate-uncertainty-to-non-statisticians.md`](./report-communicate-uncertainty-to-non-statisticians.md) | Pattern (strong default; deviate only with a written reason) | The plugin's value is judgment under uncertainty *made defensible to a non-statistician* (the agent's mission). |
| [`test-correct-for-multiple-comparisons.md`](./test-correct-for-multiple-comparisons.md) | Absolute rule | Run twenty independent tests at α=0.05 and you expect roughly one "significant" result by chance alone, even when nothing is real (pitfall #2). |
| [`test-distinguish-signal-from-noise-on-dashboard-metrics.md`](./test-distinguish-signal-from-noise-on-dashboard-metrics.md) | Absolute rule | "Revenue is up 18% — is that real?" is a different question from "is revenue up 18%?". |
| [`test-match-the-test-to-the-data-type.md`](./test-match-the-test-to-the-data-type.md) | Absolute rule | The wrong test on the right data is as broken as the right test on the wrong data. |
| [`test-use-the-nonparametric-fallback-when-the-gate-fails.md`](./test-use-the-nonparametric-fallback-when-the-gate-fails.md) | Pattern (strong default; deviate only with a written reason) | Every parametric test has a distribution-free counterpart, and the whole point of the assumption gate is that the fallback is chosen *before* a result… |
| [`timeseries-test-stationarity-and-autocorrelation.md`](./timeseries-test-stationarity-and-autocorrelation.md) | Absolute rule | Time-ordered data violates the independence assumption that almost every standard test and regression rests on, and the violation is invisible in the … |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — applied-statistics team constitution (§3 house opinions, §4 anti-patterns, §6 Output Contract, §7 smell hook).
- [`../knowledge/test-selection-decision-tree.md`](../knowledge/test-selection-decision-tree.md) — the decision tree + assumption gate + fallback table the assumptions rule leans on.
- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — the 9-pitfall guardrail both docs cite.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs and the `_TEMPLATE.md` these follow.
