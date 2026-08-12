---
description: "Name the storage surface a write lands on — who holds the bytes, who executes the write, and the trust model that comes with it. Reach for this before writing any memory design down."
argument-hint: "[the situation, e.g. the store / agent / workload in question]"
---

# Map memory surface

You are running `/memory-engineering:map-memory-surface` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Answer the two questions in writing — Who holds the bytes, and who executes the write (§3 #4).
2. Separate durable memory from context pressure — Clearing and summarization shrink a live prompt; neither survives the session (§3 #4).
3. Name the surface as one of five — Client-side memory tool, context editing, compaction, instruction files + auto memory, server-side memory stores; consolidation is a separate decision (§3 #4).
4. Read today's status, strings and caps from the knowledge file — With the `Last verified` date, and note what happens *at* each cap: fail loudly, or drop silently (§3 #4).
5. Walk the sharp edges for that surface — Virtual path prefixes and traversal, implementer-owned safeguards, attach-time-only access, retrieve-then-rewrite rollback (§3 #4 #6).
6. Record it — Surface, byte-holder, write executor, status, the date you read it, caps and their failure modes (§3 #4).

## Output
A named surface with its byte-holder, write executor, dated release status, caps and failure modes, and the sharp edges that apply. Traverse Tree 2 in the decision-trees file. See [`../skills/map-memory-surface/SKILL.md`](../skills/map-memory-surface/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- Never quote a header string, status or cap from recall — read it from [`../knowledge/memory-surfaces-2026.md`](../knowledge/memory-surfaces-2026.md) and carry its date; the sweep reports age, never correctness.
- An instruction file is context, not enforcement — to block an action, name a hook or a permission deny (§3 #6).
- No user data / memory-store contents in the output; end with owner / date / expected movement on each recommendation.
