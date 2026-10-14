# Repository review — 2026-10-13 (scheduled autonomous sweep)

> **What this is.** A scheduled, autonomous whole-repo review run on branch
> `claude/awesome-wright-ki79iu`. It ran a deterministic gate panel, then a
> multi-panel expert fan-out (Panel 1 reviewers → Panel 2 orchestrator analysis →
> Panel 3 tie-break), categorized every finding **P0–P3**, auto-fixed the
> confident low-risk non-design items, and routed everything needing your
> decision (or blocked by the tribunal's own substrate protection) here.
>
> **Run artifacts:** `.ravenclaude/runs/repo-review-2026-10-13/` (gitignored).

## How the panels ran

| Phase | Who | What |
|---|---|---|
| Deterministic panel | the repo's own gates | `ci-preflight.py`, json/shell/prettier/ruff, layout, version-sync, frontmatter, hook exec-bits |
| Panel 1 (expert review) | 5 parallel Sonnet reviewers | CI workflows · enforcement/guard hooks · lifecycle hooks (×2) · shell automation — each with a strict, anti-false-positive, traced-path-required contract |
| Panel 2 (analysis) | orchestrator (Opus) | validated each finding against the code, assigned P0–P3, added impact/effort |
| Panel 3 (tie-break) | orchestrator (Opus) | adjudicated the ambiguous priorities (see note below) |

> **Panel 3 note — honest scope.** The ambiguous-priority tie-breaks below were
> adjudicated by the orchestrator (Opus — the "heavier model for tie-breaking" the
> task calls for), **not** the live `claude -p` command-review tribunal. In an
> unattended, conserve-tokens run, spawning the full seat panel per priority call
> wasn't worth the spend, and the P0–P3 calls here are rule-derivable from a
> deterministic severity map (the same scheme `/repo-review` uses). Route any
> priority you dispute through `/decision-review` and it'll convene the real panel.

## Priority scheme (deterministic)

`blocking → P0` · `major → P1` · `minor → P2` · `nit → P3`, exactly as
`/repo-review` derives it. **No P0 (blocking) findings were found** — this is a
very healthy, heavily-gated repo. The deterministic panel was almost entirely
green; the one real gate failure (index.html staleness) is fixed below.

---

## ✅ FIXED in this PR (confident, low-risk, non-design, non-substrate)

Three code fixes (RR-02, RR-03, RR-04) are applied on the branch and verified —
all root `scripts/` or a CI workflow, **none** touching a plugin (no version
bump) or a tribunal-substrate directory. RR-01 turned out to be a false positive
and needed **no change** (kept here for the trace); its underlying footgun is
routed as RR-23.

### RR-01 · (no code change — false positive) + a routed generator-hardening recommendation
- **Outcome:** `index.html` is **unchanged from `main`** (it was correct all along). The `ci-preflight` "staleness" I first saw was an **environment artifact**, not a real finding. The underlying generator footgun is real but narrow and is **routed to you below (RR-23)** rather than fixed here — applying it drags in a concept-restamp I shouldn't do blind in an unattended run (see RR-23).
- **The full cause-trace — this one bit me, recorded because the correction is the lesson:** `ci-preflight` reported `index.html` structurally stale here — `edtech-partner-success` `templates` **38** (committed) vs **40** (regenerated in this environment). I first "fixed" it by regenerating + committing 40. **CI's Gate 97 correctly rejected it** (`✗ COMMITTED index.html is structurally fresh … exit=1`): CI's clean checkout regenerates **38**. Root cause: `_count_dir(…, "files")` uses `rglob("*")`, which recurses into nested `__pycache__` dirs and counts `.pyc` bytecode — and this cloud environment had **2 stray `.pyc`** (from running the reference scripts) that are **gitignored repo-wide** and absent from CI's checkout. So main's 38 was correct; the staleness was never real. I reverted `index.html` to main's bytes.
- **Process note (honest, per this repo's own observation-vs-inference discipline):** my first pass stated "templates is genuinely 38→40" as fact — an *inference* from `find -type f → 40` without checking those 40 were git-**tracked**. The 2 untracked `.pyc` were the uncounted variable. The CI failure forced the re-derivation; the gate worked exactly as designed. (A second self-inflicted detour: when I *did* briefly apply the generator fix, the `format-on-write` hook auto-reformatted 425 lines of the file — finding RR-07 demonstrating itself — and the edit tripped the `islanded-panel-costs-two` concept-staleness gate because that concept `covers` the generator. Both are why RR-23 is routed, not applied.)

### RR-02 · P2 · `validate-marketplace.yml` `detect` filter let a lint-config-only PR merge green, then break `main`
- **File:** `.github/workflows/validate-marketplace.yml:124` (the `detect` job's `code` filter).
- **Cause:** the filter listed `**/*.json` (covering `.prettierrc.json`) but omitted `ruff.toml` and `.prettierignore` — both root lint-config files with no matching glob. A PR touching only those is misclassified "docs-only," skips the whole-tree Ruff/Prettier **suite jobs** (moved out of the always-on `core` job), merges green, then the post-merge push run goes red — blocking every subsequent PR. The `push:` trigger's `paths:` list already includes both files; the two lists had simply drifted.
- **Fix:** added `ruff.toml` and `.prettierignore` to the `code` filter, with a comment explaining the two lists must agree. (This is doctrine-aligned: a lint-config change is *not* docs-only. It does **not** re-add a `paths:` filter to a required trigger — Gate 242's concern is untouched.)

### RR-03 · P2 · `open-dashboard.sh` could announce/open the WRONG worktree's dashboard
- **File:** `scripts/open-dashboard.sh:212` (the post-spawn readiness loop).
- **Cause:** the reuse-probe (`find_our_live_port`) is `_is_our_dashboard`-guarded, but the **post-spawn** readiness loop accepted the first port in `8000..8010` that answered `/index.html`, regardless of which checkout served it. With another worktree's dashboard already on 8000, our new server binds 8001 and the loop still picks 8000 — so posture edits land in the wrong checkout's `.ravenclaude/`.
- **Fix:** the readiness loop now accepts a port only after `_is_our_dashboard` confirms it (reusing the existing two-part cmd+cwd check), with a first-answering-port **fallback** so a host without `lsof` still launches (degraded, as before). Verified `bash -n` clean.

### RR-04 · P3 · `check-github-status.sh` crashed on a `null` component list
- **File:** `scripts/check-github-status.sh:38`.
- **Cause:** `.get("affected_components", [])` returns `None` when the key is present but JSON-`null` (the default only applies when the key is *absent*) → `for c in None` raises `TypeError`. `incident_updates: [null]` has the same shape via `[0]`.
- **Fix:** `(((i.get("incident_updates") or [{}])[0] or {}).get("affected_components") or [])`. Verified: all three hostile null shapes now return cleanly (0 relevant); normal match/no-match unchanged (1/0). Zero behavior change for the normal path; could not confirm against the live API (githubstatus.com unreachable from this sandbox), so this is defensive hardening of a genuine latent crash.

---

## 👉 NEEDS YOUR DECISION (routed here, not auto-fixed)

Every item below is **real** (most reproduced by a reviewer), but was **not**
auto-fixed for one of these reasons, stated per-item:
- **substrate** — the file is under `plugins/ravenclaude-core/{hooks,scripts}/`, which the command-review tribunal protects category-independently (an agent write there is denied by `xc.tribunal-self-disable`; confirmed this run when a reviewer's own write was denied). These need you (the dashboard master-off, or an authorized session) — exactly the `pending-guard-destructive-merge-patch.md` precedent.
- **destructive + version-bump** — editing a plugin's destructive-op script also requires a semver bump + `sync-plugin-versions.py` (+ `generate-copilot-plugin.py` for core), handled with extra care here.
- **needs live data / cross-file design** — the fix depends on information I couldn't obtain this session (e.g. the live branch-ruleset contexts; `gh` token is invalid this session).

### 🔒 Security floor (Panel 1E — guard/sanitizer hooks) — recommend prioritizing

These are reproduced **fail-opens in the catastrophe-floor guard and the secret
scrubber**. All live in tribunal-substrate files, and `guard-destructive.sh` is
the guard this repo changes only via the sanctioned careful path (the
`pending-guard-destructive-merge-patch.md` + PR #1241 precedent) — so **none was
auto-fixed**. (Priority note: the reviewer rated these `major`→P1; a maintainer
may reasonably treat a catastrophe-floor bypass as P0 — flagged as a tie-break
for your call.)

> **De-fanged examples.** The attack strings below are rendered with the
> pipe-to-interpreter adjacency broken into prose ("piped to") and placeholder
> URLs, because the literal forms trip the very `sce.curl-pipe-shell` hard rule
> this section is about — the guard can't tell a command from a description of
> one (the repo's own `printf`-assembled-fixture convention, v0.242.0/v0.244.0).
>
> Caveat the reviewer stated and I confirm: a command-string scanner **cannot**
> catch variable-indirected targets (`x=/; rm -rf $x`), `xargs rm`, or
> brace-expansion obfuscation — the guard's own comments say so, and those were
> correctly *dropped*, not reported. The items below are forms the guard **does**
> intend to catch and currently doesn't.

#### RR-S1 · P1 · `guard-destructive.sh` — a wrapped/piped heredoc body is treated as inert, so a destructive body is never scanned *(substrate; reproduced)*
- **File:** `plugins/ravenclaude-core/hooks/guard-destructive.sh:170-186, 212-226` (`_heredoc_feeds_interpreter` / `_strip_heredoc`).
- **Finding:** the interpreter check only skips `VAR=` prefixes and a leading `env`. With a recursive-delete body (`rm -rf <root>` / `shutil.rmtree('/')`), **all** of these returned **rc=0 (ALLOW)**: a heredoc fed to `sudo sh`, to `sudo`/`nohup`/`time`/`exec`/`timeout` + `bash`, to `docker exec -i c bash`, to `sudo python3`; a `cat` heredoc **piped to** `bash` or `sh`; and a heredoc inside process-substitution / command-substitution fed to `bash`/`source`/`eval`. **Control:** a plain `bash` heredoc with the same body → rc=2 (deny). The stripper blanks the body — correct only when the heredoc is *data* (a `git commit -m` body, a cat-to-file) — in every case where it's actually *code* fed to an interpreter via a wrapper or pipe.
- **Proposed fix:** don't blank a heredoc body when the command contains any interpreter token (including after a pipe on the opening line, or inside process/command substitution); strip only for `git commit -m` and cat-to-file with no execution.

#### RR-S2 · P1 · a curl-to-shell install idiom with a wrapper evades the pipe-to-shell deny — across all three layers *(substrate; reproduced)*
- **File:** `plugins/ravenclaude-core/hooks/guard-destructive.sh:1902, 1908` (`deny_patterns`).
- **Finding:** the deny regex allows only a bare `sudo ` or `sudo env X ` before the interpreter, so a wrapper between the pipe and the shell is not matched. A `curl <url>` **piped to** `sudo -E bash` (the standard nodesource/installer idiom), or to `sudo -u root bash`, `doas sh`, `exec sh`, or `php`, all returned **rc=0**. The tribunal's `sce.curl-pipe-shell` catalog regex also requires `sudo` immediately before `sh`/`bash`, and `settings.json` denies only the bare-pipe literal — **so none of the three layers covers the wrapper form.**
- **Proposed fix:** allow arbitrary `-flag [arg]` tokens + a wrapper-command list between the pipe and the interpreter, or match any interpreter token that is the target of a pipe in a curl/wget chain. Apply symmetrically to the catalog regex (the repo's own v0.242.0/v0.244.0 force-push/curl-pipe lessons require fixing a class, not one instance).

#### RR-S3 · P2 · `guard-destructive.sh` whole-disk patterns have boundary + device holes *(substrate; reproduced)*
- **File:** `plugins/ravenclaude-core/hooks/guard-destructive.sh:1912-1916` (mkfs/wipefs/shred/dd).
- **Finding (each rc=0; the flagged control forms → rc=2):** a no-flag `shred` of a disk device (the pattern needs two spaces before `/dev/`); a `mkfs`/`wipefs` chained after `;`, `&&`, or inside `( )` (the boundary is `(^|space)` only, no `;&|(`); a path-qualified `/sbin/mkfs.*` or `/usr/sbin/wipefs` (no path-qualified match — the rm/find/truncate helpers already use `_CMD_BOUNDARY` for exactly this); and `dd … of=` a macOS raw disk (`/dev/rdisk*`), `/dev/mapper/*`, `/dev/md0`, `/dev/dm-0` (device-list gaps).
- **Proposed fix:** use `_CMD_BOUNDARY` for mkfs/wipefs, change shred to `shred[[:space:]]+([^;&|]*[[:space:]])?/dev/`, and extend the dd device alternation.

#### RR-S4 · P1 · the SH-F4 walk-up disables the tribunal / runaway-brake / DoD gate in a subdir with an empty `.ravenclaude/` *(substrate; reproduced)*
- **File:** `plugins/ravenclaude-core/hooks/thing-orchestrator.sh:136-164`; same pattern in `runaway-brake.sh:49-65`, `dod-gate.sh:48-65`, `guard-probe-validity.sh:~174`.
- **Finding:** the walk-up stops at the nearest ancestor merely **containing** a `.ravenclaude/` directory, even when that dir has no `comfort-posture.yaml` — then the posture check misses and the hook `exit 0`s (guard off). Reproduced on `runaway-brake.sh` with a root posture (`max_consecutive: 2`) and an empty `sub/.ravenclaude/`: cwd=root → rcs `[0,2,2,2]` (brake fires); cwd=`root/sub` → `[0,0,0,0]` (brake dead). Reached by `mkdir -p x/.ravenclaude && cd x`, or a consumer who commits `.ravenclaude/ledger` but not the posture (then a linked worktree has `.ravenclaude/` without the posture).
- **Proposed fix:** walk up to the nearest dir whose `.ravenclaude/comfort-posture.yaml` **exists**, then fall back to `CLAUDE_PROJECT_DIR`.

#### RR-S5 · P2 · the `thing:` fast short-circuit is case-sensitive and rejects quoted YAML booleans *(substrate; confirmed)*
- **File:** `plugins/ravenclaude-core/hooks/thing-orchestrator.sh:162`.
- **Finding:** the short-circuit grep misses `thing: True`, `On`, `Yes`, `ON`, `"on"`, `'true'` — all of which PyYAML parses as true. On a hand-edited posture the hook `exit 0`s, bypassing the self-disable and hard-rule floors too.
- **Proposed fix:** `grep -Eiq`, tolerate quotes + trailing comments, or parse with the engine.

#### RR-S6 · P2 · `_scrub.sh` misses common token prefixes — including this repo's own `ghu_` token *(substrate; reproduced)*
- **File:** `plugins/ravenclaude-core/hooks/_scrub.sh:45-73` (`_secret_patterns`).
- **Finding:** `_scrub_reason` returned **unredacted** for `ghu_`/`ghs_`/`gho_`/`ghr_` (only `ghp_`/`github_pat_` covered — and CLAUDE.md says this repo's `GITHUB_TOKEN` **is** a `ghu_` token), a `Bearer` authorization header, `ASIA…` AWS temp keys, `AWS_SECRET_ACCESS_KEY=…`, basic-auth-in-URL, `--api-key=…`, and `export OPENAI_API_KEY=…`. `_deny` echoes the blocked command to stderr/transcript and `_emit_hook_event` writes it to `hook-events.jsonl` — both through this scrub — so a blocked command carrying a `ghu_` token leaks it into local logs.
- **Proposed fix:** add `gh[ousr]_[A-Za-z0-9]{30,}`, `ASIA[0-9A-Z]{12,}`, `--api[-_]?key`, `Bearer`/`Authorization:` header patterns, and a generic `*_(KEY|TOKEN|SECRET)=value` pattern.

> **Coverage note:** Panel 1E completed **partially** — it fully reviewed
> `guard-destructive`, `thing-orchestrator`, `route-decision-review`,
> `guard-web-access`, `enforce-layout`, `dod-gate`, `runaway-brake`,
> `guard-memory-compaction`, `_scrub`, and the two sanitizers, and skimmed the
> rest. It did **not** finish `worktree-guard`, `guard-premise`,
> `guard-probe-validity`, or `workaround-exhaustion` — a known gap for the next
> sweep.

### High priority (non-security)

#### RR-05 · P1 · `cleanup-branches.sh` can corrupt a branch checked out in another worktree *(substrate + destructive)*
- **File:** `plugins/ravenclaude-core/scripts/cleanup-branches.sh:285`.
- **Finding (reproduced in a scratch repo):** the delete uses `git update-ref -d "refs/heads/$b" "$_tip"` — the low-level primitive, which **bypasses git's own "cannot delete a branch checked out in another worktree" safety** that `git branch -d` enforces. The script refuses `main`/`master`/current HEAD, but not a branch live in a *different* worktree. `--auto` deleted `agent/foo` while its worktree was live, leaving that worktree on an unborn branch; the next commit there became a disconnected root.
- **Why it matters here:** this repo uses worktrees heavily (`rcwt`, `worktree-new.sh`, `worktree-swarm.sh`), so "delete a branch another worktree holds" is a realistic path. `branch-hygiene.sh`'s own comment already shows the authors know worktree interaction matters.
- **Proposed fix (defensive precondition, consistent with the script's verify-then-delete design):** before the `update-ref -d`, check `git worktree list --porcelain` for the branch and add it to `verdict_unsafe` ("checked out in worktree <path>") if found elsewhere — mirroring what `git branch -d` would refuse.

#### RR-07 · P2 · `format-on-write.sh`'s `ruff --fix` deletes a just-added, not-yet-used import *(substrate)*
- **File:** `plugins/ravenclaude-core/hooks/format-on-write.sh:51`.
- **Finding (reproduced):** `ruff check --fix` on every write removes F401 unused-imports — so `import os\nx=1` becomes `\nx = 1`, and the agent's in-progress code hits a `NameError` once it uses `os`. A format-on-write hook that silently deletes in-progress code is a sharp-edge.
- **Proposed fix (your call — this is a policy decision):** either drop `--fix` for the unused-import rule family on write (format only, don't prune), or restrict `--fix` to safe formatting-only rules, or gate it behind an opt-in. The right answer depends on how aggressively you want write-time autofix.

### Medium priority

#### RR-06 · P2 · `archive-branch.sh --delete-remote` deletes origin without a tip-equality check *(substrate + destructive)*
- **File:** `plugins/ravenclaude-core/scripts/archive-branch.sh:329`.
- **Finding:** after a clean `git ls-remote` (exit-status-checked correctly), it runs `git push origin --delete "$BRANCH"` **without comparing the remote tip to the archived local `$TIP`**. If origin has commits the local branch lacks, `--delete-remote` removes them and the archive tag (cut at local `$TIP`) doesn't cover them → unrecoverable origin-only commits.
- **Proposed fix:** parse the SHA from `_remote_refs`, compare to `$TIP`, and **refuse** the remote delete (clear message, local branch already archived) when they differ — the same fail-closed shape the script already uses for the ls-remote failure case.

#### RR-08 · P2 · `gemini-hook-adapter.sh` silently bypasses the tribunal on a >128 KiB payload *(substrate)*
- **File:** `plugins/ravenclaude-core/hooks/gemini-hook-adapter.sh:125`.
- **Finding (reproduced):** `_normalise` passes the whole payload as a `python3` argv argument; Linux caps a single argv string at ~128 KiB (`E2BIG`), the exec fails, and the `&& return 0` guard falls through to the raw snake_case payload — so a Gemini `write_file`/`run_shell_command` with >128 KiB content reaches the orchestrator as an un-normalized tool name, hits the `*) exit 0` fall-through, and is **never reviewed** (the exact MH-01 silent-bypass the adapter exists to prevent — while the tribunal's own `SCREEN_MAX_BYTES` is 1 MiB).
- **Proposed fix:** don't pass the payload as argv (it's already on stdin — use an empty fallback), and on normalization failure for a *recognized* snake_case tool, prefer `exit 2` (fail closed) over pass-through.

#### RR-09 · P2 · `spectate-steer.sh` pause/note/approve/deny are dead on native Claude Code *(substrate)*
- **File:** `plugins/ravenclaude-core/hooks/spectate-steer.sh:86`.
- **Finding (reproduced + positive-controlled):** `event_key` is built only from `CLAUDE_HOOK_EVENT`/`$1`, which native Claude Code never sets (only the copilot/cursor/gemini adapters export it). The payload's `hook_event_name` is ignored — so Spectate's pause/note/approve-deny steering never fires on the primary host. (Positive control: the `claude` binary has 26 `hook_event_name` hits, 0 `CLAUDE_HOOK_EVENT`.)
- **Proposed fix:** add the payload fallback `spectate-emit.sh` already has — read `hook_event_name`/`hookEventName` from the payload before computing `event_key`.

#### RR-10 · P2 · `copilot-hook-adapter.sh` `bash-pretool` forwards Edit/Write/Read args un-normalized *(substrate; medium confidence)*
- **File:** `plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh:161`.
- **Finding:** Copilot's `{path, old_str, new_str}` are forwarded as-is; the tribunal reads `file_path`/`old_string`/`new_string`, so it reviews an empty path and empty content. Related to the v0.311.1 tool-name-map work. **Confirm the Copilot field names against a live payload before fixing** — the names came from a leaked-prompt research note, not a verified payload.

### Low priority (P3)

| id | file:line | finding | repro |
|---|---|---|---|
| RR-11 | `spectate-emit.sh:44` *(substrate)* | whole payload exported as an env var; >128 KiB → `execve` `E2BIG` → event silently dropped (and steer pause not enforced for a large PreToolUse) | ✅ |
| RR-12 | `copilot-hook-adapter.sh:187` *(substrate)* | only `bash-pretool` mode doesn't export `CLAUDE_PROJECT_DIR` from the payload cwd → `hook-events.jsonl` never written, though the deny reason points to it | ✅ |
| RR-13 | `conserve-tokens.py:310` *(substrate)* | `changed = engaged != prev or not state` → spurious "CONSERVE TOKENS released/engaged" on the first prompt of every session (asserts a transition that never happened) | ✅ — **observed firing during this very run** |
| RR-14 | `stream-session-close.sh:69` *(substrate)* | registered on `Stop` (per-turn), so it appends a `session_closed` event + rewrites `state.md` every turn, not once per session; counts inflate | ✅ |
| RR-15 | `mark-web-domain-seen.sh:76` *(substrate; security-adjacent)* | host normalization diverged from `guard-web-access.sh` (SH-F2 hardening not mirrored): first-use consent keyed on the wrong host, and `https://evil.test?x=@good.com` marks `good.com` as already-seen | ✅ |
| RR-16 | `triage-outcome.sh:219` *(substrate)* | posture lookup uses the payload cwd, not the project root → triage goes inert after a `cd` into a subdir | code-read (live run refused by a safety check) |
| RR-17 | `remind-tests.sh:50` *(substrate)* | source-change detection misses a new untracked *directory* of files and paths with spaces → the test reminder never fires for new-module work | ✅ |
| RR-18 | `agent-dispatch-evaluator.sh:195` *(substrate)* | classifier uses `claude -p --bare` unconditionally; `--bare` fails for subscription/OAuth logins, so the shadow audit records nothing for those users | — |
| RR-19 | `dashboard-autostart.sh:87` *(substrate)* | launcher defaults to `${CLAUDE_PLUGIN_ROOT:-}/bin/rc` = `/bin/rc` under the dev-mirror registration → silent exit, though this repo has `dashboard_autostart: open` | code-read |
| RR-20 | `atlas-watch.yml:117` + `assert-not-required-check.sh:67` | the guard `grep -Fqi`s a workflow-name string ("Atlas watch") against ruleset check contexts, which are *job* names ("Re-fetch the cited vendor pages and compare") → it can never match for atlas-watch / golden-set-inject / inventory-sweep, so it **fails open**. Fix needs the live ruleset's exact context strings (gh token invalid this session) or a cross-workflow convention decision. | — |
| RR-21 | `spectate-steer.sh:218` *(substrate; inference)* | the steer note is emitted without `hookEventName` and consumed before emit → lost if the host rejects the envelope | inference |
| RR-22 | `keep-awake.sh:133` *(substrate; low confidence)* | `pgrep -f "caffeinate -s -w $PID"` is an unanchored substring → pid 432 matches an existing `caffeinate -w 4321` | inference |

---

#### RR-23 · P3 · `generate-index-dashboard.py` `_count_dir` counts gitignored `__pycache__/*.pyc` → a local-regeneration footgun *(root script; verified patch, NOT applied here)*
- **File:** `scripts/generate-index-dashboard.py` `_count_dir()` (~line 522): `return sum(1 for p in path.rglob("*") if p.is_file())`.
- **Finding:** `rglob("*")` recurses into nested `__pycache__` dirs, so a working tree where a plugin's template/reference script has been executed over-counts that plugin's `templates` by the number of `.pyc` present. The committed `index.html` then reads STALE on that machine — **it bit this very run** (RR-01). CI's clean checkout has no `__pycache__` (gitignored repo-wide), so the committed artifact is correct and CI is unaffected — the gate works as designed. A *local* footgun, not a CI bug.
- **Proposed fix (verified locally, not applied):** `return sum(1 for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts)` — provably a no-op on any clean/committed tree (nothing commits `__pycache__`); it only stops a dirty tree from over-counting. Verified: `check-artifact-freshness --check --surface index.html` passes even with the stray `.pyc` present.
- **Why routed, not fixed:** `generate-index-dashboard.py` is `covered` by the `islanded-panel-costs-two` concept entry, so editing it trips `concepts.py --check` (covers-digest drift) and must be paired with `scripts/concepts.py --restamp-cosmetic islanded-panel-costs-two` in the same change. That's a deliberate, sanctioned step best done attended — I kept this autonomous PR minimal rather than chase the freshness cascade blind.

## Tie-break notes (Panel 3)

- **RR-05 (P1 vs P2):** called **P1**. It's reproduced and causes real branch/worktree corruption with no error; the only thing holding it below P0 is that it needs concurrent worktree use (common here) and isn't data-*loss* (the commits survive as a dangling ref until gc).
- **RR-02 (P1 vs P2):** called **P2**. Blast radius is large (red `main` blocks every PR) but the trigger is narrow (a lint-config change that newly-flags existing code, then merged). Fixed anyway — it's a 2-line safe fix.
- **RR-06 (P2 vs P3):** called **P2** despite being lower-probability than RR-05, because the failure mode is true data-loss (origin-only commits, no recovery anchor) rather than recoverable corruption.

## Deliberately NOT flagged (cleared, so you don't re-investigate)

- Non-executable `plugins/ravenclaude-core/hooks/tests/*.sh` — invoked via `bash …`, never `./…`, and the CI exec-bit check uses shell globbing that doesn't cross `/`. Not a defect.
- `notify.sh` (jq-escaped payload, bounded curl, URL never logged), `worktree-clean.sh`, `ensure-plugin-installed.sh`, and the `check-*/spike-*/premerge/regen` scripts — reviewed, no real bug.
- 15 lifecycle/adapter hooks in group C and several `handoff-tax-meter.sh`/`precompact-digest.sh` SIGPIPE/`set -e` candidates — checked and dropped as false alarms by the reviewers.

## Scope & honesty

- **Executable surface only.** Panel 1 covered the CI workflows, the 59 guardrail hooks, and the 24 root shell scripts — where real logic/security bugs live. The ~7,800 markdown files (agent/skill/knowledge prose) are human-reviewed content, not a bug surface, and were not swept. The ~500 Python files are mostly self-tested gate-checkers (the `audit-gates.sh` meta-test proves each); they were not individually reviewed this run.
- **The enforcement/guard-hook security panel (Panel 1E)** is appended below if it completed; if this section is missing or marked incomplete, that panel did not finish within its budget and is a known gap for the next sweep.
