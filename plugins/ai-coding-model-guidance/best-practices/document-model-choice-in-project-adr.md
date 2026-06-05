# Document model choice and rationale in the project's ADR or runbook

**Status:** Pattern
**Domain:** Model selection methodology
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

AI coding tool model choices that live only in a developer's memory or a chat session are the first thing to go stale. When the lineup changes, the team re-asks the same question. When the developer changes, the choice disappears. When a reviewer asks "why is the team using a frontier model for inline completions?", there is no auditable answer. A lightweight ADR or runbook entry that documents the model choice, the tier rationale, and the verification date makes the choice repeatable, reviewable, and recoverable when the lineup changes.

## How to apply

For any model choice that will persist beyond a single session — a default model configuration for a team, a CI/CD agentic run model, an org policy model allow-list — produce a brief decision record:

```markdown
## AI Coding Tool Model Choice — [date]

Tool: [GitHub Copilot / OpenAI Codex / xAI Grok]
Model tier: [Fast inline / Balanced default / Frontier]
Model id at decision time: [id — verify-at-use — YYYY-MM]
Task type: [use-case description]
Rationale: [2-3 sentences from the tree traversal]
Surface: [IDE / terminal / API / CI]
Blast radius: [Low / Medium / High]
Reasoning level (Codex): [low / medium / high / n/a]
Review cadence: [monthly / on-lineup-change / other]
```

The record does not need to be long. Its value is the date and the rationale — enough to re-derive the choice when the lineup changes.

**Do:**
- Record the model id with a `[verify-at-use — YYYY-MM]` marker so the review cadence is built in.
- Set a review trigger: "review when the knowledge bank sweep finds a lineup change affecting this tier."
- Link the ADR from the relevant config file (`.github/copilot.yaml`, Codex config, Grok API wrapper).

**Don't:**
- Hard-code a specific model id in infrastructure without an associated decision record — the id will change and the change will be invisible without context.
- Create a detailed ADR for every one-off chat recommendation — reserve the record for persistent team or org choices.

## Edge cases / when the rule does NOT apply

- A one-off debugging session where the model choice is not persisted anywhere — no record needed.

## See also

- [`../templates/model-recommendation-brief.md`](../templates/model-recommendation-brief.md) — the recommendation brief that feeds the ADR
- [`../best-practices/volatile-numbers-carry-a-marker.md`](./volatile-numbers-carry-a-marker.md) — the `[verify-at-use]` marker this rule requires in the ADR

## Provenance

Derived from the broader `ravenclaude-core` Claim Grounding protocol applied to persistent model choices. A model id in a config file is a claim — it needs the same retrieval date and review trigger as any other volatile number in the knowledge bank.

---

_Last reviewed: 2026-06-05 by `claude`_
