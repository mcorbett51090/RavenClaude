# End every QBR with named, dated, owned commitments — captured in the partner's words

**Status:** Absolute rule

**Domain:** QBR composition / Followups

**Applies to:** `edtech-partner-success`

---

## Why this exists

A QBR with no commitments is a status meeting (house opinion §3 #2). The named §4 anti-pattern — "partner had a great QBR" → no commitments captured → three months later the PSM doesn't know what was promised — is how trust quietly erodes across a partnership: the next QBR re-raises the same unresolved items, and the partner concludes the meetings are theater. Action items without dates and owners (§3 #13) are findings waiting to be re-raised. The other half of the rule is fidelity: "we'll explore that" written down as "Partner committed to X" is how trust gets *actively* broken — commitments get captured in the partner's words, not the PSM's optimistic paraphrase. The anti-pattern hook flags a followups slide that says only "we'll be in touch" and action items missing dates.

## How to apply

Make the penultimate slide a real commitment table, populate it live in the meeting, and run a cadence review before the next QBR.

```
Commitment capture discipline:
  PENULTIMATE SLIDE — "What we'll do next":
    | Commitment (partner's words) | Owner (named) | Date | Side (us / partner) |
    — every row needs an owner AND a date. "We'll follow up" is not a commitment.
  CAPTURE FIDELITY:
    record what the partner actually said. "We'll explore that" ≠ "Partner committed to X".
    Quote them; don't upgrade tentative language into a promise.
  AFTER THE MEETING:
    move commitments into the touchpoint log + the durable profile's "what we promised"
    section (sacred — most-likely-to-be-forgotten across PSM transitions).
    Schedule a cadence review — don't wait until the next QBR (3 months) to check progress.
```

**Do:**
- Populate the tracker *during* the meeting so commitments aren't reconstructed from memory afterward.
- Carry cross-functional commitments that exceed PSM authority (roadmap promises, custom dev) to `project-manager` rather than promising them in the room.

**Don't:**
- Let the followups slide read "we'll be in touch" — the hook flags it and the next QBR pays for it.
- Capture an in-meeting "maybe" as a firm partner commitment; record the actual hedge.

## Edge cases / when the rule does NOT apply

- **Pure information-share session** (not a QBR) — a roadmap preview with no decisions may legitimately end without commitments; then don't *call* it a QBR.
- **Recovery QBR mid-crisis** — the commitment may be a single time-bound recovery target ("active-teacher % back above X within 30 days") rather than a list; one measurable commitment beats five vague ones.
- **Commitment blocked on partner-internal approval** (board consent agenda) — record it as a conditional commitment with the approval gate and date named, not as closed.

## See also

- [`./qbr-open-with-partner-outcomes-not-product-features.md`](./qbr-open-with-partner-outcomes-not-product-features.md) — the sibling rule on how the QBR opens
- [`../skills/qbr-composition/SKILL.md`](../skills/qbr-composition/SKILL.md) — the no-commitments-no-QBR rule + followup-tracker shell
- [`../templates/touchpoint-log.md`](../templates/touchpoint-log.md) — where in-meeting commitments land after the QBR
- [`../agents/qbr-composer.md`](../agents/qbr-composer.md) — owns commitment capture; the hook (`hooks/flag-psm-anti-patterns.sh`) flags missing dates

## Provenance

Distilled from `agents/qbr-composer.md` (capture-commitments-in-the-partner's-words, post-QBR cadence review), `agents/partner-profile-curator.md` ("what we promised" is sacred), the anti-pattern hook (§7 action-item-without-date check), and house opinions §3 #2, #13 + §4 (great-QBR-no-commitments). Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
