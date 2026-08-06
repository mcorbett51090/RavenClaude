---
scenario_id: 2026-08-06-poisoned-memory-survived-the-fix
contributed_at: 2026-08-06
plugin: memory-engineering
product: memory-store
product_version: "n/a"
scope: likely-general
tags: [asi06, poisoning, persistence, write-path, trust-boundary, read-only]
confidence: medium
reviewed: false
---

## Problem

An agent that summarized incoming documents began recommending an action nobody had approved. The team found the injected instruction in a fetched document, hardened the prompt, deployed, and closed the ticket. **The behaviour came back four days later, from sessions that never saw the original document.** The risk: a poisoned memory keeps acting long after the session that planted it, and fixing the prompt does not fix the agent (§3 #5).

## Context

- A durable store the agent wrote to at the end of each summarization run.
- Fetched documents were untrusted input; the store was mounted read-write for convenience during the pilot.
- Constraint: nobody had written down which write paths were reachable from untrusted input (§3 #5).
- The incident was classified as prompt injection, so the response only touched the prompt.

## Attempts

- Tried: **re-reading the incident as a store incident, not a turn incident.** Outcome: the injected text had been written into the store on the original run and was being retrieved as trusted context by every later session — persistence, not injection, was the defining property (§3 #5).
- Tried: **enumerating every write path and tracing each to its furthest upstream input.** Outcome: three paths terminated in fetched pages or tool results. Two of them existed only because the model could call the write tool, which no diagram showed.
- Tried: **querying the audit trail for "who wrote this entry, when, in which session."** Outcome: the trail existed but nobody had ever run the query, so the first attempt was written during the incident rather than before it (§3 #5).
- Tried: **mounting the reference namespace read-only and re-running the flow.** Outcome: the filesystem refused the write. The pilot had never needed that namespace writable.

## Resolution

The fix was to **treat the store as the incident surface**: find what was written, when and by which session; roll it back; re-mount reference material read-only; and add a detection test that a poisoned entry is *findable*, not merely that the prompt was patched. The output was a completed [memory threat model](../templates/memory-threat-model.md) with the write paths enumerated, the read-only inventory, and a rehearsed rollback — rehearsed because on a versioned store with no restore endpoint, rollback is retrieve-then-rewrite and creates a new version.

**Action for the next engineer hitting this pattern:** **an incident response that patches the prompt and closes the ticket has fixed nothing.** Reach the store. Enumerate the write paths reachable from untrusted input, classify read-only versus read-write, verify the audit trail *before* you need it, and test that a poisoned entry is detectable. See [Tree 3](../knowledge/memory-engineering-decision-trees.md) and [the security file](../knowledge/memory-security-and-privacy.md); the offensive half of this — scoping and executing the adversarial test — belongs to [`ai-red-teaming`](../../ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md), not here.

Figures and platform behaviour in this narrative are illustrative and unverified — treat as `[unverified — training knowledge]`, and re-check every vendor control, cap and header string `[verify-at-use]` against [memory surfaces](../knowledge/memory-surfaces-2026.md) before any deliverable (§3 #8).
