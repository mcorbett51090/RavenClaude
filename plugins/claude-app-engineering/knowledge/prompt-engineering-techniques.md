# Prompt engineering techniques (the craft)

**Last reviewed:** 2026-05-28 · **Confidence:** high (Anthropic prompt-engineering guidance; durable). 
**Owner:** `prompt-and-context-engineer`. This is the **quality** craft — distinct from [`prompt-caching-playbook.md`](prompt-caching-playbook.md) (cost/latency) and the *artifact* work `ravenclaude-core/prompt-engineer` owns (agent/skill files). Here: making a *running app's* prompt produce the right output.

## The ladder — apply in order, stop when it's good enough
Anthropic's rough order of leverage (cheapest/most-effective first):
1. **Be clear, direct, and specific.** State the task, the audience, the format, and the constraints explicitly. Most "bad output" is an underspecified prompt. Tell Claude what TO do, not just what to avoid.
2. **Use examples (multishot).** 2-5 diverse, correct, edge-case-covering examples in the prompt do more than paragraphs of instruction. Wrap them in tags and keep them consistent with the output you want.
3. **Let Claude think (chain-of-thought).** For reasoning/analysis, ask for step-by-step thinking before the answer — or use **extended/adaptive thinking** (Sonnet 4.6) and read the thinking block. Don't CoT trivial tasks (latency/cost). (See [`context-engineering-2026.md`](context-engineering-2026.md) for thinking config.)
4. **Use XML tags to structure** input and output (`<document>`, `<instructions>`, `<example>`, `<answer>`). Claude is trained on them; they remove ambiguity about where one thing ends and another begins — and make output parseable.
5. **Assign a role / system prompt.** Put durable role + rules + tone in the `system` prompt (also the best thing to cache); keep the per-request task in the user turn.
6. **Prefill the assistant turn.** Start Claude's reply (e.g. `{` to force JSON, or a heading) to control format and skip preamble. (Not available with extended thinking.)
7. **Chain prompts** for complex multi-stage work — one focused prompt per stage beats one mega-prompt (see [`agent-orchestration-patterns.md`](agent-orchestration-patterns.md)).

## Output control (house opinion: structured output via tools, not regex)
- For **machine-readable** output, prefer a **forced tool call** (schema + `tool_choice`) over "return JSON" — see [`tool-use-and-structured-output.md`](tool-use-and-structured-output.md). Prefill `{` is the lighter fallback.
- For **prose**, specify the shape (headings, length, audience) and give one example of the target.

## Reliability techniques
- **Reduce hallucination:** allow "I don't know"; ground in provided context (RAG/long-context) and ask Claude to cite/quote the source span before answering; lower the stakes of guessing.
- **Long documents:** put the long doc **first** (cacheable), the question last; ask Claude to quote relevant passages before reasoning.
- **Consistency:** pin `temperature` low for deterministic tasks; keep the system prompt + examples stable (also protects the cache).
- **Guardrails:** keep untrusted/user content clearly delimited and labeled as data, never as instructions (injection — [`claude-app-finops-reliability-and-security.md`](claude-app-finops-reliability-and-security.md)).

## The loop (don't hand-tune blind)
Write the prompt → build a small **eval** set → measure → change one thing → re-measure ([`evals-and-quality.md`](evals-and-quality.md)). Use Anthropic's **prompt improver / Workbench** to generate a strong first draft, then iterate against the eval — not vibes (house opinion #4).

## Model-specific notes (dated)
Newer Claude models need *less* hand-holding and *fewer* "think step by step" nudges (they reason well by default; over-prompting can hurt). Adaptive thinking on Sonnet 4.6 supersedes manual CoT for hard tasks. Keep model-version-specific tactics in [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md), not baked into every prompt.

## Sources (retrieved 2026-05-28)
Anthropic prompt-engineering docs (be-clear-and-direct, multishot, chain-of-thought, use-XML-tags, system-prompts, prefill, chain-prompts, reduce-hallucinations) on platform.claude.com; the Workbench prompt improver.
