# Every cannabis transport requires a pre-approved manifest — no exceptions

**Status:** Absolute rule
**Domain:** Cannabis operations / distribution / compliance
**Applies to:** `cannabis-operations`

---

## Why this exists

Cannabis product moving between licensed locations without a pre-approved, track-and-trace-generated manifest is untracked cannabis in the eyes of the regulator — regardless of whether the movement is between the operator's own licensed entities. Law enforcement and regulators treat manifest-less transport as prima facie diversion, which is both a license violation and a criminal exposure for the driver and the operator. The track-and-trace manifest requirement also means the receiving location cannot accept the delivery and log receipt without the manifest ID; a delivery that arrives without one creates an inbound compliance problem at both ends.

## How to apply

Build a transport compliance checklist executed before every vehicle departs:

```
Transport compliance gate — [entity] — [state] — [date/time]

Manifest ID (track-and-trace):                 ____
Origin license #:                              ____
Destination license #:                         ____
Estimated departure:                           ____
Estimated arrival:                             ____

Product on manifest (verify physical match):
  Package ID | SKU | Quantity | Weight
  __________ | ___ | ________ | ______

Driver name:                                   ____
Driver state agent ID / badge:                 ____
Vehicle license plate:                         ____
Manifest printed and in vehicle:               Y/N
Digital manifest accessible (if state allows): Y/N
Route filed (if required by state):            Y/N
GPS/telemetry active:                          Y/N

Physical product verified against manifest by: ____
Departure time:                                ____
```

File the manifest in the track-and-trace system with "in transit" status before the vehicle leaves. Update to "delivered" within the state's required window after the destination logs receipt.

**Do:**
- Confirm the manifest is approved and in-transit status in the system before the driver touches the product.
- Carry the manifest in physical or digital form (whichever the state accepts) in the vehicle for the entire trip; law enforcement can request it at any point.
- Route deviations (a stop not on the manifest) require a manifest amendment in most states — do not deviate without system notification.

**Don't:**
- Move product with a manifest that is still in "pending" status — approved/in-transit is the required state.
- Allow a driver without the correct state agent identification or credential to transport — licensing extends to the individual transporter in many states.
- Assume the same manifest rules apply to intracompany transfers as to third-party distribution; some states require separate transport licenses for each.

## Edge cases / when the rule does NOT apply

- Licensed delivery to a consumer (direct-to-consumer delivery, where permitted) operates under a separate manifest regime specific to retail delivery; this rule covers B2B transport.
- Emergency product returns (e.g., a batch recalled after distribution) follow a state-specific return manifest procedure that may differ from the standard delivery manifest.

## See also

- [`../agents/seed-to-sale-compliance-specialist.md`](../agents/seed-to-sale-compliance-specialist.md) — owns manifest compliance and transport SOP.
- [`./seed-to-sale-audit-trail-must-survive-system-failure.md`](./seed-to-sale-audit-trail-must-survive-system-failure.md) — what to do if the track-and-trace system is unavailable when the manifest needs to be filed.
- [`./the-rules-change-at-the-state-line-never-generalize-a-state.md`](./the-rules-change-at-the-state-line-never-generalize-a-state.md) — transport rules vary sharply across states.

## Provenance

Derived from state cannabis transport and distribution regulations and track-and-trace manifest requirements. `[unverified — training knowledge]` — validate transport license requirements and manifest timing against the current rules in the applicable state.

---

_Last reviewed: 2026-06-05 by `claude`_
