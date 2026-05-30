# claude-app-engineering — best-practice docs

Named, citable rules for building production applications on the Claude API, the Claude Agent SDK, and MCP. Each file is **one rule**, grounded in this plugin's dated, first-party-sourced knowledge bank ([`../knowledge/`](../knowledge/)) and (where grep-able) enforced by the `check-claude-app-anti-patterns.sh` hook. Read a doc whole and cite it; don't paraphrase a fragment.

These docs codify the cross-cutting **house opinions** in [`../CLAUDE.md`](../CLAUDE.md) §3 into copy-paste-grade guidance. Numeric / GA claims (model lineup, cache multipliers, minimums) are **dated** and live in [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md) — the platform ships monthly, so verify before quoting a client.

---

## Index

_20 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`agent-guardrail-the-loop.md`](./agent-guardrail-the-loop.md) | Absolute rule — an agent loop with no turn cap and no stop condition can burn your budget and take a destructive action unsupervised. | The moment you give the model a tool loop — the Agent SDK, Managed Agents, or a hand-rolled Messages loop — you've handed it autonomy, and autonomy wi… |
| [`agent-pick-the-build-surface.md`](./agent-pick-the-build-surface.md) | Absolute rule — defaulting to the Agent SDK for a single-shot call, or to Managed Agents when you already operate infra, is the named anti-pattern (#2). | There are four ways to build a Claude-backed feature — Workbench, Messages API (Client SDK), Claude Agent SDK, Managed Agents — and they are not inter… |
| [`cache-the-static-prefix.md`](./cache-the-static-prefix.md) | Absolute rule — never mutate tool definitions per request; it is the #1 cache-hit-rate killer. | Prompt caching is the single biggest cost and latency lever on the Claude API: a cache **read** is `0.1×` input cost, so a well-laid-out static prefix… |
| [`context-budget-the-1m-window.md`](./context-budget-the-1m-window.md) | Pattern — strong default; dumping the whole corpus/history "just in case" is the anti-pattern. | A 1M-token window (Opus 4.7, Sonnet 4.6 [verify-at-build]) is not a license to dump everything in. |
| [`context-keep-thinking-config-stable-and-dated.md`](./context-keep-thinking-config-stable-and-dated.md) | Pattern — strong default; toggling thinking mid-session busts the cache, and a version-specific thinking param hard-coded in app logic rots monthly. | Extended/adaptive thinking is a real quality lever for hard reasoning — but it has two sharp edges that quietly cost money and break in production. |
| [`cost-and-secrets-observability.md`](./cost-and-secrets-observability.md) | Absolute rule — you cannot manage a cost or a cache hit rate you don't measure; and `print(messages)` is a secret/PII leak (#8). | Every cost lever in this plugin — caching (`cache-the-static-prefix.md`), the routing ladder (`right-size-with-a-routing-ladder.md`), Batch — is invis… |
| [`cost-batch-the-async-work.md`](./cost-batch-the-async-work.md) | Pattern — strong default; running evals, backfills, or bulk enrichment at interactive rates is the named anti-pattern (#10). | A large fraction of a Claude app's token spend is *not* latency-sensitive: nightly evals, historical backfills, bulk document enrichment, dataset labe… |
| [`eval-the-retriever-separately.md`](./eval-the-retriever-separately.md) | Primary diagnostic — when a RAG answer is wrong, check retrieval before you touch the prompt. | In a RAG app, a wrong answer has two very different root causes: the right chunk was never retrieved (a retrieval failure) or the right chunk was retr… |
| [`evals-before-vibes.md`](./evals-before-vibes.md) | Absolute rule — "it looks better" is not a result. | Prompt, model, and tool-definition changes are invisible until they regress in production: a reworded system prompt that helps one case quietly breaks… |
| [`mcp-author-the-narrow-server.md`](./mcp-author-the-narrow-server.md) | Pattern — strong default; a sprawling server with 40 thin tools, non-idempotent effects, and trust-the-client auth is the failure shape. | An MCP server is a long-lived attack surface and a tool menu the model has to reason over — both get worse as the server grows. |
| [`mcp-vs-in-process-tool.md`](./mcp-vs-in-process-tool.md) | Pattern — strong default; standing up an MCP server for one app's one function is the named anti-pattern (#12). | A capability Claude can call lives in one of two homes, and picking the wrong one costs either reuse or needless operational weight. |
| [`output-structured-via-forced-tool.md`](./output-structured-via-forced-tool.md) | Absolute rule — parsing JSON out of prose (or asking for "JSON only" and hoping) is the named anti-pattern (#5). | When an app needs machine-readable output, the unreliable path is to ask Claude to "respond in JSON" and then parse the result with a regex or `json.l… |
| [`prompt-climb-the-leverage-ladder.md`](./prompt-climb-the-leverage-ladder.md) | Pattern — strong default; reaching for a multi-agent system before exhausting clear+direct+examples is the anti-pattern. | Most "the model won't do what I want" tickets are an underspecified prompt, not a model limitation — and the fix is almost always cheaper than the one… |
| [`rag-retrieve-quality-over-quantity.md`](./rag-retrieve-quality-over-quantity.md) | Pattern — strong default; "retrieve top-50 and let the model sort it out" is the failure mode that quietly tanks answer quality. | Once you've decided RAG is warranted (`rag-skip-it-under-200k.md`), the instinct is to maximize *recall* — pull more chunks so the answer is "definite… |
| [`rag-skip-it-under-200k.md`](./rag-skip-it-under-200k.md) | Pattern — strong default; building a retrieval pipeline for a corpus that fits in context is needless complexity. | RAG is a real engineering investment — chunking, an embedding model, a vector store, hybrid search, a reranker, an ingestion pipeline, and its own eva… |
| [`reliability-stream-and-back-off.md`](./reliability-stream-and-back-off.md) | Absolute rule — retrying a 429 immediately with no backoff is the named anti-pattern (#9); a blocking non-streamed call is a felt-latency regression for interactive UX. | Two reliability defaults separate a production Claude app from a demo. |
| [`right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md) | Pattern — strong default; defaulting every call to Opus is the anti-pattern. | Defaulting every request to the most capable model (Opus) is the most common way a Claude app overspends without buying quality. |
| [`tools-actionable-error-messages.md`](./tools-actionable-error-messages.md) | Pattern — strong default; returning a raw stack trace or a bare `500` as a tool result wastes the model's chance to self-correct. | In the Messages-API loop a failed tool call comes back to Claude as a `tool_result` — and Claude reads it exactly like any other context. |
| [`tools-design-as-a-contract.md`](./tools-design-as-a-contract.md) | Absolute rule — a thin tool description plus "the system prompt will fix it" is the named anti-pattern. | A tool is `{name, description, input_schema}`, and Claude decides *when* and *how* to call it almost entirely from those three fields — not from a sys… |
| [`untrusted-content-stays-untrusted.md`](./untrusted-content-stays-untrusted.md) | Absolute rule — letting a tool result or retrieved doc escalate tool access or auto-approve a destructive action is the named anti-pattern (#7); the security *verdict* is mandatory-escalated to core. | Anything that enters the context window from outside your prompt — a `tool_result`, a retrieved RAG chunk, fetched web content, a Files-API document, … |

---

## See also` (link this plugin's own knowledge/agents) · `## Provenance` · the `_Last reviewed:_` line.
3. Append a row to the index table above.
4. Cross-link from the relevant knowledge file and agent.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution + the house opinions these docs codify
- [`../knowledge/`](../knowledge/) — the dated, citation-grounded reference bank + the build-surface decision tree
- [`../../../docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) — the marketplace-wide doc template
