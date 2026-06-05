# Generate changelogs from commits, not from memory

**Status:** Pattern
**Domain:** Release engineering
**Applies to:** `devops-cicd`

---

## Why this exists

Manually maintained changelogs drift from reality: entries get omitted, described inaccurately, or duplicated. They also impose a synchronization burden — the person cutting a release must remember what changed since the last tag. A machine-generated changelog derived from Conventional Commits is always accurate, always current, and eliminates a category of human error from the release process.

## How to apply

Adopt Conventional Commits (`feat:`, `fix:`, `chore:`, `BREAKING CHANGE:`) as the commit convention and wire a generator (Release Please, semantic-release, or git-cliff) to produce changelogs and bump the semver automatically on merge to main.

```yaml
# .github/workflows/release.yml — Release Please (Google)
on:
  push:
    branches: [main]
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          release-type: node    # or python, go, maven, etc.
          token: ${{ secrets.GITHUB_TOKEN }}
```

```bash
# Commit convention examples that feed the generator
git commit -m "feat(auth): add PKCE flow for public clients"
git commit -m "fix(api): return 429 instead of 500 on rate limit"
git commit -m "feat!: drop support for Node 18"  # breaking change
```

The generator reads commit messages since the last tag, groups them by type, bumps the version (patch for `fix:`, minor for `feat:`, major for breaking), and opens a release PR with a generated `CHANGELOG.md` entry.

**Do:**
- Enforce Conventional Commits with a commit-msg lint hook (commitlint) so the generator has clean input.
- Configure the generator to include `feat:` and `fix:` in the changelog; suppress `chore:` and `docs:` unless your consumers want them.
- Review the auto-generated release PR before merging — it is the human checkpoint before publish.

**Don't:**
- Hand-edit the generated CHANGELOG.md after the fact; the next run will not know what you added.
- Mix manual CHANGELOG edits with generator output; choose one source of truth.
- Skip the release PR review step just because it's automated.

## Edge cases / when the rule does NOT apply

Hotfixes with a single commit that are cherry-picked to a release branch may need a manually written blurb if the commit message was terse. The generator's output is the base; add a paragraph-level note in the release notes UI if the audience needs more context.

## See also

- [`../agents/release-engineer.md`](../agents/release-engineer.md) — owns release cadence and changelog tooling.
- [`./release-semver-is-a-contract.md`](./release-semver-is-a-contract.md) — machine-generated SemVer and changelogs are paired practices.

## Provenance

Codifies the Conventional Commits specification (conventionalcommits.org) and the Release Please / semantic-release toolchain practice, widely adopted in open-source and cloud-native projects.

---

_Last reviewed: 2026-06-05 by `claude`_
