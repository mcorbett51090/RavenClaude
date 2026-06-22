# Make the enforcement action proportional to the harm

**Status:** Absolute rule
**Domain:** Content moderation / enforcement design
**Applies to:** `trust-and-safety`

---

## Why this exists

The reflex when content is "bad" is to remove it and move on — but a single action for every violation is both over- and under-enforcement at once: it nukes a borderline first-offense the same as a repeat severe abuse, and it has nowhere left to escalate when the abuse is genuinely dangerous. Proportionality is the whole game (house opinion #1). The **enforcement ladder** — warn → limit → remove → suspend → ban — exists so the response fits the **severity × the user's history**, reserving the irreversible top rungs for the clear, severe, or repeat case. An over-enforced user is a wronged user (a trust cost); an under-enforced harm is a safety failure. Both are the failures this team prevents.

## How to apply

Traverse the [`enforcement-decision-tree.md`](../knowledge/enforcement-decision-tree.md): resolve severity tier and repeat-offender status, then take the **lowest rung that contains the harm**. Escalate on severity or history, never on annoyance.

```
Low / borderline, first  →  warn + de-amplify          (cheapest, reversible)
Medium, first            →  limit (rate-limit / restrict reach / remove item)
High, first              →  remove + strike
High, repeat             →  remove + temporary suspension
Repeat after suspension  →  permanent ban               (irreversible — last)
Critical / imminent harm →  immediate removal + suspend + escalate
```

**Do:**
- Map every action to a severity tier and the user's history before applying it.
- Prefer the reversible rung; reserve the ban for clear, severe, or persistent abuse.
- Record strikes so the ladder has the history it needs to escalate.

**Don't:**
- Apply one blanket action (usually "remove") regardless of severity.
- Jump to a permanent ban on a first or ambiguous offense.
- Let reviewer frustration, not the policy tier, set the action.

## Edge cases / when the rule does NOT apply

- **Critical / imminent-harm classes** (e.g. CSAM-class, credible threats) skip the gradual ladder — speed and the top action dominate, with specialist/legal escalation. Proportionality still holds: the harm *is* maximal.
- **Coordinated campaigns** may justify acting at the network level (many accounts) even on individually-low-severity items, because the aggregate harm is high.

## See also

- [`../knowledge/enforcement-decision-tree.md`](../knowledge/enforcement-decision-tree.md) — the ladder + severity triage tree.
- [`./appeals-are-due-process-not-optional.md`](./appeals-are-due-process-not-optional.md) — the companion rule: every rung carries an appeal.
- [`../agents/trust-safety-policy-lead.md`](../agents/trust-safety-policy-lead.md) — "enforcement is proportional".

## Provenance

Codifies house opinion #1 (proportionality) in [`../CLAUDE.md`](../CLAUDE.md) §3. Consensus Trust & Safety enforcement-ladder practice; domain-neutral.

---

_Last reviewed: 2026-06-17 by `claude`_
