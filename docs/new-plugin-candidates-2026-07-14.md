# New plugin candidates — research & prioritization (2026-07-14)

> **Scope of the run:** identify 10 RavenClaude plugins not yet implemented, prioritize by
> demand × feasibility, and build the highest-priority ones. This doc is the research +
> prioritization record; the built plugins land under `plugins/` in the same PR.

## Method

The marketplace already ships **160 plugins** (see [`architecture.md`](architecture.md) roster). To find
genuine gaps rather than near-duplicates, every candidate below was checked against the existing
`plugins/*/.claude-plugin/plugin.json` descriptions (`grep -ril <term>`) — all ten return **zero**
dedicated matches; incidental mentions inside adjacent plugins (e.g. "treasury" inside `finance`,
"tax" inside `accounting-bookkeeping`) were confirmed to be passing references, not coverage.

Selection favored candidates that are (a) broadly demanded across industries, (b) **evergreen and
standards-anchored** so the domain content carries low volatile-claim risk, and (c) cleanly distinct
from the nearest existing plugin (the seam is stated for each).

## The 10 candidates

| # | Plugin | Purpose & value | Nearest existing (seam) | Demand | Feasibility |
|---|--------|-----------------|-------------------------|--------|-------------|
| 1 | **internal-audit** | The internal-audit function: risk-based audit universe & annual plan, engagement fieldwork, workpapers & evidence, issue rating & reporting, follow-up, and QAIP — anchored on the IIA Global Internal Audit Standards, COSO, and the Three Lines Model. | `cybersecurity-grc` (security control assurance), `regulatory-compliance` (AML/financial regs) → internal audit is the *independent assurance* discipline over all risk, not security- or reg-specific. | High — every mid/large org + all public companies have an IA function. | High — standards-anchored, evergreen. |
| 2 | **treasury-management** | Corporate treasury: cash & liquidity forecasting, bank-relationship & account structure, short-term investment/debt, FX & interest-rate risk hedging, payments & fraud controls, working-capital optimization, and TMS selection. | `finance` (FP&A/budgeting), `fintech-payments-engineering` (payment rails engineering) → treasury owns *the cash and the bank relationship*, not the P&L plan or the payment code. | High — universal corporate function. | High — evergreen mechanics. |
| 3 | **quantum-computing-engineering** | Quantum software/algorithm engineering: gate-model vs annealing, qubit-modality trade-offs, NISQ vs fault-tolerant framing, circuit design, error mitigation/correction, hybrid quantum-classical workflows, and QPU access via cloud SDKs (Qiskit/Cirq/PennyLane/Braket). | `ml-engineering`, `hardware-electronics-engineering`, `robotics-*` → none touch quantum; this is a distinct compute paradigm. | Medium-high — fast-growing, no coverage. | High — the framings (gate model, NISQ, error correction) are stable even as devices churn. |
| 4 | **investor-relations** | IR for public & pre-IPO companies: the earnings cycle, guidance policy, analyst & shareholder engagement, disclosure discipline (Reg FD), the IR website/fact sheet, ESG & proxy season, and perception studies. | `startup-fundraising` (private raises), `finance` (the numbers) → IR is *communicating* to public markets. | Medium-high. | High. |
| 5 | **mergers-acquisitions-advisory** | Corporate development / M&A: deal sourcing & screening, valuation (DCF/comps/precedent), due-diligence orchestration, deal structure & terms, synergy modeling, and post-merger integration planning. | `startup-fundraising`, `finance` → M&A is the *transaction* discipline. | Medium-high. | Medium-high — some volatile deal-norm content, flagged verify-at-use. |
| 6 | **corporate-tax-practice** | Corporate & individual tax: provision (ASC 740), federal/state/international compliance, R&D credit, transfer pricing, sales-&-use nexus, and planning. | `accounting-bookkeeping` (books/close) → tax is a distinct specialty with its own authority set. | Medium-high. | Medium — jurisdictional/volatile rules, heavy verify-at-use discipline required. |
| 7 | **telecom-carrier-operations** | Carrier/telecom operations: network provisioning, OSS/BSS, service assurance, interconnect & settlement, spectrum, and telecom regulatory. | `network-engineering` (enterprise networks) → carrier ops is the *service-provider* business layer. | Medium. | Medium. |
| 8 | **utilities-operations** | Regulated utility (electric/gas/water) operations: rate cases & regulatory, grid/asset management, outage & reliability (SAIDI/SAIFI), demand response, and metering/GIS. | `renewable-energy` (generation projects) → utilities is the *regulated distribution/retail* business. | Medium. | Medium. |
| 9 | **home-inspection-operations** | Home-inspection business: inspection workflow & report software, scheduling, InterNACHI/ASHI standards of practice, E&O/liability, and agent-referral growth. | `residential-real-estate-brokerage`, `field-service-management` → a distinct licensed inspection trade. | Medium. | High — small, well-bounded domain. |
| 10 | **learning-and-development** | Corporate L&D: training-needs analysis, instructional design (ADDIE/backward design), LMS/LXP selection, skills taxonomy, and program measurement (Kirkpatrick/Phillips ROI). | `people-operations-hr` (HR ops), `edtech-partner-success` (EdTech vendor) → L&D is the *internal capability-building* function. | Medium. | High. |

## Prioritization rationale

**Build first (Tier 1 — this PR): #1 internal-audit, #2 treasury-management, #3 quantum-computing-engineering.**
They score highest on the demand × feasibility product: internal audit and treasury are near-universal
corporate functions with authoritative, evergreen standard sets (IIA/COSO; treasury mechanics), which
keeps volatile-claim risk low and lets the agents give confident, durable guidance. Quantum is the
single highest-novelty engineering gap in the roster and its core framings are stable even though the
hardware churns (versions carry a retrieval date + verify-at-use). All three are cleanly distinct from
the existing 160 — no cannibalization.

**Tier 2 (#4–#10): scoped, not built this run.** Investor-relations and M&A round out the corporate-
finance suite; corporate-tax, telecom, and utilities carry heavier volatile/jurisdictional content that
needs a dedicated research pass to hit the repo's citation discipline; home-inspection and L&D are
well-bounded and cheap to add next. They are documented here so the next run can pick them up without
re-deriving the gap analysis.

## Implementation approach (per plugin)

Each Tier-1 plugin follows the established **2-agent** plugin shape (the `audio-dsp-engineering` /
`serverless-engineering` template): a strategy/architecture agent + an execution/operations agent,
3 skills, a 2-doc knowledge bank (a Mermaid decision tree + a dated 2026 patterns/reference doc), and
2 templates. Each agent carries the full scenario-authoring frontmatter schema
(`audience`/`works_with`/`scenarios`/`quickstart`) the `check-frontmatter.py` gate requires, and a
`description` ≤ 300 chars. Every plugin `requires ravenclaude-core@>=0.7.0`, is registered in
`.claude-plugin/marketplace.json` and the `docs/architecture.md` Status roster, and its paths already
match the standard `plugins/*/…` globs in `.repo-layout.json`.

**Dependencies:** none beyond `ravenclaude-core` (the shared foundation) — these are markdown/agent
plugins, no new runtime deps, so a consumer's `/plugin marketplace update` cannot break.

## Blockers

None encountered during research/planning. The build risk is CI-gate compliance (frontmatter schema,
prettier-on-JSON, marketplace/architecture roster parity); each is handled in the build and verified
by `scripts/audit-gates.sh` before the PR.
