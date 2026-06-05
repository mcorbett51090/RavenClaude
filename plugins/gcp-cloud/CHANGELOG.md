# Changelog — gcp-cloud

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.0] — 2026-06-05

CLOUD-domain value-add build-out against the full value-add menu. Every menu item was dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)". Builds on PR #315, which had already consolidated the knowledge decision-trees, `best-practices/`, and `templates/`.

### Added

- **scenarios/ bank completed to 4 field notes.** The `scenarios/README.md` index already listed four; two existed on disk and two were the net-new gap, now written: `shared-vpc-firewall-connectivity` (a Shared-VPC connectivity failure is subnet-IAM or the implied deny-ingress, not the topology — and a hung timeout vs. a 403 tells you which), and `committed-use-and-right-sizing-overspend` (measure with labels + billing-export before you cut; size commitments to the sustained baseline, not the peak). Both follow the 9-field schema. Pre-existing: `service-account-key-sprawl-and-over-grant`, `public-gcs-bucket-data-exposure`.
- **Decision-tree knowledge.** `knowledge/gcp-edge-and-resilience-decision-trees.md` — two Mermaid trees complementing the existing `gcp-cloud-decision-trees.md`: load-balancer / edge-exposure selection (external-vs-internal → L7-vs-L4 → global-vs-regional, + Cloud Armor + Serverless NEG), and zonal/regional/multi-region resilience-tier selection (RTO/RPO-driven, consistency-shaped). Grounded, dated, with a capability map.
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP tier + recommended-not-bundled MCP servers), §7 (value-add completeness disposition table), §8 (milestones).

### Decisions (recorded, not built)

- **No bundled MCP server.** Real first-party Google servers exist — **MCP Toolbox for Databases** (`googleapis/mcp-toolbox`, Apache-2.0, latest `v1.4.0` 2026-06-04) and **gcloud MCP** (`@google-cloud/gcloud-mcp`, Apache-2.0, preview) — but both bind to the consumer's authenticated GCP credentials (per-tenant config we can't hardcode) **and** are write-capable, failing the doctrine's zero-config-read-only bar. Documented the recommended `claude mcp add …` paths with reference-credential + `security-reviewer` gates instead of an `mcpServers` entry. No invented servers/versions.
- **No LSP.** No GCP-specific source language to wire — provisioning-as-code is `terraform-iac`'s lane, app code is `backend-engineering`'s (which ships an `.lsp.json`). Honestly N-A for a design/posture/selection domain.
- **No runnable script.** The cost arithmetic this plugin touches is entirely consumer-data- and price-dependent; the repo accuracy rule forbids baked-in prices, so a calculator would only echo the user's own inputs — no value over the decision trees + the cost best-practices that route the user to their own billing-export-to-BigQuery data.
- **No `bin/`, output-styles, monitors, settings, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate an existing surface or a neighbouring plugin" bar.
- **Skills/commands/templates/hooks coverage held sufficient** — the new decision-tree file + scenarios extend reach without a 5th skill or a new agent (team-growth-as-knowledge house rule).

### Verify-at-use

- MCP server package names, versions (`mcp-toolbox` `v1.4.0`; `gcloud-mcp` preview), Apache-2.0 licenses, and read/write surface — all version-volatile; re-confirm against the vendor before quoting. Sources: github.com/googleapis/mcp-toolbox, cloud.google.com MCP-Toolbox blog, github.com/googleapis/gcloud-mcp, docs.cloud.google.com/run/docs/use-cloud-run-mcp.
- The edge/resilience capability map (LB types, Cloud Armor, Serverless NEG, Cloud SQL regional HA, Spanner/GCS multi-region) and per-product SLAs/locations — re-check against the current Google Cloud Load Balancing + locations/SLA docs before committing a number to a design.

## [0.2.2] — earlier

4-agent GCP team (gcp-architect, gcp-iam-engineer, gcp-network-engineer, gcp-data-and-compute-engineer): 5 skills, the `gcp-cloud-decision-trees.md` knowledge bank, 30 best-practices, 4 templates, 4 commands, 1 advisory hook, and the first 2 scenarios + scenarios README. Seams to aws-cloud/azure-cloud, terraform-iac, data-platform, cloud-native-kubernetes, security-engineering, devops-cicd.
</content>
