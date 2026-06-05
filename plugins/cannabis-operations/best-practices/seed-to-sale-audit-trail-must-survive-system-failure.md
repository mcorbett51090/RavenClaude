# The seed-to-sale audit trail must survive a system failure

**Status:** Absolute rule
**Domain:** Cannabis operations / compliance / business continuity
**Applies to:** `cannabis-operations`

---

## Why this exists

Every licensed cannabis operator is required to maintain a complete, unbroken audit trail of product movement through the track-and-trace system. Regulators have issued warning letters and initiated license suspension proceedings against operators whose only response to a Metrc or BioTrack outage was "the system was down." The regulatory posture is that a system failure does not suspend the record-keeping obligation; it suspends only the real-time reporting. Operators who cannot reconstruct movement records from offline documents during an outage create an after-the-fact gap that looks indistinguishable from an attempt to conceal movement.

## How to apply

Implement a two-layer audit-trail discipline:

**Layer 1 — Offline manifest for every physical movement (required):**

```
Offline movement log — [date] — [time]
From location (license #):    ____
To location (license #):      ____
Product (track-and-trace ID): ____
Quantity / weight:            ____
Driver / handler name:        ____
Supervising manager:          ____
Signature:                    ____
Note: Entered into [Metrc/BioTrack/LeafData] on [date/time]: ____
```

Print and sign this form for every physical movement when the system is unavailable. File it by date. Enter it into the system as soon as connectivity is restored, with a note in the manifest field citing the outage period.

**Layer 2 — Nightly backup export (recommended):**
Most track-and-trace systems provide a CSV/API export. Export plant and package records nightly and store the file off-system. If a dispute arises about the state of the system on a given day, the backup is the contemporaneous record.

**Do:**
- Train staff on the offline manifest procedure before it is needed — a system failure is not the time to write the SOP.
- Report a track-and-trace system outage to the state regulator within the notification window specified in the operating license (varies by state; typically 24-48 hours).
- Reconcile all offline manifests to system entries within 24 hours of connectivity restoration; do not backlog them.

**Don't:**
- Halt all product movement during a system outage — the operational obligation continues; only the reporting timing shifts.
- Assume the state's track-and-trace vendor's outage notification also notifies the regulator — it does not.
- Delete or shred offline manifests after system entry; they are supporting documentation for the system record and may be requested in an audit.

## Edge cases / when the rule does NOT apply

- Planned maintenance windows announced by the state track-and-trace vendor: the same offline-manifest discipline applies, but the outage report to the regulator is typically waived when the vendor has pre-notified.

## See also

- [`../agents/seed-to-sale-compliance-specialist.md`](../agents/seed-to-sale-compliance-specialist.md) — owns the reconciliation and the SOP for the offline procedure.
- [`./seed-to-sale-traceability-is-the-license-reconcile-it-daily.md`](./seed-to-sale-traceability-is-the-license-reconcile-it-daily.md) — the foundational house opinion this operationalizes for the outage scenario.
- [`./sop-version-control-is-a-licensing-requirement.md`](./sop-version-control-is-a-licensing-requirement.md) — the offline manifest procedure belongs in a versioned SOP.

## Provenance

Derived from state cannabis track-and-trace operating requirements, Metrc/BioTrack outage guidance, and compliance enforcement case patterns. `[unverified — training knowledge]` — cite the applicable state's operating license conditions and vendor outage-notification procedures before advising.

---

_Last reviewed: 2026-06-05 by `claude`_
