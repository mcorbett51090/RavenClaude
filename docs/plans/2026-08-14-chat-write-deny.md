# Chat write-deny leftover — merged plan (G6)

**Run:** `forge/chat-write-deny`
**Gate:** G6 Synthesize
**Date:** 2026-08-14
**Worktree:** `/Users/matthewcorbett/.grok/worktrees/matthewcorbett-ravenclaude/copilotchatwritedeny/.claude/worktrees/forge-chat-write-deny`
**Version floor:** `ravenclaude-core` **0.270.0** (do not bump for Chat enforcement)
**Ship shape:** one reversible template + gitignored skip/partial probe records. No adapter. No hook. No new plugin / skill / agent. G8 regen not required.
**Landing:** PR only if a file under `plugins/` changes. Default committed set is `plugins/ravenclaude-core/templates/worktree-lane/chat-ceiling.md`. Gitignored probes are not a PR. A new `pre-commit-lane-check.sh` is a second plugin file and is therefore a PR if shipped.

Claims authority: this-run `claims-table.md` rows 1–16. Inferences 8 / 10 / 16 are **owner-gated** (G3b 2026-08-14). They are not product facts. This CLI cannot run VS Code Copilot Chat Agent mode (claim 15).

Honesty grep: zero matches of `Chat is protected`. Chat stays operator-lane + `[unverified]` live fire.

---

## Law (G3b owner-gate — do not re-litigate)

| Rule | Consequence in this plan |
|---|---|
| One reversible shipped file | Edit only `plugins/ravenclaude-core/templates/worktree-lane/chat-ceiling.md`. Already shipped. Upgrade the probe kit + honesty only. |
| Local-run only probes | Dated `probe-cl3.md` + `probe-cl19.md` under this run dir. Skip/partial rows allowed. |
| Phase 6 adapter/hook code | **No.** B wins D1/D4. Do **not** ship `RC_CHAT_PREVIEW_MAP`. Do **not** edit `copilot-hook-adapter.sh` or `worktree-guard.sh`. |
| Phase 7 pre-commit | May ship as opt-in template **if** labeled **not a Chat write-deny** and default off. Does **not** cite claims 8 or 10 as a shipping premise. Default for this leftover: **defer**. |
| Semver | Stay **0.270.0**. No Chat-enforcement bump. Prefer no bump at all. |
| host-support | `components.hooks.copilot.surfaces.chat.supported` stays **false**. |
| Zero protected claim | No sentence that Chat is protected. Copilot host label stays GitHub Copilot CLI. No top-level `copilot-chat` host key. |

**One-line success (G0 arm b — expected):** dated skip/partial records exist, Phase 6 stays a documented no-op, Chat remains `[unverified]` / operator-lane only, and any Phase 7 snippet is opt-in and explicitly **not a Chat write-deny**.

Arm (a) — dump-derived adapter map — is **out of this leftover**. If a live dump appears later, that is a separate fast-follow, not a rewrite of D1.

---

## Diagnosis

Already closed (0.268.0, not this leftover):

- FOREIGN-TREE + `worktree_bound` on hooked hosts Claude / Copilot CLI / Codex / Gemini (claim 1).
- Lane stamp, one-window operator default, Chat honesty docs, `chat-ceiling.md` checklist (claim 2).

Still open (this leftover only):

| Gap | Status | Close in this leftover |
|---|---|---|
| CL-3 sibling built-in Write product behavior | No dated probe file (claim 3) | Dated skip/partial + copy-paste kit |
| CL-19b live PreToolUse fire + payload shape | No dated probe file (claim 3) | Same. **Blocks any adapter edit** |
| Adapter Chat name / envelope map | Zero Chat names (claim 11); no `files[]` extract (claim 12) | **Leave code alone** (D1 → B) |
| Phase 7 pre-commit lane-stamp check | Absent (claim 4) | Defer. Ship only as labeled opt-in if chosen |
| host-support Chat cell | `supported: false` (claim 5) | Keep false |

The hole A diagnosed (docs-shaped Chat stdin would miss `toolArgs` / `files[]` and FOREIGN-TREE would allow — claim 16) is real as an **inference**. It is not a license to pre-map WD-9 names. A docs-verified name is not a payload dump (claim 9 vs 10). Shipping that map without fire is a shim that pretends to fire (claim 13 / prior G3b).

---

## Alternatives (A vs B) and pick

| ID | Approach | Trade-off |
|---|---|---|
| **A. Flag-gated docs-verified adapter map** | Edit `copilot-hook-adapter.sh` behind `RC_CHAT_PREVIEW_MAP=1` (default off). Shipping premise = claim 9 docs, not claim 10. Semver 0.271.0. Relocates G3b's one-file cap onto the adapter. | Looks like teeth. Diverges from WD-13 / G3b “zero code if skipped.” Still wrong if live envelope differs. Future readers treat adapter lines as Chat-is-hooked. |
| **B. Skip-record + probe kit + honesty audit** | Dated skip/partial; upgrade `chat-ceiling.md`; grep-proof honesty; **zero** adapter/hook/semver. Phase 6 documented no-op. Phase 7 deferred unless labeled opt-in. | Cheapest true remaining work. Chat stays operator-lane. Does not invent teeth. |
| **C. Always-on remap** | Same mappings, no flag. | Pretends Chat is wired. **Reject.** |
| **D. Teach worktree-guard Chat names** | Host-neutral hook learns `editFiles` + `files[]`. | Pollutes every hooked host. Out of G0. **Reject.** |
| **E. Wait-only / no artifacts** | Leave probes unmarked; no kit upgrade. | Next session re-discovers the open gate and may re-attempt A. Fails G0 arm (b). **Reject.** |
| **F. Phase 7 as the Chat close** | Sell opt-in pre-commit as residual write isolation. | Write already landed (claim 14). False claim. **Reject as primary.** Acceptable only as labeled git hygiene. |

**Pick B** for D1 / D3 / D4 / D5 / D6. G3b is law: the reversible file is `chat-ceiling.md`, not the adapter. Shim = any pre-map from docs without fire; the flag does not change that.

**Steal from A (non-D1):** CL-19 kit must record **which command actually ran** (adapter argv vs raw `.claude/settings.json`) and point at **Developer: Show Agent Debug Logs** / **GitHub Copilot Chat Hooks**. Merge B’s standalone honesty-audit greps into DoD.

**Phase 7:** B’s defer wins as default. A’s labeled snippet is the only allowed ship shape if G7 includes it.

**Semver:** B wins D2. Stay 0.270.0. A’s own fallback already forbade an empty minor.

---

## Phased plan

### Phase 0 — Dated owner-gate records (skip/partial)

- **goal:** Make CL-3 / CL-19b state falsifiable on disk so no future session treats “no file” as “not yet considered.” Close G0 success arm (b) for the owner-gate half. Do not run Chat from this CLI.
- **files (local-run only, gitignored):**
  - `.ravenclaude/runs/forge/chat-write-deny/probe-cl3.md`
  - `.ravenclaude/runs/forge/chat-write-deny/probe-cl19.md`
- **write exactly this skeleton for probe-cl3.md** (replace only the Status line if a later owner run fills results):

```markdown
# probe-cl3 — Chat Agent-mode sibling Write

Date: 2026-08-14
Status: skipped — owner not available in this CLI session (2026-08-14)
Claim: 8 / CL-3
[unverified — owner-gated CL-3]

## Procedure (owner, VS Code Copilot Chat Agent mode)

1. Open a window on worktree A only (`code -n <A>`). Do not add sibling B as a folder.
2. Start a new Chat session. Agent mode.
3. Ask the agent to Write an absolute path under sibling worktree B.
4. Record the product outcome in the table below. Do not guess.

## Result

| Field | Value |
|---|---|
| keep | |
| undo | |
| approval dialog | |
| no-op | |
| notes (redacted) | |

Do not claim Chat can or cannot land sibling Write until this table is filled.
```

- **write exactly this skeleton for probe-cl19.md:**

```markdown
# probe-cl19 — Chat Preview PreToolUse live fire

Date: 2026-08-14
Status: skipped — owner not available in this CLI session (2026-08-14)
Claim: 10 / CL-19b
[unverified — owner-gated CL-19]

## Procedure (owner)

1. Projected `.github/hooks` present (`ravenclaude install` if needed).
2. `chat.hooks.enabled` on. Org policy allows Preview hooks.
3. One mutating Chat tool call (Write/edit of a path inside the opened folder is enough).
4. Dump raw PreToolUse stdin (redact secrets / absolute home paths as needed).
5. Record which command actually ran: adapter argv (`copilot-hook-adapter.sh …`) vs raw `.claude/settings.json` hook.
6. Output channel: Developer: Show Agent Debug Logs / GitHub Copilot Chat Hooks.

## Observation slots (record; do not map)

| Slot | Present? | Value (redacted) |
|---|---|---|
| session_id / sessionId | | |
| cwd / workspaceRoot | | |
| tool_name / toolName | | |
| path field name(s) | | |
| toolArgs present? | | |
| tool_input object? | | |
| files[] shape (string / object / absent) | | |
| argv / which hook file ran | | |

## Payload

(redacted stdin block — omit until a live dump exists)

Until this dump exists, Phase 6 is a documented no-op. Do not flip surfaces.chat.supported.
```

- **acceptance tests:**
  1. Both files exist under `.ravenclaude/runs/forge/chat-write-deny/` and contain `2026-08-14` plus either a result row or the string `skipped`.
  2. `test -e .ravenclaude/runs/forge/chat-write-deny/probe-cl3.md` and the same for `probe-cl19.md` → exit 0 (inverts claim 3 for *this* run).
  3. Neither file claims live fire without a payload block.
  4. Neither file contains the string `Chat is protected`.
- **pre-build gates:** none (gitignored markdown).
depends_on_claims: [3, 8, 10, 15]
- **blast radius:** local-run only. Zero consumer impact.

---

### Phase 1 — Operator probe kit (upgrade chat-ceiling.md only)

- **goal:** Give the owner a copy-paste kit so the next VS Code session can settle claims 8 / 10 in minutes. Still **not Chat enforcement.**
- **files:**
  - **edit only** `plugins/ravenclaude-core/templates/worktree-lane/chat-ceiling.md`
- **required edits (implementer, do not re-derive):**
  1. Keep the title and the bold “not Chat enforcement” / “It is not Chat enforcement” lines (claim 2). Do not weaken them.
  2. Keep the optional `chat.agent.sandbox.enabled` snippet and the `RCWT_CHAT_CEILING=1` default-off note.
  3. Replace the current “Owner probes” section with numbered copy-paste procedures:
     - **CL-3:** window on worktree A only → Agent mode → Write absolute path under B → record keep / undo / dialog / no-op.
     - **CL-19b:** projected `.github/hooks`, `chat.hooks.enabled` on, org allows Preview → one mutating tool call → dump raw PreToolUse stdin.
     - **Where to write dumps:** prefer this leftover run `.ravenclaude/runs/forge/chat-write-deny/probe-cl{3,19}.md` (supersede the skip section; keep the dated skip history). Also name the prior-plan path `.ravenclaude/runs/forge/copilot-chat-worktree-lanes/probe-cl{3,19}.md` for continuity.
     - **CL-19b debug:** record argv / which hook file ran (adapter vs raw `.claude/settings.json`). Point at Developer: Show Agent Debug Logs and GitHub Copilot Chat Hooks.
     - **Payload observation slots** (not map targets): `session_id` / `sessionId`, `cwd` / `workspaceRoot`, `tool_name` / `toolName`, path field name(s), whether `toolArgs` vs `tool_input` was present, `files[]` shape if any. WD-9 names (`editFiles`, `createFile`, `create_file`, `replace_string_in_file`, `runTerminalCommand`) may appear as **docs-verified vocabulary to look for**, never as “put these in the adapter.”
     - **Phase 6 no-op sentence (required):** `Phase 6 (adapter wiring): no-op 2026-08-14 — CL-19b probe skipped; no dump-derived map. Do not ship RC_CHAT_PREVIEW_MAP.`
     - **Explicit do-not:** do not edit `copilot-hook-adapter.sh` from docs alone; do not flip `surfaces.chat.supported`; do not claim protected after a partial probe; do not invent a sample PreToolUse payload as if it were live-captured.
  4. **do not** edit adapter, worktree-guard, host-support, plugin.json, marketplace.json, CHANGELOG, or `knowledge/copilot-chat-customization.md` in this phase.
- **acceptance tests:**
  1. `rg -n "not Chat enforcement" plugins/ravenclaude-core/templates/worktree-lane/chat-ceiling.md` → ≥1.
  2. File contains `CL-3`, `CL-19`, `probe-cl3.md`, `probe-cl19.md`, and a numbered procedure (or “Procedure” heading).
  3. File contains the Phase 6 no-op sentence (string `no-op` and `2026-08-14`).
  4. File contains `Show Agent Debug Logs` or `argv` (path-discrimination steal from A).
  5. `rg -n "Chat is protected|Copilot is protected" plugins/ravenclaude-core/templates/worktree-lane/` → 0.
  6. `rg -n "editFiles|createFile|create_file|replace_string_in_file" plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh` → still 0 (kit must not smuggle maps into code).
  7. `git diff --name-only` for this phase lists at most `plugins/ravenclaude-core/templates/worktree-lane/chat-ceiling.md` among committed plugin files.
- **pre-build gates:** markdown only. Layout glob `plugins/*/templates/**` already allows the path. No `.repo-layout.json` edit. No prettier required unless a JSON sibling is touched (do not touch one).
depends_on_claims: [2, 8, 9, 10, 13]
- **blast radius:** one reversible template file. Consumers who never open it see nothing. No runtime behavior change.

---

### Phase 2 — Honesty audit (grep-proof)

- **goal:** Prove the tree still cannot be misread as “Chat write-deny shipped.” Automate G0/G3b as acceptance, not vibes. Prefer zero edits when greps are already clean. If a false claim is found, fix the **sentence** only — never “fix” by mapping adapter names.
- **files:** none required to ship. Read/check only:
  - `plugins/ravenclaude-core/knowledge/host-support.json` → `surfaces.chat.supported === false` (claim 5).
  - `plugins/ravenclaude-core/knowledge/copilot-chat-customization.md` — ceiling language intact if present.
  - `plugins/ravenclaude-core/CHANGELOG.md` top entries — no “Chat is protected” / “Chat write-deny live.”
  - `plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh` — no Chat Preview tool names (claim 11).
  - `plugins/ravenclaude-core/templates/worktree-lane/` — no protected claim.
  - `plugins/ravenclaude-core/.claude-plugin/plugin.json` version remains `0.270.0` (claim 6).
- **acceptance tests (run from worktree root):**
  1. `python3 -c "import json; c=json.load(open('plugins/ravenclaude-core/knowledge/host-support.json')); assert c['components']['hooks']['copilot']['surfaces']['chat']['supported'] is False"`
  2. `python3 -c "import json; print(json.load(open('plugins/ravenclaude-core/.claude-plugin/plugin.json'))['version'])"` → `0.270.0`
  3. `rg -n "Chat is protected|Copilot Chat is protected|Chat write-deny (is |now )?live|Chat hooks always on" plugins/ravenclaude-core/` → 0 (ignore historical prose that already says “must not”).
  4. `rg -n "editFiles|create_file|createFile|replace_string_in_file|RC_CHAT_PREVIEW_MAP" plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh` → 0.
  5. `rg -n "\"copilot-chat\"" plugins/ravenclaude-core/knowledge/host-support.json` → 0 (no top-level host key).
  6. `test ! -e plugins/ravenclaude-core/templates/worktree-lane/pre-commit-lane-check.sh` **or**, if Phase 7 shipped it, file header contains `not a Chat write-deny`.
- **pre-build gates:** `python3 -m json.tool` on host-support only if that file was edited (default: do not edit it).
depends_on_claims: [1, 5, 6, 7, 11, 13]
- **blast radius:** doc-only sentence fixes if any. Prefer zero committed edits.

---

### Phase 6 — Documented no-op (adapter stays untouched)

- **goal:** Encode the **zero-code** Phase 6 outcome as the planned leftover. B wins D1/D4. This is not a placeholder for later map code inside this run.
- **files:** **none.** The no-op sentence already lands in `chat-ceiling.md` during Phase 1. Optional local-run note `.ravenclaude/runs/forge/chat-write-deny/phase6-noop.md` is allowed; not required if the ceiling sentence exists.
- **do not:**
  - Edit `plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh`.
  - Edit `plugins/ravenclaude-core/hooks/worktree-guard.sh`.
  - Edit `scripts/generate-copilot-hooks.py`.
  - Introduce `RC_CHAT_PREVIEW_MAP` anywhere in shipped code or installer env.
  - Flip `surfaces.chat.supported`.
  - Invent Chat tool names from claim 9.
- **dump path (out of this leftover — do not implement here):** if a later owner session fills `probe-cl19.md` with a real redacted stdin, a **separate** fast-follow may map **only** field names copied from that dump, with a fixture copied from dump bytes. Still fail-open on unknown tools. Still no sibling Read deny. Still no `supported: true` until end-to-end FOREIGN-TREE deny is observed on Chat PreToolUse for a sibling Write. Still no “Chat is protected” CHANGELOG. That follow-up is not this plan’s critical path.
- **acceptance tests (this leftover):**
  1. `git diff --stat -- plugins/ravenclaude-core/hooks/copilot-hook-adapter.sh plugins/ravenclaude-core/hooks/worktree-guard.sh` → empty for this leftover.
  2. `chat-ceiling.md` states Phase 6 no-op + reason (probe skip).
  3. `rg -n "RC_CHAT_PREVIEW_MAP" plugins/ravenclaude-core/hooks/` → 0.
- **pre-build gates:** none (no hook files touched).
depends_on_claims: [10, 11, 12, 13, 16]
- **blast radius:** empty.

---

### Phase 7 — Optional opt-in pre-commit snippet (defer by default)

- **goal:** If shipped, consumers get an **opt-in** lane-stamp vs `HEAD` branch check. Explicitly **not a Chat write-deny** (write already landed — claim 14). Prefer **defer** for this leftover.
- **default for the implementer:** **do not ship.** Operator lane is layout + probes, not git hooks. Skip this phase unless G7/G8 explicitly includes it.
- **if G7 includes it (tiny follow-up, same or later PR):**
  - **new file** `plugins/ravenclaude-core/templates/worktree-lane/pre-commit-lane-check.sh`
    - `set -euo pipefail`
    - First 10 lines of the header **must** contain both `not a write-deny` and `not a Chat write-deny`.
    - Also: `Opt-in only. Do not set core.hooksPath globally.`
    - Behavior: if `.ravenclaude/lane.md` has `branch:` and `git rev-parse --abbrev-ref HEAD` ≠ that value → exit 1 with stderr containing `not a Chat write-deny`.
    - Fail-open if no lane stamp (exit 0). Absent stamp is not a deny.
    - Do **not** call it from `rcwt`, `scripts/ravenclaude`, or `setup-worktree-hygiene.sh`.
  - **edit** `plugins/ravenclaude-core/templates/worktree-lane/README.md` — one bullet: copy into `.git/hooks/pre-commit` only for branch/lane drift detection; **not** write isolation; default off.
- **acceptance tests (only if shipped):**
  1. Scratch worktree with `lane.md` `branch: feat/x` and HEAD `main` → script exit 1; stderr matches `not a Chat write-deny`.
  2. HEAD matches `branch:` → exit 0.
  3. No `lane.md` → exit 0.
  4. `rg -n "core.hooksPath|Chat is protected" plugins/ravenclaude-core/templates/worktree-lane/pre-commit-lane-check.sh` → 0.
  5. `rg pre-commit-lane-check plugins/ravenclaude-core/bin/rcwt scripts/ravenclaude` → 0 (installer does not enable it).
  6. `rg -n "write-deny|Chat enforcement|protected" plugins/ravenclaude-core/templates/worktree-lane/pre-commit-lane-check.sh` → only the **negated** honesty lines.
- **pre-build gates (only if shipped):** `bash -n` the snippet; layout glob `plugins/*/templates/**` already allows it. `RC_BASELINE.templates` does **not** increment. Executable bit: match other templates in that folder (today they are ordinary files). This is a plugin change → **PR**, not docs-straight-to-main. Still **no** semver bump.
depends_on_claims: [4, 14]
- **blast radius:** zero if deferred. If shipped: opt-in template only; default install path unchanged. Not a Chat write-deny.

---

### Phase 8 — Landing / versioning (what does not ship)

- **goal:** Land only Phase 1 (+ Phase 7 if G7 included it). Do **not** bump to 0.271.0. Do **not** cite Chat write-deny as a version reason.
- **landing table:**

| Change set | Version | PR? |
|---|---|---|
| Local-run skip records only (`probe-cl3.md`, `probe-cl19.md`) | no bump | no (gitignored) |
| `chat-ceiling.md` kit upgrade only | stay **0.270.0** | **yes** — file is under `plugins/` |
| Honesty sentence-only fix in knowledge / CHANGELOG | stay **0.270.0** | yes if under `plugins/`; docs-straight-to-main if only `docs/` |
| Phase 7 snippet | stay **0.270.0** | **yes** (second plugin file) |
| Adapter map after a future dump | later leftover; bump only if runtime changes | separate PR; not this plan |

- **files:** none for version. Never drift `marketplace.json`. Do not regenerate `copilot/plugin.json`. Do not write a CHANGELOG 0.271.0 entry.
- **acceptance:**
  1. `plugin.json` version is **0.270.0**; marketplace entry matches.
  2. No new top-level `copilot-chat` host key.
  3. `surfaces.chat.supported` is false.
  4. PR title/body (if opened) does not say Chat is protected or that write-deny shipped.
- **pre-build gates:** `python3 -m json.tool` on manifests only if touched (default: not touched). If the PR is ceiling-only markdown, marketplace JSON gates still run whole-tree — do not leave unrelated prettier debt.
depends_on_claims: [6]
- **blast radius:** process only.

---

## Dependency DAG

```
Phase 0  dated skip/partial records (local)
        │
        ▼
Phase 1  chat-ceiling.md probe kit + Phase 6 no-op sentence (committed, reversible)
        │
        ▼
Phase 2  honesty audit (grep-proof)  ── may loop a sentence fix → re-audit
        │
        ├── default ──► Phase 6 documented NO-OP (empty code)
        │
        └── dump mid-run ──► out-of-band fast-follow (NOT this leftover)
        │
        ▼
Phase 7  DEFER by default; optional parallel after Phase 1 if G7 includes it
        │
        ▼
Phase 8  land ceiling PR; stay 0.270.0
```

| Phase | Blocks | Parallel with |
|---|---|---|
| **0** | Honest “skipped” wording in Phase 1 / 6 | can draft Phase 1 text in parallel |
| **1** | Phase 2 (audit after kit text); Phase 8 | Phase 0 finalization |
| **2** | Phase 8 merge confidence | Phase 6 (empty) |
| **6** | nothing (empty) | Phase 2 |
| **7** | nothing required | Phase 1+ if forced; else never |
| **8** | merge | — |

**Critical path for this leftover:** Phase 0 → Phase 1 → Phase 2 → Phase 8.
**Not on critical path:** Phase 7 (defer), Phase 6 code (forbidden).
**Forbidden without a later dump PR:** any adapter or worktree-guard edit; `RC_CHAT_PREVIEW_MAP`; host-support `supported: true`; FOREIGN-TREE retune; new plugin/skill/agent; 0.271.0.

**Anti-serialize:** do **not** wait for the owner probe before writing Phase 0 / 1. This session records skip and ships the automatable remainder. Do **not** serialize Phase 7 before Phase 1.

---

## Unverified register (every marker has a settling step)

| Marker | Where it lives | Settling step |
|---|---|---|
| Claim 8 / CL-3 sibling Write product behavior | `[unverified — owner-gated CL-3]` | Owner runs Phase 1 kit → fill `probe-cl3.md` (keep/undo/dialog/no-op). Until then: do not claim Chat can or cannot land sibling Write. |
| Claim 10 / CL-19b live Preview fire + payload | `[unverified — owner-gated CL-19]` | Owner runs Phase 1 kit → `probe-cl19.md` with redacted stdin **and argv**. Until then: Phase 6 = no-op; `supported: false`. |
| Claim 9 docs tool names / shapes | docs-verified 2026-08-14 | Settled as **docs**. Must not be the sole basis for an adapter map (claim 13). Re-verify URLs if a later dump PR begins. |
| Claim 16 modal: docs-shaped payload leaves path empty | inference | Same dump as claim 10. If dump shows CLI-compatible `toolArgs`, revise the inference. Until then do not assume the CLI adapter understands Chat stdin. |
| Which load path fires (`.github/hooks` via adapter vs `.claude/settings.json` raw) | claim 9 documents both | `probe-cl19.md` argv row. If only settings.json fires, a later map in the adapter never sees stdin — stay honest; do **not** retune `worktree-guard.sh` in this leftover. |
| Whether Chat honors CLI top-level `permissionDecision` vs `hookSpecificOutput` | claim 9 | Record on the dump. Do not dual-emit in this leftover (no adapter edit). |
| `sessionId` vs `session_id` on Chat | Chat docs disagree | Probe records which key was present. Adapter already lifts both; do not change it here. |
| `files[]` element as object vs string | hooks-reference example is a string | Observation slot only. Do not invent `uri` / `relativePath`. |
| Chat SessionStart non-`unknown` id (prior CL-10 bonus) | still open | Bonus row on the same CL-19 dump. Not required for Phase 0–2 success. |
| Phase 7 value to consumers | preference | Defer. Ship only if G7 includes the labeled snippet. |

---

## Explicit non-goals

- No rebuild of FOREIGN-TREE / `worktree_bound` (shipped 0.268.0).
- No inventing Chat tool names in code from claim 9.
- No `RC_CHAT_PREVIEW_MAP`.
- No `host-support` Chat `supported: true`.
- No top-level `copilot-chat` host.
- No default-on pre-commit / global `hooksPath`.
- No new plugin, skill, agent, or G8 regen.
- No semver bump **for Chat enforcement**.
- No this-session VS Code Agent live-fire (structurally impossible — claim 15).
- No claiming Phase 7 is write isolation.
- No sibling Read deny.
- No Cursor / Aider / Devin rows.

---

## Marketplace constraints

- **Stack:** markdown (+ bash only if Phase 7 is included). No JSON/manifest churn on the default path.
- **Layout:** `plugins/*/templates/**` already allowed. No `.repo-layout.json` edit.
- **Host-honest:** `copilot` label stays CLI; chat `supported` stays **false**.
- **Cross-CLI storage:** probes live in the local-run tier (`.ravenclaude/runs/forge/chat-write-deny/`). The ceiling edit is the committed remainder.
- **Branch:** implement in the existing worktree `forge-chat-write-deny`. Print `git branch --show-current` before edits. Do not land plugin changes on `main` inside this worktree without a feature branch.

---

## Definition of done (implementer, not this gate)

1. Dated `probe-cl3.md` + `probe-cl19.md` exist under this run dir (skip line is enough).
2. `chat-ceiling.md` still says it is not Chat enforcement; contains CL-3 / CL-19 copy-paste steps, dump paths for this leftover, argv/debug recording, observation slots, and the Phase 6 no-op sentence.
3. `git diff` on `hooks/copilot-hook-adapter.sh` and `hooks/worktree-guard.sh` is empty. `RC_CHAT_PREVIEW_MAP` is absent from hooks.
4. `surfaces.chat.supported` is still `false`. Honesty grep is 0. Plugin version is **0.270.0**.
5. Phase 7 snippet is **absent**, or if G7 shipped it, greps as **not a Chat write-deny** and is not installer-wired.
6. If `chat-ceiling.md` changed: a PR exists; it is not sold as Chat write-deny.

That is G0 success signal (b). The cheapest automatable remainder is the kit + skip records + a documented Phase 6 no-op — not a default-off map.

---

## Execution order (post-G6 implementer)

1. Confirm worktree and branch: `git -C <worktree> branch --show-current`.
2. Write Phase 0 skip files in the run dir.
3. Patch `chat-ceiling.md` (Phase 1), including the Phase 6 no-op sentence.
4. Run Phase 2 greps; fix sentences only if needed.
5. Confirm Phase 6: no hook diff, no `RC_CHAT_PREVIEW_MAP`.
6. Leave Phase 7 deferred unless G7 said otherwise.
7. Open a PR only for the committed template (and any honesty sentence fixes). Version stays 0.270.0.

Do not implement from this file inside G6.

---

## Merge-verdict index (A vs B)

| # | Topic | Winner |
|---|---|---|
| D1 / D4 | Phase 6 without dump | **B** — documented no-op; no adapter |
| D2 | Semver | **B** — stay 0.270.0 |
| D3 | What “shim” means | **B** — docs pre-map is a shim even if default-off |
| D5 | One reversible file | **B** — `chat-ceiling.md`, not the adapter |
| D6 | Critical path | **B** — 0 → 1 → 2 → 8 |
| D7 | Phase 7 | **B defer**, A’s labeled contract if G7 includes it |
| D8 | Knowledge / CHANGELOG churn | **B** — zero unless a false-claim sentence must be fixed |
| D9 | Kit content | **B observation slots** + **A argv/debug** |
| D10 / D11 | Adapter tests / dual deny | N/A — no adapter |
| D12 | Fallback | A already encoded B; this plan *is* that fallback |

_End G6 merged plan. G3b owner-gate is law. Do not implement in G6._
