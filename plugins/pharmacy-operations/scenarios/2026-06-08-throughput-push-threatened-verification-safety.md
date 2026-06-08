---
scenario_id: 2026-06-08-throughput-push-threatened-verification-safety
contributed_at: 2026-06-08
plugin: pharmacy-operations
product: throughput-staffing
product_version: "n/a"
scope: likely-general
tags: [throughput, verification, safety, staffing]
confidence: medium
reviewed: false
---

## Problem

A pharmacy manager under volume pressure proposed hitting a higher fill target by trimming the pharmacist verification step. The risk: throughput and verification safety are both the job, not a trade-off — squeezing verification to lift volume is a patient-safety and liability failure, and the clinical verification itself is the pharmacist's (§3 #1).

## Context

- Setting: high-volume community pharmacy adding immunizations.
- Constraint: verification capacity is a hard constraint; clinical-service time is real load on top of fill (§3 #1 #5).
- The manager reasoned from a scripts-per-staff ratio that ignored clinical time.

## Attempts

- Tried: **sized staffing to volume PLUS clinical-service time** (`pharmacy_operations_calc.py throughput-staffing`). Outcome: the fixed ratio under-counted hours once immunization time was added — the real gap was staffing, not verification slack.
- Tried: **held verification capacity as a non-negotiable constraint** (§3 #1). Outcome: the throughput target only worked with added tech/pharmacist hours, not by squeezing the check.
- Tried: **framed the dispensing-error rate as the operational signal**, routing the clinical/dispensing judgment to the pharmacist (§3 #7 #8). Outcome: a clean operational/clinical boundary.

## Resolution

The fix was to **add tech and pharmacist hours to cover volume + clinical-service time and protect verification — not trim the check**. The output was the staffing read with the verification-safety constraint held, with no patient PHI in the deliverable.

**Action for the next consultant hitting this pattern:** **never buy throughput by squeezing verification — staff to volume plus clinical-service time.** Safety is a hard constraint, not an efficiency variable; the clinical check is the pharmacist's. See Tree 1 and the `throughput-staffing` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
