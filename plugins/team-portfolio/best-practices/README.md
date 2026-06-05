# team-portfolio — best-practice docs

Named, citable rules for the `team-portfolio` plugin. Each file is **one rule** — read, applied, and cited whole. These rules cover cross-repo activity tracking, portfolio roll-up cadence, token and security posture, deterministic output, and routing between this plugin and its neighbours.

---

## Index

_10 rules._

| Doc | Status | Use when |
|---|---|---|
| [`github-is-the-source-of-truth-never-self-reported-logs.md`](./github-is-the-source-of-truth-never-self-reported-logs.md) | Absolute rule | Any design decision about where activity data lives or how it is collected. |
| [`token-lives-in-env-never-in-config.md`](./token-lives-in-env-never-in-config.md) | Absolute rule | Any token provisioning, config review, or security audit of the hub repo. |
| [`fail-soft-per-repo-one-bad-repo-never-sinks-the-run.md`](./fail-soft-per-repo-one-bad-repo-never-sinks-the-run.md) | Absolute rule | Any error-handling change to the collection scripts; any partial-run diagnosis. |
| [`zero-runtime-dependencies-keeps-the-action-portable.md`](./zero-runtime-dependencies-keeps-the-action-portable.md) | Absolute rule | Any feature addition to the portfolio scripts that might introduce a third-party import. |
| [`deterministic-output-makes-diffs-and-caching-trustworthy.md`](./deterministic-output-makes-diffs-and-caching-trustworthy.md) | Absolute rule | Any script change that touches serialization, sorting, or timestamp injection. |
| [`route-cross-repo-tracking-here-single-project-management-elsewhere.md`](./route-cross-repo-tracking-here-single-project-management-elsewhere.md) | Absolute rule | Any ambiguous routing decision between this plugin and project-management or ravenclaude-core. |
| [`unmatched-activity-is-signal-not-an-error.md`](./unmatched-activity-is-signal-not-an-error.md) | Pattern | Any output artifact design; any report review where unmatched counts appear. |
| [`roll-up-cadence-weekly-not-daily.md`](./roll-up-cadence-weekly-not-daily.md) | Pattern | Any Action schedule configuration or cadence review. |
| [`unauthenticated-runs-produce-incomplete-counts-say-so.md`](./unauthenticated-runs-produce-incomplete-counts-say-so.md) | Absolute rule | Any run that may be unauthenticated or rate-limited; any output honesty review. |
| [`cross-repo-project-tracking-uses-filters-not-manual-lists.md`](./cross-repo-project-tracking-uses-filters-not-manual-lists.md) | Absolute rule | Any cross-repo project configuration or project-filter design session. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../skills/portfolio-setup/SKILL.md`](../skills/portfolio-setup/SKILL.md) — the setup skill these rules govern.
- [`../skills/cross-repo-project-tracking/SKILL.md`](../skills/cross-repo-project-tracking/SKILL.md) — the cross-repo project tracking skill.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
