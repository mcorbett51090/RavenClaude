# Changelog — azure-cloud

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-05-28

Initial release. An Azure cloud infrastructure & platform specialist team built from a researched, expert-reviewed plan (see [`docs/azure-cloud-plugin-analysis.md`](../../docs/azure-cloud-plugin-analysis.md)).

- **7 agents:** `azure-architect`, `bicep-iac-engineer`, `entra-identity-engineer`, `network-engineer`, `app-platform-engineer`, `integration-engineer`, `azure-ops-engineer`.
- **9-doc knowledge bank** (CAF/WAF + first-party, retrieval-dated 2026-05-28): landing zones & governance, IaC decision + Bicep, compute decision tree, Entra identity & access, networking & connectivity, integration decision, observability & FinOps, deployment & CI/CD, and the dated 2026 capability map.
- **6 templates:** landing-zone plan, IaC deployment spec, architecture spec, Entra identity design, cost & observability review, CI/CD runbook.
- **1 advisory hook** (`check-azure-anti-patterns.sh`, `AZURE_STRICT=1` to block): hardcoded secret, public exposure, Owner/Contributor at sub/MG scope, TLS/HTTPS off, hardcoded subscription/tenant GUID, Terraform local backend.
- **16 house opinions.** Ships **no** security/architect clone — escalates to core.

### Built per the round-3 expert review
- Added the `network-engineer` agent + `azure-networking-and-connectivity.md` (networking was unowned); added private-endpoint/deny-public-by-default + zone-redundant-prod + CAF-naming house opinions; moved CI/CD into `bicep-iac-engineer`.
- **Shipped the four reciprocal seam edits in the same release:** `power-platform/CLAUDE.md` (Logic-Apps↔Power-Automate, the #1 collision), `claude-app-engineering/CLAUDE.md` (Azure-host seam), `microsoft-fabric/CLAUDE.md` (raw Azure data services), `web-design/agents/web-architect.md` (Static Web Apps provisioning).
- Accuracy: B2C end-of-sale nuances, Deployment Stacks GA / Blueprints deprecated, Flex Consumption constraints, AVM ALZ + vending modules.

### Deferred to a later version
- `azure-ops-engineer` likely splits (observability / FinOps / governance) in v0.2.0.
- A `skills/` directory and a `scenarios/` bank when the first engagement scenario surfaces.
- Evaluate bundling an Azure MCP server if a stable community one emerges.
