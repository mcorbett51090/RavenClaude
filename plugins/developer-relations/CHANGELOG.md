# Changelog — developer-relations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in
`.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-18

Initial build of the **developer-relations (DevRel)** plugin — the craft of growing and serving a
developer audience honestly. Identified as the P0 gap in `docs/plugin-roadmap-2026-06-18.md` (not the
docs system, not the API contract, not the buyer funnel).

- **2 doing-agents:**
  - `devrel-strategist` — DevRel strategy & program design, the developer funnel
    (awareness→activation→advocacy), honest measurement, community-program design.
  - `developer-advocate` — sample apps & demos that run as shipped, content, CFP abstracts & talks,
    the content calendar, community engagement.
  - Both carry the full scenario-authoring schema and the scenario-retrieval inline prior.
- **5 skills:** `devrel-strategy-and-metrics`, `developer-onboarding-funnel`,
  `sample-app-and-demo-design`, `conference-talk-and-cfp`, `developer-community-program`.
- **4-doc knowledge bank** (dated + cited): `devrel-funnel-and-metrics.md` (the funnel + the
  vanity-vs-real metric table, Mermaid tree), `devrel-strategy-decision-trees.md` (3 Mermaid trees —
  content-format, community build-vs-sponsor, launch-channel), `developer-experience-and-onboarding.md`
  (the golden path + the TTFS audit), `devrel-tooling-2026.md` (tiered tooling, every number marked
  verify-at-use).
- **7 best-practices** — measure-activation-not-vanity, optimize-time-to-first-success,
  sample-code-runs-as-shipped, teach-dont-market, cfp-leads-with-takeaway,
  community-health-is-response-and-resolution, volatile-claims-carry-retrieval-dates.
- **4 templates** — DevRel strategy brief, developer-onboarding audit (drop-off map), CFP abstract,
  content calendar.
- **4 commands** — `/design-devrel-program`, `/audit-developer-onboarding`, `/draft-cfp-abstract`,
  `/plan-sample-app`.
- **1 advisory hook** — `flag-devrel-antipatterns.sh` (vanity-metric headline without an activation
  metric, marketing-speak at developers, placeholder secret / `TODO` in a sample). Advisory by default;
  `DEVREL_STRICT=1` makes it blocking.
- **Scenarios bank** — README + 2 dated scenarios (vanity-metric board deck → activation funnel;
  onboarding drop-off → time-to-first-success).
- Runtime-tier value-add items (MCP / LSP / bin / monitors / calculator) dispositioned **N-A** with
  reasons (CLAUDE.md §11) — this is an advisory program vertical, like `applied-statistics`.
- Seams: `technical-writing-docs` (docs artifact), `api-engineering` (the contract),
  `product-management` (what to build), `marketing-operations` (the buyer funnel),
  `ravenclaude-core/security-reviewer` (a sample's security verdict). Requires `ravenclaude-core@>=0.7.0`.
