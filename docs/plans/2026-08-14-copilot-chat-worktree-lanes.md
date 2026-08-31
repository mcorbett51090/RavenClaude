> **Leftover (phases 6–7) forged 2026-08-14:** see [`2026-08-14-chat-write-deny.md`](2026-08-14-chat-write-deny.md). Phase 6 remains a documented no-op (CL-3 / CL-19b still owner-gated). Chat is **not** claimed as protected.

<!-- Landed by FORGE G8 2026-08-14. Canonical run artifacts remain in `.ravenclaude/runs/forge/copilot-chat-worktree-lanes/` (gitignored). G7: execution=use_local landing=pr. Do not treat this as Chat-is-protected. -->

# Copilot Chat worktree-lane isolation — merged plan (G6)

**Run:** `forge/copilot-chat-worktree-lanes`
**Gate:** G6 Synthesize (A write-teeth + B lane/operator default; G3b owner-gate is law)
**Owner folder:** `plugins/ravenclaude-core` (hooks, templates, knowledge, best-practices, `bin/rcwt`, skills) plus installer / dashboard generators only where a new knob or honesty sentence must round-trip
**Ship shape:** markdown + shell + JSON. No new plugin. No new skill or agent (G8 regen not required). Sleipnir stays a label.
**Landing:** PR `feat/ravenclaude-core-worktree-bound` (plugin + installer-adjacent). Not docs-straight-to-main.
**Semver:** `ravenclaude-core` `0.266.0` → `0.268.0` (0.266.0 landed as session-handoff #931; 0.267.0 is claimed by open PR #928 webfetch — stay out of that lane). CHANGELOG exists — write a new `0.268.0` top entry. Do not invent missing backfill.

Claims authority: `claims-table.md` CL-1..CL-20. Inferences CL-3 and CL-19 are **owner-gated** (G3b 2026-08-14). They are not disconfirmed; they are not product facts. No phase in the `0.256.0` PR may claim "Chat is protected" or ship a Chat write-deny as the reason for the bump.

---

## 0. Owner questions (G3b — do not skip)

These are the only remaining BLOCK inferences. They cannot be settled in this CLI session.

1. **CL-3.** In VS Code Copilot Chat Agent mode, with the window opened only on worktree A, ask the agent to Write an **absolute path** under sibling worktree B. What happens: keep / undo / approval dialog / no-op? Record the transcript (redacted) as `.ravenclaude/runs/forge/copilot-chat-worktree-lanes/probe-cl3.md`.
2. **CL-19.** With projected `.github/hooks` present and `chat.hooks.enabled` on, does one Chat tool call produce a PreToolUse stdin payload that `worktree-guard.sh` understands (fields: `session_id` or `sessionId`, `cwd`, tool name, a file-path field)? Dump one payload (redacted) as `probe-cl19.md`. Bonus: after SessionStart, does `~/.ravenclaude/worktree-guard/sessions/<path_key>/` gain a Chat session file with a non-`unknown` id (CL-10 + CL-19)?

Until both rows exist, Chat hook teeth and Chat sibling-Write product behavior stay `[unverified — premise not disconfirmed: G3b owner-gated 2026-08-14]`. FOREIGN-TREE for Claude / Copilot CLI / Codex / Gemini, and the observed context-bleed close, do **not** wait on these answers.

---

## 1. Diagnosis (mechanism, not symptoms)

The observed failure is **context bleed in VS Code Copilot Chat**. It is not a shared CLI hook, not a shared committed `AGENTS.md` (CL-20, intended), and not a second git object store (CL-17, given).

Three distinct mechanisms. Only the first is observed today. The second is a **named hole** in a hook this marketplace already projects.

| Lane | Mechanism | Why the current guard misses it |
|---|---|---|
| **Context** (observed) | Chat view is scoped to **that window's opened folder** (CL-1, CL-4). The Agents window + Agent Host **share sessions across workspaces** (CL-4). A multi-root window with two worktree folders is **one context pool** — search / `#codebase` / open editors / conversation all see both (CL-5, CL-20). | `worktree-guard.sh` never inspects Read / open-editor / conversation. CONTENTION is two-writers-one-tree, not one writer reading another tree. Selling a green CONTENTION check as Chat isolation is a false claim. |
| **Write** (forward) | Chat **built-in** file tools are **not** OS-sandboxed (CL-2). Sibling-path Write is **undocumented** (CL-2 silence). Terminal sandbox, when on, limits writes to cwd+subdirs and is **off by default** (`chat.agent.sandbox.enabled`). Whether Chat will actually land a sibling Write is CL-3, owner-gated. Independently of Chat: this repo's hook already has a hole. | `_wg_is_mutating` in `hooks/worktree-guard.sh` L290–293: a `Write\|Edit\|MultiEdit` whose `file_path` is **not** under `REAL_TOP` returns 1 (not mutating) and is **allowed even in `worktree_guard=block`**. A sibling-worktree absolute Write is therefore a silent allow. G3b 2026-08-14 observed this control. This is a defect on every hooked host (Claude, Copilot CLI, Codex, Gemini), not a Chat-only theory. |
| **Git** (forward) | Worktrees share refs + objects; they do **not** share index / `HEAD` (CL-17). `git checkout` already refuses a branch checked out elsewhere. Confusion is cwd / `git -C <sibling>` / committing in the wrong window. | Guard detects two writers in one `realpath(toplevel)` (CONTENTION) or anchor-work on primary (ANCHOR). It does not bind a session to its registered toplevel against a `git -C` / `GIT_WORK_TREE` escape. |

The closest shipped enforcement — `hooks/worktree-guard.sh` (SessionStart `register` + PreToolUse `check`) — is the right **script** and the wrong **clause set**. Copilot CLI already projects this hook (`generate-copilot-hooks.py` `_SKIP` does not include it; CL-8). Claude / Codex / Gemini already fire the same script through native / shim / adapter paths. VS Code Chat **Preview** *can* load the same `.github/hooks` **if** org policy / `chat.hooks.enabled` allows it (CL-7 observation; CL-19 inference, owner-gated). This worktree currently has **no** `.github/hooks/` directory, so even a Preview-on Chat has nothing to fire here until the Copilot installer projects hooks.

So the close is dual-track, not either/or:

1. **Operator default (observed leak):** one VS Code window per worktree; never multi-root two worktrees; never hop Agents-window sessions; a durable `.ravenclaude/lane.md` stamp so hosts without SessionStart injection still see the lane.
2. **Mechanical bound (forward write/git, already-hooked hosts):** a third clause `FOREIGN-TREE` that denies any mutating tool whose target path or git cwd resolves to a different listed worktree than this session's `realpath(toplevel)`, behind a new scalar `worktree_bound` default **block**.

Do not add a plugin. Do not fork `AGENTS.md` per tree. Do not sell CONTENTION as Chat context isolation. Do not ship a version-bump that asserts Chat enforcement.

---

## 2. Alternatives (keep ≥2, then pick)

| ID | Approach | Trade-off |
|---|---|---|
| **A. Mechanical bound only** | Third clause in `worktree-guard.sh` (`FOREIGN-TREE`) + `worktree_bound: block`. Same knob idiom. | Closes the named mutating-path hole on every hooked host. Does **not** stop Agents-window session share or a human adding a second folder. Chat write-deny still depends on Preview hooks (CL-19). |
| **B. Workflow-first only** | `rcwt` opens a dedicated window (`code -n`), writes `.ravenclaude/lane.md`, documents hard rules. No hook change. | Strongest on the **observed** context class; host-honest when Chat hooks are off. Leaves the `_wg_is_mutating` sibling-Write hole open on Claude / Copilot CLI / Codex / Gemini — a known defect in an already-projected script. |
| **C. Instruct-only / docs-only** | Host table + Chat knowledge file. No `rcwt` change, no hook change. | Zero runtime blast. Every operator rediscovers the layout. Does not close sibling Write. Fails G0's "named guard or explicit cannot" success signal for write. |
| **D. New hook script / new plugin / Sleipnir component** | Dedicated `worktree-bound.sh` or a new marketplace plugin. | Cleaner separation, but G0 forbids a new plugin / Sleipnir component, and a second PreToolUse on every Write is the R-9 cost this repo already flagged. |

**Pick A+B together (gap-delta §12).** Observed failure is context → B's operator default and lane stamp are the primary Chat close. Named write hole is already in a projected hook → A's FOREIGN-TREE is the primary write/git close on hooked hosts, same PR if the test file stays maintainable. C is rejected as "please don't." D is rejected by G0 and R-9.

Why not flip `worktree_guard` default from `warn` → `block`: that would start denying **CONTENTION / ANCHOR** mutating ops for every consumer, a different and noisier contract. FOREIGN-TREE is never a preference — leaving your tree is a defect — so it gets its **own** scalar, default **block**. `worktree_guard` stays `warn`.

Why not wait for CL-3/CL-19 before FOREIGN-TREE: G3b reshape is explicit. FOREIGN-TREE for Claude / Copilot CLI / Codex / Gemini does not rest on those inferences. Waiting would leave a documented hole open for no reason.

---

## 3. G3b reshape (law — how this plan is capped)

| Rule | Consequence in this plan |
|---|---|
| CL-3 and CL-19 are owner-gated | Phase 0 records the probes. No other `0.256.0` phase cites 3 or 19 as a shipping premise. |
| A phase that would claim "Chat is protected" or ship a Chat write-deny as a version-bump is capped to **one reversible file** and **feature-flagged** | That file is `plugins/ravenclaude-core/templates/worktree-lane/chat-ceiling.md` (probe checklist + optional sandbox snippet + explicit "this is not Chat enforcement"). `rcwt` merges the sandbox key only when `RCWT_CHAT_CEILING=1`. CHANGELOG / host-support / isolate-parallel **must not** say Chat is protected. |
| FOREIGN-TREE for Claude / Copilot CLI / Codex / Gemini may proceed | Phase 1. Does not rest on CL-3/19. |
| Observed context-bleed close proceeds | Phase 2 (one folder per window, no Agents-window hop, no two-worktree multi-root, lane stamp, SessionStart lane banner when hooks fire). |
| Carry every `[unverified]` with the step that settles it | See §10. |

Verified this session (dashboard host matrix): `scripts/generate-dashboards.py` L13750–13776 iterates `Object.keys(data.hosts)` and looks up `comp[h]`. A missing cell renders "no", so a new top-level host key is *mechanically* safe — but it would look like a fifth install target. **Do not add `copilot-chat` as a `hosts` key.** Keep `copilot.label` = `"GitHub Copilot CLI"` (CL-11). Chat honesty is a caveat + nested `surfaces` note + a new knowledge file.

---

## 4. Phased plan

### Phase 0 — Owner-gate probes + the one reversible Chat ceiling file

- **goal:** Settle CL-3 and CL-19 on the owner's VS Code, or leave them explicitly unverified. Ship exactly one reversible Chat-adjacent file so later docs have a place to point without claiming enforcement.
- **files:**
  - **local-run only** (gitignored `.ravenclaude/runs/`): `probe-cl3.md`, `probe-cl19.md` (payload dump, redacted).
  - **one reversible shipped file:** add `plugins/ravenclaude-core/templates/worktree-lane/chat-ceiling.md` — dated probe checklist (the two owner questions in §0), the optional settings snippet `{"chat.agent.sandbox.enabled": true}`, and a bold honesty line: sandbox does **not** cover built-in file tools (CL-2); Preview hooks are **not** claimed on (CL-7 + `[unverified]` CL-19). Feature flag: `rcwt` reads `RCWT_CHAT_CEILING=1` before merging that sandbox key; default is off.
- **acceptance tests (falsifiable):**
  1. `chat-ceiling.md` contains the strings `CL-3`, `CL-19`, and `not Chat enforcement` (or equivalent "not protected").
  2. `rg -n "Chat is protected|Copilot is protected" plugins/ravenclaude-core/templates/worktree-lane/` → 0 matches.
  3. After probes: `probe-cl3.md` and `probe-cl19.md` have dated keep/undo/payload rows, or a dated `skipped — owner not available` line. Either is a pass for this phase; a skip leaves Chat cells `[unverified]`.
- **pre-build gates:** none for the local-run probes. `python3 -m json.tool` on any JSON fenced in `chat-ceiling.md` if a raw snippet is included as a `.json` sibling later. Layout glob `plugins/*/templates/**` already allows the new dir.
- depends_on_claims: [3, 7, 10, 19]
- **blast radius:** one new template file + local-run notes. No plugin version bump **as Chat enforcement**. This file may ride in the `0.256.0` PR only as a checklist / optional snippet, never as the reason the version exists.

---

### Phase 1 — FOREIGN-TREE clause (write + git escape deny on hooked hosts)

- **goal:** The session's registered `realpath(git rev-parse --show-toplevel)` is the **only** allowed write root among this repo's listed worktrees. A Write / Edit / MultiEdit / Bash `git -C` / `GIT_WORK_TREE` / `cd` that resolves into **another** `git worktree list` path is denied. This closes the current hole: sibling Write is classified as non-mutating and sails through. This phase is **not** a Chat product claim.
- **files to edit:**
  - **edit** `plugins/ravenclaude-core/hooks/worktree-guard.sh`
    - New clause `_wg_is_foreign()`: target realpath is under some `git worktree list --porcelain` `worktree ` entry whose realpath ≠ `REAL_TOP`.
    - Target extraction (in addition to today's `tool_input.file_path`): `tool_input.path`, and from Bash `command` the tokens `-C <dir>`, `--git-dir=`, `--work-tree=`, `GIT_WORK_TREE=`, `GIT_DIR=`. Do **not** invent Chat tool names; Chat names enter only after `copilot-hook-adapter.sh` (already lifts `sessionId // session_id`, `file_path // path // filePath`, `create→Write`, `edit→Edit`).
    - **Do not** deny `/tmp`, `$TMPDIR`, or paths outside every listed worktree — those are other hooks' jobs (layout, destructive). FOREIGN-TREE is **sibling-worktree only**, not a general jail.
    - Sibling set = every porcelain `worktree ` line whose `realpath` ≠ `REAL_TOP`. A path is foreign if `realpath` of the nearest existing ancestor (same walk as `_wg_path_under_tree` L262–282) is equal to or under any sibling.
    - New knob `worktree_bound: off|warn|block` in `.ravenclaude/comfort-posture.yaml`, **default `block` if the key is absent** (leaving the tree is never a preference). Independent of `worktree_guard` (stays `warn`; CONTENTION/ANCHOR unchanged).
    - Escape: `RC_WORKTREE_BOUND_ACK=1` (do **not** overload `RC_WORKTREE_GUARD_ACK` — that is the two-writers hatch).
    - `off` short-circuits FOREIGN-TREE only; does not disable CONTENTION/ANCHOR.
    - **Control-flow rewrite (load-bearing):** today's early exit (`worktree-guard.sh` L75–78) is `if mode=off and not status → exit 0`. That would disable FOREIGN-TREE whenever `worktree_guard` is off. Split it: parse both knobs; if **both** are `off` and subcommand is not `status`, exit 0; otherwise skip only the clauses whose knob is `off`.
    - v1: foreign **mutating** ops only. Matchers are ignored in Chat (CL-7), so `check` will run on Read/Grep if Chat Preview ever fires — those must **allow** (do not deny sibling Read in v1). Foreign Write/Edit/MultiEdit **is** mutating-for-bound (this inverts the hole). Unknown tool + no resolvable path → allow (fail-open); if the adapter already stderr-logs unmapped names, keep that.
    - `register` SessionStart: if other worktrees exist, emit `additionalContext` **lane pin** (always, not only on contention): `LANE: toplevel=<REAL_TOP> branch=<HEAD> host=<hostname> siblings=<n>`. If `$REAL_TOP/.ravenclaude/lane.md` exists, append `task=<value>`. This is the context-isolation floor that works even when Read cannot be denied, **on hosts whose SessionStart fires**.
    - `status --json`: add `worktree_bound`, `foreign` (bool), `siblings` (count). Keep `schema_version: 1` and **add** fields (additive). Dashboard reader already fail-opens on extra keys (`serve-dashboards.py` `_read_worktree_guard`).
    - Fail-open unchanged (missing git/jq/shasum → exit 0). Portability unchanged (bash 3.2 / BSD-safe, `set -uo pipefail`, no `declare -A` / `mapfile` / `grep -P`).
  - **edit** `plugins/ravenclaude-core/hooks/hooks.json` — update the two `comment` strings (PreToolUse `check` ~L113, SessionStart `register` ~L229) to name the third clause + `worktree_bound`. **No new hook entry** (same `check` / `register` commands). R-9: no sixth PreToolUse process.
  - **edit** `plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml` — document + default `worktree_bound: block` next to the existing `worktree_guard: warn` block (L22–36).
  - **edit** `plugins/ravenclaude-core/dashboard-schema.json` — new `worktree_bound` key (`off|warn|block`, default `block`), Settings-only like `worktree_guard` (schema around L221–227). No new Pipeline stage card.
  - **edit** `scripts/generate-dashboards.py` — three mechanical slots, or a dashboard Save will silently drop the key (v0.61.0 data-loss class; same reason `dashboard_autostart` has a state slot with no DOM toggle, L8099–8105):
    1. `WORKTREE_BOUND_VALUES` / `WORKTREE_BOUND_DEFAULT = "block"` next to L8097–8098.
    2. `state.worktree_bound` in the state object (~L8192) + hydrate from `src.worktree_bound` (~L8602).
    3. `emitYaml` writes the key only when it differs from default `block` (~L8756).
    4. One description string in the skip-map next to `"worktree-guard.sh"` (L1096–1097) naming the third clause.
    Regenerated `dashboard.html` is a consequence, not a hand-edit.
- **acceptance tests (falsifiable):** extend `hooks/tests/test-worktree-guard-core.sh` (T1–T7 stay) and `hooks/tests/test-gate140-worktree-guard.sh` (F1/F2/P1–P3 stay). Do not invent a third test file unless the existing ones exceed maintainability.
  - **T8 / F3:** two-worktree fixture; session cwd = sibling A; `Write` absolute path under sibling B → `worktree_bound=block` → **exit 2**. Same payload with `worktree_bound=warn` → exit 0 + stderr mentions `FOREIGN` / sibling. `worktree_bound=off` → exit 0, no stderr.
  - **T9 / P4:** same fixture; `Write` under A (this tree) → exit 0 (solo silence preserved).
  - **T10:** `Write` to `/tmp/rc-wt-probe` → exit 0 (not a listed worktree).
  - **T11:** Bash `git -C <B> commit` from cwd A → exit 2 when bound=block.
  - **T12:** `RC_WORKTREE_BOUND_ACK=1` + Write to B → exit 0.
  - **T13:** `worktree_guard: off` + `worktree_bound: block` + Write to B → still exit 2 (knobs independent; this is the early-exit rewrite test).
  - **T14:** lone checkout (no other worktrees) + Write under tree → exit 0 (FOREIGN cannot fire).
  - **T15:** `GIT_WORK_TREE=<B> git add -A` from cwd A → exit 2.
  - **T16:** `git status` (no `-C`) from A → exit 0.
  - **Teeth half (Gate 140 style):** show **before** the patch that today's `_wg_is_mutating` + Write-to-sibling exits 0 in `block`; **after**, exit 2. That is the hole proof.
  - Existing T1–T7 and Gate 140 F1/F2/P1–P3 **must stay green**.
- **pre-build gates:** `bash -n` the hook; `bash plugins/ravenclaude-core/hooks/tests/test-worktree-guard-core.sh`; `bash plugins/ravenclaude-core/hooks/tests/test-gate140-worktree-guard.sh`; `scripts/audit-gates.sh` Gate 140; `python3 -m json.tool` on `hooks.json` + `dashboard-schema.json`; `npx --yes prettier@3.9.4 --check` on touched JSON; `ruff check scripts/generate-dashboards.py` (and `python3 -m ruff` if `ruff` is not on PATH).
- depends_on_claims: [2, 8, 10, 12, 14, 16, 17]
- **blast radius:** one existing hook + posture template + dashboard schema/state/emitYaml. **No new module. No new PreToolUse process.** Consumers who never write a sibling path see no new stderr. Consumers who do get a deny by default. `worktree_guard: warn` behavior for two-writers-one-tree is unchanged. Codex consumers must `/hooks` after this byte change (hash-trust, CL-14) — Phase 4 names that. Chat is **not** in this phase's success signal.

---

### Phase 2 — Lane identity + one-window operator default (observed context close)

- **goal:** The correct Chat layout is what `rcwt new` produces. One opened folder = one worktree. A named lane stamp is readable without hooks. Multi-root-as-two-worktrees is an anti-pattern, never a generated layout.
- **files:**
  - **add** `plugins/ravenclaude-core/scripts/write-lane-stamp.sh` — bash, `set -euo pipefail`, shared writer for `rcwt` and the new-worktree skill. Args: dest path, task, branch, created_by. Writes `$dest/.ravenclaude/lane.md`:
    - YAML-ish header fields: `task`, `branch`, `worktree_path` (realpath), `created_at` (ISO), `created_by`
    - Hard-rules block (verbatim, so instruction surfaces can quote it):
      - This session's write root is **this worktree only**.
      - Do **not** open a sibling worktree as a second folder in this window (multi-root = context pool — CL-5).
      - Do **not** continue an Agents-window session that was started for another workspace (CL-4).
      - Prefer a **new Chat session** when switching windows/worktrees.
      - Shared committed `AGENTS.md` is intentional; ignore other trees' dirty files / `.ravenclaude/runs/<other-task>/`.
  - **edit** `plugins/ravenclaude-core/bin/rcwt` (`new` branch, L73–83):
    1. After successful `git worktree add`, call `write-lane-stamp.sh "$dest" "$task" "$branch" rcwt`.
    2. Change `code "$dest"` to `code -n "$dest"` (new window; B's stricter default — do not rely on `code` happening to open a new window).
    3. Print: `LANE window: $dest  (do not add another worktree folder to this window)`.
    4. Merge **only** the CL-6-backed parent-walk pin into `$dest/.vscode/settings.json` with the **same non-destructive add-absent-keys** Python as `skills/terminal-status-indicators/setup-terminal-indicators.sh` L68–107 (copy the 15-line merge; do not shell-`jq` mutate JSON): `{"chat.useCustomizationsInParentRepositories": false}`. Pinning a default-off setting prevents a user from turning parent-walk bleed back on.
    5. Do **not** merge `chat.agent.sandbox.enabled` here unless `RCWT_CHAT_CEILING=1` (Phase 0 feature flag). Default off.
  - **add** `plugins/ravenclaude-core/templates/worktree-lane/settings.json` — the parent-walk pin only:
    ```json
    {
      "chat.useCustomizationsInParentRepositories": false
    }
    ```
    Honest comment lives in `templates/worktree-lane/README.md` (not in the JSON): one screen — open **this folder only**; do **not** `Add Folder to Workspace` a sibling; do **not** hop sessions in the Agents window; sandbox (if the operator later sets the flag) does **not** cover built-in file tools.
  - **edit** `plugins/ravenclaude-core/skills/new-worktree/SKILL.md` — one short **"Peer-process / IDE"** subsection after the existing Procedure: after create, write the lane stamp (same helper), open a **dedicated** VS Code window (`rcwt` / `code -n <path>`); never add it as a second folder in an existing window. Do **not** restyle the skill's existing sub-agent procedure.
  - **edit** `plugins/ravenclaude-core/skills/cleanup-worktrees/SKILL.md` — one bullet: close the VS Code window / end the Chat session for that lane before `worktree remove`.
  - **edit** marketplace `.gitignore` — add `.ravenclaude/lane.md` so a stamp written in this checkout (or any consumer who copies the ignore) stays local. Consumer note in the lane README: the stamp is tree-local identity, not constitution; do not commit it; do not rewrite root `AGENTS.md` to name one task (CL-20).
  - **do not** add a committed `.vscode/` to the marketplace checkout (already gitignored; layout allow-list has no `.vscode/**` at repo root). Consumer `.vscode/settings.json` is written **inside the worktree** at create time.
  - **do not** ship a multi-root `*.code-workspace` that lists two worktrees. If a helper is ever added, it is a **single-folder** `.code-workspace` whose `"folders"` has length 1. Multi-root-as-two-worktrees is a **context-bleed layout** (CL-5), not a guard.
  - **do not** permanently rewrite committed `.github/copilot-instructions.md` or `AGENTS.md` to name one task. Lane identity is the stamp + SessionStart banner (Phase 1 `register`) + operator layout.
- **acceptance tests (falsifiable):** new `plugins/ravenclaude-core/hooks/tests/test-rcwt-lane-settings.sh` (no `test-rcwt` exists today; a focused script is honest):
  1. `rcwt new` in a temp repo → `$dest/.ravenclaude/lane.md` contains path + branch + the anti-multi-root rule string.
  2. Re-run after the consumer set `"chat.useCustomizationsInParentRepositories": true` → merge **does not overwrite**.
  3. With a stub `code` on PATH that records argv → invocation contains `-n` and the dest path.
  4. Absent `RCWT_CHAT_CEILING` → `$dest/.vscode/settings.json` does **not** contain `chat.agent.sandbox.enabled`.
  5. `RCWT_CHAT_CEILING=1` → sandbox key is added (Phase 0 flag).
  6. `jq '.folders | length'` if we ever emit a `.code-workspace` → `1`.
  7. Manual (Chat, owner): open the window `rcwt` created; Chat view `@workspace` must not list the sibling worktree's dirty files. Adding the sibling as a second folder **must** be documented as the self-inflicted bleed (cannot be hook-denied inside VS Code's workspace model).
- **pre-build gates:** `python3 -m json.tool` on the snippet; `bash -n` on `rcwt` and `write-lane-stamp.sh`; executable bit preserved on both; layout globs already allow `plugins/*/templates/**`, `plugins/*/bin/**`, `plugins/*/scripts/**`, `plugins/*/skills/**`. No `.repo-layout.json` edit.
- depends_on_claims: [1, 4, 5, 6, 17, 18, 20]
- **blast radius:** `rcwt` default create path for every consumer of the binary; skill prose; one helper script; one gitignore line. Marketplace checkout gains **no** `.vscode/`. Consumer worktrees gain an untracked lane stamp + optional local settings only when they run `rcwt new`. Medium — this is the observed-leak close.

---

### Phase 3 — Host-honest map (Chat ≠ CLI; no "Chat is protected")

- **goal:** Stop the false-equivalence "Copilot CLI hooks = Chat protected." Name Chat as a distinct surface with an explicit enforcement ceiling. House rule for every sentence in this phase: **do not sell CONTENTION as context isolation.**
- **files:**
  - **add** `plugins/ravenclaude-core/knowledge/copilot-chat-customization.md` — VS Code Chat surface only. Mirror the honesty style of `copilot-cli-customization.md`; **do not merge** the two files (CLI ≠ Chat). Required sections, each with a 2026-08-14 source or a this-session path:
    - Instruction load (CL-6)
    - Preview hooks (CL-7) + org-disable + matchers ignored
    - Agents window vs Chat view + session share (CL-4)
    - Multi-root = bleed (CL-5)
    - Lane workflow (pointer to Phase 2 + isolate-parallel)
    - Ceiling table (write / context / git) with `[unverified]` on live Preview fire and sibling built-in Write
    - Explicit: shared `AGENTS.md` is intended (CL-20)
  - **edit** `plugins/ravenclaude-core/knowledge/copilot-cli-customization.md` — one paragraph: Chat is a separate product; see the Chat file. CLI projection is not Chat coverage.
  - **edit** `plugins/ravenclaude-core/knowledge/host-support.json`:
    - Keep host key `copilot` label **"GitHub Copilot CLI"** (CL-11). Bump `"updated"` to the ship date.
    - **Do not** add a top-level `copilot-chat` host (dashboard iterates every `hosts` key as an install column).
    - Append to `hooks.copilot.caveat`: CLI projection ≠ Chat Preview; Chat is Preview + org-disable + matcher-ignored (CL-7); live fire on this machine is `[unverified]` until Phase 0.
    - Optional nested object `hooks.copilot.surfaces.chat` (or top-level `notes.copilot_chat`) with `supported` **false** or `basis: docs-verified only` until Phase 0 says otherwise. Preferred `supported` value in `0.256.0`: do **not** flip to true on a guess.
  - **edit** `plugins/ravenclaude-core/best-practices/isolate-parallel-claude-instances-in-git-worktrees.md` — **keep the filename** (avoid broken links; rename is a separate docs-only PR if wanted). **Keep** the Claude-native `--worktree` / `claude agents` block. **Add** a dated "Other supported hosts" / "Operator layout (all hosts)" table. One row per surface in §6. Explicit: Sleipnir remains labeling only. Explicit: CONTENTION is two-writers-one-tree, not Chat context isolation.
  - **edit** root `AGENTS.md` host-support table — one extra sentence under Copilot: Chat is a distinct product; Preview hooks may load `.github/hooks`; do not claim CLI coverage as Chat coverage. Minimal pointer; do not bloat the constitution.
- **acceptance tests (falsifiable):**
  - `python3 -m json.tool plugins/ravenclaude-core/knowledge/host-support.json`
  - Grep the new knowledge file + BP + CHANGELOG (Phase 5): **zero** matches of `all hosts isolated` / `Copilot is protected` / `Chat is protected` without the Preview qualifier.
  - Grep isolate-parallel BP: now matches `Copilot Chat` **and** still matches `claude --worktree`.
  - Dashboard / host-support: `copilot` label still contains `CLI`. `jq -r '.hosts | keys[]'` does **not** contain `copilot-chat`.
- **pre-build gates:** JSON validity; prettier on `host-support.json`; layout globs already allow `plugins/*/knowledge/**` and `plugins/*/best-practices/**`. Draft this phase in parallel with Phase 1 — do not wait for FOREIGN-TREE code to be complete before writing honesty (gap-delta anti-serialization). Chat wording that asserts hook teeth is blocked on Phase 0; the draft uses `[unverified]`.
- depends_on_claims: [4, 5, 6, 7, 8, 9, 11, 15, 18, 20]
- **blast radius:** docs + one JSON map. No runtime change. Consumer-visible honesty on `/plugin marketplace update`.

---

### Phase 4 — Cross-host footnotes + verification matrix

- **goal:** FOREIGN-TREE is defense-in-depth on hosts that already have a write root. A later session can open two worktrees and name a guard or an explicit cannot for each lane × host. Do not turn on Gemini `experimental.worktrees`. Do not cite Codex desktop Handoff (CL-15).
- **files:**
  - **edit** `plugins/ravenclaude-core/knowledge/codex-cli-customization.md` — one paragraph: `workspace-write` is the write floor (CL-14); FOREIGN-TREE is extra; after the hook-script change the consumer must `/hooks` (hash-trust). Not ChatGPT desktop managed worktrees (CL-15).
  - **edit** `plugins/ravenclaude-core/knowledge/gemini-customization.md` — one paragraph: JIT-on-touch (CL-16) means a **Read** of a sibling path can pull that tree's `GEMINI.md`; FOREIGN-TREE does **not** deny Read by default; do not set `experimental.worktrees`.
  - **no** Claude constitution rewrite. Native worktree isolation already blocks writes/cwd/git-redirects into the **main** checkout (CL-12). FOREIGN-TREE additionally blocks **sibling-B**. One sentence in the isolate-parallel BP host table is enough. Shared approvals on main `.claude/settings.local.json` are **policy bleed**, not file-write bleed (CL-13).
  - Record the verification matrix (below) in the isolate-parallel BP or in this plan's §6; after implementation, copy results into the run `summary.md` or a promoted `docs/research/` note if a teammate needs it.
- **acceptance tests:**
  - Docs contain the CL-15 / CL-16 honesty markers.
  - `grep experimental.worktrees` in the installer → still not flipped to true.
  - Every cell in §6 is either an enforceable mechanism with a source **or** explicit "cannot enforce — do X."
  - No cell claims the Claude session-id registry alone isolates Chat context.
- **pre-build gates:** markdown only.
- depends_on_claims: [9, 12, 13, 14, 15, 16, 17]
- **blast radius:** two knowledge files + BP table cells.

---

### Phase 5 — Version, catalog, installer honesty

- **goal:** User-visible guardrail ships as a semver bump consumers can `marketplace update`. Installer messages do not imply Chat coverage from CLI projection alone. CHANGELOG does **not** assert Chat enforcement.
- **files:**
  - `plugins/ravenclaude-core/.claude-plugin/plugin.json` `version`: `0.255.0` → `0.256.0` (minor: new deny class + new posture key + `rcwt` default-create change).
  - `.claude-plugin/marketplace.json` matching `ravenclaude-core` entry (L279; CI fails on drift).
  - `plugins/ravenclaude-core/CHANGELOG.md` new top entry `## 0.256.0`: FOREIGN-TREE, `worktree_bound` default block, lane stamp, `code -n`, Chat honesty with `[unverified]` Preview. **Must not** say Chat is protected. Current file top is `0.253.1` while the manifest is `0.255.0` — write `0.256.0` as the new top; do not invent `0.254`/`0.255` backfill.
  - `scripts/generate-copilot-hooks.py` — comment/docstring only: projected hooks are CLI **and** Chat-Preview-when-enabled (CL-7); Chat is still not session-isolated by CONTENTION alone. **Do not** add `worktree-guard.sh` to `_SKIP`.
  - `scripts/ravenclaude` install path for copilot — print one Chat operator-layout line + pointer to `knowledge/copilot-chat-customization.md`. Must not say "Copilot Chat hooks always on."
- **acceptance tests:** `python3 -m json.tool` both manifests; existing version-drift CI gate; installer / generator text has no "Chat hooks always on"; CHANGELOG grep as in Phase 3.
- **pre-build gates:** validate-marketplace / validate-schemas; prettier on JSON. **Blocked on Phases 1–4 landing in the same PR** (or 1+2+3 if 4 is a docs-only follow-up the same week). If Phase 0 probes are still pending — the expected state — CHANGELOG must say Chat hook teeth are `[unverified]`.
- depends_on_claims: [7, 8, 11]
- **blast radius:** version integers + changelog + two comment/print sites. The bump is for FOREIGN-TREE (hooked hosts) + lane stamp + honesty, **not** for Chat enforcement.

---

### Phase 6 — Chat adapter / payload wiring (follow-up only; feature-flagged; default no-op)

- **goal:** If and only if Phase 0 confirms Chat loads projected `.github/hooks` and the stdin carries a session id `worktree-guard.sh` already understands, then two Chat windows in two worktrees `register` as two sessions and FOREIGN-TREE can deny **on that machine**. If Phase 0 says hooks are off or the payload is unusable, this phase is a **no-op** plus an honesty sentence — do not ship a shim that pretends to fire.
- **G3b cap:** this is the Chat write-deny path. It does **not** ride in `0.256.0` as enforcement. If a mapping is required, it is a **fast-follow PR** after a real dump, feature-flagged, and still must not flip host-support `supported: true` without the dump.
- **files (only if probe passes):**
  - **edit** `plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh` — only if the dumped Chat payload uses field names the adapter does **not** already lift. Today it already reads `.sessionId // .session_id`, `.cwd // .workspaceRoot`, and maps `create→Write`, `edit→Edit`, `file_path // path // filePath`. **Do not pre-emptively remap invented Chat tool names.** If the dump shows a new file-path field, add that one mapping and a Gate 20-style fixture **copied from the dump**, not from a guessed name.
  - **do not** add a Chat-specific env shim analogous to `codex-hook-env.sh` unless the adapter path is not used (Chat loading `.claude/settings.json` with `${CLAUDE_PLUGIN_ROOT}` that does not resolve). If that is the probe result: document that Chat's reliable path is `.github/hooks` via the existing generator (CL-8), and that `.claude/settings.json` plugin-root hooks are Claude-dev-only.
  - **do not** change `generate-copilot-hooks.py` `_SKIP`.
- **acceptance tests:**
  - If adapter changes: extend `hooks/tests/test-gate20-adapter-diagnostics.sh` (or Gate 167) with a fixture **copied from the Phase 0 dump** (session_id present → `CLAUDE_SESSION_ID` exported; Write-shaped tool → FOREIGN-TREE sees `file_path`).
  - If probe fails or is skipped: **zero code changes** in this phase; Phase 3 already recorded the ceiling.
- **pre-build gates:** existing adapter gates 20 / 157 / 167; `generate-copilot-hooks.py --check`.
- depends_on_claims: [7, 8, 10]
- **blast radius:** adapter only if the payload requires it. Otherwise empty. **Blocked on Phase 0.** Not part of the `0.256.0` critical path.

---

### Phase 7 — Optional git pre-commit snippet (default off; not MVP)

- **goal:** Consumers who want a commit-time branch-vs-lane-stamp check can copy a snippet. This is **not** a Chat built-in Write close (the write already landed). A is correct that pre-commit is the wrong primary layer. Keep it opt-in only.
- **files (only if a consumer asks, or as a tiny follow-up):**
  - `plugins/ravenclaude-core/templates/worktree-lane/pre-commit-lane-check.sh` — if `.ravenclaude/lane.md` declares `branch` and `git rev-parse --abbrev-ref HEAD` ≠ that branch → deny commit. Documented snippet, **not** a default `core.hooksPath` change (`setup-worktree-hygiene.sh` already treats global hooksPath as high-blast).
- **acceptance:** snippet tested once in a scratch worktree; marketplace install does not enable it.
- depends_on_claims: [17, 20]
- **blast radius:** opt-in template. Not in the `0.256.0` PR unless it is free. Prefer leaving it out of the first PR.

---

## 5. Dependency DAG

```
Phase 0 (probes + one Chat ceiling file)
        │
        │     ┌──────── Phase 1 (FOREIGN-TREE + worktree_bound + SessionStart lane banner)
        │     │
        ├─────┴──────── Phase 2 (lane stamp + code -n + parent-walk pin)     [parallel with 1]
        │                    │
        │                    ▼
        │              Phase 3 (honesty docs)   [draft ∥ 1/2; wording that asserts Chat teeth waits on 0]
        │                    │
        │                    ▼
        │              Phase 4 (Codex/Gemini/Claude footnotes + matrix)   [parallel with 3]
        │                    │
        │                    ▼
        │              Phase 5 (0.256.0 + CHANGELOG + installer)          [last in the MVP PR]
        │
        ▼
Phase 6 (adapter)  — follow-up, only if Phase 0 says hooks fire
Phase 7 (pre-commit snippet) — optional, not MVP; needs Phase 2 stamp if it exists
```

| Phase | Blocks | Parallel with |
|---|---|---|
| **P0** | P6; Chat-asserting sentences anywhere; sandbox merge default-on | P1, P2, P3 draft, P4 |
| **P1** | P5 | P0, P2, P3 draft |
| **P2** | P5; P7 if P7 exists | P0, P1 |
| **P3 / P4** | P5 | each other |
| **P5** | merge of the MVP PR | — |
| **P6** | a later Chat-teeth PR | — |
| **P7** | nothing required | — |

**Critical path for the observed (context) leak:** P2 → P3 → P5.
**Critical path for the named write hole:** P1 → P5.
**MVP PR:** **P1 + P2 + P3 + P4 + P5** (`feat/ravenclaude-core-worktree-bound`). P0 is owner time, not a merge blocker. P6/P7 stay out unless a probe dump lands the same day.

If PR size must split: ship **P2+P3+P5 first** (unblocks the observed leak's defaults + honesty), **P1 the same week** — do not leave the named `_wg_is_mutating` hole open. Do not ship honesty+lane without a dated "FOREIGN-TREE follows this week" sentence in CHANGELOG if you split.

---

## 6. Host coverage (Chat ≠ CLI)

Treat Chat and CLI as **two products** (G0, CL-7, CL-11). Cursor / Aider / Devin: **out of scope**. Do not add host-support rows.

| Surface | Write isolation | Context isolation | Git isolation |
|---|---|---|---|
| **VS Code Copilot Chat** | Floor that always applies: one-folder window (CL-1) + do not multi-root (CL-5) + lane stamp hard rules. Terminal sandbox only if `RCWT_CHAT_CEILING=1` (Phase 0); sandbox **does not** cover built-in file tools (CL-2). Hook deny is **[unverified — CL-19]** until Phase 0; even then it is Preview + org-disable. **Cannot** claim Chat is protected in `0.256.0`. | **Cannot stop** Agent Host / Agents-window session share (CL-4). **Can stop** the common setup error: two worktrees in one window (`code -n`, refuse to generate multi-root). SessionStart lane pin **if** hooks fire. Open-editor bleed is a window-layout problem, not a hook. | Git floor (CL-17). Chat git follows the workspace folder. FOREIGN-TREE denies `git -C <sibling>` **only if** that call is a hooked terminal tool **and** hooks are on. Optional Phase 7 pre-commit is not a Chat built-in Write close. |
| **Copilot CLI** | Cwd + projected PreToolUse (already wired, CL-8). FOREIGN-TREE is live as soon as Phase 1 ships. Adapter already lifts `session_id`. | Separate process = separate conversation. Instruction files from repo/cwd (CL-18). No Agents-window analogue. | Git floor + existing CONTENTION + new FOREIGN-TREE on `git -C`. |
| **Claude Code** | Native worktree checks block writes/cwd/git-redirects into the **main** checkout (CL-12). FOREIGN-TREE adds **sibling-B**. `isolation: "worktree"` isolates cwd. | Per-session cwd; `CLAUDE.md` follows the tree. **Cannot** isolate `~/.claude/`, project plugins, or saved approvals written to main `.claude/settings.local.json` (CL-13). | Git floor + native destructive-git-to-main blocks + FOREIGN-TREE. |
| **Codex CLI** | `workspace-write` = this cwd; outside-workspace edits need approval (CL-14). FOREIGN-TREE is defense-in-depth. **Not** ChatGPT desktop managed worktrees (CL-15). | `AGENTS.md` walk cwd→`.git` (same committed file — intended). Shared `~/.codex`. | Git floor. `.git` read-only inside sandbox (commits often need approval). Hash-trust: `/hooks` after Phase 1. |
| **Gemini CLI** | Project cwd + optional sandbox. No documented sibling deny (CL-16). FOREIGN-TREE via `gemini-hook-adapter.sh` if the write tool is mapped. Layout gate still not wired (unverified path field) — do not claim it. | `GEMINI.md` walk + **JIT on tool touch** (CL-16): a Read of a sibling path can pull that tree's `GEMINI.md`. FOREIGN-TREE does not deny Read by default. Shared `~/.gemini`. | Git floor. `experimental.worktrees` stays **false**. |

### Verification matrix (Phase 4 acceptance — every cell is a named guard or a cannot)

| Lane | Chat | Copilot CLI | Claude | Codex CLI | Gemini CLI |
|---|---|---|---|---|---|
| Write | One-folder + lane rules; Preview hook deny **[unverified CL-19]**; else instruct. Cannot OS-sandbox built-in tools (CL-2). | cwd + projected FOREIGN-TREE (P1) | Native main-checkout blocks + FOREIGN-TREE sibling-B | workspace-write + FOREIGN-TREE | cwd + FOREIGN-TREE if mapped; do not claim layout-gate |
| Context | **One window per tree; new session; no multi-root; no Agents cross-ws resume; lane stamp** | Separate process | cwd-scoped session | cwd walk | No sibling Read (JIT) |
| Git | CL-17 floor + lane branch stamp | CL-17 + CONTENTION + FOREIGN on `git -C` | CL-17 + native + FOREIGN | CL-17 + sandbox | CL-17 |

---

## 7. Three lanes (what we close, with which artifact)

### Write isolation

- **Close (hooked hosts):** tool Write/Edit/MultiEdit / `git -C` whose target is another listed worktree. Artifact: `worktree-guard.sh` FOREIGN-TREE + `worktree_bound: block` (Phase 1).
- **Chat extra:** one reversible ceiling file + optional sandbox flag (Phase 0). Preview hooks **if** Phase 0 says they fire (Phase 6 follow-up). Else one-folder window only.
- **Not a close:** OS-sandboxing Chat built-in tools (vendor does not; CL-2). Pre-commit after the write landed.

### Context isolation (observed)

- **Close (layout):** one VS Code window per worktree; never multi-root two worktrees; `rcwt new` launches `code -n "$dest"` and says so (Phase 2).
- **Close (identity):** `.ravenclaude/lane.md` stamp — works when SessionStart does not inject (Phase 2).
- **Close (pin):** SessionStart `additionalContext` lane banner when hooks fire (Phase 1 `register`).
- **Cannot close:** Agents-window / Agent Host session reuse (CL-4); open editors in a multi-root window (CL-5, CL-20); JIT Gemini read-of-sibling (CL-16) unless we later deny Read (we will not in v1); shared `~/.{copilot,claude,codex,gemini}`.

### Git isolation

- **Already closed by git:** same branch checked out in two worktrees (CL-17).
- **Close:** `git -C` / `GIT_WORK_TREE` / `--git-dir` aimed at a sibling (Phase 1).
- **Already closed by us:** CONTENTION (two live writers, one toplevel) + ANCHOR-WORK (primary + on main while worktrees exist).
- **Not a close:** shared object store / shared refs (given). A `pre-commit` mismatch check is the wrong primary layer (Phase 7 opt-in only).

---

## 8. What CANNOT be enforced (do not claim)

| Thing | Why | What we do instead |
|---|---|---|
| Shared `~/.copilot`, `~/.claude`, `~/.codex`, `~/.gemini` | Host-private user scope; applies across projects (CL-13, CL-14, CL-16, AGENTS.md house rule). | Name it. Do not "fix" it. |
| Agent Host / Agents-window **session sharing** (CL-4) | Product: both surfaces share sessions; Agent Host owns the session independent of windows. No marketplace hook can split that object. | Instruct: one Chat-**view** window per worktree; do not resume a session from the other tree in the Agents window. Cannot deny. |
| Multi-root as a context pool (CL-5) | If the human adds a second folder, search/index/open-editors are one pool. Agents window does not even support multi-root sessions (limitation). | Refuse to **generate** that layout. Cannot intercept `Add Folder to Workspace`. |
| Chat built-in Write when hooks are off or unproven (CL-19) | Preview + org-disable. No PreToolUse point until Phase 0 says otherwise. | Phase 0 ceiling file + Phase 2 layout + honesty. Not a silent adapter. |
| Sibling **Read** / dirty files / `.ravenclaude/runs/<other-task>/` entering context via `#codebase` or open editors (CL-20) | Not a PreToolUse we reliably see; semantic index is the workspace. Denying Read of a sibling path would break legitimate compare-two-trees workflows and is **not** v1. | Layout (don't put the other tree in the workspace). Lane banner / stamp. |
| Shared committed `AGENTS.md` | Intended (CL-20, G0). | Do not per-tree-fork the constitution. |
| Claude saved **permission approvals** on main checkout (CL-13) | Policy bleed, not file-write bleed. | Name it in the BP host row. |
| Codex **desktop** managed worktrees (CL-15) | Different product than the CLI this marketplace installs. | Do not cite as a CLI guard. |
| Gemini `experimental.worktrees` | Defaults false; unproven as an isolation guarantee. | Leave off. |
| Plugin-level Copilot hooks (github/copilot-cli#2540) | G0 out of scope. | Stay on repo-level `.github/hooks`. |
| VS Code hook **matchers** (CL-7) | Chat currently **ignores** matchers — hooks run on every tool. | Hooks must keep self-filtering (already true). Do not depend on a matcher to stay off the Read path. |

---

## 9. Marketplace constraints (this plan obeys)

- **Stack:** bash + JSON + markdown only. FOREIGN-TREE is more `jq`/`git` in an existing `set -uo pipefail` script (bash 3.2 / BSD-safe, same as today).
- **Ship in** `ravenclaude-core` hooks / templates / knowledge / best-practices / `bin/rcwt` / `scripts/write-lane-stamp.sh`. Installer change is comment + one print line. `generate-copilot-hooks.py` stays projected (guard not in `_SKIP`).
- **No new plugin. No new skill or agent.** Existing skills `new-worktree` and `cleanup-worktrees` gain a subsection. G8 regen is **not** required.
- **Host-honest:** new Chat knowledge file; `copilot` label stays "GitHub Copilot CLI"; no "all hosts isolated"; no Chat-protected CHANGELOG line.
- **Versions:** `0.255.0` → `0.256.0` in `plugin.json` **and** `marketplace.json`. CHANGELOG top entry required (file exists).
- **Layout:** new paths under `plugins/*/templates/**`, `plugins/*/knowledge/**`, `plugins/*/hooks/**` (tests included), `plugins/*/scripts/**`, `plugins/*/bin/**` — already allowed. No `.repo-layout.json` edit unless someone tries to commit `.vscode/` at marketplace root (don't).
- **Knob idiom:** `worktree_bound: off|warn|block` next to `worktree_guard`. Dashboard schema + state slot + emitYaml + balanced template. Absent ⇒ `block` for bound; absent ⇒ `warn` for guard.
- **Comfort-posture Save safety:** any new scalar must have a dashboard state slot or the next Save deletes it.

---

## 10. `[unverified]` register (every marker has a settling step)

| Marker | Where it lives | Settling step |
|---|---|---|
| CL-3 Chat built-in Write to an absolute sibling path | claims-table; G3b owner-gated | Phase 0 probe 1 (`probe-cl3.md`). Until then: do not claim Chat cannot/can Write a sibling; FOREIGN-TREE still ships for other hosts. |
| CL-19 Chat Preview fires projected `.github/hooks` on this machine + payload shape | claims-table; G3b owner-gated | Phase 0 probe 2 (`probe-cl19.md`). Until then: host-support Chat cell is docs-verified Preview (CL-7) + `[unverified — live Preview]`. Phase 6 stays no-op. |
| Chat SessionStart `register` distinguishes two Chat windows (non-`unknown` id) | CL-10 + CL-19 | Phase 0 probe 3 (bonus on the same dump). Until then: CONTENTION is not a Chat context claim. |
| Whether `code` without `-n` reuses a window | product default | Do not probe. Phase 2 always passes `-n`. |
| Chat setting that auto-loads `.ravenclaude/lane.md` | not in G1 product docs | Do not invent a setting. Stamp is filesystem identity; SessionStart banner when hooks fire; operator/agent reads the file. |
| Gemini layout-gate path field | already unverified in `host-support.json` | Do not claim FOREIGN-TREE on unmapped Gemini write tools. Adapter maps only names it already maps. |
| Dashboard new-host-key safety | checked this session: missing cell renders "no" | Still **do not** add `copilot-chat` as a host key (looks like an install target). Nested caveat only. |

---

## 11. Implementation notes (for the builder — do not re-derive)

1. **Detect the hole first in a test.** Today's `_wg_is_mutating` + Write-to-sibling must be shown to exit 0 in `block` **before** the patch, and exit 2 after. Gate 140 already knows how to write a teeth half.
2. **Split the `worktree_guard: off` early exit** before adding any FOREIGN-TREE call, or T13 is impossible and `worktree_guard: off` silently disables the new clause.
3. **Sibling set** = every `worktree ` line from `git worktree list --porcelain` whose `realpath` ≠ `REAL_TOP`. Walk up for not-yet-created files the same way `_wg_path_under_tree` already does.
4. **Do not** treat "path outside REAL_TOP" as foreign by itself — that would deny `/tmp` and home-dir scratch and fight other tools. **Only listed worktrees of this repo.**
5. **Chat tool names** enter the hook only after `copilot-hook-adapter.sh`. Until Phase 0 dumps a payload, assume Claude-shaped names post-adapter. Self-filter: unknown tool + no resolvable path → allow.
6. **Matchers ignored in Chat (CL-7)** means FOREIGN-TREE `check` will run on Read/Grep too **if** Preview ever fires. v1: allow those.
7. **Dashboard:** `worktree_bound` is Settings-only, like `worktree_guard` — not a Pipeline stage card. State + hydrate + emitYaml are mandatory even with no new DOM toggle (Gate 132 budget is at zero slack; `dashboard_autostart` is the pattern).
8. **Hash-trust:** any byte change in `worktree-guard.sh` skips Codex hooks until `/hooks`. Phase 4 docs must say so.
9. **`rcwt` test:** stub `code` on PATH; do not require a real VS Code. `write-lane-stamp.sh` must be `bash -n` clean and executable.
10. **Copy the settings merge** from `setup-terminal-indicators.sh` L68–107. Atomic write (`*.tmp` + `os.replace`). Add-absent-keys only.
11. **Register lane banner** when `siblings > 0`, not only on CONTENTION/ANCHOR. SessionStart cannot block (`register` always exit 0).
12. **Do not** add a sixth PreToolUse process. Same `check` / `register` commands, one more function.
13. **CHANGELOG** is the honesty backstop: if a sentence would not survive a grep for `Chat is protected`, do not write it.

---

## 12. Risks

| Risk | Mitigation |
|---|---|
| CL-19 false: Chat never loads `.github/hooks` | Phase 2 is the Chat ceiling; Phase 3 says so; Phase 1 still pays off on CLI/Claude/Codex/Gemini |
| CL-3 false: Chat already cannot Write a sibling | FOREIGN-TREE still needed on other hosts; Chat row says "product may already refuse; our hook is defense-in-depth **if** enabled" |
| New default-block knob surprises a workflow that **intentionally** patches a sibling tree | `RC_WORKTREE_BOUND_ACK=1` + `worktree_bound: off`. Do not weaken the default. |
| Sixth PreToolUse on Write (R-9 latency) | **No sixth hook** — same `check` process, one more function. |
| Dashboard Save drops `worktree_bound` | State slot + emitYaml (Phase 1). Same class as v0.61.0. |
| VS Code settings merge overwrites user parent-walk-on or sandbox-off | Non-destructive add-absent-keys only (Phase 2 test 2). Sandbox merge is flag-gated. |
| Over-claim Chat teeth in CHANGELOG | Phase 5 grep; G3b cap on the one ceiling file. |
| Under-claim CLI write close by shipping honesty without FOREIGN-TREE | MVP PR includes Phase 1. Split only with a dated follow-up sentence, same week. |
| `code -n` unavailable / `code` missing | Existing fallback print stays: `open it: code -n "$dest"`. |

---

## 13. Out of scope (so G7 cannot "helpfully" add them)

- New plugin, new skill, new agent, Sleipnir command, Ultraplan.
- Changing git worktree semantics / second object store.
- Per-worktree constitution / different `AGENTS.md` content.
- Fixing github/copilot-cli#2540.
- Proving write/git failure by landing a bad commit in a live tree.
- Cursor / Aider / Devin rows.
- Denying Read of sibling trees in v1.
- Enabling Gemini `experimental.worktrees` or citing Codex desktop Handoff.
- A top-level `copilot-chat` host key.
- Default-on pre-commit or a global `core.hooksPath` change.
- Flipping `worktree_guard` default from `warn` to `block`.
- A version-bump that asserts Chat enforcement.

---

## 14. Definition of done

A later implementer can execute this file without re-deriving the mechanism when all of the following are true:

1. **Hole named and tested.** Sibling absolute Write in `worktree_guard=block` exits 0 before the patch and 2 after (`worktree_bound=block`). T8–T16 and Gate 140 F1/F2/P1–P3 are green. T13 proves the knobs are independent.
2. **Observed leak has a default-correct create path.** `rcwt new` writes `.ravenclaude/lane.md`, opens `code -n`, prints the one-window warning, and does not generate a two-folder workspace.
3. **Honesty is grep-proof.** `host-support.json` still labels `copilot` as CLI; a Chat knowledge file exists; isolate-parallel has dated host rows; no shipped sentence says Chat is protected; CL-3 and CL-19 remain `[unverified]` until Phase 0 files exist.
4. **Cannot-enforce list is named** (§8) including Agents-window session share, multi-root-if-human-adds, host-private `~/.{copilot,claude,codex,gemini}`, shared `AGENTS.md`, and Chat built-in Write when hooks are off.
5. **Consumers can update.** `0.256.0` is in both manifests, CHANGELOG top is current, Codex docs say `/hooks`, and the installer does not claim Chat hooks are always on.

That is G0's success signal: two worktrees, four in-scope hosts, a named guard or an explicit cannot, and **no new false claim of support**.

---

_End merged plan. Source plans: `plan-A.md` (enforce-first), `plan-B.md` (workflow-first), `gap-delta.md` §12, `g3b.md` reshape. A+B dual-track; G3b owner-gate on CL-3/CL-19._
