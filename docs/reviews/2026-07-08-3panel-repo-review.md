# Autonomous 3-panel repo review — 2026-07-08

**Routine:** scheduled comprehensive repo review (find → validate → tie-break → implement → PR + design-questions doc).
**Branch:** `claude/stoic-fermat-3atqnf`

> **Reconciled against `main` (rebased 2026-07-08).** While this branch was open, `main` advanced with three other autonomous review runs (#579, #585, #588) plus #582 (SHA-pin actions) and #581 (hermetic audit-gates). Re-checking each finding against the new `main`: **3 were already fixed there** — #7 (create-pull-request SHA-pin, byte-identical), #8 (prettier `@3.9.4` pin), #9 (mark-web trailing-dot strip) — and **#2 (config_error) was fixed on main and better** (main *defers* on a config error). Those four are **dropped** from this PR. **This PR now carries the 5 findings `main` had not yet addressed:** #1, #3, #4, #5, #6. The branch was merged up to `main` and the surviving fixes re-applied on its new structure (the decision-engine `_tally` had a new `heimdall`-abstain path; audit-gates was rewritten hermetic; versions moved to rc 0.187.3 / finance 0.17.3 → this PR bumps to 0.187.4 / 0.17.4). Re-verified green post-merge.

## Method

- **Panel 1 (find):** 6 parallel expert finders partitioned across the code surface (Python generators, decision-engine Python, shell hooks/guards, CI/manifests/config, other-plugin code, tests/evals/JS). Each returned P0–P3 findings with a concrete `file:line` + failure scenario.
- **Panel 2 (validate):** each finding was validated by direct code inspection at the cited location (priorities confirmed, impact/effort assessed). The originating Workflow orchestrator was unavailable in this non-interactive run (permission-stream closed), so the panels ran via parallel subagents + main-loop validation.
- **Panel 3 (tie-break):** finder priorities were well-calibrated; no cross-panel priority disagreement required a tie-break. One P1-vs-P2 judgment (finding 1) was resolved to **P2** (binding mode is opt-in and off by default; high-blast still defers).

**Baseline:** every objective gate was green at the start of the run — JSON validity, shell syntax, hook executability, prettier, ruff, frontmatter, plugin↔marketplace version drift, and markdown link resolution. The repo is very well maintained; findings are targeted defects, not systemic issues.

## Confirmed findings (9) — all implemented in this PR

| # | Pri | Area | File | Fix |
|---|-----|------|------|-----|
| 1 | P2 | safety | [`thing-decide.py:455`](../../plugins/ravenclaude-core/scripts/thing-decide.py) | Unanimous panel `defer` no longer routed to the Thor tie-breaker (which could flip it to a binding yes/no). Short-circuit `distinct == {"defer"}` → `defer`. |
| 2 | P3 | robustness | [`thing-decide.py:495`](../../plugins/ravenclaude-core/scripts/thing-decide.py) | Surface `resolve_panel_config` error as `config_error` on the result (mirrors the command path). |
| 3 | P3 | test-coverage | [`evals/runner.py`](../../evals/runner.py) | Wire `runner.py --self-test` into `audit-gates.sh` (new Gate 128) + extend `--self-test` to exercise all four scorers. |
| 4 | P3 | correctness | [`evals/runner.py:117`](../../evals/runner.py) | `_tiny_yaml` peek uses the loop index, not `lines.index(raw)` (first-occurrence bug on duplicate lines). |
| 5 | P3 | robustness | [`generate-index-dashboard.py:1019`](../../scripts/generate-index-dashboard.py) | Splice the data payload **last**, after all sentinel substitutions, so a description equal to a sentinel can't corrupt the payload. |
| 6 | P3 | robustness | [`oauth_client.py:33`](../../plugins/finance/scripts/connectors/oauth_client.py) | Docstring corrected: the client _classifies_ a 429; the caller drives the Retry-After backoff. **(See open design question below.)** |
| 7 | P2 | security | [`quarantine-intake.yml:137`](../../.github/workflows/quarantine-intake.yml) | Pin `peter-evans/create-pull-request` to a full commit SHA (was mutable `@v6`) in the write-privileged, externally-triggered workflow. |
| 8 | P2 | robustness | [`validate-marketplace.yml:304`](../../.github/workflows/validate-marketplace.yml), [`regenerate-artifacts.yml:251`](../../.github/workflows/regenerate-artifacts.yml) | Pin prettier to `3.9.4` (was unpinned `npx --yes prettier`) — matches the ruff/actionlint pinning discipline; prevents a whole-tree wedge on an upstream release. |
| 9 | P3 | robustness | [`mark-web-domain-seen.sh:70`](../../plugins/ravenclaude-core/hooks/mark-web-domain-seen.sh) | Add the trailing-FQDN-dot strip so the writer's seen-file slug matches `guard-web-access.sh`; ends the re-prompt loop for dotted hosts. |

Each fix keeps the repo's gates green (verified via `audit-gates.sh`, including new Gate 128 and the extended Gate 17). Version bumps: `ravenclaude-core` 0.186.1 → 0.186.2, `finance` 0.17.1 → 0.17.2 (both mirrored in `marketplace.json` + CHANGELOG).

## Open question needing your input

### Q1 — `oauth_client.py`: correct the docstring (done) OR implement the retry loop?

**Context.** The OAuth connector's error-cause routing table documents `429 → BACKOFF_RETRY (honor Retry-After, then retry)`, and ships a `honor_retry_after()` helper — but the public API (`refresh` / `get_access_token`) raises `TokenRefreshError` on a 429 and never backs off or retries. `honor_retry_after` is referenced only by tests. So the shipped component makes a "then retry" promise it doesn't keep.

**What this PR did (the safe, zero-behavior-change half):** corrected the docstring to state accurately that the client _classifies_ the 429 while the **caller** honors Retry-After and re-invokes. This makes the module honest today. See [`oauth_client.py:33`](../../plugins/finance/scripts/connectors/oauth_client.py) and the raise at [`oauth_client.py:298`](../../plugins/finance/scripts/connectors/oauth_client.py).

**The design decision for you:** should the retry loop instead live **inside** the client (`_refresh_locked` sleeps `honor_retry_after(...)` and retries up to N times before raising)? That is a genuine behavior change in a finance GL-extract path — it needs a call on retry count, total time budget, and whether the client or the caller should own the loop — which is why it's deferred rather than guessed. QBO/Xero token endpoints do throttle in practice, so a caller that doesn't implement its own loop currently aborts the whole GL extract on a transient 429.

- **Recommendation:** if the intended contract is "the connector is self-healing on throttle," implement the in-client loop (bounded attempts + a max wait, honoring `Retry-After`) as a follow-up; otherwise the docstring correction is the complete fix and callers own the loop by contract.

> **RESOLVED (2026-07-08): implement it.** The in-client backoff-retry shipped as a follow-up (finance 0.17.5) — `_refresh_locked` now honors `Retry-After` and retries on 429/5xx up to `max_backoff_retries`, bounded by a total `backoff_budget_seconds` so it can't pin the per-entity lock; `REAUTH_REQUIRED` is never retried and the security invariants (no token leak, persist-then-use) are preserved and tested (`test_connectors.py` W2.6c). The docstring was updated to match the new behavior.

## Minor follow-up (no input needed)

- **Eval scorer coverage (finding 3).** This PR wired `--self-test` into CI (Gate 128) and added synthetic-input assertions for all four `score_*` functions. A fuller property/fixture suite over the scorers could be added later, but the "never run by CI" gap — the actual finding — is now closed.

## Notes

- The Workflow orchestrator (dynamic multi-agent) was unavailable this session (tool permission-stream closed in the non-interactive scheduled context); the 3-panel structure was preserved using the Agent tool + direct-inspection validation.
- No P0 or P1 findings survived validation. The repo's own guardrails were observed working during this run (e.g. `guard-destructive.sh` blocked a test-cleanup `rm -rf`).
