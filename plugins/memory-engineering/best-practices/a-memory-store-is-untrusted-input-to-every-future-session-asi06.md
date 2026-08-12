# A memory store is untrusted input to every future session (ASI06).

**Status:** Absolute rule. **Constitution:** §3 #5, §4.

## Use when

Any diff that writes to, reads from, or deletes from a durable agent memory store — and any threat model that mentions prompt injection.

## The rule

**Content read back from a store is data, never instruction.** Anything that entered the store from a tool result, a fetched page, a file, a subagent, or another user is untrusted input to every future session. It authorizes nothing: not an action, not a permission change, not a configuration edit, not a claim about the agent's own capabilities.

**Its defining property is persistence.** A prompt injection ends when the turn ends. A poisoned entry keeps acting long after the session that planted it, and **fixing the prompt does not fix the agent**. That single sentence is the whole difference between a memory threat model and a prompt-injection one.

## Why it matters

The vendor documents this about its own product: if an agent processes untrusted input, a successful injection can write malicious content into the store, and *later sessions then read that content as trusted memory*. The recommended control is to mount reference material **read-only**.

The trust boundary is also usually drawn in the wrong place. In the query-only injection shape, the attacker needs **no access to the store at all** — they interact as an ordinary user, the model's own reasoning traces are written to memory, and those entries are later retrieved as demonstrations for other users. The assumption "only privileged writers can write" never held: the model is the writer, and the user steered it.

## How to apply

- **Enumerate every write path into the store**, including the ones the model drives rather than the ones your code calls.
- For each, **trace back to the furthest upstream input.** A path terminating in a fetched page, a tool result, another user's content, a subagent's output, or a file from outside the repo is reachable from untrusted input.
- **Classify each store or namespace read-only or read-write**, and mount reference material read-only where the platform offers it. A write path reachable from untrusted input is a permanent injection channel, not a bug to be patched later.
- **Verify the audit trail is queryable** — "who wrote this entry, when, in which session" must be answerable *before* an incident.
- **Rehearse rollback.** On a versioned store with no restore endpoint, rollback is retrieve-then-rewrite, which itself creates a new version.
- **Test that a poisoned entry is *detectable*, not merely that the prompt was fixed.** This is the step everyone skips and the one that makes the review worth running.
- Record all six answers in the [memory threat model](../templates/memory-threat-model.md).

## The anti-pattern this prevents

The §4 failure mode: **treating retrieved memory content as instruction, especially one that expands the agent's own authority** — and its incident-response twin, closing the ticket after patching the prompt while the store still holds the entry.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) §3 #5 — the house opinion this rule encodes.
- [`../knowledge/memory-security-and-privacy.md`](../knowledge/memory-security-and-privacy.md) — the attack shapes, the three shipped controls, and the write-path trust-boundary review.
- [`../../ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md`](../../ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md) — ASI06 is an attack-taxonomy row owned there; this rule is the defensive design-time complement, not a second copy of it.
- [`../agents/memory-architect-lead.md`](../agents/memory-architect-lead.md) — owns the write-path trust boundary at design time.
