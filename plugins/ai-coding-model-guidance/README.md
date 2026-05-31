# ai-coding-model-guidance

Cross-tool model guidance for the **non-Claude** AI-coding ecosystems. Three strategist agents help you reason about *which model to pick* — and just as often, talk you out of overriding the default without a reason — in:

- **GitHub Copilot** — the model picker across completions / chat / coding agent / cloud agent / mobile, plan-gated availability, and org model rules → `copilot-model-strategist`
- **OpenAI Codex** — CLI + cloud model **and reasoning-level** selection (GPT-5.5 default, GPT-5.5-Pro, GPT-5.3-Codex / GPT-5-Codex, Codex-Spark, GPT-5.4 fallback) → `codex-model-strategist`
- **xAI Grok** — the Grok 4.x lineup (Grok 4.3 flagship, 4.1 Fast / 4.20) and retirement/billing warnings → `grok-model-strategist`

## What it gives you

- A **vendor-neutral decision tree** (latency → fast tier · autonomy → coding-agent tier · difficulty → top frontier · everyday → balanced default) that you traverse *before* naming a SKU.
- **Right-sizing discipline** — the metric is cost-per-resolved-task, not model rank.
- A **single, dated, citation-grounded lineup** ([`knowledge/cross-tool-model-lineup-2026.md`](knowledge/cross-tool-model-lineup-2026.md)) — the freshness anchor for all three vendors, re-verified on the weekly Researcher sweep.
- A **closed-world rule** so an agent never invents a model that doesn't exist (the dense GPT-5.x / Grok-4.x naming invites exactly that).

## What it deliberately does NOT cover

**Claude models and Claude-app builds.** The moment the right answer is "use a Claude model" or "build a Claude app," the agents seam to [`claude-app-engineering`](../claude-app-engineering/) (`claude-solution-architect`). This plugin owns the *non-Claude* tools.

## Important: these facts are volatile

Model names, prices, context windows, and picker availability across these three vendors **churn weekly-to-monthly** and are past the author's training cutoff. Every number in the knowledge bank carries a **retrieval date** and a **verify-at-use** rider, and the agents re-verify against the cited primary source before quoting. **Treat a lineup whose `Last reviewed:` date is more than ~30 days old as stale-until-re-checked.** The current snapshot was retrieved 2026-05-31.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ai-coding-model-guidance@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Layout

```
ai-coding-model-guidance/
├── .claude-plugin/plugin.json
├── CLAUDE.md                                  team constitution
├── README.md
├── agents/
│   ├── copilot-model-strategist.md
│   ├── codex-model-strategist.md
│   └── grok-model-strategist.md
└── knowledge/
    └── cross-tool-model-lineup-2026.md        single source of truth (dated + cited)
```
