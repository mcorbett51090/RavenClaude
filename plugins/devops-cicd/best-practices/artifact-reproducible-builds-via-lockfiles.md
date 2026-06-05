# Commit and verify lockfiles to make dependency resolution deterministic

**Status:** Absolute rule
**Domain:** Build / artifact engineering
**Applies to:** `devops-cicd`

---

## Why this exists

A build that resolves dependencies at build time without a lockfile is non-deterministic: the same commit can produce different binaries on different days if an upstream dependency releases a patch. Non-deterministic builds make debugging impossible ("it worked yesterday"), make incident reproduction unreliable, and open a supply-chain attack vector where a dependency is swapped between CI and local. Committed lockfiles make `pip install`, `npm ci`, `cargo build`, and `go mod download` resolve the exact same graph every time, everywhere.

## How to apply

Commit the lockfile for every language ecosystem in the repo. Use the "clean install" command in CI (not the "interactive" one that may upgrade). Fail the build if the lockfile is out of sync with the manifest.

| Ecosystem | Lockfile | CI install command | Sync-check command |
|---|---|---|---|
| Node.js | `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` | `npm ci` | `npm install --frozen-lockfile` |
| Python | `requirements.txt` (pinned) / `poetry.lock` / `uv.lock` | `pip install --no-deps -r requirements.txt` | `pip-audit` or `uv lock --check` |
| Go | `go.sum` | `go mod download` | `go mod verify` |
| Rust | `Cargo.lock` | `cargo build --locked` | `cargo verify-project` |
| Java (Maven) | (use Dependabot / explicit version ranges) | `mvn dependency:resolve` | Maven enforcer plugin |

```yaml
# GitHub Actions: Node.js with frozen lockfile enforcement
- name: Install dependencies
  run: npm ci                   # fails if package-lock.json is out of sync

# Go: verify module graph
- name: Verify go.sum
  run: go mod verify            # fails if any module hash doesn't match

# Python with uv
- name: Install Python deps
  run: uv sync --frozen         # fails if uv.lock is stale
```

**Do:**
- Commit lockfiles alongside package manifests.
- Use the "frozen" or "clean install" command in CI to detect drift.
- Add a CI check that fails if running the lock-generation command produces a diff.
- Review lockfile diffs in PRs — a new transitive dependency is a supply-chain event.

**Don't:**
- Ignore the lockfile in `.gitignore` (a common mistake for libraries — applications must commit it).
- Use `npm install` in CI instead of `npm ci`; the former may silently upgrade.
- Allow a lockfile diff to merge without review just because it came from a bot (Dependabot, Renovate).

## Edge cases / when the rule does NOT apply

Published libraries may intentionally omit lockfiles from the published package (to avoid constraining consumers), but the repo's dev/test lockfile must still be committed for reproducible CI. Go modules use `go.sum` rather than a traditional lockfile; commit and verify it.

## See also

- [`../agents/build-and-artifact-engineer.md`](../agents/build-and-artifact-engineer.md) — owns build reproducibility and the supply-chain integrity posture.
- [`./build-build-once-promote-the-same-artifact.md`](./build-build-once-promote-the-same-artifact.md) — lockfiles make the "build once" guarantee meaningful.

## Provenance

Codifies the SLSA supply-chain levels requirement for hermetic, reproducible builds and the NIST SSDF practice PW.4.1 (protect software from unauthorized modification during build). Ecosystem-specific guidance comes from npm, Go modules, and uv documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
