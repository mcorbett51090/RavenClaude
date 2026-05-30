# Lead with the effect size and CI — the p-value is secondary

**Status:** Absolute rule
**Domain:** Result communication / significance vs importance
**Applies to:** `applied-statistics`

---

## Why this exists

A bare p-value answers "is this distinguishable from chance?" — it does not answer "is it big enough to matter to the decision?" On large n, a trivially small effect is "highly significant"; on small n, a real effect can miss the α=0.05 cut and be dismissed as "no effect." Both are failure modes this plugin exists to prevent. The deliverable is the **interval, not the point** (house opinion #2): the effect size with its 95% confidence interval as the headline, the p-value secondary. Significance is not importance (house opinion #3 / pitfall #6). And an underpowered null is not "no effect" (pitfall #8) — "absence of evidence is not evidence of absence," so a non-significant result ships with the CI and the minimum detectable effect (MDE) the study could actually have caught.

## How to apply

Lead every result with effect size + CI tied to the business decision; relegate p to support. State the magnitude in units the stakeholder can act on:

```
Result:  +4.2% conversion lift  (95% CI: +1.1% to +7.3%),  Cohen's d ≈ 0.18,  p = 0.011
Verdict: lift is real AND clears the +2% decision threshold the team set -> ship.

Underpowered case:
Result:  −0.8% (95% CI: −5.1% to +3.5%), p = 0.71
Verdict: NOT "no effect" — the CI spans effects large enough to matter; the study could only
         detect an MDE of ~5%. State the CI + MDE; recommend a larger sample, don't declare null.
```

Put the effect size + CI as the headline on the Output Contract's `Result:` line, and screen pitfall #6 (significance ≠ effect) and #8 (underpowered null) on the `Pitfall screen:` line.

**Do:**
- Lead with the effect size and its 95% CI; state the p-value after, not instead.
- Tie the magnitude to the decision threshold ("is +4% enough to matter to this launch?").
- For a non-significant result, give the CI and the MDE the design could detect — never call it "no effect."

**Don't:**
- Give a bare p-value with no magnitude, or call something "highly significant" on huge n without checking whether the effect is trivial.
- Treat p < 0.05 as the finding; the finding is the effect and its uncertainty.
- Read a single result in isolation when many tests were run — correct for multiplicity (FWER for confirmatory, FDR for exploratory) before calling any one "significant."

## Edge cases / when the rule does NOT apply

- **Pure go/no-go gates with a pre-registered single primary metric and a fixed threshold** still carry the effect + CI — the CI is what tells you whether you cleared the threshold with room to spare or by a hair.
- **Equivalence / non-inferiority tests** invert the logic (you're arguing the effect is *within* a margin), but the rule holds in spirit: the deliverable is still the interval against the margin, not a bare p.
- **Screening / exploratory passes** over many features legitimately surface candidates by significance — but flag them as exploratory, correct with FDR (Benjamini-Hochberg), and never present a screened hit as a confirmed effect without follow-up.

## See also

- [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) — pitfall #6 (significance ≠ effect size), #8 (underpowered study), and the FWER-vs-FDR multiple-comparisons guidance.
- [`./check-assumptions-before-the-test.md`](./check-assumptions-before-the-test.md) — the companion rule that makes the test valid before you quote its effect.
- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — "effect size + CI as the headline; the p-value is secondary".
- [`../templates/statistical-report.md`](../templates/statistical-report.md) — the write-up shape: plain-language bottom line + effect size & CI + caveats.

## Provenance

Codifies house opinions #2 ("the deliverable is the interval, not the point"), #3 ("significance ≠ importance"), and #6 ("an underpowered null is not 'no effect'") in [`../CLAUDE.md`](../CLAUDE.md) §3, and pitfalls #6 and #8 in [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md) (last reviewed 2026-05-26; Tier 1 / consensus). The advisory hook [`../hooks/flag-statistical-smells.sh`](../hooks/flag-statistical-smells.sh) flags a p-value with no nearby effect size or CI.

---

_Last reviewed: 2026-05-30 by `claude`_
