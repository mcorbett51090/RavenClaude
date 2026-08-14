# PR queue — analog-repos-gap-fill

**Owner:** marketplace-maintainer  
**Stop (copy into the decision record):** 0 `closeable` with `status=open`, **or** every remaining `closeable` is `queued` with owner + branch + named test, **and** F1 + F2 have shipped or been retagged, **and** L4 remains `accepted-limit`.

## This increment’s three slots

| id | title | gap_family | lattice | ships_in | files[] | acceptance_test | est_files/loc | depends_on_queue | version_bump | stop_eligible |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | WebFetch-only result sanitizer | L1 | C06 C15 | [#928](https://github.com/mcorbett51090/RavenClaude/pull/928) `feat/ravenclaude-core-webfetch-sanitize-hook` | `hooks/sanitize-webfetch-output.{sh,py}`, `hooks.json`, `RC_BASELINE.hooks` 32→33, manifests, CHANGELOG, dashboards | poisoned payload → `updatedToolOutput` + strip>0; clean → identity; crash → fail-open exit 0; `RC_BASELINE.hooks===33` | ~12 files / hook+regen (Yellow/Red split accepted on regen) | [] | `[verify-at-implement]` (0.266.0 claimed on branch; **CONFLICTING** vs current main) | true |
| F2 | Injection + analog-README minting evals | L2 L3 | C09 C15 | [#929](https://github.com/mcorbett51090/RavenClaude/pull/929) `feat/evals-injection-minting-cases` | `evals/cases/ravenclaude-core/*.yaml`, `evals/closeable_validator.py`, fixtures | `python3 evals/runner.py --self-test`; minting fixture fails C4; injection case judged fail | ~8 / evals-only | [] | none (evals are marketplace CI) | true |
| F3 | Promote survey catalog + matrix + decision | survey packaging | C01–C15 (docs) | this commit, `docs/` on `main` | `docs/plans/2026-08-14-analog-repos-gap-fill/**`, `docs/decisions/2026-08-14-analog-repos-gap-fill.md` | catalog header has date + N=13 + shortfall; matrix has RC paths; `test -e` every RC baseline path; checker exit 0 | 5 files / docs-only | [F1, F2] (does not block; F1/F2 stay queued) | none | true |

F3 adds **no** hook, skill, or agent. Claim 7 satisfied (≤3 fills).

## Leftovers (not a fourth fill)

| id | title | gap_family | lattice | ships_in | acceptance_test | est_files/loc | depends_on_queue | stop_eligible |
|---|---|---|---|---|---|---|---|---|
| Q1 | MCP result quarantine (`mcp__.*` `updatedToolOutput`) | L4 | C06 C15 | later forge | same fail-open fixtures on an MCP-shaped payload; House Rule 3 walkthrough | needs_split | [F1] | true |
| Q2 | Analog closeness scorecard skill | F-scorecard | C01–C15 | later forge | skill frontmatter + a must-fail fixture; **not** this increment (surface budget) | 4 / skill | [F3] | true |

DAG: F1 ∥ F2; F3 docs-only; Q1 after F1; Q2 after F3. Acyclic. No slot owns “all gaps.”

## Serial ban

Do not open another PR that edits `plugins/ravenclaude-core/.claude-plugin/plugin.json` while #928 is open. F2 and F3 do not touch it.
