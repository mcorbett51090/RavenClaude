# Memory Engineering — Corrections, Provenance and the Six-Decision Spine

**Last verified:** 2026-08-06 · every external fact below carries a source URL and that retrieval date, or an explicit `[unverified]` marker.

> **Re-verify before quoting.** Anthropic beta→GA transitions invalidate this file independently of its age; the 90-day sweep surfaces it on a date, it does not check it.

## Corrections — claims that circulate and are wrong

This plugin was built from a widely-shared thread that got the shape of agent memory roughly right and **twelve specific claims wrong**. Each one is stated below in the form a reader will actually meet it, then corrected. This block is first on purpose: read it before anything else in the plugin, because every falsehood here is one a competent engineer would otherwise reproduce in good faith.

The single largest error was structural. The thread organised memory research into four *institutional lenses* — Stanford, Microsoft, Anthropic, NVIDIA — and naming a teaching unit after an institution creates an attribution slot that has to be filled. It got filled with the wrong lab. **This plugin uses six engineering decisions instead of institutional lenses**, and puts every citation in one provenance table below.

### C01 · "Two systems with identical accuracy differ by 47× in energy."

**Correction — false.** 47× is the **best-vs-worst** spread across the whole suite, between systems with **very different accuracy**: BM25 at 4,128 J per correct answer and **47.0%** accuracy, against Letta at 185,873 J / 27.7% and MIRIX at 144,629 J / **20.0%**. The paper's separate and much weaker sentence is that systems with *similar* accuracy differ by "an order of magnitude" — about 10×, not 47×. Keep the two numbers in separate sentences and never fuse them.
**Source:** arXiv 2606.06448, Fig. 4 + Table 3 — https://arxiv.org/html/2606.06448v1 (retrieved 2026-08-06).

### C02 · "The NVIDIA lens gives 4,290 vs 2,447 tok/s."

**Correction — the numbers are real; the attribution is fabricated.** There is **no NVIDIA lens.** Those throughput figures are Microsoft's, from MEMENTO (arXiv 2604.09852), measured on a single NVIDIA B200. The only two occurrences of that vendor's name in the paper are hardware descriptions; it authored nothing here and published nothing on this. If you want a hardware lens, call it *the serving lens* and carry the configuration with the number — 1× B200, Qwen3-8B, 240 concurrent requests at 32K — because these are high-concurrency, KV-pressure figures that do not transfer to low-concurrency serving.
**Source:** arXiv 2604.09852 §Throughput — https://arxiv.org/pdf/2604.09852 (retrieved 2026-08-06).

### C03 · "PlugMem beat purpose-built designs while spending fewer tokens."

**Correction — the paper says the opposite about total tokens.** Its own §Token Cost Analysis states that PlugMem's token usage is **comparable** to strong baselines and "remains within the **same order of magnitude**." Two real efficiency claims exist and are different: **injected-context** memory tokens drop by one to two orders of magnitude via the reasoning module's condensation, and **information density** (decision-relevant bits per memory token) is highest. The paper's cost argument is about per-token *pricing* (open-source models offline vs GPT-4o baselines), not token count.
**Source:** arXiv 2603.03296 — https://arxiv.org/pdf/2603.03296 (retrieved 2026-08-06).

### C04 · "Microsoft Research built PlugMem."

**Correction — wrong lead institution.** It is **UIUC**-led (Yang, He, Jiang, Han, Zhai), with **Tsinghua** and three MSR co-authors (Galley, Wang, Gao). Say "a UIUC-led collaboration with Microsoft Research," never "Microsoft Research's memory module."
**Source:** MSR publication page — https://www.microsoft.com/en-us/research/publication/plugmem-a-task-agnostic-plugin-memory-module-for-llm-agents/ (retrieved 2026-08-06).

### C05 · "Memory cuts first-pass errors by 97% and speeds verification by a third."

**Correction — two different customers' unaudited testimonials, generalised into a property of the technique.** The figures are real and attributable: Anthropic's launch post reports **Rakuten** citing 97% fewer first-pass errors and **Wisedocs** citing 30% faster verification. No methodology, baseline, sample size or independent audit is published, and no third-party corroboration was found. These are **vendor-published testimonials, not benchmarks**. Attribute them per-company with that limit, or drop them — never present either as an expected outcome of building memory. Confidence: **Low**.
**Source:** https://claude.com/blog/claude-managed-agents-memory (retrieved 2026-08-06).

### C06 · "Anthropic's memory is files on a filesystem."

**Correction — true of exactly one of five surfaces.** It describes **Managed Agents** memory stores (public beta), which mount into the session sandbox and are read and written with ordinary file tools. The **generally available memory tool is client-side**: Claude *requests* file operations and your application executes them, and `/memories` is a **virtual prefix your handler maps onto storage you own**. Collapsing the two misstates the security and data-residency model, which is the part that matters.
**Source:** https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool and https://platform.claude.com/docs/en/managed-agents/memory (both retrieved 2026-08-06).

### C07 · "Anthropic ships an Agent SDK memory API."

**Correction — no such documented surface exists.** Nothing by that name appears in the platform or Claude Code documentation index. What the Agent SDK actually inherits is the Claude Code surface: CLAUDE.md, auto memory, subagent memory and compaction. **Do not invent an API to fill the gap.** `[unverified — absence of evidence; a full `llms.txt` page enumeration was not completed this session]`
**Source:** absence checked against https://code.claude.com/docs/en/memory (retrieved 2026-08-06).

### C08 · "Memento manages its own context." — written with no arXiv ID

**Correction — two unrelated agent-memory papers carry that name, so a bare mention is ambiguous.** Microsoft's context-management **MEMENTO** is arXiv **2604.09852**; the unrelated case-based-reasoning agent **Memento** is arXiv **2508.16153**. A reader searching the bare name lands on the wrong one. Every mention anywhere in this plugin carries an ID or the word arXiv on the same line — that is an authoring contract, not a style preference.
**Source:** https://arxiv.org/abs/2604.09852 and https://arxiv.org/abs/2508.16153 (both retrieved 2026-08-06).

### C09 · "Attention is quadratic, so long context costs quadratically per token."

**Correction — the complexity claim is right about prefill and wrong about decode.** Prefill / full-sequence attention is O(n²) in prompt length, but with a KV cache, **per-decoded-token attention is O(n) — linear** in context length. And in production the binding constraint is usually neither: it is **KV bytes resident in HBM**, which caps concurrency. `[unverified — training knowledge]`: this correction follows from the definition of KV-cached autoregressive decoding rather than from a source fetched this session; it is textbook and not contested.
**Source (HBM half, verified):** arXiv 2604.09852 — "vanilla vLLM becomes KV-cache-bound" — https://arxiv.org/pdf/2604.09852 (retrieved 2026-08-06).

### C10 · "Prefix caching gives you cross-session memory."

**Correction — a prefix cache is an optimisation, never a memory tier.** vLLM's automatic prefix caching hashes KV blocks and, on exhaustion, **evicts blocks with reference count 0, least-recently-used first**. It is **opportunistic** and **replica-local**: a session that returns after eviction re-prefills from scratch, and a second replica never had the blocks at all. Never model it as persistence.
**Source:** https://docs.vllm.ai/en/stable/design/prefix_caching/ (retrieved 2026-08-06).

### C11 · "CLAUDE.md controls what the agent does."

**Correction — Anthropic's own documentation says CLAUDE.md and auto memory are "context, not enforced configuration."** The docs continue: "To block an action regardless of what Claude decides, use a PreToolUse hook instead." A memory-engineering design that names an instruction file as the control that prevents something has no control at all — it has a suggestion the model may weigh or ignore.
**Source:** https://code.claude.com/docs/en/memory (retrieved 2026-08-06).

### C12 · "The published, peer-reviewed 2606.06448 is Stanford's paper."

**Correction — it is a preprint, and it is not one institution's.** arXiv 2606.06448 v1 was submitted **2026-06-04** with **no venue**: never call it published or peer-reviewed. It is **Stanford-led** but **multi-institution** — Verhelst and Geens are KU Leuven. Its full title is *Agent Memory: Characterization and System Implications of Stateful Long-Horizon Workloads*; the truncated title that circulates drops the half that says what it measured.
**Source:** https://arxiv.org/abs/2606.06448 (retrieved 2026-08-06).

## How to read the rest of this file

The corrections above are the negative space. What follows is the positive content that survived verification: the spine the plugin teaches, one consolidated provenance table, the paradigm taxonomy, the baseline result that should embarrass most memory projects, and the landscape of shipped memory layers with the cost each one chooses to pay.

Four companion files carry the rest of the bank:

- [Memory surfaces (2026)](memory-surfaces-2026.md) — the five distinct storage surfaces, who holds the bytes, who executes the write.
- [Memory economics](memory-engineering-economics.md) — cost per correct answer, amortization, cache economics, growth.
- [Memory security and privacy](memory-security-and-privacy.md) — ASI06 poisoning, erasure residue, right-to-erasure.
- [Decision trees](memory-engineering-decision-trees.md) — the three traversals, in Mermaid.

## The six-decision spine

Memory engineering is six decisions, not four institutions. Each maps 1:1 onto one skill in this plugin.

| # | The decision | The question it answers | Evidence base |
|---|---|---|---|
| 1 | **What earns a write?** | Do you need memory at all, and if so which paradigm (I–IV)? | arXiv 2606.06448 |
| 2 | **Who holds the bytes, and who executes the write?** | Which storage surface owns this write, and what trust model comes with it? | Five shipped vendor surfaces (dated) |
| 3 | **What makes it forget, and what does erasure actually require?** | TTL, caps, consolidation timing — and what survives a delete | 2606.06448 Insight 7 + shipped mechanisms |
| 4 | **What can poison it?** | Which write paths are reachable from untrusted input | OWASP ASI06 + three shipped controls |
| 5 | **What does it cost, and when does it amortize?** | Build cost vs per-query saving, against a *named* baseline | 2606.06448 energy data + vendor billing docs |
| 6 | **How would you know it works?** | Golden set, judged failure modes, cost per correct answer | No trustworthy leaderboard exists — you build the bake-off |

**Why not institutional lenses.** Any lens framing keeps the attribution slot that produced C02, and it ages out the moment a paper is superseded. Six decisions map onto the six things a builder actually has to decide.

## Provenance — every paper this plugin cites

One table, so no citation lives inside a teaching unit named after a lab. All rows retrieved **2026-08-06**.

| Institution(s) | Full title | arXiv ID | Date | What it does **not** claim |
|---|---|---|---|---|
| Stanford-led, multi-institution (incl. KU Leuven) | Agent Memory: Characterization and System Implications of Stateful Long-Horizon Workloads | 2606.06448 | 2026-06-04 (v1) | Not published, not peer-reviewed — a preprint with no venue; and not one institution's |
| UIUC-led, with Tsinghua + Microsoft Research | PlugMem: A Task-Agnostic Plugin Memory Module for LLM Agents | 2603.03296 | 2026 | Not built by MSR alone (UIUC-led, Tsinghua co-authors); does not claim lower *total* token usage — comparable, same order of magnitude |
| Microsoft Research (10 authors) | MEMENTO: Teaching LLMs to Manage Their Own Context | 2604.09852 | 2026-04-10 (v1) | Not that vendor's whose B200 GPU it ran on — hardware only, not an author; and not the same work as arXiv 2508.16153 |
| — (unrelated; cited only to disambiguate) | Memento: Fine-tuning LLM Agents without Fine-tuning LLMs | 2508.16153 | 2025-08 | Not the same paper as arXiv 2604.09852 — do not conflate the two |
| Mem0 team | Mem0 (the LOCOMO claims paper) | 2504.19413 | 2025-04-28 | Numbers are self-reported and disputed by a competitor's methodological critique; not independently corroborated |
| Zep team | Zep: A Temporal Knowledge Graph Architecture for Agent Memory | 2501.13956 | 2025-01-20 | Bi-temporality is a product-docs claim, **not** stated in the paper abstract; Zep's own rebuttal figures are equally self-reported |

**LangMem has no row on purpose.** Its semantic / episodic / procedural taxonomy is cited by its documentation URL — https://langchain-ai.github.io/langmem/concepts/conceptual_guide/ (retrieved 2026-08-06) — because no arXiv paper backs it. Inventing an ID to make the table symmetrical would be the same error as C02 in miniature.

## Paradigms I–IV, along four axes

The taxonomy is the strongest asset in the source material and it survives verification intact. Two things are commonly conflated: the **four paradigms** and the **four axes** are different fours.

**The four axes** — how any system is classified: **construction · storage · retrieval · mutability**.

**The four paradigms** — what systems actually do:

| Paradigm | What it does | Named examples | The bill it pays |
|---|---|---|---|
| **I** — raw context | Prefill the full history at every query | long-context prompting | Zero construction cost; per-query cost grows with history |
| **II** — flat retrieval | LLM eliminated from construction; deterministic top-*k* | BM25, embedRAG | Cheap construction; amortizes almost immediately |
| **III.a** — structure-augmented extraction | LLM-mediated extraction into a graph/index | GraphRAG, HippoRAG v2 | Large-batch **offline** indexing traffic |
| **III.b** — consolidating fact store | LLM-mediated extraction into a mutable fact store | Mem0, SimpleMem | Sequential **per-event** traffic on the write-loop critical path |
| **IV** — agentic | The model decides when to write, which tool, whether evidence suffices | Letta, A-Mem, MIRIX | Same per-event traffic, **plus** each ingestion queries the growing store before writing |

The III.a / III.b split is not pedantry: it predicts the **shape** of the embedding traffic, which is what determines whether your write path is a batch job or a latency tax on every turn.

**Source:** arXiv 2606.06448 — https://arxiv.org/html/2606.06448v1 (retrieved 2026-08-06).

## What the Stanford-led study actually measured

Five findings, all directly quotable, all with load-bearing conditions.

1. **Construction energy exceeded all query-phase energy across the benchmark's 300 queries** for LLM-mediated systems. **300 is the benchmark's fixed query count, not a measured crossover point** — the paper never claims a break-even at 300. Frame this as *amortization*, and note that Paradigm II amortizes almost immediately while III and IV had not paid themselves back at the point the measurement stopped. Conditions: LongMemEval_S\*, 5 samples × ~360K tokens, Qwen3-32B + Qwen3-Embedding-0.6B on local vLLM.
2. **Energy per correct answer is the right unit, and the suite-wide spread exceeds 47× on a best-vs-worst basis** (BM25 4,128 J/correct → Letta 185,873 J/correct). Among *similar-accuracy* systems the gap is about one order of magnitude. See C01 above for why these two must never be fused.
3. **Nothing forgets by default** — "None of the evaluated systems prune or forget by default, so footprint grows monotonically under default behavior; bounding fleet storage requires an independent forgetting policy." This is the most directly actionable finding in the whole literature: retention is the operator's job, not the library's.
4. **Footprint varies ~9× at 1M tokens** (HippoRAG v2 ~62 MB, Mem0 ~12 MB) — but **token cost diverges far more sharply**, super-linearly for Paradigm IV. Storage is the tame axis. Long-term cost is set by the growth slope, not the initial footprint.
5. **Build wall-clock is the hidden number.** BM25 finished construction in ~16 minutes; SimpleMem took ~3.9 h and Letta ~14.4 h on the same corpus.

## The humbling baseline

**BM25 scored the highest accuracy in the suite (47.0%) *and* the lowest cost.** Every LLM-mediated system tested was both more expensive and less accurate on this benchmark.

That result should be the first slide of any memory proposal. Any guidance — including this plugin's — that does not make the reader seriously consider plain lexical retrieval first is selling something. The mandatory first step in [choosing a paradigm](memory-engineering-decision-trees.md) is proving the no-memory baseline **and** the flat-retrieval baseline lose on your own data.

## The landscape — four shipped memory layers, and the cost each chooses to pay

Every published number in this section is **self-reported by its vendor** or **reported by a competitor**. None is independently corroborated. Read them as claims about design intent, not as a ranking.

| System | Mechanism | The cost it chooses to pay |
|---|---|---|
| **Mem0** | LLM pass extracts salient facts per turn, then ADD / UPDATE / DELETE against a vector store (graph variant available) | **Write cost.** Every stored turn costs inference before it is ever read |
| **Letta** (formerly MemGPT) | In-context **memory blocks** (always visible, character-limited) + out-of-context recall and archival tiers searched by tool call; **sleep-time compute** edits blocks off the critical path | **Standing context cost.** Blocks occupy the window every turn; sleep-time compute buys latency relief with inference you pay for whether or not it is used |
| **Zep / Graphiti** | Temporal knowledge graph; entity/edge extraction with historical relationships preserved rather than overwritten | **Build and maintenance cost.** A graph database + extraction pipeline + temporal invalidation — the heaviest infrastructure, in exchange for contradiction handling the others approximate |
| **LangMem / LangGraph** | A taxonomy more than a store: **semantic** (facts), **episodic** (past experiences), **procedural** (evolving system behaviour); names the **hot path vs background** write fork explicitly | **It makes the cost an explicit choice.** Hot path pays latency; background pays staleness. Its contribution is naming the dial, not setting it |

Sources, all retrieved 2026-08-06: Mem0 https://arxiv.org/abs/2504.19413 · Letta https://docs.letta.com/guides/agents/memory-blocks and https://www.letta.com/blog/sleep-time-compute/ · Zep https://arxiv.org/abs/2501.13956 and the competitor critique at https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory/ · LangMem https://langchain-ai.github.io/langmem/concepts/conceptual_guide/.

**Two honesty notes.** The Letta sleep-time-compute paper's **arXiv identifier was not verified this session** — cite the blog and docs URLs, and do not fabricate an ID. And Graphiti's **bi-temporal** model is asserted in product documentation but is **not** in the Zep paper abstract — do not cite the paper for it.

## Benchmarks are contested, and there is no leaderboard worth citing

The two most-cited benchmarks are **LOCOMO** (multi-session conversational memory) and **LongMemEval** (500 questions across six categories including knowledge update and temporal reasoning). Both are contested:

- LOCOMO conversations run roughly 16k–26k tokens — comfortably inside a modern context window — so a long-context baseline with **no memory system at all** is a serious contender, which is exactly the C01/humbling-baseline problem again.
- Newer work argues that agents near-saturating LOCOMO "perform poorly in agentic settings," and that task-disclosed prompting plus string-matching metrics conflate memory fidelity with prompt adaptation. `[unverified — search-result summary, 2026-08-06; abstracts not primary-read]` — Locomo-Plus, arXiv 2602.10715, and arXiv 2602.16313.
- A public head-to-head of Mem0 vs Zep vs Letta by a neutral party **was not located**. One hobbyist repository surfaced; a single hobbyist repository is a lead, not a finding.

**The house position: every published memory-system ranking is self- or competitor-reported.** Do not cite one, do not build one into a slide, and do not let a vendor's benchmark stand in for your own. Build a golden set on your data and measure **cost per correct answer** — the procedure lives in [memory economics](memory-engineering-economics.md) and the eval skill.

## The two in-model results worth carrying

**MEMENTO (arXiv 2604.09852).** Segment reasoning into blocks → compress each into a dense note → evict that block's KV entries. Reported: ~**2.5×** peak KV-cache reduction and ~**1.75×** throughput on their vLLM fork (say 1.75×, not "nearly doubles"). The transferable finding is the **dual information stream**: the note's *text* is not the whole channel — its cached KV states carry information the text does not, and recomputing them without block context costs **15 percentage points on AIME24**, from a targeted ablation. Generalised: **a summary you re-encode from scratch is strictly weaker than one whose KV states you kept.**

**PlugMem (arXiv 2603.03296).** One unchanged, task-agnostic module exceeded task-specific memory designs across LongMemEval, HotpotQA and WebArena. Its efficiency claim is **information density** and **injected-context** tokens — see C03 for what it is not.

## Related knowledge in this marketplace

- Corpus retrieval, chunking and recall@k are a different discipline: [`ai-rag-engineering`](../../ai-rag-engineering/).
- Whether to build an agent at all, and its topology: [`ai-agent-engineering`](../../ai-agent-engineering/).
- Generic LLM eval harnesses: [`llm-evaluation-engineering`](../../llm-evaluation-engineering/).
- DSAR process, legal basis and records-retention policy: [`data-governance-privacy`](../../data-governance-privacy/).
