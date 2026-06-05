# Seam to claude-app-engineering for any Claude model question

**Status:** Absolute rule
**Domain:** Plugin scope / seam discipline
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

This plugin covers the non-Claude AI-coding ecosystems: GitHub Copilot, OpenAI
Codex, and xAI Grok. Claude models, the Anthropic API, and Claude build-surface
decisions are owned by the sibling plugin `claude-app-engineering`. An agent that
half-answers a "should I use Claude instead?" question inside this plugin
gives the developer incomplete guidance — missing the build-surface decision tree,
the caching strategy, the deployment targets, and the eval discipline that
`claude-app-engineering` provides. The boundary is hard, not fuzzy.

## How to apply

When a developer asks anything that is about Claude (model ids, Anthropic API,
Claude build surfaces, Claude pricing), do not attempt to answer. Hand off:

```
"Your question is about Claude model selection / the Anthropic API, which is
owned by the sibling plugin claude-app-engineering —
specifically the claude-solution-architect agent.

Reasons to use Claude for this use case: [1–2 factual pointers if obvious].
I'll route you there for the full surface/model/deployment decision."
```

Do not even provide a brief Claude model comparison "just to be helpful" — an
incomplete comparison is worse than a clean handoff because it may bias the
developer before they see the full picture.

**Do:**
- Name the specific agent to contact: `claude-app-engineering/claude-solution-architect`.
- Hand off cleanly; do not answer a Claude question and then add "but for more
  detail see claude-app-engineering."
- If the developer is comparing Claude vs Codex vs Copilot vs Grok for a task:
  cover the non-Claude sides and explicitly hand off the Claude side.

**Don't:**
- Answer "which Claude model should I use?" inside this plugin.
- Discuss Anthropic pricing inside this plugin.
- Give a partial Claude answer and label it "just an overview."

## Edge cases / when the rule does NOT apply

- The developer is asking a general methodology question (e.g. "how do I choose
  between AI coding tools?") where Claude is one of many options being compared
  at a high level: a high-level mention is fine; defer the Claude-specific depth.

## See also

- [`../agents/codex-model-strategist.md`](../agents/codex-model-strategist.md) — stays in its lane (OpenAI Codex only)
- [`../agents/copilot-model-strategist.md`](../agents/copilot-model-strategist.md) — stays in its lane (Copilot only)
- [`../agents/grok-model-strategist.md`](../agents/grok-model-strategist.md) — stays in its lane (Grok only)

## Provenance

Codifies house opinion #8 from `CLAUDE.md` §3 ("stay in your lane; seam to
Claude") and the seam definition in §9 ("the moment the right answer is a Claude
model's capabilities or a Claude build, hand to claude-app-engineering").

---

_Last reviewed: 2026-06-05 by `claude`_
