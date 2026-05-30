# Climb the prompt leverage ladder — clear+direct first, multi-agent last

**Status:** Pattern — strong default; reaching for a multi-agent system before exhausting clear+direct+examples is the anti-pattern.

**Domain:** Prompt + context engineering

**Applies to:** `claude-app-engineering`

---

## Why this exists

Most "the model won't do what I want" tickets are an underspecified prompt, not a model limitation — and the fix is almost always cheaper than the one reached for. Anthropic publishes a rough order of leverage (cheapest, highest-impact technique first); applying it in order means you stop at the first rung that works instead of jumping straight to chain-of-thought, a fine-tune-equivalent, or a multi-agent orchestration for a problem a clear instruction and two examples would have solved. Skipping rungs costs latency, tokens, and debuggability — and newer Claude models actively *regress* when over-prompted (they reason well by default; a "think step by step" nudge on a trivial task adds cost and can hurt). The ladder is the order; the discipline is climbing it one rung at a time against an eval, not all at once on vibes.

## How to apply

Apply rungs in order, stop when the output is good enough, and change one rung at a time so you can attribute the delta.

```python
# The ladder (cheapest/highest-leverage first — stop when good enough):
# 1. Clear + direct + specific  — task, audience, format, constraints; say what TO do
# 2. Multishot examples         — 2-5 diverse, correct, edge-covering, wrapped in <example> tags
# 3. Let it think (CoT)         — only for genuine reasoning; or adaptive thinking on Sonnet 4.6
# 4. XML structure              — <document>/<instructions>/<answer>: removes ambiguity, parseable
# 5. Role / system prompt       — durable role+rules+tone in `system` (also the best thing to cache)
# 6. Prefill the assistant turn — start the reply ("{" for JSON, a heading) to skip preamble
# 7. Chain prompts              — one focused prompt per stage > one mega-prompt
system = [{"type": "text", "text": ROLE_RULES_TONE, "cache_control": {"type": "ephemeral"}}]
messages = [{"role": "user", "content": (
    "<instructions>Summarize the contract for a non-lawyer in 5 bullets.</instructions>\n"
    f"<document>{contract}</document>"
)}]
# Only after a rung lands, re-measure on the golden set before adding the next (evals-before-vibes).
```

**Do:**
- Start at rung 1: state task, audience, format, and constraints explicitly; tell Claude what TO do, not only what to avoid.
- Add **2-5 diverse, edge-covering examples** before reaching for chain-of-thought — examples out-leverage paragraphs of instruction.
- Put durable role/rules/tone in the **`system`** prompt (it's also the best thing to cache — [`cache-the-static-prefix.md`](./cache-the-static-prefix.md)); keep the per-request task in the user turn.
- Change **one rung at a time** and re-measure on the golden set ([`evals-before-vibes.md`](./evals-before-vibes.md)).

**Don't:**
- Jump to multi-agent orchestration before a single well-prompted call with retrieval + examples has been tried ([`agent-orchestration-patterns.md`](../knowledge/agent-orchestration-patterns.md): start simple).
- Bolt "think step by step" onto a trivial task — newer models over-prompt poorly; reserve CoT/thinking for genuine reasoning.
- Tune by feel — climb the ladder against an eval delta, not vibes.

## Edge cases / when the rule does NOT apply

- **Machine-readable output** is not a prompting rung — force a tool call instead of asking for "JSON only" ([`output-structured-via-forced-tool.md`](./output-structured-via-forced-tool.md)).
- **Genuinely multi-stage work** legitimately lands on rung 7 (prompt chaining) or an orchestration pattern — the ladder doesn't forbid complexity, it forbids *premature* complexity.
- **Prefill is unavailable with extended/adaptive thinking** — rung 6 doesn't apply when thinking is on.
- Authoring/critiquing a **RavenClaude agent or skill file** (the prompt-as-artifact) is `ravenclaude-core/prompt-engineer`, not this rung ladder for a running app (the seam, [`../CLAUDE.md`](../CLAUDE.md) §10).

## See also

- [`../knowledge/prompt-engineering-techniques.md`](../knowledge/prompt-engineering-techniques.md) — the full ladder, output control, hallucination reduction, the prompt→eval loop
- [`./output-structured-via-forced-tool.md`](./output-structured-via-forced-tool.md) — the structured-output path that is *not* a prompting rung
- [`./evals-before-vibes.md`](./evals-before-vibes.md) — the loop that keeps ladder-climbing honest
- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) — owns the running app's prompt craft

## Provenance

Codifies the prompt-engineering leverage ladder from [`../knowledge/prompt-engineering-techniques.md`](../knowledge/prompt-engineering-techniques.md) (Anthropic prompt-engineering docs — be-clear-and-direct, multishot, CoT, XML, system prompts, prefill, chain — retrieved 2026-05-28) and the start-simple principle from [`../knowledge/agent-orchestration-patterns.md`](../knowledge/agent-orchestration-patterns.md). Model-version-specific tactics (adaptive thinking, less hand-holding) are dated — verify against the capability map.

---

_Last reviewed: 2026-05-30 by `claude`_
