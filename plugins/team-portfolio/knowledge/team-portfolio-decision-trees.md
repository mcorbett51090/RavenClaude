# Team portfolio decision trees

Which approach for which situation — traverse top-to-bottom before picking a method. Last reviewed: 2026-06-05.

## Decision Tree: Routing — This Plugin vs Neighbouring Plugins

**When this applies:** A request arrives that involves tracking, reporting, or managing work across repos or people. The agent needs to decide whether to use the `team-portfolio` plugin's skills, the `cross-repo-project-tracking` skill, the `project-management` plugin, or `ravenclaude-core/project-manager`. The wrong route produces the wrong deliverable.

**Last verified:** 2026-06-05 against `team-portfolio` CLAUDE.md §3 routing rules and §8 seams.

```mermaid
flowchart TD
    START[Request involves tracking or reporting work] --> Q1{Does the request ask for activity ACROSS multiple repos or people?}
    Q1 -->|yes - cross-repo or cross-person view| Q2{Does the request name a specific project that spans multiple repos?}
    Q2 -->|yes - named cross-repo project| LEAF_A[cross-repo-project-tracking skill - team-portfolio plugin]
    Q2 -->|no - general activity roll-up| LEAF_B[portfolio-setup skill plus collection scripts - team-portfolio plugin]
    Q1 -->|no - single effort or single repo| Q3{Does the request involve sprint facilitation, EVM, risk registers, or PMO governance?}
    Q3 -->|yes - deep PM craft| LEAF_C[project-management plugin]
    Q3 -->|no| Q4{Does the request involve RAID hygiene, action items, or status on a single effort?}
    Q4 -->|yes| LEAF_D[ravenclaude-core project-manager agent]
    Q4 -->|no - prose polish on a portfolio narrative| LEAF_E[ravenclaude-core documentarian agent]
```

**Rationale per leaf:**
- *cross-repo-project-tracking* — a named project spanning multiple repos needs the filter-based tracking model, not just raw activity counts.
- *portfolio scripts* — an undifferentiated cross-repo roll-up is the base collection use case for this plugin.
- *project-management plugin* — deep PM craft (predictive baselines, EVM, scored risk) belongs to the specialist plugin that carries PMBOK/Agile canon.
- *ravenclaude-core project-manager* — RAID/status hygiene on a single effort is the core agent's lane; it does not require the deep PM plugin.
- *documentarian* — prose polish on a generated report is a writing task, not a tracking task.

**Tradeoffs summary:**

| Method | Cost / time | What you get | Use when |
|---|---|---|---|
| cross-repo-project-tracking skill | Minutes to configure | Project-attributed activity with filter-defined scope | Named effort spanning repos |
| portfolio scripts | Minutes to run | Raw cross-repo activity counts by person/repo | Weekly supervisor view |
| project-management plugin | Deeper engagement | EVM, sprint plan, scored risk register | Running or governing a project |
| ravenclaude-core project-manager | Minutes to hours | RAID log, action items, status hygiene | Single effort, hygiene focus |

## Decision Tree: Collection Problem — Diagnose Why Counts Are Wrong

**When this applies:** The portfolio output is missing repos, showing zero counts for known activity, or showing different counts on consecutive runs with the same time window. The agent needs to identify the root cause before recommending a fix.

**Last verified:** 2026-06-05 against GitHub API behavior and `team-portfolio` script architecture.

```mermaid
flowchart TD
    START[Portfolio counts appear wrong or missing] --> Q1{Is the affected repo listed in team-portfolio.json?}
    Q1 -->|no - repo not in config| LEAF_A[Config gap - add the repo to team-portfolio.json and re-run]
    Q1 -->|yes - repo is in config| Q2{Does the run log show a skip or error for the repo?}
    Q2 -->|yes - skip or error logged| Q3{What is the error type?}
    Q3 -->|403 - access denied| LEAF_B[Token scope problem - verify PORTFOLIO TOKEN has read access to this repo - check fine-grained PAT permissions]
    Q3 -->|404 - not found| LEAF_C[Repo moved or renamed - update team-portfolio.json with the current repo path]
    Q3 -->|rate limit hit| LEAF_D[Authentication or cadence problem - confirm token is set and collection window matches cron interval]
    Q2 -->|no - no skip logged - counts just differ| Q4{Are the counts different on consecutive runs with the same date range?}
    Q4 -->|yes - nondeterministic output| LEAF_E[Determinism bug - check for unsorted dict iteration or per-row timestamp injection in the scripts]
    Q4 -->|no - counts stable but lower than expected| LEAF_F[Collection window mismatch - verify collection-window-days matches the cron interval - no overlap and no gap]
```

**Rationale per leaf:**
- *Config gap* — the most common cause; the repo was added to the team but not to the config.
- *Token scope* — fine-grained PATs scope permissions per repo; a new repo may need an explicit grant.
- *Repo renamed* — GitHub redirects API calls to renamed repos, but the config path needs updating for clarity and correctness.
- *Rate limit* — an unauthenticated or misconfigured run hits the rate limit and skips the tail of the repo list.
- *Determinism bug* — nondeterministic output on identical inputs indicates a sorting or timestamp injection problem in the scripts.
- *Window mismatch* — a `collection_window_days` shorter than the cron interval creates gaps; longer creates double-counting.

**Tradeoffs summary:**

| Root cause | Fix effort | Impact if unfixed | Detectability |
|---|---|---|---|
| Config gap | Minutes | Missing repo entirely | Obvious - known repo absent |
| Token scope 403 | Minutes - PAT update | Repo skipped with error | Error log present |
| Repo renamed 404 | Minutes - config update | Repo skipped with error | Error log present |
| Rate limit | Minutes - add token | Tail repos silently skipped | Warning banner if surfaced |
| Determinism bug | Hours - script fix | Unstable diffs and caching | Only visible on re-run |
| Window mismatch | Minutes - config update | Gaps or double-counts | Subtle - needs manual check |

## Decision Tree: Project Filter Design — How to Define a Cross-Repo Project

**When this applies:** A user wants to track a named project (e.g., "Website Redesign", "API v2") that spans work across multiple repos. The agent needs to recommend a filter strategy that will capture the right events without over-matching (pulling in unrelated activity) or under-matching (missing project work).

**Last verified:** 2026-06-05 against `team-portfolio` cross-repo-project-tracking skill and filter evaluation model.

```mermaid
flowchart TD
    START[User wants to track a named cross-repo project] --> Q1{Does the project have dedicated repos used only for that project?}
    Q1 -->|yes - one or more dedicated repos| LEAF_A[Repo-level match - add those repos to match-repos in the project filter - all activity is attributed to the project]
    Q1 -->|no - shared repos used across multiple projects| Q2{Do team members use consistent PR/issue labels for this project?}
    Q2 -->|yes - consistent labels| LEAF_B[Label match - add the label to match-labels - works across all shared repos without over-matching]
    Q2 -->|no - labels not used consistently| Q3{Do PR and issue titles follow a consistent naming prefix for this project?}
    Q3 -->|yes - consistent title prefix| LEAF_C[Title-prefix match - add the prefix to match-title-prefix - lower maintenance than labels]
    Q3 -->|no - no consistent naming| LEAF_D[No viable filter - recommend that the team adopt a label or title convention before tracking - document why unstructured activity cannot be auto-matched]
```

**Rationale per leaf:**
- *Repo-level match* — the cleanest filter; when a repo is dedicated to the project, 100% of its activity is attributable and no per-item discipline is needed from the team.
- *Label match* — reliable when the team applies labels consistently; requires labeling discipline but does not require title changes.
- *Title-prefix match* — the lowest-friction option for teams that don't use labels; a `[website]` prefix is easy to adopt and easy to scan.
- *No filter* — tracking unstructured activity produces noise, not insight; the honest recommendation is to establish a naming convention first.

**Tradeoffs summary:**

| Filter type | Team discipline required | Over-match risk | Under-match risk | Use when |
|---|---|---|---|---|
| Repo-level | None - automatic | Low if repos are dedicated | Low | Project has dedicated repos |
| Label match | Labeling every PR/issue | Low | Medium - unlabeled items missed | Shared repos, label discipline exists |
| Title prefix | Prefixing every PR/issue title | Low | Medium - unprefixed items missed | Shared repos, no label habit |
| No filter | N/A | N/A | N/A | Avoid - recommend convention first |
