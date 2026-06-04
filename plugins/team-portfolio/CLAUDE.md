# team-portfolio — plugin constitution

Centralized, multi-repo, multi-person activity & project tracking for a team. This file
governs how the Team Lead and agents behave when a request touches cross-repo activity
tracking, weekly/status roll-ups, or a supervisor's manage-the-team view. It **extends**
`ravenclaude-core` — it inherits the Capability Grounding, Structured Output, Last-Mile
Completion, and Claim-Grounding protocols and does not restate them.

## 1. What this plugin is (and is not)

- **Is:** a thin hub that reads the GitHub API across many repos and rolls activity up by
  person, repo, and cross-repo project — plus the markdown reports, HTML dashboard,
  scheduled Action, and on-demand command around it.
- **Is not:** a replacement for `ravenclaude-core/project-manager` (RAID/status hygiene) or
  the `project-management` plugin (delivery craft). Those run *a* project; this **observes
  activity across all of them**. A request to facilitate a sprint or score a risk register
  routes there; a request to "see who did what across my repos" routes here.

## 2. No agents — by design

This plugin ships **no agents**. Per the marketplace house rule (domain plugins extend core
via skills + knowledge, not parallel agents), the work here is deterministic tooling +
playbooks: the core `project-manager` / `documentarian` agents drive it via the skills and
scripts below. There is no review or architecture judgment that a core agent handed these
skills couldn't produce.

## 3. Routing rules (Team Lead)

| Request signal | Route to |
| --- | --- |
| "track activity across my repos", "who did what", "weekly tracker across repos" | `portfolio-setup` skill → the scripts |
| "track a project that spans repos", "roll up the website work" | `cross-repo-project-tracking` skill |
| "refresh the portfolio / show the latest" | `/portfolio-refresh` command |
| run/own a single project, sprint facilitation, scored risk register | `project-management` plugin (not here) |
| RAID/status hygiene on one effort | `ravenclaude-core/project-manager` (not here) |

## 4. House opinions (every invocation enforces)

1. **GitHub is the source of truth; logs are the optional narrative layer.** Never propose a
   tracking doc *inside each tracked repo* — that is the exact failure this plugin exists to
   fix. The hub reads GitHub; it does not ask repos to self-report.
2. **Secrets live in env/secrets, never in `team-portfolio.json`.** The token is read from
   `PORTFOLIO_TOKEN` → `GITHUB_TOKEN` → `GH_TOKEN`. If you ever find a token in the config,
   flag it as a security issue.
3. **Least privilege.** A read-only token scoped to the tracked repos — never org-admin,
   never write — is the recommendation. Don't suggest a broader scope than the task needs.
4. **Zero runtime dependencies.** The scripts are pure standard library so they run in a bare
   GitHub Action and a plain `python3` session unchanged. Don't add `requests` / PyYAML /
   anything that needs `pip install`; if a feature seems to need one, reach for the stdlib
   equivalent or reconsider.
5. **Fail soft per repo.** One unreadable repo (private, 404'd, renamed) records an error and
   is skipped — it never sinks the whole run. Preserve that property in any change.
6. **Deterministic output.** Same input → same `portfolio-activity.json`, same reports, same
   HTML. Don't introduce nondeterminism (unsorted dict iteration, timestamps in rendered
   bodies beyond the declared `generated_at`).

## 5. Anti-patterns to flag

- A token committed to the config or printed into an artifact / log.
- Re-introducing a per-repo activity log "as well" — it re-creates the blind spot.
- Claiming counts are complete when the run was unauthenticated or skipped repos (the
  reports/dashboard surface both states with a banner — keep it honest).
- Treating "unmatched" activity (no project) as an error — it's normal.

## 6. Skills in this plugin

| Skill | Use for |
| --- | --- |
| [`portfolio-setup`](skills/portfolio-setup/SKILL.md) | Stand up the hub: config, token, Action, command, optional narrative. |
| [`cross-repo-project-tracking`](skills/cross-repo-project-tracking/SKILL.md) | Define + track a project spanning multiple repos (repo / label / title-prefix match). |

## 7. Scripts, templates & knowledge

- `scripts/portfolio-collect.py` — GitHub REST API → `portfolio-activity.json` (stdlib only).
- `scripts/portfolio-report.py` — activity JSON → `weekly-tracker.md` + `activity-rollup.md` +
  `project-status.md`.
- `scripts/portfolio-dashboard.py` — activity JSON → self-contained `portfolio.html`.
- `templates/team-portfolio.json` — the config schema (copy to the hub repo).
- `templates/portfolio-tracker.yml` — the scheduled GitHub Action (copy to the hub repo).
- `templates/activity-narrative.md` — optional hand-maintained note template.
- `templates/sample-activity.json` — fixture for an offline demo of the renderers.
- [`knowledge/multi-repo-tracking-model.md`](knowledge/multi-repo-tracking-model.md) — the
  event data model, gathering boundaries, the where-should-tracking-live decision tree, and
  the privacy posture.

## 8. Seams to neighbouring plugins

- **`project-management`** — owns running a project (schedule, EVM, sprints, risk registers).
  This plugin feeds it observed cross-repo activity; it does not duplicate delivery craft.
- **`ravenclaude-core/project-manager`** — lightweight RAID/status hygiene on a single effort.
- **`ravenclaude-core/documentarian`** — prose polish on the narrative layer.
- **`ravenclaude-core/security-reviewer`** — any token-handling / scope question escalates here.

## 9. Requires

`ravenclaude-core@>=0.7.0`.
