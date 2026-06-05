# Multi-DVM Protocol Variation Is a Margin and Quality Problem

**Status:** Absolute rule
**Domain:** Clinical protocols / multi-doctor practice management
**Applies to:** `veterinary-practice`

---

## Why this exists

In a multi-DVM practice, unwarranted variation in how the same clinical presentation is worked up and treated — different diagnostic panels for the same presenting complaint, different pre-anesthetic thresholds, different treatment protocols for common conditions — has two direct costs. First, clients who see different DVMs receive inconsistent recommendations, which erodes trust and makes referral communication unreliable. Second, variation in diagnostic and treatment selection produces variation in revenue per case even when the case mix is identical. A practice where DVM A runs a minimum database on every vomiting patient and DVM B runs only a physical exam will have systematically different ACT and diagnostic revenue per visit. The variation is invisible until it is measured.

## How to apply

Establish named, standard protocols for the practice's most common 20–30 presentations, and track compliance per DVM.

```
Protocol standardization steps:
1. Identify the top presentations by visit frequency (pull from PIMS):
   - Typically: wellness exams, vaccines, vomiting/GI, skin disease, ear issues,
     urinary signs, dental, lameness, respiratory, annual diagnostics

2. For each protocol, define:
   - Minimum diagnostic workup (what is always recommended for this presentation)
   - Tiered options (what to offer if client declines minimum workup)
   - Treatment standard (first-line medication choices, dosing guidelines)
   - Recheck recommendation trigger (what findings require a follow-up and when)
   - Who approves exceptions (protocol deviations require medical director note, not silent)

3. Track compliance per DVM (monthly):
   - % of visits matching the defined minimum workup for each presentation
   - ACT by DVM by case type (variation > 15% per case type warrants review)
   - Diagnostic utilization rate per DVM for named panels

4. Use the data for coaching, not policing:
   - Present as "here's what the team is doing, here's where you differ"
   - Variation that is clinically justified is documented; variation that isn't is addressed
```

**Do:**
- Involve the DVMs in protocol creation — protocols imposed without clinical buy-in are ignored.
- Treat the protocol as decision-support for the licensed DVM, not an order — the DVM retains clinical discretion; the protocol sets the default.
- Review protocols annually or when a new evidence-based standard emerges.

**Don't:**
- Use ACT-per-DVM data as a compensation metric without first confirming that case mix is comparable — a DVM who sees more wellness appointments will have a different ACT than one who sees mostly sick cases.
- Allow variation to accumulate because "every doctor practices differently" — in a multi-DVM practice, that is a customer experience and quality problem.
- Publish protocol compliance data in team settings without explaining the intent; it will be perceived as surveillance unless framed as quality improvement.

## Edge cases / when the rule does NOT apply

Solo-DVM practices have no variation to manage between doctors. The protocol still adds value as a staff-communication and coverage (locum DVM) standard, but the multi-DVM compliance tracking step does not apply.

## See also

- [`../agents/clinical-protocol-specialist.md`](../agents/clinical-protocol-specialist.md) — owns protocol design and compliance tracking.
- [`./standardize-protocols-to-kill-unwarranted-variation.md`](./standardize-protocols-to-kill-unwarranted-variation.md) — the overarching principle this rule operationalizes.

## Provenance

Codifies CLAUDE.md §3 #1 (standardize protocols to kill unwarranted variation) for the multi-DVM practice context; grounded in AAHA quality and practice excellence standards and veterinary practice management consulting frameworks.

---

_Last reviewed: 2026-06-05 by `claude`_
