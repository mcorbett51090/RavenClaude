# Realization and Utilization Drive Firm Economics

**Status:** Pattern
**Domain:** US public-accounting / CPA-firm operations
**Applies to:** accounting-firm-cpa

## Why this exists

A CPA firm's economic health is expressed through two ratios: realization (how much of billed
standard fees is actually collected) and utilization (how much of available staff time is spent
on billable work). A firm that ignores these metrics may grow revenue while shrinking margin —
taking on more clients, working more hours, and collecting less per hour each year.

Realization and utilization are the feedback loop between the firm's pricing decisions, scope
discipline, staffing model, and leverage ratio. A low realization rate signals underpricing,
scope creep, slow review, or a client mix that does not fit the firm's model. A low utilization
rate signals overstaffing, administrative inefficiency, or a capacity plan that doesn't match
the return/engagement volume.

## How to apply

**Do:**
- Track realization at the engagement level, the partner level, and the service-line level.
  An overall firm average masks the service lines or partners dragging the average down.
- Track utilization by staff level (staff, senior, manager, partner) and by season. Utilization
  norms differ by level and by time of year — a partner at 55% utilization in February busy
  season is a different problem than a partner at 55% in July.
- Use realization data from prior engagements to set fixed fees for the current year. A fixed
  fee that results in realization below 85% on a repeating engagement is a pricing error, not
  a one-time event.
- Document write-down root cause at the engagement level: scope creep (client asked for more),
  original underprice (fee was wrong from the start), slow review (preparer or reviewer was
  inefficient), client complexity (return was harder than expected). Root cause determines the
  fix.
- Review leverage ratios by service line: a line where partners or managers do work that
  seniors or staff could handle is destroying margin and blocking development.
- Use `scripts/firm_calc.py` for the standard realization, utilization, effective rate, and
  leverage calculations.

**Don't:**
- Set fixed fees without a floor based on estimated hours × standard rate ÷ target realization.
- Write off hours without documenting the reason — silent write-downs are invisible tuition.
- Average realization across service lines when analyzing firm economics — tax and CAS have
  different realization dynamics.
- Confuse utilization with productivity. A senior at 95% utilization during busy season is
  also burning out; the goal is sustainable, profitable utilization, not maximum utilization.

## Edge cases / when the rule does NOT apply

- **Fixed-fee commoditized returns:** for very simple, high-volume returns (e.g., W-2-only
  1040s at a flat rate), the relevant metric is contribution margin per return, not realization
  rate — the standard billing rate is nominal. Track margin-per-return instead.
- **Introductory pricing for new service lines:** a firm launching a new CAS practice may
  price below its target realization in year one to build the client base and capture process
  data. This is a deliberate investment, not a realization failure — document it as such and
  set a realization target for year two.
- **Pro-bono and reduced-fee work:** community service, non-profit support at reduced fees.
  Track separately; do not let these dilute the firm's commercial realization metrics.

## See also

- `agents/firm-practice-lead.md` — primary owner of realization/utilization analysis
- `scripts/firm_calc.py` — realization, utilization, effective rate, leverage ratio calculations
- `knowledge/cpa-firm-decision-trees.md` — fixed-fee vs. hourly pricing decision tree
- `best-practices/the-engagement-letter-scopes-the-work-and-the-fee.md` — scope discipline
  as a realization driver

## Provenance

Standard firm management practice in US public accounting. Benchmark ranges cited in the
agent files (e.g., 75–85% utilization for staff/seniors) reflect commonly cited ranges in
the public accounting profession and are marked `[verify-at-use]` — they shift with market
conditions and firm size.

_Last reviewed: 2026-06-08 by `claude`._
