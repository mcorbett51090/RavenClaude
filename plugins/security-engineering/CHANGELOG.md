# Changelog — security-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.9] — 2026-09-23

Weekly Tier-A news sweep (2026-09-23) — 5 independently re-verified corrections:

### Changed

- **CISA BOD 22-01 → BOD 26-04.** BOD 22-01 was revoked; **BOD 26-04 "Prioritizing Security Updates Based on Risk"** (issued 2026-06-10) supersedes it (and BOD 19-02), replacing a flat KEV-catalog clock with a four-factor risk matrix (exposure, KEV status, exploit automatability, technical impact) — close to this plugin's existing risk-band shape. Updated in `knowledge/vulnerability-severity-vs-risk-decision-tree.md` (:43, :62), `scripts/sec_risk.py` (:34, :141 — help text only, no logic change), and `CLAUDE.md` §5. Re-verified via WebSearch (CISA's own page titles indexed as "Revoked" / the BOD 26-04 announcement; cisa.gov itself was egress-blocked this session, consistent with the original sweep report — the exact 3/14/60-day tier table is flagged `[verify-at-build]` pending a direct read of the directive).
- **`best-practices/container-image-scanning-in-ci.md`** — the CI example used `aquasecurity/trivy-action@master`, a mutable ref. Confirmed via GHSA-69fq-xp46-6x23 (CVE-2026-33634, aquasecurity/trivy, published 2026-03-21): a threat actor with compromised maintainer credentials force-pushed 76 of 77 `trivy-action` version tags (and all `setup-trivy` tags) to a credential-stealing payload in March 2026. Pinned to the current `v0.36.0` tag's commit SHA (`ed142fd0673e97e23eac54620cfb913e5ce36c25`, resolved via `git ls-remote` against the live repo this session, not invented) with an inline comment explaining why and how to re-verify. Also bumped `github/codeql-action/upload-sarif@v3` → `@v4` (v3 is deprecated December 2026; Node 20, which v3 runs on, reached EOL 2026-04-30).
- **`best-practices/sast-tune-for-signal.md`** — `returntocorp/semgrep-action@v1` is deprecated and archived (confirmed 2024-04-09, via the repo's own README). Replaced with the native `semgrep ci` CLI pattern (verified current flag syntax: `--config` per ruleset, `--sarif --sarif-output=`; `SEMGREP_RULES` is real but documented incompatible with `SEMGREP_APP_TOKEN`, so rulesets are passed via `--config` instead). Also fixed a cosmetic bug in the same example: `# nosec B105` is Bandit suppression syntax sitting in a Semgrep example — corrected to `# nosemgrep`.
- **`knowledge/security-engineering-decision-trees.md:110`** — capability map: SLSA v1.0 → **v1.2** (approved 2025-11-12, promotes the Source Track from experimental to approved).
- **`knowledge/sast-dast-sca-scanner-selection-decision-tree.md:61`** and **`CLAUDE.md` §6.1** — OSV-Scanner v2.4.0 → **v2.6.0** (released 2026-09-14; v2.5.0 migrated scanning/filtering/matching to osv-scalibr end-to-end).

**Migration:** none — knowledge-file and CI-example content only; no agent/skill behavior change.

## [0.3.8] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

## [0.3.7] — 2026-08-08

Weekly Tier-A news sweep (2026-08-08) — **correction** in `knowledge/security-engineering-decision-trees.md:113` (npm install-script hardening capability-map row). npm **v12.0.0 shipped GA on 2026-07-08**, so the row's "est. July 2026 / warnings today / preview" framing was stale, and the approval command it named (`npm approve-scripts --allow-scripts-pending`) was the **pre-GA preview** path. Corrected to the released date and the **GA approval flow** — `npm install-scripts approve` then `npm rebuild` — re-verified this session against the primary source ([npm v12.0.0 release](https://github.com/npm/cli/releases/tag/v12.0.0)); the `[verify-at-build]` hedge is retained. No sibling fan-out: `agents/supply-chain-security-engineer.md:46` already frames v12 as GA-adoptable and stays consistent. **Migration:** none — knowledge-file content only.

Passed a three-panel funnel (usefulness → source-verified detail → tiebreak-not-required); audit trail in `docs/research/2026-08-08-plugin-news-research-panel-review.md`.

## [0.3.6] — 2026-07-14

Captured a generalizable security principle surfaced by an autonomous 3-panel repo review (PR #622, 2026-07-13), where a bare-name interpreter denylist was bypassed by a path-qualified pipe (`curl … | /bin/bash`) and a credential slipped through a scanner that checked only a subset of fields.

### Added

- **`best-practices/a-denylist-is-only-as-good-as-its-coverage.md`** — prefer allowlists; when you must denylist, match the thing in all its forms (bare / path-qualified / relative / `sudo`- or `env`-wrapped) and scan **every** field/path, not a sample; pin each bypass form as a test fixture so a future edit can't silently reopen it. Roster count updated 22 → 23.

## [0.3.5] — 2026-07-08

Weekly Tier-A news sweep (2026-07-08) — **correction** in `knowledge/sast-dast-sca-scanner-selection-decision-tree.md` (+ CLAUDE.md §6.1): OSV-Scanner is **v2.4.0** (June 2026, adds CycloneDX 1.7 support), superseding the documented **v2.3.8**. Re-verified via the GitHub releases API. **Migration:** none — knowledge-file content only.

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
