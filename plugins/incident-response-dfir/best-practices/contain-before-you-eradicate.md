# Contain before you eradicate

**Status:** Absolute rule
**Domain:** Incident lifecycle (NIST SP 800-61r3, CSF 2.0-aligned; supersedes r2)
**Applies to:** `incident-response-dfir`

---

## Why this exists

The incident-handling phase is *Containment, Eradication & Recovery* — in that order — for a reason. If you start deleting malware and closing accounts while the adversary still has active access and lateral-movement paths, you tip them off, they burn their current foothold and pivot to another you haven't found, and you've turned a contained incident into a game of whack-a-mole against an alerted adversary. Containment stops the spread and freezes the blast radius so eradication can be *complete* rather than partial.

## How to apply

Once an incident is scoped, choose a containment strategy — short-term (isolate the host, disable the account, block the C2 domain/IP) to stop the immediate bleed, or long-term (rebuild in a clean segment) for a durable hold — *before* you eradicate. Only once spread is halted and scope is confirmed do you remove the root cause (malware, exploited vuln, compromised credentials, persistence), then recover to known-good and monitor.

**Do:**
- Halt spread first: isolate, disable, block — then confirm the adversary can't move.
- Scope fully before eradicating, so eradication removes *all* footholds at once, not one at a time.
- Sequence a coordinated eradication (rotate all compromised creds, remove all persistence) so the adversary loses access simultaneously.

**Don't:**
- Delete malware / close accounts piecemeal while the adversary is still active and watching.
- Jump to eradication before you know the full blast radius (you'll miss a foothold).
- Recover before eradicating root cause — you'll reintroduce the compromise.

## Edge cases / when the rule does NOT apply

- **Active, ongoing destruction** (ransomware actively encrypting) flips the priority to *stopping the harm now* — containment and eradication compress; isolate immediately even if scoping is incomplete.
- **Preserve evidence first** where containment is destructive — this rule is subordinate to [`preserve-evidence-before-you-remediate.md`](preserve-evidence-before-you-remediate.md): capture volatile evidence, then contain.

## See also
- [`../skills/run-the-incident-lifecycle/SKILL.md`](../skills/run-the-incident-lifecycle/SKILL.md)
- [`preserve-evidence-before-you-remediate.md`](preserve-evidence-before-you-remediate.md)
- [`../knowledge/incident-lifecycle-decision-tree.md`](../knowledge/incident-lifecycle-decision-tree.md)

## Provenance
Codifies the *Containment, Eradication & Recovery* phase ordering from NIST SP 800-61r2 (superseded by r3, 2025, CSF 2.0-aligned — cite r3 as current). Last reviewed 2026-07-08.

---

_Last reviewed: 2026-07-01 by `claude`_
