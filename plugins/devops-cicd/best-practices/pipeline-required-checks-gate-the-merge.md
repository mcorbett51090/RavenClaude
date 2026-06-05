# Enforce required status checks — branch protection is the merge gate

**Status:** Absolute rule
**Domain:** CI/CD pipeline design
**Applies to:** `devops-cicd`

---

## Why this exists

A CI pipeline that can be bypassed — because branch protection isn't configured, or admins can override it, or the required checks list is empty — is decoration, not a gate. Developers will merge with a red build when under pressure, and the first merged failure teaches everyone that the pipeline is advisory. Required status checks make "green CI" a precondition enforced by the platform, not by social contract.

## How to apply

Configure branch protection rules on the default branch (and any long-lived release branches) to require a defined set of CI checks. Map each required check to a job that must pass before a PR can merge.

```yaml
# GitHub branch protection via CLI (example — also configurable in Settings UI)
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "ci / lint",
      "ci / unit-tests",
      "ci / security-scan",
      "ci / build"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null
}
JSON
```

Key decisions:
- `"strict": true` — the branch must be up-to-date before merging (prevents the "works on my branch, breaks main" failure mode).
- `"enforce_admins": true` — no bypass for repo owners; the gate is universal.
- List only checks that genuinely gate safety (lint, tests, security scan, build). Don't add optional informational checks to the required list.

**Do:**
- Set `enforce_admins: true`; an admin bypass defeats the purpose.
- Keep the required checks list to the fastest gates that prove safety — gate only what matters.
- Use a required check on the PR rather than a post-merge gate wherever possible (catch failures before main is broken).
- Document the bypass path (e.g., emergency deploy process) so it's an explicit decision, not a habit.

**Don't:**
- Add slow tests (>10 min) to the required set without sharding them; a slow gate is an ignored gate.
- Allow status checks to be required only for non-admins — that's branch protection theater.
- Treat a consistently-red required check as acceptable; fix it or remove it.

## Edge cases / when the rule does NOT apply

Bots that auto-merge dependency update PRs (Renovate, Dependabot) still go through required checks — they are not exempt. A deliberate break-glass for production incidents must be logged, time-bounded, and reviewed post-incident.

## See also

- [`../agents/pipeline-engineer.md`](../agents/pipeline-engineer.md) — owns required-check selection and pipeline-as-code.
- [`./build-fast-gates-first.md`](./build-fast-gates-first.md) — required checks must be fast enough to not block the team.

## Provenance

Codifies GitHub branch protection documentation (docs.github.com/repositories/configuring-branches-and-merges) and the DORA research finding that required CI gates correlate with higher deployment frequency and lower change failure rates.

---

_Last reviewed: 2026-06-05 by `claude`_
