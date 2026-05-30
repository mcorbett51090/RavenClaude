# Retain records on a written schedule keyed to the regime — not on disposal instinct

**Status:** Absolute rule
**Domain:** Records retention
**Applies to:** `regulatory-compliance`

---

## Why this exists

Compliance evidence is only useful if it still exists when the regulator asks for it — and the firm can only prove it kept the right things for the right period if it works to a written, regime-keyed retention schedule. Two symmetric failures recur. Disposing too early: a KYC file, a SAR record, a screening log, or a return workpaper destroyed before the regime's minimum retention period elapses — so when an exam reaches back, the evidence is gone and the firm cannot demonstrate the control operated. Keeping too long, or everything forever: a sprawl of PII and customer data retained past its lawful basis, which is itself a data-protection exposure. Retention periods differ by record type *and* by regime — a SAR record typically outlives a routine KYC file, and the minimums vary by jurisdiction — so "we keep things for a while" is not a schedule. The discipline is a written schedule that names each record class, its minimum retention, the regime that sets it, the disposal trigger, and the legal-hold override.

## How to apply

Maintain a written retention schedule, keyed to record class and regime, with disposal and legal-hold handled explicitly:

```
Record class       KYC/CDD file · EDD pack · SAR/STR record · screening log · return workpaper · exam evidence · policy version
Minimum retention  the regime's minimum for THIS class  [verify-at-build — periods vary by record type and jurisdiction]
Regime / cite      which regulator/rule sets the minimum (name it; same word, different regulators)
Start trigger      when the clock starts (relationship end, filing date, period end) — not "creation date" by default
Disposal           scheduled disposal once retention elapses AND no legal hold applies
Legal hold         active litigation/investigation/exam FREEZES disposal — overrides the schedule
```

A no-file SAR decision and the screening list-version capture are records too — they sit on the schedule alongside the filed reports.

**Do:**
- Work to a written schedule that names each record class, its minimum retention, and the regime that sets it.
- Apply a legal hold that overrides scheduled disposal whenever litigation, investigation, or an exam is live.
- Start the retention clock from the correct trigger (relationship end / filing date / period end), recorded per class.

**Don't:**
- Dispose of records on instinct or to "tidy up" — disposal is a scheduled event gated by retention + no-hold.
- Keep everything forever — over-retention of PII is itself a data-protection exposure.
- Assume one jurisdiction's minimum applies across regimes — SAR retention ≠ KYC retention, and both vary by regulator (house opinion #12).

## Edge cases / when the rule does NOT apply

- **Legal hold always wins** — when an exam, investigation, or litigation is live, nothing on the affected record classes is disposed regardless of the schedule; release the hold only on counsel's instruction.
- **SAR/STR confidentiality persists for the full retention** — these stay `regulator-only` and encrypted in-directory for their (typically longer) retention; tipping-off rules outlive the filing.
- **Legal-opinion gate** — the *lawful basis* for retention/disposal and the *exact* statutory minimum are legal questions; route the legal conclusion to counsel and mark periods `[verify-at-build]`. The schedule mechanics continue.

## See also

- [`./aml-document-the-no-file-decision.md`](./aml-document-the-no-file-decision.md) — no-file decisions are records on the schedule.
- [`./aml-sanctions-screening-hygiene.md`](./aml-sanctions-screening-hygiene.md) — captured list versions are retained evidence.
- [`./exam-evidence-on-every-pbc-item.md`](./exam-evidence-on-every-pbc-item.md) — the evidence the exam asks for must have survived retention.
- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — recordkeeping ("5-year minimum (BSA), longer for SARs; specific requirements vary by regulator") `[verify-at-build]`.

## Provenance

Codifies the `aml-kyc-analyst` recordkeeping surface area ("5-year minimum, longer for SARs; varies by regulator") ([`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md)), the constitution's confidentiality handling for SAR/STR material (§2, §7), and house opinions #6 (default to written), #9 (privacy by default), and #12 (jurisdiction matters) in [`../CLAUDE.md`](../CLAUDE.md) §3. Specific retention periods are marked `[verify-at-build]` per the no-invented-citations constraint.

---

_Last reviewed: 2026-05-30 by `claude`_
