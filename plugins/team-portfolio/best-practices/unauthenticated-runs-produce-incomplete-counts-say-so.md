# An unauthenticated run produces incomplete counts — surface this prominently

**Status:** Absolute rule
**Domain:** Team portfolio / data quality / transparency
**Applies to:** `team-portfolio`

---

## Why this exists

GitHub's unauthenticated API rate limit is 60 requests per hour, shared across the IP address. A portfolio collection across 10 repos with commit, PR, issue, and review event queries easily exceeds 60 API calls. When the rate limit is hit, the collection silently skips the remaining repos and events. An output that appears complete but is missing 40% of the repos is worse than a clearly partial output — the supervisor reads the numbers as authoritative and acts on incomplete information. The same risk applies to runs against private repos without a token: the API returns a `404`, the repo is skipped, and the counts are understated without explanation.

## How to apply

Detect unauthenticated or rate-limited runs and surface them with a prominent banner in every output artifact:

```python
def check_auth_and_rate(token):
    """Returns (authenticated: bool, remaining: int, reset_at: str)"""
    import urllib.request
    url = "https://api.github.com/rate_limit"
    headers = {"Authorization": f"token {token}"} if token else {}
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers=headers)
        ) as resp:
            data = json.loads(resp.read())
            remaining = data["rate"]["remaining"]
            reset_at = data["rate"]["reset"]
            return bool(token), remaining, reset_at
    except Exception:
        return False, 0, "unknown"
```

In `weekly-tracker.md`:
```markdown
> **WARNING — PARTIAL RUN:** This report was generated without authentication
> (or with a token that lacked scope). Rate limit exhausted after N repos.
> Counts for the following repos are missing: [list]. Authenticate to get
> complete results.
```

In `portfolio.html`, render a persistent warning banner at the top of the page (not a dismissable notification).

**Do:**
- Check remaining rate limit before the collection begins and warn if it is insufficient for the planned run.
- Include the list of skipped repos in the warning, with the reason (unauthenticated, rate limited, or token scope).
- Exit with a non-zero code on partial runs — this distinguishes partial from clean in CI.

**Don't:**
- Present partial counts without the warning — a supervisor reading "47 commits" when the actual total is 83 will make decisions on wrong data.
- Suppress the warning to make the output look cleaner — the warning is a data-quality signal that the supervisor needs.
- Retry indefinitely waiting for the rate limit to reset — set a maximum wait of one reset window and then fail soft with a partial-run marker.

## Edge cases / when the rule does NOT apply

- A fully authenticated run against public repos only is unlikely to hit the authenticated rate limit (5,000 requests per hour) in a typical portfolio. The banner is still displayed if any repo is skipped for any reason.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — anti-pattern §5 "Claiming counts are complete when the run was unauthenticated or skipped repos."
- [`./fail-soft-per-repo-one-bad-repo-never-sinks-the-run.md`](./fail-soft-per-repo-one-bad-repo-never-sinks-the-run.md) — the per-repo error handling that produces the skip list this banner cites.

## Provenance

Derived from `team-portfolio` plugin CLAUDE.md §5 anti-patterns and GitHub API rate-limit behavior. The "be honest about completeness" principle is a direct extension of the claim-grounding discipline in `ravenclaude-core`.

---

_Last reviewed: 2026-06-05 by `claude`_
