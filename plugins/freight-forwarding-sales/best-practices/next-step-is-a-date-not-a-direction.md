# A pipeline next step is a date and a commitment — not a direction or a wish

**Status:** Absolute rule
**Domain:** Pipeline management / CRM hygiene
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

"Will follow up" and "customer to revert" are not next steps. They are placeholders that accumulate in a CRM until a pipeline review forces a reckoning. The most common cause of pipeline overstatement in freight forwarding is opportunities with a stage, a value, and a "next step" field containing a direction rather than a date and an owner. Without a date, a deal does not exist in the forecast — it is a wish. A next step that is a specific action, owned by a named person, with a date in the future is the minimum unit of CRM data that makes a forecast trustworthy.

## How to apply

After every customer interaction (call, meeting, email exchange), record the next step before closing the CRM record.

**The minimum valid next step contains four elements:**

```
[Action] + [by / with] + [named person] + [on or by DATE]

Examples:
  "Send all-in rate comparison for HKG–FRA lane — by [Seller] — by 2026-06-09"
  "Discovery call — [Seller] with [Customer contact, Title] — 2026-06-12 at 10:00 CET"
  "Await PO from procurement — expected by 2026-06-20 — follow-up call booked 2026-06-18"
```

**Pipeline review test — every open deal must pass these three questions:**

1. What is the specific next action?
2. Who owns it — seller or customer?
3. When is the date?

If any answer is blank, "TBD", "ASAP", or "when customer is ready" — the deal is stalled. Apply the stalled-deal protocol below.

**Stalled deal protocol:**
- If a deal has had no customer-side forward movement in 21+ days: reclassify the stage down by one step.
- If a deal has had no next-step date update in 30+ days: flag it for pipeline review inspection.
- If a deal has had no customer contact in 45+ days: move to a "Nurture" or "Inactive" stage; it is not a forecast-able opportunity.

**Do:**
- Log the next step **during** the customer call, not from memory afterward — date and action while it is live.
- When the customer says "we'll get back to you" — agree a specific follow-up date on the call, not open-ended.
- When the next step is a customer action (e.g., "they will send the volume data") — set a seller-owned follow-up date 5 days out so you do not wait indefinitely.

**Don't:**
- Accept "awaiting customer decision" as a next step without a date by which you will follow up regardless.
- Update the stage forward without a corresponding dated next step — stage movement without next step is optimism, not progress.
- Delete stalled deals to clean the pipeline; reclassify them honestly so coverage metrics stay accurate.

## Edge cases / when the rule does NOT apply

Opportunistic/transactional spot-quote accounts that operate on an inbound-call model (customer calls with a shipment, you quote, they accept or reject in real time) do not always have a tracked next step — the deal closes in minutes. For structured key accounts and formal RFQ opportunities, this rule is absolute.

## See also
- [`../agents/pipeline-forecast-coach.md`](../agents/pipeline-forecast-coach.md) — pipeline hygiene and deal inspection
- [`../skills/pipeline-forecasting/SKILL.md`](../skills/pipeline-forecasting/SKILL.md) — stage definitions, coverage ratio, and the deal-inspection checklist

## Provenance

Codifies `pipeline-forecast-coach`'s deal-inspection checklist and house opinion §5 ("The CRM is the forecast"). Standard in every mature B2B sales methodology (MEDDIC, Challenger, Miller Heiman).

---

_Last reviewed: 2026-06-05 by `claude`_
