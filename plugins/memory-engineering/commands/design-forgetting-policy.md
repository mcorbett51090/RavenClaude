---
description: "Design retention and erasure before the first write — TTL, caps, consolidation timing, dedup, contradiction handling, and what a delete leaves behind. Reach for this on any durable store."
argument-hint: "[the situation, e.g. the store / agent / workload in question]"
---

# Design forgetting policy

You are running `/memory-engineering:design-forgetting-policy` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. State the default out loud — Nothing in this store forgets unless we make it; an unbounded store is a decision nobody made (§3 #3).
2. Choose the bound and project it — TTL, size/item cap, decay — via `memory_engineering_calc.py store-growth` (§3 #3).
3. Check the surface's own cap and its failure mode — Some caps fail the write, others drop the overflow silently at load (§3 #3 #4).
4. Decide where consolidation runs — Write path pays per turn, offline pays staleness, read time pays repeatedly (§3 #1 #3).
5. Write the dedup rule — Name the identity key; "same fact" is not a definition (§3 #3).
6. Handle contradictions — Detect, keep both with provenance, surface to a named human, record the resolution. **Never auto-merge** (§3 #3).
7. Separate staleness from poisoning — Once-true-and-aged is a retention defect; never-true from a reachable write path is a security incident (§3 #5).
8. Enumerate the erasure residue — Vectors, version history, derived summaries, cached prefixes, backups (§3 #7).
9. Rehearse the deletion and verify by reading back — Never by a return code; a redaction on a current head can return success and leave the value (§3 #7).
10. Hand off the legal determination — Route lawful basis, scope and schedule to the qualified authority (§2).

## Output
A retention and erasure policy with the bound and its projection, the consolidation position and its bill, the dedup key, the contradiction procedure with a named owner, and the residue list behind a rehearsed deletion. Traverse Tree 3 in the decision-trees file. See [`../skills/design-forgetting-policy/SKILL.md`](../skills/design-forgetting-policy/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- Never auto-merge a contradiction — surface it for a human decision, with both entries and their provenance intact (§3 #3).
- Deleting the row is not erasure; an erasure story that stops at the row is incomplete (§3 #7).
- No user data / memory-store contents in the output; end with owner / date / expected movement on each recommendation.
