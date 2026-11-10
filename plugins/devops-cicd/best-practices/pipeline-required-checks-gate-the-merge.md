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
- Put a `paths:` or `branches:` filter on a workflow you are about to require. A skipped workflow stays pending and the pull request cannot merge. Gate a step with `if:` instead. The write-up is `ravenclaude-core` `knowledge/github-actions-hardening.md` rule 5.
- Add an advisory reviewer to the required list. GitHub's troubleshooting page, retrieved 2026-11-05 from <https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks>, treats `success`, `skipped`, and `neutral` as conclusions that satisfy a required check. A bot that exits neutral when it did not review anything would then satisfy the gate. Keep it off the list. A gate you mean to enforce exits non-zero when it fails.

## Strict, or a merge queue

GitHub's protected-branch doc, retrieved 2026-11-05 from <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches>:

| Setting | Merge requirement |
|---|---|
| **Strict** ("Require branches to be up to date before merging" checked) | The head must include the latest base. This is GitHub's default once required checks are on. |
| **Loose** (checkbox clear) | A green branch that lags the base can merge. The combination can fail after it lands. |
| **Merge queue** | The queue gives the same up-to-date benefit and tests a group built from the latest base. Doc: <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue>. Required workflows also trigger on `merge_group`. |

Use strict when people merge by hand. Use a queue on a busy default branch, and do not also hand-merge ahead of it. Hand-merge order, when there is no queue, is [`merge-behind-clean-tips-before-dirty-ones.md`](./merge-behind-clean-tips-before-dirty-ones.md).

`enforce_admins: true` is the default for a **product** default branch. A marketplace that keeps an admin bypass so docs can land on `main` has scoped that bypass to itself. Do not copy the bypass onto a product code branch, and do not use it to land a red check.

**Content placement on a product that has the gate.** RavenPower-Website's ship gate is `check-content-placement.mjs` (Website #953), covering `account/**` and shell/nav files. Do not rename it. The workflow runs on every pull request (no `paths:` filter). The job exits non-zero when placement fails, including on a diff that touches those paths. A prose Keep / Move / Remove note does not replace the check. The pass is `web-design` `knowledge/content-placement-page-ia-2026-11.md`. This plugin does not add the script to a product repo.

## Edge cases / when the rule does NOT apply

Bots that auto-merge dependency update PRs (Renovate, Dependabot) still go through required checks — they are not exempt. A deliberate break-glass for production incidents must be logged, time-bounded, and reviewed post-incident.

## See also

- [`../agents/pipeline-engineer.md`](../agents/pipeline-engineer.md) — owns required-check selection and pipeline-as-code.
- [`./build-fast-gates-first.md`](./build-fast-gates-first.md) — required checks must be fast enough to not block the team.

## Provenance

Codifies GitHub branch protection documentation (docs.github.com/repositories/configuring-branches-and-merges) and the DORA research finding that required CI gates correlate with higher deployment frequency and lower change failure rates.

---

_Last reviewed: 2026-06-05 by `claude`_
