# Technician Utilization Is the Doctor Capacity Multiplier

**Status:** Pattern
**Domain:** Staffing / capacity
**Applies to:** `veterinary-practice`

---

## Why this exists

A DVM who spends time on tasks that a credentialed veterinary technician can legally perform — venipuncture, catheter placement, patient history, client education, treatment plan communication — is substituting low-leverage time for the high-leverage diagnostic and clinical reasoning work that only the DVM can do. In a capacity-constrained practice (which most are), every 15 minutes of DVM time displaced by a technician-appropriate task is 15 minutes the DVM could spend seeing another patient or performing a higher-value procedure. Technician utilization is the doctor capacity multiplier: it directly determines how many patients the same DVM team can see per day without adding hours.

## How to apply

Map DVM tasks by credential requirement and shift technician-appropriate work to the technician team.

```
DVM vs. technician task matrix:

DVM-only tasks (cannot delegate):
  - Physical examination and diagnosis
  - Treatment plan development and client explanation of findings
  - Drug prescription and authorization
  - Surgical performance and anesthetic oversight (varies by state)
  - Euthanasia

Technician-appropriate tasks (delegate to credentialed tech):
  - Patient history collection and preliminary vital signs
  - Sample collection: venipuncture, urinalysis, cytology
  - IV catheter placement
  - Medication administration (under DVM order)
  - Treatment plan re-explanation and client education follow-up
  - Vaccine administration
  - Discharge instructions and recheck scheduling
  - Anesthetic monitoring (under DVM supervision)

Technician utilization target:
  - Each DVM should have 2–3 technicians (FTE) supporting them at peak schedule
    [unverified — varies by practice model and state scope-of-practice law]
  - Track: % of technician-appropriate tasks actually performed by technicians vs. DVMs
    Pull from workflow observation or PIMS time-stamp data

Capacity impact formula [ESTIMATE]:
  - If a DVM reclaims 30 min/day via tech delegation × 250 working days =
    125 DVM hours/year ≈ 1–2 additional patients/day at current ACT
```

**Do:**
- Train technicians to their full scope of practice — underutilized credentialed technicians are an expensive misallocation of talent.
- Build the appointment template to pre-assign technician tasks (room prep, history, triage) before the DVM enters the room.
- Track technician-to-DVM ratios as a capacity metric on the practice scorecard.

**Don't:**
- Confuse receptionist or assistant roles with credentialed technician roles — scope of practice varies by state, and tasks delegated beyond the legal scope create liability.
- Use technician utilization to increase patient volume without confirming exam room capacity supports the additional throughput.
- Allow senior DVMs to decline technician support for "efficiency" — the practice loses the multiplier benefit when the DVM performs tasks that don't require their license.

## Edge cases / when the rule does NOT apply

Emergency and critical-care settings have fluid role boundaries during active emergencies — protocol-based task assignment matters, but the formal task-delegation matrix loosens appropriately under true emergency conditions.

## See also

- [`../agents/practice-operations-manager.md`](../agents/practice-operations-manager.md) — owns staffing ratios, scheduling, and capacity management.
- [`./capacity-gates-revenue-the-schedule-is-the-constraint.md`](./capacity-gates-revenue-the-schedule-is-the-constraint.md) — technician utilization is the mechanism for unlocking doctor-constrained capacity.

## Provenance

Standard veterinary practice management principle; codifies CLAUDE.md §3 #3 (capacity gates revenue) at the task-delegation level; grounded in NAVTA (National Association of Veterinary Technicians in America) scope-of-practice guidance and veterinary practice management consulting.

---

_Last reviewed: 2026-06-05 by `claude`_
