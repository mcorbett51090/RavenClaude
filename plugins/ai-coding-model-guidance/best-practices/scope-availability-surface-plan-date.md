# Scope every availability claim to surface, plan, and retrieval date

**Status:** Absolute rule
**Domain:** Claim grounding / accuracy
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

"Model X is in Copilot" stated as a flat universal is almost certainly wrong for
some surface or some plan tier. GitHub Copilot serves model access differently
across completions, chat (IDE), coding agent, cloud agent, and mobile — and
availability differs between Free, Pro, Business, and Enterprise plans. The same
is true for Grok access tiers and Codex plan gates. An unscoped claim that gets
copy-pasted into a procurement decision or a developer's `.copilotignore`
configuration can cost real money or block a team for months.

## How to apply

Structure every availability claim with three mandatory qualifiers:

```
Model X is available in <SURFACE> for <PLAN_TIER> as of <RETRIEVAL_DATE> [verify-at-use].
```

Example (do this):
```
GPT-5.5 is available for Copilot chat in the IDE for Pro and Enterprise plans
as of 2026-05 [verify-at-use — check the GitHub Copilot model availability page].
```

Example (don't do this):
```
GPT-5.5 is in Copilot.
```

When the knowledge bank's retrieval date is more than 4 weeks old for the claimed
surface/plan, add: "re-verify before acting — the picker contents change
frequently."

**Do:**
- Always include surface + plan + retrieval date in any model availability claim.
- Cite the source field in the knowledge bank entry that backs the claim.
- Add a `[verify-at-use — YYYY-MM]` marker when the date is > 4 weeks old.

**Don't:**
- Omit the plan qualifier ("available for Copilot" when it's Enterprise-only).
- Omit the surface qualifier ("available for Copilot" when it's IDE-chat-only).
- Quote availability from training memory — always use the dated knowledge bank.

## Edge cases / when the rule does NOT apply

- When the developer is asking about a model they are already actively using in a
  confirmed context: they have fresher real-world evidence than the knowledge
  bank; defer to their observation while noting the date caveat.

## See also

- [`../agents/copilot-model-strategist.md`](../agents/copilot-model-strategist.md) — owns Copilot surface/plan availability
- [`./volatile-numbers-carry-a-marker.md`](./volatile-numbers-carry-a-marker.md) — the complementary rule for pricing and context-window claims
- [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) — the availability gates live here

## Provenance

Codifies house opinion #3 from `CLAUDE.md` §3 ("availability is always scoped")
and the anti-pattern "model X is in Copilot with no surface/plan/date scope."
Standard claim-grounding discipline for fast-churn vendor facts.

---

_Last reviewed: 2026-06-05 by `claude`_
