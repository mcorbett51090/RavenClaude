# RavenClaude whole-repo review — findings & design-input

**Date:** 2026-10-03 · **Branch:** `claude/awesome-wright-j35r63` · **Scope:** executable + CI surface (scripts, plugin hooks/scripts, CI workflows, manifests)

This is the design-input companion to the autonomous repo-review PR. It carries every finding the review could **not** safely auto-fix — because the file is tribunal-protected substrate, the change alters security-guard matching logic, or applying it would surface a coupled bug and turn CI red. Each needs your decision. The 13 findings that *were* auto-fixed (repo-review engine tooling) are in the PR itself and listed at the end for completeness.

## How this was produced (3-panel consensus)

- **Panel 1 (detection, Sonnet ×7):** seven expert reviewers swept coherent slices of the executable+CI surface across 8 dimensions (correctness, security, concurrency, resource-leaks, error-handling, performance, ci-cd-actions-security, dead-code-simplification). **207 findings**, each with a verbatim evidence quote and a concrete failure scenario; most reproduced by running the code.
- **Merge (deterministic):** the repo's own `findings_merge.py` deduped and derived P0–P3 from severity (`blocking→P0`, `major→P1`, `minor→P2`, `nit→P3`).
- **Panel 2 (validation, Opus):** adversarially re-verified every P0 (mostly via live probes) and the repo-review-engine candidates, adding impact/effort and a route. **All 18 P0s CONFIRMED, 0 refuted.**
- **Panel 3 (tie-break):** Panels 1 and 2 converged on every severity — no severity disputes to arbitrate. The only adjudication was the engine implement-vs-defer split, resolved conservatively (clean + self-test-safe + cannot-redden-CI → implement; behavior-changing / coupled → defer here).

### Model assignment (per the task's cost guidance)
Lighter (Sonnet) for the high-volume detection/categorization pass; heavier (Opus) for validation, tie-break, and the implementation decisions.

## Finding inventory & routing

| route | P0 | P1 | P2 | P3 | total |
|---|---|---|---|---|---|
| design-doc(substrate) | 17 | 47 | 56 | 10 | 130 |
| editable(ci-config) | 0 | 3 | 9 | 2 | 14 |
| editable(other) | 0 | 0 | 1 | 0 | 1 |
| editable(root-script) | 0 | 11 | 16 | 10 | 37 |
| editable(skill-tooling) | 1 | 12 | 9 | 3 | 25 |
| **TOTAL** | 18 | 73 | 91 | 25 | 207 |

`design-doc(substrate)` = under `plugins/ravenclaude-core/{hooks,scripts}/`, `concerns-catalog.md`, or `scripts/generate-dashboards.py` — writes are blocked by the Thing's self-tamper floor, and they are security-guard logic that needs your review regardless. `editable(*)` = the review could edit it, but it still needs a design decision (see §4) or was deferred as behavior-changing.

## 1. P0 — confirmed blocking findings (18) — all need your decision

Every one reproduced from the code as written. None was auto-fixed: 17 are tribunal substrate / security-guard logic; the 18th (`estimate_cost.py` cap guard) needs a workflow-behavior change. Grouped by subsystem; effort is S/M/L.

### Command-review tribunal (the Thing)

- **`plugins/ravenclaude-core/scripts/thing-concerns.py:409`** — Self-disable read-only carve-out strips double-quoted spans, so cmd-substitution inside double quotes escapes the guard
  - **Why (confirmed):** Probe: _self_disable_read_only of `cat "$(<mutate> <substrate>)"` -> True (bypass). _RO_QUOTED strips the double-quoted span incl. its command-substitution before _RO_META runs, but the shell executes command substitution inside double quotes. (Backtick form IS caught by _RO_META -> minor over-claim in the finding.)
  - **Impact:** A prompt-injected agent wraps a tribunal-tampering command in cat of a double-quoted command-substitution and the category-independent self-disable floor is skipped. · **Effort:** S
- **`plugins/ravenclaude-core/scripts/thing-concerns.py:395`** — Read-only allowlist contains programs/flags that execute arbitrary commands; re.IGNORECASE makes -C match -c
  - **Why (confirmed):** Probe: read_only=True for `rg --pre '<cmd>' foo .`, `ugrep --filter=...`, `git -c core.fsmonitor=evilcmd status`, `git -c core.pager=evilcmd log`. The `git (?:-C \S+ )?` alt is compiled re.IGNORECASE so `-c <config>` satisfies the `-C <dir>` form; rg --pre / ugrep --filter run programs per file.
  - **Impact:** A tribunal-tampering command disguised with rg --pre / ugrep --filter / git -c core.* passes the unconditional self-disable guard. · **Effort:** S
- **`plugins/ravenclaude-core/scripts/thing-concerns.py:335`** — revalidate() EDIT-safety invariant skips category migration and does not re-run screen_always
  - **Why (confirmed):** revalidate (lines 335-336) evaluates original AND revised under the ORIGINAL category only and never calls screen_always; orchestrator cited-EDIT path (thing-orchestrator.sh:790) calls only revalidate before emit_edit. A seat EDIT rewriting a shell_local_mutate command into a curl-to-shell (hard-rule in another category) passes ok:true and is applied with permissionDecision allow. harden path enforces category equality+screen_always; the cited path does neither.
  - **Impact:** A steered seat EDIT bypasses the pre-LLM hard rules (force-push/curl-to-shell) via an EDIT verdict. · **Effort:** M
- **`plugins/ravenclaude-core/scripts/thing-concerns.py:173`** — ReDoS: catalog triggers quadratic on repeated tokens; SCREEN_MAX_BYTES (1MiB) far above screenable size
  - **Why (confirmed):** Timed screen_always on 'git push ' repeated: 18KB 0.91s, 36KB 3.77s, 72KB 14.70s, 144KB 59.21s (~4x/doubling). _matches runs re.search over up to 4 variants per trigger with no per-regex budget; exceeds the 90s timeout near ~180KB, well under the 1MiB cap.
  - **Impact:** An attacker prepends padding to dangerous content; the screen never finishes and the hook times out fail-open. · **Effort:** M
- **`plugins/ravenclaude-core/scripts/thing-decision.py:1421`** — Malformed comfort-posture.yaml silently turns tribunal OFF (fail-open); orchestrator never reads posture_error
  - **Why (confirmed):** On YAML parse exception thing_enabled stays its default False (lines 1307/1311) while posture_error is set; orchestrator line 172 reads thing_enabled//false and line 283 `[ "$enabled" != "true" ] && exit 0`; grep shows NO posture_error consumer. A one-char typo/appended garbage disables all category review incl. the always_screen hard floor.
  - **Impact:** Whole tribunal (incl. unarguable force-push/curl-to-shell/self-disable floors) silently off on a malformed posture; worst on Copilot where the tribunal IS the portable floor. · **Effort:** S
- **`plugins/ravenclaude-core/scripts/thing-decision.py:216`** — classify() routes a whole compound command by its FIRST segment only
  - **Why (confirmed):** Line 216 `re.split(...maxsplit=1)[0]` -> only the leading segment is classified+reviewed. A leading read exempts chained commands from category-specific concerns (package-install/chmod/network_write). Blast limited for the 2 always_screen hard rules (force-push, curl-to-shell) which still screen on raw text, but category concerns do not.
  - **Impact:** Prefixing a harmful action with `ls;`/`cat x;` defeats shell_package_install / shell_local_mutate / network_write review for the chained command. · **Effort:** M
- **`plugins/ravenclaude-core/scripts/thing-decision.py:667`** — _posture_content_disables only denies explicit falsy thing:; DELETING the key is not detected
  - **Why (confirmed):** Lines 658-672: loops categories, `if v is not None` skips a category whose `thing` key is absent; `categories: {}` -> loop never runs -> returns False (not disabled). thing_enabled_for treats an absent key as OFF, so deleting `thing: on` disables review but is not flagged, while `thing: off` is. Asymmetric guard.
  - **Impact:** A write/edit of comfort-posture.yaml that deletes thing: on lines (or empties categories) disables review without tripping the self-disable guard. · **Effort:** S
- **`plugins/ravenclaude-core/scripts/thing-decision.py:216`** — ReDoS: leading-segment split quadratic in a run of whitespace
  - **Why (confirmed):** Timed classify('ls'+N spaces+'x'): N=5k 0.19s, 10k 0.76s, 20k 3.19s, 40k 12.27s (~4x/doubling, quadratic). Extrapolates past the 90s hook timeout near ~120-130KB (one argv element); platform treats hook timeout as fail-OPEN.
  - **Impact:** An agent pads a destructive command with whitespace so the tribunal times out and fails open. · **Effort:** S

### Egress / orchestration / posture

- **`plugins/ravenclaude-core/scripts/claude-orchestrate.sh:156`** — Egress secret scan false-negatives on large multi-line briefs (pipefail + grep -q SIGPIPE)
  - **Why (confirmed):** Reproduced 5/5: under `set -euo pipefail`, a 300KB brief with AKIA on line 1 -> `printf\|grep -Eiq` returns 141 (printf SIGPIPE) so the `if` is FALSE and exit-8 never fires; small brief detects 3/3. pipefail alone (grok's `set -uo pipefail`) also misses.
  - **Impact:** Secrets (AWS/GitHub/etc.) in any >~64KB brief/log pasted to the orchestrator egress to the model API un-refused; all 18 patterns affected. · **Effort:** S
- **`plugins/ravenclaude-core/scripts/copilot-delegate.sh:160`** — Pre-egress secret backstop fails OPEN when hooks/_scrub.sh not found (copilot lane)
  - **Why (confirmed):** Byte-identical block to grok-delegate.sh (line 156 sources _scrub.sh fail-silent, 160 `if command -v _scrub_reason`, no inline fallback). Same fail-open as EGR-002.
  - **Impact:** Secret-bearing task egresses to Copilot CLI unscanned when the scrub helper isn't co-located. · **Effort:** S
- **`plugins/ravenclaude-core/scripts/grok-delegate.sh:166`** — Pre-egress secret backstop fails OPEN when hooks/_scrub.sh not found next to script
  - **Why (confirmed):** Scan wrapped in `if command -v _scrub_reason` with NO inline fallback (line 154 sources _scrub.sh fail-silent); unlike claude-orchestrate.sh which carries an inline _secret_patterns fallback (lines 127-152). Symlink/copied/partial-install -> _scrub_reason undefined -> whole refusal block skipped.
  - **Impact:** A task with an AWS key / GH token egresses to a second vendor (Grok) with no refusal when the helper isn't co-located. · **Effort:** S

### Guardrail hooks

- **`plugins/ravenclaude-core/hooks/guard-destructive.sh:217`** — A literal <<TAG inside a quoted string is parsed as a heredoc, blanking a real destructive command
  - **Why (confirmed):** End-to-end against the real hook: control `rm -rf <tgt>` -> DENY(2); `echo '<<EOF' newline <rm> newline EOF` -> ALLOW(0); double-quoted opener form -> ALLOW(0). The heredoc regex matches the fake opener, the body (the live rm) has no cmd-subst and an empty quote group so _strip_heredoc blanks it to <<HEREDOC before any deny pattern sees it.
  - **Impact:** The primary destructive guard is bypassed; a live rm -rf after a fake quoted heredoc opener runs unblocked. · **Effort:** S
- **`plugins/ravenclaude-core/hooks/guard-destructive.sh:142`** — -m quoted-arg stripping pairs a quote closing an earlier string with one opening a later string
  - **Why (confirmed):** End-to-end against the real hook: `echo "-m " ; <rm> ; echo " -m"` -> ALLOW(0); single-quote twin -> ALLOW(0); control -> DENY(2). The `(-m\s+)"([^"\n]*)"` regex matches the -m inside the first string + its closing quote, spanning the middle command into the 'body' which is rewritten to -m MSG.
  - **Impact:** The primary destructive guard is bypassed; a live rm -rf between quote-paired echo -m args runs unblocked. · **Effort:** S
- **`plugins/ravenclaude-core/hooks/thing-orchestrator.sh:137`** — Posture file looked up under payload cwd; any cwd below project root disables the ENTIRE tribunal
  - **Why (confirmed):** Probe via real hook (force-push payload): cwd=<root> -> permissionDecision=deny; cwd=<root>/plugins and <root>/plugins/ravenclaude-core -> exit 0, no output (allow). Line 137 keys posture_file on ${cwd} (payload .cwd, line 130); line 143-145 short-circuits exit 0 when it's absent, BEFORE any screen_always, so even the hard-deny/self-disable floors are bypassed. Sibling hooks key on CLAUDE_PROJECT_DIR. Residual: that CC sends a subdir cwd after cd is the finding's own flagged inference, but the hook-side bypass is deterministic.
  - **Impact:** After the agent cd's into any subdir, every subsequent command (incl. force-push) is unreviewed/unblocked. · **Effort:** S

### Premise / claim gates

- **`plugins/ravenclaude-core/scripts/premise-gate.py:163`** — Premise gate settles a claim by SUBSTRING match: 'unsettled'/'not falsified' contain a settled token
  - **Why (confirmed):** Probe: _SETTLED=('settled','falsified','partially-settled','owner-gated'); `any(s in settle)` -> settle='unsettled'->True, 'not settled yet'->True, 'not falsified'->True; 'G3b'->False. Natural negation words in the settling column mark an unsettled inference settled.
  - **Impact:** An unsettled inference is reported CLEAN, inverting the gate's single purpose (advisory gate, lower blast radius than the tribunal/egress P0s). · **Effort:** S
- **`plugins/ravenclaude-core/scripts/premise-gate.py:162`** — Claim 'kind' defaults to permissive 'observation' when kind column is missing/unrecognised/pipe-shifted
  - **Why (confirmed):** Line 137 i_kind=col('kind'); line 149-150 derive kind only from substrings inference/observation else ''; line 162 `kind or 'observation'`. A 'type'-headed column -> i_kind None -> all rows observation; 'assumption' -> observation; a literal pipe shifts cells. The zero-ROWS guard (line 172) was added but the wrong-COLUMN case is not guarded.
  - **Impact:** An unreadable kind column reports inferences:0 CLEAN, so conjunct 1 (block building on an unsettled inference) silently never fires. · **Effort:** S
- **`plugins/ravenclaude-core/scripts/premise-gate.py:277`** — A plan whose phase headings the parser doesn't recognise yields phases:0 and exit 0 (CLEAN)
  - **Why (confirmed):** _PHASE_RE (line 60) requires a NUMBER in the heading (P?-?digits), so '## Phase A' doesn't match -> phases=[]. Line 277 `if require_edges and phases and not any(...)` is skipped when phases is empty -> returns (0,result). The symmetric zero-CLAIMS hole was fixed (line 172); this zero-PHASES hole was left.
  - **Impact:** A plan whose headings aren't numbered creates a module citing an unsettled inference and the gate reports CLEAN (advisory gate). · **Effort:** S

### repo-review engine

- **`plugins/ravenclaude-core/skills/repo-review/scripts/estimate_cost.py:57`** — Cap guard is advisory-only: workflow tier defaults exceed the 1000-call cap by construction at max/ultra
  - **Why (confirmed):** repo-sweep.workflow.js EFFORT_TIERS budgetBatches 20/40/80/160 (lines 129-158) are passed straight to repo_map.py --budget-batches (line 658); the estimate_cost.py call (lines 675-685) is 'best-effort...never blocks the sweep'. The v0.321.1 cache-doubling+hard-cap fixes make the ESTIMATE accurate but nothing on the run path CONSUMES it. At max (80 batches x 15 rapb x2 cold = 2400) the real sweep exceeds the 1000 cap by construction.
  - **Impact:** `/repo-review max/ultra` on a large repo (this one plans ~359) hits WorkflowAgentCapError mid-Review (the 2026-09-09 98.7M-token/zero-findings incident). Block mode (v0.323.8) is a manual/opt-in mitigation, not an auto-gate. · **Effort:** L

## 2. P1 — major findings (73)

Grouped by subsystem. Full evidence quotes are in each finding's shard; the failure scenario is summarized here.

### CI gate scripts (6)

| location | finding | failure scenario |
|---|---|---|
| `scripts/check-dashboard-server-parity.py:107` | Endpoint parity is a text-token comparison, and every dispatched endpoint of the plugin server is also named in comments/docstrings, so removing any route cannot be detected | endpoints() collects '/__name' tokens 'anywhere in the file' (the docstring concedes comment mentions count). Measured on the real plugin server: 18 of 18 self.path-dispatched endpoints are also named elsewhere (docstrin |
| `scripts/check-dashboard-server-parity.py:185` | The MH-33 'GET handler must call _local_request_ok()' check parses only one dispatch idiom and never asserts it found every handler: /__reserve is already unchecked | unguarded_get_handlers() matches `self.path.startswith\|== "/__x":\n self._handle_y(`. In both server copies do_GET has 15 '/__' literals but the regex yields 14 entries; /__reserve (dispatched as `self.path.split("?", 1 |
| `scripts/check-hard-rule-floor.py:216` | Gate 209 'locks' the hard-rule floor but never asserts guard-destructive.sh is registered/wired; it drives the script directly and scans hooks.json only for a Write-only attachment | scan_hooks_json iterates _file_only_matchers and flags the hook only when attached to a Write/Edit/MultiEdit-only matcher. Reproduced: a copy of hooks.json with every guard-destructive registration deleted -> scan_hooks_ |
| `scripts/check-model-ids.py:168` | Gate 134 passes on zero governed files and its self-test exercises scan_text(), which main() never calls - an over-broad carve-out turns the gate into a no-op | main() re-implements the scan loop inline; scan_text() is referenced only by self_test(). The real pipeline (git ls-files -> GOVERNED_EXT -> is_carved -> per-line MODEL_RE) has no must-fail fixture and no 'scanned N file |
| `scripts/check-model-tier-ratchet.py:377` | The ratchet's reference is a file edited in the same PR, and the 'loosen only with a recorded reason' rule exists only inside --stamp; a hand edit of the baseline passes every gate | --check compares the working tree to tests/fixtures/model-tier-ratchet.json read from the same working tree, and the loosening refusal (`if rc != 0 and not allow_loosen`) lives only in stamp(). check-ratchet-freshness.py |
| `scripts/check-verdict-default-nonpermissive.py:42` | Gate 199's static half scans only `case "$verdict\|decision\|final_verdict\|panel_verdict\|v"`; it does not see the v0.205.1 tie-breaker shape it cites, and in practice covers 2 case statements in one file | The docstring's shape 1 is 'every branch failed safe except the final else' (an if/elif chain on $tv in thing-orchestrator.sh). VERDICT_CASE only matches case statements with those five variable names; of 137 `case` stat |

### CI workflows (3)

| location | finding | failure scenario |
|---|---|---|
| `.github/workflows/github-protocol-secret-scan.yml:35` | Required check 'Scan for committed secrets (TruffleHog)' reports success on workflow_dispatch without scanning anything | OBSERVATION: the live main ruleset lists 'Scan for committed secrets (TruffleHog)' (this job's name) as a required status check. On `workflow_dispatch` the TruffleHog step is skipped (`if: github.event_name == 'pull_requ |
| `.github/workflows/quarantine-intake.yml:123` | Intake pipeline depends on labels that do not exist in the repo; the trigger label is never applied and the reject / over-cap / stage paths would hard-fail before closing the issue | OBSERVATION (live API, this session): the repo's 16 labels do not include `scenario-submission`, `not-staged`, `queue-full`, `staged`, `quarantine` or `needs-maintainer-review`. The issue form (.github/ISSUE_TEMPLATE/sce |
| `.github/workflows/regenerate-artifacts.yml:399` | SELF_HEAL_PAT (a PR-merge-capable PAT) is a plain repo secret reachable from any branch's workflow; the job has no environment gate or main-ref guard | OBSERVATION: the job passes `secrets.SELF_HEAL_PAT` to create-pull-request and to `gh pr merge`; the file has no `environment:` key and no `if: github.ref == 'refs/heads/main'`, and it declares `workflow_dispatch` (line  |

### Command-review tribunal (the Thing) (12)

| location | finding | failure scenario |
|---|---|---|
| `plugins/ravenclaude-core/scripts/thing-concerns.py:170` | _matches() recomputes _match_variants(command) for EVERY concern; evaluate() therefore does ~17-60x the normalisation work of screen_always() on the same command | variants (wrapper normalisation + two flatten passes) depend only on the command but are rebuilt inside the per-concern loop (and again for each decoded base64 text). Measured on a 10KB space run: one _match_variants 0.5 |
| `plugins/ravenclaude-core/scripts/thing-concerns.py:176` | _matches() drops a trigger whose regex fails to compile ('except re.error: continue'), silently disabling pre_llm_deny rules that are not always_screen | screen_always() was hardened to treat an uncompilable always_screen regex as a MATCH (fail closed), but _matches - used by evaluate() for every other concern - skips it. xc.secret-in-command and xc.injection-attempt are  |
| `plugins/ravenclaude-core/scripts/thing-decide.py:83` | The deterministic high-blast floor misses the common CLI spelling of a protected-branch force push and other destructive git forms, so those decisions can auto-resolve | The docstring says the invariant 'high-blast decisions never auto-resolve' must not rest on the LLM or the caller's flag, but the vocabulary only matches the hyphenated force-push words, force-with-lease, reset --hard, r |
| `plugins/ravenclaude-core/scripts/thing-decide.py:267` | Decision seats wrap the untrusted question/context in a FIXED delimiter (no per-call nonce, no defanging), so the text can close the envelope and issue instructions | thing-seat.sh documents and fixes exactly this ('A FIXED literal delimiter lets a command containing it escape' -> per-call nonce + defang), but _run_seat still emits <untrusted decision> ... </untrusted decision> with r |
| `plugins/ravenclaude-core/scripts/thing-decision.py:89` | _route() swallows every exception and returns a no-concerns fallback with no error flag, silently disabling all concern-based routing (its 'convenes the full panel' promise is never honoured) | evaluate() and screen_always() walk the same catalog, but screen_always skips non-always_screen entries while evaluate dereferences every concern. Reproduced on a copy of the catalog with ONE concern given 'triggers: oop |
| `plugins/ravenclaude-core/scripts/thing-decision.py:188` | Wrapper normalisation is incomplete: wrappers that take an argument or are not listed make the command classify to None, so the tribunal never reviews it | '-\S+' in the wrapper regex strips flags but not their values, and timeout/time/exec/xargs/ionice/setsid/subshell/brace-group/negation are not handled. Reproduced (classify -> None): 'nice -n 10 <cmd>', 'sudo -u bob <cmd |
| `plugins/ravenclaude-core/scripts/thing-decision.py:239` | Force-delete override only recognises uppercase -D (and --delete with --force); '-df', '-fd', '-d -f', '-d --force' classify as read-only and dodge slm.delete-protected-branch-locally | Git treats 'git branch -d' combined with -f/--force exactly like -D. Reproduced: classify() returns shell_local_mutate with concern slm.delete-protected-branch-locally for 'git branch -D main' and for '--delete --force m |
| `plugins/ravenclaude-core/scripts/thing-decision.py:728` | Posture-file self-disable check is a case-sensitive suffix test on the raw path (no realpath/inode/normcase), so case variants and links bypass it | _posture_write_disables returns False unless file_path.endswith('comfort-posture.yaml'). On a case-insensitive filesystem (the maintainers run macOS) '.ravenclaude/Comfort-Posture.yaml' is the same file; a symlink or har |
| `plugins/ravenclaude-core/scripts/thing-denial-kb.py:140` | Secret scrub misses common credential shapes (the module's own comment claims a denied Bearer-token command never lands in the KB) | _SECRET_RES (a port of hooks/_scrub.sh, the 'substrate-wide' source of truth) only covers ghp_ among GitHub token prefixes and has no Authorization/Bearer, api-key/secret flag, basic-auth user:pass flag, NAME_PASSWORD=/A |
| `plugins/ravenclaude-core/scripts/thing-denial-kb.py:428` | Agent-writable 'resolution'/'doc' text (and unsanitised category/source) is injected verbatim into every future session's context; learned resolutions also override the seed security rules | cmd_resolve stores --resolution/--doc with no scrub, clip or newline stripping (line 445) and any agent session can call it; recall prints it as a trusted '✅ resolution' into the SessionStart additionalContext (hook bann |
| `plugins/ravenclaude-core/scripts/thing-harden.py:407` | harden_ok computes tier descent from the built-in default category tier map, ignoring the consumer's resolved category_tier_map, then the orchestrator runs the rewrite autonomously | _tier_for uses decision_mod._DEFAULT_CATEGORY_TIER_MAP although gate_floor is passed in from the resolved config. If a consumer raises a category (e.g. command_review.category_tier_map: {shell_local_mutate: extreme}) so  |
| `scripts/thing-golden-eval.py:153` | Golden-set regression gate passes vacuously: zero matching entries (empty corpus, a typo'd 'lane', or truncated file) prints '0/0 pass' and exits 0 | det = entries with lane == 'deterministic'; total = len(det) + fails; return 1 if fails else 0. Reproduced: an empty --corpus file and a one-line corpus with lane 'determinstic' both print '== golden-set deterministic la |

### Dashboard server / generators (7)

| location | finding | failure scenario |
|---|---|---|
| `plugins/ravenclaude-core/scripts/serve-dashboards.py:78` | Hardening G15 applied to the root server only: the shipped consumer server still allows /__save and /__read of .ravenclaude/environment-context.md | The root server removed `.ravenclaude/environment-context.md` from ALLOWED_TARGETS/ALLOWED_READ (comment at scripts/serve-dashboards.py:76: 'dead attack surface ... no UI producer'). The bundled plugin copy - the build c |
| `plugins/ravenclaude-core/scripts/serve-dashboards.py:1809` | Bundled consumer server imports/executes scripts from the served PROJECT before its own bundled copies | _reserve_engine, _read_concern_stats and _read_worktree_guard are byte-identical in both server copies. In the root dev server project_root is the (trusted) marketplace; in the bundled plugin server project_root is PROJE |
| `scripts/_index_dashboard_template.py:1344` | Portal plugin-detail view: scenario `difficulty` is interpolated into a class attribute without esc() (attribute-breakout XSS from agent frontmatter) | `diffCls = (d) => "d-" + (d \|\| "starter")` is used unescaped inside `<span class="uc-diff ${diffCls(x.difficulty)}" ...>`, while the sibling text node in the same template (`${esc(x.difficulty)}`) and the use-case tabl |
| `scripts/generate-dashboards.py:12169` | Plugin-variables form: missing `+` between string literals lets ASI truncate the innerHTML assignment (no textarea, no Save/Download) | In renderPluginVarsForm the line ending `spellcheck="false"'` is followed on the next line by a bare string literal (no `+`), and again after `per line"'`. JavaScript inserts a semicolon before each offending string toke |
| `scripts/generate-index-dashboard.py:471` | Frontmatter parser silently degrades without PyYAML: a regenerated index.html loses every scenario / use-case row | _parse_frontmatter prefers PyYAML but on ImportError (or any parse error, swallowed by `except Exception: pass`) falls back to a line parser that cannot read nested `scenarios`, `quickstart` or block-style lists. The gen |
| `scripts/serve-dashboards.py:2189` | /__read: yaml.safe_load can return non-JSON-serializable values (dates); json.dumps then raises outside any try - dropped connection, hydration silently fails | `payload["parsed"] = yaml.safe_load(content)` sits in a try/except, but the later `self._json(200, payload)` (line 2197) is not guarded. YAML scalars such as `since: 2026-01-01` load as datetime.date, so json.dumps raise |
| `scripts/serve-dashboards.py:2609` | send_error() is fed untrusted multi-line / non-latin-1 text, which goes raw into the HTTP status line | BaseHTTPRequestHandler.send_error writes `message` verbatim into `HTTP/1.0 <code> <message>` (encoded latin-1 strict). /__save validation errors interpolate PyYAML's MarkedYAMLError text (multi-line, quotes the offending |

### Egress / orchestration / posture (9)

| location | finding | failure scenario |
|---|---|---|
| `plugins/ravenclaude-core/scripts/apply-comfort-posture.py:124` | shell_readonly category auto-allows mutating commands (find, git branch, git remote, rg --pre) | The `shell_readonly` emission list is placed in the allow bucket when the owner picks `allow` (the recommended posture), but it contains prefix rules whose arguments mutate or execute: `Bash(find:*)` matches `find . -del |
| `plugins/ravenclaude-core/scripts/claude-orchestrate.sh:137` | Secret pattern set under-matches common token families (the egress floor for all three delegates and this script) | The inline fallback list (declared byte-for-byte equal to hooks/_scrub.sh) only covers `ghp_` for GitHub and `AKIA` for AWS. Running the canonical _scrub_reason against sample tokens left these UNREDACTED: GitHub OAuth/i |
| `plugins/ravenclaude-core/scripts/claude-orchestrate.sh:300` | `--tools ""` is documented as ZERO tools but only removes built-in tools; MCP servers still load in the nested session | The header and comments present layer 3 as a structural guarantee that the nested session 'has ZERO tools ... regardless of prompt injection'. `claude --help` states `--tools` selects 'from the built-in set', and a separ |
| `plugins/ravenclaude-core/scripts/context-usage-meter.py:514` | Grok's ~/.grok/config.toml context_window overrides the real model window for Claude Code sessions | measure() takes rank 3 `window_from_grok_config()` for ANY session and labels it 'explicit', so the model-aware Claude resolution (rank 4) only runs when no Grok config exists. Reproduced with GROK_HOME pointing at a con |
| `plugins/ravenclaude-core/scripts/handoff-spawn.sh:169` | Always-printed copy-paste block embeds raw --task-id inside double quotes - command substitution executes when pasted | $seed (printed by copy_paste_block, the 'ALWAYS printed' path, and echoed again on --dry-run) is `grok "${grok_prompt}"` with the unvalidated task id interpolated raw. The file's own comment claims the injection hole was |
| `plugins/ravenclaude-core/scripts/handoff-spawn.sh:683` | VS Code / Cursor same-host spawn types the unquoted launch path into a live shell and reports success | The launch script path (`$project_root/.ravenclaude/runs/$task_id/launch-successor.sh`) is escaped only for AppleScript string syntax, then typed with `keystroke` followed by Return into a new integrated terminal, where  |
| `plugins/ravenclaude-core/scripts/pseudonymize-brief.py:88` | Luhn-gated card regex is greedy, so a valid card number followed by separator+digits (CVV/expiry) is never tokenized | `finditer` takes the greedy match `(?:\d[ \-]?){12,18}\d` (up to 19 digits) and THEN applies the Luhn validator; when the validator rejects the over-long match nothing backtracks to the shorter valid card inside it, and  |
| `plugins/ravenclaude-core/scripts/route-task.py:34` | Escalation rules use stem prefixes and singular nouns inside \b...\b, so common word forms never escalate (router leaks tasks to the cheap lane) | The module's whole safety design is 'escalation is BROAD, cheap is NARROW, default is claude'. But `escalat`, `vulnerab`, `diagnos`, `investigat` and `migrat` are followed by `\b`, which cannot match inside a longer word |
| `plugins/ravenclaude-core/scripts/stall_watch.py:276` | PID-reuse guard is dead code and cannot detect reuse: proc_identity_ok only tests process existence and its result is never read | The docstring says the function 'Guard[s] against PID reuse', but it returns `bool(out)` of `ps -o etime= -p <pid>` - i.e. just 'a process with this pid exists', which pid_alive() already established - and the `identity_ |

### Guardrail hooks (23)

| location | finding | failure scenario |
|---|---|---|
| `plugins/ravenclaude-core/hooks/claim-grounding-lint.sh:260` | PostToolUse advisory forks 2-10 processes per line of every edited docs/knowledge markdown file; measured 37.7 s for a 3000-line file | The scan loop pipes every line through `echo "$line" \| grep ...` several times (the claim-lint-ok test at line 253 and the outcome/diagnostic test at line 260 run on EVERY line), i.e. O(N) subprocess creation, on a hook |
| `plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh:320` | Stop mode runs the wrapped hook with `2>/dev/null`, so dod-gate's first-run trust instructions (exit 2 + stderr) are replaced by a generic reason | Reproduced: dod-gate.sh run directly exits 2 with a stderr block containing the `touch "<confirm file>"` authorization step; run through `copilot-hook-adapter.sh stop`, the adapter emits only {"decision":"block","reason" |
| `plugins/ravenclaude-core/hooks/dod-gate.sh:46` | Posture lookup uses the payload/PWD cwd; from a subdirectory the definition-of-done gate exits 0 without running | Reproduced: repo with a tracked, modified python file and `definition_of_done.cmd: 'false'`: Stop at cwd=<root> exits 2 (first-run trust check); Stop at cwd=<root>/pkg exits 0 silently. A session whose last Bash `cd` was |
| `plugins/ravenclaude-core/hooks/dod-gate.sh:91` | `git status --porcelain=v1 -z` collapses wholly-untracked directories to `?? dir/`, so source files created in a NEW directory are never seen and the gate is skipped | Reproduced: after a commit, create `newpkg/feature.py` (new directory) and nothing else. Porcelain output is `?? newpkg/` (no .py suffix), the `grep -cE '\.(ts\|...\|py\|...)$'` at line 93 counts 0, and the gate exits 0  |
| `plugins/ravenclaude-core/hooks/enforce-git-protocol.sh:234` | The subject check takes the first line of a `-m "$(cat <<'EOF' ... EOF)"` message, which is the shell wrapper text, so the standard heredoc-style commit is always 'non-conventional' | Reproduced with git_protocol: block: `git commit -m "$(cat <<'EOF'` + newline + `feat(core): add thing` + body + `EOF` + newline + `)"` exits 2 with 'commit subject is not Conventional Commits ... "$(cat <<'EOF'"'. The s |
| `plugins/ravenclaude-core/hooks/enforce-layout.sh:88` | Only `..` is refused; `/./` and `//` segments survive into rel_path, so forbidden/in_scope globs compare against a non-canonical path | Manifest `forbidden_globs: ["secrets/*"]`, `allowed_globs: ["*"]`. Reproduced: `<root>/secrets/key.pem` -> exit 2, but `<root>/./secrets/key.pem` and `<root>//secrets/key.pem` -> exit 0 (rel_path becomes `./secrets/key.p |
| `plugins/ravenclaude-core/hooks/gemini-hook-adapter.sh:147` | Gemini posttool lane reads a top-level `file_path` that Gemini's payload nests under tool_input and never forwards stdin, so every PostToolUse hook is a silent no-op | posttool does `fp="$(_field file_path)"` (jq `.file_path`, top level) and then `bash "$real" "$fp" >/dev/null 2>&1`. The adapter has already consumed stdin with `payload="$(cat)"`, so the real hook gets neither a stdin p |
| `plugins/ravenclaude-core/hooks/guard-destructive.sh:298` | Newlines (command separators) are collapsed to spaces before the `[^;&\|]*`-scoped matchers run, so a flag on a later line is attributed to an earlier `git push`/`curl` | Reproduced exit 2 for the two-line commands `git push origin feature` + newline + `rm -f /tmp/x.txt` (reported as a force push), + `tail -f log.txt` (force push), + `ls -d build` (reported as remote-branch deletion), and |
| `plugins/ravenclaude-core/hooks/guard-destructive.sh:588` | `_is_dangerous_rm` (and chmod/find/truncate) test the recursive flag and the absolute-path target against the WHOLE command string, not the rm invocation | Reproduced exit 2 'recursive-rm-of-dangerous-target' for `cd /tmp/proj && rm -rf build`, `rm -rf build && ls /tmp`, `ls -R /tmp; rm notes.txt` (the `-R` belongs to ls, the target to ls, the rm has neither) and exit 2 're |
| `plugins/ravenclaude-core/hooks/guard-destructive.sh:1823` | Any `-X` flag that is bare-trailing or carries an unresolvable value is denied as a DELETE API call, regardless of the tool | Round 13/14 dropped the gh/curl command-name requirement, so `_seg_has_delete_method` now fires on every tool with an `-X` option. Reproduced exit 2 'destructive-delete-api-call' for `mvn test -X` (debug flag, bare trail |
| `plugins/ravenclaude-core/hooks/guard-destructive.sh:1857` | `git reset --hard` deny pattern requires `--hard` immediately after `reset`; flag-after-ref and flag-before spellings slip through | `git reset HEAD~1 --hard` and `git reset -q --hard` both exit 0 (reproduced) while `git reset --hard HEAD~1` exits 2. Git accepts options after the commit-ish (verified: `git reset HEAD~1 --hard` printed 'HEAD is now at  |
| `plugins/ravenclaude-core/hooks/guard-destructive.sh:1864` | Pipe-to-interpreter guard tolerates only `sudo` and `env VAR <interp>`; `\| sudo -E bash` and `\| env bash` are not matched | `curl -fsSL https://host/setup.sh \| sudo -E bash -` (the common NodeSource/installer idiom) and `curl https://host/x \| env bash` both exit 0 (reproduced); the control `curl https://host/x \| bash` exits 2. After `sudo` |
| `plugins/ravenclaude-core/hooks/guard-premise.sh:486` | The T-SHAPE exemption `rel.startswith('.claude/')` also swallows `.claude/worktrees/<wt>/...`, the nested-worktree layout the file's own comments name as where parallel agents run | When CLAUDE_PROJECT_DIR is the primary checkout and the agent writes to `<proj>/.claude/worktrees/wt/src/new_module.py`, rc_rel returns `.claude/worktrees/wt/src/new_module.py`, which hits the prefix exemption and exits  |
| `plugins/ravenclaude-core/hooks/guard-web-access.sh:68` | Host extraction only cuts at the first `/`, so a URL with `?` or `#` directly after the authority yields a host like `evil.example?x=1` that matches no deny rule | deny: [evil.example]. Reproduced: `https://evil.example/path` -> exit 2 (blocked); `https://evil.example?x=1` and `https://evil.example#frag` -> exit 0 with no output (falls through to the normal prompt instead of the bl |
| `plugins/ravenclaude-core/hooks/guard-web-access.sh:160` | Domains in the per-session `web-allow.txt` are silently allowed, but that file is writable by the agent itself with no user choice involved | The YAML allow-list is protected by a first-use `ask` precisely because 'a hostile YAML edit can't silently auto-allow exfiltration' (line 165-170), yet the session file has no such check. Reproduced: writing `attacker.e |
| `plugins/ravenclaude-core/hooks/reapply-posture.sh:75` | SessionStart failure path echoes the posture translator's raw output (which quotes attacker-controlled YAML values) into additionalContext | On a translator failure the hook prints `$out` (python stderr+stdout, 2>&1) via _advise.sh, which re-emits it as SessionStart additionalContext under the trusted 'RavenClaude guard notice' banner. apply-comfort-posture.p |
| `plugins/ravenclaude-core/hooks/route-decision-review.sh:69` | With `set -euo pipefail`, the mode-parsing pipeline's `grep` returns 1 when the posture file has no `decision_review:` line, aborting the script with exit 1 (non-blocking hook error) instead of the intended `emit_allow` | Reproduced: posture file containing only `design_checkins: true`, AskUserQuestion payload -> exit code 1, empty stdout (decision_review: off -> exit 0 with the allow JSON). Any consumer with a comfort-posture file that d |
| `plugins/ravenclaude-core/hooks/runaway-brake.sh:44` | Posture lookup (and the counter file location) use the payload `cwd`; from any subdirectory the brake silently no-ops | Reproduced: with `max_consecutive: 2`, three identical calls at cwd=<root> trip (2nd call exits 2), while four identical calls at cwd=<root>/pkg all exit 0 (no posture file found -> exit 0, and the counter state would be |
| `plugins/ravenclaude-core/hooks/runaway-brake.sh:169` | `exec 9>file 2>/dev/null` permanently redirects the hook's own stderr to /dev/null, so the trip message is never delivered (exit 2 with empty stderr) | `exec` with only redirections applies them to the current shell, so `2>/dev/null` here is not scoped to the flock call. Reproduced on Linux (flock present) with `max_consecutive: 2`: the 2nd identical call exits 2 with s |
| `plugins/ravenclaude-core/hooks/thing-denial-kb-recall.sh:25` | Learned denial 'resolutions' are stored unscrubbed/unbounded and replayed into every future SessionStart context as a 'trusted fix' (persistent memory-poisoning channel) | The hook injects the output of `thing-denial-kb.py recall` and its banner promises 'Only DERIVED labels ... + the trusted fix'. But cmd_resolve stores an agent-supplied `--resolution` and `--doc` verbatim (`learned[signa |
| `plugins/ravenclaude-core/hooks/thing-orchestrator.sh:694` | Tie-breaker (Thor) is run after the panel with a full fresh `seat_timeout` and no cumulative deadline, so panel + Thor can exceed the 90s hook timeout, which the platform treats as fail-OPEN | The header and hooks.json comment state the ~75s panel deadline 'stays under the 90s hook timeout so the script emits its own verdict before the platform's fail-OPEN-on-timeout fires'. That holds only until Thor is conve |
| `plugins/ravenclaude-core/hooks/worktree-guard.sh:946` | SessionStart lane banner injects raw .ravenclaude/lane.md task text (and the branch name) into additionalContext, unbounded and unsanitized | register builds ctx with `task=${task}` where task is the first `task:` line of $REAL_TOP/.ravenclaude/lane.md (a repo file) and `branch=${br}` from git, then emits it via jq as hookSpecificOutput.additionalContext. The  |
| `plugins/ravenclaude-core/hooks/worktree-guard.sh:993` | Stale-lease takeover hard-denies (exit 2) with NO stderr message when the holder auto-commit fails, and mislabels the event 'lease-stale-anchor' | _wg_lease_autocheckin only prints a reason on its anchor-branch refusal. Its other failure paths (`wg_git add -A ... \|\| return 1`, `git commit -q -m ... \|\| return 1`, all output sent to /dev/null) return 1 silently.  |

### Premise / claim gates (1)

| location | finding | failure scenario |
|---|---|---|
| `plugins/ravenclaude-core/scripts/premise-gate.py:223` | An over-floor phase that declares no depends_on_claims is only listed as 'unwired' and the gate still exits 0 (and block-style YAML edge lists are not recognised) | evaluate() puts such a phase in unwired and 'continue's; run() ignores unwired for the exit code unless NO phase anywhere declares edges. Reproduced: P1 declares 'depends_on_claims: [1]' (an observation), P2 creates a ne |

### repo-review engine (12)

| location | finding | failure scenario |
|---|---|---|
| `plugins/ravenclaude-core/skills/repo-review/scripts/block_planner.py:256` | Block manifest pins no plan identity; every block invocation regenerates the plan, so a block's batchIds can silently point at different files than the manifest assigned | build_manifest records plan_path/run_id but not the plan's commit or a digest. repo-sweep.workflow.js re-runs repo_map.py (--out the same PLAN_PATH) at the start of EVERY invocation and only checks that each batchIds ent |
| `plugins/ravenclaude-core/skills/repo-review/scripts/estimate_cost.py:225` | Estimator never models --converge: verify+fix+merge are counted once, leaving ~100 calls of headroom for iterations 2..N | total_agents = review_agents + v_max + k_max + o counts one Review/Merge/Verify/Fix pass. A --converge run repeats Merge + Verify enumerate + per-file verify (<= verifyCap) + Fix enumerate + per-file fix (<= fixCap) ever |
| `plugins/ravenclaude-core/skills/repo-review/scripts/findings_merge.py:130` ✅fixed | One torn/invalid shard raises JSONDecodeError and aborts the entire merge - including the documented hand-recovery path | load_shards does an unguarded json.load per shard. Review agents write shards directly (no atomic rename), and the SKILL's recovery procedure exists precisely for a session-usage-limit failure mid-Review - when a half-wr |
| `plugins/ravenclaude-core/skills/repo-review/scripts/findings_merge.py:131` ✅fixed | Shards that are not a JSON array of objects (or whose name does not match) are silently dropped; stats cannot tell 'dimension found nothing' from 'shard ignored' | `if not isinstance(data, list): continue` (and the non-dict/ non-matching-filename skips) emit no warning and no counter. Reproduced: a shard {"findings":[{... severity: blocking}]} -> survivors=0, stats raw_input_count= |
| `plugins/ravenclaude-core/skills/repo-review/scripts/findings_merge.py:151` | A finding with no `title` hashes to an empty token set, so every such finding in the same file and 5-line bucket collapses into one survivor (distinct bugs silently dropped) | compute_key keys on file + line//5 + title tokens; with title '' the token list is empty. Reproduced: two different bugs (SQL injection / hardcoded password, lines 10 and 11, `description` only) -> 1 survivor, raw_input_ |
| `plugins/ravenclaude-core/skills/repo-review/scripts/findings_merge.py:311` ✅fixed | by_priority counts only the capped survivors; over_cap findings are invisible to it, so the --converge 'CONVERGED - 0 open P0-P3' claim and the report's priority line understate real findings | run_merge computes by_priority over capped_survivors while after_dedup_count counts everything. Reproduced: three blocking findings with cap=1 -> by_priority {'P0': 1,...} and over_cap holds two more P0s. repo-sweep.work |
| `plugins/ravenclaude-core/skills/repo-review/scripts/fix_summary.py:150` | The advertised 'hard safety invariant' is a tautology: rows and total_applied are both derived from the same receipts, so it can only fail if this code is edited | write_summary asserts len(rows) == total_applied, but build_rows builds one row per entry of receipt['applied'] and main() computes total_applied = sum(len(r['applied'])...) from the same list. It never checks the tree ( |
| `plugins/ravenclaude-core/skills/repo-review/scripts/fix_summary.py:200` | Patch/stat capture ignores git's return code: a failing git writes an empty fixes.patch and exits 0; untracked/staged changes are never captured | subprocess.run([... 'diff'], capture_output=True).stdout is used without checking returncode. Reproduced: --repo-root /nonexistent/not-a-repo with receipts claiming 3 applied fixes -> exit 0, fixes.patch and fixes.stat b |
| `plugins/ravenclaude-core/skills/repo-review/scripts/repo_map.py:27` | Plan is not a pure function of (HEAD, config): the churn window is relative to wall-clock now, so batch ids/ordering change over time on an unchanged commit | The docstring states 'Same commit + same config must yield a byte-identical plan' and SKILL.md lists 'determinism (same commit -> byte-identical plan)' as covered, but churn_rank() calls `git log --since=90.days`. Reprod |
| `plugins/ravenclaude-core/skills/repo-review/scripts/repo_map.py:124` ✅fixed | Source filter is extension-only: ESM/CJS JavaScript and extensionless shell scripts are classified non_source and never reviewed (excluded.non_source is an opaque count) | SOURCE_EXTENSIONS lacks .mjs/.cjs/.mts/.cts/.ps1 and ALWAYS_SOURCE_NAMES is only {'Dockerfile'}, so `Path(rel_path).suffix in SOURCE_EXTENSIONS` rejects them. Measured on this repo's own plan: 25 tracked .mjs/.cjs files  |
| `plugins/ravenclaude-core/skills/repo-review/scripts/repo_map.py:182` ✅fixed | --since silently drops changed files whose names git quotes (non-ASCII / special characters): `git diff --name-only` is read without -z | Reproduced: repo with src/plain.py and src/café.py both modified since tag base. `git diff --name-only base...HEAD` prints "src/caf\303\251.py" (quoted, octal-escaped) and src/plain.py; build_plan(since='base') returned  |
| `plugins/ravenclaude-core/skills/repo-review/scripts/repo_map.py:187` ✅fixed | --since with an unresolvable ref silently falls back to the whole repo and reports nothing about it | `except GitError: pass` leaves `tracked` unfiltered. Reproduced: build_plan(since='no-such-ref') returned the full file set (tracked=5 of 5) with no stderr and coverage.deferred_reason=None. A typo like --since origin/mi |

## 3. P2 — minor findings (91)

### CI gate scripts (6)

| location | finding |
|---|---|
| `scripts/check-frontmatter.py:286` | check-frontmatter exits 0 with 'Frontmatter OK - every skill/agent parses...' when it scans zero files |
| `scripts/check-generated-gate-state.py:31` | Gate 210 is named for a class ('prose is not a typed lie') but denylists exactly one phrase; its self-test's first check is true by construction |
| `scripts/check-hard-rule-floor.py:168` | Source-scan only recognizes docs/ and tests/fixtures skips and a comment-stripper that mis-parses ${v#pat}; other path skips on the deny path pass undetected |
| `scripts/check-inception-coverage.py:56` | Gate 242 (no `paths:` on required workflows) covers 3 of the 7 workflows the live ruleset requires |
| `scripts/check-layout.py:83` | check-layout reads `git ls-files` / `git diff --name-only` without -z: any non-ASCII path arrives quoted and can never match the allow-list (and a forbidden one is mis-reported) |
| `scripts/check-nested-dispatch.py:70` | Dispatch grants are a closed name list {agent, task}; other dispatch-capable tools (e.g. Workflow, which fans out agent() calls) are not recognized |

### CI workflows (9)

| location | finding |
|---|---|
| `.github/workflows/github-protocol-pr-title.yml:34` | Required check 'Semantic PR title (Conventional Commits)' exits 0 when dispatched manually, validating no title |
| `.github/workflows/github-protocol-secret-scan.yml:31` | TruffleHog filtered to verified+unknown results, so unverified pattern matches never fail the required secret scan |
| `.github/workflows/github-protocol-zizmor.yml:30` | SHA-pin integrity is never verified: the required zizmor check runs offline, so impostor-commit / ref-version-mismatch audits are skipped |
| `.github/workflows/golden-set-inject-light.yml:64` | The 'never a required check' self-assertion cannot ever fire: it greps a ruleset listing that contains no check names, for a name that is not a check context |
| `.github/workflows/inventory-sweep.yml:90` | ANTHROPIC_API_KEY is a repo-level secret with no dedicated environment (inventory-sweep, spike-claude-availability) |
| `.github/workflows/inventory-sweep.yml:109` | The 'sweep is NOT a required status check' re-measurement is a no-op: wrong endpoint depth and wrong name |
| `.github/workflows/quarantine-intake.yml:29` | Write-scoped token (contents/pull-requests/issues: write) applies to the whole job that parses untrusted issue content |
| `.github/workflows/quarantine-intake.yml:146` | Quarantine PR title violates the now-required Conventional-Commits title check, and the PR body's CI claims are stale |
| `.github/workflows/regenerate-artifacts.yml:112` | Unpinned PyPI install feeds generators whose output is auto-squash-merged to main under a PAT |

### Command-review tribunal (the Thing) (11)

| location | finding |
|---|---|
| `plugins/ravenclaude-core/scripts/thing-concern-stats.py:68` | A Saga file that is valid JSON but not an object (or has non-list 'seats') crashes the whole report despite the 'one bad entry never poisons the report' contract |
| `plugins/ravenclaude-core/scripts/thing-concerns.py:289` | Unknown/typo'd severity strings silently rank as 'low' (rank 0) instead of failing or defaulting conservatively |
| `plugins/ravenclaude-core/scripts/thing-decide.py:187` | Production code honours test-only env hooks (THING_DECIDE_MOCK_VERDICT / THING_DECIDE_MOCK_EVAL) with no guard |
| `plugins/ravenclaude-core/scripts/thing-decide.py:466` | _parse_seat does not validate types: an unhashable 'verdict' raises TypeError (crashing the panel) and a NaN confidence passes the confidence threshold |
| `plugins/ravenclaude-core/scripts/thing-decide.py:601` | Only Heimdall's abstention forces a tie-break; if Forseti (the risk seat) abstains, the remaining two seats can return a binding verdict |
| `plugins/ravenclaude-core/scripts/thing-decide.py:687` | decide() runs the seats sequentially with no overall deadline (panel_deadline_seconds is ignored) and writes the Saga entry only at the end |
| `plugins/ravenclaude-core/scripts/thing-decision.py:1206` | A user 'bypass' pattern auto-allows any command it re.search-matches anywhere (incl. chained tails); only a CRITICAL concern prevents it, high-severity concerns do not |
| `plugins/ravenclaude-core/scripts/thing-decision.py:1449` | In the opted-in dev repo every classification spawns 'gh api' (up to 10s, uncached) even when no exemption is relevant |
| `plugins/ravenclaude-core/scripts/thing-denial-kb.py:278` | A malformed seed regex or a non-integer 'count' row aborts every sync silently (top-level handler swallows it, exit 0, cursor never advances) |
| `plugins/ravenclaude-core/scripts/thing-harden.py:95` | The git-force-with-lease transform decides 'force' from the whole command string, so an unrelated -f elsewhere turns a plain push into a force-with-lease push |
| `plugins/ravenclaude-core/scripts/thing-harden.py:351` | The 'AppSec-signed' registry YAML is never consulted to authorise a transform: apply_all iterates the hard-coded _APPLIERS dict |

### Dashboard server / generators (13)

| location | finding |
|---|---|
| `plugins/ravenclaude-core/scripts/serve-dashboards.py:2803` | Port-reclaim 'is this our dashboard?' test compares the holder's process cwd with PROJECT_ROOT, but with --project-root the server does not chdir - it can SIGTERM a dashboard serving a DIFFERENT project |
| `scripts/_index_dashboard_template.py:1296` | esc() (HTML-escaping) is used inside a JS string literal inside an onclick attribute - `&#39;` is decoded back to `'` before the JS runs |
| `scripts/generate-dashboards.py:3126` | Generated dashboard.html/index.html embed OS-dependent paths: str(Path.relative_to(...)) yields backslashes on Windows |
| `scripts/generate-dashboards.py:12343` | Web-access editor emits user-typed domains as unquoted YAML scalars: `*.example.com` is a YAML alias error and `yes`/`no`/`1.5` become non-strings |
| `scripts/serve-dashboards.py:394` | /__runs reads every events.jsonl/actions.log end-to-end just to count lines, up to 500 run dirs per request |
| `scripts/serve-dashboards.py:456` | _read_hook_events holds every hook event of every run in memory before applying the day window |
| `scripts/serve-dashboards.py:461` | Heimdall/Vidarr sort on e.get("ts", "") raises TypeError when a JSON-valid event has ts:null or a non-string ts |
| `scripts/serve-dashboards.py:764` | /__nidhoggr spawns one `git log` per plugin (184) serially on every request, with no cache |
| `scripts/serve-dashboards.py:1264` | _read_streams reads the whole history.jsonl to keep 25 lines, and a UnicodeDecodeError is not caught (only OSError) |
| `scripts/serve-dashboards.py:2220` | /__saga uses glob.glob on an unescaped absolute path: a project path containing [ ] * ? shows an empty Review log |
| `scripts/serve-dashboards.py:2235` | /__saga: a thing-*.json that is valid JSON but not an object crashes the whole endpoint (docstring promises malformed files are skipped) |
| `scripts/serve-dashboards.py:2606` | comfort-posture.yaml - the most security-sensitive save target - is the only /__save target written with no structural validation |
| `scripts/serve-dashboards.py:3111` | An explicit --bind <specific IP> yields a server that 403s every request (bind address never added to the Host allow-list) |

### Egress / orchestration / posture (8)

| location | finding |
|---|---|
| `plugins/ravenclaude-core/scripts/apply-comfort-posture.py:637` | Unknown category keys are ignored silently, so a typo in a deny category falls back to global_default |
| `plugins/ravenclaude-core/scripts/claude-orchestrate.sh:94` | Relay-all egress floor is skipped for any scope value other than the exact lowercase string `all` |
| `plugins/ravenclaude-core/scripts/conserve-tokens.py:310` | `changed` is true on the first prompt of every session, printing a spurious 'CONSERVE TOKENS released' directive |
| `plugins/ravenclaude-core/scripts/context-usage-meter.py:455` | read_posture anchors on a commented `# context_handoff:` example, so a real block later in the file is silently ignored |
| `plugins/ravenclaude-core/scripts/grok-delegate.sh:115` | Value-taking flag as the last argument spins forever (`shift 2` fails without consuming) |
| `plugins/ravenclaude-core/scripts/pseudonymize-brief.py:177` | Vault is only 0600 when newly created; an existing --map-file keeps its old (possibly world-readable) mode |
| `plugins/ravenclaude-core/scripts/routine-reserve.py:143` | Repo-level comfort-posture.yaml can override the account-scoped `home` repo, redirecting the SessionStart git fetch |
| `plugins/ravenclaude-core/scripts/stall_watch.py:546` | Every tick fully re-reads each stalled session's transcript just to count compactions |

### Guardrail hooks (31)

| location | finding |
|---|---|
| `plugins/ravenclaude-core/hooks/_advise.sh:57` | Hooks run `python3 -c`/`python3 -` from the project cwd, so a repo-supplied json.py/re.py/hashlib.py is imported and executed (no -I/-P/PYTHONSAFEPATH anywhere) |
| `plugins/ravenclaude-core/hooks/_advise.sh:103` | rc_advise_flush relays ALL buffered stderr (including raw file lines and command text echoed by call sites) as additionalContext under a trusted banner |
| `plugins/ravenclaude-core/hooks/_portable.sh:45` | The perl `alarm` fallback kills only the exec'd process, not its children, unlike GNU timeout which signals the whole process group |
| `plugins/ravenclaude-core/hooks/_scrub.sh:64` | Pattern set misses several very common credential shapes, so they are written verbatim to hook-events.jsonl (guard-destructive passes the FULL command string) and echoed to stderr |
| `plugins/ravenclaude-core/hooks/agent-dispatch-evaluator.sh:118` | Unguarded jq in a command substitution under set -e/pipefail makes the hook exit non-zero on a malformed payload, contradicting 'ANY error -> allow' |
| `plugins/ravenclaude-core/hooks/agent-dispatch-evaluator.sh:216` | LLM-classifier output (verdict/tier/confidence, unvalidated and uncapped) plus raw subagent_type is written into the event `rule`, which the run-state monitor then emits as a notification line |
| `plugins/ravenclaude-core/hooks/cursor-hook-adapter.sh:169` | Cursor adapter drops the stdin payload it consumed for stop/promptsubmit/sessionstart, so hooks that read their payload run on empty input |
| `plugins/ravenclaude-core/hooks/dashboard-autostart.sh:87` | Launcher path has no fallback when CLAUDE_PLUGIN_ROOT is unset (the dev-mirror registration), resolving to /bin/rc |
| `plugins/ravenclaude-core/hooks/enforce-git-protocol.sh:149` | shlex-based segmenting treats only whole-token `;`/`&&`/`\|\|`/`\|`/`&` as separators, so a second git command after a newline or a glued `;` is swallowed into the first command's args |
| `plugins/ravenclaude-core/hooks/enforce-git-protocol.sh:200` | `git branch --merged main` / `--contains <sha>` are treated as plain branch creation because only some list options are excluded |
| `plugins/ravenclaude-core/hooks/enforce-layout.sh:46` | When jq is absent and the path arrives via stdin (the Claude Code contract), the hook exits at line 46 before reaching the 'jq not found' warning, so the layout gate no-ops silently |
| `plugins/ravenclaude-core/hooks/enforce-layout.sh:112` | The traversal scrub tests the substring `..` anywhere in the path, so ordinary names like `notes..txt` or `v1..v2.md` are denied |
| `plugins/ravenclaude-core/hooks/guard-destructive.sh:71` | Registered for Read/Write/Edit/WebFetch/mcp calls too, where `tool_input.command` is legitimately empty, so it prints a false 'guard is DEGRADED (jq and python3 both unavailable)' warning on every non-Bash call |
| `plugins/ravenclaude-core/hooks/guard-destructive.sh:1137` | Segment-gate builder walks the command one character at a time with `${var:i:1}`, which is O(n) per step in a UTF-8 locale, making `_is_dangerous_merge` quadratic |
| `plugins/ravenclaude-core/hooks/guard-destructive.sh:1512` | `git merge --abort` / `--quit` and `git pull --rebase` on main are denied as 'bypass-shaped merge' |
| `plugins/ravenclaude-core/hooks/guard-destructive.sh:1864` | Pipe-to-interpreter pattern matches an interpreter given ANY arguments, so read-only data uses (`python3 -m json.tool`, `node -e`, `perl -pe`) are blocked |
| `plugins/ravenclaude-core/hooks/guard-foreground-suite.sh:166` | First-word check lets wrapper-prefixed invocations of the full suite through (time/timeout/env/subshell), and denies `bash -n audit-gates.sh` |
| `plugins/ravenclaude-core/hooks/guard-memory-compaction.sh:139` | Snapshot file name has 1-second resolution and the run dir falls back to `unknown` (Claude Code does not export CLAUDE_SESSION_ID), so rapid or cross-session writes overwrite the before-image the guard exists to preserve |
| `plugins/ravenclaude-core/hooks/guard-memory-compaction.sh:232` | MultiEdit shrink is computed as `old_bytes + delta` where delta comes from jq `length` (codepoints), mixing units; multibyte memory shrinks are under-counted up to 3-4x |
| `plugins/ravenclaude-core/hooks/guard-probe-validity.sh:239` | PreToolUse advisory echoes 160 chars of the raw Bash command segment back into additionalContext |
| `plugins/ravenclaude-core/hooks/keep-awake.sh:133` | Idempotency check `pgrep -f "caffeinate -s -w $SESSION_PID"` is an unanchored regex, so another session's pid with the same prefix suppresses this session's assertion |
| `plugins/ravenclaude-core/hooks/keep-awake.sh:136` | Backgrounded caffeinate inherits the saved real-stderr fd 3 from _advise.sh and holds the hook's stderr pipe open for the whole session |
| `plugins/ravenclaude-core/hooks/log-probe.sh:76` | WebFetch is in the matcher but only Bash-shaped tool_response fields (stdout/stderr) are read, so WebFetch probes never produce a verdict |
| `plugins/ravenclaude-core/hooks/log-probe.sh:260` | session_id from the hook payload is joined into a filesystem path without the allow-list sanitizer every sibling hook applies (absolute/`..` ids write outside .ravenclaude/runs/premise) |
| `plugins/ravenclaude-core/hooks/remind-tests.sh:44` | The once-per-session latch is consulted only after two full `git status --porcelain` runs, so every later Stop still pays for both |
| `plugins/ravenclaude-core/hooks/route-decision-review.sh:173` | If perl is missing, the `\|\| printf '%s' "$reasoning"` fallback returns the ORIGINAL reasoning, undoing the tr line-break stripping as well as the U+2028/2029 fold |
| `plugins/ravenclaude-core/hooks/stream-prompt-attribute.sh:113` | Latency budget silently disappears on stock macOS because it relies on GNU `timeout` instead of the repo's _rc_timeout shim |
| `plugins/ravenclaude-core/hooks/stream-session-close.sh:72` | Stop fires every turn, not at session end, so a `session_closed` event and a state.md rewrite are appended after every assistant turn |
| `plugins/ravenclaude-core/hooks/thing-orchestrator.sh:678` | The 'cited critical can never ALLOW' backstop defaults to `false` when the severity helper fails |
| `plugins/ravenclaude-core/hooks/triage-outcome.sh:456` | Same unsanitized session_id path join as log-probe.sh (writes open.jsonl, triage-alive and seen-* files wherever sid points) |
| `plugins/ravenclaude-core/hooks/workaround-exhaustion.sh:125` | The sed scalar read only accepts an unquoted value, so `workaround_exhaustion: "block"` is read as absent and the gate (absent = off) is silently inert |

### Other (1)

| location | finding |
|---|---|
| `schemas/findings.schema.json:159` | findings.schema.json is enforced nowhere and has drifted from findings_merge.py: real merge output fails validation |

### Premise / claim gates (3)

| location | finding |
|---|---|
| `plugins/ravenclaude-core/scripts/classify_claim.py:92` | High-frequency inference markers are absent from every family (since, suggests/indicates/proves, always/never, should/might/may, has failed), so common uncited inferences type as observation |
| `plugins/ravenclaude-core/scripts/classify_claim.py:209` | Code-span/URL stripping lets an author type an inference as an observation by wrapping the claim in backticks, contradicting the 'upward only / never self-report' invariant |
| `plugins/ravenclaude-core/scripts/premise-gate.py:198` | Blast-radius heuristic under-counts: inflected verbs ('Creating', 'Adds') do not match \b(create\|add)\b and file counting uses a prefix-match extension list |

### repo-review engine (9)

| location | finding |
|---|---|
| `plugins/ravenclaude-core/skills/repo-review/scripts/estimate_cost.py:69` | Tier cap tables are hand-duplicated from repo-sweep.workflow.js and have already drifted (ultra verifyCap 160 here vs 320 in the workflow); no gate compares them |
| `plugins/ravenclaude-core/skills/repo-review/scripts/estimate_cost.py:218` ✅fixed | total_agents can exceed agent_budget and the hard cap with no flag; an empty plan reports full_coverage=True at 246 agents |
| `plugins/ravenclaude-core/skills/repo-review/scripts/findings_merge.py:156` | Survivor ids are agent-chosen, first-seen and never checked for uniqueness; downstream stages key on id |
| `plugins/ravenclaude-core/skills/repo-review/scripts/findings_merge.py:220` ✅fixed | Sorting survivors by `s["id"] or ""` crashes the merge with TypeError when ids mix int and str |
| `plugins/ravenclaude-core/skills/repo-review/scripts/findings_merge.py:246` | Dedup misses same-bug pairs at bucket boundaries, short titles and differently spelled paths (the exact-key and near-dup rules each have a hole) |
| `plugins/ravenclaude-core/skills/repo-review/scripts/fix_summary.py:50` ✅fixed | load_receipts/load_merged do not tolerate a torn or non-object receipt; the summary stage crashes exactly when a fix agent was cut off |
| `plugins/ravenclaude-core/skills/repo-review/scripts/fix_summary.py:164` ✅fixed | Receipt fields are written into a markdown table unescaped: a '\|' or newline in an LLM summary corrupts the row |
| `plugins/ravenclaude-core/skills/repo-review/scripts/review_cache.py:4` | Cache key omits the rubric/prompt/skill version, so unchanged files replay stale findings after dimensions.md or the pipeline changes |
| `plugins/ravenclaude-core/skills/repo-review/scripts/review_cache.py:293` ✅fixed | `store` trusts --findings-file: no list/shape validation, and a missing/invalid file is a raw traceback (exit 1) while every other error is a clean exit 2 |

## 4. P3 — nit / dead-code / simplification (25)

### CI gate scripts (2)

| location | finding |
|---|---|
| `scripts/check-hard-rule-floor.py:354` | --must-fail uses exit 2 for 'plants caught' and for 'could not run' (missing hook files) |
| `scripts/check-verdict-default-nonpermissive.py:165` | Header says 'Exit codes: 0 clean; 2 finding or unreadable input. Never 1' but the fail-closed paths raise SystemExit(<str>), which exits 1 |

### CI workflows (2)

| location | finding |
|---|---|
| `.github/workflows/regenerate-artifacts.yml:78` | Workflow-level write permissions instead of a read-only floor with job-level elevation |
| `.github/workflows/validate-marketplace.yml:153` | PR-code-executing jobs have no `timeout-minutes` (default 360); same in validate-layout, validate-schemas, validate-macos, github-protocol-* |

### Command-review tribunal (the Thing) (4)

| location | finding |
|---|---|
| `plugins/ravenclaude-core/scripts/thing-decide.py:578` | Second disjunct of the abstention gate can never fire on its own |
| `plugins/ravenclaude-core/scripts/thing-decision.py:1137` | Per-category timeout posture is computed and then discarded: _DEFAULT_TIMEOUT_POSTURE, the thing.yaml 'timeout_posture' merge and cfg.pop(...) are dead |
| `plugins/ravenclaude-core/scripts/thing-denial-kb.py:247` | sync re-reads and parses every historical Saga file on every SessionStart before checking the processed-cursor; the cursor stores every path and is rewritten each time |
| `scripts/thing-golden-eval.py:243` | run_live parses the corpus without per-line error handling and prints a judgment-entry count that includes entries it then skips |

### Dashboard server / generators (6)

| location | finding |
|---|---|
| `scripts/generate-index-dashboard.py:1230` | index.html is written with write_text (CRLF on Windows) while the sibling generator deliberately uses write_bytes to preserve LF |
| `scripts/serve-dashboards.py:157` | _is_plugin_config_target accepts non-ASCII lowercase letters and digits although the contract is [a-z0-9-] |
| `scripts/serve-dashboards.py:622` | _norns_git_lines: a NUL in ?plugin= raises ValueError from subprocess (not caught), contradicting 'never raises' |
| `scripts/serve-dashboards.py:2582` | /__save: non-string `path` in the JSON body reaches str methods before any type check (no 400) |
| `scripts/serve-dashboards.py:2614` | /__save writes in place (truncate-then-write) and does not handle OSError |
| `scripts/serve-dashboards.py:2819` | /__classify: a NUL in `command` raises an uncaught ValueError from subprocess.run |

### Egress / orchestration / posture (2)

| location | finding |
|---|---|
| `plugins/ravenclaude-core/scripts/context-usage-meter.py:189` | Fallback transcript-path encoder only replaces `/`, disagreeing with the documented Claude Code project-dir encoding |
| `plugins/ravenclaude-core/scripts/copilot-delegate.sh:90` | Recursion guards are per-agent: the copilot lane does not honour the grok lane's re-entrancy flag (and vice versa) |

### Guardrail hooks (5)

| location | finding |
|---|---|
| `plugins/ravenclaude-core/hooks/_host-canary.sh:241` | mktemp -d result is not checked in the Tier A canaries (the Tier D lane checks it), so a failed mktemp plants probe/marker files at the filesystem root |
| `plugins/ravenclaude-core/hooks/_model-fallback.sh:144` | `local IFS=','` is function-scoped, so with the ladder enabled the caller's runner executes with IFS=',' (enabled path differs from the 'byte-identical' disabled path) |
| `plugins/ravenclaude-core/hooks/_scrub.sh:48` | `sk-(ant-)?[A-Za-z0-9-]{20,}` has no word-boundary anchor, so any word ending in `sk-` followed by 20+ hyphenated characters is mangled |
| `plugins/ravenclaude-core/hooks/alias-deprecation-advisory.sh:35` | No-op `if` block (empty body) left in the session-id resolution |
| `plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh:114` | Blockquote suppression `^\s*>\s*` can never match because each candidate line is prefixed with `NNN:` by grep -n |

### Premise / claim gates (1)

| location | finding |
|---|---|
| `scripts/premise-gate.py:21` | Shim reports a missing canonical script as exit 2 ('tripped' in premise-gate's contract) and argparse usage errors also exit 2; could-not-run is exit 1 |

### repo-review engine (3)

| location | finding |
|---|---|
| `plugins/ravenclaude-core/skills/repo-review/scripts/estimate_cost.py:221` ✅fixed | Redundant clamp/branch: batches_affordable collapses to min(b, batches_planned) |
| `plugins/ravenclaude-core/skills/repo-review/scripts/repo_map.py:221` | churn_rank spawns one `git log` per reviewable file (933 subprocesses, ~8 s here) for what a single `git log --name-only` pass computes |
| `plugins/ravenclaude-core/skills/repo-review/scripts/repo_map.py:247` ✅fixed | Equal-risk batches tie-break on the string id, so b100 sorts before b11 |

## 5. Implemented autonomously in this PR (13)

Confirmed, clean, self-contained fixes to the `/repo-review` engine tooling (`skills/repo-review/scripts/`) — non-substrate, each shipped with a must-pass teeth assertion in that script's `--self-test`; Gate 258/260 and the whole-tree ruff/prettier floor stay green. See the PR diff and the `ravenclaude-core` CHANGELOG `0.327.1` entry.

| location | fix |
|---|---|
| `estimate_cost.py:218` | total_agents can exceed agent_budget and the hard cap with no flag; empty plan reports full_coverage=True at 246 agents |
| `estimate_cost.py:221` | Redundant clamp/branch: batches_affordable collapses to min(b, batches_planned) |
| `findings_merge.py:130` | One torn/invalid shard raises JSONDecodeError and aborts the entire merge |
| `findings_merge.py:131` | Shards not a JSON array of objects (or non-matching name) silently dropped; stats can't tell nothing-found from ignored |
| `findings_merge.py:220` | Sorting survivors by s['id'] crashes with TypeError when ids mix int and str |
| `findings_merge.py:311` | by_priority counts only capped survivors; over_cap findings invisible, so --converge 'CONVERGED - 0 open' understates |
| `fix_summary.py:50` | load_receipts/load_merged crash on a torn or non-object receipt |
| `fix_summary.py:164` | Receipt fields written into a markdown table unescaped: a pipe or newline corrupts the row |
| `repo_map.py:124` | Source filter is extension-only: .mjs/.cjs/.mts/.cts/.ps1 and extensionless scripts never reviewed |
| `repo_map.py:182` | --since silently drops changed files whose names git quotes (non-ASCII): git diff --name-only read without -z |
| `repo_map.py:187` | --since with an unresolvable ref silently falls back to the whole repo |
| `repo_map.py:247` | Equal-risk batches tie-break on the string id, so b100 sorts before b11 |
| `review_cache.py:293` | store trusts --findings-file: no list/shape validation, and a missing/invalid file is a raw traceback (exit 1) |

### Engine findings deferred here (behavior-changing / coupled)

- `block_planner.py:256` — Block manifest pins no plan identity; a block's batchIds can point at different files than assigned (why deferred: build_manifest (lines 253-260) records plan_path/run_id but no plan commit or content digest; the workflow re-runs repo_map.py each invocation and only checks b)
- `estimate_cost.py:57` — Cap guard advisory-only (same as P0 p1-est-001) (why deferred: See P0 p1-est-001: the estimator is best-effort and never gates the run path; workflow tier defaults exceed the 1000-call cap by construction at max/ultra.)
- `estimate_cost.py:69` — Tier cap tables hand-duplicated from the workflow and already drifted (ultra verifyCap 160 vs 320); no gate compares them (why deferred: estimate_cost TIER_VERIFY_CAP_DEFAULT high60/xhigh120/max160/ultra160 and TIER_FIX_CAP_DEFAULT 40/60/80/80 vs workflow EFFORT_TIERS verifyCap 40/80/160/320 and )
- `estimate_cost.py:225` — Estimator never models --converge (why deferred: total_agents (line 225) counts one Review/Merge/Verify/Fix pass; grep shows zero converge handling. A --converge run repeats Merge+Verify+Fix (+resolve + cold r)
- `findings_merge.py:151` — A finding with no title hashes to an empty token set; distinct titleless bugs in the same file+5-line bucket collapse (why deferred: Probe: two titleless distinct bugs (lines 10,11, failure_scenario only) -> 1 survivor. compute_key uses file+line//5+title tokens; title '' -> empty tokens. Rea)
- `findings_merge.py:156` — Survivor ids are agent-chosen, first-seen, never checked for uniqueness; downstream keys on id (why deferred: Line 156 `"id": finding.get("id")` with no uniqueness check; dimensions.md asks for a hash an LLM can't compute, so sequential ids collide. verify/fix/fix_summa)
- `findings_merge.py:246` — Dedup misses same-bug pairs at bucket boundaries, short titles, differently-spelled paths (why deferred: Exact merge uses fixed 5-line buckets (lines 19/20 hash differently); near-dup requires >=4 shared title tokens (line 246, absolute) AND exact file string match)
- `fix_summary.py:150` — The advertised 'hard safety invariant' is a tautology (rows and total_applied derive from the same receipts) (why deferred: Line 150 `if row_count != total_applied` compares two values both built from receipt['applied']; it never checks the tree (git diff), duplicate ids, or that ids)
- `fix_summary.py:200` — Patch/stat capture ignores git return code: a failing git writes an empty patch and exits 0 (why deferred: Probe: write_patch_and_stat(..., '/nonexistent/not-a-repo') -> fixes.patch 0 bytes, no error. Lines 199-210 use .stdout without checking returncode; FileNotFoun)
- `repo_map.py:27` — Plan is not a pure function of (HEAD, config): churn window is relative to wall-clock now (why deferred: CHURN_WINDOW='90.days' (line 27) used in churn_rank git log --since=90.days (line 150). Same HEAD days apart -> different batch ordering. Also reads working-tre)
- `repo_map.py:221` — churn_rank spawns one git log per reviewable file (933 subprocesses, ~8s) (why deferred: Line 220-221 loops per file calling churn_rank (line 147-155) which spawns a git log each; measured ~8s on this repo, ~45s at 5000 files for the 'cheap' plannin)
- `review_cache.py:4` — Cache key omits the rubric/prompt/skill version, so unchanged files replay stale findings (why deferred: Docstring/lookup key = sha256(content)+dimension+model (lines 4, 283-285). After dimensions.md tightens or a pipeline bug is fixed, every unchanged file is a ca)

