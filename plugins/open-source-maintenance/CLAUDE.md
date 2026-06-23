# Open-source-maintenance Plugin — Team Constitution

> Team constitution for the `open-source-maintenance` Claude Code plugin. Two specialist agents — the **oss-maintainer-strategist** (stewardship) and the **release-and-versioning-engineer** (release) — plus a knowledge bank, skills, templates, and an advisory hook, aimed at one job: **run a public project people can use, trust, and contribute to.**
>
> **Orientation:** this file is **domain-specific** to open-source maintenance. For the domain-neutral team constitution inherited by every plugin (architect, coders, reviewers, project-manager, etc.), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`oss-maintainer-strategist`](agents/oss-maintainer-strategist.md) | License/CLA/DCO, governance & community-health files, issue/PR triage, contributor funnel, bus factor, funding | "which license?"; "set up triage"; "write CONTRIBUTING/governance/SECURITY"; "reduce our bus factor" |
| [`release-and-versioning-engineer`](agents/release-and-versioning-engineer.md) | Semver, changelogs, release automation, deprecation/breaking-change windows, coordinated security releases, dependency intake, supply-chain provenance | "major/minor/patch?"; "automate releases"; "plan a deprecation"; "cut a security release" |

Two agents map to the two genuinely distinct halves of maintenance — *stewardship* (the project and its people) and *release* (the artifacts and their contract). They share one skill ([`coordinate-a-security-release`](skills/coordinate-a-security-release/SKILL.md)) at the seam where a security report becomes a coordinated release.

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 2. Routing rules (Team Lead)

- **"Which license?" / "CLA or DCO?"** → `oss-maintainer-strategist` (drives `choose-an-open-source-license`).
- **"My backlog is out of control" / "set up triage"** → `oss-maintainer-strategist` (drives `triage-issues-and-prs`).
- **"Write CONTRIBUTING / CODE_OF_CONDUCT / GOVERNANCE / SECURITY"** → `oss-maintainer-strategist` (uses the community-health knowledge + templates).
- **"Is this major/minor/patch?" / "cut a release" / "write the changelog"** → `release-and-versioning-engineer` (drives `plan-a-release`).
- **"Remove/rename this API safely" / "plan a deprecation"** → `release-and-versioning-engineer` (drives `manage-breaking-changes-and-deprecations`).
- **A vulnerability report arrives** → either agent enters `coordinate-a-security-release`; the *analysis* escalates to `security-engineering`.
- **The CI/CD pipeline / the vuln analysis / community growth / docs craft** → escalate (see §10).

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **License before the first public commit.** No-license code is all-rights-reserved; retrofitting is messy.
2. **Bump by the change, not the feeling.** Semver is a contract; a removed public symbol is a major regardless of size.
3. **The changelog is for humans.** Group for upgraders (Keep a Changelog); never ship a bump with no entry.
4. **A breaking change needs a deprecation window.** Warn → window → remove in a major; never yank in a minor.
5. **Triage has an SLA and a decline path.** First-response promise + a kind, fast decline; silence is the failure mode.
6. **Security reports go private first.** A public fix commit before the advisory is a 0-day handed to attackers.
7. **DCO over CLA unless a real reason demands a CLA.** A CLA is contributor friction — justify it.
8. **Bus factor is a first-class risk.** One-person dependence is tracked and mitigated, not accepted.
9. **Tag, sign, attest.** A signed, provenance-attested artifact (Sigstore/SLSA/npm provenance) is the baseline.
10. **Volatile claims carry a retrieval date** (tooling, GitHub feature availability) and are re-verified before quoting.

---

## 4. Anti-patterns the agents flag

- Public code with no LICENSE file ("all rights reserved" masquerading as open source).
- A version bump with no CHANGELOG entry (the hook flags this on manifests).
- A removed/renamed public API shipped in a minor or patch.
- A deprecation warning with no named replacement / migration path.
- An unbounded, silent backlog; issues closed with no reason.
- A security fix committed to `main` before the advisory is published.
- A bespoke CLA imposed on a small community project "just in case."
- One maintainer holding all publish keys and release knowledge.
- An artifact published with no provenance/signature.
- A tooling/feature claim quoted with no retrieval date.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before either agent says "I can't" or names a license/version/policy, it must:

1. **Check the 5 skills** plus core skills.
2. **Traverse the decision tree** ([`knowledge/oss-licensing-decision-tree.md`](knowledge/oss-licensing-decision-tree.md) or [`knowledge/semver-and-release-decision-tree.md`](knowledge/semver-and-release-decision-tree.md)) before naming a license or a bump — don't keyword-match.
3. **Try the next-easiest defensible path** before declaring blocked.
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path.

See the upstream protocol in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contract

```
Question: <what was asked, in the decision tree's terms>
Decision: <license / version bump / triage disposition / deprecation plan + WHY (the tree node)>
Artifacts: <the concrete files/policies to add or change>
Risks / seams: <bus-factor, security, or hand-off to another plugin>
Verdict / next step: <plain-language, tied to the maintainer's goal>
```

**Plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 7. Automated checks (hooks)

The `hooks/` directory ships [`flag-oss-hygiene-smells.sh`](hooks/flag-oss-hygiene-smells.sh) — a PreToolUse Write/Edit/MultiEdit advisory hook:

| Check | Triggers on | Rule (§3) |
|---|---|---|
| Versioned manifest with no CHANGELOG found | package.json / pyproject.toml / Cargo.toml | #3 |
| Manifest with no `license` field | package.json / pyproject.toml / Cargo.toml | #1 |
| CHANGELOG with breaking wording but no `BREAKING` marker | CHANGELOG.md | #4 |

Advisory by default (`exit 0` with stderr warnings). Set `OSS_MAINT_STRICT=1` to make it blocking. Patterns are POSIX ERE only (the `check-grep-ere-pcre.py` gate).

---

## 8. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/choose-an-open-source-license/SKILL.md`](skills/choose-an-open-source-license/SKILL.md) | `oss-maintainer-strategist` | License recommendation + dependency-compat check + CLA/DCO call + the files to add |
| [`skills/triage-issues-and-prs/SKILL.md`](skills/triage-issues-and-prs/SKILL.md) | `oss-maintainer-strategist` | Label taxonomy + SLA tiers + reproduction gate + decline path |
| [`skills/plan-a-release/SKILL.md`](skills/plan-a-release/SKILL.md) | `release-and-versioning-engineer` | Semver bump + changelog assembly + release checklist |
| [`skills/manage-breaking-changes-and-deprecations/SKILL.md`](skills/manage-breaking-changes-and-deprecations/SKILL.md) | `release-and-versioning-engineer` | The warn → window → remove lifecycle + migration guide |
| [`skills/coordinate-a-security-release/SKILL.md`](skills/coordinate-a-security-release/SKILL.md) | both (shared) | Private report → GHSA/CVE → patched releases → coordinated disclosure |

## 8a. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/oss-licensing-decision-tree.md`](knowledge/oss-licensing-decision-tree.md) | Choosing a license / CLA-DCO posture — the Mermaid trees + reference table |
| [`knowledge/semver-and-release-decision-tree.md`](knowledge/semver-and-release-decision-tree.md) | Deciding a version bump — the Mermaid tree + the breaking-change gray zone |
| [`knowledge/community-health-and-governance.md`](knowledge/community-health-and-governance.md) | Standing up governance / community-health files / the contributor funnel |
| [`knowledge/oss-tooling-2026.md`](knowledge/oss-tooling-2026.md) | Recommending tooling — release automation, provenance, dependency intake (dated, re-verify at use) |

## 9. Templates in this plugin

| Template | Use for |
|---|---|
| [`templates/contributing-guide.md`](templates/contributing-guide.md) | `CONTRIBUTING.md` — the operations doc that converts drive-bys |
| [`templates/security-policy.md`](templates/security-policy.md) | `SECURITY.md` — private reporting channel + response SLA |
| [`templates/release-checklist.md`](templates/release-checklist.md) | A per-release runbook (also a bus-factor mitigation) |
| [`templates/governance-and-maintainer-ladder.md`](templates/governance-and-maintainer-ladder.md) | `GOVERNANCE.md` — roles, decision process, maintainer ladder |

---

## 10. Escalating out of the open-source-maintenance team

- **`devops-cicd`** — the CI/CD pipeline that actually runs the release (this plugin decides *what/when*; devops-cicd builds the *how*).
- **`security-engineering`** — the vulnerability analysis behind a CVE (exploitability, CVSS, blast radius); this plugin owns the *release choreography*.
- **`developer-relations`** — community growth, advocacy, conference/content strategy (this plugin owns the *governance/triage mechanics*).
- **`technical-writing-docs`** — the docs craft (Diataxis, docs site); this plugin authors the community-health files, not the product docs.
- **`developer-tooling`** — monorepo release graph, build caching, dependency-management tooling at depth.
- **`ravenclaude-core/project-manager`** — RAID / status for a multi-week maintenance initiative.

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- Adjacent plugins: [`../devops-cicd/CLAUDE.md`](../devops-cicd/CLAUDE.md), [`../security-engineering/CLAUDE.md`](../security-engineering/CLAUDE.md), [`../developer-relations/CLAUDE.md`](../developer-relations/CLAUDE.md), [`../technical-writing-docs/CLAUDE.md`](../technical-writing-docs/CLAUDE.md), [`../developer-tooling/CLAUDE.md`](../developer-tooling/CLAUDE.md)

## 12. Milestones

- **v0.1.0** — initial build-out: 2 agents (oss-maintainer-strategist, release-and-versioning-engineer), 5 skills, 4 knowledge docs (2 Mermaid decision trees + community-health + a dated 2026 tooling map), 8 best-practices, 4 templates, 1 advisory hook, CHANGELOG.
