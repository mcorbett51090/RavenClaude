# team-portfolio — best-practice docs

Named, citable rules for the `team-portfolio` plugin. Each file is **one rule** — read, applied, and cited whole. These rules cover cross-repo activity tracking, portfolio roll-up cadence, token and security posture, deterministic output, and routing between this plugin and its neighbours.

---

## Index

_20 rules._

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
| [`collection-window-must-match-cron-interval.md`](./collection-window-must-match-cron-interval.md) | Absolute rule | Any change to the cron schedule or the collection-window-days setting. |
| [`activity-counts-are-not-performance-metrics.md`](./activity-counts-are-not-performance-metrics.md) | Absolute rule | Any report, dashboard, or summary that surfaces activity counts to a supervisor. |
| [`rotate-portfolio-token-on-team-member-departure.md`](./rotate-portfolio-token-on-team-member-departure.md) | Absolute rule | Any team-member offboarding where the departing person provisioned the portfolio token. |
| [`hub-repo-must-not-be-tracked-by-itself.md`](./hub-repo-must-not-be-tracked-by-itself.md) | Absolute rule | Initial hub setup; any time team-portfolio.json repos list is modified. |
| [`bot-and-ci-accounts-need-explicit-config-entries.md`](./bot-and-ci-accounts-need-explicit-config-entries.md) | Pattern | First few runs show unexpected unmatched activity; any repo with automation bots. |
| [`sample-activity-json-is-for-offline-testing-not-production.md`](./sample-activity-json-is-for-offline-testing-not-production.md) | Absolute rule | Any use of sample-activity.json outside of offline renderer testing or demos. |
| [`add-repos-to-config-before-expecting-them-in-reports.md`](./add-repos-to-config-before-expecting-them-in-reports.md) | Absolute rule | A new repo is created or a contractor's repo is added to the team's tracked scope. |
| [`project-filters-must-be-tested-with-a-dry-run-before-production.md`](./project-filters-must-be-tested-with-a-dry-run-before-production.md) | Pattern | A new cross-repo project filter is being added to team-portfolio.json. |
| [`narrative-layer-is-additive-not-corrective.md`](./narrative-layer-is-additive-not-corrective.md) | Absolute rule | Any use of activity-narrative.md — narrative adds context, never corrects counts. |
| [`cross-team-contributor-analysis-surfaces-patterns-not-verdicts.md`](./cross-team-contributor-analysis-surfaces-patterns-not-verdicts.md) | Pattern | Any use of contributor analysis output — the patterns inform conversations, not decisions. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../skills/portfolio-setup/SKILL.md`](../skills/portfolio-setup/SKILL.md) — the setup skill these rules govern.
- [`../skills/cross-repo-project-tracking/SKILL.md`](../skills/cross-repo-project-tracking/SKILL.md) — the cross-repo project tracking skill.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
