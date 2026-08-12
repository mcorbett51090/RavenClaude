---
name: memory-poisoning-review
description: "Audit an agent's durable memory for poisoning risk and harden it against OWASP ASI06 — enumerate write paths reachable from untrusted input, classify read-only vs read-write, verify audit and rollback. Reach for this when a diff touches a memory store."
---

# Skill: Memory poisoning review (OWASP ASI06)

**You were sent here by an inline prior on `ravenclaude-core/security-reviewer`, because the diff touches something that persists across sessions.**

**This is not a second rubric.** It is a set of priors that extend the rubric you already run. Nothing below replaces your review; it tells you which of your existing sections to point at a durable store, what a finding looks like there, and where the severity line sits. You need no memory-engineering background to execute it.

## The one thing that is different — read this first

You already know prompt injection. This is the same class with one property changed, and that property changes the fix:

> **A prompt injection ends when the turn ends. A poisoned memory keeps acting long after the session that planted it, and fixing the prompt does not fix the agent.**

The vendor says it about its own product, which is the citation to use:

> "If the agent processes untrusted input … a successful prompt injection could write malicious content into the store. **Later sessions then read that content as trusted memory.** Use `read_only` for reference material."
> — Anthropic managed-agents memory documentation (retrieved 2026-08-06)

**The operational consequence, and the thing to check for in the diff or the PR description:** an incident response that patches the prompt and closes the ticket has fixed nothing. The response has to reach the **store** — find what was written, when, and by which session, and either roll it back or prove it was never read. If the change you are reviewing is a prompt fix for a bad-memory incident, that alone is a finding.

## Where this attaches to your existing rubric

| Your section | The prior to add |
|---|---|
| **§2 Input handling** | The store is an **input**, to every future session — not a database the app owns. Trace each write back to its furthest upstream source, not to the function that called it |
| **§1 Identity & Access** | The model is a writer. Ask who may write *to a namespace*, not only who may call the endpoint |
| **§7 Logging & observability** | "Who wrote this entry, when, in which session" must be answerable **before** an incident, not during one |
| **§8 Defaults & failure modes** | Default the mount to read-only. A write path reachable from untrusted input is a permanent injection channel, not a bug to patch later |

## Triage — five questions, in order

Stop at the first one that fires; each has a defined verdict.

**Q1. Does this diff create, expand, or newly expose a path that writes something a *later* session reads?**
A memory store, a memory-tool handler, an instruction or memory file the agent edits, a vector row, a summary that replaces the turns it summarizes, a cache treated as durable.
→ **No** — this skill does not apply. Return to your normal review and say so explicitly, so the next reviewer knows it was considered.
→ **Yes** — continue.

**Q2. Can content originating from untrusted input reach that write path?**
Untrusted means: a fetched page, a tool result, a file from outside the repo, another user's content, a subagent's output, or *any ordinary user query whose text the model may echo into what it writes*. That last one is the trap — the attacker needs **no access to the store at all**; they talk to the agent as a normal user, and the agent is the writer.
→ **No, and you traced it** — record the trace as evidence and go to Q4.
→ **Yes, or you cannot tell** — go to Q3. "Cannot tell" is a **Yes** for this purpose.

**Q3. Is the reachable target mounted read-only, or scoped so the untrusted path cannot write it?**
→ **No** — this is the **Blocker** shape. Write it up as one (see calibration below).
→ **Yes** — record which control enforces it and at what layer, then continue. A comment or a documented convention is not a control.

**Q4. Can you answer "who wrote this entry, when, in which session" from an artifact that exists today?**
→ **No** — you cannot scope the blast radius of any future incident. Versioning or an audit trail comes before anything else in this area.
→ **Yes** — continue.

**Q5. Has rollback been *performed*, not just designed — and is a poisoned entry **detectable**?**
→ **No** — the standing finding, and the step everyone skips. See "the test nobody runs" below.

## The write-path trust boundary map

Six questions. Every one needs a **written** answer before the store takes its first write — the sheet for that is [`memory-threat-model.md`](../../templates/memory-threat-model.md). If the diff adds a store and the PR cannot answer these, that gap is the finding.

1. **Enumerate every write path into the store** — including the ones the model drives, not only the ones your code calls.
2. **Trace each one back to the furthest upstream input.** If a path terminates in a fetched page, a tool result, another user's content, a subagent's output, or a file from outside the repo, that path is **reachable from untrusted input**.
3. **Classify every store or namespace read-only or read-write,** and mount reference material read-only.
4. **Verify the audit trail exists and is queryable.**
5. **Verify rollback works, by doing it.** Where there is no restore endpoint, rollback means retrieve-a-version-and-write-it-back — which itself creates a new version. Rehearse it.
6. **Test that a poisoned entry is *detectable*, not just that the prompt was fixed.**

## Three controls that actually exist, and one that does not

Most memory-security writing is exhortation. Prefer a control a platform ships:

| Control | What it does |
|---|---|
| **Read-only mounts** | The filesystem itself refuses the write. Access may be settable **only at session creation**, with no mid-session promotion — check when it is set, not just that it is |
| **Immutable versions + a redaction operation** | Every mutation creates a version: an audit trail and point-in-time recovery, with its own retention window. Redaction scrubs a historical version's content while preserving who/what/when |
| **External-import approval gate** | A project-level memory file importing a path outside the working directory triggers a one-time approval; declining disables those imports permanently. User-scope imports may bypass it |

Adjacent and worth naming: a **content-hash precondition** on writes gives optimistic concurrency — the shipped answer to two writers silently clobbering each other, which becomes a security problem the moment one of them is untrusted.

**And the control that is not one:** an instruction file is context, not enforced configuration. To block an action regardless of what the model decides, the answer is a hook or a permission deny. **Never accept a threat model whose mitigation column says "documented in the memory file."** Flag it every time.

Exact strings, statuses and caps for these controls are dated and live in [memory surfaces (2026)](../../knowledge/memory-surfaces-2026.md) — read them there rather than from recall, and carry the date.

## The test nobody runs

Ask for one artifact: **a test that fails when a poisoned entry is present and passes when it is not.**

Almost every memory incident response tests that the *prompt* was fixed. That test passes on a still-poisoned store. If no such test exists, the finding is not "add a test" — it is that **the team currently has no way to know whether the store is clean**, which is a different and larger statement.

## Severity calibration

You have no domain background here, so use these lines rather than intuition.

**🔴 Blocker**
- A write path reachable from untrusted input lands in a store that is later read as trusted, with no read-only scoping and no provenance on the entry.
- Reference material mounted read-write with no stated reason.
- No audit trail on a store whose contents influence agent actions — the blast radius of any incident is unbounded and unknowable.
- A stored value is treated as an authorization decision, a permission, a configuration, or a claim about the agent's own capabilities.
- An erasure or rollback path whose success is asserted from a return code that was never read back.

**🟡 Concern**
- Audit trail exists but has never been queried; rollback designed but never rehearsed.
- No detectability test for a poisoned entry.
- Provenance recorded in the chat or the PR rather than **inline in the stored item** — a basis that was spoken and not written launders into an unmarked, trusted-looking prior.
- Dedup or consolidation that merges entries from different trust levels without recording which source won.

**✅ Done well** — say so, specifically. Read-only by default, provenance stamped into the entry, a rehearsed rollback, and a detectability test are all worth naming so they survive the next refactor.

## Boundaries — what this skill does not do

- **It does not run the attack.** Offensive testing of a memory store belongs to [`ai-red-teaming`](../../../ai-red-teaming/). Recommend an engagement; do not improvise one.
- **It does not make a legal determination.** Whether the store holds personal data, and what a deletion request requires, routes to [`data-governance-privacy`](../../../data-governance-privacy/) and to counsel. The engineering residue a delete leaves behind is [design-forgetting-policy](../design-forgetting-policy/SKILL.md).
- **It does not choose the surface.** If the diff has not decided who holds the bytes and who executes the write, that is [map-memory-surface](../map-memory-surface/SKILL.md) and it comes first.

## The seam with the attack taxonomy, stated once so neither side drifts

> ASI06 (Memory & context poisoning) is an **attack-taxonomy** entry owned by [`ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md`](../../../ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md) `:91` — that plugin scopes and executes the adversarial test. `memory-engineering`'s `memory-poisoning-review` skill is the **defensive design-time complement**: trust-boundary mapping, read-only-vs-read-write classification, and audit/rollback verification a builder applies *before* an ASI06 red-team engagement — not a second copy of the taxonomy row.

**Carried forward, not re-verified here:** the ASI series is a 2026 edition, retrieved **2026-07-13** via search because the OWASP site returns 403 to automated fetch, and cross-referenced against the OWASP resource page plus four independent analyses. Category names and IDs shift between editions — re-verify the current edition before quoting an ID in a deliverable.

Attack shapes, the corroborating vendor warning, and the erasure-residue half: [memory security and privacy](../../knowledge/memory-security-and-privacy.md).

## Output

Fold your findings into **your own** Output Contract — verdict, threat model, Blockers, Concerns, Done well, Out of scope. Add three lines to the threat model paragraph that a normal review would not carry:

```
**Write paths reachable from untrusted input:** <path — furthest upstream source — read-only? — provenance stamped?>
**Audit & rollback:** <trail exists / queryable / rollback rehearsed on: date>
**Detectability:** <the test that fails on a poisoned entry, or: none exists>
```
