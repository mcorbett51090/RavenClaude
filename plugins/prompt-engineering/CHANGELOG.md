# Changelog — prompt-engineering

All notable changes to this plugin are documented here. Versioning is semver, bumped
on every user-visible change and mirrored in `.claude-plugin/marketplace.json`.

## 0.1.2 — 2026-09-14

### Changed

- `prompt-implementation-engineer`: `model: opus` → `model: sonnet`. The role is the implementation half of an architect/engineer pair — bounded, well-specified work against a design made upstream — which is the `sonnet` row of the marketplace's tier table (`ravenclaude-core/knowledge/model-tier-delegation.md`), and the tier the earlier app-craft plugins (backend / frontend / api / database) already give their implementers. Enforced going forward by the marketplace's model-tier-fit CI gate (`check-model-tier-fit.py`, Gate 288). No behaviour change beyond the model the agent runs on; the architect sibling stays on `opus`.

## 0.1.0 — 2026-07-15

Initial release. The prompt & context engineering team — owns *the prompt and
context that go into the model, and the contract that comes out*, the layer no
existing AI plugin owned (the neighbors owned model choice, retrieval, eval-at-scale,
and system attack).

- **3 agents:** `prompt-architect` (decomposition / pattern / context / output
  contract), `prompt-implementation-engineer` (wording / few-shot / structured-output / templates),
  `prompt-reliability-engineer` (eval-regression / CI gate / versioning / prompt-layer
  injection defense).
- **4 skills:** prompt-pattern-selection, structured-output-design,
  context-window-engineering, prompt-eval-and-regression.
- **Knowledge bank (2 docs):** four Mermaid decision trees (pattern / structured-output
  / context-inclusion / injection defense) and a dated 2026 reference.
- **5 best-practices** and **2 templates** (prompt spec, prompt eval plan).
- Provider-neutral. Seams: `ai-coding-model-guidance` / `claude-api`,
  `ai-rag-engineering`, `llm-evaluation-engineering`, `ai-red-teaming`,
  `claude-app-engineering` / `backend-engineering`, `security-engineering`. Requires
  `ravenclaude-core@>=0.7.0`.

## [0.1.1] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

