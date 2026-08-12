---
description: "Audit an agent's durable memory for poisoning risk and harden it against OWASP ASI06 — write paths reachable from untrusted input, read-only classification, audit and rollback. Reach for this when a diff touches a memory store."
argument-hint: "[the situation, e.g. the store / diff / write path in question]"
---

# Memory poisoning review

You are running `/memory-engineering:memory-poisoning-review` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3. This extends an existing security rubric with memory-specific priors; it does not replace one.

## Steps (traverse top-to-bottom; do not skip)
1. Fix the frame — A poisoned memory keeps acting after the session that planted it, and fixing the prompt does not fix the agent; the response has to reach the store (§3 #5).
2. Triage Q1 — Does this diff create, expand or newly expose a path that writes something a *later* session reads? If not, say so explicitly and stop (§3 #5).
3. Triage Q2 — Can untrusted input reach that write path? Fetched pages, tool results, other users' content, subagent output — and any user query the model may echo into what it writes. "Cannot tell" counts as yes (§3 #5).
4. Triage Q3 — Is the reachable target read-only or scoped so the untrusted path cannot write it? A documented convention is not a control (§3 #5 #6).
5. Triage Q4 — Can you answer "who wrote this entry, when, in which session" from an artifact that exists today? If not, versioning comes before anything else (§3 #5).
6. Triage Q5 — Has rollback been performed, not just designed, and is a poisoned entry **detectable**? Ask for the test that fails on a poisoned store and passes on a clean one (§3 #5 #8).
7. Map the write-path trust boundary — Enumerate every write path, trace each to its furthest upstream input, classify read-only vs read-write, verify audit and rollback (§3 #5).
8. Prefer a shipped control over an exhortation — Read-only mounts, immutable versions plus redaction, the external-import approval gate, content-hash preconditions (§3 #5).

## Output
Findings folded into your own security Output Contract, plus three added threat-model lines: write paths reachable from untrusted input, audit and rollback status, and the detectability test (or its absence). See [`../skills/memory-poisoning-review/SKILL.md`](../skills/memory-poisoning-review/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- Never accept a threat model whose mitigation column says "documented in the memory file" — an instruction file is context, not enforcement (§3 #6).
- Do not run the attack: offensive testing of a memory store routes to [`ai-red-teaming`](../../ai-red-teaming/); the legal determination routes to [`data-governance-privacy`](../../data-governance-privacy/).
- Re-verify the current OWASP edition before quoting an ID; category names and IDs shift between editions.
- No user data / memory-store contents in the output; end with owner / date / expected movement on each recommendation.
