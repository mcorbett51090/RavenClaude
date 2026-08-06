# Memory Security and Privacy — Poisoning, Erasure Residue, Right to Erasure

**Last verified:** 2026-08-06 · the ASI06 taxonomy row is cited from this marketplace's own attack taxonomy, which carries its own dated volatility marker (reproduced below).

> **Re-verify before quoting.** Anthropic beta→GA transitions invalidate this file independently of its age; the 90-day sweep surfaces it on a date, it does not check it.

## The two failure modes, and why they are the same shape

A durable memory store fails in two directions:

1. **Something gets in that should not** — poisoning. The store becomes an injection channel that outlives the session that opened it.
2. **Something stays in that should be gone** — erasure residue. A delete removes the row and leaves the meaning.

Both are the same structural fact viewed from opposite ends: **a memory store is an input to every future session, and the write path is a trust boundary nobody drew.**

## 1. ASI06 — memory and context poisoning

**ASI06 — Memory & Context Poisoning** is a named, ranked entry in the OWASP Top 10 for Agentic Applications: *"Persistent corruption of the agent's memory / stored context so a later session misbehaves."* This plugin **cites** that row rather than re-deriving it; the canonical in-repo row lives at [`ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md`](../../ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md) `:91`, with the "what the LLM Top 10 does not cover" framing at `:99` and the volatility caveat at `:101`.

**The seam between the two plugins, stated once so neither drifts:**

> ASI06 (Memory & context poisoning) is an **attack-taxonomy** entry owned by [`ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md`](../../ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md) `:91` — that plugin scopes and executes the adversarial test. `memory-engineering`'s `memory-poisoning-review` skill is the **defensive design-time complement**: trust-boundary mapping, read-only-vs-read-write classification, and audit/rollback verification a builder applies *before* an ASI06 red-team engagement — not a second copy of the taxonomy row.

**Carried forward verbatim, not re-verified here:** the ASI series is a 2026 edition (published December 2025; **retrieved 2026-07-13 via `WebSearch`** because `genai.owasp.org` **403s automated fetch**, so IDs and titles were cross-referenced against the OWASP resource page plus F5, Promptfoo, Adversa and Giskard). Category names and IDs shift between editions — re-verify the current edition against the OWASP GenAI Security Project before quoting an ID in a deliverable.

## 2. Persistence, not injection, is the defining property

A prompt injection ends when the turn ends. **A poisoned memory keeps acting long after the session that planted it, and fixing the prompt does not fix the agent.**

That framing reaches this file from OWASP-derivative analyses via a search-result summary (**Medium** confidence), but it is **independently corroborated by the vendor's own documentation**, which is the citation to use:

> "If the agent processes untrusted input … a successful prompt injection could write malicious content into the store. **Later sessions then read that content as trusted memory.** Use `read_only` for reference material."
>
> — https://platform.claude.com/docs/en/managed-agents/memory (retrieved 2026-08-06)

That is a vendor warning about its own product, on the page for the surface it applies to. It is the strongest single sentence in this file.

**The operational consequence:** an incident response that patches the prompt and closes the ticket has fixed nothing. The response has to reach the **store**: find what was written, when, and by which session, and either roll it back or prove it was never read.

## 3. The attack shapes worth knowing

**Query-only memory injection (MINJA).** The attacker needs **no access to the memory store at all**. They interact with the agent as an ordinary user, through ordinary queries, and the resulting reasoning traces are written to memory — then later **retrieved as few-shot demonstrations for other users**. The trust boundary the designer assumed (only privileged writers can write) never existed: the model itself is the writer, and the user's input steered it.

**Percentages are deliberately omitted.** The paper reports injection and attack success rates; those figures reached this run only through a search-result summary and were never fetched verbatim, and a precise two-decimal number carries an authority its provenance does not support. Cite the **shape**, and the paper: *Memory Injection Attacks on LLM Agents via Query-Only Interaction*, arXiv **2503.03704** — https://arxiv.org/abs/2503.03704 (retrieved 2026-08-06).

**Named families, as leads rather than findings** (each **Low** confidence, single search-result summary, none read primary this session): **AgentPoison** (trigger tokens clustered into poisoned entries in RAG embedding space) and **MemoryGraft** (poisoning a persistent experience store via a benign-looking artifact). Defensive work exists under arXiv 2606.12703, 2605.03482 and 2606.30566 — **titles only; do not cite any of these as evidence for a design decision.**

## 4. Three shipped controls — mechanisms, not advice

Most memory-security writing is exhortation. These three are things a platform actually ships, verified 2026-08-06.

| Control | What it does | Where |
|---|---|---|
| **`read_only` mounts** | Attach reference material so the filesystem itself refuses the write. Access is enforced at the filesystem level and can only be set **at session creation** | https://platform.claude.com/docs/en/managed-agents/memory |
| **Immutable versions + `redact`** | Every mutation creates a `memver_…` version — an audit trail and point-in-time recovery, retained 30 days. `redact` scrubs a historical version's content while preserving who/what/when, documented for "removing leaked secrets, PII, or user deletion requests" | ibid. |
| **External-import approval gate** | A *project*-level Claude Code memory file that imports a path outside the working directory triggers a one-time approval dialog; declining disables those imports permanently. User-scope imports bypass it | https://code.claude.com/docs/en/memory |

A fourth, adjacent one worth naming: **`content_sha256` preconditions** give optimistic concurrency on memory writes — the shipped answer to two writers silently clobbering each other, which is a correctness problem that becomes a security problem the moment one of the writers is untrusted.

**And the control that is not one:** an instruction file is not enforcement. The docs say CLAUDE.md and auto memory are "context, not enforced configuration," and that to block an action you use a **PreToolUse** hook. Never write a threat model whose mitigation column says "documented in the memory file."

## 5. Mapping the write-path trust boundary

The design-time review this plugin owns. Six questions; every one has to have a written answer before the store takes its first write.

1. **Enumerate every write path into the store.** Include the ones the model drives, not just the ones your code calls.
2. **For each, trace back to the furthest upstream input.** If any path terminates in a fetched page, a tool result, another user's content, a subagent's output, or a file from outside the repo, that path is **reachable from untrusted input**.
3. **Classify each store or namespace `read_only` or `read_write`,** and mount reference material read-only. A write path reachable from untrusted input is a permanent injection channel, not a bug to be patched later.
4. **Verify the audit trail exists and is queryable** — "who wrote this entry, when, in which session" has to be answerable before an incident, not during one.
5. **Verify rollback works, by doing it.** On a versioned store with no restore endpoint, rollback means retrieve-a-version-and-write-it-back, which itself creates a new version. Rehearse it.
6. **Test that a poisoned entry is *detectable*, not just that the prompt was fixed.** This is the step everyone skips, and it is the one that distinguishes a memory threat model from a prompt-injection one.

## 6. Deleting the row is not erasure

**The claim:** removing a memory's row does not necessarily erase the personal data it carried, because the derived artifacts retain it.

**The evidence, verified.** Text embeddings are invertible to a startling degree: a multi-step inversion method "is able to recover **92% of 32-token text inputs exactly**," and the authors "recover important personal information (full names) from a dataset of clinical notes." *Text Embeddings Reveal (Almost) As Much As Text*, Morris, Kuleshov, Shmatikov, Rush, EMNLP 2023 — arXiv **2310.06816**, https://arxiv.org/abs/2310.06816 (retrieved 2026-08-06). **Confidence: High.**

**The regulatory position, verified — and note precisely what it covers.** EDPB **Opinion 28/2024**, adopted **2024-12-17**: an AI model trained on personal data "cannot, in all cases, be considered anonymous"; anonymity must be assessed **case by case**, and requires that both the likelihood of extraction *and* the likelihood of obtaining personal data from queries be **insignificant**. The Opinion acknowledges that personal data "may still be embedded in the model's parameters through mathematical objects." Primary PDF: https://www.edpb.europa.eu/system/files/2024-12/edpb_opinion_202428_ai-models_en.pdf (retrieved 2026-08-06 via search-result listing; corroborated by three independent law-firm summaries). **Confidence: High.**

**The stated gap, and it matters.** That Opinion is about **models**, not vector stores, and **no regulator guidance addressed specifically at embeddings in an agent memory index was located.** The step from "a model's parameters can embed personal data" to "your memory index's vectors can too" is **this plugin's reasoned inference**, not settled law:

> Morris et al. show embeddings are invertible in practice; the EDPB reasons that mathematical objects derived from personal data are not automatically anonymous. Together those make **"delete the row, keep the vector"** an indefensible erasure story. **Teach that as an engineering inference. Do not imply it is settled law, and route the legal determination to the qualified authority.**

### What actually survives a delete

Write this list into the design record before the first write, because every item is a place an erasure request quietly fails.

| Residue | Why it survives | What to do about it |
|---|---|---|
| **Embeddings / vector rows** | Deleting the source text does not delete the derived vector, and vectors are invertible | Delete or re-index the vector in the same transaction as the row |
| **Immutable version history** | The audit trail is the point — versions survive deletion of the memory and are retained 30 days | Use the platform's **redact** operation; verify it actually applied |
| **Derived summaries** | A compaction, a consolidation output, or a "learned context" carries the fact forward under a new id | Enumerate every derived artifact at design time; there is no automatic cascade |
| **Cached prefixes** | An evictable cache is not a store of record, but the bytes exist until eviction | Do not model it as durable; do not model it as erased either |
| **Backups and exports** | Out of scope for the store's own API entirely | Answer this in the retention policy, not in the code |

### The sharp edge that breaks naive erasure implementations

**A version that is the current head cannot be redacted.** You must write a new version, or delete the memory, **first** — then redact. An implementation that calls redact on the live value silently fails on exactly the data the request was about, and returns success-shaped output. Verify erasure by reading back, never by checking a return code.

**And there is no restore endpoint.** Rollback is retrieve-then-rewrite, which creates a new version — so a rollback performed *after* an erasure request can reintroduce the erased content. Sequence matters.

## 7. What this file is not

This is an engineering file. **Whether a given store holds personal data, what lawful basis applies, whether a deletion request is in scope, and what a retention schedule must say are determinations for the qualified authority** — route them to [`data-governance-privacy`](../../data-governance-privacy/) and to counsel. The plugin's job is to make sure that when the determination arrives, the system can actually carry it out.

Two adjacent files carry the rest: the exact controls, headers and limits are in [memory surfaces](memory-surfaces-2026.md); what a delete costs and what a retention policy is worth are in [memory economics](memory-engineering-economics.md).
