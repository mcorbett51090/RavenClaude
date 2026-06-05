# Rotate the portfolio token when a team member who provisioned it departs

**Status:** Absolute rule
**Domain:** Team portfolio / token security
**Applies to:** `team-portfolio`

---

## Why this exists

A GitHub Personal Access Token (PAT) is tied to the account that created it. When a team member who provisioned the `PORTFOLIO_TOKEN` departs and their account is removed from the organization, the PAT is invalidated — the next scheduled run fails with a 401, and the portfolio goes dark without a clear error message in the supervisor's dashboard. Worse, in the window between departure and account removal, the departing member's account retains token access to all repos scoped in the PAT. Rotating the token on departure eliminates both the fragility and the access risk.

## How to apply

When a team member leaves (or when the person who provisioned the token changes roles):

```
1. Provision a new fine-grained PAT under the repo owner's account or a shared team account
   → Same permissions as the original (read-only, scoped to repos in team-portfolio.json)
   → Set an expiry date on the new PAT

2. Update the PORTFOLIO_TOKEN secret in the hub repo:
   Hub repo → Settings → Secrets and variables → Actions → PORTFOLIO_TOKEN → Update secret

3. Trigger a manual run to verify the new token works:
   Actions → portfolio-tracker → Run workflow

4. Revoke the old PAT if it is still active:
   → The departing team member should revoke it from their GitHub account
   → If they are no longer reachable: escalate to the org admin to revoke via org settings

5. Document the rotation:
   → Update the token-owner field in the hub repo's README or PORTFOLIO_OWNER.md
   → Note the rotation date
```

**Do:**
- Treat a planned team-member departure as a token-rotation trigger on the same timeline as their offboarding.
- Keep a record of which account owns the current token so rotations can be planned proactively.

**Don't:**
- Wait until the token fails with a 401 to rotate — the failure happens after the account is removed, which may be immediate or may be a delayed offboarding process.
- Provision the new PAT under another team member's personal account — use a shared team or bot account so the next departure doesn't repeat this scenario.

## Edge cases / when the rule does NOT apply

- The portfolio uses only the GitHub Actions built-in `GITHUB_TOKEN` (all repos public, no cross-account access) — this token auto-rotates per run and is not tied to any individual's account; team-member departure has no token impact.

## See also

- [`../skills/portfolio-access-review/SKILL.md`](../skills/portfolio-access-review/SKILL.md) — the full token audit and rotation procedure
- [`../CLAUDE.md`](../CLAUDE.md) — §4 house opinion #2 (token in env, never in config) and #3 (least privilege)

## Provenance

Derived from `team-portfolio` house opinion #2 (secrets live in env/secrets, never in config) and the `portfolio-access-review` skill's token-rotation procedure. Token tied to a departed account is a routine failure mode that preventative rotation eliminates.

---

_Last reviewed: 2026-06-05 by `claude`_
