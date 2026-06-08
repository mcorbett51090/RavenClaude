# hospitality-hotels

Hotel and lodging operations specialist team — revenue management, channel distribution, guest
experience, rooms & housekeeping, and the property operating model (USALI/GOPPAR).

> **The one-line philosophy:** RevPAR is the north star. Know your net ADR after distribution cost,
> manage reputation as a revenue lever, and never overbooker without the math.

## When to use this plugin (vs. its neighbours)

| You're asking…                                                              | Use                                                                 |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| "Should we raise rates this weekend? What does the demand signal say?"      | **hospitality-hotels** (`revenue-manager`)                          |
| "Our OTA mix is eating our margin — how do we shift to direct?"             | **hospitality-hotels** (`reservations-and-channel-analyst`)         |
| "Walk me through our P&L — GOPPAR, department margins, GOP%"                | **hospitality-hotels** (`hotel-ops-lead`)                           |
| "Our TripAdvisor score dropped — what do we do?"                            | **hospitality-hotels** (`guest-experience-lead`)                    |
| "Housekeeping labor costs are spiking — diagnose and fix"                   | **hospitality-hotels** (`rooms-and-housekeeping-analyst`)           |
| "Design our F&B menus / manage kitchen ops / engineer our restaurant P&L"   | `restaurant-operations`                                             |
| "Run a digital marketing campaign / build the loyalty program strategy"     | `marketing-operations-demand-gen`                                   |
| "Build the review-data ingestion pipeline from TrustYou"                   | `data-platform`                                                     |
| "Close the books / build the board pack / full P&L with EBITDA"             | `finance`                                                           |

## What's inside

- **5 agents** — `hotel-ops-lead`, `revenue-manager`, `reservations-and-channel-analyst`,
  `guest-experience-lead`, `rooms-and-housekeeping-analyst`.
- **3 skills** — `revenue-management-and-pricing`, `channel-and-distribution`,
  `guest-experience-and-reputation`.
- **3 commands** — `/hospitality-hotels:set-room-pricing`,
  `:optimize-channel-mix`, `:plan-guest-experience`.
- **2 templates** — `rate-plan.md`, `channel-mix-model.md`.
- **Knowledge bank** — `knowledge/hospitality-hotels-decision-trees.md`: Mermaid trees for
  raise-or-hold-rate, direct-vs-OTA, and overbook-or-not, plus a dated 2026 capability map of the
  hotel tech stack (PMS, RMS, channel manager, review platforms).
- **6 best-practices** — from the RevPAR-as-north-star absolute rule to reputation-score-moves-rate
  and the overbooking-is-a-calculated-risk pattern.
- **1 advisory hook** — flags rate changes without RevPAR/demand basis, OTA channels without
  net-ADR notes, hard-coded occupancy/ADR figures, and overbooking policies without no-show math.
- **1 calculator** — `scripts/hotel_calc.py`: RevPAR, ADR, occupancy %, GOPPAR, net ADR after OTA
  commission, displacement analysis. Stdlib-only, self-testing.

## House opinions (the short list)

1. RevPAR is the north star — not occupancy alone.
2. Know your net ADR after distribution cost; gross rate is a fiction.
3. The guest experience is the product; revenue strategy that erodes it eats the asset.
4. Overbooking is a calculated risk — never without the no-show / walk math.
5. Reputation score moves rate; manage it as a revenue lever.
6. USALI first: Rooms, F&B, OOD, Undistributed, GOP — then management overlays.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
