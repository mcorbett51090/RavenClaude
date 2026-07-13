# Repo review — decisions needed (2026-07-13)

Autonomous 3-panel repo review (expert finders → adversarial validation → tie-break),
run over the executable-code surface (~208 Python files, 180 shell scripts), with
emphasis on surface added since the last review (PR #604, 2026-07-09): the
terminal-status-indicators skill, the CI self-heal workflow, the `derive_rubric`
rewrite, and the 45-hook stdin-fallback change. The repo passed every mechanical CI
gate going in (JSON, `bash -n`, python compile, ruff, prettier, no version drift,
frontmatter), so the panels hunted for what the gates can't catch.

**18 findings survived adversarial validation: 2 P1, 5 P2, 11 P3; 0 rejected.**
**15 were mechanical and are implemented + verified in the accompanying PR** (each
fix exercised end-to-end, not just typechecked). This doc holds the **3 findings that
need a design decision from you** before they can land.

## What was implemented in the PR (no decision needed)

| Pri | Fix | File(s) |
|---|---|---|
| **P1** | **Security — `curl\|sh` guard bypass.** `guard-destructive.sh`'s two pipe-to-shell deny patterns anchored the interpreter name immediately after the pipe, so a **path-qualified** interpreter (`curl … \| /bin/bash`, `\| sudo /bin/sh`, `\| /usr/bin/python3`, `\| ./sh`) slipped the guard while the bare form was blocked. An optional path-prefix group closes it; verified all malicious forms block + benign path-bearing pipes still pass; gate corpus extended. | `plugins/ravenclaude-core/hooks/guard-destructive.sh`, `scripts/audit-gates.sh` |
| **P1** | **NetSuite M2M signer non-functional.** Passed the hash alg as a **string** (`RSAAlgorithm("sha256")` → `TypeError` on every mint, since PyJWT calls `self.hash_alg()`) **and** used PKCS1v15 padding for a `PS256`-declared JWT. Now selects `RSAPSSAlgorithm`/`RSAAlgorithm` correctly and passes a `hashes` class; **verified with a real `PyJWT[crypto]` round-trip** (the dep whose absence masked the bug in CI). | `plugins/finance/scripts/connectors/netsuite_signer.py` |
| P2 | **Security — banner frame-break.** `capability-orientation.py` inlined the run-config `task_class` + tier values into the always-injected SessionStart banner **without** the frame-break sanitization its sibling `rationale` already gets — a hostile/cloned repo's `run-config.json` could break out of the untrusted-data frame. Now sanitized; verified breakout neutralized. | `plugins/ravenclaude-core/scripts/capability-orientation.py` |
| P2 | **Security — intake secret gate gap.** `process-scenario-submission.py`'s secret/PII reject gate scanned only 4 fields and skipped the required `plugin` field (slug-validated only), so a credential shaped like `ghp_…`/`AKIA…` in `### Plugin` passed unscanned into a staged file. Now gated; verified a PAT is rejected. | `scripts/process-scenario-submission.py` |
| P2 | **Straight-line depreciation never reached salvage.** A rounds-down monthly slice stranded a residual NBV that persisted forever while the rollforward still tied (so `--strict` never caught it). Now drains to exactly salvage on the final month and stays there. | `plugins/finance/scripts/schedule_engine.py` |
| P3 | Prepaid/deferred-revenue phantom residual balance in periods after full amortization/recognition. | `plugins/finance/scripts/schedule_engine.py` |
| P3 | `terminal-watcher.py` — recycled PID inherited a stale controlling PTY (start-time identity check added); `running_pid()` crashed on a foreign-owned pidfile (EPERM now treated as "alive", unlink fail-safe). | `plugins/ravenclaude-core/skills/terminal-status-indicators/terminal-watcher.py` |
| P3 | `derive_rubric.py` silently dropped a whole dimension (and its hard gate) on a markdown-bold weight cell `**40**`; now tolerated (mirrors the `**yes**` the hard_gate column accepts) + warns on a genuinely non-numeric weight. | `plugins/ravenclaude-core/skills/refine-to-rubric/scripts/derive_rubric.py` |
| P3 | Gate blind spots: `check-hook-stdin-fallback.py` matched only `="${1:-}"` (missed `="$1"`/`="${1}"`/`=$1`); `check-grep-ere-pcre.py` `_PCRE_CONSTRUCT` missed the `(?P<`, `(?>`, `(?#`, `(?i)` members of the `(?…)` family. Both broadened (latent — no current file exploits them). | `scripts/check-hook-stdin-fallback.py`, `scripts/check-grep-ere-pcre.py` |
| P3 | `generate-bi-report.py` — a string-valued `data_quality_flags` element crashed that plugin's report (AttributeError); `cohort.size` was interpolated into HTML unescaped (inconsistent with the escaped sibling `cohort.label`). Both fixed. | `scripts/generate-bi-report.py` |
| P3 | EVM `TCPI` printed a nonsensical negative "efficiency needed to hit BAC" when AC ≥ BAC — the exact over-budget distress case the tool forecasts. Now routes to the undefined branch with a "budget unrecoverable — re-baseline to EAC" message. | `plugins/project-management/scripts/evm_calc.py` |

Version bumps: `ravenclaude-core` 0.189.0→0.189.1, `finance` 0.18.2→0.18.3,
`power-platform` 0.44.6→0.44.7, `project-management` 0.4.0→0.4.1 (both `plugin.json`
and `marketplace.json`), plus a CHANGELOG entry for the three plugins that carry one.

---

## Decision 1 (the recurring one) — PreToolUse `check-*-anti-patterns.sh` hooks scan disk, so they miss new-file content

**Finding (P2, `needs_design`, verified this session).** The **46** `plugins/*/hooks/check-*-anti-patterns.sh`
advisory hooks are wired **PreToolUse** on `Edit|Write|MultiEdit`, and after resolving
the file path they scan the file **from disk** ([`check-analytics-engineering-anti-patterns.sh:19`](../../plugins/analytics-engineering/hooks/check-analytics-engineering-anti-patterns.sh)
and cohort). But at PreToolUse the write **hasn't happened yet**:

- A **Write** creating a brand-new deliverable → the file doesn't exist on disk, so the
  `[ ! -f "$file" ] && exit 0` guard fires and the content being written is never scanned.
- An **Edit** → the hook greps the **stale pre-edit** content, missing the anti-pattern
  being introduced.

None of these hooks reads `.tool_input.content` / `.new_string` (grep confirms zero
references). So the flagship "write a brand-new model and get it flagged" path is a
**silent no-op** — the same inert-hook class the #605 stdin-path fix targeted (that fix
made the *path* resolve; the *content* is still never seen for a new file). The
PostToolUse `flag-*` cohort is unaffected (the file exists with new content when they run).

**Why this wasn't auto-applied:** the fix is a semantics choice across 46 hooks, and
either option has a real trade-off:

- **(a) Scan the proposed content** — read `.tool_input.content` (Write) / `.new_string`
  (Edit) / concatenated MultiEdit edits from the stdin payload already captured, and grep
  **that** instead of the on-disk file. Keeps PreToolUse (so `*_STRICT=1` can still *block*
  a bad write before it lands), but adds Edit/MultiEdit content-reconstruction logic to
  every hook.
- **(b) Convert the cohort to PostToolUse** — the on-disk file then contains the new
  content, matching the `flag-*` cohort. Simpler, but a PostToolUse exit 2 **cannot block**
  the write, so it **silently forfeits the advertised `*_STRICT=1` blocking mode**.

Both touch all 46 hooks and bump ~46 plugin versions (a consumer-facing release event,
parallel to Decision 1 of the 2026-07-08/09 reviews). **Recommendation: (a)** — it keeps
the STRICT blocking contract real, and the content-reconstruction block is identical per
hook (author once, roll across the cohort). Your call on (a) vs (b), and whether to ship it
as its own dedicated 46-plugin PR.

---

## Decision 2 — `dataverse-payload-preflight` false "missing required" on a disambiguated lookup nav property

**Finding (P2, `needs_design`, verified by code trace).** In [`preflight.py:98`](../../plugins/power-platform/skills/dataverse-payload-preflight/preflight.py),
a well-formed `@odata.bind` only marks a lookup as present when the **navigation property
name equals the attribute logical name** (`if low in by_lower`). For a **polymorphic /
customer** required lookup, Dataverse **requires** a target-qualified nav property (e.g.
`contoso_CustomerId_account@odata.bind` for the logical `contoso_customerid`), so
`present_logicals` is never updated and check #5 emits a spurious **missing-required ERROR
+ exit 3** — blocking the "clean" verdict even though the required lookup **was** correctly
supplied. This is a **false positive in exactly the SPN-create / required-lookup scenario
the tool exists to de-risk** (over-strict, never under-strict — it never passes a bad
payload and never touches data).

**The decision (how much metadata to carry):**

- **(a) Carry a nav-property → logical map** — `fetch_metadata` already queries
  `LookupAttributeMetadata`; also select the navigation-property/schema name and index binds
  by **both** nav and logical. Most correct; slightly more metadata per run.
- **(b) Target-set reconciliation** — when a bind's target entity-set matches one of a
  required lookup's declared targets, mark that lookup present. Lighter; needs the target
  list in metadata.
- **(c) Minimal** — don't emit a hard missing-required error for a lookup attribute when
  **any** `@odata.bind` in the payload resolves to one of that attribute's declared targets.

**Recommendation: (a)** — the metadata fetch already exists, so it's the smallest honest
fix that makes the check correct rather than merely-less-wrong. Your call on how much
nav-property metadata to carry.

---

## Decision 3 — terminal-watcher idle signal counts writes to *all* fds, not just the PTY

**Finding (P3, `needs_design`, real signal limitation).** [`terminal-watcher.py:68`](../../plugins/ravenclaude-core/skills/terminal-status-indicators/terminal-watcher.py)
reads `/proc/<pid>/io` `wchar:`, which is **process-wide** bytes-written accounting — not
just the controlling terminal. The module's premise ("a positive `wchar` delta means
actively writing a response") is therefore inaccurate: any watched process that writes ≥1
byte to **any** fd (a log file, telemetry socket, cache) more often than `IDLE_THRESHOLD`
(3s) while otherwise idle keeps `last_write_time` fresh, so the idle bell **never rings**.
The named targets (`claude`/`copilot`) usually block on stdin when idle and write nothing,
so the common case still rings — the degradation hits only processes with steady sub-3s
background writes. It's a **best-effort convenience tool** with no runtime assertion, so
nothing catches it.

**The decision (there's no clean mechanical fix):**

- **(a) Document + tune** — note the limitation in the skill's `SKILL.md` and expose
  `IDLE_THRESHOLD` tuning guidance. Cheap, honest, no behavior change. **(Recommended
  minimum — I can do this immediately on your say-so; it's the only part that's mechanical.)**
- **(b) Narrow the signal to PTY output** — a different mechanism (e.g. pts master/slave
  write accounting, or diffing only when the process's terminal is the write target). More
  correct, materially more complex, and platform-specific.

**Recommendation: (a) now, (b) only if a real agent with steady background writes turns up.**
Confirm and I'll land the SKILL.md note as a follow-up (it doesn't need a design decision
beyond your go-ahead — it's separated here only because the *code* narrowing is the design call).

---

## Notes

- The CI self-heal workflow (`regenerate-artifacts.yml`, #610/#611) and the `derive_rubric`
  rewrite were reviewed and found sound apart from the P3 bold-weight edge above.
- All 45 advisory `flag-*-antipatterns.sh` hooks from #605 were re-verified to carry the
  stdin `.tool_input.file_path` fallback (45/45), and the case-fixed gate correctly catches
  the uppercase idiom — that fix is solid.
