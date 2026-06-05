# Changelog — aws-cloud

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.0] — 2026-06-05

Value-add build-out — enriching the plugin against the full value-add menu on top of PR #315 (which added the consolidated knowledge decision-trees, `best-practices/`, and `templates/`). Every menu item is dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) §9 "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `over-permissioned-role-wildcard` (generate least-privilege from observed access + cap it with a boundary/SCP, don't hand-write from memory), `nat-gateway-cost-spike` (decompose by usage type before rightsizing; VPC endpoints over NAT egress), `cross-account-vpc-connectivity-failure` (read the hang-vs-refused signal, walk the layers in packet order, confirm with Reachability Analyzer), `public-s3-bucket-exposure` (scope the whole estate first, give the non-public replacement, Block Public Access at the account level + SCP ceiling). Matches the existing `scenarios/README.md` index and the 9-field schema; no account IDs/ARNs/keys, numbers `[ESTIMATE]`.
- **Decision-tree knowledge.** `knowledge/aws-finops-and-landing-zone-decision-trees.md` — two Mermaid trees: cost-lever ordering (*measure → eliminate waste → rightsize → then commit*) and landing-zone bootstrap (Control Tower vs hand-rolled SCPs vs enroll-existing-org). Complements PR #315's compute/storage/database/network/IAM/security-finding trees by adding the *sequencing* decisions they don't cover.
- **Bundled MCP server — AWS Documentation.** `plugin.json` now declares `aws-documentation` (`uvx awslabs.aws-documentation-mcp-server@latest`, Apache-2.0, part of the official `awslabs/mcp` suite). It is **read-only and needs no AWS credentials** (reads only the public docs site), which is what clears the zero-config + read-only bundling bar. CLAUDE.md §6 carries the doctrine block (owner + trigger + boundary + failure path); `NOTICE.md` carries the attribution + PATH-fallback; `x-mcpAttribution` declares it third-party.
- **Runnable calculator.** `scripts/aws_cost_estimator.py` (stdlib only, Python 3.8+) — `nat-vs-endpoint` / `rightsize` / `commit-breakeven`. A calculator, not a data source: **every price is a user input; no AWS prices are baked in** (region/date-volatile). Owned by `aws-ops-finops-engineer`. Ruff-clean.
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (bundled MCP doctrine), §7 (recommend-not-bundle credentialed servers), §8 (LSP N-A + runnable tooling), §9 (value-add completeness table), §10 (milestones).
- **NOTICE.md** — third-party attribution for the bundled AWS Documentation MCP server.

### Decisions (recorded, not built)

- **Credentialed AWS MCP servers are recommend-not-bundle, never shipped.** Cost Explorer (*billed ~$0.01/request*), Pricing, and the API/IaC/EKS/ECS/DynamoDB/RDS servers all use AWS credentials and most are write-capable — per the bundled-MCP doctrine they're documented as `claude mcp add …` paths with a `security-reviewer` gate and secret-as-reference, not an `mcpServers` entry. No invented servers. The deprecated `cost-analysis-mcp-server` is explicitly not recommended (use the Pricing server).
- **No LSP** — AWS cloud is an infra/advisory domain with no plugin example language; IaC source intelligence belongs to `terraform-iac`. Honest N-A.
- **No `bin/`, monitors, output-styles, settings defaults, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate an existing surface" bar; the calculator covers the runnable surface.
- **Skills/commands/templates/hooks coverage held sufficient** — the new trees + script + scenarios extend reach without a new agent or a redundant skill.

### Verify-at-use

- The bundled doc-server package name + `uvx` invocation + Apache-2.0 license; the credentialed servers' package names + the Cost Explorer per-request billing + the `cost-analysis-mcp-server` deprecation; Access Analyzer policy-generation, VPC Reachability Analyzer cross-account support, Control Tower's managed-guardrail set, and all per-GB/hourly AWS rates. All version-volatile — re-confirm against the vendor before quoting.

## [0.2.2] — earlier

5-agent AWS team (aws-architect, aws-iam-identity-engineer, aws-network-engineer, aws-compute-platform-engineer, aws-ops-finops-engineer): 6 skills, 12 best-practices, 5 templates, 4 commands, 1 advisory hook, and (PR #315) a consolidated decision-tree knowledge bank. Seams to azure-cloud/gcp-cloud, terraform-iac, cloud-native-kubernetes, observability-sre, devops-cicd, and ravenclaude-core/security-reviewer.
