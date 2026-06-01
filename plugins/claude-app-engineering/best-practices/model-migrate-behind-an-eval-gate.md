# Migrate models behind an eval gate — pin, re-baseline, diff, cut over

**Status:** Pattern — strong default for any model-version change (upgrade or forced retirement); deviate only with a written reason.

**Domain:** Model lifecycle / evals

**Applies to:** `claude-app-engineering`

---

## Why this exists

Models get versioned and retired on a schedule the platform sets, not you — a model you pinned will eventually be deprecated, and a newer version (4.6→4.7, a Haiku/Sonnet/Opus bump) regularly ships with better behavior you want. Both are **recurring, unavoidable events**, and the dangerous move is the silent swap: change the model string, ship, and discover in production that prompts tuned for the old model regressed (different refusal behavior, different formatting, different tool-call cadence). `evals-before-vibes` says "no prompt/model change ships without an eval delta" generically; this rule names the **migration trigger** specifically and the safe sequence, because it's the moment teams skip the eval out of "it's just a version bump."

## How to apply

Treat a model-version change as a change that **must** pass the eval gate before cutover:

1. **Pin both.** Keep the current pinned model running; add the new version behind a flag/branch — don't replace in place.
2. **Re-run the golden set on the new version.** Same prompts, same graders (programmatic + LLM-judge on Haiku via Batch), randomized order.
3. **Diff the deltas.** Compare pass-rate, judge scores, cost-per-resolved-task, latency, and any format/tool-call contract the app depends on. A "better" model can still regress *your* specific prompt.
4. **Fix the regressions on the new version** (re-tune the prompt/thinking config for the new model — params are version-specific; keep them in the capability map, not baked in code) before cutover.
5. **Cut over deliberately**, keep the old pin available for rollback until the new version is proven in production.

**Triggers that fire this loop:** a deprecation notice on a model you use; wanting a newer flagship's capability; a price/latency change that makes a different tier attractive.

**Do:** pin → eval-gate → diff → re-tune → cut over; re-baseline the golden set on the new version; keep rollback available.

**Don't:** swap the model string and ship; assume "newer = strictly better" for your prompts; carry the old model's thinking/temperature params unverified onto the new version (they're version-specific).

## Edge cases / when the rule does NOT apply

A dev/prototype with no production traffic and no golden set yet: build the golden set *as part of* the migration rather than blocking on a pre-existing one. A forced same-day retirement with no newer-version choice may require an emergency cutover — do it, but run the eval immediately after and treat any regression as a P1. Exact model IDs, deprecation dates, and version-specific params are volatile — capability map, `[verify-at-use]`.

## See also

- [`./evals-before-vibes.md`](./evals-before-vibes.md) — the general "no change without an eval delta" rule this specializes
- [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md) — current model lineup, deprecations, version-specific params (dated)
- [`../knowledge/evals-and-quality.md`](../knowledge/evals-and-quality.md) — golden sets + judge design
- [`../agents/eval-engineer.md`](../agents/eval-engineer.md) — owns the eval gate
- [Claude API model deprecations](https://docs.claude.com/en/docs/about-claude/model-deprecations) — authoritative (verify dates at use)

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01, both panels AGREE — durable posture, not a volatile fact, so it correctly lives as a BP not capability-map content): `evals-before-vibes` covered eval-before-shipping generically but nothing named the version-migration/deprecation trigger, a recurring real event. The model-version-migration *tree* Panel 1 also proposed was cut by Panel 3 (the sequence is a linear gated procedure, not a branch) — folded into this BP. Model IDs/dates/params are `[verify-at-use]`.

---

_Last reviewed: 2026-06-01 by `claude`_
