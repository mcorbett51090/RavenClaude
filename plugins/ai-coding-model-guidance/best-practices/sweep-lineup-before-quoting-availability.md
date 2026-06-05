# Sweep the knowledge bank before quoting model availability

**Status:** Absolute rule
**Domain:** Knowledge currency
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

The knowledge bank (`cross-tool-model-lineup-2026.md`) is Tier-4 (fast-churn): picker contents, pricing tiers, and model ids change weekly to monthly. An agent that quotes availability from a bank that is more than 4 weeks old is producing stale recommendations as confidently as fresh ones. The CI gate (`check-lineup-citations.py`) enforces that volatile numbers carry `[verify-at-use]` markers, but the gate cannot enforce that the bank itself was recently swept. This rule fills that gap: before quoting any availability claim, check whether the bank needs a sweep.

## How to apply

Before quoting model availability, pricing markers, or context-window sizes:

```
1. Check the bank's Last-retrieved header
   → If more than 4 weeks old: trigger a lineup-freshness-sweep first
   → If within 4 weeks: proceed with [verify-at-use] markers as normal

2. When triggering a sweep:
   → Use the lineup-freshness-sweep skill
   → Delegate to ravenclaude-core/deep-researcher for live primary-source verification
   → Update the bank's Last-retrieved date after the sweep

3. When the bank cannot be swept immediately (no deep-researcher, no live access):
   → Mark all claims from the bank as [unverified — training knowledge — reverify YYYY-MM]
   → Do not present them as current
```

**Sweep triggers (any one is sufficient):**
- Bank header is more than 4 weeks old
- Developer reports a discrepancy with what they see in their picker
- A retirement / redirect is suspected
- The `researcher-reminder.yml` weekly sweep fires

**Do:**
- Treat a stale bank as a pre-condition failure, not a permission to quote stale data.
- Document the retrieval date and primary source URL on every updated bank entry.
- Mark claims as `[unverified]` rather than silently omitting them when a sweep is not possible.

**Don't:**
- Quote picker contents as current without checking the bank's sweep date.
- Treat a recent sweep of one ecosystem's section as covering all three ecosystems.
- Skip the sweep trigger when the developer's urgency is high — a stale recommendation is worse than a delayed one.

## Edge cases / when the rule does NOT apply

- The claim is about the vendor-neutral decision-tree methodology (not a specific SKU, price, or availability fact) — the tree is stable and does not require a sweep before use.

## See also

- [`../skills/lineup-freshness-sweep/SKILL.md`](../skills/lineup-freshness-sweep/SKILL.md) — the sweep procedure
- [`../knowledge/cross-tool-model-lineup-2026.md`](../knowledge/cross-tool-model-lineup-2026.md) — the knowledge bank being swept

## Provenance

Codifies the `CLAUDE.md` §7 knowledge bank discipline: the Tier-4 tag means "sweep before quoting." The CI gate enforces markers on the content; this rule enforces that the content is current.

---

_Last reviewed: 2026-06-05 by `claude`_
