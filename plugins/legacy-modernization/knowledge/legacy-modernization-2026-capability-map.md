# Legacy Modernization — 2026 Capability Map

_A dated read of the modernization tooling landscape. Every row is `[verify-at-use]` — tool names, versions, and capabilities are volatile; re-confirm against the vendor/project before quoting or adopting. Last reviewed: 2026-06-19 (training-knowledge baseline — verify live before relying on any specific row)._

> This map orients; it does not endorse. License, maintenance activity, and security posture must be vetted at adoption (route security-sensitive choices through `ravenclaude-core/security-reviewer`).

## Characterization & approval testing
| Need | Representative tooling `[verify-at-use]` | Note |
|---|---|---|
| Approval/golden-master snapshots | ApprovalTests (multi-language), Verify (.NET), Jest/Vitest snapshots (JS/TS), syrupy (Python) | Snapshot the output; lock as the golden master. Review snapshots like code. |
| Coverage to target the change area | language-native coverage (coverage.py, c8/istanbul, JaCoCo, go test -cover) | Target the blast radius, not the whole system. |

## Dependency & framework upgrade automation
| Need | Representative tooling `[verify-at-use]` | Note |
|---|---|---|
| Automated dependency PRs | Dependabot, Renovate | Drive the *incremental* path; still one major at a time. |
| Codemods / automated migrations | jscodeshift, OpenRewrite (JVM), framework-shipped codemods (e.g. Next.js, React) | Mechanical edits at scale; verify against tests, don't trust blindly. |
| Polyglot large-scale refactor | OpenRewrite recipes, Sourcegraph batch changes | Recipe-driven; the recipe is the reviewable artifact. |

## Code comprehension / archaeology
| Need | Representative tooling `[verify-at-use]` | Note |
|---|---|---|
| Dependency / call-graph mapping | language LSPs, Sourcegraph, dep-graph tools (madge, deptry, jdeps) | Ground claims in the graph + `file:line`, not a guess. |
| Churn / hotspot analysis | git log/blame, code-maat / CodeScene-style churn×complexity | Hotspot = change frequency × complexity × blast radius. |
| AI-assisted comprehension | Claude Code (this surface) + LSP code intelligence | Useful for orientation; verify every inferred behavior against the code. |

## Migration & cutover infrastructure
| Need | Representative tooling `[verify-at-use]` | Note |
|---|---|---|
| Traffic shifting (canary / blue-green) | service mesh, gateway/ingress weighting, feature flags | The *automation* is `devops-cicd`'s; we design the plan + rollback. |
| Data CDC / dual-write / parallel-run | CDC tooling (e.g. Debezium), app-level dual-write, reconciliation jobs | Reconcile before cutover; streaming specifics → `data-streaming-engineering`. |
| Online schema change (expand/contract) | DB-native online DDL, schema-migration tools | DDL mechanics → `database-engineering`. |

## What this map deliberately does NOT do
- It does not pick your tool — the decision trees and the driver do.
- It does not freeze versions — every row is verify-at-use by design.
- It does not replace the patterns reference; tools execute patterns, they don't substitute for choosing one.
