# Test your pipeline definition before merging it

**Status:** Absolute rule
**Domain:** CI/CD pipeline engineering
**Applies to:** `devops-cicd`

---

## Why this exists

A pipeline definition that is never validated is infrastructure debt masquerading as config. Syntax errors, broken step references, and misconfigured secrets don't surface until a developer pushes and waits — or, worse, until a release is blocked at 2 am. Every pipeline change should go through the same review rigor as application code because a broken pipeline is a production incident for the engineering team.

## How to apply

Use the vendor's native linting and dry-run tooling before merging pipeline changes.

```shell
# GitHub Actions — lint locally with actionlint
actionlint .github/workflows/*.yml

# GitLab CI — validate against the API (requires a token)
curl --header "Content-Type: application/json" \
     --header "PRIVATE-TOKEN: $GL_TOKEN" \
     --data @- https://gitlab.example.com/api/v4/ci/lint <<'EOF'
{ "content": "$(cat .gitlab-ci.yml)" }
EOF

# Generic: dry-run before real run (GitHub CLI)
gh workflow run --dry-run my-workflow.yml
```

Add a required status check that runs `actionlint` (or the GitLab equivalent) on every PR that touches `**/.github/workflows/**` or `.gitlab-ci.yml`. Treat pipeline lint failures as build failures.

**Do:**
- Run `actionlint` (GitHub Actions) or `gitlab-ci-lint` in CI on every pipeline change.
- Review pipeline diffs in code review — they are infra changes.
- Test env-var and secret references in a staging job before wiring to prod.
- Keep pipeline jobs composable (reusable workflows / `include:` templates) so the unit under test is small.

**Don't:**
- Merge pipeline changes that only "look right" without a lint pass.
- Skip review because the diff is "just YAML."
- Hard-code environment names or secret names that differ between staging/prod without parameterization.
- Use `continue-on-error: true` as a way to silence lint failures.

## Edge cases / when the rule does NOT apply

Bootstrap situations where you must push an untested pipeline to bring up the very first CI environment. Document this explicitly in the commit message and add a follow-up ticket to add lint CI.

## See also

- [`../agents/pipeline-engineer.md`](../agents/pipeline-engineer.md) — owns pipeline shape and lint standards.
- [`./build-fast-gates-first.md`](./build-fast-gates-first.md) — lint should be the first gate that runs.

## Provenance

Codifies `pipeline-engineer`'s ownership of pipeline-as-code quality from CLAUDE.md §1. Standard practice from GitHub Actions and GitLab CI official hardening guides; actionlint is the de-facto community standard (rhysd/actionlint).

---

_Last reviewed: 2026-06-05 by `claude`_
