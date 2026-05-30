# Inherent, residual, and target are three separate ratings — a two-rating register hides the truth

**Status:** Absolute rule
**Domain:** Risk and controls — risk register
**Applies to:** `regulatory-compliance`

---

## Why this exists

A risk register exists to answer one question: is the firm over- or under-controlled against its appetite? It can only answer that with three distinct ratings per row — **inherent** (the risk gross of controls), **residual** (the risk net of the controls actually operating), and **target** (where appetite says the residual should sit). Registers that carry only inherent and residual look complete but hide the most important comparison: residual *against target*. A residual that's below target means the firm may be over-controlling (spending control effort it doesn't need); a residual above target with no remediation plan is a risk the firm is knowingly running outside appetite. Worse is the register where inherent and residual are identical on every row — proof the controls were never actually rated, just asserted. A register row without inherent *and* residual is, in the constitution's words, half a register; without target, it can't be read against appetite at all.

## How to apply

Rate every row three ways, using the firm's actual scoring rubric, and read residual against target:

```
Inherent      likelihood x impact, GROSS of controls — the raw exposure
Controls      the controls operating against this risk (named, mapped, evidenced)
Residual      likelihood x impact, NET of controls actually operating — not aspirational
Target        where the risk-appetite statement says residual should sit
Read          residual <= target  -> within appetite (check for over-control)
              residual >  target  -> OUT of appetite -> remediation plan with owner + date REQUIRED
```

Appetite drives this, not the controls — without an articulated appetite, "target" floats and the whole register loses its anchor (house opinion #4). Note correlations explicitly: two "medium/medium" risks that are perfectly correlated are a "high" together, and a heat map that omits the correlation lies.

**Do:**
- Carry inherent, residual, and target as three separate ratings per row, scored on the firm's rubric (not narrative).
- Set target from the risk-appetite statement — quantified thresholds, not "low risk" as a vibe.
- Flag every residual-above-target row with a remediation plan (owner + date); note correlated risks explicitly.

**Don't:**
- Ship a two-rating register (inherent + residual only) — it can't show over/under-control vs appetite.
- Leave inherent and residual identical on every row — that means the controls were never rated.
- Let the register grow unbounded — prune resolved/immaterial risks quarterly; 800 rows is a list, not a register.

## Edge cases / when the rule does NOT apply

- **A brand-new risk with no controls yet** legitimately has inherent = residual until a control is designed — flag it as uncontrolled, don't pretend a control exists.
- **Qualitative red-line risks** (conduct, reputational) may resist a clean likelihood×impact score — rate them on the firm's qualitative scale and state the basis, rather than forcing a false number.
- **Legal-implication risk** (penalty, litigation exposure) is identified in the register but the legal quantification routes to counsel; the inherent/residual/target framing of the *operational* risk continues.

## See also

- [`./controls-one-control-one-requirement-traceable.md`](./controls-one-control-one-requirement-traceable.md) — the controls that move inherent to residual must be mapped and evidenced.
- [`./controls-classify-the-control-type-before-you-rate-it.md`](./controls-classify-the-control-type-before-you-rate-it.md) — control type informs the residual rating.
- [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md) — `## Decision Tree: Control type — preventive vs detective vs corrective`.
- [`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md) — "Inherent ≠ residual ≠ target. Three distinct ratings."

## Provenance

Codifies the `risk-and-controls-specialist` opinions "Inherent ≠ residual ≠ target," "Risk appetite first, controls second," "Risk registers prune, they don't grow," and "Heat maps lie about correlated risks," plus the anti-patterns "inherent and residual ratings identical for every row" and "risk-appetite statement with words but no numbers" ([`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md)), and house opinions #4 (appetite drives controls) and #13 (risk quantified) in [`../CLAUDE.md`](../CLAUDE.md) §3.

---

_Last reviewed: 2026-05-30 by `claude`_
