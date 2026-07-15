# prompt-engineering

> A RavenClaude plugin: the prompt & context engineering team — the agents that own
> **the prompt and context that go into the model, and the contract that comes out.**

## What it is

A provider-neutral, 3-agent team for prompt engineering. It decomposes a task into
prompts, picks the prompting pattern, engineers the context window, defines and
enforces the output contract, and makes the result trustworthy in production
(eval/regression, CI gate, versioning, prompt-injection defense) — then hands the
*model choice* to `ai-coding-model-guidance` / `claude-api`, the *retrieval* to
`ai-rag-engineering`, and the *measurement-at-scale* to `llm-evaluation-engineering`.

It is **advisory and educational** — prompt-layer defense is necessary, not
sufficient; whole-system security routes to `security-engineering` / `ai-red-teaming`.

## Why it exists (the gap it fills)

Several AI plugins sit *around* a model, but none owned the prompt itself:

| Question | Owner |
| --- | --- |
| Which model, at what cost? | `ai-coding-model-guidance`, `claude-api` |
| How do we retrieve knowledge into the prompt? | `ai-rag-engineering` |
| How do we measure quality at scale? | `llm-evaluation-engineering` |
| How do we attack the whole system? | `ai-red-teaming` |
| **What prompt, what context, what output contract — and how do we keep it reliable?** | **this plugin** |

## Roster

| Agent | Owns |
| --- | --- |
| **`prompt-architect`** | Task→prompt decomposition, pattern selection, context-window engineering, the output-format contract. |
| **`prompt-implementation-engineer`** | Writing/iterating prompts, few-shot curation, structured-output plumbing, templates, token budgeting. |
| **`prompt-reliability-engineer`** | Eval/regression set, CI gate, prompt versioning & rollout, prompt-layer injection/jailbreak defense. |

## What's inside

- **4 skills** — `prompt-pattern-selection`, `structured-output-design`, `context-window-engineering`, `prompt-eval-and-regression`.
- **Knowledge bank (2 docs)** — four Mermaid decision trees (pattern / structured-output / context-inclusion / injection defense) and a dated 2026 reference (structured-output support, model capability axes, injection landscape, eval methods, tooling).
- **5 best-practices** — show-don't-tell, contract-the-output, the-window-is-a-budget, evaluate-prompts-like-code, untrusted-input-is-not-instructions.
- **2 templates** — prompt spec, prompt eval plan.

## Install

```shell
/plugin marketplace update ravenclaude
/plugin install prompt-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0` (inherits the Team Lead, the Capability Grounding
and Structured Output protocols, and the security/review seams).

## Seams

`ai-coding-model-guidance` / `claude-api` (which model) · `ai-rag-engineering`
(retrieval) · `llm-evaluation-engineering` (measurement at scale) · `ai-red-teaming`
(system attack) · `claude-app-engineering` / `backend-engineering` (the app) ·
`security-engineering` (app-layer controls).

This plugin owns **the prompt, the context, the output contract, and the
reliability of all three.** Everything else around the model belongs to someone else.
