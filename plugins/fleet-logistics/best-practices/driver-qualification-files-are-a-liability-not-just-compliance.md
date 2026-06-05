# Driver Qualification Files Are a Liability, Not Just Compliance

**Status:** Absolute rule
**Domain:** Regulatory compliance / risk management
**Applies to:** `fleet-logistics`

---

## Why this exists

Driver qualification (DQ) files — the FMCSA-required records for every commercial driver — are treated by many carriers as a compliance checkbox. They are also a litigation liability: in a post-accident negligent entrustment claim, the plaintiff's attorney will request every DQ file document on the driver involved. An incomplete DQ file (missing MVR, outdated medical certificate, undated employment verification) signals carrier negligence and is used to pierce the liability cap and pursue punitive damages. The cost of a missing document in a serious accident dwarfs any administrative savings from loose file management.

## How to apply

Build and maintain a DQ file compliance system:

```
DQ file required contents (per FMCSA 49 CFR Part 391):
  [ ] Employment application (signed, dated)
  [ ] Motor Vehicle Record (MVR) — at hire + annual
  [ ] Previous employer safety performance history (3 years)
  [ ] Road test certificate or equivalent (CDL = waived)
  [ ] Medical examiner's certificate (current — not expired)
  [ ] Annual review of driving record (MVR, signed by carrier rep)
  [ ] Annual list of violations (self-reported by driver, signed)
  [ ] CDL copy (front and back)
  [ ] Drug and alcohol clearinghouse query results

DQ file audit cadence:
  - At hire: complete before first dispatch
  - Annual: MVR pull, violation list, driving-record review
  - Medical certificate: track expiration and pull 30 days before expiry
  - Employment: 3-year history verified before dispatch
```

Risk-stratification rule: any driver with an incomplete DQ file is not dispatched until the file is complete. No exceptions.

**Do:**
- Use a calendar or fleet management system to auto-flag medical certificate expirations 45 days out.
- Keep DQ files in a secure system with access logs — in litigation, file-access history matters.
- Conduct a DQ file audit annually and after any accident involving a DOT-reportable injury or fatality.

**Don't:**
- Dispatch a driver whose DQ file is incomplete on any FMCSA-required item — the liability exposure is asymmetric.
- Treat annual reviews as a once-per-calendar-year formality; the review must be completed within 12 months of the prior one.

## Edge cases / when the rule does NOT apply

Owner-operators under their own authority (not leased to a carrier) maintain their own DQ files; when they are leased on, the carrier is responsible for the lease-on DQ file documentation. Non-CDL vehicles under 10,001 lbs operating in intrastate commerce may fall under state regulations rather than FMCSA; verify the applicable standard.

## See also

- [`../agents/fleet-engagement-lead.md`](../agents/fleet-engagement-lead.md) — flags DQ compliance gaps during the engagement scoping read.
- [`../agents/fleet-maintenance-specialist.md`](../agents/fleet-maintenance-specialist.md) — coordinates with DQ tracking on medical certificate currency for drivers operating specialized equipment.

## Provenance

FMCSA 49 CFR Part 391 (Driver Qualifications); negligent entrustment liability analysis is standard in transportation law; DQ file completeness as a litigation risk is covered in ATRI and ATA safety management publications.

---

_Last reviewed: 2026-06-05 by `claude`_
