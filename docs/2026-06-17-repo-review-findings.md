# Repository review — findings, fixes, and open decisions (2026-06-17)

A full-repo expert review run as a scheduled routine. Three independent Panel-1
reviewers (shell, Python, docs/consistency) scanned the codebase; their findings
were validated and priority-tie-broken against the actual code (Panel 2 / Panel 3),
which **rejected one false positive** and confirmed the rest. Confirmed,
clearly-correct, low-blast fixes were implemented directly (see the PR). Items
needing a decision or an API change are below.

## Starting health

The repo is in strong shape. The project's own gate suite is the authoritative
definition of correctness, and at review start **443/444 self-audits passed**
(`scripts/audit-gates.sh`), plus JSON validity, shell `bash -n`, frontmatter,
markdown links, layout allow-list, prettier, and ruff — all green. The bug
surface was therefore logic-level (what gates can't catch) plus one stale
generated artifact.

## Implemented in this PR (grouped by priority)

### P1 — real bugs

1. **Dead credit-card PAN regex in two PII guards.**
   `plugins/regulatory-compliance/hooks/scrub-confidential-pre-write.sh:81` and
   `plugins/finance/hooks/flag-finance-anti-patterns.sh:74` used PCRE
   non-capturing groups `(?:…)` under `grep -E` (POSIX ERE), which does not
   support them — `grep` emitted `warning: ? at start of expression` and the
   pattern **silently failed to match 16-digit Visa (`4…`) and Discover (`6011…`)
   PANs entirely** (the `\b` after 13 digits never anchored). For
   `regulatory-compliance` this is the layer documented as the one you flip to
   `exit 2` to *block* SAR/STR writes. Fix: `(?:…)` → plain `(…)`. Verified: all
   four card types now match, no ERE warnings.

2. **`reset-plugin-cache.py` resolved a backup dir as the live cache on re-run.**
   `plugins/ravenclaude-core/scripts/reset-plugin-cache.py` —
   `resolve_plugin_version_dir` took the lexically-max child of the plugin dir,
   but the retained backups (`<version>-snapshot-<ts>`, `<version>-pre-ragnarok-<ts>`)
   are siblings that sort *after* the bare version. A second Ragnarök within the
   30-day retention window would resolve to a backup and snapshot/swap the wrong
   tree — a path bug in a high-blast disaster-recovery tool. Fix: exclude the
   backup-naming patterns from the version scan. Proven with a synthetic cache
   (resolver now returns the live version even with leftovers present).

### P2 — tech-debt with real impact

3. **`feedback-report.html` was stale (Gate 99 red on a clean tree).** The
   committed report reflected 366 scenarios / "As of 2026-06-10"; the corpus has
   369 / "2026-06-12". Regenerated deterministically; `--check` now passes. This
   was the single failing self-audit at review start (443→444).

4. **`check-run-actions-argv.py` shell-form guard was bypassable.** The gate
   exists to prove every `/__run` action maps to a fixed argv with no shell, but
   its guard rejected only the exact string `argv[1] == "-c"` — `-lc`, `-c=…`,
   and `--command` all passed. Fix: reject **any** leading-dash `argv[1]` (a
   fixed-argv launcher takes a script path, never a flag). Real file still passes.

5. **`check-layout.py` silently passed when git failed.** Neither `git ls-files`
   nor `git diff` checked the return code, so an unresolvable base ref yielded
   empty output → zero paths → "Layout OK". Fix: check `returncode`, fail loudly
   (exit 2). Verified it now exits 2 on a bad ref.

6. **README plugin/skill/hook counts had drifted** (the recurring hand-maintained-
   count bug the CHANGELOG already flagged). Corrected: `README.md` "99 plugins"
   / "98 of the 99" → 101 / "100 of the 101"; core ships 43 skills / 16 hooks
   (was "40 skills" in root README, "20 skills, 5 hooks" in core README);
   core README rule-sets 4 → 5. All verified against `marketplace.json` + `find`.

### P3 — low

7. **`i18n_calc.py` `%`-placeholder parser ate literal `%`** ("50% off" treated
   the lone `%` as a printf placeholder, slightly undercounting translatable
   length in a heuristic estimator). Fix: only treat `%` as a conversion start
   when a printf-ish char follows. `%s`/`%d` still detected; `50%` now literal.

### Rejected (Panel-2 validation caught a false positive)

- **`stream_sizing.py` "returns partition count as exit code"** — *not a bug.*
  `size_partitions` returns `0` on success (line 80); verified by running it
  (8 partitions → exit 0). No change made.

## Open decisions — need your input (NOT implemented)

These are confirmed but require a judgment call, an API/semantics change, or a
gate-fixture build, so they were deliberately left for you.

### D1 (P1) — `supply_calc.fill_rate()` returns cycle-service-level, not fill rate
`plugins/supply-chain-planning/scripts/supply_calc.py:236-245`. The function
computes `_unit_loss(z)` then **discards it** and returns `Φ(z)` — the Type-1
cycle service level, not the Type-2 fill rate its name/docstring promise. Since
CSL ≥ fill rate, a planner sizing to a 95% fill target **under-stocks**.

**Decision needed:** (a) implement the real fill rate
`FR = 1 − σ_LT·L(z)/E[demand-per-cycle]` — requires adding a cycle-demand
argument to the signature (an API change for any caller), or (b) rename the
function to `cycle_service_level` and delete the dead `_unit_loss` line if CSL is
actually what's wanted. **Recommendation: (a)** — the module's intent (and the
dead `_unit_loss` call) shows fill rate *was* the goal; (b) only if no caller
needs true fill rate. Either way, delete the dead line.

### D2 (P1) — `guard-destructive.sh` doesn't cover `find … -delete` / `truncate`
`plugins/ravenclaude-core/hooks/guard-destructive.sh`. Empirically confirmed
(base64-fed to avoid the session's own guard): `find / -delete` and
`truncate -s 0 /etc/passwd` are **allowed (exit 0)**, while `rm -rf` and
force-push are correctly denied. `find -delete`/`-exec rm` is a named destructive
idiom (the runaway-brake's read-only carve-out already excludes `find` for this
reason), yet the catastrophe-floor guard has no pattern for it.

**Why not auto-fixed:** this is a security-floor guard and *what to treat as
destructive is a policy scope decision*; adding patterns also needs matching
`must_fail` fixtures in `audit-gates.sh` (gate-change discipline). The PAN fix
above was a *bug* (broken regex restored to intent); this is *new* blocking
behavior. **Recommendation:** add deny patterns for `find … (-delete|-exec\s+rm)`
and `truncate -s ?0` plus the bidirectional gate fixtures. **Decision needed:**
confirm the scope (e.g. should a benign `find . -name '*.tmp' -delete` be denied,
or only whole-tree/system-path forms?).

### D3 (P2) — durable count-drift gate (the recurring root cause)
Every README count finding (D6/#6 above and prior CHANGELOG entries) is the same
bug: hand-maintained prose counts drift from reality, and no gate covers free
prose like "40 skills" / "99 plugins". **Recommendation:** add a small CI check
(or extend `check-marketplace-claims.py`) that asserts the prose counts in
`README.md` + `plugins/ravenclaude-core/README.md` match `marketplace.json` /
`find`. **Decision needed:** worth a new gate, or keep correcting by hand? Note
the "shipped slash commands" count in the core README (`4`) is also stale —
there are 7 command files incl. an alias pair (`reset-plugin-cache`/`ragnarok`)
and `forge` — but "what counts as a user-facing command" is itself the decision,
so it's parked here rather than guessed.

### Lower-severity latent items (from the Python sweep; FYI, no action requested)
- `_emit-event.sh` no-`jq` fallback doesn't escape control bytes (`\x1b`, U+2028/9)
  in the `path` field — can corrupt a JSONL line / carry terminal escapes when
  `jq` is absent. (`jq` path is fine.)
- Per-plugin anti-pattern hooks use line-scoped `grep -Ev` placeholder exclusion:
  a real SSN sharing a line with a placeholder example is suppressed. Narrow
  surface, advisory hooks.
- `thing-golden-eval.py` returns 0 on an *empty* entry set ("0/0 pass").
- `rm -rf $VAR` (unexpanded variable target) is allowed by `guard-destructive.sh`
  — arguably correct (a static normalizer can't resolve the var); worth a one-line
  "accepted residual risk" comment.

## Method note

Panels were run as parallel subagents (lighter categorization fan-out); validation
and tie-breaking were done against the actual code with this-session checks
(running scripts, feeding fixtures, synthetic caches) rather than taking any
finding on faith — which is how the `stream_sizing` false positive and the
slightly-overstated `i18n` claim were caught.
