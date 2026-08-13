# Repository review — 2026-08-07 (autonomous three-panel + implementation)

**Run shape:** Panel 1 (partitioned finder agents over the logic-bearing code) → Panel 2
(adversarial re-read of every finding against the current code on disk, rejecting anything
already fixed by #829/#830 or false) → implementation of the confirmed non-substrate,
non-design fixes on `claude/stoic-fermat-35pmcu`, with each hook/regex fix reproduced before
and after.

> **Panel-mechanics note.** The first attempt used a background dynamic Workflow. Its subagent
> tool-call layer failed this run — every finder's `Read`/`StructuredOutput` call errored with a
> spurious "required parameter is missing", so it returned `confirmed: []`. That was an
> **infrastructure fault, not a healthy-repo signal** (recovered by reading the run journal). The
> review was re-run via the `Agent` path, where tools worked correctly; all findings below come
> from that path and were each verified against the real code.

## Mechanical health (pre-review sweep) — all green

Every CI gate passed on the tree at `ab002ed` before the semantic review began, so all findings
below are logic/robustness/safety defects the structural gates cannot catch:

- JSON validity (marketplace / all 180 `plugin.json` / repo-layout): OK
- `prettier@3.9.4 --check .` (whole tree): exit 0 · `ruff check .`: passed
- `check-frontmatter` / `marketplace-claims` / `md-links` / `mcp-attribution` / `grep-ere-pcre` /
  `hook-stdin-fallback` / `model-ids` / `storage-contract` / `host-support`: all exit 0
- Version drift (180 marketplace entries vs `plugin.json`): none
- `audit-gates.sh`: **686 pass / 0 fail / 1 skipped**. The 1 skip (Gate 47, validate-schemas)
  was for a missing local `jsonschema` module; closed manually — all 180 `plugin.json` +
  `marketplace.json` validate against `schemas/*.schema.json`.

## Scope reviewed

Six partitions over the logic-bearing surfaces: repo-root shell utilities, the ravenclaude-core
safety hooks, the `check-*.py` CI gates, the ravenclaude-core runtime Python (tribunal, PII
scrubbing, comfort posture, work-streams), the Python generators, and the `.mjs` render/router
checks. Generated dashboards, vendored code, and per-plugin markdown were out of scope.

## Confirmed findings & disposition

**11 findings confirmed** across the six partitions (many candidate findings were rejected in the
verify pass as already-fixed or false). Of the confirmed:

- **5 fixed in this PR** (repo-root `scripts/` — not the tribunal's protected substrate)
- **4 require maintainer action** — they touch the ravenclaude-core hook/script substrate, which
  the Thing's `xc.tribunal-self-disable` guard (correctly) blocks an autonomous session from
  editing. Ready-to-apply patches: [`2026-08-07-repo-review-maintainer-actions.md`](2026-08-07-repo-review-maintainer-actions.md).
- **2 low-risk test-hygiene items** left for the maintainer's call (also in that doc).

### Fixed in this PR (grouped by priority)

**P1 — silent security-control disablement**

| # | File:line | Defect |
|---|---|---|
| 1 | `scripts/emit-codex-config.py:357` | An existing `[sandbox_workspace_write]` table with a different key (e.g. `writable_roots`) but no `network_access` caused a **second** `[sandbox_workspace_write]` header to be appended → duplicate table → **invalid TOML** → Codex rejects the whole file and falls back to defaults, so the `sandbox_mode`/`approval_policy` just "set" bound nothing (the exact silent-weakening the module prevents). No parse-verify step caught it. Now locates the existing table header and inserts under it; adds a best-effort parse-before-write guard (mirroring `install-codex-mcp.py`). Self-test fixture 4c added. |

**P2 — TOCTOU parity gap / latent security-gate hole**

| # | File:line | Defect |
|---|---|---|
| 2 | `scripts/cleanup-branches.sh:293` | Remote branch delete not SHA-guarded, unlike the local delete (`git update-ref -d <ref> $_tip`, fail-closed on ref drift). Remote path fetched the branch SHA then discarded it (`--silent`) and deleted unconditionally → a concurrent post-verdict push to the remote is hard-deleted while the identical local move is refused. Now fetches `.commit.sha`, refuses unless it equals the verdict-time tip. Restores parity; fails safe. |
| 3 | `scripts/check-prompt-builder-render.mjs:47` | The XSS-sink grep (the advertised "no HTML-string sink anywhere" floor) missed the append form: `\s*=(?!=)` cannot match past the `+` in `innerHTML += x`, so a future `preview.innerHTML += userText` would sail through. Broadened to `\s*\+?=(?!=)` (both `=` and `+=`; still excludes `==`/`===`); added a `+=` mutant to the must-fail half. Current code is clean — closes a latent hole. |

**P3 — latent hardening**

| # | File:line | Defect |
|---|---|---|
| 4 | `scripts/open-dashboard.sh:52` | `--port <val>` skipped the numeric validation the bare-positional form enforces, so `--port abc` flowed into `seq abc 5` and every port loop silently zero-iterated, ending in the misleading "dashboard server did not come up". Now validated in the `--port` branch (exit 2, clear message). |
| 5 | `scripts/open-dashboard.sh:176` | A possibly-empty `bind_args` array expanded as `"${bind_args[@]}"` raises unbound-variable under `set -u` on bash 3.2 (stock-macOS target). Now the set-u-safe `${bind_args[@]+"${bind_args[@]}"}` form. Latent today; explicit per the portability target. |

### Verification

Each shell/regex/TOML fix was reproduced before and after: `--port abc` → exit 2; set-u-safe array
idiom on empty+full; `emit-codex-config.py --self-test` → 0 failures incl. the new duplicate-table
fixture (header count == 1, key preserved, valid TOML); Gate 156 green; `check-prompt-builder-render.mjs`
green incl. the new `+=` teeth. `ruff` + `prettier --check` clean on all edited files.

## Partitions confirmed clean (no actionable defect)

- **`check-*.py` gate suite** — no fail-open gate, no crash-on-valid-input, no truthiness/glob/off-by-one
  slip; the #829/#830 hardening (`_is_blank`, recursive globs, etc.) verified genuinely present.
- **Shell utilities** — `archive-branch.sh`, `worktree-{new,swarm,clean}.sh`, `setup-worktree-hygiene.sh`,
  `dod-fast.sh`, `notify.sh`, `branch-hygiene.sh`: all sound (SHA-guarded deletes, fail-closed dirty
  checks, never-block invariants).
- **Runtime Python** — the tribunal engine (`thing-decide.py` / `thing-decision.py` / `thing-concerns.py`
  all fail safe to defer/deny), `apply-comfort-posture.py` (security_deny floor unconditional),
  `forge-route.py`, and the PII tokenizers (`pseudonymize*.py` — IBAN/surrogate/homoglyph fixes hold;
  under-matches are the documented "layer C is the floor" honest limits).
- **`sanitize-webfetch-body.py`** — greedy nested-decoy handling, unterminated-tag variants, TOCTOU size
  guard, traversal rejection all present.
- **Untrusted-issue intake** — `process-scenario-submission.py` (secret/PII gate on NFKC-normalized text,
  slug/enum clamping, no traversal), the generators' HTML/TOML escaping boundaries, and the SSRF posture
  in `content-scan.py` — all sound.
