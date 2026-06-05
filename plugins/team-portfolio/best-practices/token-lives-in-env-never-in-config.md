# The portfolio token lives in the environment — never in team-portfolio.json

**Status:** Absolute rule
**Domain:** Team portfolio / security / secrets management
**Applies to:** `team-portfolio`

---

## Why this exists

`team-portfolio.json` is a configuration file that lives in a repository and is committed to version control. A GitHub token committed to version control is exposed in every clone, fork, pull, and CI artifact that uses the repo. GitHub's secret scanning catches many committed tokens and invalidates them automatically — but the invalidation happens after the exposure, and private repos may not have secret scanning enabled. The access pattern for the portfolio token (read-only, scoped to specific repos) is exactly the kind of credential that should be trivial to rotate; committing it makes rotation into an incident response event.

## How to apply

Read the token exclusively from environment variables, in this priority order:

```python
import os

token = (
    os.environ.get("PORTFOLIO_TOKEN")
    or os.environ.get("GITHUB_TOKEN")
    or os.environ.get("GH_TOKEN")
)
if not token:
    raise RuntimeError(
        "No token found. Set PORTFOLIO_TOKEN, GITHUB_TOKEN, or GH_TOKEN. "
        "Never put a token in team-portfolio.json."
    )
```

For the GitHub Actions workflow:
```yaml
env:
  PORTFOLIO_TOKEN: ${{ secrets.PORTFOLIO_TOKEN }}
```

For local runs: set `PORTFOLIO_TOKEN` in the shell session or in a `.env` file that is listed in `.gitignore`.

**Do:**
- Use a fine-grained GitHub PAT with read-only access scoped to only the tracked repos — not a classic PAT, and never an org-admin token.
- Rotate the token on any suspected exposure and whenever a person with access to the token leaves the team.
- Add `.env` to `.gitignore` in the hub repo if you store the token there for local development.

**Don't:**
- Embed the token value in `team-portfolio.json`, any script, or any template.
- Use an org-admin or write-capable token; the portfolio scripts require only `repo:read` (or the fine-grained equivalent).
- Print the token value in any script log, even a debug log.

## Edge cases / when the rule does NOT apply

- This rule has no exceptions. A token in a config file is a security incident regardless of the repo's visibility. If you encounter a token in the config, flag it as a security issue and rotate it before proceeding.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — house opinions §4 #2 and §4 #3 state this rule and the least-privilege principle.
- [`../skills/portfolio-setup/SKILL.md`](../skills/portfolio-setup/SKILL.md) — the setup skill that provisions the token correctly.

## Provenance

Derived from `team-portfolio` plugin CLAUDE.md §4 house opinions #2 ("Secrets live in env/secrets, never in `team-portfolio.json`") and #3 ("Least privilege"). Reinforced by GitHub secret scanning policy and standard secrets management practice.

---

_Last reviewed: 2026-06-05 by `claude`_
