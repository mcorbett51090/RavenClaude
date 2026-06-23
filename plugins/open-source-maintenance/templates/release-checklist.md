# Release checklist — <project> v<version>

> Template for a release runbook. Copy per release; check each box. The goal is a boring, repeatable, signed, provenance-attested release — and a documented process so the bus factor isn't one.

**Release manager:** <name> · **Date:** <YYYY-MM-DD> · **Bump:** <major / minor / patch> · **Decided by:** <semver decision-tree node>

## 1. Pre-flight
- [ ] All intended PRs merged; `main` is the intended release content.
- [ ] CI is green **on the actual release commit** (verify a run exists for this SHA, not a stale one).
- [ ] No unresolved security reports that this release should include.

## 2. Version & changelog
- [ ] Version bumped in the manifest(s): <package.json / pyproject.toml / Cargo.toml / …> — consistent across the monorepo if applicable.
- [ ] `CHANGELOG.md` `[Unreleased]` moved under `## [<version>] — <date>`, grouped (Added/Changed/Deprecated/Removed/Fixed/Security).
- [ ] Breaking changes lead with `**BREAKING:**` and link a migration guide.

## 3. Tag & build
- [ ] Tag created: `v<version>` — **signed** (`git tag -s`).
- [ ] Artifact(s) built reproducibly.
- [ ] Provenance attached: <Sigstore cosign / SLSA attestation / `npm publish --provenance` / PyPI Trusted Publisher>.

## 4. Publish
- [ ] Published to <registry: npm / PyPI / crates.io / Maven / GitHub Releases>.
- [ ] GitHub Release created with notes (link the changelog section).
- [ ] Downstream / docs site / announcement updated as needed.

## 5. Security release only
- [ ] Advisory (GHSA → CVE) published **simultaneously** with the fix.
- [ ] Patched versions shipped for **every supported line**, not just `main`.
- [ ] Reporter credited; disclosure timeline honored.

## 6. Post-release
- [ ] Smoke-test the published artifact (install fresh, run).
- [ ] Open a fresh `[Unreleased]` section.
- [ ] Note any process friction to fix before next time.
