# LLM-eval tooling & method map — 2026

> **Last reviewed:** 2026-07-07. Confidence: **medium** — this space moves fast. Every specific product
> name, model, price, or capability below is **[verify-at-use]**; treat it as a pointer, not a
> guarantee. For anything about **Claude / Anthropic** models specifically, do **not** answer from
> memory — verify against current docs (the marketplace's accuracy discipline).

## Method families (stable) → representative tooling (volatile)

| Method | What it does | Representative tooling `[verify-at-use]` |
|---|---|---|
| Assertion / rule-based harness | regex, schema, must-contain, code-exec checks | Pytest-style harnesses, promptfoo, custom CI scripts |
| LLM-as-judge | model grades outputs vs a rubric (absolute or pairwise) | Framework judges (OpenAI Evals, promptfoo, DeepEval, Braintrust, LangSmith, Ragas for RAG) `[verify-at-use]` |
| Human labeling | expert/crowd labels, pairwise arenas | Internal labeling UIs, arena-style pairwise tools `[verify-at-use]` |
| Online/production eval | logs, traces, implicit+explicit signals | Tracing/observability platforms with eval hooks `[verify-at-use]` |
| Guardrail / red-team | injection, jailbreak, PII, off-policy | Dedicated red-team/guardrail libraries + hand-built adversarial sets `[verify-at-use]` |

## Known LLM-judge biases to audit (stable list)

- **Position/order bias** — the option shown first (or as "A") wins more often. Mitigate: randomize order, run both orders.
- **Verbosity/length bias** — longer answers score higher regardless of quality. Mitigate: length-controlled pairs, watch the length-vs-score correlation.
- **Self-preference bias** — a judge favors outputs from its own model family. Mitigate: use a different judge model, or audit explicitly.
- **Leniency/anchoring drift** — scores creep over runs, or anchor to the first example. Mitigate: fixed anchors, periodic re-calibration.

## RAG-specific eval (route to `ai-rag-engineering`)

Retrieval quality (recall@k, MRR, nDCG) and answer groundedness/faithfulness are owned by
`ai-rag-engineering`'s evaluation surface — this plugin owns the *generation-quality* eval and the
harness/judge/CI machinery around it. Coordinate; don't duplicate.

## What to re-verify each time you cite this file

- Model names, context windows, and per-token prices (all move quarterly).
- Which judge models exhibit which biases (changes with model versions).
- Framework feature sets (judge templates, CI integrations, tracing hooks).
