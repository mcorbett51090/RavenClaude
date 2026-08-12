# Memory Threat Model (ASI06) — &lt;store&gt; — &lt;date&gt;

> The **defensive, design-time** sheet: trust boundaries, write reachability from untrusted input, the read-only inventory, and the audit/rollback path. The attack taxonomy itself is owned by [`ai-red-teaming`](../../ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md) — this is the complement a builder completes *before* an engagement, not a second copy of that row.
>
> **Persistence is the defining property.** A poisoned entry keeps acting long after the session that planted it, and fixing the prompt does not fix the agent (§3 #5).

## 1. Write paths — enumerate every one, including the ones the model drives

| # | Write path | Furthest upstream input | Reachable from untrusted input? |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

A path terminating in a fetched page, a tool result, another user's content, a subagent's output, or a file from outside the repo **is** reachable from untrusted input. The model calling the write tool is a write path even when no diagram shows it.

## 2. Read-only inventory

| Store / namespace | Classification | Set at session creation? | Reference material mounted read-only? |
|---|---|---|---|
| | read_only / read_write | | |

A write path reachable from untrusted input is a permanent injection channel, not a bug to be patched later.

## 3. Audit trail

| Question | Answer |
|---|---|
| Can you answer "who wrote this entry, when, in which session"? | |
| **Has that query actually been run** — before an incident, not during one? | |
| Version retention window `[verify-at-use]` | [memory surfaces](../knowledge/memory-surfaces-2026.md) |

## 4. Rollback — rehearsed, not assumed

| Question | Answer |
|---|---|
| Is there a restore endpoint, or is rollback retrieve-then-rewrite? | |
| Date rollback was last **performed** on this store | |
| Does a rollback after an erasure reintroduce erased content? (sequence it) | |

## 5. Detection — the step everyone skips

| Question | Answer |
|---|---|
| Can a poisoned entry be **found** in the store? | |
| What test proves that, and when did it last run? | |
| Does the incident runbook reach the **store**, or stop at the prompt? | |

## 6. Mitigations — mechanism, not document (§3 #6)

| Risk | **Mechanism that blocks it** | Evidence / document |
|---|---|---|
| | | |

**A mitigation whose subject is a file is not a control.** A remembered rule is one more input the model may weigh or ignore; to block an action use a hook or a permission deny. Reject any row whose mechanism column names a document.

## 7. Boundaries

- Offensive testing of this store → [`ai-red-teaming`](../../ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md).
- Whether the store holds personal data, lawful basis, DSAR scope → [`data-governance-privacy`](../../data-governance-privacy/) and counsel (§2).
- What a delete leaves behind → the erasure section of the [design record](memory-design-record.md).

**Sources:** &lt;URL — retrieval date&gt; for every external claim; taxonomy IDs and titles shift between editions — re-verify before quoting one (§4).
