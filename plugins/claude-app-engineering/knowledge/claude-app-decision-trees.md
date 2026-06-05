# Claude app decision trees (canonical)

**Last reviewed:** 2026-05-30 · **Confidence:** high (grounded in this plugin's own knowledge bank — caching, model-selection, RAG, tool-use, MCP, evals, orchestration — all retrieved 2026-05-28; statuses dated).
**Owner:** all six agents (traverse the relevant tree **before** recommending — don't keyword-match on the user's situation).

This file collects the plugin's canonical `## Decision Tree:` sections in the marketplace's standard shape ([`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md)). The **build-surface** tree (Messages API / Agent SDK / Managed Agents / Workbench) already lives canonically in [`claude-build-surface-decision-tree.md`](claude-build-surface-decision-tree.md) `## Decision Tree: Claude Build Surface` — traverse it there; this file does **not** duplicate it. The sections below cover the model, retrieval strategy, single-document input mode, capability home (tool / MCP / prompt-only), and the eval-gate decisions.

> **Decision-tree traversal (priors).** When the user's situation matches a tree's entry condition, traverse the Mermaid graph top-to-bottom before selecting an approach. Do NOT pattern-match on keywords in the situation description. The first branch where the condition resolves cleanly is the leaf to apply. Every numeric/GA fact below is dated — confirm against [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md) before quoting a client.

---

## Decision Tree: Model selection — which Claude model for this task?

**When this applies:** A request needs a model assigned and the observable inputs are the task *shape* — is it high-volume classification/extraction/triage; is it general app work (drafting, summarizing, moderate reasoning, tool use); or is it the genuinely hard reasoning tail (deep agentic work, multi-file refactors, hard analysis). Use this **after** the build surface is chosen ([`claude-build-surface-decision-tree.md`](claude-build-surface-decision-tree.md)) — surface and model are orthogonal. Not for the deployment-target call (Claude API vs Bedrock/Vertex/Foundry).

**Last verified:** 2026-05-30 against [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md) (lineup dated 2026-05-28; the platform ships monthly — re-confirm the model ids).

```mermaid
flowchart TD
    A[Task needs a model] --> V{High-volume classify / extract / triage / eval-judge?}
    V -->|Yes| HAIKU[Haiku 4.5<br/>cheap + fast; default eval judge]
    V -->|No| G{General app work<br/>draft / summarize / tool use / moderate reasoning?}
    G -->|Yes| SONNET[Sonnet 4.6<br/>balanced default; 1M context; adaptive thinking]
    G -->|No, genuinely hard tail| LADDER{Can a cheap model triage<br/>+ escalate on uncertainty?}
    LADDER -->|Yes| RUNG[Routing ladder:<br/>Haiku triage -> Sonnet -> Opus on the hard tail]
    LADDER -->|No, uniformly hard / latency-bound| OPUS[Opus 4.7<br/>hardest reasoning, agentic depth; 1M context]
```

**Rationale per leaf:**

- _Haiku 4.5_ — high-volume, latency-sensitive, or schema-constrained extraction; also the **default eval judge**. Cheapest per token; right-size here before reaching up.
- _Sonnet 4.6_ — the **balanced default** for most app work (1M context, adaptive thinking). Start here unless an observable says otherwise.
- _Routing ladder_ — when uncertainty is measurable (schema-invalid output, low self-reported confidence, a judge flag), triage cheap and escalate; the metric is **cost-per-resolved-task**, not raw tokens — a Haiku call that fails and re-routes to Opus is *more* expensive than starting on Sonnet.
- _Opus 4.7_ — reserve for the genuinely hard tail (deep agentic reasoning, large-repo refactors) or when a multi-hop ladder's re-route cost / latency outweighs its savings. Don't *default* here unmeasured (anti-pattern #3).

**Tradeoffs summary table:**

| Model | Relative cost | Speed | Best for | Avoid when |
|---|---|---|---|---|
| Haiku 4.5 | lowest | fastest | volume classify/extract/triage; eval judge | the task needs deep reasoning the model can't reach |
| Sonnet 4.6 | mid | fast | general app work; balanced default; 1M context | proven-trivial work Haiku resolves (overspend) |
| Opus 4.7 | highest | slower | hardest reasoning / agentic depth; 1M context | as a blanket default "to be safe" (the #3 anti-pattern) |
| Routing ladder | mid (amortized) | varies | mixed difficulty where uncertainty is measurable | strict latency budgets (the extra hop adds round-trips) |

Re-baseline **deliberately** when the platform ships a new model — a default shift is an eval event ([`evals-and-quality.md`](evals-and-quality.md)), not a silent swap.

---

## Decision Tree: Retrieval strategy — long context vs Files API vs RAG

**When this applies:** Claude must answer over a corpus and the observable inputs are corpus **size** (does it fit under ~200K tokens [verify]), **volatility** (static vs dynamic/per-tenant/frequently-updated), the **shape per request** (a handful of known files vs search over a big/growing KB), and whether you **must surface citations**. Not the chunking/rerank *internals* (that's [`retrieval-and-rag-2026.md`](retrieval-and-rag-2026.md) once you're on the RAG branch).

**Last verified:** 2026-05-30 against [`retrieval-and-rag-2026.md`](retrieval-and-rag-2026.md) (Anthropic Contextual Retrieval + cookbook, 2026-05-28). The ~200K threshold and 1M window are dated — verify.

```mermaid
flowchart TD
    A[Need Claude to answer over a corpus] --> Q{Corpus < ~200K tokens AND fairly static?}
    Q -->|Yes| LC[Long context + prompt caching<br/>hold the corpus inline, cache the prefix]
    Q -->|No| F{A handful of KNOWN files per request?}
    F -->|Yes| FILES[Files API<br/>upload once, reference by id]
    F -->|No, search a big/growing/dynamic KB| RAG[Contextual Retrieval pipeline<br/>contextual chunks + hybrid + RRF + rerank]
```

**Rationale per leaf:**

- _Long context + caching_ — under the threshold + static, the whole corpus sits above a cache breakpoint and reads at 0.1× input; simpler, faster, often cheaper than any pipeline. Skip RAG ([`../best-practices/rag-skip-it-under-200k.md`](../best-practices/rag-skip-it-under-200k.md)).
- _Files API_ — a known small set of documents per request: upload once, reference by id, avoid re-sending bytes every call. The middle ground between "hold inline" and "full RAG."
- _Contextual Retrieval pipeline_ — large, dynamic, per-tenant, or citation-required corpora: retrieve a tight, high-precision slice (quality over quantity — [`../best-practices/rag-retrieve-quality-over-quantity.md`](../best-practices/rag-retrieve-quality-over-quantity.md)).

**Tradeoffs summary table:**

| Strategy | Setup cost | Per-request cost | Freshness | Citations | Use when |
|---|---|---|---|---|---|
| Long context + caching | none | low (cached 0.1×) | static only | weak (whole corpus in window) | small + static corpus |
| Files API | low (upload once) | low (by-id reference) | per-upload | per-file | a handful of known files per request |
| Contextual Retrieval (RAG) | high (pipeline + eval) | mid (retrieve + generate) | dynamic / per-tenant | strong (chunk→source) | large/dynamic KB; must cite sources |

A "fine-tune-equivalent" outcome (domain adaptation) is reached on Claude via **better context** — retrieval + examples + a strong system prompt — not a weight update; this tree is that adaptation lever. Eval the retriever **separately** from the generator on the RAG branch ([`../best-practices/eval-the-retriever-separately.md`](../best-practices/eval-the-retriever-separately.md)).

---

## Decision Tree: Document input — native PDF/image, pre-extracted text, or Files API?

**When this applies:** the app feeds **one document** (or a known small set) to Claude — a contract, invoice, report, scanned form — and the observable inputs are: does the task need the document's **visual layer** (layout, tables, figures, handwriting, charts) or just the **words**; is the **same document reused** across many requests/turns; and what's the **volume** (native document tokens are a real line item at scale). This is the _single-document input-mode_ fork; for answering over a _corpus_ (many documents, search), use the retrieval-strategy tree above instead. The failure it prevents: defaulting to "just send the PDF" (cost) or naive text extraction that discards the layout the task needed (fidelity).

**Last verified:** 2026-05-30 against [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md) + [`server-side-tools-and-files.md`](server-side-tools-and-files.md) (Anthropic vision + Files API docs, 2026-05-28). Vision-model support, per-page token costs, and Files API retention/limits are volatile — `[verify-at-use]`, never quote from memory.

```mermaid
flowchart TD
    A[Feed a document to Claude] --> CORPUS{One document / known small set, or a whole corpus?}
    CORPUS -->|A corpus — search over many docs| SEERAG["Use the retrieval-strategy tree<br/>(long-context / Files API / RAG)"]
    CORPUS -->|One document or a known small set| VIS{Does the task need the visual layer?<br/>layout / tables / figures / handwriting / charts}
    VIS -->|Yes — layout carries meaning| NATIVE["Native PDF / image to a vision-capable model<br/>confirm vision support in the capability map"]
    VIS -->|No — genuinely text-only| TEXT["Pre-extract text (OCR/parse), send the text<br/>cheaper, you control chunking"]
    NATIVE --> REUSE{Same document referenced across many requests/turns?}
    TEXT --> REUSE
    REUSE -->|Yes| FILES["Files API — upload once, reference by id<br/>pairs with native OR extracted input"]
    REUSE -->|No — one-shot| INLINE["Send inline this request<br/>native bytes or extracted text"]
```

**Rationale per leaf:**

- _SEERAG_ — a question spanning many documents is a retrieval problem, not an input-mode one; this tree is for getting a _single_ document into context. Skip RAG under ~200K tokens ([`../best-practices/rag-skip-it-under-200k.md`](../best-practices/rag-skip-it-under-200k.md)).
- _NATIVE_ — when layout/tables/figures/handwriting/charts carry meaning, send the document natively to a vision-capable model; pre-extraction here silently drops the signal the task needed. Costs more tokens per page — justified only when fidelity > cost.
- _TEXT_ — a genuinely text-only document (plain article, text contract clause) needs only the words; pre-extract to cut cost and control chunking. Lossy for anything visual — don't use where layout matters.
- _FILES_ — the same document referenced across many requests/turns: upload once via the Files API, reference by id, stop re-sending bytes every call. Pairs with either native or extracted input.
- _INLINE_ — a one-shot, low-reuse read: send it inline this request and move on; the Files API's upload step isn't worth it for a single use.

**Tradeoffs summary:**

| Input mode | Per-page/token cost | Fidelity | Reuse efficiency | Use when |
|---|---|---|---|---|
| Native PDF / image | Highest (vision tokens) | Full (visual layer) | Low (re-sends bytes) | Layout/tables/figures/handwriting matter |
| Pre-extracted text | Low | Lossy (words only) | Low | Genuinely text-only documents |
| Files API (native or text) | Low after upload | Inherits chosen mode | Highest (by-id) | Same document reused across requests |
| Inline one-shot | Per-request | Inherits chosen mode | n/a | One-off, low-volume read |

This tree operationalizes [`../best-practices/multimodal-extract-vs-native-document-input.md`](../best-practices/multimodal-extract-vs-native-document-input.md); at volume, measure cost-per-resolved-task and pre-extract where the visual layer adds nothing.

---

## Decision Tree: Capability home — prompt-only vs in-process tool vs MCP server

**When this applies:** Claude needs to *do* something and the observable inputs are: does the task need an **external call/effect at all** (vs reasoning over what's already in context); is the capability **reused across apps/agents/clients** or app-specific; and is it **coupled to one app's state** or independently runnable. Not for Anthropic-hosted server tools (computer use / code execution / web / Files / memory — a separate category, [`server-side-tools-and-files.md`](server-side-tools-and-files.md)).

**Last verified:** 2026-05-30 against [`mcp-server-authoring.md`](mcp-server-authoring.md) + [`tool-use-and-structured-output.md`](tool-use-and-structured-output.md) (modelcontextprotocol.io + Anthropic tool-use docs, 2026-05-28).

```mermaid
flowchart TD
    A[Claude needs to DO something] --> E{Needs an external call / effect at all?}
    E -->|No, reason over in-context info| PROMPT[Prompt-only<br/>climb the leverage ladder; no tool]
    E -->|Yes| R{Reused across apps / agents / clients?}
    R -->|No, app-specific or one-off| INPROC[In-process tool<br/>Messages-API or Agent SDK custom tool]
    R -->|Yes, multiple clients / its own service| MCP[MCP server<br/>narrow, idempotent, auth every request]
```

**Rationale per leaf:**

- _Prompt-only_ — if the answer is derivable from what's already in context, a tool is needless machinery; climb the prompt ladder instead ([`../best-practices/prompt-climb-the-leverage-ladder.md`](../best-practices/prompt-climb-the-leverage-ladder.md)).
- _In-process tool_ — app-specific, coupled to your app's state, or a one-off: ship the function (a Messages-API tool or an Agent SDK custom tool), skip the service overhead.
- _MCP server_ — reused across apps/agents/clients or wanted from Claude Desktop / Claude Code / your app interchangeably: author it **narrow, idempotent, authenticated** ([`../best-practices/mcp-author-the-narrow-server.md`](../best-practices/mcp-author-the-narrow-server.md)). Don't stand one up for a single app's single function (anti-pattern #12).

**Tradeoffs summary table:**

| Home | Build cost | Reuse | Coupling | Ops surface | Use when |
|---|---|---|---|---|---|
| Prompt-only | lowest | n/a | none | none | answer derivable from in-context info |
| In-process tool | low | none (one app) | tight to app state | none extra | app-specific / one-off capability |
| MCP server | high (service + auth + versioning) | across clients | independent process | a deployed, secured service | capability reused across apps/agents/clients |

All three apply the same contract discipline where a schema exists — name + description-as-prompt + typed schema ([`../best-practices/tools-design-as-a-contract.md`](../best-practices/tools-design-as-a-contract.md)). Auth/sandboxing of an MCP server escalates to `ravenclaude-core/security-reviewer`.

---

## Decision Tree: When to add an eval gate

**When this applies:** A change is about to ship and the observable input is **what kind of change** it is — a behavioral change to the prompt / model / tool definitions; a retrieval-pipeline change; a pure refactor with no behavior change; or a brand-new feature with no prior baseline. The question is whether CI needs an eval delta to gate it.

**Last verified:** 2026-05-30 against [`evals-and-quality.md`](evals-and-quality.md) + [`retrieval-and-rag-2026.md`](retrieval-and-rag-2026.md) (established LLM-eval practice + Anthropic guidance, 2026-05-28).

```mermaid
flowchart TD
    A[About to ship a change] --> B{Changes model output behavior?<br/>prompt / model / tool defs}
    B -->|No, pure refactor| SKIP[No eval gate<br/>rename/reformat doesn't change behavior]
    B -->|Yes| N{Prior baseline exists?}
    N -->|No, brand-new feature| FIRST[Ship WITH a golden set<br/>establish the FIRST baseline, not a delta]
    N -->|Yes| RT{Touches the retrieval pipeline?}
    RT -->|Yes| BOTH[Gate on retriever delta<br/>recall@k / MRR AND the answer delta]
    RT -->|No| GATE[Gate on the answer delta<br/>golden set; fail CI on regression > threshold]
```

**Rationale per leaf:**

- _No eval gate (refactor)_ — renaming a variable or reformatting code that doesn't touch the prompt/model/tools changes no behavior; the gate is for *behavioral* change.
- _Ship with a golden set (first baseline)_ — a brand-new feature has nothing to delta against, but still ships on a golden set, not vibes — it *establishes* the first baseline ([`../best-practices/evals-before-vibes.md`](../best-practices/evals-before-vibes.md)).
- _Gate on the answer delta_ — any prompt/model/tool-def change runs the golden set in CI and fails on a regression beyond threshold, failing cases enumerated; pin model + judge model + judge prompt so a baseline shift is intentional.
- _Gate on retriever delta too_ — a retrieval-pipeline change can drop recall@k while answers still "look fine" on the happy path; gate the retriever separately (recall@k / MRR) to localize the failure ([`../best-practices/eval-the-retriever-separately.md`](../best-practices/eval-the-retriever-separately.md)).

**Tradeoffs summary table:**

| Change kind | Eval gate? | What you measure | Why |
|---|---|---|---|
| Pure refactor (no behavior change) | none | — | no behavioral surface to regress |
| New feature (no baseline) | golden set, first run | absolute pass-rate | establishes the baseline; not vibes |
| Prompt / model / tool-def change | answer delta, CI | pass-rate delta vs pinned baseline | catches silent regressions before users do |
| Retrieval-pipeline change | retriever **+** answer delta | recall@k / MRR + answer delta | localizes retrieval vs generation failure |

A re-baseline on a new platform model is a **deliberate** eval event, not an automatic swap — the platform ships monthly and defaults change ([`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md)).

---

## Decision Tree: Orchestration shape — single call vs workflow vs agent

**When this applies:** A multi-step Claude-backed task needs a structure and the observable inputs are: **can the steps be predetermined** (a fixed pipeline) or must they be **decided dynamically** by the model; if fixed, is it **one step or many**; and does the task need **iterative refinement to a checkable rubric**. Use this once the build surface is chosen ([`claude-build-surface-decision-tree.md`](claude-build-surface-decision-tree.md)) — orchestration shape and surface are related but distinct (a workflow can run on the Messages API; an agent implies the Agent SDK / Managed Agents).

**Last verified:** 2026-05-30 against [`agent-orchestration-patterns.md`](agent-orchestration-patterns.md) (Anthropic "Building effective agents", durable, 2026-05-28).

```mermaid
flowchart TD
    A[Multi-step Claude task] --> R{Needs iterative refinement<br/>to a checkable rubric?}
    R -->|Yes| EO[Evaluator-optimizer loop<br/>generate -> evaluate -> repeat until it passes]
    R -->|No| P{Can the steps be predetermined?}
    P -->|No, dynamic decomposition| OW[Orchestrator-workers<br/>orchestrator delegates to workers, synthesizes]
    P -->|Yes| S{One step or many?}
    S -->|One| ONE[Single prompt + tools + retrieval<br/>the start-simple default]
    S -->|Many, fixed| WF[Workflow: chaining / routing / parallelization]
```

**Rationale per leaf:**

- _Single prompt + tools + retrieval_ — the **start-simple default**; a single well-prompted call with retrieval + good examples beats a multi-agent system for most tasks. Add complexity only when it measurably wins.
- _Workflow (chaining / routing / parallelization)_ — fixed, predeterminable steps: chain for sequential decomposition, route to send each input to a specialized prompt/model (the cost ladder), parallelize independent subtasks. Predictable, debuggable, cheaper than an agent.
- _Orchestrator-workers_ — the subtask shape is **unpredictable** (e.g. multi-file code changes): an orchestrator LLM decomposes and delegates, then synthesizes. **RavenClaude itself is this pattern.** Workers don't spawn workers.
- _Evaluator-optimizer_ — clear iterative quality gains against a checkable rubric: one model generates, another evaluates, loop until it passes.

**Tradeoffs summary table:**

| Shape | Predictability | Cost / latency | Autonomy | Use when |
|---|---|---|---|---|
| Single prompt + tools | highest | lowest | none | most tasks — the start-simple default |
| Workflow (chain/route/parallel) | high | low-mid | none (you wire the paths) | steps are fixed and predeterminable |
| Orchestrator-workers | low | higher | model decomposes dynamically | subtask shape is unpredictable |
| Evaluator-optimizer | medium | higher (loops) | bounded by the rubric | clear iterative gains to a checkable rubric |

Prove the added complexity with an **eval delta** before shipping it (house opinion #4) — autonomy buys outcomes at the cost of latency, tokens, and unpredictability; spend it deliberately. Any agentic leaf inherits the loop guardrails ([`../best-practices/agent-guardrail-the-loop.md`](../best-practices/agent-guardrail-the-loop.md)).

---

## Sources

Every leaf above is grounded in this plugin's own knowledge bank (all retrieved 2026-05-28, re-confirmed for these trees 2026-05-30): [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md), [`retrieval-and-rag-2026.md`](retrieval-and-rag-2026.md), [`mcp-server-authoring.md`](mcp-server-authoring.md), [`tool-use-and-structured-output.md`](tool-use-and-structured-output.md), [`evals-and-quality.md`](evals-and-quality.md), [`agent-orchestration-patterns.md`](agent-orchestration-patterns.md), and the canonical build-surface tree in [`claude-build-surface-decision-tree.md`](claude-build-surface-decision-tree.md). The platform ships monthly — re-verify every dated model id / GA status / threshold on the Researcher sweep and re-date the `Last verified:` lines.

---

## Decision Tree: Async delivery — polling vs streaming vs webhook

**When this applies:** A Claude task is expected to run longer than a synchronous HTTP timeout, or uses the Batch API, or involves a multi-step agentic job. Observable triggers: client timeout errors on long jobs; high polling costs; "how do I deliver results to the user for a job that takes minutes?"

**Last verified:** 2026-06-05 against Batch API and streaming documentation.

```mermaid
flowchart TD
    START[Claude task result needed] --> Q1{Is the user waiting in real time for incremental tokens?}
    Q1 -->|Yes| STREAM[Streaming SSE - server-sent events to the client]
    Q1 -->|No| Q2{Expected completion time vs client timeout}
    Q2 -->|Under 30 seconds and latency-sensitive| SYNC[Synchronous await - block and return]
    Q2 -->|Over 30 seconds or batch job| Q3{Can the client accept a callback or is it polling?}
    Q3 -->|Callback available| WEBHOOK[Webhook event handler - verified and idempotent]
    Q3 -->|Polling only| POLL[Exponential backoff poll - max 1 per 30s; store result in DB]
```

**Rationale per leaf:**
- *Streaming SSE* — token-by-token delivery for interactive UX; user sees progress immediately; client holds the connection.
- *Synchronous await* — short jobs where blocking is fine; simplest path; fails above load-balancer timeout.
- *Webhook event handler* — the preferred async path: producer posts a completion event; consumer handles idempotently; decoupled and restartable.
- *Exponential backoff poll* — last resort when the consumer cannot receive callbacks; cap poll frequency to avoid thundering-herd on status endpoints.

**Tradeoffs summary:**

| Method | Latency to user | Infra complexity | Blast radius on failure | Use when |
|---|---|---|---|---|
| Streaming SSE | Immediate incremental | Low | Client drop = lost stream | User waits; interactive |
| Sync await | Full job duration | None | Timeout kills the result | Short jobs only |
| Webhook + idempotent handler | Job duration + delivery | Medium | At-least-once = need dedupe | Long jobs; Batch API |
| Backoff poll | Job duration + poll lag | Low | Poll quota exhaustion | No callback infrastructure |

---

## Decision Tree: Injection risk — should this content touch tool permissions?

**When this applies:** A `tool_result`, retrieved document, fetched webpage, Files-API file, or user-supplied string is about to be inserted into the context window, and one or more tools in scope can perform destructive or privileged actions. Observable triggers: "can I pass this webhook payload to the model?"; "the user uploaded a PDF and I'm feeding it directly to an agent with write tools."

**Last verified:** 2026-06-05 against the AI-app security section of `claude-app-finops-reliability-and-security.md` (2026-05-28).

```mermaid
flowchart TD
    START[External content entering context] --> Q1{Does the content come from a fully trusted internal system with no user-controlled bytes?}
    Q1 -->|Yes| Q2{Do the in-scope tools have destructive or privileged effects?}
    Q1 -->|No - user input / third-party API / retrieved doc / web fetch| UNTRUSTED[Treat as untrusted]
    Q2 -->|No - read-only tools only| SAFE[Proceed - low injection risk]
    Q2 -->|Yes - write / delete / send / escalate| ESCALATE[Escalate design to security-reviewer before shipping]
    UNTRUSTED --> Q3{Do any in-scope tools auto-approve a destructive action?}
    Q3 -->|No - requires explicit human approval or read-only| SANDBOX[Sandbox the untrusted content - no auto-escalation]
    Q3 -->|Yes| BLOCK[STOP - restructure tool permissions; add human-in-the-loop gate]
```

**Rationale per leaf:**
- *Proceed (low risk)* — trusted internal content + read-only tools: injection cannot cause destructive effects.
- *Escalate to security-reviewer* — trusted source but destructive tool scope: even clean content deserves a review when the blast radius is high.
- *Sandbox the untrusted content* — untrusted content is allowed in context when no tool can auto-approve a destructive action; still follow the isolation rule.
- *STOP / restructure* — untrusted content with an auto-approving destructive tool is the canonical injection failure shape; restructure before shipping.

**Tradeoffs summary:**

| Content source | Tool scope | Required action | Owner |
|---|---|---|---|
| Internal trusted | Read-only | Proceed | `prompt-and-context-engineer` |
| Internal trusted | Destructive | Escalate to security-reviewer | `claude-app-ops-engineer` + core |
| External / user / retrieved | Read-only | Sandbox; no auto-approve | `prompt-and-context-engineer` |
| External / user / retrieved | Destructive | STOP; restructure; human gate | `core/security-reviewer` mandatory |

---

## Decision Tree: Context format — native document vs pre-extracted text vs Files API

**When this applies:** A document (PDF, image, long HTML page) must be fed to Claude and you must choose the input format. Observable triggers: "should I extract text before sending?"; "the PDF has charts I need Claude to read"; "I'm sending the same report to 50 requests today."

**Last verified:** 2026-06-05 against `knowledge/server-side-tools-and-files.md` and the multimodal best-practice (2026-05-28).

```mermaid
flowchart TD
    START[Document needs to enter context] --> Q1{Same document sent to multiple requests today - more than ~5?}
    Q1 -->|Yes| FILES[Files API - upload once reuse by file ID]
    Q1 -->|No| Q2{Document has layout-dependent content - charts, tables, mixed text-image?}
    Q2 -->|Yes| NATIVE[Native document input - PDF or image bytes in the message]
    Q2 -->|No - prose only and extractable cleanly| Q3{Extracted text fits within token budget without padding?}
    Q3 -->|Yes| TEXT[Pre-extracted text - cheapest; no vision tokens]
    Q3 -->|No - too long even pre-extracted| NATIVE2[Native + long-context model or chunk and retrieve]
```

**Rationale per leaf:**
- *Files API* — amortizes upload cost over many requests; mandatory for high-frequency same-document patterns (shared reference docs, nightly report, etc.).
- *Native document input* — layout matters (charts, tables, mixed content): native PDF/image input preserves spatial relationships; uses vision tokens.
- *Pre-extracted text* — prose-only documents where a clean extraction exists; cheapest (no vision tokens); loses layout.
- *Native + long-context / chunk* — document too long even as text; either use the 1M-context model directly or chunk and retrieve.

**Tradeoffs summary:**

| Format | Cost | Layout fidelity | Re-use | Use when |
|---|---|---|---|---|
| Files API | Upload once + cheap ref | As-native | High — many requests | Same doc, many requests |
| Native input | Vision token cost per request | Full | Low | Charts, tables, images |
| Pre-extracted text | Cheapest | None | N/A | Prose; clean extraction exists |
| Long-context / chunked | Model-tier cost | Full (long-context) | N/A | Doc too long for any single approach |
