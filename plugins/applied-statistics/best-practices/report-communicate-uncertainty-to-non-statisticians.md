# Report uncertainty in the stakeholder's terms — the plain-language bottom line carries the CI and the caveats

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Result communication / deliverables
**Applies to:** `applied-statistics`

---

## Why this exists

The plugin's value is judgment under uncertainty *made defensible to a non-statistician* (the agent's mission). A technically-correct result communicated as a bare p-value, a naked point estimate, or an undated vendor claim fails the engagement even when the math is right — the client either over-trusts a fragile number or can't act on it. The deliverable is not the test output; it is a plain-language bottom line a decision-maker can act on, *with the uncertainty travelling alongside it* — the confidence interval tied to the decision threshold, the assumptions that were checked, the pitfalls screened, and a retrieval date on anything volatile. This is the Output Contract made into a communication discipline: the interval, not the point; the caveat in the open, not buried.

## How to apply

Lead with the decision, attach the uncertainty, surface the caveats — never invert that order:

```
Bottom line (plain language):  <what the stakeholder should DO, tied to their threshold>
Evidence:                       <EFFECT SIZE + 95% CI>  (p secondary), <test + why>
Assumptions checked:            <normality / variance / independence — result or fallback taken>
Pitfall screen:                 <which of the 9 are in play; how handled>
Caveats / what could change this: <underpowered? observational? volatile vendor claim + date?>
# Shape per ../templates/statistical-report.md ; for a dashboard metric, emit the CI/uncertainty annotation
```

**Do:**
- Open with a one-sentence, plain-language bottom line tied to the business decision; put the effect size + CI right behind it.
- State assumptions checked and pitfalls screened *in the open* — a buried caveat is an undisclosed risk.
- Translate magnitude into the stakeholder's units ("+4 conversions per 100 visitors", not just "d = 0.18"); date any volatile claim (tooling version, vendor A/B method).

**Don't:**
- Hand over a bare p-value, a naked point estimate, or a forecast point line with no interval.
- Present a two-point movement as a "trend", or a dashboard jump as "real", without the signal-vs-noise check and the uncertainty band.
- Let "drives / causes / impact" into the bottom line unless a causal design backs it (downgrade to "associated with").

## Edge cases / when the rule does NOT apply

- **Internal analyst-to-analyst notes** can be terser and more technical — the full plain-language framing is for the stakeholder-facing deliverable, though the CI and caveats stay regardless of audience.
- **A pre-agreed go/no-go gate** may only need the verdict — but the CI still rides along, because "cleared by a hair" vs "cleared with room" changes how much to trust the call.
- **Live, interactive review** (walking a client through the analysis) lets the caveats surface in conversation rather than in a written structure — but anything durable (a written report, a dashboard annotation) carries them in text.

## See also

- [`../templates/statistical-report.md`](../templates/statistical-report.md) — the write-up shape: plain-language bottom line + method + effect size & CI + caveats.
- [`./effect-size-and-ci-not-bare-p.md`](./effect-size-and-ci-not-bare-p.md) — the rule on what the headline number must be.
- [`./test-distinguish-signal-from-noise-on-dashboard-metrics.md`](./test-distinguish-signal-from-noise-on-dashboard-metrics.md) — the uncertainty annotation a dashboard metric needs.
- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — the Output Contract this codifies (Question / Method / Assumptions / Result / Pitfall screen / Verdict / Tooling).

## Provenance

Codifies the Output Contract in [`../CLAUDE.md`](../CLAUDE.md) §6 and the agent's mission ("make the answer defensible to a non-statistician") in [`../agents/applied-statistician.md`](../agents/applied-statistician.md), plus house opinions #2 (the interval, not the point) and #10 (volatile claims carry a retrieval date). Tier 1 / consensus on the communication spine; grounded in the plugin's own [`../templates/statistical-report.md`](../templates/statistical-report.md).

---

_Last reviewed: 2026-05-30 by `claude`_
