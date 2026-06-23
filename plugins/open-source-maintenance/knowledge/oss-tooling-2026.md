# Knowledge — OSS maintenance tooling (2026)

> **Last reviewed:** 2026-06-23 · **Confidence:** Medium-High for the categories (stable); **volatile** for specific feature availability and version numbers — **re-verify at use** before quoting a consumer. This is a *category map*, not a settled fact sheet.

The discipline: recommend the **category and the fit**, name a tool second, and carry a retrieval date on any volatile specific (a tool's current feature set, a GitHub feature's GA status).

---

## Release automation

| Tool | Ecosystem fit | Mechanism | Pick it when |
|---|---|---|---|
| **release-please** | polyglot, GitHub-native | Conventional Commits → a "release PR" that bumps + changelogs | you want a reviewable release PR, GitHub Actions |
| **semantic-release** | JS-first (plugins beyond) | Conventional Commits → fully automated publish on merge | you want zero-touch publish, no human gate |
| **Changesets** | JS monorepos | contributor-authored intent files → versioned per-package | a monorepo where each PR declares its own bump |
| **goreleaser** | Go | builds + packages + publishes cross-platform artifacts | Go binaries/releases |
| **cargo-release / cargo-dist** | Rust | crate version + tag + installers | Rust crates |

All consume some form of **Conventional Commits** as input — if you adopt one, enforce the commit convention (commitlint / a CI check).

## Supply-chain provenance & integrity

| Concern | Tool / standard | Note |
|---|---|---|
| Signed artifacts | **Sigstore (cosign)** | keyless signing via OIDC; the modern default |
| Build provenance | **SLSA** framework + GitHub provenance attestations | proves *where/how* an artifact was built |
| Package-registry provenance | **npm `--provenance`**, PyPI Trusted Publishers (OIDC) | publish from CI with verifiable origin, no long-lived tokens |
| Posture scoring | **OpenSSF Scorecard** | automated checks (branch protection, signed releases, deps) |
| Best-practices badge | **OpenSSF Best Practices Badge** | self-certified maturity checklist |

## Dependency intake

| Tool | Note |
|---|---|
| **Dependabot** | GitHub-native; version + security updates; grouping config |
| **Renovate** | more configurable; grouping, scheduling, automerge rules, monorepo-aware |

Triage these like any change — group, test, read the upstream changelog (especially across a major). Don't blanket-automerge majors.

## Community & triage automation

| Need | Tool |
|---|---|
| DCO enforcement | DCO GitHub App |
| CLA gate | CLA Assistant |
| Stale management | `actions/stale` (exempt `priority/*` / `ready`) |
| Contributor recognition | All Contributors bot |
| Security advisories | GitHub Security Advisories (GHSA) → CVE request |
| Health metrics | CHAOSS / GitHub Insights |

## Provenance
- Tool homepages + GitHub docs (release-please, semantic-release, Changesets, goreleaser); OpenSSF (Sigstore, SLSA, Scorecard, Best Practices Badge); npm/PyPI provenance docs; GitHub Dependabot/Advisories docs. **Specific feature availability is volatile — re-verify at use.** Last reviewed 2026-06-23.
