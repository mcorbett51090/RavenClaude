# Changelog — security-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.2] — 2026-06-22

Version bump previously unlogged here; the change that set `0.3.2`:

- Knowledge freshness sweep: nested-subagent house-policy reframe + OWASP 2025 + Power Platform grid/PBIR (#440)

## [0.3.1] — 2026-06-13

Research-sweep **correction** (Tier-A weekly news sweep) — the capability map listed the **OWASP Top 10:2021** as "current"; the **OWASP Top 10:2025 is now Final** and 2021 is superseded. Verified this session against the primary source [owasp.org/Top10/2025](https://owasp.org/Top10/2025/) (incl. the new **A03:2025 Software Supply Chain Failures** category). Routed through two expert panels (usefulness → USEFUL/unanimous; detailed review → APPROVE-WITH-FIX). A second candidate (SLSA v1.0 → v1.1/v1.2) was reviewed and **deliberately dropped by the usefulness panel** as patch-level churn with no decision-altering false claim.

### Fixed

- **`knowledge/security-engineering-decision-trees.md`** — capability-map OWASP row updated from "2021 edition current" to "**2025 edition Final** (2021 superseded)", noting the new **A03:2025 Software Supply Chain Failures** category (`supply-chain-security-engineer`'s lane) with a Top10:2025 citation and a `[verify-at-build]` rider on category numbering. (The unverified "SSRF folded into Broken Access Control" sub-claim from research was dropped pending primary-source confirmation.) Quoting the 2021 list as "current" in mid-2026 misroutes triage + SAST rule-mapping.
- Version **0.3.0 → 0.3.1** in `.claude-plugin/plugin.json` **and** `marketplace.json` (lockstep).

## [0.3.0] — 2026-06-05

Value-add build-out — completing the plugin against the full value-add menu on top of PR #315's consolidated knowledge/best-practices/templates. Every menu item is dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `dependency-cve-triage-sla` (re-anchor the SLA on exploitability + CISA KEV, not the CVSS number), `committed-secret-rotation-ir` (rotate → audit → scanner rule → history-rewrite, in that order; OIDC removes the long-lived secret), `sast-finding-false-positive-triage` (triage by taint reachability; tune the rule once, never blanket-suppress over the one real bug), `broken-object-level-authz-remediation` (BOLA fix belongs at the data-access layer, not per-handler; UUIDs are defense-in-depth, not the control). README + the 9-field schema, matching the marketplace scenarios pattern.
- **knowledge/ decision trees (2 new Mermaid trees).** `vulnerability-severity-vs-risk-decision-tree.md` (CVSS base → environmental/threat context → risk band + proposed SLA; grounded in CVSS v4.0 metric groups, CISA KEV, SSVC, EPSS, BOD 22-01) and `sast-dast-sca-scanner-selection-decision-tree.md` (which scanner class for which defect class + pipeline placement; names concrete currently-published tools). Both complement — do not duplicate — PR #315's trees in `security-engineering-decision-trees.md`.
- **scripts/sec_risk.py — runnable risk-triage calculator (stdlib-only, ruff-clean).** `risk-band` (CVSS + reachability/exposure/auth/KEV/EPSS → risk band + proposed SLA, mirroring the new severity-vs-risk tree's leaves exactly) and `cvss-temporal` (transparent, *approximate* within-band re-weighting as a ranking aid — explicitly NOT the official CVSS calculator). Calculator, not a data source — the user supplies every input; outputs are decision-support, the verdict routes to `security-reviewer`.
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (runtime tier — recommended-not-bundled MCP servers + LSP disposition), §7 (runnable tooling), and the value-add completeness disposition table.

### Decisions (recorded, not built)

- **No bundled MCP server.** No published security MCP server clears the doctrine's zero-config + read-only bar ([`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md)): **Semgrep MCP** (`semgrep-mcp`, MIT) is third-party and its standalone repo is **deprecated** (folded into the `semgrep` binary), and it operates on the consumer's source (path-bound like the filesystem-server case); **OSV-Scanner MCP** (Apache-2.0) is **experimental**, repo-path-bound, and network-bound (osv.dev); **Trivy MCP** is per-consumer-path + network-bound. All documented as recommend-not-bundle with the exact `claude mcp add …` paths and a `security-reviewer` gate before adoption. No invented servers/versions/CVEs.
- **No bundled LSP server.** The plugin is an AppSec/advisory domain with no single source language to drive go-to-definition/diagnostics. The real **Semgrep LSP** (`semgrep lsp`, experimental) is a *findings* surface, not code-navigation, and is documented as a recommend-not-bundle option owned by `appsec-engineer`. The `.lsp.json` config-bundling pattern (as in `backend-engineering`) is N-A here.
- **No `bin/`, monitors, output-styles, settings defaults, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate the advisory hook / skills / a neighbouring plugin" bar.
- **Skills/commands/templates/hooks coverage held sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory anti-pattern hook already cover the surface; the new trees + script extend reach without a new agent (team-growth-as-knowledge house rule). No `NOTICE.md` (nothing third-party is bundled).

### Verify-at-use

- Security MCP/LSP project names, versions, licenses, maintenance/deprecation status (Semgrep MCP repo deprecation; OSV-Scanner v2.3.8 / experimental MCP; Trivy MCP); the OWASP edition (2021 current, 2025 refresh tracked); CVSS version (v4.0 current); KEV/EPSS contents; any policy/regulatory SLA window. All version-volatile — re-confirm against the vendor/standard before quoting.

## [0.2.x] — earlier

4-agent security-engineering (AppSec) team (appsec-engineer, threat-modeler, supply-chain-security-engineer, cloud-security-engineer): 5 skills, a decision-tree knowledge bank (vuln-triage + secrets-handling + shift-left + auth/authz + dependency-update + cloud-misconfig trees with a dated capability map), 12 best-practices, 4 templates, 4 commands, 1 advisory hook. Proposes controls; every ship/no-ship VERDICT escalates to `ravenclaude-core/security-reviewer`. Seams to api-engineering (API OWASP), auth-identity (identity), data-governance-privacy (data privacy), devops-cicd (artifact-side SBOM/provenance), and the cloud plugins.
