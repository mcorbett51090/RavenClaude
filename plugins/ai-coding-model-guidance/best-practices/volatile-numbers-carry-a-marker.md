# Volatile numbers carry a verify-at-use marker

**Status:** Absolute rule
**Domain:** Claim grounding / accuracy
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

Prices, context-window sizes, and benchmark scores for Copilot, Codex, and Grok
models churn weekly to monthly. A confidently-quoted number without a date and
a verification rider that reaches a developer's architecture decision document
or a procurement spreadsheet may be months stale by the time they act on it.
In this plugin's domain, the entire payload is volatile third-party facts past
the author's training cutoff — the claim-grounding discipline is load-bearing,
not decorative.

## How to apply

Append `(verify-at-use — YYYY-MM)` to every numeric or benchmark claim:

- **Prices:** "Model X costs approximately $Y per million tokens
  (verify-at-use — 2026-05) — check the vendor's current pricing page."
- **Context windows:** "Model X supports approximately N tokens of context
  (verify-at-use — 2026-05) — confirm against the vendor's model card."
- **Benchmarks:** "Model X scores approximately Z on HumanEval
  (verify-at-use — 2026-05) — benchmark scores are not task-specific; measure
  on your own workload."

The `YYYY-MM` stamp is the month in the knowledge bank's retrieval date for that
entry. If no retrieval date exists, use `[unverified — training knowledge]` and
offer to research before the developer acts.

**Do:**
- Include the month stamp, not just "verify" — the stamp tells the developer
  *how stale* the number might be.
- Point to the primary source (vendor pricing page URL, model card) where
  the developer can re-verify.
- Treat benchmarks with an extra caveat: they measure a specific task class,
  not fitness to the developer's workload.

**Don't:**
- Quote a specific price or context-window size without the marker.
- Use "approximately" as a substitute for the marker — it signals imprecision
  but not staleness.
- Keep volatile numbers in agent personas (house opinion #4) — they live in the
  dated knowledge bank only.

## Edge cases / when the rule does NOT apply

- Boolean availability facts (yes/no, GA/preview) that are not numeric: still
  scope by date, but no numeric marker needed.
- The developer provides their own freshly-verified numbers from the vendor site:
  accept and use their numbers; add a note to update the knowledge bank.

## See also

- [`../agents/grok-model-strategist.md`](../agents/grok-model-strategist.md) — Grok pricing and context are especially volatile
- [`./scope-availability-surface-plan-date.md`](./scope-availability-surface-plan-date.md) — availability claims get a parallel scoping treatment
- [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) — the freshness anchor for this plugin's facts

## Provenance

Codifies house opinion #4 from `CLAUDE.md` §3 ("volatile numbers carry a
retrieval date and a verify-at-use rider") and the anti-pattern "quoting a
price or context window with no retrieval date / verify-at-use." Standard
Claim-Grounding Protocol discipline inherited from `ravenclaude-core`.

---

_Last reviewed: 2026-06-05 by `claude`_
