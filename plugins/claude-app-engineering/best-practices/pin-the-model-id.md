# Pin the exact model id; never use a floating alias

**Status:** Absolute rule
**Domain:** Reliability / model management
**Applies to:** `claude-app-engineering`

---

## Why this exists

Floating aliases like `claude-sonnet-latest` resolve to whatever Anthropic
currently considers the latest model. When that pointer moves, your app silently
upgrades: prompt tuning, thinking params, output length, and latency change
without a deployment event, without an eval gate, and without your knowledge.
Teams discover this during incident review — "the prompt regressed last Tuesday"
aligns with a model-pointer rotation. The fix is always to pin a specific model
id and migrate deliberately with an eval gate.

## How to apply

Always specify the full versioned model id in every `messages.create` call
and in every agent/skill file that names a model. Keep the pinned ids in a
single config file so there is one place to update.

```python
# config.py — single source of truth for pinned model ids
MODELS = {
    "triage":   "claude-haiku-4-5",       # cheap + fast; eval-judge, triage
    "default":  "claude-sonnet-4-6",      # balanced; most app work
    "frontier": "claude-opus-4-7",        # hardest reasoning tail
}
# [verify-at-build] — re-confirm ids against the dated capability map before deploy

# Usage:
from config import MODELS
resp = client.messages.create(model=MODELS["default"], ...)
```

The hook (`check-claude-app-anti-patterns.sh`) flags retired model ids
(`claude-2`, `claude-instant`, `claude-1`) — but it cannot know about a new
wrong id you pick. Use the capability map as the source of truth.

**Do:**
- Use the exact versioned id from the dated capability map.
- Keep all pinned ids in one config file; grep it on every capability-map refresh.
- Run evals before migrating from one pinned id to another
  (`model-migrate-behind-an-eval-gate.md`).

**Don't:**
- Use `*-latest`, `*-new`, or any non-versioned alias in production code.
- Bake a model id directly into a system prompt string where it is invisible to
  grep.
- Upgrade a model id across environments without an eval gate.

## Edge cases / when the rule does NOT apply

- Local rapid prototyping / exploratory notebooks where you want the latest
  model: fine. Never promote unpinned ids to a staging or production config.

## See also

- [`../agents/claude-solution-architect.md`](../agents/claude-solution-architect.md) — model right-sizing decision
- [`./model-migrate-behind-an-eval-gate.md`](./model-migrate-behind-an-eval-gate.md) — how to migrate safely
- [`./right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md) — picking the right tier

## Provenance

Codifies house opinion #11 from `CLAUDE.md` §3 ("pin the model") and the
`model-selection-and-2026-capability-map.md` refresh discipline (capability map
dated 2026-05-28). The anti-pattern grep in
`hooks/check-claude-app-anti-patterns.sh` catches the retired ids but not all
wrong ids — the capability map is the authority.

---

_Last reviewed: 2026-06-05 by `claude`_
