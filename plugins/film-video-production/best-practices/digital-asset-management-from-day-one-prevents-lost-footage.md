# Establish digital asset management from day one — lost footage is unrecoverable

**Status:** Absolute rule
**Domain:** Film & video production / post / data management
**Applies to:** `film-video-production`

---

## Why this exists

Digital camera originals (OCF — original camera files) are the production's irreplaceable master. Unlike film where a negative physically exists, digital originals exist only as data on media; a single drive failure without a verified backup is a complete, permanent loss of everything shot on that card. Productions that defer data management to the post house, or that rely on a single set of media as the "backup," routinely discover the gap at the worst possible moment — during a reshoot that cannot be scheduled, or when the post house asks for the original media and it has already been wiped. The cost of a proper data management workflow (a data manager, verified backups to two independent drives per card, and an off-site third copy) is a small fraction of the cost of a single reshoot day.

## How to apply

Stand up data management before the first shoot day:

```
Data management plan — [Project] — [Date]

Original camera format:               ____
Average data volume per shoot day:    ____GB
Total estimated data volume:          ____GB

Storage provision:
  On-set primary (data manager drive): ____GB — make/model: ____
  On-set backup:                       ____GB — make/model: ____
  Off-site / cloud copy:               ____GB — service: ____

Backup verification method (checksum):  MD5 [ ]  SHA256 [ ]  Vendor tool: ____
Verification performed by:              ____
Wiping policy (media cleared only after): 3 verified backup copies [ ]

File naming convention:
  [Project]-[Date]-[Camera]-[Roll]-[Scene]-[Take]: Y/N

Card log (maintained daily):
  Card ID | Date | Scene/Take range | Backup 1 verified | Backup 2 verified | Off-site
  _______ | ____ | ________________ | _________________ | _________________ | _______
```

**Do:**
- Hire a dedicated data manager on any project with more than 2 camera cards per day; the DIT (digital imaging technician) and data manager roles are distinct.
- Verify checksums against originals — a file transfer without checksum verification is not a verified backup.
- Establish the off-site copy before production wraps on day one; delays in the off-site copy accumulate into a growing unprotected window.

**Don't:**
- Wipe or reuse camera media before three independent verified copies are confirmed — the "we'll just wipe the card" decision before backup verification is the most common cause of lost footage.
- Store both on-set copies in the same physical location (production vehicle, equipment room) — two drives in the same vehicle that gets stolen or damaged is one backup.
- Assume the production's cloud sync has completed; verify the cloud copy with a checksum or at minimum a file count before treating it as verified.

## Edge cases / when the rule does NOT apply

- Streaming-to-server productions (live events shot directly to server with no camera cards) have a different backup topology, but the three-copy discipline still applies to the server recordings.
- Archival projects working with pre-digitized media operate under a different chain-of-custody; the rule applies to the digitized files.

## See also

- [`../agents/post-production-supervisor.md`](../agents/post-production-supervisor.md) — receives the verified digital assets and owns the post data chain.
- [`../agents/line-producer.md`](../agents/line-producer.md) — budgets the data manager and storage provision.
- [`./locked-picture-is-the-gate-everything-downstream-waits-on.md`](./locked-picture-is-the-gate-everything-downstream-waits-on.md) — picture lock requires that all assets are available and verified; a data loss prevents it.

## Provenance

Derived from digital production and post-production data management standards, camera original backup best practices, and production risk management. `[unverified — training knowledge]` — validate checksum tool choices and off-site storage requirements with the post house and the completion bond company.

---

_Last reviewed: 2026-06-05 by `claude`_
