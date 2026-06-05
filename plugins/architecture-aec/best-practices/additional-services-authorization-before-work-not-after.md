# Additional Services Authorization Before Work, Not After

**Status:** Absolute rule
**Domain:** Architecture/AEC
**Applies to:** `architecture-aec`

---

## Why this exists

An additional-services claim submitted after the work is done is a billing dispute. An authorization obtained before the work begins is a contract. The distinction determines whether the firm collects. In practice, the failure mode is not that the additional service isn't real — it is that the architect started the work because the relationship was good, the client's need was urgent, and asking for paper felt awkward. That awkwardness costs the firm the recovery. The rule exists because every "we'll sort it out later" conversation ends the same way.

## How to apply

Use a lightweight additional-services authorization (ASA) form for every out-of-scope request:

```
Additional Services Authorization
───────────────────────────────────
Project:         ________________
Date:            ________________
Request:         ________________
Reason for ASA:
  [ ] Change in program or scope by owner
  [ ] Request for additional options or studies
  [ ] Design changes after phase sign-off
  [ ] Unforeseen site/existing conditions
  [ ] Extended CA services beyond original schedule
  [ ] Other: ________________

Scope of additional service: ____________________________
Estimated fee:  $_______ ([ ] fixed  [ ] time-and-materials not to exceed $_______)
Schedule impact: ________________

Owner authorization:  ________________  Date: ________
Project architect:    ________________  Date: ________

Work may proceed after both signatures are obtained.
```

**Do:**
- Keep the ASA form to one page; the longer the form, the more likely it is to be deferred.
- Send the ASA the same day the out-of-scope request is received, before a single hour is logged to the new scope.
- Track cumulative ASA totals against the original fee in the project budget report — the ASA log is a secondary project economics document.

**Don't:**
- Work "pending authorization" and chase the signature later — "pending" billing is the most common uncollected additional-services category.
- Lump multiple ASA requests into a single large form at the end of a phase — each request should be individually authorized at the time it arises.
- Confuse design iterations within the agreed scope with additional services — the phase scope and sign-off define the baseline; only work outside that baseline triggers an ASA.

## Edge cases / when the rule does NOT apply

Emergency site conditions requiring immediate action may not allow advance authorization. Document the decision to proceed, notify the owner in writing within 24 hours, and follow with an ASA form within 72 hours. The notice record is the substitute authorization.

## See also

- [`../agents/aec-engagement-lead.md`](../agents/aec-engagement-lead.md) — owns scope management and ASA workflow.
- [`./scope-creep-is-the-margin-killer-control-additional-services.md`](./scope-creep-is-the-margin-killer-control-additional-services.md) — the governing rule on scope-creep management.

## Provenance

Codifies CLAUDE.md §3 #2 (scope creep is the margin killer — control additional services) with a specific pre-authorization instrument. The pre-authorization requirement is consistent with AIA B101 standard contract additional-services provisions and standard AEC contract-administration practice [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
