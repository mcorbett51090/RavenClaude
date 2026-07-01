# Repo review — deferred findings needing your decision (2026-07-01)

A three-panel review (six parallel expert finders → validation → tie-break) swept
the whole repo's code surface (37 Python scripts, 9 shell scripts, 156 hooks, 6 CI
workflows, 3 schemas, 119 plugin manifests). The **design-free fixes are already
implemented** in the accompanying PR (`claude/stoic-fermat-n4gfwi`), grouped by
priority. This doc is the residue: findings that need a **policy/design decision**
or a larger change than an autonomous fix should make unattended.

Each item has a recommendation. Where I recommend a specific option, the PR does
**not** pre-empt it — these are genuinely your call.

---

## D1 (P2) — `enforce-layout.sh` task-scope gate fails **open** without `jq`

- **Where:** [`plugins/ravenclaude-core/hooks/enforce-layout.sh:50-53`](../../plugins/ravenclaude-core/hooks/enforce-layout.sh)
- **What:** When `jq` is absent, the hook prints a warning and `exit 0` — so both
  the repo-layout allow-list **and** the task-scope blast-radius bound (`.ravenclaude/task-scope.json`)
  become no-ops. It at least warns (unlike the `guard-destructive.sh` catastrophe
  floor, whose silent fail-open the PR fixes to fail **closed**).
- **The decision:** the *layout* policy is structure hygiene, so fail-open is
  arguably fine. The *task-scope* policy is a security-relevant write-blast-radius
  bound — should it fail **closed** (or `ask`) when `.ravenclaude/task-scope.json`
  is present but `jq` is missing?
- **Recommendation:** keep the layout half fail-open (with its existing warning),
  but fail **closed** for the task-scope half specifically when the task-scope
  file exists and `jq` is unavailable — matching the `guard-destructive` posture
  the PR just established. Left to you because it changes a guard's default
  behavior for consumers on jq-less hosts.

## D2 (P2, systemic) — the marketplace-claims self-heal has no failure detection

- **Where:** [`.github/workflows/regenerate-artifacts.yml`](../../.github/workflows/regenerate-artifacts.yml),
  [`.github/workflows/validate-marketplace.yml:~397`](../../.github/workflows/validate-marketplace.yml)
  (`check-marketplace-claims.py --structural-only` at PR time),
  [`scripts/check-marketplace-claims.py`](../../scripts/check-marketplace-claims.py)
- **What:** This is the **root cause** of the P1 corruption the PR fixed:
  `marketplace.json` shipped "46 skills" for 111 of 119 plugins on `main` (entered
  in PR #525, never healed). The PR corrects the data (`--fix` + regenerated
  `index.html`), but the **design gap remains**: the PR gate runs only
  `--structural-only` (blind to count drift by design), deferring the full check to
  a post-merge self-heal — and when that self-heal doesn't run/commit, *nothing*
  catches the drift. The 9.4 MB `index.html` can likewise sit stale on `main` with
  no gate signal.
- **The decision:** how should an un-healed drift become **observable**? Options:
  1. Add a **post-merge assertion** (or nightly cron) that runs the *full*
     `check-marketplace-claims.py` + `generate-index-dashboard.py --check` on
     `main` and notifies via [`scripts/notify.sh`](../../scripts/notify.sh) on
     failure. (Turns "self-heal silently didn't run" into a push notification.)
  2. Also investigate **why** the #525/#537 self-heal didn't heal (did the
     `regenerate-artifacts` run fire? did its `git push origin HEAD:main` succeed?
     did `[skip ci]`/concurrency swallow it?).
- **Recommendation:** do both — (1) is a small, high-leverage backstop; (2) is a
  one-time investigation. I did **not** add the cron/notify wiring because "where
  the alert goes" and "nightly vs post-merge" are your calls.

## D3 (P3) — `serve-dashboards.py` exists as two hand-maintained ~2 K-line copies

- **Where:** [`scripts/serve-dashboards.py`](../../scripts/serve-dashboards.py) (2223 lines)
  vs [`plugins/ravenclaude-core/scripts/serve-dashboards.py`](../../plugins/ravenclaude-core/scripts/serve-dashboards.py) (2071 lines);
  gate [`scripts/check-dashboard-server-parity.py`](../../scripts/check-dashboard-server-parity.py)
- **What:** Intentional dual-copy (root dev server vs. locked-down bundled consumer
  server). The parity gate only checks that the root's `/__` **endpoint token set**
  is a subset of the plugin copy's — it does **not** guard behavioral parity inside
  a shared handler, so a security-relevant change to e.g. `_local_request_ok` can
  diverge silently.
- **Recommendation (needs design):** either (a) factor the shared request/security
  core into one module both import, or (b) extend the parity gate to compare
  normalized bodies of the security-critical shared functions. Deferred because the
  dedup approach is an architecture decision.

## D4 (P1-adjacent, follow-up) — close the `check-md-links` copilot blind spot

- **Where:** [`scripts/check-md-links.py:55`](../../scripts/check-md-links.py)
  (`any(part == "copilot" ...)` exclusion)
- **What:** The PR **fixed** the 120 broken links in the shipped `copilot/agents/*.agent.md`
  tree (generator now repoints relative links for the deeper home; tree regenerated;
  120/120 resolve) — but left the blanket `copilot/` exclusion in the link gate,
  because lifting it also requires fixing one **root-relative** link in the
  projected `copilot/AGENTS.md` (`plugins/ravenclaude-core/CLAUDE.md`, which doesn't
  resolve from the copilot subdir). The generator is now correct **and**
  freshness-gated, so link correctness is enforced transitively — but the gate
  can't independently catch a future regression until the exclusion is lifted.
- **Recommendation:** in a follow-up, rewrite the projected grounding section's
  root-relative links in `build_agents_md()` (add the right `../` depth), then
  remove the `copilot/` exclusion so the tree is validated like everything else.

## D5 (P3) — `guard-destructive.sh` fail-closed has no regression gate

- **Where:** [`plugins/ravenclaude-core/hooks/guard-destructive.sh`](../../plugins/ravenclaude-core/hooks/guard-destructive.sh),
  [`scripts/audit-gates.sh`](../../scripts/audit-gates.sh)
- **What:** The PR fixed the P0 fail-open (verified this session: jq-absent +
  dangerous payload → deny/exit 2; benign → allow; empty payload → allow). But
  `audit-gates.sh` only covers this hook's **syntax + executability**, not its
  fail-closed behavior. Adding a numbered behavioral gate (with a must-fail half
  that strips the fail-closed branch and asserts the leak) is the repo's own
  discipline, but wiring a new numbered gate into `audit-gates.sh` is invasive.
- **Recommendation:** add `Gate NN` (e.g. a `test-guard-destructive-failclosed.sh`
  under `plugins/ravenclaude-core/hooks/tests/`) proving jq-absent + destructive →
  exit 2, with the must-fail half. Deferred to avoid destabilizing the meta-test in
  an unattended run.

## D6 (P3) — lower-value tech-debt (batch when convenient)

| # | Finding | Where | Suggested fix |
|---|---|---|---|
| a | `schemas/brand-kit.schema.json` validated by nothing in CI | [`validate-schemas.yml`](../../.github/workflows/validate-schemas.yml) | Add a fixture under `tests/fixtures/` validated against the schema, or document it as reference-only. |
| b | 6 dead `allowed_globs` entries (`.gitattributes`, `plugins/*/docs/**`, gitignored configs) | [`.repo-layout.json`](../../.repo-layout.json) | Prune the truly-dead ones, or add a "reserved / not-yet-populated" comment convention. |
| c | `validate-layout` skipped on `[skip ci]` self-heal commits | [`validate-layout.yml`](../../.github/workflows/validate-layout.yml) vs `regenerate-artifacts.yml` | Run a lightweight `check-layout.py --all` inside `regenerate-artifacts.yml` before its commit. |
| d | Large scripts with zero test/gate coverage (`eval-adaptive-classifier.py` 54 KB, `content-scan.py`, `reddit-scan.py`) | `scripts/` | At minimum a `python3 -c "import ast; ast.parse(...)"` smoke gate in `audit-gates.sh`; ideally a small fixture test. |

---

## What the PR already fixed (for cross-reference)

**P0:** `guard-destructive.sh` fail-open on missing `jq` → fail **closed** (E14 parity). ·
**P1:** `marketplace.json` mass-corruption (`--fix` + regenerated `index.html`); monthly
skill-gap audit hardcoded "7 plugins" → enumerate from `marketplace.json`;
`peter-evans/create-pull-request` mutable `@v6` → SHA-pinned `@c5a7806…` (v6.1.0) +
Dependabot; 120 broken links in the shipped Copilot agent tree. ·
**P2:** `</script>` XSS-breakout hardening in the 3 HTML generators (+ regenerated
`dashboard.html`/`index.html`, all render gates green); `content-scan.py` SSRF
private-IP/metadata guard; `regenerate-artifacts.yml` failed-revert `|| true` →
restore-and-clean; `check-marketplace-claims.py` skill over-count filter. ·
**P3:** `check-streams-classify.py` `%`-format crash; `generate-bi-report.py`
`KeyError` on malformed data; `process-scenario-submission.py` secret scan over all
fields; `check-derive-rubric.py` tautological assertion; `open-dashboard.sh`
over-broad `pkill`.
