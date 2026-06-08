# One source of truth for campaign cost

**Status:** Pattern
**Domain:** Campaign operations / marketing analytics
**Applies to:** `marketing-operations-demand-gen`

---

## Why this exists

Marketing teams routinely operate with multiple overlapping cost sources: the paid-channel
dashboard (Google Ads, LinkedIn Campaign Manager), a shared spreadsheet, the MAP campaign record,
and the finance system. When these differ — and they almost always differ, because dashboards
include estimated spend, invoices arrive later, and credits and adjustments are rarely applied
in all places — the channel ROI report is untrustworthy. A pipeline-to-spend ratio calculated
on dashboard spend vs. invoice spend can differ by 10–20%, and a decision to double LinkedIn
budget based on stale figures is a consequential error.

The rule is simple: pick one system as the authoritative cost record, reconcile everything else
to it, and make the reconciliation a standing weekly practice.

## How to apply

- **Designate a single cost ledger.** The canonical spend source is typically the finance
  system (GL/AP) or a dedicated campaign cost tracker reconciled to finance. Paid-channel
  dashboards are a secondary reference — directionally useful for in-flight pacing, never
  the settlement number.
- **Reconcile weekly against paid-channel dashboards.** Compare the cost ledger figure to the
  dashboard-reported spend. Discrepancies >5% require investigation before the next budget
  cycle — they are usually a missing invoice, a credit not applied, or a dashboard attribution
  window mismatch.
- **Lock the cost figure at campaign close.** When a campaign ends, the final spend in the cost
  ledger is frozen and attached to the campaign record in the CRM. Retroactive edits to closed
  campaigns require documentation.
- **Require a GL code on every campaign line.** Marketing spend that exists in a spreadsheet
  but not in the GL is invisible to finance and creates reconciliation debt at the end of the
  quarter.
- **Never use dashboard spend as a source of truth in a board-level or finance report.** Always
  cite the invoiced/settled figure from the ledger or finance system.

**Do:**

- Include the cost ledger source and reconciliation date in every channel ROI report.
- Maintain the campaign cost tracker as a shared, versioned document with edit history.
- Train channel owners (paid, events, content syndication, sponsorships) to log actuals to the
  cost ledger, not just update their own channel dashboard.

**Don't:**

- Build a channel ROI report from paid-channel dashboard spend alone.
- Allow the cost tracker to drift more than one billing cycle behind actuals.
- Use different spend figures in different reports for the same campaign — the number must be
  consistent across all surfaces (marketing report, finance report, board deck).

## Edge cases / when the rule does NOT apply

For early-stage planning and in-flight budget pacing, dashboard spend estimates are acceptable
as directional indicators — clearly labeled as estimates. The rule applies to any report that
asserts a definitive spend figure, calculates CAC, or informs a budget reallocation decision.

## See also

- [`./attribution-is-a-model-not-the-truth.md`](./attribution-is-a-model-not-the-truth.md)
- [`../skills/campaign-operations/SKILL.md`](../skills/campaign-operations/SKILL.md)
- [`../templates/campaign-brief.md`](../templates/campaign-brief.md)

## Provenance

Codifies the finance reconciliation discipline applied to marketing spend — a direct application
of the "one source of truth per metric" principle from corporate FP&A practice to the campaign
cost tracking problem. Referenced in Demand Gen Report and marketing ops community practitioner
guides as a root cause of unreliable channel ROI reporting.

---

_Last reviewed: 2026-06-08 by `claude`._
