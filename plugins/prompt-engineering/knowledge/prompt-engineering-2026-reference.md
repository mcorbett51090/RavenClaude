# Prompt-engineering 2026 reference (dated — verify at use)

> **Retrieval date: 2026-07-15.** The facts here — model capabilities, structured-
> output support, injection techniques, tooling — move fast. Every figure carries a
> re-verify-at-use rider per ravenclaude-core's Claim Grounding protocol. The
> *methods* in [`prompt-decision-trees.md`](prompt-decision-trees.md) are durable;
> the *facts* below are snapshots. When a claim gates an irreversible action,
> re-verify against the provider's current docs first.

## 1. Structured-output support (as of 2026-07, verify per model)

Three mechanisms, strongest first. Availability is model-specific — check the
provider's current docs for your exact model.

| Mechanism | What it gives you | Notes |
| --- | --- | --- |
| **Native structured / JSON-schema output** | Provider validates the output against a supplied JSON Schema | Strongest when available; still validate business rules yourself |
| **Tool / function calling** | Model emits arguments matching a tool's parameter schema | Universally useful — define the output *as* a tool and force the call |
| **Constrained decoding / grammars** (e.g. GBNF) | Token-level constraint to a formal grammar | Mostly self-hosted / open-weights runtimes |
| **Prose + parser** | Nothing enforced | Last resort — always with delimiters + repair retry |

**Durable rule (not dated):** whatever the mechanism, keep a parse → validate →
repair-retry → fail-closed path. A valid document can still be a wrong document.

## 2. Model capability axes that affect prompt design

These are the axes to check for *your* model at design time (values omitted
deliberately — they change per release):

- **Context-window size** — sets your token budget. Bigger is not free: cost,
  latency, and the lost-in-the-middle accuracy dip all scale with fill.
- **Native structured-output / tool-calling support** — determines §2's leaf.
- **Reasoning / "thinking" modes** — some models do CoT internally; explicit
  "think step by step" can be redundant or even counterproductive on those. Test.
- **Prompt caching** — many providers cache a stable prefix. Put the *stable*
  content (system instructions, schema, few-shot) first so it caches; put the
  *variable* content last. This is both a cost and a latency lever.
- **Determinism controls** — temperature, top-p, seed availability. Reproducible
  evals need these pinned.

## 3. Prompt-injection & jailbreak landscape (2026-07 snapshot)

Common technique families to include in a regression/red-team suite (treat as a
*starting* set — the field evolves):

- **Direct instruction override** ("ignore previous instructions…").
- **Indirect / data-borne injection** — malicious instructions embedded in
  retrieved documents, tool outputs, web pages, or file contents the model reads.
  The highest-risk class for RAG and agent systems.
- **Role-play / hypothetical framing** jailbreaks.
- **Encoding / obfuscation** (base64, translation, homoglyphs) to slip past
  keyword filters.
- **Payload splitting** across turns or fields.

**Durable defensive posture (not dated):** fence + label untrusted input as data;
separate instruction from data; constrain output to an allow-list; require
out-of-band authz + human-in-the-loop for high-impact actions; add every seen
attack to the suite; and **state that prompt-layer defense is necessary, not
sufficient.** Whole-system attacks → `ai-red-teaming`; authz/rate-limit/output-
moderation → `security-engineering`.

## 4. Prompt-eval methods (durable) with a dated caveat

- **Exact / schema-valid scoring** — for closed-form or structured tasks. Cheap,
  reproducible; use it wherever the task allows.
- **Rubric scoring** — human or model grades against explicit criteria.
- **LLM-as-judge** — scalable but the judge is itself a fallible prompt. *Dated
  caveat:* judge models have known biases (position, verbosity, self-preference).
  Validate the judge against human labels before trusting it; never let a model
  grade its own output unaudited.
- **Pairwise / A-B preference** — often more reliable than absolute scores for
  quality-ranking prompt variants.

## 5. Tooling categories (names change — verify current options)

- **Prompt management / versioning** — keep prompts in VCS at minimum; managed
  registries exist but are volatile, so evaluate current options at adoption time.
- **Eval frameworks** — offline eval + regression harnesses; the specific tools
  churn, so pick at build time and pin versions.
- **Observability / tracing** for LLM calls — capture inputs, outputs, tokens,
  latency, and model version for every call so a production regression is
  debuggable.

*(Specific product names are intentionally omitted here because they date fastest;
choose at build time against current docs and pin the version.)*

## 6. Cross-plugin seams (stable)

| Need | Plugin |
| --- | --- |
| Which model / model tradeoffs / pricing | `ai-coding-model-guidance`, `claude-api` |
| Retrieval design (chunking, embeddings, reranking) | `ai-rag-engineering` |
| Large offline eval program / benchmark design | `llm-evaluation-engineering` |
| Adversarial red-teaming of the whole system | `ai-red-teaming` |
| The app / API / orchestration around the prompt | `claude-app-engineering`, `backend-engineering` |
| App-layer security (authz, rate limits, moderation) | `security-engineering` |
