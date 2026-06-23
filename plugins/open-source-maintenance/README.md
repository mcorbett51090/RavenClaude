# open-source-maintenance

> A RavenClaude plugin for **running a healthy open-source project** — the maintainer's craft, not the coding. Two specialist agents cover the two halves of maintenance: stewardship (license, governance, triage, community) and release (semver, changelog, deprecations, security releases, supply-chain).

Part of the [RavenClaude](https://github.com/mcorbett51090/RavenClaude) marketplace. Requires `ravenclaude-core@>=0.7.0`.

## What it's for

You can write the code; the hard part of open source is everything *around* it — choosing a license you can defend, converting drive-by reporters into contributors, keeping an unbounded backlog from burning you out, cutting releases that don't break your users, and handling a vulnerability report without handing attackers a 0-day. This plugin is the team that does that with you.

## Agents

| Agent | Owns | When to spawn |
|---|---|---|
| [`oss-maintainer-strategist`](agents/oss-maintainer-strategist.md) | License choice, CLA/DCO, governance & community-health files, issue/PR triage policy, contributor funnel, bus factor, funding | "which license?"; "set up triage"; "write CONTRIBUTING/governance/SECURITY"; "reduce our bus factor" |
| [`release-and-versioning-engineer`](agents/release-and-versioning-engineer.md) | Semver, changelogs, release automation, deprecation/breaking-change windows, coordinated security releases, dependency intake, provenance | "major/minor/patch?"; "automate releases"; "plan a deprecation"; "cut a security release" |

## Skills

- [`choose-an-open-source-license`](skills/choose-an-open-source-license/SKILL.md) — license + CLA/DCO decision, dependency-compat checked.
- [`triage-issues-and-prs`](skills/triage-issues-and-prs/SKILL.md) — label taxonomy + SLA tiers + decline path.
- [`plan-a-release`](skills/plan-a-release/SKILL.md) — semver bump + changelog + release checklist.
- [`manage-breaking-changes-and-deprecations`](skills/manage-breaking-changes-and-deprecations/SKILL.md) — the warn → window → remove lifecycle.
- [`coordinate-a-security-release`](skills/coordinate-a-security-release/SKILL.md) — private report → GHSA/CVE → patched releases → disclosure.

## Knowledge bank

- [`oss-licensing-decision-tree.md`](knowledge/oss-licensing-decision-tree.md) — Mermaid license + CLA/DCO trees.
- [`semver-and-release-decision-tree.md`](knowledge/semver-and-release-decision-tree.md) — Mermaid version-bump tree + the breaking-change gray zone.
- [`community-health-and-governance.md`](knowledge/community-health-and-governance.md) — the community-health file set, governance models, the contributor funnel.
- [`oss-tooling-2026.md`](knowledge/oss-tooling-2026.md) — dated category map (release automation, provenance, dependency intake, community automation).

Plus 8 [`best-practices/`](best-practices/README.md) rules, 4 [`templates/`](templates/) (CONTRIBUTING, SECURITY, release checklist, governance), and 1 advisory [`hook`](hooks/flag-oss-hygiene-smells.sh).

## Seams (where it hands off)

| Need | Goes to |
|---|---|
| The CI/CD pipeline that runs the release | `devops-cicd` |
| The vulnerability analysis behind a CVE | `security-engineering` |
| Community growth, DevRel, advocacy | `developer-relations` |
| Docs craft (Diataxis, docs site) | `technical-writing-docs` |
| Monorepo release graph / build caching | `developer-tooling` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install open-source-maintenance@ravenclaude
```
