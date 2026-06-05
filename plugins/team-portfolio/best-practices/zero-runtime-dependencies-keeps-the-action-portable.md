# Use only Python stdlib — zero runtime dependencies keeps the Action portable

**Status:** Absolute rule
**Domain:** Team portfolio / engineering / portability
**Applies to:** `team-portfolio`

---

## Why this exists

The portfolio scripts run in two contexts: the consumer's GitHub Action (a bare `ubuntu-latest` runner with Python 3 and nothing else pre-installed) and a developer's local `python3` session. A script that imports `requests`, `PyYAML`, `httpx`, or any other third-party library requires a `pip install` step in both contexts. In the Action, this adds latency and a dependency on PyPI availability. Locally, it requires the developer to have the right package installed. Every additional dependency also expands the attack surface for supply-chain vulnerabilities. Python's standard library includes `urllib.request` for HTTP, `json` for parsing, `csv` for tabular output, `html` for HTML generation, and `datetime` for time handling — the complete stack the portfolio scripts need.

## How to apply

Before adding any import to a portfolio script, check whether the standard library provides it:

| Need | stdlib module | Third-party to avoid |
|---|---|---|
| HTTP requests | `urllib.request`, `http.client` | `requests`, `httpx`, `aiohttp` |
| JSON parsing | `json` | `simplejson` |
| YAML parsing | Use JSON config instead | `PyYAML`, `ruamel.yaml` |
| Date/time | `datetime`, `zoneinfo` | `arrow`, `pendulum`, `dateutil` |
| HTML generation | `html`, string templates | `jinja2`, `markupsafe` |
| CSV output | `csv` | `pandas` |
| Environment variables | `os.environ` | `python-dotenv` |
| Argument parsing | `argparse` | `click`, `typer` |

If a feature genuinely cannot be implemented with stdlib alone, reconsider the feature before adding a dependency. Document the decision in the PR.

**Do:**
- Write the GitHub Action's Python step as `python3 scripts/portfolio-collect.py` with no preceding `pip install` step.
- Use `urllib.request.urlopen` with `Authorization` headers for GitHub API calls.
- Generate HTML using f-strings or `html.escape()` rather than a template engine.

**Don't:**
- Add a `requirements.txt` to the plugin — its absence is the contract.
- Use `requests.get()` — even if it is available locally, it will fail in a bare Action runner.
- Introduce `pandas` for data manipulation — `collections.Counter`, `itertools`, and list comprehensions cover what the portfolio scripts need.

## Edge cases / when the rule does NOT apply

- A consumer who extends the portfolio scripts for their own project can add dependencies to their own copy — this rule governs the plugin's canonical scripts, not consumer forks.
- Future Python versions that promote a currently-third-party library to stdlib (e.g., `tomllib` was added in Python 3.11) — evaluate at the time.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — house opinion §4 #4 states this rule ("Zero runtime dependencies").
- [`../skills/portfolio-setup/SKILL.md`](../skills/portfolio-setup/SKILL.md) — the setup flow that demonstrates no-install usage.

## Provenance

Derived from `team-portfolio` plugin CLAUDE.md §4 house opinion #4 ("Zero runtime dependencies"). Reinforced by GitHub Actions runner environment constraints and supply-chain security practice.

---

_Last reviewed: 2026-06-05 by `claude`_
