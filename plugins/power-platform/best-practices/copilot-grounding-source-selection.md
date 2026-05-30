# Curate grounding sources over collecting them, and enable strict grounding

**Status:** Primary diagnostic — when a Copilot Studio agent hallucinates, check the knowledge sources first, not the model.

**Domain:** Copilot Studio / grounding

**Applies to:** `power-platform`

---

## Why this exists

Generative answers are retrieval-augmented: the agent reads from its **knowledge sources** at query time and an LLM composes the reply. The single biggest cause of hallucination is **bad sources, not a bad model** — point the agent at "the whole intranet" and it ingests stale, duplicated, and contradictory content, then confidently picks the wrong one. The `copilot-studio-bot-design` skill ranks knowledge-source hygiene as the **#1 hallucination prevention**: curate over collect, control freshness, de-duplicate, and test each source in isolation. Compounding the risk: agents that ingest **untrusted content** (emails, tickets, web pages) open a prompt-injection surface, which is why grounding mode and connector/DLP governance matter (see `copilot-agents-2026.md` governance section). A poorly-sourced agent is worse than no agent — it launders wrong answers in an authoritative voice.

## How to apply

Pick canonical sources per topic area, set a deliberate refresh cadence, turn grounding to a strict mode that requires citations, and test each source as you add it:

```text
Knowledge source config (per source):
  Source:        SharePoint /sites/Policies/HR        ← canonical, single source of truth for HR policy
  Scope:         this library only (NOT the whole tenant)
  Refresh:       daily        ← match the source's actual change rate
  Authority:     publish-to-bot (authoritative)  vs  reference-only

Generative-answers settings:
  Grounding:     Strict        ← answer ONLY from sources; refuse when unsupported
  Citations:     required      ← every answer cites the source row/page
  Confidence:    raise threshold → low-confidence routes to "I don't know" / escalation, not a guess
  Content moderation: ON

Per-source acceptance test: add source → run topic-specific 5–10 prompt set → verify no regression.
```

**Do:**
- Curate **canonical** sources per topic area; one authoritative source beats ten overlapping ones.
- Set each source's **refresh interval** to its real change rate (a daily-changing page indexed weekly serves stale answers).
- Resolve contradictions/duplicates in the **source content** before adding more sources.
- Enable **strict grounding + required citations**; raise the confidence threshold so low-confidence → escalate, not hallucinate.
- Treat sources that ingest untrusted user content as a prompt-injection surface — route the design to `security-reviewer`.

**Don't:**
- "Set the bot loose on the intranet" — broad, uncurated indexing is the canonical anti-pattern.
- Leave grounding on a permissive mode for a customer-facing agent.
- Add a new source without running the topic-specific regression set.

## Edge cases / when the rule does NOT apply

- A **single, small, authoritative document set** (one product manual) needs little curation — the discipline scales with source sprawl.
- **Reference-only** sources are legitimately broader than authoritative ones, as long as authority is marked so the agent weights citations correctly.
- When the requirement is **custom RAG over a vector store** or fine-tuning, you may step outside Copilot Studio's generative answers to AI Builder / prompt-flow / direct Azure OpenAI — but you then own moderation and grounding yourself (skill §8).

## See also

- [`copilot-topic-vs-generative-routing.md`](./copilot-topic-vs-generative-routing.md) — routing decides *when* generative answers run at all
- [`copilot-escalation-and-guardrails.md`](./copilot-escalation-and-guardrails.md) — low-confidence answers should escalate, not guess
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Copilot Studio — Grounding source choice`
- [`../skills/copilot-studio-bot-design/SKILL.md`](../skills/copilot-studio-bot-design/SKILL.md) — §3 knowledge-source hygiene, §6 guardrails
- [`../knowledge/copilot-agents-2026.md`](../knowledge/copilot-agents-2026.md) — governance / DLP / Purview for ingesting untrusted content
- [`../agents/copilot-studio-engineer.md`](../agents/copilot-studio-engineer.md) — owner

## Provenance

Grounded in [Add knowledge sources](https://learn.microsoft.com/microsoft-copilot-studio/knowledge-add-knowledge), [Generative answers grounding](https://learn.microsoft.com/microsoft-copilot-studio/nlu-generative-answers), and the in-house [`copilot-studio-bot-design`](../skills/copilot-studio-bot-design/SKILL.md) skill §3 ("knowledge-source hygiene is the #1 hallucination prevention") (retrieved 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
