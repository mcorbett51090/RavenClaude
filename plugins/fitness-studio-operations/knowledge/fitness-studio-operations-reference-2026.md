# Fitness Studio Operations — 2026 Tooling & Benchmark Map

> Dated snapshot of the studio-ops tooling and rule-of-thumb benchmarks the team reaches for. **Platforms, pricing, processor fees, and benchmark numbers are volatile — re-verify against the vendor and your own historical data before quoting to an operator.** The durable reasoning lives in [`fitness-studio-operations-decision-trees.md`](fitness-studio-operations-decision-trees.md); this file is the freshness-anchored "what to reach for."
>
> _Last reviewed: 2026-06-25 by `claude`. Each row carries a confidence note; treat unmarked specifics as `[verify-at-use]`._

---

## Booking / membership / billing platforms

| Tool | Use for | Note |
|---|---|---|
| **Mindbody** | Full studio management, booking, billing, marketplace discovery | Incumbent; broad but heavy; pricing by tier `[verify-at-use]` |
| **Mariana Tek** | Boutique/multi-location, branded app, capacity & waitlists | Strong for boutique cycling/HIIT `[verify-at-use]` |
| **Glofox / ABC Glofox** | Boutique studios & gyms, recurring billing | Membership + class booking |
| **Walla / Momence / Arketa** | Newer boutique platforms, lighter setup | Verify current feature/pricing parity before quoting `[verify-at-use]` |
| **TeamUp** | Smaller studios, flexible class packs & memberships | Lower-cost, flexible models |
| **Trainerize / TrueCoach** | Personal-training / 1:1 program delivery + billing | PT-led studios; client-app focused |

## Payments / processing

| Tool | Use for | Note |
|---|---|---|
| **Embedded processor (Stripe/Adyen via platform)** | Recurring card billing inside the booking platform | Per-transaction fee + platform markup `[verify-at-use]` |
| **Card-on-file + dunning** | Recovering failed/declined recurring payments | Involuntary churn is the cheapest churn to fix |
| **ACH / bank debit** | Lower-fee recurring for higher-ticket memberships | Lower fee, higher failure-handling complexity `[verify-at-use]` |

## Front-desk / member experience

| Tool | Use for |
|---|---|
| **Branded member app** | Booking, waitlist, class packs, push reminders |
| **Automated reminders + waitlist auto-promote** | Cutting no-shows, filling cancellations |
| **Digital waiver / liability + intake** | First-visit flow, health/PAR-Q, consent |
| **Retail POS (integrated)** | Apparel, supplements, drinks — ancillary margin |

## Benchmark rules of thumb — `[verify-at-use against YOUR data]`

> These are starting priors only. Your own historical actuals beat any industry average — replace these as soon as you have data.

| Metric | Rough prior | Caveat |
|---|---|---|
| Healthy monthly member churn | low single-digit % is strong; high single-digit is a leak | Varies hugely by model/market `[verify-at-use]` |
| Class fill-rate target band | ~60-85% of capacity | Depends on room, format, instructor `[verify-at-use]` |
| First-90-day cliff | largest share of churn happens early | Onboarding is the highest-ROI retention work |
| LTV:CAC target | ~3:1 commonly cited | A floor, not a goal; watch payback alongside it |
| CAC payback target | the faster the better; long payback strains cash | Cash-flow test, separate from LTV:CAC `[verify-at-use]` |
| Failed-payment / involuntary churn share | a meaningful slice of total churn | Recoverable with dunning + card updater |
| Late-cancel / no-show window | often 12h (some 24h) | Set to protect capacity, not earn fees `[verify-at-use]` |

## Worker classification (1099 vs W2) — practical, not legal

| Factor leaning **W2 (employee)** | Factor leaning **1099 (contractor)** |
|---|---|
| Studio sets schedule, sequence, music, attire | Instructor controls their own methods |
| Studio provides space, equipment, clients | Instructor markets/serves independently |
| Ongoing, indefinite, integral relationship | Project/substitute, non-integral |

> Misclassification is expensive (back taxes, penalties, benefits, possible state-level tests like ABC). **This table is an operator flag, not a determination** — the binding call belongs to `people-operations-hr` and the studio's counsel; the filing to `accounting-bookkeeping`.

## Standards / references

- **Member PII + payment data** — PCI scope (processor-tokenized card-on-file keeps you out of most of it), waiver/health-data handling → loop `ravenclaude-core/security-reviewer`.
- **Unit economics** — compute from your own net billing; see [`../skills/compute-studio-unit-economics/SKILL.md`](../skills/compute-studio-unit-economics/SKILL.md).
- **Cross-link:** the books, tax, sales-tax, and the payroll run live in [`../../accounting-bookkeeping/CLAUDE.md`](../../accounting-bookkeeping/CLAUDE.md); acquisition campaigns in [`../../marketing-operations/CLAUDE.md`](../../marketing-operations/CLAUDE.md); hiring and the binding classification call in [`../../people-operations-hr/CLAUDE.md`](../../people-operations-hr/CLAUDE.md) — not here.

---

_Re-verify any platform, fee, benchmark, or classification claim against the source — and against your own historical actuals — before it reaches an operator deliverable. These move quarterly, and classification is jurisdiction-specific._
