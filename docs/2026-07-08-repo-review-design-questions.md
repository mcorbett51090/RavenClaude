# Repo review — decisions needed (2026-07-08)

Autonomous 3-panel repo review (expert finders → analysis/validation → tie-break).
This doc holds the confirmed issues that were **not** auto-implemented because they
need a release-management or policy **decision** from Matt. The mechanical,
non-design fixes are in the accompanying PR.

## What was implemented in the PR (no decision needed)

| Pri | Fix | File(s) |
|---|---|---|
| P1 | Stdin-JSON path fallback added to the 6 **ravenclaude-core** file hooks so they stop no-op'ing under Claude Code (`$CLAUDE_TOOL_FILE_PATH` is not a real hook var). | `hooks/{enforce-layout,format-on-write,guard-recursive-spawn,claim-grounding-lint,delegation-nudge}.sh` (regen-on-manifest-change already had it) |
| P2 | Supply-chain: pin `peter-evans/create-pull-request` to an immutable SHA (`c5a7806`, == v6.1.0) instead of the movable `@v6`. | `.github/workflows/quarantine-intake.yml` |
| P2 | `check-grep-ere-pcre.py` now catches separated-flag `grep -v -E '(?:…)'` (was only matching bundled `-vE`). + teeth fixture. | `scripts/check-grep-ere-pcre.py`, `scripts/audit-gates.sh` |
| P2 | `sanitize-webfetch-body.py` now strips the **unclosed** `<important>` variant (pattern 3 had no unterminated counterpart); comment corrected. + poisoned-fixture teeth. | `plugins/ravenclaude-core/scripts/sanitize-webfetch-body.py`, `tests/fixtures/webfetch/poisoned-body.txt` |
| P3 | `mark-web-domain-seen.sh` strips the trailing FQDN dot to mirror `guard-web-access.sh` (writer/reader agreed on seen-file path). | `plugins/ravenclaude-core/hooks/mark-web-domain-seen.sh` |
| P3 | `thing-decide.py` `_sanitize_reasoning` uses a set-of-10-grams scan (O(n+m), byte-identical behavior) instead of the O(n·m) substring scan over unbounded stdin input. | `plugins/ravenclaude-core/scripts/thing-decide.py` |

One Panel-1 finding was **rejected** by Panel 2 as a false positive: the claimed
off-by-one in the `quarantine-intake.yml` open-submission cap — the strict `-gt`
comparison is correct (the cap is exactly `MAX_OPEN` concurrent).

---

## Decision 1 (the big one) — the 66 domain advisory hooks share the P1 bug

**Same root cause as the P1 core-hook fix, replicated across 66 domain plugins.**
Every domain plugin ships one advisory anti-pattern hook (`check-*-anti-patterns.sh`
/ `flag-*-antipatterns.sh`) registered in its `hooks.json` as
`script.sh "$CLAUDE_TOOL_FILE_PATH"` and reading only `file="${1:-}"`. Because
`$CLAUDE_TOOL_FILE_PATH` is **not** a real Claude Code hook variable (the path
arrives on stdin as `tool_input.file_path`), the arg is empty under Claude Code
and **all 66 hooks silently no-op** — none of the advertised secret/CORS/auth/SQL/
IAM file checks ever inspect a written file.

- **Impact:** advisory only (these hooks print to stderr, never block), so no gate
  breaks and no security floor is bypassed — but every domain plugin's in-editor
  "anti-pattern" assistance is inert. Contrast `salesforce`'s hook, which already
  reads stdin and is unaffected.
- **The fix is purely mechanical and identical** to the 5 core hooks in the PR:
  insert the same stdin-JSON fallback block after `file="${1:-}"`.

**Why this wasn't auto-applied:** touching 66 domain plugins means, per the repo's
"bump semver on every user-visible change" convention, **66 `plugin.json` bumps +
66 matching `marketplace.json` entry bumps** (CI hard-fails on version drift). That
is a broad, consumer-facing release event (every one of those plugins would ship an
update on the next `/plugin marketplace update`) — the kind of high-blast release
this repo's own discipline routes to a human rather than an autonomous 200-file PR.

**Affected plugins (66):** analytics-engineering, api-engineering, applied-statistics,
auth-identity, aws-cloud, azure-cloud, backend-engineering, claude-app-engineering,
cli-tooling-engineering, cloud-native-kubernetes, construction-general-contractor,
cybersecurity-grc, data-governance-privacy, data-platform, data-science-research,
data-streaming-engineering, database-engineering, desktop-app-engineering,
developer-relations, devops-cicd, edtech-partner-success, email-engineering,
esg-sustainability-reporting, event-management, experimentation-growth-engineering,
field-service-management, finance, fintech-payments-engineering, frontend-engineering,
gcp-cloud, geospatial-engineering, incident-response-dfir, insurance-life-health-benefits,
legal-ops-clm, localization-i18n-engineering, manufacturing-operations,
microsoft-365-copilot, microsoft-fabric, microsoft-graph, ml-engineering,
mobile-engineering, network-engineering, observability-sre, open-source-maintenance,
optometry-eyecare-practice, performance-engineering, physical-therapy-rehab-clinic,
power-platform, product-management, public-sector-govtech, qa-test-automation,
realtime-collaboration-engineering, regulatory-compliance, retail-store-operations,
sales-engineering, security-engineering, staffing-operations, supply-chain-planning,
technical-program-management, technical-writing-docs, terraform-iac, trust-and-safety,
web-design, wordpress-cms-engineering.

**Recommendation:** Yes — fix all 66 in one dedicated follow-up PR, patch-bump each
plugin. It's the same proven fix, it's mechanical, and the current state means the
whole domain-hook value proposition is silently dead under Claude Code. I can run a
scripted, verified migration (insert the identical fallback block after each
`file="${1:-}"`, `bash -n` each, patch-bump both manifest mirrors in lockstep, add a
Gate-6-style stdin regression assertion). **Questions for you:**
  1. One batch PR for all 66, or split by domain family?
  2. Patch bump each plugin (my default), or a coordinated note that these are a
     single correctness sweep?
  3. Want me to proceed now, or hold?

## Decision 2 — Dependabot for GitHub Actions (complements the SHA pin)

The PR pins the one third-party action to a SHA. The finding also suggested adding
`.github/dependabot.yml` (`package-ecosystem: github-actions`) so pinned actions get
**deliberate** bump PRs instead of silently drifting or going stale. This opens
automated PRs on a schedule — a maintainer-workflow preference, so it's yours to
call.

**Recommendation:** add it (low-noise, weekly, actions-only). Say the word and I'll
include it.

## Decision 3 — pin the first-party `actions/*` too?

`actions/checkout@v4` and `actions/setup-python@v5` are also movable tags. Panel 2
rated these **lower-risk** (first-party GitHub-owned) — a policy call, not a
confirmed defect. Pin them to SHAs for uniform supply-chain discipline, or leave
first-party actions on major tags? Your call.
