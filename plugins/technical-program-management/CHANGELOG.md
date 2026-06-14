# Changelog — technical-program-management

All notable changes to this plugin are documented here. Versions follow semver;
the `version` field in `.claude-plugin/plugin.json` is the source of truth.

## 0.1.0 — 2026-06-14

Initial release.

- 3 agents: `technical-program-manager`, `cross-team-dependency-manager`,
  `program-launch-coordinator`.
- 3 skills: `program-charter`, `dependency-mapping`, `launch-readiness-review`.
- 2-doc knowledge bank with Mermaid decision trees (TPM-vs-PM-vs-EM,
  escalate-or-not, go/no-go) plus a program-delivery playbook.
- 4 best-practices, 5 templates, 4 commands.
- 1 advisory anti-pattern hook (`flag-tpm-antipatterns.sh`) — flags
  activity-led status updates and launch checklists with no go/no-go criteria.
- 1 worked scenario.
