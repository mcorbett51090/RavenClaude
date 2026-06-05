# Free-tier model access is a subset — never assume full picker availability

**Status:** Absolute rule
**Domain:** Model availability / Copilot-specific
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

GitHub Copilot Free exposes a subset of models compared to Pro, Business, and Enterprise plans. A developer on the Free tier who is told "model X is in Copilot" and then cannot find it in their picker loses trust in the recommendation and, more importantly, loses time. The scoped-availability rule (`scope-availability-surface-plan-date.md`) covers the surface and plan axes; this rule exists specifically to call out the Free-tier sub-list as a distinct, narrower list that requires its own verification step — it is not just "the same picker with a usage cap."

## How to apply

Whenever a model recommendation involves GitHub Copilot and the developer's plan is unknown or Free:

1. **Ask or infer the plan before recommending.** If the developer has not mentioned their plan, ask: "Are you on Copilot Free, Pro, Business, or Enterprise?" Do not assume Pro.
2. **For Free-tier developers:** verify the specific model against the Free-tier sub-list in the dated knowledge bank, not the full Copilot picker.
3. **If the model is not in the Free sub-list:** explain the plan gate explicitly — "this model requires Copilot Pro or above" — and optionally offer the best available Free-tier alternative at the correct tier.

```
Verification check for Free-tier:
  1. Is the model in the verified Copilot lineup?              → if no: closed-world, do not confirm
  2. Is the model in the Free-tier sub-list specifically?      → if no: explain plan gate
  3. Does the Free sub-list have a usage cap for this model?   → if yes: mention it [verify-at-use]
```

**Do:**
- Always verify against the Free sub-list for Free-tier developers — it changes independently of the full picker.
- Mention the usage cap if the Free tier has one for the recommended model `[verify-at-use]`.

**Don't:**
- Quote the full Copilot picker to a Free-tier developer.
- Assume the same models available for Pro are available for Free.
- Treat "Copilot is installed" as evidence of plan tier — Free and Pro installs look the same to the developer.

## Edge cases / when the rule does NOT apply

- Developer confirms they are on Pro or above — use the full picker with the standard plan-gate verification.

## See also

- [`../best-practices/scope-availability-surface-plan-date.md`](./scope-availability-surface-plan-date.md) — the parent scoping rule this one specializes
- [`../agents/copilot-model-strategist.md`](../agents/copilot-model-strategist.md) — Copilot plan tiers and model rules in depth

## Provenance

Derived from `copilot-model-strategist` and the `copilot-surface-audit` skill — the Free sub-list is a distinct gate that the general scope rule doesn't make salient enough. Developer confusion about Free vs. Pro availability is a recurring report.

---

_Last reviewed: 2026-06-05 by `claude`_
