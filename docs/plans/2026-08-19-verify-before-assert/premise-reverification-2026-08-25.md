# Premise re-verification — verify-before-assert, re-measured 2026-08-25

The plan's `claims-table.md` was written against `main @ 2b91635f` (plugins v0.282.0).
Re-measured here against `main @ e8a15454` (PR #1020), ~20 PRs later, in worktree `forge/vba-impl`
(base `origin/main`, behind=0). Every row below was re-probed in-session.

| # | Claim as written | Verdict now | Evidence |
|---|---|---|---|
| C2 | 4 FORGE helpers present | **HOLDS** | per-file `-f` test; `resolve-plugin-root.sh` exits 0 |
| C3 | PostToolUse(Bash) wires log-probe.sh ONLY | **FALSE — superseded** | 10 PostToolUse entries; `Bash` matcher now wires `triage-outcome.sh` too. Expected: Phase 3 shipped (#991, #1006). |
| C4 | guard-probe-validity.sh = exactly ONE rule, WARN-only | **HOLDS** | header still reads "ONE rule. WARN only"; 1 rule marker. Phase 4's "do not append to it" reasoning stands. |
| C5 | claim-grounding-lint + guard-premise see only written file content | **HOLDS** | stated verbatim at claim-grounding-lint.sh:41,58 |
| C7 | NO hook triages a FAILED Bash command | **FALSE — superseded, by design** | `triage-outcome.sh` is wired and fired live twice this session. Phase 5's real dependency is "the ledger exists", which is now satisfied rather than pending. |
| C9 | all five hosts support hooks | **HOLDS** | `host-support.json` components.hooks: claude-code/copilot/codex/cursor/gemini `supported=true` |
| C10 | Copilot PLUGIN-level hooks never fire; ship repo-level | **HOLDS** | caveat present, cites github/copilot-cli#2540 |
| C11 | Copilot CHAT `supported=false` | **HOLDS** | surfaces.chat.supported=false + the "do not flip without a Phase 0 payload dump" note |
| C12 | Codex speaks the Claude hook contract natively | **HOLDS** | components.hooks.codex.how + the HASH-TRUST caveat |
| C13 | aider/windsurf ABSENT from components.hooks | **FALSE in letter, TRUE in substance** | both are now PRESENT with `supported=false`. No hook support either way; Phase 7's text-floor treatment is unchanged. |
| C15 | `_wg_bash_is_mutating` substring-matches the RAW command, so prose reads as a command | **HOLDS** | worktree-guard.sh:649-666 still `case " $cmd " in *" add "*` etc. Phase 4 R-4's anti-requirement and Phase 6 test 9 remain necessary. |
| C16 | `_wg_lease_autocheckin` refuses a CLEAN tree on main | **RESOLVED** | worktree-guard.sh:534-552 now short-circuits on a clean tree BEFORE the anchor refusal, with the ordering marked load-bearing. Phase 6's C16 dependency is moot. |
| C14 | no hook on any host carries the model's chat text | **STILL UNSETTLED** | `[unverified — premise not disconfirmed: needs five vendor hook references; above cheap floor]`. Phase 8 carries the marker; no phase may depend on reading chat text. |

## G7.2 — the re-probe the plan required, and its result

`host-support.json` still reads `updated: 2026-08-14` — unchanged since the plan was written. The
cursor/gemini cells therefore carry no newer evidence than the plan had, so R7's downgrade to
**UNWIRED — declared** stands unmodified. control: read the `updated` field and the per-host
`basis` strings directly rather than inferring currency from the file's mtime.

## The gap this pass found

`knowledge/cause-taxonomy.md` (component A6) did not exist, and `cause_taxonomy.py` already exported
`extract_ids_from_doc` plus a `--check-doc` CLI branch — a parity mechanism wired to a document that
was never authored. Phase 2 names that document as a pre-build gate that lands FIRST. It shipped
without it, so the parity gate could not have run. control: `--check-doc` against a 2-id stub
reports 32 ids "in the module only" and exits 1, so the checker discriminates rather than passing
vacuously.

## Two live false positives in shipped Phase 3

`triage-outcome.sh` fired twice this session on **successful** commands with **empty stderr**,
deriving `permission-denied`/`conn-refused`/`in-progress` and later `timeout` labels from words
present in the command's own **stdout**. Recorded here as measured FP evidence for Phase 9's J3 gate
and Phase 11's live re-measurement; not fixed in this increment.
