# Changelog — hospice-referral-sales

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.2] — 2026-07-09

### Fixed

- **Advisory anti-pattern hook now fires under Claude Code.** `hooks/flag-hospice-referral-sales-antipatterns.sh` read the target path only from `$CLAUDE_TOOL_FILE_PATH` (`$1`) — not a real Claude Code hook variable — so under Claude Code it received an empty path and silently no-op'd. Added the canonical stdin-JSON `.tool_input.file_path` fallback so the hook inspects the written file as intended. Advisory-only (no gate/behavior change beyond the hook actually running now). From the 2026-07-09 autonomous repo review (Decision 1).

## [0.1.0] — 2026-06-05

Initial release. A compliance-first referral-development team for a hospice sales / community-education representative (community liaison, patient care coordinator, hospice care consultant, account executive).

- **6 agents** — `referral-development-strategist`, `hospice-eligibility-educator`, `referral-account-manager`, `admissions-conversion-coach`, `goals-of-care-conversation-coach`, `hospice-sales-compliance-advisor`. Each carries the scenario-authoring frontmatter schema (audience / works_with / scenarios / quickstart).
- **6 skills** — `referral-territory-development`, `hospice-eligibility-criteria` (+ LCD quick-reference resource), `referral-account-planning`, `admissions-funnel-analytics`, `goals-of-care-conversations`, `hospice-sales-compliance` (+ AKS safe-harbor resource).
- **6 slash commands** — `/plan-referral-territory`, `/screen-hospice-eligibility`, `/prep-referral-review`, `/analyze-admissions-funnel`, `/coach-hospice-conversation`, `/compliance-check-outreach`.
- **4-doc knowledge bank** — `hospice-sales-decision-trees.md` (6 Mermaid trees), `hospice-sales-glossary.md`, `hospice-eligibility-lcd-reference.md` (published LCD decline criteria by diagnosis, framed as education not certification, dated + sourced), `hospice-sales-compliance-reference.md` (AKS / Stark / beneficiary-inducement CMP / OIG hospice risk areas / HIPAA, dated + sourced).
- **14 best-practices** — led by `the-rep-educates-eligibility-the-physician-certifies-it.md` and `every-referral-source-arrangement-must-clear-anti-kickback.md`.
- **Scenarios bank** — 4 dated, scope-tagged, web-sourced narratives (marketplace 9-field schema, `product_version: "n/a"`): late-referral / short length-of-stay, SNF partner relationship recovery, end-stage heart-failure eligibility education, and the gift/inducement compliance line.
- **6 templates** — referral account plan, referral-partner review, territory plan, in-service education brief, hospice-conversation prep, compliance self-check.
- **Runnable calculator** — `scripts/hospice_calc.py` (`funnel` / `census` / `benefit-periods` / `eligibility-indicators`), zero-dependency stdlib Python. The `eligibility-indicators` subcommand is explicitly educational and defers every determination to the attending physician / medical director.
- **Advisory hook** — `hooks/flag-hospice-referral-sales-antipatterns.sh` flags the three highest-consequence anti-patterns (PHI in a deliverable, an eligibility/coverage guarantee by the rep, an un-cleared value exchange). Advisory by default; `HOSPICE_REFERRAL_SALES_STRICT=1` makes it blocking.

### Defining discipline

The plugin's whole reason for existing in a regulated space: **the representative educates referral sources on the published eligibility criteria; the attending physician and hospice medical director certify it. Every value exchange clears the Anti-Kickback Statute first. PHI is protected at every step.** This is enforced in every agent constitution, the §6 Output Contract (mandatory `Patient-data / PHI note:` and `Compliance note:` lines), the §5 hard line ("the agents do not certify, diagnose, prognose, guarantee admission, promise coverage, or render legal rulings"), and the advisory hook.

### Shared-file changes (orchestrator-owned)

- `.claude-plugin/marketplace.json` — new catalog entry pinned at `0.1.0` (matches `plugin.json`).
- `docs/architecture.md` — Status-table row added (required by `scripts/check-marketplace-claims.py --structural-only`).
- `.repo-layout.json` — no new glob required; every path falls under existing `plugins/*/…` globs.
