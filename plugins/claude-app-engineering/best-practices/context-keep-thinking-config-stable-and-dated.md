# Keep thinking config stable across turns — and dated, never baked into code

**Status:** Pattern — strong default; toggling thinking mid-session busts the cache, and a version-specific thinking param hard-coded in app logic rots monthly.

**Domain:** Prompt + context engineering / FinOps

**Applies to:** `claude-app-engineering`

---

## Why this exists

Extended/adaptive thinking is a real quality lever for hard reasoning — but it has two sharp edges that quietly cost money and break in production. **The cache edge:** thinking blocks consume context and are *cached alongside content*; changing the thinking configuration mid-session (or having a non-tool-result turn strip cached thinking on older models) **invalidates the message cache**, so a session that toggles thinking pays full input repeatedly. **The staleness edge:** the exact parameters are version-coupled and change monthly — adaptive thinking on Sonnet 4.6 uses `thinking:{type:"adaptive"}` with `budget_tokens` *deprecated* there [verify-at-build]; extended thinking needs `temperature` unset/1. Bake `budget_tokens=8000` into app logic and it's wrong the next model. The discipline: keep thinking config **stable across a session** (protect the cache) and keep the version-specific params **in the capability map**, not in your code or an agent persona — so one dated file refreshes, not six call sites.

## How to apply

Set thinking once per session and hold it constant; reference the current params from the capability map, don't hard-code them; reserve thinking for genuine reasoning.

```python
# Pull the CURRENT thinking config from the dated capability map, not a literal in code.
THINKING = current_thinking_config("claude-sonnet-4-6")   # e.g. {"type": "adaptive"} [verify-at-build]
resp = client.messages.create(
    model="claude-sonnet-4-6", max_tokens=2048,
    thinking=THINKING,            # SAME object every turn this session — toggling busts the cache
    # temperature unset (extended thinking needs temperature 1/unset)
    system=SYSTEM, tools=TOOLS, messages=messages,
)
# Prior-turn thinking blocks are preserved by default on Opus 4.5+/Sonnet 4.6+ and counted as
# cached input on read -> keeping config stable keeps the cache valid. Don't CoT trivial tasks.
```

**Do:**
- Choose thinking on/off (and the mode) **once per session** and keep it **constant across turns** — stability protects the cache ([`cache-the-static-prefix.md`](./cache-the-static-prefix.md)).
- Pull version-specific thinking params from [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md) — the **dated** source — not from a literal in app code or an agent persona (#14).
- Reserve thinking for **genuine reasoning/analysis**; newer models reason well by default and don't need a "think step by step" nudge on simple tasks ([`prompt-climb-the-leverage-ladder.md`](./prompt-climb-the-leverage-ladder.md)).
- Remember thinking blocks **consume + are charged as context** — budget for them in the window ([`context-budget-the-1m-window.md`](./context-budget-the-1m-window.md)).

**Don't:**
- Toggle thinking on/off mid-session, or flip `temperature` while thinking is on — both invalidate the message cache.
- Hard-code `budget_tokens=N` (deprecated on Sonnet 4.6 [verify-at-build]) or any version-coupled param into app logic — it rots on the next model release.
- Enable thinking on trivial classification/extraction — it adds latency and cost for no quality gain (right-size instead, [`right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md)).

## Edge cases / when the rule does NOT apply

- **Deliberately switching models** (a routing-ladder escalation to Opus) legitimately changes the thinking config — that's a new request shape with its own cache, not a mid-session toggle ([`right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md)).
- **Older models / Haiku** strip cached thinking on a non-tool-result user turn — on those, the cache interaction differs; verify against the caching playbook.
- **Single-shot calls** have no session to keep stable — the staleness/dated-params half of the rule still applies (don't hard-code the param).
- The exact param names and deprecations are **dated** — `[verify-at-build]` against the capability map before quoting or coding them.

## See also

- [`../knowledge/context-engineering-2026.md`](../knowledge/context-engineering-2026.md) — thinking config (dated), thinking blocks consume + are cached, keep config stable
- [`../knowledge/prompt-caching-playbook.md`](../knowledge/prompt-caching-playbook.md) — thinking + caching: preservation rules across models
- [`./cache-the-static-prefix.md`](./cache-the-static-prefix.md) · [`./context-budget-the-1m-window.md`](./context-budget-the-1m-window.md)
- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) — owns thinking config

## Provenance

Codifies the thinking-config discipline from [`../knowledge/context-engineering-2026.md`](../knowledge/context-engineering-2026.md) and [`../knowledge/prompt-caching-playbook.md`](../knowledge/prompt-caching-playbook.md) (Anthropic context + caching docs, retrieved 2026-05-28) and house opinions #11 (thinking config is dated; keep version-specific params in the capability map) and #14 (cite with a retrieval date) from [`../CLAUDE.md`](../CLAUDE.md) §3. Param names/deprecations are dated — verify against [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md).

---

_Last reviewed: 2026-05-30 by `claude`_
