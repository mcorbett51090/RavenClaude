# construction-general-contractor

The **general-contractor project-delivery** specialist team. This plugin's agents help you estimate
and bid work, build CPM schedules, coordinate submittals and RFIs, manage change orders, track
project P&L and retainage, run closeout, and maintain a safe jobsite — from bid invitation through
punch-list.

> **The one-line philosophy:** a GC makes money by knowing the real cost before signing the
> contract, documenting every change before the work starts, and keeping the schedule logic honest
> so you know — and can prove — what hit the critical path.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Do the takeoff / build the bid / what markup?" | **construction-general-contractor** (`estimating-and-takeoff-analyst`) |
| "Build the CPM schedule / what's on critical path / analyze this delay" | **construction-general-contractor** (`scheduling-engineer`) |
| "Set up the submittal log / draft this RFI / price this change order" | **construction-general-contractor** (`submittal-rfi-coordinator`) |
| "Is this job making money / prepare the pay app / manage retainage / closeout" | **construction-general-contractor** (`gc-project-lead`) |
| "Write a JHA / review the safety program / what OSHA standard applies" | **construction-general-contractor** (`jobsite-safety-advisor`) |
| "Review the structural drawings / coordinate MEP" | `architecture-aec` |
| "Run the electrical sub's own business (quoting, payroll, licensing)" | `skilled-trades-contracting` |
| "Build a RAID log / run Agile sprints on a construction program" | `project-management` |

## What's inside

- **5 agents** — `gc-project-lead`, `estimating-and-takeoff-analyst`, `scheduling-engineer`,
  `submittal-rfi-coordinator`, `jobsite-safety-advisor`.
- **3 skills** — estimating-and-bidding, cpm-scheduling, submittals-rfis-change-orders.
- **3 commands** — `/construction-general-contractor:build-bid-estimate`,
  `:create-cpm-schedule`, `:manage-change-order`.
- **2 templates** — bid-package, schedule-of-values.
- **Knowledge bank** — `knowledge/construction-gc-decision-trees.md`: Mermaid trees for
  markup-vs-margin, change-order-or-absorb, and critical-path-impact, plus a dated 2026
  capability map (Procore, Autodesk Build, Bluebeam, P6/MS Project).
- **6 best-practices** — scope-the-bid-or-lose-it-on-the-change-order (Absolute),
  the-schedule-is-cpm-not-a-wish-list (Pattern), every-change-is-documented-before-the-work
  (Absolute), safety-is-a-precondition-not-a-line-item (Absolute),
  retainage-and-cash-flow-can-sink-a-profitable-job (Pattern),
  submittals-gate-procurement-sequence-them-early (Pattern).
- **1 advisory hook** — flags markup/margin confusion, hardcoded undated rates, verbal change
  orders, and schedules without critical-path logic.
- **1 calculator** — `scripts/construction_calc.py`: markup/margin conversion, schedule-of-values
  line, earned value (CPI/SPI), labor productivity, retainage withheld, bid markup.

## House opinions (the short list)

1. Every change is documented before the work starts — oral directions don't exist contractually.
2. Markup and margin are not the same number — always state which basis and show the conversion.
3. The schedule is a CPM network, not a Gantt wish-list — every task needs logic ties.
4. Safety is a precondition, not a line item — it is never value-engineered out.
5. Retainage and cash flow can sink a profitable job — model it before signing.
6. Submittals gate procurement — sequence them early in the CPM network.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
