# Construction Field Management

The **construction-field-management** plugin — the field side of construction project delivery: executing a building job on the jobsite *after* design is done. It runs the information flow (RFIs, submittals, daily logs, document control), the money (schedule of values, AIA G702/G703 pay applications, change orders, cost codes, budget-vs-actual), and quality/safety/closeout (punch lists, QA/QC, JHAs and toolbox talks, inspections, project closeout) — distinct from the drawings, the master schedule, and the trade work themselves.

## Agents

- **`project-engineer`** — The field information flow: RFIs (one answerable question, tracked to a dated response), submittals and the submittal register (required-by dates back-calculated from the install date), daily logs, document control (current revision per sheet, ASIs/bulletins, transmittals), schedule coordination, and action-item meeting minutes. Ball-in-court is the unit of progress.
- **`cost-and-change-controls-lead`** — The money: the schedule of values tied to cost codes, AIA G702/G703 pay applications with stored materials and retainage handled correctly, change management from PCO to executed CO so nothing gets built unpriced, and budget-vs-actual with a real cost-to-complete.
- **`field-and-safety-coordinator`** — Quality, safety, and closeout: inspection-and-test plans with hold points the work can't pass without, punch lists driven to zero by responsible trade, JHAs and toolbox talks grounded in OSHA, inspections (AHJ, special, owner walks), and a closeout package that actually releases retainage.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install construction-field-management@ravenclaude
```

## Seams

- **The drawings, the BIM model, the spec, the design answer** → `architecture-aec`; this team sends the RFI when the field hits a conflict, they own the design and answer it.
- **The master CPM schedule, the risk register, the RAID log, stakeholder management** → `project-management`; we coordinate the field to the schedule and flag time-impacts, they build and own the schedule.
- **The trade means-and-methods, the subcontract scope, the buyout** → `skilled-trades-contracting`; we manage submittals/changes/quality across trades, they do the trade work.
- **Contract/lien/payment-dispute legal posture, a serious safety incident with regulatory exposure** → `ravenclaude-core/security-reviewer` + the relevant specialist.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `architecture-aec`, `project-management`, and `skilled-trades-contracting`.
