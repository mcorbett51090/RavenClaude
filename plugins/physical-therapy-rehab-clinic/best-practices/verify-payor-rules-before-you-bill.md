# Verify payor rules before you bill

**Status:** Absolute rule
**Domain:** Billing / accuracy discipline
**Applies to:** `physical-therapy-rehab-clinic`

> This rule is the plugin's accuracy-discipline anchor: every payor specific is `[verify-at-use]`.

---

## Why this exists

The 8-minute-rule variant, modifier/NCCI edits, certification windows, visit caps, the therapy threshold, and cancellation rules **are not uniform across payors and change at least annually.** One payor's correct claim is another's denial. A confident, stale number quoted to a client or billed on a claim is the plugin's primary failure mode.

## How to apply

- Before billing or quoting, **confirm the rule against the specific payor's current policy** (or CMS for Medicare).
- Record the **source + retrieval date** on every figure in a deliverable, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- Re-verify annually and on any policy-update notice.

## Edge cases / when the rule does NOT apply

Never — verification is always cheaper than a denial or a compliance finding.

## See also

- [`../knowledge/pt-clinic-reference-2026.md`](../knowledge/pt-clinic-reference-2026.md)
- [`../../ravenclaude-core/CLAUDE.md`](../../ravenclaude-core/CLAUDE.md) (Claim Grounding & Source Honesty)

## Provenance

Codifies the cross-agent accuracy discipline inherited from `ravenclaude-core`, specialized to PT/rehab payor rules.

---

_Last reviewed: 2026-06-22 by `claude`_
