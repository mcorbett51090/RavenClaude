# Fail soft per repo — one unreadable repo must never sink the whole run

**Status:** Absolute rule
**Domain:** Team portfolio / reliability / error handling
**Applies to:** `team-portfolio`

---

## Why this exists

A portfolio run that fails entirely when a single tracked repo returns a `404`, a `403`, or a network timeout is an unreliable tool that the team will stop trusting after the first surprise failure. In practice, tracked repos go private, get renamed, get archived, or have their access token scope narrowed — not as coordinated events but as independent operations across multiple teams. A portfolio run that skips one unavailable repo and reports the skip clearly is much more useful than one that halts and produces no output. The supervisor reading the weekly report needs to know that the counts are complete except for one named repo with a stated reason, not that the run failed silently.

## How to apply

Wrap per-repo collection in a try/except that records the error and continues:

```python
errors = []
results = []

for repo in config["repos"]:
    try:
        data = collect_repo(repo, token)
        results.append(data)
    except PermissionError as e:
        errors.append({"repo": repo["name"], "status": "403 - access denied", "detail": str(e)})
    except FileNotFoundError as e:
        errors.append({"repo": repo["name"], "status": "404 - not found", "detail": str(e)})
    except Exception as e:
        errors.append({"repo": repo["name"], "status": "error", "detail": str(e)})

# Surface errors in every output artifact
if errors:
    # Add a visible banner to weekly-tracker.md and portfolio.html
    report_errors(errors)
```

Surface the skipped repos prominently in every output artifact — a banner at the top of `weekly-tracker.md`, a warning tile in `portfolio.html`, and a non-zero exit code from the script.

**Do:**
- Record the error reason (HTTP status code, exception type) in the output, not just "repo skipped."
- Exit with a non-zero code when any repo was skipped, so a GitHub Action can distinguish a partial run from a clean run.
- Include skipped repos in the output JSON (`portfolio-activity.json`) as entries with an `error` status, so downstream scripts do not silently miss them.

**Don't:**
- Suppress the skip silently — an invisible skip produces a report that looks complete but is not, which is worse than a visible failure.
- Fail the entire run on a single repo error — the remaining repos' data is still valuable.
- Treat a `403` and a `404` identically; a `403` means the token lacks scope (likely fixable) and a `404` means the repo moved or was deleted (likely a config update).

## Edge cases / when the rule does NOT apply

- If the number of skipped repos exceeds a configured threshold (e.g., more than 50% of tracked repos fail), consider treating the run as degraded and suppressing the output entirely to avoid presenting a misleading partial picture.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — house opinion §4 #5 states this rule ("Fail soft per repo").
- [`./github-is-the-source-of-truth-never-self-reported-logs.md`](./github-is-the-source-of-truth-never-self-reported-logs.md) — the output banner must distinguish "no activity" from "skipped - not read."

## Provenance

Derived from `team-portfolio` plugin CLAUDE.md §4 house opinion #5 ("Fail soft per repo"). Reinforced by standard resilience patterns for API fan-out collection.

---

_Last reviewed: 2026-06-05 by `claude`_
