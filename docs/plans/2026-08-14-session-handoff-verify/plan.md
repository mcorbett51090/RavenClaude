# Plan — session-handoff-verify (same-host close)

**Owner:** ravenclaude-core · **Run:** `session-handoff-verify` · **G6 synthesize**
**Origin lock (audit):** `9c7f0744478d2a033d349cbf6a6a48a695ae4d76` / plugin **0.269.0**. Re-read tip + versions at implement.
**This checkout:** `handoff2` is `fdb1efeb`, **37 behind**. Implement on a branch cut from **origin/main**, not this tree's `plugins/`.

**Intent.** The shipped session-context handoff (#931 / #934) is **enabled-off**, not broken: Stop-hook nudge at soft 70 vs Grok auto-compact ~85 is coded and gated; same-host today is a new integrated terminal running positional `grok`. This plan adds host-paired spawn so Copilot Chat resumes in a **new Chat session** (prompt-file + Cmd+N / paste — guaranteed), Copilot CLI resumes in a new CLI terminal, and Grok TUI stays Grok. Live Chat URI open is owner-gated best-effort and is **not** a ship gate. Origin posture stays off. No `copilot-chat` install column.

---

## Verdict (three audit questions)

### 1. Does the shipped process work (code + gates + enablement)?

**Enabled-off. Code and CI work as designed. Automatic nag is silent until the owner opts in.**

- **Code:** Shipped on origin/main as #931 (`d054a856`, ravenclaude-core **0.266.0**) + #934 (`b2e7114c`, **0.269.0**). Scripts, Stop hook, skill, and successor-ack exist on origin (C1). This `handoff2` tree does **not** contain them (C2).
- **Gates:** **212** (nudge + leak), **213** (spawn + `grok -p` teeth), **214** (successor-ack) are registered. Human boxes on #931/#934 remain **unchecked** (C4).
- **Enablement:** Default `context_handoff.mode: off`. Origin `.ravenclaude/comfort-posture.yaml` has **no** `context_handoff:` block. Template block is commented (C3). Nudge is silent until `nag|block` (C8).
- **Manual path:** `/handoff` + `rc handoff` / `handoff-spawn.sh --recipe copy-paste` still write the brief and print a resume seed with mode off.

C9's "therefore the shipped process is not working" is an **inference, contained here**: honest wording is **enabled-off**, not broken. No implement phase cites C9. **Do not** flip origin posture.

### 2. Does it trigger before compaction at the soft threshold vs auto-compact floor?

**The floor is implemented. The automatic trigger does not fire until opted in. Auto-compact is independent of the nag.**

- Soft default **70**, clamped `1 ≤ n < auto_compact` (C6). Grok auto-compact default **85** (C5). This user's `~/.grok/config.toml` has no `[session]` block, so the meter falls back to 85.
- Live used tokens = last `updates.jsonl` `params._meta.totalTokens`. Never `signals.json.contextTokensUsed` (C7). Window ranked: same-session `signals.json.contextWindowTokens` → posture knob → Grok `context_window`. Never hardcode 500000 (C21).
- Nudge fires only when Stop `reason=end_turn`, `mode` ∈ {nag, block}, meter `status=ok` and `percent >= threshold`, not throttled, and no non-empty `handoff.md` newer than 15 minutes (C8).
- Nudge is a **Stop** hook, **not** PreCompact (C10). Compaction still happens if the model ignores the nag. Auto-compact is Grok-side.

“Before compact” means **soft nag floor**, not a compact-blocking PreCompact hook.

### 3. What is missing for Copilot Chat → Chat and CLI → CLI?

Same-host today is a **new integrated terminal + positional `grok`**. It does not open Chat. There is no Copilot CLI recipe.

| Same-host pair | Today (0.269.0) | Gap this plan closes |
|---|---|---|
| **Grok TUI → Grok TUI** | Shipped. Seed always `grok "Continue task…"`. `same-host` opens a new integrated terminal (VS Code/Cursor keystrokes) or Terminal.app. Owner-flagged `spawn: same-host`. Successor-ack SessionStart. | Regression-only. Human live box still open (C4). |
| **Copilot CLI → Copilot CLI** | Missing. Seed hard-coded `grok` (C11). Zero `copilot` matches in `handoff-spawn.sh` (C19). | Host-aware CLI seed + terminal spawn of confirmed interactive `copilot` argv. |
| **Copilot Chat → Copilot Chat** | Missing / wrong surface. Same-host always launches **terminal + grok**, never Chat (C12). Chat ≠ CLI (C13). URI `mode=agent` is docs-real (C14); new-session+prefill is **not** a product fact (C17). Chat Stop/nudge fire is unverified (C18). | **Guaranteed:** write `chat-resume.md` + print Cmd+N / New Chat + paste. **Best-effort:** C14 URI, owner-gated, fail to copy-paste, **not** a ship gate. |

**Chat successor must never launch Grok.** Copy-paste is always printed. Auto-nudge in Chat is **not claimed**; the Chat path is **user or model runs `/handoff` / the `session-handoff` skill**.

---

## Reconciled picks (no dangling conflict)

G3 gap-delta left five forks. G6 picks, all binding:

| # | Fork | Pick | Why |
|---|---|---|---|
| 1 | Chat spawn | **B guaranteed + A live as best-effort.** Write `chat-resume.md` + print Cmd+N / new-session + paste. Live `vscode://GitHub.Copilot-Chat/chat?mode=agent` (C14) is owner-gated (C17) and **must** fail to that copy-paste. URI-prefill is **not** a ship gate. | Chat is a view, not an `exec` target. C17 forbids treating new-session+prefill as a product fact. Prompt-file + Cmd+N is docs-verified (C15). |
| 2 | Host select | **Detect origin host, but `--host` wins.** Skill/user `--host chat\|cli\|grok` (aliases `copilot-chat` / `copilot-cli` accepted) overrides detection. **Never infer Chat from `TERM_PROGRAM=vscode` alone** (that is also Grok-in-VS-Code). Unknown → copy-paste, never the wrong binary. | A's anti-false-Chat rule + B's detect-when-helpful. Flag-first prevents silent wrong-product launch. |
| 3 | Gates | **New Gate 215** for Chat/CLI recipes **and** keep Gate 213 Grok teeth. Gate 215 additionally asserts a Chat/CLI seed must never emit `grok -p` **or** positional `grok` when origin host is Chat/CLI. | Clean slot after origin max 214. 213 stays Grok-byte-stable. 215 owns the new host matrix. |
| 4 | Live Chat fail | **Print copy-paste and exit 0** for the guaranteed path. A live-launch miss is **not** a hard fail. Originating session still stops only on **SUCCESSOR_ACK** when a successor actually starts. | Guaranteed path is emit+instruct. Exit 2 would punish the always-works UX. Ack wait stays Grok-only until C18/C20 prove Chat SessionStart. |
| 5 | Version / enablement / install | **0.269.0 → 0.270.0** + CHANGELOG top. Re-read origin tip at implement. **Do not** turn `context_handoff` on in origin posture. Document opt-in: `mode: nag`, `spawn: same-host`. **No** `copilot-chat` marketplace / `host-support.json` install column. | User-visible adapter, default-off, #933 honesty. |

---

## Alternatives (considered, rejected)

### Delivery model (Chat)

| # | Approach | Why rejected / kept |
|---|---|---|
| **A (URI-only live launch)** | `vscode://…?mode=agent` ± invented `prompt=` | C17 blocks treating new-session+prefill as shipping fact. Whole PR becomes owner-probe lottery. |
| **B (copy-paste-only, no file)** | Print “Cmd+N then paste” with no `chat-resume.md` | Guaranteed, but no portable artifact the next CLI can `@file`. Weaker than a run-dir file. |
| **C (VS Code prompt-file + `workbench.action.chat.open` query)** | Elegant if `query` still prefills (historical vscode#210819) | Schema undocumented on pages fetched 2026-08-14. Implement-time probe only. Risk of prefilling the *current* session. |
| **D (detect-only, no Chat delivery)** | Refuse cross-host seed; no Chat recipe | Prevents wrong-host Grok, leaves Chat users with nothing. |
| **E (picked)** | Host-detect + **`chat-resume.md` primary** + copy-paste always + optional C14 open | Correct product model for Chat (UI, not CLI). Always-works resume. Live open is owner-flagged and never required for acceptance. |

### Script shape (spawn)

| # | Approach | Why rejected / kept |
|---|---|---|
| **A1** | Three spawn scripts (grok / chat / cli) | Isolates blast; triples refuse-list / dry-run / owner-flag surface. |
| **A2 (picked)** | Host-dispatch **inside** shipped `handoff-spawn.sh` (`--host grok\|cli\|chat`) | One script, one refuse-list, one always-print copy-paste. Grok path is a branch, not a rewrite. |
| **A3** | Skill-only copy-paste; no live same-host adapter | Cheapest; does **not** close the named same-host product ask for CLI, and leaves Chat with no file artifact. |
| **A4** | Ship a Chat URI that assumes `prompt=` / `query` starts a **new** session and prefills | Treats C17 as settled. **Forbidden.** |

### Chat live-assist sub-choice

| # | Assist | Role |
|---|---|---|
| **B1** | Keystroke Cmd+N in Chat view | Documented new-session; focus-wrong if Chat is not frontmost. Fallback only, and only if focus can be stated honestly. |
| **B2** | `open vscode://GitHub.Copilot-Chat/chat?mode=agent` **without** prefill | Documented agent-mode open (C14). **Default live assist** — owner-flagged, fail to copy-paste, **not** a ship gate. |
| **B3** | `code --command` / URI `prompt=` / `query` new-session+prefill | C17 `[unverified]`. Owner probe only. Ships **off**. Never the default. |

CLI flag is **implement-time `copilot --help`**, not a design pick. If the documented form is one-shot / headless (the `grok -p` analogue), refuse it and print copy-paste + bare `copilot`. Do not invent `--prompt`.

---

## Dependency DAG + critical path

```
origin/main  (#931 / #934 shipped; do not rewrite)
 │
 ├─► P0  Verdict freeze (this FORGE run — already written)
 │
 ├─► P1  Host detect + seed matrix + chat-resume.md + always-print copy-paste
 │         --host wins; never Chat-from-TERM_PROGRAM=vscode; unknown → copy-paste
 │
 ├─► P2  Skill + command pairing (Chat /handoff is invoke-path, not Stop-path)
 │         needs P1 (--host + chat-resume.md exist)
 │
 ├─► P3  CLI same-host launch (reuse VS Code/Cursor terminal; confirmed copilot seed)
 │         needs P1
 │         ∥ P2, ∥ P4
 │
 ├─► P4  Chat live assist (C14 default; C17 probe off; fail → copy-paste + exit 0)
 │         needs P1
 │         ∥ P3
 │         not a ship gate
 │
 ├─► P5  Gate 215 + keep 213 + 0.270.0 + CHANGELOG (wire, do not enable)
 │         needs P1 + P2 on disk
 │         P3/P4 may land thin (C14-only / CLI copy-paste-only) in the same PR
 │
 └─► P6  Owner probes (C17 new-session+prefill; C18 Chat Stop fire)
           off critical path; post-merge ok
```

- **Critical path:** **P1 → P2 → P5**. A Chat/CLI user can invoke the skill, get `chat-resume.md` + Cmd+N instructions, and paste into a new session even if live launch never opens a window.
- **Parallel after P1:** P3 ∥ P4. Do **not** serialize CLI behind a Chat URI probe.
- **0.270.0 ships** with P1+P2+Gate 215 even if P3/P4 live branches are thin.
- **P4 C17 probe negative →** B2 URI or copy-paste only. **P3 `copilot --help` is one-shot →** copy-paste + bare `copilot`.
- **P1 without P3/P4** still closes the **wrong-binary** defect (Chat no longer prints `grok`).
- **Do not enable** origin `context_handoff`. **Do not** wait on C18.

---

## Phases

Implement on a branch cut from **origin/main** (`9c7f0744` or whatever tip is free). Print `git branch --show-current` before the edit run. Empty output is detached HEAD — resolve it. Do not land plugin edits on this stale `handoff2` `main`.

### P0 — Freeze audit artifacts (this FORGE run)

depends_on_claims: [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 19]

**Goal.** Written verdict. No product code.

**Work.** This file. Keep work on a branch from origin/main for the implement PR.

**Pre-build gates.** None (docs-only run artifacts under `.ravenclaude/runs/forge/…`).

**Acceptance.** Three audit answers written; C9 wording is **enabled-off** not broken; C17/C18 marked unsettled for build.

---

### P1 — Host-aware seed + `chat-resume.md` + always-print copy-paste

depends_on_claims: [11, 12, 13, 15, 19]

**Goal.** Same script, three seeds. Unset/`grok` host is **byte-stable** with today's positional `grok "…"` (C11). `chat` never emits `grok`. `cli` never emits `grok`. Copy-paste is always printed. Chat recipe **writes** `.ravenclaude/runs/<task-id>/chat-resume.md` and prints Cmd+N / New Chat / paste. No window is opened for Chat/CLI in this phase.

**Host selection (binding).**

1. **`--host grok|cli|chat`** (aliases `copilot-cli` / `copilot-chat` accepted) wins when set.
2. Else `RC_HOST` / `THING_HOST` if they name one of those three.
3. Else detect: `GROK_AGENT` / `GROK_HOOK_EVENT` / `GROK_SESSION_ID` ⇒ `grok`; Copilot CLI env/process markers (confirm at implement) ⇒ `cli`.
4. **Never** infer `chat` from `TERM_PROGRAM=vscode` or `__CFBundleIdentifier` alone. That is also Grok-in-VS-Code (C12).
5. Uncertain / unknown ⇒ host label `unknown`, recipe **copy-paste only**, never a binary.

**Files (extend, do not rewrite Grok).**

- `plugins/ravenclaude-core/scripts/handoff-spawn.sh` — `--host`, `detect_origin_host`, seed matrix, Chat emit+instruct, always-print copy-paste. Origin L69 seed string and L71–75 refuse-list stay the **grok** branch. Do not retune Grok refuse tokens.
- `plugins/ravenclaude-core/scripts/context-handoff.py` — `seed_text()` grows a `host` argument; `handoff-seed.txt` matches the spawn seed. `detect_host()` may accept `chat` / `cli` when `--host` / `RC_HOST` / `THING_HOST` says so. After a non-empty `handoff.md`, write/refresh `chat-resume.md` when host is `chat` (short: read `handoff.md`, next steps, anti-`/fork`). Prefer a **separate file** so the Grok seed stays positional-CLI clean.
- `plugins/ravenclaude-core/bin/rc` — usage currently lists `copy-paste|os-terminal` and "fresh Grok window". Mention `--host` and the three pairs. Verb still `exec`s `handoff-spawn.sh`.
- Optional hygiene (not load-bearing): `context-usage-meter.py` `read_posture` spawn regex is still `copy-paste-only|os-terminal` and missed #934's `same-host`. Align only if this file is already open.

**Chat print block (always, host=chat or unknown-in-Chat-skill):**

```
# Copilot Chat resume (same window, NEW session):
# 1. Cmd+N / Ctrl+N  (or Command Palette: "Chat: New Chat")
# 2. Paste the block below  OR  open chat-resume.md / handoff.md via @file
```

Cite C15 shortcuts. **Never** `/fork` (fork copies bloated history). **Never** `grok "…"`.

**Pre-build gates.**

- `command -v copilot` / `copilot --help` at implement time before writing a CLI seed. If help documents an interactive positional `PROMPT`, use it. If the only prompt flag is one-shot/headless, **do not emit it**; CLI copy-paste is `cd <root>` + `copilot` + the pointer paragraph as a separate paste.
- Layout: `plugins/*/scripts/**` already allowed. No new glob. No new top-level directory.
- Do not add a `copilot-chat` key to `knowledge/host-support.json` (C13).

**Acceptance tests.**

- `--dry-run --host grok` (or unset): stdout contains `grok "` + run-dir path; absent `grok -p`, `--single`, `--prompt-file`, `--prompt-json`, `SessionStart` as a positive seed (Gate 213 still green).
- `--dry-run --host chat`: writes/mentions `chat-resume.md`; stdout contains Cmd+N / New Chat and the pointer path; **absent** `grok "`; absent `open -na Terminal`; **no** hard dependency on `prompt=` URI.
- `--dry-run --host cli`: stdout contains `copilot` (or the `--help`-confirmed interactive form) + the pointer; **absent** `grok "`; absent a refused one-shot flag.
- Missing `handoff.md` still exits 1 and prints no host seed argv (any `--host`).
- `--recipe same-host` without posture `spawn: same-host|os-terminal` still says `owner-flagged` and still prints copy-paste (C12).
- `TERM_PROGRAM=vscode` + unset `--host` + `GROK_AGENT=1` still seeds **grok**, not Chat.
- Unset `--host` + `TERM_PROGRAM=vscode` + no Grok/CLI markers ⇒ `unknown` + copy-paste, **not** Chat URI and **not** `grok` unless a Grok marker is present.

**Blast.** Two existing scripts + `rc` usage. No live Chat/CLI launch. Reversible.

---

### P2 — Skill + command: same-host pairing; Chat `/handoff` without claiming auto-nudge

depends_on_claims: [12, 13, 15]

**Goal.** The model that is actually running `/handoff` (or the `session-handoff` skill) names its own host and passes `--host`. Chat → Chat. Grok TUI → Grok TUI. Copilot CLI → Copilot CLI. Chat auto-nudge is **not** a success criterion (C18 is a non-claim).

**Files.**

- `plugins/ravenclaude-core/skills/session-handoff/SKILL.md`
  - Gotchas: seed is host-paired; Chat successor **must not** launch Grok; never `/fork` (C15); copy-paste always printed; live launch owner-flagged.
  - Procedure: resolve originating host (you are Chat / Grok / Copilot CLI — **do not guess from `TERM_PROGRAM=vscode` alone**) → `rc handoff --task-id <id> --host <pair> --recipe same-host` (or `copy-paste`).
  - Out of scope: rewrite the Grok path; other-host adapters beyond these three pairs; a `copilot-chat` install column (C13); enabling origin `context_handoff`.
  - Honesty: **Chat Stop/nudge fire is unverified.** This skill is the Chat path when the **user or the model** invokes it.
  - Description: keep `/handoff`, fresh window, context hot; add Chat "new chat session" / CLI "new copilot session" trigger phrases so Chat/CLI can load the skill. Chat loads project skills from `.claude/skills`. `/handoff` the Claude slash command is **not** claimed as a Chat-native command — the skill is.
- `plugins/ravenclaude-core/commands/handoff.md` — thin: after write, call `rc handoff` with the host the skill resolved. Do not hard-code grok.
- `plugins/ravenclaude-core/skills/session-handoff/templates/handoff.md` Do-not-redo: add "Chat/CLI successor must not launch `grok`." Keep existing grok `-p` / `/fork` negations.

**Pre-build gates.**

- `python3 scripts/check-frontmatter.py` clean. Quoted `description:`. Description ≤ 300 chars.
- Skill body names `grok -p`, `/fork`, `SessionStart`, `40%` only inside **negations**.
- Gate 206: do not put an artifact-count literal in plugin/marketplace descriptions.
- Do not write "Chat is protected" or add `copilot-chat` to `host-support.json` `hosts` (C13).

**Acceptance tests.**

- Reviewer grep: SKILL.md contains `chat` / "new Chat" and a **must not launch grok** instruction.
- Reviewer grep: no positive instruction to `open -na Terminal` from a Chat host.
- `yaml.safe_load` on SKILL.md + `commands/handoff.md`.
- Skill still says never `/fork` (C15) and never PreCompact.

**Blast.** Skill + command + template. No hook change. Chat path works when invoked; silent if never invoked.

---

### P3 — Copilot CLI same-host: new terminal running `copilot` + pointer

depends_on_claims: [11, 12, 19]

**Goal.** When `--host cli` and `--recipe same-host` and posture `spawn: same-host`, reuse the **existing** VS Code/Cursor integrated-terminal keystroke launch (C12) but exec a **CLI** launch script, not `grok`. Grok branch untouched.

**Files.** `plugins/ravenclaude-core/scripts/handoff-spawn.sh` only (extend `launch-successor.sh` generation). `spawn_vscode_terminal` / `spawn_cursor_terminal` stay; the script they type becomes host-specific. `os-terminal` + CLI host opens Terminal.app with the CLI seed, not grok.

**Pre-build gates.**

- Implement-time: `copilot --help` (and `gh copilot --help` if that is the on-PATH binary). Record the exact interactive form in the PR body. **Do not invent flags.**
- Refuse one-shot / headless CLI flags the same way origin L71–75 refuse `grok -p`. If help only documents a one-shot prompt, live launch is `copilot` with no prompt argv; copy-paste still carries the pointer paragraph.
- `command -v copilot` missing → do not launch; print copy-paste; **exit 0** (guaranteed path succeeded).
- No live Terminal.app / osascript in CI. `--dry-run` only.

**Acceptance tests.**

- Dry-run `--host cli --recipe same-host` + posture flag + `TERM_PROGRAM=vscode`: `detected-ui=vscode`, names a VS Code terminal, **absent** `open -na Terminal`, **absent** `grok "`, present `copilot`.
- Dry-run same without posture flag: `owner-flagged` + copy-paste, no launch.
- Mutant that emits `copilot --prompt` / `-p` / a documented one-shot flag **if that flag was classified one-shot** is caught by Gate 215 teeth (CLI analogue of Gate 213).
- Grok dry-run fixtures from Gate 213 remain green (C11).

**Blast.** One existing script. Live launch can open a terminal — owner-flagged, always-print copy-paste. Fail-open.

---

### P4 — Copilot Chat live assist (C17 owner-gated; fail to copy-paste; not a ship gate)

depends_on_claims: [14, 15]

**Goal.** When `--host chat` and `--recipe same-host` and posture `spawn: same-host`, try a **small** live assist that opens agent-mode Chat. **Do not assume new-session+prefill works.** Default assist is C14 only. C17 is an owner probe. **URI-prefill is not a ship gate.**

`[unverified — premise not disconfirmed: current vscode:// / code --command can start a *new* Chat session *and* prefill the pointer]`. One reversible function. Feature-flagged by the existing `spawn: same-host` knob. Fail to the P1 copy-paste block and **exit 0**.

**Files.**

- `plugins/ravenclaude-core/scripts/handoff-spawn.sh` — add **one** function, e.g. `spawn_copilot_chat()`. No new module.
  - Always write `chat-resume.md` and print the P1 Chat copy-paste (Cmd+N / Ctrl+N new session + pointer) **before** any live attempt (C15).
  - Default live assist: `open 'vscode://GitHub.Copilot-Chat/chat?mode=agent'` (C14). This opens agent mode. It does **not** claim a new session and does **not** prefill.
  - Optional owner probe (same function, behind an explicit env or a comment-gated branch — **not** a new posture key): `code --command workbench.action.chat.newChat` and/or a URI `prompt=` / `query` **if** the this-session probe shows it starts a **new** session and prefills. If the probe is negative or not run: do not ship that branch enabled.
  - Never `exec grok`. Never keystroke a grok seed into a Chat host.
  - If `open` / `code` missing or the URI fails: print copy-paste, `launched=0`, **exit 0**. Live-launch miss is not a hard fail.
  - Do **not** wait on `successor-ack.json` as a Chat success signal. Chat SessionStart fire is C18 / unverified. Originating session still stops only on SUCCESSOR_ACK when a successor **actually** starts (Grok path unchanged).

**Pre-build gates.**

- C14 URI is the only live Chat command that may ship **on** without a this-session probe.
- C17 branch ships **off** unless the implementer records: command run, stdout/stderr, whether a **new** Chat session appeared, whether the pointer was prefilled. Expected-if-true ≠ expected-if-false.
- No `prompt=` in the default seed string.
- No Chat hook registration. No claim that Stop will nag in Chat.
- Accessibility keystroke Cmd+N (B1) is allowed only as a documented fallback inside the same function, and only if Chat view focus can be stated honestly; otherwise skip.

**Acceptance tests.**

- Dry-run `--host chat --recipe same-host` + posture flag: stdout contains Cmd+N / new session and path to `chat-resume.md` / `handoff.md`; **may** mention `vscode://GitHub.Copilot-Chat/chat?mode=agent` as best-effort; **absent** `grok "`; **absent** a `prompt=` query unless the C17 branch is explicitly under test.
- Dry-run without posture flag: `owner-flagged` + Chat copy-paste, no `open` / `code --command`.
- Live miss (simulated: `open`/`code` absent): still prints copy-paste; **exit 0**.
- Live (human, owner machine, **unchecked box on the PR**): with flag on, agent-mode Chat opens **or** copy-paste is sufficient; this tab is not reused as the successor. Prefill is recorded as pass/fail, never silently assumed.
- Gate 215 teeth: a mutant that emits `grok "` or `grok -p` for `--host chat` is caught.

**Blast.** One function in one existing file. Reversible. Owner-gated. Fail to copy-paste + exit 0. This is the only phase that *mentions* C17, and it does **not** depend on C17 being true.

---

### P5 — Gate 215 + keep 213 + 0.270.0 + CHANGELOG (wire, do not enable)

depends_on_claims: [1, 4, 13]

**Goal.** Count the user-visible adapter, keep Grok gates green, add Gate **215**, do **not** enable `context_handoff` on origin, do **not** add a `copilot-chat` install column.

**Files.**

- `plugins/ravenclaude-core/hooks/tests/test-gate215-handoff-host-spawn.sh` — Gate **215** (next free after origin highest **214**). Shape = Gate 213: bash 3.2, fixtures only, `--dry-run`, bidirectional teeth.
- `plugins/ravenclaude-core/hooks/tests/test-gate213-handoff-spawn.sh` — **keep Grok teeth**. Update the mutant needle only if P1's grok seed assignment **must** move; prefer not to. If the assignment line moves, update the needle in the same PR. Gate 213 continues to refuse `grok -p` / `--single` / `--prompt-file` / `--prompt-json`.
- `scripts/audit-gates.sh` — register 215 in (1) `--check` dispatcher, (2) main sequence after 214, (3) `Supported:` string. GREP THE SUITE OUTPUT FOR `215`.
- `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` ravenclaude-core entry: origin tip **0.269.0 → 0.270.0** (or one minor above whatever is free on origin at implement). Marketplace catalog `metadata.version` is **not** this plugin's version — do not touch it unless a separate catalog rule requires it.
- `plugins/ravenclaude-core/CHANGELOG.md` — new **0.270.0** top entry (file exists → keep current). Honest "Not claimed" bullets: Chat Stop/nudge (C18); C17 prefill; Chat is not a protected install host; origin posture stays off.
- `plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml` — comment-only: spawn values unchanged (`copy-paste-only | same-host | os-terminal`); note that `same-host` is **host-paired** (Chat→Chat, Grok→Grok, CLI→CLI). Document opt-in:

  ```yaml
  # context_handoff:
  #   mode: nag          # off (default) | nag | block
  #   spawn: same-host   # copy-paste-only | same-host | os-terminal
  #   threshold_percent: 70
  ```

  Do **not** uncomment the block on origin `.ravenclaude/comfort-posture.yaml` (C3).
- Optional pointer in `knowledge/copilot-chat-customization.md` Honesty: `/handoff` spawn is skill-invoked; Preview Stop fire still `[unverified]`. Still no `copilot-chat` host key (C13).

**Gate 215 fixture list (follow 213/214).**

- `--host chat` dry-run: no `grok "`; no `grok -p`; has new-session / Cmd+N; has `chat-resume.md` or pointer path.
- `--host cli` dry-run: no `grok "`; no `grok -p`; has `copilot` (or recorded interactive form); no one-shot flag.
- Unset `--host`: still `grok "` (regression — Gate 213 still owns this).
- Chat same-host without owner flag: `owner-flagged` + copy-paste.
- `--must-fail-chat-grok` teeth: plant `seed="grok` on the Chat host branch (or delete the Chat refuse); mutant **must** emit `grok "`; the assertion must catch it (exit 1 on mutant emit, same as Gate 213 `--must-fail-headless`).
- Optional `--must-fail-cli-headless` if a one-shot CLI flag was classified at implement time.
- `TERM_PROGRAM=vscode` + `GROK_AGENT=1` + unset `--host` still seeds grok, not Chat.
- `bash -n` on `handoff-spawn.sh`.
- No live `osascript` / `open` / `code --command` in CI.

**Pre-build gates.**

- Branch is not `main`. Versions in plugin.json and marketplace.json match before commit.
- P1–P2 files exist on disk. `git diff --name-only` does **not** include `hooks/compact-anchor.sh` or `scripts/compact-anchor.py`.
- No `context_handoff:` block introduced in origin `.ravenclaude/comfort-posture.yaml`.
- No `copilot-chat` key under `host-support.json` `hosts`.
- Regen if descriptions change: `generate-dashboards.py`, `generate-index-dashboard.py`, `generate-copilot-plugin.py`. Gate 206 forbids count literals — do not write "N skills".
- `npx prettier@3.9.4 --write` then `--check`; `ruff check .`; `scripts/audit-gates.sh` including 212–215.

**Acceptance tests (falsifiable).**

```
git branch --show-current   # not main, not empty
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool plugins/ravenclaude-core/.claude-plugin/plugin.json >/dev/null
python3 scripts/check-frontmatter.py
python3 scripts/check-marketplace-claims.py
bash -n plugins/ravenclaude-core/scripts/handoff-spawn.sh
npx --yes prettier@3.9.4 --write . --log-level warn
npx --yes prettier@3.9.4 --check . --log-level warn
python3 -m ruff check .
bash plugins/ravenclaude-core/hooks/tests/test-gate212-handoff-nudge.sh
bash plugins/ravenclaude-core/hooks/tests/test-gate213-handoff-spawn.sh
bash plugins/ravenclaude-core/hooks/tests/test-gate213-handoff-spawn.sh --must-fail-headless; test $? -ne 0
bash plugins/ravenclaude-core/hooks/tests/test-gate214-handoff-successor-ack.sh
bash plugins/ravenclaude-core/hooks/tests/test-gate215-handoff-host-spawn.sh
bash plugins/ravenclaude-core/hooks/tests/test-gate215-handoff-host-spawn.sh --must-fail-chat-grok; test $? -ne 0
scripts/audit-gates.sh --check 213
scripts/audit-gates.sh --check 215
# then full scripts/audit-gates.sh before the PR
```

Human boxes on the PR (C4 shape — leave `[ ]` until a human ticks them):

- [ ] Grok `/handoff` + `spawn: same-host` still opens a **new Grok TUI** (not Chat).
- [ ] In Copilot Chat, user/model runs the skill / `/handoff`: `chat-resume.md` + copy-paste names **new Chat** and does **not** mention `grok`; pasting into Cmd+N Chat continues the task.
- [ ] Chat `spawn: same-host`: agent-mode URI opens **or** copy-paste is enough (exit 0 either way); this thread is not the successor. Prefill recorded separately (C17).
- [ ] Copilot CLI `spawn: same-host`: new terminal runs `copilot` (or the `--help`-confirmed interactive form) with the pointer; not `grok`.
- [ ] Origin posture still has no live `context_handoff:` block after merge.

**Blast.** User-visible 0.270.0. Reversible by revert. **No migration for default-off.** Consumers who never set `context_handoff` see no new Stop nag. Chat/CLI same-host launch still requires the existing owner spawn flag.

---

### P6 — Owner probes (non-blocking; post-merge ok)

depends_on_claims: []

C17 and C18 are **not** load-bearing. This phase settles them for a possible follow-up, not for 0.270.0.

**Work (owner machine with live VS Code Chat + optional Preview hooks).**

1. **C17:** can `code --command` / URI start a **new** session and/or prefill? Record yes/no + VS Code / Copilot Chat version. If yes, a later PR may promote B3 behind the same `spawn: same-host` flag. If no, leave P4 as C14 + copy-paste.
2. **C18 / CL-19:** does Chat Preview fire Stop / `handoff-nudge`? If no, Chat path stays skill-invoke forever in honesty docs. If yes, a later PR may document Chat nag — **not** part of 0.270.0 must-ship.

**Acceptance.** Probe notes in the PR or `.ravenclaude/runs/…`. Guaranteed path already merged without them.

---

## G1 inferences — settling or containing

| id | kind | This plan |
|---|---|---|
| **C9** | inference (enabled-off ⇒ "not working") | **Contained in the verdict.** No implement phase cites C9. Wording is enabled-off, not broken. |
| **C17** | inference / BLOCK if treated as product fact | **P4 mentions it; P6 settles it.** Owner-gated, one function, fail to copy-paste + exit 0. Default live assist is C14 (observation). URI-prefill is **not** a ship gate. P4 `depends_on_claims` is `[14, 15]` only. |
| **C18** | inference / owner-gated | **Non-claim.** No `depends_on_claims` cites C18. Chat path is skill invoke (P2). Settled by P6 owner probe if at all. |

C5, C14, C15, C16 are outside-repo observations with this-session sources. **C16 is unused** — Chat has a visible meter, but we do not build a Chat Stop detector on it.

---

## Risk matrix

| Risk | Source | Severity | Mitigation |
|---|---|---|---|
| Chat same-host inferred from `TERM_PROGRAM=vscode` launches Chat from a Grok TUI (or grok from Chat) | C12 | High | Detection order in P1; `--host` wins; skill passes `--host`; Gate 215: unset host + `GROK_AGENT` stays grok; vscode-only + no markers ⇒ unknown + copy-paste. |
| Chat successor prints `grok "…"` or `grok -p` | C11 + product ask | High | P1 seed split + Gate 215 `--must-fail-chat-grok` + Gate 213 Grok refuse-list kept. |
| C17 treated as a product fact / URI-prefill becomes a ship gate | C17 | High | P4 only; owner-gated; default is C14 without prefill; fail to copy-paste + exit 0; P6 settles. |
| Chat auto-nudge assumed, so Chat users never `/handoff` | C18 | High | Skill honesty (P2); success signal is invoke-path; do not register a Chat Stop hook. |
| CLI `--prompt` is one-shot (grok `-p` analogue) | C19 | Med | Implement-time `copilot --help`; refuse one-shot; copy-paste + bare `copilot`. |
| Origin posture silently enabled | C3 / C9 | High | P5 acceptance: no `context_handoff:` in origin posture. Document opt-in in the template comment only. |
| `copilot-chat` install column | C13 | High | Explicit out of scope; reviewer grep `host-support.json`. |
| Gate 213 mutant needle drifts | C4 / C11 | Med | Prefer not to move the grok `seed=` assignment; if moved, update 213 in the same PR. |
| Human same-host / long-session nag still unchecked | C4 | Med | PR Human boxes stay `[ ]` until a human ticks them; CI stays `--dry-run`. |
| Stale checkout implementation | C2 | High | Branch from origin/main; do not edit `handoff2/plugins/` as if it were shipped. |
| Live Chat fail treated as hard error | gap-delta #5 | Med | Guaranteed path exit 0; `launched=0` is informational. Originating session waits on SUCCESSOR_ACK only when a successor actually starts. |
| Origin tip moves past 0.269.0 | C1 | Med | Re-read `plugin.json` + marketplace at implement; bump to next free minor. |

---

## What this plan will not do

- Rewrite the shipped Grok seed, AppleScript terminal launch, successor-ack, meter, or Stop nudge.
- Treat C17 as settled or ship `prompt=` as default. URI-prefill is not a ship gate.
- Claim Chat hooks fire (C18). Plan the Chat path as **user or model runs the skill**.
- Add a `copilot-chat` marketplace / `host-support.json` install column (C13).
- Enable `context_handoff` on origin posture (C3 / C9 contained as enabled-off).
- Infer Chat from `TERM_PROGRAM=vscode` alone (that is also Grok-in-VS-Code).
- Launch Grok from a Chat or Copilot CLI successor.
- Touch `compact-anchor` / add PreCompact / add a Chat-only Stop hook.
- Wait on `successor-ack.json` for Chat unless SessionStart fire is owner-proved (C18/C20).

---

## Versioning + gate slot (re-read at implement)

| Artifact | Origin now | This work |
|---|---|---|
| `plugins/ravenclaude-core/.claude-plugin/plugin.json` `version` | **0.269.0** | **0.270.0** (or next free minor) |
| `.claude-plugin/marketplace.json` ravenclaude-core `version` | **0.269.0** | lockstep |
| `CHANGELOG.md` | top `## 0.269.0` | new `## 0.270.0` top entry |
| New gate | highest **214** | **215** host-pair spawn + Chat/CLI-must-not-emit-grok teeth |
| Gate 213 | Grok spawn + headless teeth | **kept**; do not replace with 215 |
| Origin posture | no `context_handoff:` | **unchanged** (document opt-in: `mode: nag`, `spawn: same-host`) |
| `host-support.json` `hosts` | no `copilot-chat` | **unchanged** |

Minor bump: user-visible spawn pairing. Re-read both version fields at implement if tip has moved past 0.269.0.

---

## Files expected to change in the implement PR (0.270.0)

| Path (on origin tree) | Change |
|---|---|
| `plugins/ravenclaude-core/scripts/handoff-spawn.sh` | `--host`, detect (no vscode→Chat), seed matrix, `chat-resume.md` emit, CLI recipe, C14 best-effort |
| `plugins/ravenclaude-core/scripts/context-handoff.py` | `seed_text(host)`, `handoff-seed.txt`, Chat resume skeleton |
| `plugins/ravenclaude-core/skills/session-handoff/SKILL.md` | Same-host product wording; Chat/CLI; invoke-path honesty |
| `plugins/ravenclaude-core/skills/session-handoff/templates/handoff.md` | Chat/CLI must-not-launch-grok Do-not-redo |
| `plugins/ravenclaude-core/commands/handoff.md` | Pass resolved `--host`; do not hard-code grok |
| `plugins/ravenclaude-core/hooks/tests/test-gate215-handoff-host-spawn.sh` | New Gate 215 |
| `plugins/ravenclaude-core/hooks/tests/test-gate213-handoff-spawn.sh` | Keep Grok teeth; needle only if seed assignment moves |
| `scripts/audit-gates.sh` | Register 215 |
| `plugins/ravenclaude-core/bin/rc` | Usage string for `--host` / recipes |
| `plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml` | Comment: host-paired `same-host`; opt-in `mode: nag` |
| `plugins/ravenclaude-core/knowledge/copilot-chat-customization.md` | Honesty cross-link (optional) |
| `plugins/ravenclaude-core/.claude-plugin/plugin.json` | 0.270.0 |
| `.claude-plugin/marketplace.json` | lockstep version |
| `plugins/ravenclaude-core/CHANGELOG.md` | 0.270.0 entry + Not claimed |

**Unchanged by design:** nudge meter math, Gate 212 semantics, compact-anchor, Grok positional seed forbid list, default posture off, no install column, no new top-level directory (no layout-glob update).

---

## Definition of done

- [ ] Branch cut from **origin/main**, not this 37-behind `handoff2` checkout. `git branch --show-current` is non-empty and not `main`.
- [ ] Verdict stands: **enabled-off** + soft-70 Stop-hook + Grok same-host shipped owner-flagged; human live still open.
- [ ] Guaranteed Chat path: `chat-resume.md` + Cmd+N / New Chat + paste. No `grok` in Chat/CLI seed output.
- [ ] `--host` wins; never Chat-from-`TERM_PROGRAM=vscode`; unknown → copy-paste.
- [ ] Live C14 URI is owner-gated best-effort; miss → copy-paste + **exit 0**. URI-prefill is not a ship gate.
- [ ] Gates **212 / 213 / 214 stay green**. Gate **215** added with `--must-fail-chat-grok` teeth. `scripts/audit-gates.sh --check 213` and `--check 215` pass; full `audit-gates.sh` before the PR.
- [ ] ravenclaude-core **0.269.0 → 0.270.0** (or next free) in `plugin.json` + marketplace lockstep + CHANGELOG top.
- [ ] Origin `.ravenclaude/comfort-posture.yaml` still has **no** `context_handoff:` block. Template documents opt-in (`mode: nag`, `spawn: same-host`).
- [ ] No `copilot-chat` key in `host-support.json` / marketplace install column.
- [ ] `npx prettier@3.9.4 --write` then `--check`; `python3 -m ruff check .`; `python3 scripts/check-frontmatter.py`.
- [ ] No new top-level directory → **no** `.repo-layout.json` glob update.
- [ ] Human boxes on the PR left `[ ]` until a human runs them (C4).
- [ ] C17 / C18 remain owner-gated probes (P6), not merge blockers.

---

## Success signal (maps to scope)

1. Written verdict: **enabled-off** + soft-threshold implemented + Grok same-host shipped owner-flagged; human live still open.
2. Bounded plan: Chat→Chat via **`chat-resume.md` + Cmd+N (always)**; CLI→CLI via **confirmed terminal seed**; Grok→Grok **regression-only**; version **0.270.0**; Gate **215** added and Gate **213** kept; C17/C18 not load-bearing for merge.
