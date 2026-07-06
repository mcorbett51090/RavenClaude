# New plugin candidates — research & prioritization (2026-07-01)

Research pass over the RavenClaude marketplace (119 plugins at time of writing) to identify
high-demand, technically-feasible plugin gaps. Each candidate below was checked against the
existing `plugins/` roster and confirmed **not** covered by an existing plugin (adjacent
plugins that own a neighboring surface are noted as *seams*, not overlaps).

## Method

1. Enumerated all existing plugins (`ls plugins/`) and their `marketplace.json` descriptions.
2. Brainstormed candidate domains across two axes the marketplace already splits on —
   **engineering disciplines** and **business/vertical operations**.
3. Discarded anything an existing plugin already owns (e.g. "prompt engineering" →
   `claude-app-engineering`; "feature flags / experimentation" →
   `experimentation-growth-engineering`; "VPC networking" → the cloud plugins).
4. Scored the survivors on **user demand** (how commonly this work shows up) × **technical
   feasibility** (how groundable the domain is without a live external system).

## Prioritized candidates

| # | Plugin | Priority | Demand | Feasibility | Why it's a gap (nearest seam) |
|---|--------|----------|--------|-------------|-------------------------------|
| 1 | **incident-response-dfir** | **P0** | High | High | Blue-team detection engineering, triage, threat hunting, digital forensics, breach response (NIST SP 800-61r2). `security-engineering` owns appsec/secure-coding; `cybersecurity-grc` owns governance/risk; `trust-and-safety` owns platform abuse — none own the SOC / DFIR lane. |
| 2 | ~~**networking-engineering**~~ → **superseded** | **P0** | High | High | Enterprise/campus/data-center networking. **A parallel routine independently shipped an equivalent `network-engineering` plugin to `main` (PR #532/#535) while this branch was in flight** — same domain, same lead agents (`network-architect`). Dropped here to avoid a duplicate + a cross-plugin agent-name collision; `network-engineering` already fills the gap. |
| 3 | **quantitative-trading** | P1 | Med-High | High | Systematic/algorithmic trading: strategy research, backtesting rigor (look-ahead/survivorship bias), risk & position sizing, execution & microstructure. `wealth-management-ria` is advisory; `finance` is FP&A — neither is quant. |
| 4 | **technical-seo-engineering** | P1 | High | High | SEO as an engineering discipline at scale: crawl budget, rendering (JS/SSR), structured data, Core Web Vitals, log-file analysis, migrations. `web-design` carries a light SEO auditor; this is the deep, technical lane. |
| 5 | **grant-writing-management** | P1 | Med | High | Grants lifecycle: prospect research, narrative/proposal, budgets, compliance, reporting — for nonprofits and research orgs. `nonprofit-fundraising` owns donor development; grants are a distinct discipline. |
| 6 | **conversation-design** | P2 | Med | High | Chatbot / voice / agent conversational UX: intent taxonomy, dialog flows, error recovery, disambiguation, persona/tone. Seams to `claude-app-engineering` (the runtime) and `technical-writing-docs` (copy). |
| 7 | **robotics-engineering** | P2 | Med | Med | ROS 2, motion planning, perception, control loops, sim-to-real, safety. `embedded-iot-engineering` owns firmware/MCU; robotics is the autonomy/kinematics layer above it. |
| 8 | **payroll-operations** | P2 | Med | Med | Payroll processing, multi-jurisdiction tax withholding, garnishments, year-end (W-2/1099), compliance. Deepens `people-operations-hr` (which owns the people lane, not the pay-run mechanics). |
| 9 | **aviation-operations** | P3 | Low-Med | Med | Flight operations, MRO/maintenance planning, crew scheduling, safety management systems (SMS). No transportation-ops plugin covers aviation. |
| 10 | **creator-economy-operations** | P3 | Med | Med | Creator business ops: monetization mix, sponsorship/brand deals, audience & channel analytics, multi-platform publishing. `marketing-operations` owns brand marketing, not the creator P&L. |

## Prioritization rationale

- **P0** picks (`incident-response-dfir`, networking) were both **high-demand engineering
  disciplines** with **clean seams** to existing plugins and **highly groundable** (stable,
  standards-based: NIST 800-61, RFCs). `incident-response-dfir` is built and merged here.
  The networking pick was **superseded before merge** — a parallel routine shipped an
  equivalent `network-engineering` to `main` (PR #532/#535), so this branch drops its
  duplicate rather than collide with it (two plugins can't both ship a `network-architect`
  agent — the frontmatter uniqueness gate blocks it).
- **P1** picks add breadth into finance-quant, marketing-technical, and nonprofit lanes that
  have real demand but slightly narrower audiences or a partially-adjacent existing plugin.
- **P2/P3** are solid future additions but either narrower in audience (aviation, creator)
  or a deepening of an existing plugin (payroll → people-operations-hr) rather than a
  net-new discipline.

## Build status (this PR)

- ✅ **incident-response-dfir** — built (2 agents, 5 skills, knowledge bank with decision
  trees, best-practices, templates, advisory hook).
- ⛔ **networking-engineering** — dropped as a duplicate. `main` independently shipped an
  equivalent **`network-engineering`** plugin (PR #532/#535) while this branch was open, so
  the gap is already filled; shipping a second networking plugin would be redundant and
  would fail the cross-plugin agent-name-uniqueness gate (both use `network-architect`).
- ⏭️ Candidates 3–10 — documented here as a prioritized roadmap for follow-up PRs.

Each future plugin follows the same newest-plugin standard (see
`plugins/open-source-maintenance/` as the reference structure) and must clear the CI gates:
frontmatter schema (`scripts/check-frontmatter.py`), the ≤300-char agent-description cap,
the layout allow-list (`.repo-layout.json`), prettier, and the gate-audit meta-test.
