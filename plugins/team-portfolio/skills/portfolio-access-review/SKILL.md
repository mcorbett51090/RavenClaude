---
name: portfolio-access-review
description: "Review and tighten the GitHub token scope and hub-repo access configuration for a team-portfolio deployment. Reach for this skill during any security audit, when a team member leaves, when new repos are added to the tracked list, or when a 403 error appears in the collection log."
---

# Skill: Portfolio Access Review

The team-portfolio hub holds a GitHub token that reads across multiple repos. Over time, the token's scope drifts — it may have been provisioned with broader access than needed, it may cover repos that were removed from the tracking list, or it may need to be rotated after a team-member departure. This skill audits the access configuration and produces a minimal, principle-of-least-privilege token spec.

## Step 0 — Identify what token is in use

The collector reads `PORTFOLIO_TOKEN` → `GITHUB_TOKEN` → `GH_TOKEN`. Determine which variable is set and whether it is a classic PAT, a fine-grained PAT, or the GitHub Actions built-in token.

| Token type | Scope control | Rotation mechanism |
|---|---|---|
| GitHub Actions built-in `GITHUB_TOKEN` | Scoped to the current repo only | Auto-rotates per run |
| Classic PAT | Org-wide or repo-level scopes | Manual rotation |
| Fine-grained PAT | Per-repo read permissions | Manual rotation + expiry date |

**Security preference:** fine-grained PAT scoped to exactly the tracked repos, with read-only access and an expiry date set.

## Step 1 — Enumerate the tracked repos and the token's current scope

```
From team-portfolio.json:
  repos: [list all tracked repos]

From the PAT settings (platform.github.com → Settings → Developer settings → Personal access tokens):
  What repos does the current token have access to?
  What permissions does it have (read-only? write? admin?)?
```

Flag any mismatch: repos in the token that are not in `team-portfolio.json` (over-scoped), or repos in `team-portfolio.json` that are not in the token (collection gap).

## Step 2 — Apply the minimum-required permission set

For the `team-portfolio` use case, the required permissions are read-only and limited to:
- `repo` (for private repos) or no additional scopes (public repos only)
- Specifically: read access to commits, pull requests, issues, and releases

No write access is needed. No org-admin scope is needed. No webhook configuration scope is needed.

```
Minimum fine-grained PAT spec:
  Repository access: only the repos in team-portfolio.json
  Permissions:
    - Contents: Read
    - Pull requests: Read
    - Issues: Read
    - Metadata: Read (default)
  Expiry: 90 days (set a calendar reminder for rotation)
```

## Step 3 — Flag team-member departure scenarios

If a team member who created the PAT has left:
1. The PAT is tied to their account — it may be invalidated when the account is removed from the org.
2. Action: provision a new fine-grained PAT under a team/bot account or under the repo owner's account.
3. Update the `PORTFOLIO_TOKEN` secret in the hub repo's Action secrets.

## Step 4 — Review hub-repo access controls

The hub repo stores the collection outputs (reports, dashboard) and the workflow file. Confirm:
- The hub repo is not publicly readable if the reports contain non-public activity data.
- The `PORTFOLIO_TOKEN` secret is in the hub repo's Action secrets, not in `team-portfolio.json` or any committed file.
- The workflow file does not echo or print the token in any step.

## Step 5 — Produce the access review summary

```
Review date: YYYY-MM-DD
Token type: [fine-grained PAT / classic PAT / built-in]
Token owner: [username or bot account]
Token expiry: [date or "no expiry — set one"]

Repos in token vs team-portfolio.json:
  Over-scoped (in token, not in config): [list or "none"]
  Under-scoped (in config, not in token — collection gaps): [list or "none"]

Permission audit:
  Write access present: [yes — flag / no — OK]
  Admin scope present: [yes — flag / no — OK]
  Principle of least privilege: [PASS / FAIL]

Recommended actions:
  [ ] Re-provision as fine-grained PAT if currently classic
  [ ] Remove repos not in team-portfolio.json from token scope
  [ ] Set or update expiry date
  [ ] Rotate token (if team member has left or expiry is past)
```

## Pitfalls

- Ignoring the token after initial setup — a token provisioned with "I'll tighten it later" is the most common over-scope source.
- Using the GitHub Actions built-in token for private repos in other accounts — it can only read the current repo; fine-grained PAT is required for cross-account access.
- Rotating the token without updating the `PORTFOLIO_TOKEN` secret — the next scheduled run will fail with a 401, not a clear error message.

## See also

- [`../../CLAUDE.md`](../../CLAUDE.md) — §4 house opinion #2 and #3 (token in env, least privilege)
- [`../../skills/portfolio-setup/SKILL.md`](../../skills/portfolio-setup/SKILL.md) — initial token provisioning in Step 2
