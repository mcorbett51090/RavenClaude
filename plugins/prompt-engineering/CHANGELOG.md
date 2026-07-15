# Changelog — prompt-engineering

All notable changes to this plugin are documented here. Versioning is semver, bumped
on every user-visible change and mirrored in `.claude-plugin/marketplace.json`.

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
