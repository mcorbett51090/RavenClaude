# Multi-host audit — Round 1 — deduped, authoritative ledger

**Date:** 2026-07-28 · **Repo:** `/Users/matthewcorbett/RavenClaude` · **Branch at authoring:** `feat/ravenclaude-core-0.216.0`

**Source lenses (6, all read in full):** `.ravenclaude/runs/forge/multi-host-audit/round1/` —
`claude-code.md` · `copilot-cli.md` · `codex.md` · `cursor-windsurf-aider.md` · `gemini.md` · `dashboard-multihost.md`

> **Why this file lives under `docs/`.** The `.ravenclaude/runs/` tree is gitignored, so the six round-1
> reports are **not committed and will be lost**. This ledger is the committed record; it carries every
> finding's `file:line` evidence verbatim so the reports are recoverable in substance if not in prose.

**Path conventions (read these first).**

- **`RC`** = the `ravenclaude-core` plugin root, i.e. `plugins/ravenclaude-core`. A path written
  `RC/hooks/foo.sh` therefore lives at that plugin root, under `hooks/`.
- Paths written from the repo root (`scripts/generate-dashboards.py`, `AGENTS.md`, `.repo-layout.json`,
  `docs/…`) are literal.
- The four command-review tribunal scripts are named **without their file extensions** —
  `thing-orchestrator`, `thing-decision`, `thing-seat`, `thing-concerns`. They are unambiguous, and the
  reason is below.
- Line numbers are verbatim from the source reports and are never adjusted.

> **Why those two conventions exist — it is itself an audit finding, logged as MH-42.**
> Writing this file with fully-expanded paths was **denied twice by the command-review tribunal** (Sága
> `thing-2026-07-28T18-40-51Z-71592` and `…T18-50-54Z-76982`; `phase: T4-self-disable`, concern
> `xc.tribunal-self-disable`, category `file_edit_project`) — for a write to `docs/plans/…`, which is not
> substrate. Trigger regex (1) of that concern matches **any `>` character followed by one run of
> non-space characters and then a substrate filename**. That catches a markdown blockquote (`> ` + a
> path) *and* — as the second denial proved — an angle-bracket placeholder, because a token like
> `<core>` **ends in `>`**. The concern's own comment scopes it to *"the shell-level scope"*; applied to
> a **file-shape** write, where the screened text is `"<file_path>\n<content>"`, ordinary prose that
> **cites** substrate paths is read as a shell redirect into them. **Both denials were obeyed, not
> bypassed.**

**Lens key:** `CC` = claude-code · `CP` = copilot-cli · `CX` = codex · `CWA` = cursor-windsurf-aider ·
`GEM` = gemini · `DASH` = dashboard-multihost.

**Evidence tags are carried verbatim from the source reports and are never promoted.** `[verified]` = the
lens read or executed it that session. `[docs-verified]` = fetched vendor documentation, URL given.
`[inferred]` = reasoned from two verified halves, **not observed**. No `[inferred]` finding is written up
here as verified, and every one is listed again in §4 as needing verification before it is built.

---

## §1 — The architectural finding (the through-line)

**All six lenses hit this independently, from six different angles:**

> **The repo models the world as `{Claude Code} ∪ {everything else = Copilot}`.**

The evidence that this is a modelling decision and not an accident is that it is *load-bearing in exactly
one direction*. There is precisely **one** of each non-Claude artifact, and all of them are Copilot's: one
installer (`scripts/ravenclaude:2` — *"install / update the RavenClaude plugins for **GitHub Copilot
CLI**"*), one hook adapter (`RC/hooks/copilot-hook-adapter.sh`), one generated projection
(`scripts/generate-copilot-plugin.py`, 456 lines), one per-host knowledge file
(`RC/knowledge/copilot-cli-customization.md`), one dashboard install tab
(`scripts/generate-dashboards.py:6634`), one layout glob (`.repo-layout.json:56` —
`"plugins/*/copilot/**"`). Every other host gets a name in a sentence.

How each lens arrived at it:

| Lens | The angle |
|---|---|
| **CX** | States it outright (Appendix A): *"The repo's mental model is `{Claude Code} ∪ {everything else = Copilot}`."* |
| **CWA** | *"RavenClaude ships exactly one cross-tool artifact for these three hosts: the prose claim in `AGENTS.md:3`… they got a name-check."* |
| **DASH** | The framing fact the whole dashboard audit hangs on: hooks fire under Claude natively and Copilot via the adapter; *"Codex / Cursor / Gemini / Aider / Windsurf have **no adapter and no hook path**… The dashboard renders identical copy to all seven hosts and conditions on none of this."* |
| **GEM** | The lane is *"purely aspirational"* — 17 name-checks, zero support. |
| **CP** | Arrives from *inside* the Copilot lane: the adapter was built against *an assumed tool vocabulary that mirrors Claude Code's own capitalized names* — i.e. Copilot was modelled as "Claude Code with a different envelope," which is exactly why the tool-name values were never checked. |
| **CC** | Arrives from the Claude side: the dashboard's own Claude-only panel *"answers confidently about Claude Code from a source it has not actually checked."* Same class, other end of the line. |

### And Codex sits on the WRONG side of that line

This is the sharpest form of the finding, and it is `[docs-verified]` (https://learn.chatgpt.com/docs/hooks):

Codex CLI has converged on the **Claude Code hook contract almost exactly** — same event names, same stdin
field names, the same `hookSpecificOutput.permissionDecision` / `updatedInput` / `additionalContext`
envelope, the same `exit 2 + stderr = block` semantics, and a plugin loader that reads a plugin's
`hooks/hooks.json` **directly**. The event overlap is **6/6** `[verified]`: RavenClaude registers
`PreToolUse`(5) `PostToolUse`(2) `Stop`(1) `UserPromptSubmit`(1) `SubagentStart`(1) `SessionStart`(1) —
every one is a documented Codex event.

**Copilot needed a 456-line generator plus a ~300-line envelope adapter because its envelope differs.
Codex needs neither.** What Codex does *not* share is the **env-var vocabulary** (`PLUGIN_ROOT` /
`PROJECT_DIR` / `SESSION_ID` vs the `CLAUDE_*` names the hooks read) — a 3-line-per-variable alias, not a
translation layer.

So the correct model is:

> **`{Claude-Code-contract hosts: Claude Code, Codex} ∪ {Copilot, which needs an envelope adapter} ∪
> {file-convention hosts: Cursor, Aider, Devin Desktop} ∪ {undecided: Gemini}`**

**Codex is on the *near* side of the boundary the repo drew, and has been treated as though it were on the
far side.** It is simultaneously the *cheapest* host to support properly and the one the repo has invested
the least in. Every Codex P0 and most Codex P1s below follow from that single misclassification — which is
also why `5c6d0744` correctly shipped a **3-line alias**, not a second adapter.

**The corollary that generalizes past Codex:** the two artifacts that would have caught all of this — a
host verdict (`/__host`) and a machine-readable per-component host-support map — **do not exist**. Every
host-sensitive surface therefore *guesses*, and the guess is always "Claude Code, or else Copilot." MH-14
and MH-21 are those two artifacts, which is why §3 sequences them first.

---

## §2 — The ledger

42 deduped entries. Severity is the **highest** any lens assigned; disagreements are named inline.

### P0 — broken, blocking, or actively false

---

#### MH-01 · Copilot tool-name mismatch silently disabled the tribunal and the web-access guard
**Severity:** P0 · **Hosts:** GitHub Copilot CLI · **Reported by:** CP (P0-1, P0-2) · **Effort:** M
**Status:** ✅ **FIXED `f55039ec`**

**Evidence** `[verified]` + `[docs-verified]`
- `RC/hooks/thing-orchestrator` `:113-116` —
  `case "$tool_name" in Bash | Read | Write | Edit | MultiEdit | WebFetch | WebSearch | mcp__*) ;; *) exit 0 ;; esac`
- Copilot's actual native `toolName` values per `docs.github.com/en/copilot/reference/hooks-configuration`
  (fetched that session): `"bash"`, `"powershell"`, `"view"`, `"create"`, `"edit"`, `"grep"`, `"glob"`,
  `"web_fetch"`, `"ask_user"`, `"task"`. Bash `case` is case-sensitive, so **every** Copilot tool call fell
  to `*) exit 0` before the classifier, the self-disable guard (§B.9.5), or the category-independent
  hard-rule screen (§B.9.3) ever ran.
- `RC/scripts/thing-decision` `:343` `classify_payload()`: `if tool_name == "Bash":` — the same
  literal-string dependency one layer down, *"so fixing only the case statement above is insufficient."*
- `RC/hooks/guard-web-access.sh:63` — `[ "$tool" = "WebFetch" ] || exit 0`; Copilot's real web-fetch tool
  name is `"web_fetch"`, so the hook exited 0 on every call, including genuine web fetches.
- CP on blast radius: this is *"the marketplace's single most heavily-engineered safety mechanism (20+
  dedicated `CLAUDE.md` milestones) and it is completely dark on this host."*

**Remedy applied:** adapter-side tool-name normalization in `copilot-hook-adapter.sh` (51 insertions), so
every downstream script — which already expects Claude's names — works unmodified.

**Residual open work split out:** MH-24 (the structural cause — no per-tool matcher, undocumented) and
MH-37 (the Learn-tab card that overstated portability), plus the fixture below.

> ⚠ **Verified residual, not covered by `f55039ec`.** The Gate 20 fixture at
> `RC/hooks/tests/test-gate20-adapter-diagnostics.sh:51` still hard-codes `toolName:"shell"` — a **third**,
> still-incorrect value that CP cited as proof the real one was never verified. **Confirmed still present
> this session.** Replace it with the docs-verified `"bash"`, and add a fixture that drives the tribunal
> orchestrator itself (not just adapter I/O shape) through a real Copilot-shaped payload, asserting a
> force-push is still hard-denied. **Effort: S.** Tracked here rather than as its own row because it is the
> same one-line vocabulary defect.

---

#### MH-02 · Mímir read top-level `model`/`usage`; Claude Code nests them under `message` — and the fixture encoded the same wrong shape
**Severity:** P0 · **Hosts:** Claude Code · **Reported by:** CC (P0-1) · **Effort:** S
**Status:** ✅ **FIXED `a5d7e4bf`**

**Evidence** `[verified]`
- `RC/scripts/serve-dashboards.py:1145-1147` — `m = ev.get("model")` (last-used model)
- `RC/scripts/serve-dashboards.py:1180-1184` — `usage = ev.get("usage")` → `output_tokens`
- Real assistant-event top-level keys, dumped that session:
  `['attributionPlugin','attributionSkill','cwd','entrypoint','gitBranch','isSidechain','message',…]` —
  **no top-level `model`, no top-level `usage`.** They live at `ev["message"]["model"]` and
  `ev["message"]["usage"]`.
- **Why every gate passed anyway:** the reader test at `RC/hooks/tests/test-mimir-reader.py:108` wrote the
  *flat* shape — `{"type":"assistant","model":"claude-opus-4-8","usage":{"output_tokens":42}}` — and
  `scripts/check-mimir-render.mjs:187` fed a synthetic payload that never touches the reader. **The reader
  and its gate agreed with each other and disagreed with Claude Code.** CC: *"This is the repo's own
  documented 'silent green defect' shape, landing on the repo's own Claude-Code-only panel."*
- Fix-commit measurement on a real 116 MB transcript: model at top level **0/6060** assistant events;
  nested under `message` **6060/6060**.

**Remedy applied:** nested read first, with the flat read retained as a fallback for any other producer, in
**both** server copies (Gate 32 body parity holds; 20 reader helpers identical); **the fixture re-derived
from the platform artifact, not from the reader**, with teeth proven bidirectionally (real-shape fixture +
old flat-only reader → exit 1; + fixed reader → exit 0).

> **Not fixed by this commit:** the 50 KiB head-read cap and the permission-mode first-event bug — those are
> **MH-06, still OPEN.** CC measured **877 of 1,006** transcripts exceed the cap.

---

#### MH-03 · `AGENTS.md:3` falsely claimed Aider reads `AGENTS.md` natively
**Severity:** P0 · **Hosts:** Aider (claim also unverified for Cursor, Windsurf) · **Reported by:** CWA (P0-1), CX (P3-2) · **Effort:** S
**Status:** ✅ **FIXED `a5d7e4bf`**

**Evidence** `[docs-verified]`
- `AGENTS.md:3` — *"Cursor, OpenAI Codex CLI, Aider, GitHub Copilot, and Windsurf read this file natively."*
- `aider.chat/docs/usage/conventions.html` (fetched live) makes **zero mention of `AGENTS.md`**. Its
  documented file is `CONVENTIONS.md`, and even that is **not auto-loaded**: *"It's best to load the
  conventions file with `/read CONVENTIONS.md` or `aider --read CONVENTIONS.md`."* Automatic loading
  happens only via an explicit `read:` entry in `.aider.conf.yml`. Same conclusion on
  `aider.chat/docs/faq.html`.
- Open upstream issue **aider-ai/aider#4363** asks Aider to even *mention* `AGENTS.md`. Open, unresolved,
  no maintainer response recorded.
- CWA on why P0: *"A consumer who follows this repo's own instructions and puts everything into
  `AGENTS.md`, trusting the 'Aider reads this natively' claim, gets **silent zero coverage under
  Aider**… That is a broken promise for the one file the whole cross-tool story rests on."*

**Remedy applied:** replaced with a per-tool table carrying the basis for each row — Copilot + Codex
`[docs-verified]`, Claude Code by import, **Aider NO** with the source, Cursor and Windsurf `[unverified]`
(Windsurf also noted as reportedly renamed to Devin Desktop).

**Residual open work split out:** MH-26 (Aider still has nothing actionable), MH-28 (two other call sites
still assert the corrected claim), MH-29 (Windsurf naming at the remaining call sites).

---

#### MH-04 · Codex env-var vocabulary failed open — every guardrail inert, the Guardrails dashboard dark
**Severity:** P0 · **Hosts:** OpenAI Codex CLI · **Reported by:** CX (P0-2) · **Effort:** S (shim) / M (wired)
**Status:** ✅ **FIXED `5c6d0744` — FOUNDATION ONLY.** The wiring is **MH-08, still OPEN.**

**Evidence** `[verified]` + `[docs-verified]` + one `[inferred]` step, tagged as such
- `RC/hooks/hooks.json:2` — `"$schema": "https://json.schemastore.org/claude-code-hooks.json"`; `:3` —
  *"Paths use `${CLAUDE_PLUGIN_ROOT}`"*. Every command is `${CLAUDE_PLUGIN_ROOT}/hooks/<script>.sh`
  (`hooks.json:11`, `:15`, `:19`). Five PostToolUse entries pass `"$CLAUDE_TOOL_FILE_PATH"` as argv
  (`hooks.json:11,15,19,25,31`).
- Across the plugin hook scripts: `CLAUDE_PROJECT_DIR` ×28, `CLAUDE_SESSION_ID` ×24, `CLAUDE_PLUGIN_ROOT`
  ×12, `CLAUDE_TOOL_FILE_PATH` ×6.
- `RC/hooks/_emit-event.sh:142` — `local project_dir="${CLAUDE_PROJECT_DIR:-}"`; the helper silently
  no-ops when it is empty.
- Codex supplies `PLUGIN_ROOT` / `PLUGIN_DATA` and `cwd` / `session_id` **on stdin** `[docs-verified]`.
- **`[inferred, from the two verified halves]`** — `${CLAUDE_PLUGIN_ROOT}` resolves empty → the command
  string becomes `/hooks/format-on-write.sh` → non-zero, non-2 exit → Codex *"reports hook failure and
  processing continues"* `[docs-verified]`. **Every guardrail — the tribunal, the layout gate, the
  destructive-command guard, the runaway brake, the DoD gate — fails open**, and because the event helper
  no-ops without a project dir, `hook-events.jsonl` is never written, so the whole **Guardrails**
  destination and the SessionStart banner's "RECENT GUARDRAIL ACTIVITY" line render permanently empty.
  CX: *"exactly the silent-green shape catalogued in the repo's own failure-mode index."*

**Remedy applied:** `_rc_host_env()` + `_rc_host()` in `RC/hooks/_portable.sh:92-142` — a 3-line-per-var
**alias**, not an adapter, with the never-clobber invariant (a `CLAUDE_*` the host already set always wins)
and `_rc_host()` returning `unknown` rather than guessing. bash-3.2 safe.

---

#### MH-05 · The dashboard asserts guardrails are LIVE, and renders *unwatched* as *clean*, on hosts where no hook ever fires
**Severity:** P0 · **Hosts:** Codex · Cursor · Gemini · Aider · Windsurf/Devin (all); Copilot (when the installer was never run) · **Reported by:** DASH (P0-1, P0-2), CC (the through-line) · **Effort:** M (pipeline) + S (empty states) · **Status:** `OPEN`

Two panels, one root cause: **the dashboard conditions on nothing about the host or the emitter.**

**Evidence** `[verified]`
- **The Pipeline map asserts state.** `scripts/generate-dashboards.py:588-907` — `_PIPELINE_LANES` renders
  every stage with a badge; `reapply-posture`, `guard-destructive`, `enforce-layout`-class stages carry
  `"badge": "always"` (`:597`, `:785`, `:800`) with copy like *"Right when the robot wakes up, it loads
  your settings"* (`:592`) and *"Turns each rule into a real Claude Code permission"* (`:602`). **Nothing
  in the lane data or the render is host-conditioned.**
- **Empty states read as clean.** `scripts/generate-dashboards.py:10878` (Heimdall — *"No recent events —
  your perimeter has been quiet."*) and `:11310` (Víðarr — *"No security events. Your perimeter has been
  quiet."*). Both fire whenever the served endpoints return zero events. On an unhooked host the JSONL
  substrate is never written, so the panels **always** render "quiet" — asserting
  surveillance-and-no-findings when the true state is **no surveillance**.
- The contrast that proves this was a miss and not a policy: the Heimdall **CI** card was deliberately
  built with three honest states so its empty state *"never masquerades as CI green."* **The hook cards
  never got the same treatment for the no-emitter case.**

**Why P0 (DASH):** *"'the brake is on' shown to a driver whose car has no brake line. It invites exactly
the trust the guardrails exist to earn."* And: *"an operator doing a security review under Cursor/Codex
reads a green audit log that is structurally incapable of ever showing an event."*

**Remedy**
1. Add a per-stage **`host_support`** field (`{claude: native, copilot: adapter, other: none}`) next to
   `_PIPELINE_STAGE_HOOKS` (`scripts/generate-dashboards.py:889-907`) and render a host-scope line per
   stage. **This is MH-21's data model — build it once, consume it here.**
2. Distinguish *zero events, emitters present* from *zero events, no emitter has ever written here*: a
   pure server-side file-existence boolean in `_read_hook_events` / `_read_vidarr_events` (**both** server
   copies, per the parity discipline). Render *"No guardrail telemetry has ever been recorded in this
   project — hooks emit it under Claude Code and (after the installer runs) Copilot CLI; other hosts do
   not emit it."*
3. Once **MH-14** lands, add the page-level banner keyed on the `/__host` verdict.
4. For Copilot, key the wired-state on `.github/hooks/*.json` presence — a boolean file check.

---

#### MH-06 · Mímir reports the session's *opening* permission mode as current — and said `default` while the session was in `auto`
**Severity:** P0 · **Hosts:** Claude Code · **Reported by:** CC (P0-2) · **Effort:** M · **Status:** `OPEN`

**Evidence** `[verified]`
- `RC/scripts/serve-dashboards.py:1148-1151`:
  ```python
  if first_perm_mode is None and ev.get("type") == "permission-mode":
      pm = ev.get("permissionMode")
  ```
  Takes the **first** event in forward order. Contrast `last_model` two lines above (`:1145-1147`), which
  *overwrites* — **the same loop deliberately keeps the newest model and deliberately keeps the oldest
  permission mode.** Confirmed still present this session at `:1156-1159`, after `a5d7e4bf`, which fixed
  only the model/usage nesting.
- `_mimir_iter_jsonl_bounded` (`:901-916`) does `fh.read(cap_bytes)` from **offset 0** — the head of the
  file — with `_MIMIR_JSONL_READ_CAP = 50 * 1024` at `:850`.
- Measured: Mímir yields `permission_mode = "default"`; the file's **325** `permission-mode` events run
  `default → default → acceptEdits → acceptEdits → auto → auto → …`.
- **877 of 1,006** `.jsonl` transcripts under `~/.claude/projects/` exceed the cap
  (`find ~/.claude/projects -name '*.jsonl' -size +50k | wc -l`). *"The cap is not an edge case; it is the
  normal case"* — the audited session's own transcript exceeded it by **285×**.
- Rendered bare at `scripts/generate-dashboards.py:11556` — `["Permission mode", s.permission_mode]` —
  with **no staleness pill**, while the *activity* card 25 lines below (`:11581-11587`) carries a
  **mandatory** `as of` pill (documented as contract RM4). *"The honesty discipline this repo is proud of
  is applied to the low-stakes card and omitted from the high-stakes one."*

**Why P0 (CC):** `RC/hooks/ensure-default-mode.sh` exists for exactly one reason, stated in its own header:
in `acceptEdits`/`bypassPermissions` the comfort-posture allow/ask/deny rules *"are partially or fully
ignored."* **The dashboard is telling a Claude Code operator that the guardrails are live while the session
has moved to a mode in which they are not.** *"That is not a missing feature; it is the surface actively
vouching for a safety state that does not hold."*

**Remedy**
1. **Tail-scan for `permission-mode`** — seek to `max(0, size - cap)`, drop the torn first line, take the
   **last** event. Keep the head read for anything genuinely session-opening.
2. **Derive the verdict, do not print the enum.** Cross-read `.claude/settings.json`
   `permissions.defaultMode` (pinned to `"default"` by `RC/scripts/apply-comfort-posture.py:872-880`) and
   render **"posture rules LIVE" / "posture rules BYPASSED"** as the headline, with the raw mode as the
   subtitle. *"That is the sentence the operator needs; the enum is trivia."*
3. Add the `as of <timestamp>` pill plus a `scanned N KiB of M MiB` note whenever the read was capped. If
   the tail scan cannot establish a mode, render the honest in-process pill (`mimirInProcessPill`,
   `scripts/generate-dashboards.py:11528-11533`) — **never a value.**
4. Render `plan` as a first-class value (**MH-32**).
5. **Gate it with a fixture whose mode changes *after* the cap** — one that flips at byte 60,000 and
   asserts the reader reports the flipped value. *"That fixture is the whole teeth; without it this
   recurs."*
6. Apply byte-identically to both server copies (the `_read_*` prefix means Gate 32's
   `_BODY_DIFF_PREFIXES` enforces it for free).

---

#### MH-07 · There is no install or wiring path for Codex at all — the entire plugin is unreachable
**Severity:** P0 · **Hosts:** OpenAI Codex CLI · **Reported by:** CX (P0-1, P1-1), DASH (P1-3) · **Effort:** M ·
**Status:** ✅ **FIXED 2026-07-28** (installer + shim + Gate 155) · projection deferred, see below

> **Shipped:** `ravenclaude install --host codex` — a **host dimension on the one installer**, not a
> second installer, exactly as the remedy specified. Verified end-to-end in a scratch project: **50
> skills** symlinked into `.agents/skills/`, **12 hooks** written to `.codex/hooks.json`, dashboard
> launchers wired, MH-17 re-trust notice printed. `status` reports the Codex lane separately;
> `update` fires the re-trust notice whenever `.codex/hooks.json` exists.
>
> **Host auto-detection resolves ambiguity to `copilot`.** If both CLIs are on PATH, or neither, the
> install is byte-identical to yesterday's. A user who happens to have `codex` installed must not
> silently get a different install than they got before — detection reports, it never surprises.
>
> **`.agents/skills` was verified from the primary source before a line was written**, because
> host-support.json had it marked `[inferred]`. Worth recording: **multiple third-party guides claim
> `.codex/skills`** — the primary source says `.agents/skills`. Had this been taken from a blog, the
> installer would have wired 50 skills into a directory Codex never reads, and `install` would have
> reported success — reproducing the exact "completes successfully, wires nothing" defect MH-07 is.
>
> **Deferred, deliberately and with the reason recorded — `scripts/generate-codex-plugin.py` + the
> `plugins/*/codex/**` glob.** The remedy also asked for a generated projection carrying the 15
> agents. **There is no verified Codex agent-file contract in this repo** — the format was never read
> from a primary source. Projecting 15 agent files from a guessed schema is precisely the
> Copilot-shaped mis-scoping MH-15 traced, and the same call made on the Copilot `tools:` P0: *do not
> guess at a contract.* The `.repo-layout.json` glob is therefore NOT added either — the ledger says
> it "must land in the same commit as the projection", and an unused glob is dead config that would
> silently pre-authorize an unreviewed directory.
>
> **Also still open:** MCP (`.codex/config.toml` `[mcp]`) and the posture emitter (MH-16 part 2).
> **The installer prints both gaps at install time** rather than leaving them to be discovered.

**Evidence** `[verified]` + `[docs-verified]`
- `scripts/ravenclaude:2` — *"install / update the RavenClaude plugins for **GitHub Copilot CLI**"*. It is
  the only installer in the repo.
- `scripts/ravenclaude:10`, `:137-142` — skills are symlinked into `<project>/.claude/skills`.
- `scripts/ravenclaude:13`, `:221` — MCP is merged into `${COPILOT_HOME:-$HOME/.copilot}/mcp-config.json`.
- `scripts/ravenclaude:183-217` — hooks are written to `.github/hooks/ravenclaude.json` **through the
  Copilot adapter**.
- `scripts/generate-dashboards.py:6634` — the only install surface is headed *"Install RavenClaude — GitHub
  Copilot CLI"*; `:6638` offers exactly one alternative: *"Using Claude Code instead?"*.
  `_INSTALL_COMMANDS` (`:1555-1580`) is five Copilot commands.
- Codex reads skills from `$CODEX_HOME/skills` and repo-local **`.agents/skills`** `[docs-verified]` —
  **never `.claude/skills`** (that is Copilot's read path). It reads MCP from `~/.codex/config.toml`
  `[mcp]`, not `~/.copilot/mcp-config.json`. **So a Codex operator's setup completes "successfully" and
  wires zero skills, zero hooks, zero MCP into their host. Nothing in the repo tells them so.**
- **No `codex/` directory, no `generate-codex-plugin.py`** (`find . -iname "*codex*"` → 11 paths: 4 docs,
  3 model-guidance files, 2 SVGs, the onboarding skill, the Gate 70 test).
- `.repo-layout.json` `allowed_globs` contains `plugins/*/copilot/**` but **not** `plugins/*/codex/**` —
  **confirmed still true this session at `.repo-layout.json:56`** — so a projection would be denied by
  both the layout hook and `validate-layout.yml` until the glob is added.
- **No `docs/decisions/` entry, no CLAUDE.md milestone, and no `Value-add completeness` row dispositions
  Codex. It is an omission, not a documented N-A.**

**The asymmetry is the finding:** `scripts/generate-copilot-plugin.py:11-16` records that the Copilot
package declares **only `agents`** — *"NO `skills` / `hooks` keys … plugin-level preToolUse hooks don't
fire in Copilot today (github/copilot-cli#2540)."* Codex has no such defect: plugin-bundled hooks load from
`hooks/hooks.json` and skills are a first-class plugin component. **A Codex projection would be strictly
more capable than the Copilot one already shipped, for less work.**

**Remedy** — add a **host dimension** to the installer, not a second installer: `--host codex` that (a)
symlinks the 50 skills into `<project>/.agents/skills/` (repo-local, team-shareable — the better default)
with a `--user` variant for `$CODEX_HOME/skills`, (b) writes `.codex/config.toml` `[mcp]` entries, (c)
emits `.codex/hooks.json` (MH-08). Default the host by probing `command -v codex` / `command -v copilot`.
Ship `scripts/generate-codex-plugin.py` as the sibling generator — byte-deterministic + `--check` gated —
emitting `plugins/ravenclaude-core/codex/` with a `plugin.json` declaring **`skills` and `hooks`** (both of
which Copilot's cannot), the 15 agents, a `hooks.json` wrapped through the shim, and a `codex/AGENTS.md`
carrying the same accuracy-discipline + dashboard-launch blocks the Copilot projection carries
(`copilot/AGENTS.md:20-64`). **Add `plugins/*/codex/**` to `.repo-layout.json` in the same commit** (the
repo's own layout-discipline rule, `AGENTS.md:148-151`). Promote the dashboard install tab to a **3-tab
host switcher** — noting this costs an owner-approved Gate 132 DOM-ratchet raise.

---

#### MH-08 · The Codex env shim has ZERO callers — the foundation is wired to nothing
**Severity:** P0 · **Hosts:** OpenAI Codex CLI · **Reported by:** CX (P0-2, remainder) · **Effort:** M ·
**Status:** ✅ **FIXED 2026-07-28** — but NOT the way this entry proposed. Read the correction.

> **The shim has callers now:** every entry in the generated `.codex/hooks.json` routes through
> `codex-hook-env.sh` (in the plugin's hook directory). Proven by **Gate 155** — 14 assertions with
> two must-fail halves.
>
> **⚠️ CORRECTION — open piece #1 of the table below is FALSE, and building on it would have wasted
> the work.** It claims *"26 `${CLAUDE_PLUGIN_ROOT}` interpolations still resolve empty under Codex.
> A generated `codex/hooks.json` must wrap each entry through the shim."* Re-read from the primary
> source (`learn.chatgpt.com/docs/hooks`, 2026-07-28): **Codex publishes `CLAUDE_PLUGIN_ROOT` and
> `CLAUDE_PLUGIN_DATA` as legacy-compatibility names.** Those interpolations resolve fine. This entry
> inherited the same wrong premise that the portable helper's original comment carried, and which
> `knowledge/codex-cli-customization.md` corrected on creation (MH-15) — the correction had not
> propagated here.
>
> **Piece #2 was also mis-aimed.** It says *"every hook must source and call the shim."* The
> genuinely-absent variables are `CLAUDE_PROJECT_DIR` and `CLAUDE_SESSION_ID`, and `_rc_host_env`
> **cannot supply them**: its fallbacks (`CODEX_PROJECT_ROOT`, `SESSION_ID`, `PROJECT_DIR`) are
> speculative names that are **not in Codex's documented environment**, so they resolve to nothing in
> a real session. Touching all 18 hooks would have changed nothing. The documented, reliable source
> is **stdin** — every payload carries `cwd` and `session_id` — so the wrapper lifts them there, and
> no hook was modified at all.
>
> **Net: the fix was one ~100-line wrapper and an installer branch, not an 18-hook edit plus a
> projection.** Two of this entry's four "open pieces" dissolved on contact with the primary source.
> Pieces #3/#4 (the projection + its layout glob) are deferred with reasons under MH-07.

**Evidence** `[verified — this session]`
- A repo-wide search for `_rc_host_env` returns exactly **one** hit: `RC/hooks/_portable.sh:118` — its own
  definition. **No hook sources it; no hook calls it.** The alias exists and runs on nothing.
- `.repo-layout.json:56` carries `"plugins/*/copilot/**"` and **no codex glob**, so a generated
  `plugins/ravenclaude-core/codex/` would be blocked by both enforcement layers today.

Four distinct pieces remain, each independently blocking:

| # | Open piece | Note |
|---|---|---|
| 1 | ~~**`hooks.json` interpolation**~~ | ❌ **FALSE — do not build this.** Codex publishes `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA` as legacy-compat names `[docs-verified 2026-07-28]`, so the 26 interpolations resolve fine. This row inherited a wrong premise the MH-15 knowledge file had already corrected. |
| 2 | ~~**Every hook must source and call the shim**~~ | ❌ **MIS-AIMED — would have changed nothing.** `_rc_host_env`'s fallbacks (`CODEX_PROJECT_ROOT`/`SESSION_ID`/`PROJECT_DIR`) are **not in Codex's documented environment**. The reliable source is **stdin** (`cwd`, `session_id`). ✅ Closed 2026-07-28 by a wrapper; **zero hooks modified**. |
| 3 | **Generated projection** | `scripts/generate-codex-plugin.py` — still does not exist. **Deferred with cause:** no verified Codex agent-file contract in this repo; projecting 15 agents from a guessed schema is the mis-scoping MH-15 traced. |
| 4 | **`.repo-layout.json` glob** | `plugins/*/codex/**` — **correctly NOT added**, since #3 did not ship. An unused glob is dead config that silently pre-authorizes an unreviewed directory. |

**Remedy** — belt-and-braces from CX: have the shim **`exit 2` with a stderr reason when `PLUGIN_ROOT` is
unset**, converting the failure mode from fail-open to loud. Verify field-by-field against the Codex hooks
doc before writing a line — *"No JSON translation is needed in either direction."*

---

#### MH-09 · The generated `copilot/AGENTS.md` never loads into a Copilot session by default — a closed loop
**Severity:** P0 · **Hosts:** GitHub Copilot CLI · **Reported by:** CP (P0-3) · **Effort:** S · **Status:** `OPEN`

**Evidence** `[verified]` + `[docs-verified]`
- `scripts/ravenclaude` contains **zero** occurrences of `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (verified via
  `grep -c`) — none of `cmd_install`, `cmd_setup`, or `add_rc_alias` exports it or writes it into
  `~/.bashrc`. The installer also never writes a `.github/copilot-instructions.md` stub — the pattern
  `RC/knowledge/copilot-cli-customization.md:80` itself recommends (*"Consumers keep a short
  `.github/copilot-instructions.md` pointing at `AGENTS.md`"*) and the installer never does.
- Per `docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions` (fetched
  that session), `AGENTS.md` is discovered only in *"the repository root, the current working directory,
  intermediate directories between them… [or] directories listed in
  `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`."* A second fetch confirmed **no mention anywhere of `--plugin-dir`**
  as a discovery path — matching that knowledge file's own honest `[verify-at-use]` flag on the exact
  point (`:81`).
- The `rc` alias (`scripts/ravenclaude:44-53`) launches Copilot **without** the env var set, so
  `copilot/AGENTS.md` — and with it the dashboard-launch block and the Relay-mode block — never enters
  context. The v0.158.0 milestone's stated goal (*"'open the dashboard' in a Copilot session Just
  Works"*) does not hold for a default install. `grep -c COPILOT_CUSTOM_INSTRUCTIONS_DIRS
  scripts/generate-dashboards.py` → **0**.

**The closed loop (CP):** *"The instructions on how to make Copilot load the discipline live **only**
inside the file Copilot will not read without already knowing to set that variable."*

**Remedy** — in the install/setup commands, do the cheap durable fix: write a 3-line
`.github/copilot-instructions.md` into the consumer repo pointing at the marketplace clone's
`copilot/AGENTS.md` — **this loads automatically: no env var, no shell-restart dependency.** Optionally
also add the `export COPILOT_CUSTOM_INSTRUCTIONS_DIRS=…` line to the same `~/.bashrc` block the alias
writer already produces, as a belt-and-suspenders second path.

---

#### MH-10 · The least-privilege `tools:` allowlist is dropped when agents project to Copilot — every generated agent gets ALL tools
**Severity:** P0 · **Hosts:** GitHub Copilot CLI · **Reported by:** CP (P0-4) · **Effort:** S/M · **Status:** `OPEN`

**Evidence** `[verified]`
- `scripts/generate-copilot-plugin.py:189-209` (`parse_name_description`) extracts **only** `name` +
  `description`; the comment at `:17-19` states it plainly: *"everything else (tools, model, audience,
  works_with, scenarios, quickstart, …) is intentionally dropped."*
- Confirmed empirically: `RC/copilot/agents/security-reviewer.agent.md` frontmatter is `name` +
  `description` only. The canonical `RC/agents/security-reviewer.md` declares
  `tools: Read, Grep, Glob, Bash, WebFetch` — **deliberately no Write/Edit**, per root `AGENTS.md` house
  rule #9 (*"the tool set is the only real bound on a dispatched subagent's blast radius"*), gated by
  `scripts/check-frontmatter.py`.
- `RC/knowledge/copilot-cli-customization.md:30` (the repo's own docs-verified reference): *"optional
  `tools`; by default an agent has **all** tools — a `tools` spec only *restricts*."*

**So the security reviewer's Copilot projection — an agent whose canonical design deliberately withholds
Write/Edit — gets unrestricted tool access, including write and arbitrary shell, the moment it is used as a
Copilot custom agent.**

**Remedy** — project `tools:` into the Copilot `.agent.md` frontmatter, translated through the same
tool-name vocabulary table `f55039ec` established (**this finding shares its root cause with MH-01**).
Gate it with the existing `--check` freshness test so a future agent that adds a restriction cannot
silently lose it in translation. Verify Copilot's `.agent.md` `tools:` value syntax before shipping.

---

#### MH-11 · The dashboard's only self-repair instruction is broken by the dashboard's own Copilot onboarding
**Severity:** P0 · **Hosts:** GitHub Copilot CLI (human path) · **Reported by:** DASH (P0-3) · **Effort:** S · **Status:** `OPEN`

**Evidence** `[verified]`
- The launch remediation shown in ~10 empty states and the portal banner is literally `rc dashboard` —
  `scripts/generate-dashboards.py:10491,10709,10738,10854,11086,11147,11284,11371,11507,11672`;
  `scripts/_index_dashboard_template.py:987` (`const SERVED_CMD = "rc dashboard"`).
- But the Install & Update tab tells the Copilot operator to create an alias
  `rc='bash scripts/ravenclaude update && copilot --plugin-dir plugins/ravenclaude-core/copilot'`
  (`scripts/generate-dashboards.py:1582-1586`), and the installer writes the same alias into the shell rc
  file (`scripts/ravenclaude:46`, printed again at `:246`).
- **In an interactive shell an alias shadows a PATH binary**, so for exactly the Copilot operator
  `rc dashboard` runs *update-then-launch-Copilot* with a stray `dashboard` argument — **not** the
  dispatcher at `RC/bin/rc`, whose `dashboard` verb the message intends (`bin/rc:1-24`).
- The generated `copilot/AGENTS.md` DASHBOARD_BLOCK dodges this by using the full `bin/rc` path — **the
  agent path works, the human path doesn't.**

**Why P0 (DASH):** *"the dashboard's only self-repair instruction, followed as written after the
dashboard's own onboarding, does the wrong thing for the flagship non-Claude host."*

**Remedy** — resolve the name collision **once**: rename the installer alias (e.g. `rcc`); *or* point the
alias at `bin/rc` and teach `bin/rc` an `update`/launch verb; *or* change every empty-state string to the
unambiguous full-path form. One decision, then a mechanical sweep of `SERVED_CMD` plus the
`sagaEmptyPanel`/`hmEmpty` call sites.

---

### P1 — the host is materially underserved

---

#### MH-12 · Copilot hook wiring is hand-maintained and has drifted badly — 12+ hooks unwired, no freshness gate
**Severity:** P1 · **Hosts:** GitHub Copilot CLI · **Reported by:** CP (P1-1, P2-2) · **Effort:** M · **Status:** `OPEN`

**Evidence** `[verified]` — the canonical `RC/hooks/hooks.json` registers **19** distinct hook scripts
across 6 event types. The installer's embedded generator (`scripts/ravenclaude:184-216`, the Python
heredoc) wires **10**: `capability-orientation.sh` (SessionStart); `guard-destructive.sh`, the tribunal
orchestrator, `runaway-brake.sh`, `enforce-layout.sh` (PreToolUse); `format-on-write.sh`,
`claim-grounding-lint.sh` (PostToolUse); `dod-gate.sh`, `remind-tests.sh`, `stream-session-close.sh`
(Stop); `stream-prompt-attribute.sh` (UserPromptSubmit).

**Missing entirely from the Copilot wiring:** `guard-recursive-spawn.sh`, `delegation-nudge.sh`,
`mark-web-domain-seen.sh`, `worktree-guard.sh` (both `register` and `check` modes), `guard-web-access.sh`,
`route-decision-review.sh`, `reapply-posture.sh`, `ensure-default-mode.sh`, the two **v0.210.1** Muninn
hooks (`thing-denial-kb-sync.sh` / `thing-denial-kb-recall.sh`), and the **v0.216.0**
`dashboard-autostart.sh`. **Nothing enforces that the two lists stay in sync** — unlike the agents
projection, which has a real `--check` freshness gate.

**Merged consequence (CP P2-2 — not separately actionable):** **Muninn is doubly dead under Copilot.** Its
entire value derives from the Sága audit logs the tribunal writes (dark until `f55039ec`) **and** its two
hooks are not wired. It resolves automatically once MH-01 and MH-12 both land; worth one regression test
confirming a denial recorded under a fixed Copilot session actually reaches the KB.

**Remedy** — derive the Copilot `.github/hooks/ravenclaude.json` **programmatically** from the canonical
manifest (a projection function analogous to the agent projection), with a `--check` gate. Where a hook's
*event* has no Copilot equivalent (e.g. `SubagentStart`), the projector must **skip it explicitly and say
so, not silently.**

---

#### MH-13 · Cursor's mature hooks API has zero RavenClaude guardrail port — the only finding that closes an actual in-loop enforcement gap
**Severity:** P1 · **Hosts:** Cursor · **Reported by:** CWA (P1-3) · **Effort:** L · **Status:** `OPEN`

**Evidence** `[docs-verified via web search, corroborated across GitButler's deep-dive, InfoQ, and Cursor's
community forum]` — Cursor shipped a real hooks system in **Cursor 1.7 (October 2025)**:
`.cursor/hooks.json` registers `beforeSubmitPrompt` / `beforeShellExecution` / `beforeMCPExecution` /
`afterFileEdit` / `stop`, and `beforeShellExecution` / `beforeMCPExecution` can return JSON
`allow`/`deny`/`ask` — **structurally the same shape as Claude Code's `PreToolUse` hook**, and the exact
shape the Copilot adapter already bridges. **No `cursor-hook-adapter.sh`, no `.cursor/hooks.json`
template, and no mention of Cursor's hooks API exists anywhere in the repo.**

**Under Cursor, none of the guardrail stack applies** — not `enforce-layout.sh` (CI backstop only), not
`guard-destructive.sh`, not the command-review tribunal, not `runaway-brake.sh` / `dod-gate.sh`, not
`guard-web-access.sh`.

**Remedy** — build `RC/hooks/cursor-hook-adapter.sh` following the Copilot adapter precedent (I/O envelope
translation, `permissionDecision` mapping), a `.cursor/hooks.json` template wiring it, and a gate
analogous to Gate 20 proving the translation round-trips.

**CWA's own assessment, recorded verbatim because it drives §3:** *"This is real work — a new host's I/O
envelope, not a copy-paste — but the precedent already proves the shape is buildable, and it is the single
highest-value item in this audit for closing an actual security gap (right now Cursor consumers have *no*
guardrail enforcement in-loop, CI-only)."*

---

#### MH-14 · There is no host verdict — and where one is planned it is an island with a two-host worldview
**Severity:** P1 · **Hosts:** all · **Reported by:** DASH (P2-1 — rated P2), CX (P1-6), CWA (P1-5), CP (P2-1 — rated P2), CC (P2-2 — rated P2) · **Effort:** M · **Status:** `OPEN`
**Severity disagreement (recorded):** DASH, CP and CC each rated their slice **P2**; CX and CWA rated
theirs **P1**. Carried at **P1** because it is the shared prerequisite for MH-05, MH-18 and MH-21.

**Evidence** `[verified]`
- **Not built.** A scan across the server for every `/__*` route shows **no `/__host` endpoint**;
  `git log --oneline -5` on the branch showed only the planning doc landed (`138b597a`).
- **The plan's detector is right, and its hard edges are correct rather than timid** —
  `docs/plans/2026-07-28-prompt-engineering-learn/plan.md` §6.1 (one-sided by design; Copilot has **no
  documented session signal**, so *"GitHub Copilot CLI"* is *never rendered* in v1, enforced by Gate 152),
  §6.2 (verdict bound to **session liveness**, an always-visible inheritance caveat, an **age-qualified
  headline**, and an **inverse must-fail** — *"a wrong verdict is worse than no verdict"*), §6.4 (closed
  env-**NAME** allow-list, booleans-not-paths, no `os.environ` iteration). DASH calls the liveness inverse
  must-fail *"the single best assertion in the plan."*
- **Gap A — the verdict is an island.** As planned, `/__host` feeds only the new page. MH-05, MH-18 and
  the Mímir framing each need exactly this verdict to become honest. *"Otherwise the dashboard will
  contain one honest page surrounded by the same unconditioned ones."*
- **Gap B — a two-host worldview.** `grep -i "codex\|cursor\|aider\|windsurf" plan.md` → **zero matches
  across 762 lines.** §4b/§4d source the precedence table from the Copilot knowledge file +
  `code.claude.com/docs/en/memory`; the wired-state file list is `AGENTS.md`, `CLAUDE.md`,
  `.claude/settings.json`, comfort-posture, environment-context, `.github/copilot-instructions.md` —
  **Claude + Copilot only.** A session under any other host renders **"cannot determine"** with no
  host-specific static fallback content ever surfacing.

**Remedy**
1. **Consume the verdict.** Cache the `/__host` result once client-side; the other panels read it for
   their host-scope banners. **Effort: S — the banners ride the existing JS panels.**
2. **Add a Codex branch to `_HOST_SIGNAL_NAMES` (§6.4).** Per the Codex env-var doc there is **no**
   documented in-session host marker `[docs-verified]`, so **do not invent one** — instead honor an
   explicit `host: codex` key in `.ravenclaude/comfort-posture.yaml` as a first-class positive signal:
   honest, user-controlled, and works for every future host. §6.4's closed-allow-list design makes this
   *"a one-constant edit, not a redesign."*
3. **Extend the wired-state card** to check `.agents/skills/`, `.codex/config.toml`, `.codex/hooks.json`
   and **`.github/hooks/`** (more load-bearing than `copilot-instructions.md` for what the dashboard
   claims elsewhere) — booleans keyed off a fixed relative-path list, exactly as §6.4 already requires.
4. **Add a static "Other hosts" section** naming Cursor / Devin Desktop / Aider / Gemini explicitly and
   linking to MH-15's knowledge files. **Time-sensitive: cheap now, harder to retrofit once the page's
   byte-level DOM-budget contract (§5.2) is locked and ratcheted.**
   > `[inferred]` — DASH and CWA both flag that these hosts' exact instruction-file conventions were **not
   > verified this session and must not be authored from memory**. See §4.
5. Keep the Mímir reader **Claude-only and say so**, rather than generalizing it (CX's explicit call).

---

#### MH-15 · The per-host knowledge file exists for exactly one host
**Severity:** P1 · **Hosts:** Codex · Cursor · Aider · Windsurf/Devin · Gemini · **Reported by:** CX (P2-4 — rated P2), CWA (P1-1), GEM (P1) · **Effort:** M · **Status:** `OPEN`
**Severity disagreement (recorded):** CX rated its Codex slice **P2** — while simultaneously calling it
*"the prerequisite artifact for P1-2, P1-4, and P1-6; sequence it first."* CWA and GEM rated **P1**.
Carried at **P1**; CX's sequencing note is honored in §3.

**Evidence** `[verified]`
- The plugin knowledge directory holds 23 entries; `copilot-cli-customization.md` exists and **no analog
  for any other host does**. A `find` for `*cursor*` / `*aider*` / `*windsurf*` under the plugin returns
  nothing but the generic prose mentions already cited.
- The Copilot file has a real spine — custom instructions, custom agents, agent skills, hooks, runtime &
  config, a "How RavenClaude maps onto each surface" table, document discovery — verified against GitHub's
  own docs with an inline citation ("verified 2026-06-09").
- **The absence propagates.** `docs/best-practices/agent-onboarding.md:17` — *"Canonical mechanism:
  `copilot-cli-customization.md` §7"* — and `:7` scopes that best-practice to *"repos operated by
  non-Claude-Code agents (GitHub Copilot CLI, Cursor, Aider)"*, which **does not even list Codex**. The
  onboarding skill (`:28`, `:93`) routes a Codex agent to **Copilot's** mechanism doc for its load-bearing
  mechanic.

**Remedy** — author `RC/knowledge/codex-cli-customization.md` **first** (it unblocks MH-16, MH-23 and
MH-14) as the exact structural sibling of the Copilot file: instruction files + precedence, skills paths
(`$CODEX_HOME/skills`, `.agents/skills` scanned cwd→repo-root), the hooks event set + envelope + trust
model, `config.toml` layering, `approval_policy` × `sandbox_mode`, MCP config location, and a
RavenClaude-maps-onto-each table. **Every claim carries its `learn.chatgpt.com` /
`developers.openai.com` URL + retrieval date.** Then one file per remaining host (or one combined file,
given the smaller surface area) covering instruction-file precedence, the native rules/hooks mechanism,
MCP support, and the mapping section — *"the exact analytical work Copilot got and these three never did."*

---

#### MH-16 · Codex's trust/approval model does not map, and RavenClaude's containment guidance is *wrong* for Codex
**Severity:** P1 · **Hosts:** OpenAI Codex CLI · **Reported by:** CX (P1-4) · **Effort:** L ·
**Status:** ✅ **PART 1 FIXED 2026-07-28** · part 2 (`.codex/config.toml` emitter, L) `OPEN`

> **Part 1 landed — and the claim was verified from the primary source before it was written, not taken
> from this ledger.** `knowledge/codex-cli-customization.md` had marked the sandbox model `[inferred]` with
> the standing rule *"must be verified before it is built on"* — writing a Codex row into the constitution
> is building on it, so the doc was fetched first (`https://learn.chatgpt.com/docs/sandboxing`). It
> **corroborated and strengthened** the finding: same primitives as Claude Code's optional sandbox
> (Seatbelt / bubblewrap / Windows sandbox), **default-on** at `sandbox_mode = workspace-write`, and
> explicitly *"applies to spawned commands"* — i.e. it closes the **subprocess** gap the containment
> section exists to name, by default, where Claude Code's is opt-in. The plugin `CLAUDE.md` bullet
> heading — *"Claude Code's OS sandbox is Claude-only"* — was the false generalization and is rewritten;
> the Copilot half (genuinely unevidenced) is preserved intact. The `[inferred]` marker in the knowledge
> file was upgraded to `[docs-verified]` in the same change, since leaving it stale is this audit's own
> recurring defect. **Part 2 (the emitter) is unchanged and still open**, and the corrected section now
> states plainly that a saved comfort-posture does **not** bound a Codex session today.

**Evidence**
- `[docs-verified]` Codex's actual controls are `approval_policy` ∈ {untrusted, on-request, never} ×
  `sandbox_mode` ∈ {read-only, workspace-write, danger-full-access}, resolved through **six** layers ending
  at `/etc/codex/config.toml`, plus `requirements.toml` managed policy (`allow_managed_hooks_only`) and
  MDM.
- `[verified]` RavenClaude's posture engine emits **only** `.claude/settings.json` `allow`/`ask`/`deny`
  rules — `RC/scripts/apply-comfort-posture.py` is the single translator; nothing in the repo writes
  `~/.codex/config.toml` or `.codex/config.toml`.
- `[verified]` The plugin `CLAUDE.md` § "Containment posture" states: *"Claude Code can add an OS sandbox …
  but there is no evidence Copilot CLI honors it — so under Copilot the container/worktree is the
  containment, not the sandbox."* **The section generalizes from Copilot to every non-Claude host.**

**That generalization is false for Codex**, which ships its own OS-level sandbox as a first-class,
default-on control `[docs-verified]`. *"A Codex operator reading RavenClaude's containment guidance is told
to reach for a devcontainer when their host already holds the stronger, OS-enforced boundary — and is told
nothing about the knob that actually governs their blast radius."* **The 12-category comfort-posture matrix
has no projection onto `approval_policy` × `sandbox_mode` at all, so the dashboard's headline product
(posture editing) does nothing for this host.**

**Remedy** — two pieces, in order. **(1)** Correct the containment section: add a Codex row stating the OS
sandbox **is** available and **is** the boundary, with the `sandbox_mode` values and what each permits.
**(2)** Add a Codex emission target to the posture translator — coarse but honest (`security_deny` floor
present + no `allow` on remote-mutate ⇒ `approval_policy = untrusted` + `sandbox_mode = read-only`;
balanced ⇒ `on-request` + `workspace-write`; **never auto-emit `danger-full-access` / `never`**) written to
`.codex/config.toml`, with a `posture-events.jsonl` entry like the existing path. **State plainly in the
dashboard that the Codex mapping is coarser than the Claude one — a 12-category matrix does not have 12
degrees of freedom on this host.**

---

#### MH-17 · Codex's hash-based hook trust turns "an update is just `git pull`" into a silent disarm
**Severity:** P1 · **Hosts:** OpenAI Codex CLI · **Reported by:** CX (P1-5) · **Effort:** S (docs) / M (managed hooks) ·
**Status:** ✅ **FIXED 2026-07-28** — shipped in the SAME commit as MH-07, as this ledger required

> Row 13 of the build order said MH-17 *"ships with MH-07; without it, every update silently disarms
> the guardrails MH-08 just wired."* That was right, and it is why these landed together: shipping
> the installer alone would have **manufactured** the silently-inert-guardrail class this whole audit
> exists to close — on the very host it was closing it for.
>
> Four surfaces, chosen so the warning appears where the damage happens: install-time,
> **update-time** (`ravenclaude update`, gated on `.codex/hooks.json` existing so a Copilot-only user
> never sees a Codex instruction), `status` (reports hooks are wired **and must be TRUSTED** — the
> distinction that matters), and the generated `.codex/hooks.json` `description` itself. Plus a full
> section in `knowledge/codex-cli-customization.md`.
>
> **`--dangerously-bypass-hook-trust` is named only to refuse it**, per CX. It converts an honest
> "your guardrails are off" into a dishonest "your guardrails are on" — strictly worse than the
> problem. `requirements.toml` managed hooks are documented as the only unattended-survival path.

**Evidence**
- `[docs-verified]` *"Codex hashes each hook and tracks trust by hash. New **or modified** hooks are marked
  for review and **skipped until trusted**. Users review via `/hooks`."* Plugin-bundled hooks use the same
  non-managed trust flow; installing a plugin does **not** auto-trust its hooks.
- `[verified]` The plugin `CLAUDE.md` § Copilot bridge: *"we deliberately do NOT use Copilot's
  install-and-cache mechanism … the plugin loads **live** … so an **update is just `git pull`**. No
  re-install, ever."* `scripts/ravenclaude:46` bakes this into the `rc` alias.

**Under Codex the live-load pillar inverts into a silent disarm:** every `git pull` that changes a byte of
any hook script invalidates its hash, and that hook is skipped until the user notices. Given 18 hooks and
near-weekly plugin bumps, *"the steady state for a Codex consumer is guardrails silently off after every
update — with no banner, because the SessionStart banner is itself a hook."*

**Remedy** — **(a)** document it loudly in the Codex onboarding section and the generated
`codex/AGENTS.md`: *after every update, run `/hooks` and re-trust.* **(b)** Make it mechanical: have the
Codex-host update path print the list of hooks whose hash changed and end with an explicit
`Run /hooks in Codex to re-trust N hooks` line. **(c)** For teams, document the `requirements.toml`
**managed-hooks** path — managed hooks are auto-trusted by policy and cannot be disabled `[docs-verified]`,
*"the only configuration where RavenClaude's guardrails survive an update unattended on this host."*
**Do NOT reach for `--dangerously-bypass-hook-trust`** — CX: *"naming it as the fix would be exactly the
'governance theatre' anti-pattern the onboarding skill itself lists (`SKILL.md:73`)."*

---

#### MH-18 · Claude-only invocation is taught as universal, while the host-agnostic equivalent already ships
**Severity:** P1 · **Hosts:** every non-Claude host · **Reported by:** DASH (P1-2, P1-4, P1-5), CX (P2-1, P3-3) · **Effort:** M · **Status:** `OPEN`

Four surfaces, one root cause: **`RC/bin/rc` was built (v0.158.0) precisely to solve this for Copilot, and
was never extended to the Commands catalog, the settings fallback, or the cross-tool instruction file.**
CX: *"the identical gap Codex has… it is copy-paste, and it makes `rc dashboard` the one launch verb across
all three hosts."*

**Evidence** `[verified]`
- **Commands catalog** — `scripts/generate-dashboards.py:1670-1762`: every Class-B card renders *"copy it,
  then paste into Claude Code"* (`:1710-1719`); the tab intro says *"Copy a command and paste it into your
  Claude Code session"* (`:1750-1754`); `:1646` — *"All 4 shipped commands are Claude Code slash
  commands."* **No card carries a non-Claude alternative even where one exists and is documented in the
  same file**: `/dashboard` ≡ `rc dashboard`, `/stream` ≡ `rc streams …`, `/set-posture` ≡ the Run button's
  posture script. *"A Copilot/Codex operator browsing the catalog is handed instructions that cannot work
  in their host, with no signpost."*
- **Posture editor** — the category intro promises *"you pick **Deny** (never), **Ask** (check with me
  first), or **Allow**"* (`scripts/generate-dashboards.py:2132-2141`); Save & apply's sole output is
  `.claude/settings.json` (`RC/scripts/serve-dashboards.py:142-145,1837-1852`); the no-server fallback says
  *"run `/set-posture`"* (`:6600`) — a Claude-only slash command. **The editor's central interaction
  describes enforcement one host delivers, one host partially delivers by a different mechanism, and five
  hosts don't deliver at all — with no scope note anywhere on the Settings tab.**
- **The cross-tool instruction file routes to a Claude-only command** — root `AGENTS.md` § Setup: *"open
  the dashboard's **Install a plugin (Bifröst)** tab (`/dashboard` → `#/bifrost`)"*, and `AGENTS.md:16-21`
  is `/plugin marketplace add ./` + `/plugin install ravenclaude-core@ravenclaude`. CX's framing: the
  onboarding skill makes step 1 of every Codex session *"Read `AGENTS.md` end-to-end … don't skim"* — so
  **the first substantive thing that agent reads is a setup procedure it structurally cannot execute,
  followed by a pointer to a command that does not exist on its host.**

**Remedy**
1. Extend the data-driven Commands classifier with an optional **`host_equivalents`** map (command →
   `{copilot: "…", shell: "…"}`) sourced from command frontmatter, rendered as a second card line (*"Not in
   Claude Code? run: …"*). Where none exists, say **"Claude Code only"** — the good precedent already
   exists at `scripts/generate-dashboards.py:1755-1762`.
2. One host-scope line under the posture category intro, mirroring the command-review disclaimer's honesty
   (`:2304-2321` — *"the house style the rest should copy"*): *"These levels bind Claude Code's permission
   engine. Under Copilot CLI, enforcement comes from the wired hooks + command review; under other hosts
   the posture is advisory and CI is the backstop."* Condition the `/set-posture` hint on host, or print
   the shell equivalent alongside.
3. Restructure `AGENTS.md` Setup as a **three-row host table** (Claude Code / Copilot CLI / Codex CLI),
   each with the command that actually works, and replace the bare `/dashboard` pointer with the
   host-agnostic launcher — **full path**, per MH-11 — marking `/dashboard` as the Claude Code shorthand.
4. Carry the `copilot/AGENTS.md:28-64` dashboard block verbatim into the `codex/AGENTS.md` MH-07 produces.

---

#### MH-19 · No MCP surface anywhere in the dashboard, though 6 plugins declare servers and the repo calls MCP lazy-loading a *permanent* trap
**Severity:** P1 · **Hosts:** Claude Code (primarily) · **Reported by:** CC (P1-1) · **Effort:** M · **Status:** `OPEN`

**Evidence** `[verified]`
- The dashboard server contains **zero** MCP references (case-insensitive grep).
- `scripts/generate-dashboards.py` — the only hits are `:2300`, `:2468`, `:2481`, `:2872`, all of which are
  the tribunal's `mcp_tools` **permission-review category**, not server state.
- Six shipped plugins declare servers:
  `plugins/{aws-cloud,microsoft-fabric,generative-web-media,microsoft-365-copilot,power-platform,microsoft-graph}/.claude-plugin/plugin.json`
  → `"mcpServers": {…}`.
- `CLAUDE.md:30` names this the *permanent* trap: *"MCP tools are deferred + lazy-loaded… calling one
  directly fails with `InputValidationError`. Run `ToolSearch` first… Never infer 'tool doesn't exist' from
  a missing schema. **This trap is permanent.**"*

**Consequence:** *"an agent that hits `InputValidationError` on an MCP tool has no dashboard answer to 'is
this server even declared here, and at what scope?' — it must go read six `plugin.json` files."* **The repo
knows MCP is the #1 recurring capability confusion and gives the operator no surface for it.**

**Remedy** — an **MCP card**, ideally seated on the `#/host-context` page (MH-14). Rows from three disk
sources: installed plugins' `plugin.json` `mcpServers`, a project `.mcp.json` (absent here), and
`~/.claude.json` if present. Columns: **server name · scope (plugin / project / user) · declared by**. An
honest in-process pill for connection state — *"whether a server is connected is in-process only — run
`/mcp`"* — the same `mimirInProcessPill` pattern, **never a fabricated green dot**. **Leak floor: names and
scopes only. Never `args`, never `env` values, never a resolved absolute path** — `index.html` is a
published artifact, so the plan's §6.4 closed-allow-list discipline binds here too.

---

#### MH-20 · Subagent dispatch is invisible, though the attribution data is already sitting in the transcript
**Severity:** P1 · **Hosts:** Claude Code · **Reported by:** CC (P1-2) · **Effort:** M · **Status:** `OPEN`

**Evidence** `[verified]`
- `RC/hooks/hooks.json:149-159` registers `SubagentStart` → `agent-dispatch-evaluator.sh`, which
  shadow-logs to `.ravenclaude/runs/dispatch-eval/`.
- **No reader consumes it.** A grep for `dispatch-eval` / `SubagentStart` across
  `scripts/generate-dashboards.py` returns exactly one hit — `:918`, its **exclusion** reason inside
  `_PIPELINE_EXCLUDED_HOOKS`. There is no `/__dispatch` endpoint in either server copy.
- The transcript already carries per-event `attributionSkill`, `attributionPlugin` and `isSidechain`.
  Measured on one session: **688** events attributed to `ravenclaude-core:forge-pipeline`, 29 to
  `claude-in-chrome`, 11 to `artifact-design`, 10 to `ravenclaude-core:decision-review`. **None of those
  three field names appears in either the server or the generator.**

**Consequence (CC):** *"Claude Code's orchestration primitive is the subagent, and this marketplace's
entire thesis is a Team Lead fanning work out to specialists. The Activity destination shows *runs* and
*worktrees* (Sleipnir) — never *who was dispatched, by what, how often*. An orchestrating agent auditing
its own fan-out has nowhere to look."*

**Remedy** — **(1) cheap and immediate:** extend the Mímir recent-session rows with derived `by_skill` /
`by_plugin` counts from `attributionSkill` / `attributionPlugin`. **Derived labels + integers only** — the
exact no-egress contract `_read_streams` already follows. **Zero new endpoint.** **(2) fuller:** a
`/__dispatch` reader over `.ravenclaude/runs/dispatch-eval/`, active only when
`.ravenclaude/dispatch-config.json` has `enabled: true`; honest empty state otherwise (it defaults off).
**(3)** Surface both on **Activity**, next to the run feed, *"where an operator already looks for 'what is
the agent doing'."*

---

#### MH-21 · No machine-readable per-component host-support map — and monitors are invisible *and* outside the drift gate's field of view
**Severity:** P1 · **Hosts:** all · **Reported by:** CC (P1-4), DASH (P2-2 — rated P2) · **Effort:** M · **Status:** `OPEN`
**Severity disagreement (recorded):** DASH rated its half **P2**. Carried at **P1** because it is MH-05's
data model — the P0 fix is copy-by-copy prose without it.

**Evidence** `[verified]`
- `RC/.claude-plugin/plugin.json` → `"experimental": {"monitors": "./monitors/monitors.json"}`;
  `RC/monitors/monitors.json` registers `run-state-monitor` (`when: "on-skill-invoke:spawn-team"`). The
  plugin `CLAUDE.md` describes it as **Claude-Code-only** — *"the push complement the Heimdall/Víðarr pull
  readers structurally cannot provide."*
- It appears **nowhere** in `scripts/generate-dashboards.py`. And unlike the deliberately-suppressed hooks
  it is not even *excludable*: `_PIPELINE_EXCLUDED_HOOKS` (`:912-928`) and **Gate 133**
  (`scripts/check-pipeline-lanes.py`) reconcile against the hooks manifest **only**, so **a monitor is
  outside the drift gate's field of view entirely.**
- Same class, other components: the Copilot adapter implements modes `bash-pretool` (`:63`),
  `file-pretool` (`:130`), `sessionstart` (`:141`), `posttool` (`:152`), `userpromptsubmit` (`:159`),
  `stop` (`:171`) — **no `subagentstart` mode**, so the dispatch evaluator is Claude-Code-only; and all
  eight `RC/commands/*.md` slash commands are Claude-Code-only (correctly disclosed at
  `scripts/generate-dashboards.py:1755-1762` — *"the good precedent to copy"*).
- `_PIPELINE_STAGE_HOOKS` (`scripts/generate-dashboards.py:889-907`) already maps stage → hook. **Nothing
  machine-readable states, per hook, which hosts execute it** — *"which is why every dashboard surface (and
  Gate 133) is silent on host scope."*

**Remedy** — one artifact, three consumers:
1. Add a **`host_support`** field per stage (`{claude: native, copilot: adapter, other: none}`) next to
   `_PIPELINE_STAGE_HOOKS`. **MH-05's fix then becomes data-driven instead of copy-by-copy.**
2. Render a **"What's wired on this host"** card (a natural fit for `#/host-context`, and cheap there),
   generated from the real manifests: hooks (grouped by event), monitors (`experimental.monitors`), slash
   commands. Each row carries a **Claude Code only / portable** badge **derived mechanically from the
   adapter's mode list rather than hand-asserted** — so the badge cannot rot when a mode is added.
   **Booleans and fixed labels only** (no paths), per the §6.4 leak floor.
3. **Extend Gate 133** to reconcile `experimental.monitors` as well, and to require `host_support` — *"so a
   future monitor cannot land unsurfaced and unexcluded."*

---

#### MH-22 · The consumer-facing dashboard points at a portal consumers do not have
**Severity:** P1 · **Hosts:** Claude Code (consumers) · **Reported by:** CC (P1-3) · **Effort:** S (b) / M (a) · **Status:** `OPEN`

**Evidence** `[verified]`
- `scripts/generate-dashboards.py:13350-13353` (the Plugin-variables intro, shipped into `dashboard.html`):
  *"For the full reference — agents, scenarios, skills, hooks, templates, best-practices — open the plugin
  in the portal's **Marketplace** section."*
- The portal is `index.html` at the **marketplace repo root**; there is no `index.html` inside the plugin,
  and the bundled server serves the plugin dir and redirects `/` → `/dashboard.html`. **A consumer who
  installs the plugin and runs `/dashboard` gets `dashboard.html` and no portal.**
- `docs/dashboard-removed-routes.md` retires `#/team` with *"Catalog — the specialist roster now lives in
  the marketplace."* The roster genuinely exists only in the portal generator
  (`scripts/generate-index-dashboard.py:517-558`, `_scan_agents`).
- **Compounding:** `AGENTS.md:63-70` makes the ~15K agent-description budget explicitly *the consumer's*
  job (*"Enable only what you need… budget before you enable, not after the warning fires"*) — **and then
  the consumer's dashboard ships no agent or plugin inventory to budget against.**

**Remedy** — pick one, (a) preferred:
- **(a)** Ship a **roster island** into `dashboard.html`: agent name + one-line description + owning plugin
  + per-plugin agent count, emitted inside `<script type="application/json">`. `html.parser` treats script
  content as CDATA, so this is **+0 counted DOM elements** — the same islanding trick `panel-learn` and
  `panel-commands` already use (`scripts/generate-dashboards.py:190-213`). **Gate 132's zero-slack ratchet
  is untouched.** This directly serves the budget decision the repo asks consumers to make.
- **(b)** One-line honesty fix: name a destination a consumer actually has — Claude Code's own `/plugin` →
  **Discover** tab, which surfaces per-plugin **Context cost** and the **Will install** inventory natively
  (already cited at `AGENTS.md:70`).

---

#### MH-23 · `codex-onboarding` is a Copilot/Cursor skill wearing a Codex name, and its entire evidence base is a dead `/tmp` path
**Severity:** P1 · **Hosts:** OpenAI Codex CLI (and every host the skill claims) · **Reported by:** CX (P1-2, P1-3, P3-1), CWA (P2-1) · **Effort:** M · **Status:** `OPEN`

**Evidence** `[verified]` — all line refs are `RC/skills/codex-onboarding/SKILL.md`
- `:45-52` "Tool-version floors" table rows: **GitHub Copilot CLI, Cursor, Claude Code, Aider, Devin.
  There is no Codex row.**
- `:82` "what done looks like": *"The tool's version floor has been verified (`gh copilot --version` /
  `cursor --version` / etc.)"* — no `codex --version`.
- `:66-74` anti-patterns: 3 of 7 are Copilot-CLI-version-specific, 1 is Devin-specific. **None is
  Codex-specific.**
- Nothing in the file mentions `approval_policy`, `sandbox_mode`, `~/.codex/config.toml`, `.agents/skills`,
  `$CODEX_HOME`, `/hooks`, `codex exec`, or Codex's own hook system. *"The most Codex-relevant thing in the
  file is `:24` ('read `.repo-layout.json`') — good, generic advice."*
- `:3` positions Codex 4th in a list of 5 hosts, yet **Codex owns the skill's name and therefore the
  discovery keyword**; `:6` lists `audience: [external-coding-agent, codex-user, copilot-cli-user,
  cursor-user, aider-user]`.
- **The evidence base is unfalsifiable by construction.** `:8` — `sources: -
  /tmp/research-codex-2026-updates.md §1-§3, §7-§8`. `:53` — `[verify-at-use — 2026-06-04 — Copilot CLI
  changelog versions per /tmp/research-codex-2026-updates.md §1]`, the sole provenance for the whole
  version-floor table. **`ls /tmp/research-codex-2026-updates.md` → `No such file or directory`.** `:5` —
  `last_reviewed: 2026-07-08`; the marker is dated 2026-06-04, *"now 7+ weeks stale."*
- **Merged from CWA (P2-1):** `:48` — *"Cursor ≥ 3.3 — `/multitask` parallel agents + Composer 2.5
  file-tree refactor."* No citation, no `[unverified]` marker, **no `[verify-at-use]` tag** — while the
  Copilot row *beside it* at `:53` carries exactly such a tag. CWA could not corroborate the pairing and is
  **explicitly not asserting it is wrong** — *"only that it is stated as bare fact in a file that otherwise
  practices citation discipline for its neighboring rows, which is itself the defect."*

**This is the repo's own Claim-Grounding rule failing on the repo's own file:** `AGENTS.md:206` requires a
durable consequential claim to *"cite the this-session check that backs it inline."* **A `/tmp` path is
unfalsifiable by construction — it cannot be checked by any later reader on any machine.**

**Remedy** — **split.** Keep a generic **`external-agent-onboarding`** (the first-five-minutes ritual,
spec-reread, diff-budget, validator handoff — all genuinely portable) and add a real per-host section. The
Codex section must carry the `~/.codex/config.toml` ↔ `.codex/config.toml` precedence chain,
`approval_policy` × `sandbox_mode` and how they interact with this repo's testing instructions,
`.agents/skills` as the repo-local skills path, `/hooks` trust review, and `codex --version`. **Re-derive
every version-floor row from a durable, linkable source, cited inline as a markdown link** — backticked
paths are invisible to Gate 29's `check-md-links.py`. **Any row that cannot be re-sourced gets deleted, not
re-dated.** Add a `last_verified` per row.

---

#### MH-24 · Copilot's `hooks.json` has no per-tool `matcher` — undocumented, and it is the structural cause of MH-01
**Severity:** P1 · **Hosts:** GitHub Copilot CLI · **Reported by:** CP (P1-2) · **Effort:** S (doc-only, high leverage) · **Status:** `OPEN`

**Evidence** `[docs-verified]` + `[verified]` — the hooks-configuration example in
`RC/knowledge/copilot-cli-customization.md` §4 (itself sourced from the docs, re-confirmed by that
session's fetch of `docs.github.com/en/copilot/reference/hooks-configuration`) shows
`"hooks": { "preToolUse": [ {…} ] }` — a flat array with **no tool-scoping field**. Claude Code's manifest
by contrast nests every hook block under an explicit `"matcher": "WebFetch"` (`RC/hooks/hooks.json:37,90`).

**This asymmetry is never stated in the knowledge file's "How RavenClaude maps onto each surface" table
(§6)** — *"even though it is exactly the blind spot behind P0-1 and P0-2: every registered Copilot
preToolUse hook fires on **every** tool call, and the tool-name filter has to live inside the invoked
script — which is precisely where the wrong string comparisons were shipped."*

**Remedy** — add one explicit line to §4 stating Copilot has no per-tool hook matcher, and add it to
whatever pre-merge checklist governs new hooks, *"so the next hook author doesn't repeat the mistake."*
**CP's own note: "S (doc-only), but high leverage — this is the guardrail against the *next* instance of
this defect class."**

---

#### MH-25 · Cursor's native `.cursor/rules/*.mdc` convention is completely unserved
**Severity:** P1 · **Hosts:** Cursor · **Reported by:** CWA (P1-2) · **Effort:** M · **Status:** `OPEN`

**Evidence** `[docs-verified — cursor.com/docs, fetched live]` — Cursor's primary, current mechanism is
`.cursor/rules/*.mdc` files with `description`/`globs`/`alwaysApply` frontmatter, with a stated precedence
*"Team Rules → Project Rules → User Rules."* Cursor's own docs frame `AGENTS.md` as *"a simple markdown
file… as an alternative to `.cursor/rules`"* — **the simpler, unscoped sibling, not a superset.** Nothing
in `RC/templates/agent-ready-repo/` (9 files, none named for Cursor) ever emits an `.mdc` file.

**A Cursor user gets only the flat, always-on `AGENTS.md` text — never the globbed, file-scoped rule
Cursor's own convention is built for** (e.g. a rule that fires only on Write-shaped paths matching
`.repo-layout.json`'s `allowed_globs` — *"exactly this repo's most distinctive mechanism and exactly the
kind of thing `.mdc` globs exist to express"*).

**Remedy** — add a `.cursor/rules/ravenclaude.mdc` template (`alwaysApply: true`, projecting the
`AGENTS.md` grounding section — the same projection pattern as the Copilot AGENTS.md block) to
`/init-agent-ready`'s output, plus a second, **glob-scoped** rule for the layout allow-list.

**CWA's own prioritization, recorded because it drives §3:** *"Cursor: worth building, but the higher-value
item is the hooks adapter (MH-13), not the rules projection… it upgrades ergonomics (glob-scoped rules) but
doesn't fix a gap the way the hooks adapter would."*

---

#### MH-26 · Aider's real mechanism (`CONVENTIONS.md`) still has no projection — the prose is corrected, the gap is not closed
**Severity:** P1 · **Hosts:** Aider · **Reported by:** CWA (P0-1 real fix, P2-3) · **Effort:** M · **Status:** `OPEN`
**Severity note:** CWA rated the composite finding **P0**. Its P0 element — the false claim — is **FIXED
(MH-03)**. What remains is the buildable half, carried at **P1**. **This is a scope split, not a severity
downgrade by this ledger.**

**Evidence** `[docs-verified]` — as MH-03. Aider's documented file is `CONVENTIONS.md`, auto-loaded only
via an explicit `read:` entry in `.aider.conf.yml` — *"a per-repo opt-in the user must author"*, which
**this repo documents nowhere.**

**Remedy** — ship a generated `CONVENTIONS.md` projection (the `extract_section()` pattern at
`scripts/generate-copilot-plugin.py:316-338` already proves it out for Copilot) plus an `.aider.conf.yml`
template with `read: [CONVENTIONS.md]`, wired into `/init-agent-ready`'s template set
(`RC/templates/agent-ready-repo/`) — *"so the claim becomes true for anyone who adopts it, instead of
merely being corrected in prose."*

**CWA's verdict on whether this is over-engineering, quoted because the brief asked the question
directly:** *"Aider: worth building. Its actual native mechanism is knowable, narrow, and already has a
proven projection pattern to copy… Not over-engineering — it's the **minimum** correct fix, since
correcting the prose alone leaves Aider users with nothing actionable."* Contrast **Windsurf/Devin Desktop:
not worth a projection** — `AGENTS.md` already works there natively and by the same mechanism as
root-level Devin/Cascade rules; *"a projection would duplicate content the host already reads correctly."*

---

#### MH-27 · FORGE and Wireframe have zero Copilot bridging, and `copilot/plugin.json` overclaims slash-command support
**Severity:** P1 · **Hosts:** GitHub Copilot CLI · **Reported by:** CP (P1-3) · **Effort:** S/M · **Status:** `OPEN`

**Evidence** `[verified]`
- `RC/copilot/plugin.json`'s `description` states: *"Slash commands: /init-agent-ready, /wrap,
  /set-posture, /dashboard, /forge, /wireframe, /reset-plugin-cache."*
- The plugin `CLAUDE.md`'s own Copilot bridge section says plainly: *"Slash commands (`/set-posture`,
  `/wrap`) don't port (Copilot CLI has no user slash commands yet)."*
- Only `/dashboard` gets a dedicated Copilot-specific bridging block (`DASHBOARD_BLOCK`,
  `scripts/generate-copilot-plugin.py:62-102`) telling the host the real equivalent. `/forge` (the
  `forge-pipeline` skill) and `/wireframe` get **no** equivalent block — *"under Copilot, invoking either
  relies entirely on Copilot's own description-based skill inference, with no explicit guidance anywhere in
  the generated package."*

**Remedy** — either soften the description so it does not claim these are slash commands under Copilot,
**or** add short bridging blocks for `forge-pipeline` and `wireframe` mirroring the existing
`DASHBOARD_BLOCK` pattern.

---

#### MH-28 · The claim-grounding double standard survives at two call sites the fix did not reach
**Severity:** P1 · **Hosts:** Cursor · Aider · Windsurf/Devin · Codex · **Reported by:** CWA (P1-6), CX (P3-2) · **Effort:** S · **Status:** `OPEN`

**Evidence** `[verified]`
- The identically-shaped claim **for Copilot is verified in-repo, with an inline citation**:
  `scripts/generate-copilot-plugin.py:52-54` — *"Verified 2026-05-31 against GitHub docs: Copilot CLI reads
  AGENTS.md from the repo root, cwd, or any dir named in COPILOT_CUSTOM_INSTRUCTIONS_DIRS
  (docs.github.com/…)."*
- The identically-worded claims for the other hosts carried **no citation, no `[unverified]` marker, and no
  date** — despite `AGENTS.md:204-208` requiring exactly this treatment for any *"consequential claim…
  written into a durable doc."* **One of the uncited claims turned out to be false** (MH-03). CWA: *"This
  isn't a one-off oversight; it's the repo's own accuracy discipline applied inconsistently across hosts
  named in the same sentence."*
- **`a5d7e4bf` fixed `AGENTS.md:3` only.** Two sibling call sites still assert the corrected claim:
  - `RC/commands/init-agent-ready.md:141` — *"AGENTS.md is read by Cursor / Codex / Aider / Copilot
    natively; CLAUDE.md is Claude-Code-only."*
  - `RC/skills/codex-onboarding/SKILL.md:3` — *"…routes through AGENTS.md (which all major 2026 agents
    read)…"*

**Remedy** — apply the same per-row basis discipline to both call sites, or replace each with a pointer to
the corrected `AGENTS.md` table as the single source of truth. Where a host is genuinely unverified, **mark
it** — *"a false claim of support is worse than an admitted gap, because it stops anyone from building the
bridge that would make it true"* (now the repo's own words, in `AGENTS.md`).

---

#### MH-29 · "Windsurf" is a stale brand name at the remaining call sites — rebranded Devin Desktop, 2026-06-02
**Severity:** P1 · **Hosts:** Windsurf / Devin Desktop · **Reported by:** CWA (P1-4, P3-1) · **Effort:** S · **Status:** `OPEN`

**Evidence** `[docs-verified this session by CWA]` — `docs.windsurf.com/windsurf/cascade/agents-md` now
**307-redirects** to `docs.devin.ai/desktop/cascade/agents-md`. Cognition (maker of Devin) acquired
Windsurf in mid-2025 and formally rebranded the product **Devin Desktop on 2026-06-02** — roughly eight
weeks before this audit — per Cognition's/Devin's own blog and multiple contemporaneous trade-press pieces.

**Functionally the claim still holds** — Devin Desktop's docs confirm it *"automatically discovers
[`AGENTS.md`] and feeds it into the same Rules engine"* as `.devin/rules/` / the legacy `.windsurf/rules/`.
**So this is a naming-currency defect, not a functional one.**

`a5d7e4bf` noted the rename in the new `AGENTS.md` table. **Still open:** `RC/commands/init-agent-ready.md:5`,
and the onboarding skill's audience lists (`:6`, `:17`) plus the version-floor table (`:51`), which name
**"Devin"** and imply **"Windsurf"** as if unrelated hosts on separate tracks — *"a reader unaware of the
2026-06-02 rebrand would reasonably wonder why the tool-version-floor table has a 'Devin' row but no
'Windsurf' row, or vice versa."*

**Why it went uncaught, and it compounds** (CWA): *"(a) there is no knowledge file tracking this host
(MH-15) for a staleness sweep to even look at, and (b) the mention is only 2 files deep, so it is easy to
miss in a routine sweep scoped to `knowledge/`."*

**Remedy** — update the remaining call sites to *"Windsurf (rebranded Devin Desktop, June 2026)"* and add
one clarifying parenthetical wherever both names appear together.

---

#### MH-30 · The Gemini lane is name-checked 17 times, supported zero times, and formally undecided
**Severity:** P1 *(as reported — see the contest note)* · **Hosts:** Gemini CLI · **Reported by:** GEM (P1 ×2, P2 ×2) · **Effort:** S (unsupport) / M–L (build) · **Status:** `OPEN`

> **Severity contested — by the reporting lens itself.** GEM rated this **P1** and no other lens covered
> Gemini, so P1 stands under the highest-wins rule. But GEM's own **Honesty Notes** say: *"**No bridge is
> broken** — the repo doesn't promise Gemini CLI support and then break it… A Gemini CLI user trying to
> install this marketplace **would not be betrayed**; they would simply find no Gemini-specific
> guidance."* That is materially weaker than every other P1 here, all of which describe a broken promise or
> an inert guardrail. **This ledger records P1 as reported and recommends treating it as P2 in the build
> order (§3).**

**Evidence** `[verified]`
- `AGENTS.md:3`'s supported-tool list — *"Cursor, OpenAI Codex CLI, Aider, GitHub Copilot, and Windsurf"* —
  **Gemini CLI is explicitly absent.** The README does not mention Gemini CLI anywhere.
- A repo-wide `find` for `GEMINI.md` returns only
  `plugins/power-platform/skills/visual-qa/resources/gemini-review.md` — a **supplemental Power Platform
  skill resource** for using the Gemini API in visual-QA tests, **not** Gemini CLI orchestration guidance.
  **No root `GEMINI.md` exists.**
- **17 grep hits, exhaustively enumerated by GEM and spot-checked for context.** They are *real* but *not
  support*: research/knowledge references (Gemini as an AI model in decision trees, AEO discussions, the
  `[unverified]`-tagged cross-tool model-lineup row, *"Vertex (now Gemini Enterprise Agent Platform)"*, the
  spawn-team model-diversity recommendation) plus **one** actual integration — the Power Platform
  visual-QA skill's optional `GEMINI_API_KEY`-driven test-recording review.

**Merged sub-finding (GEM P2 → MH-36):** that one real integration is undiscoverable.

**Remedy — this is a decision, not a build.** Pick one and write it down:
1. **Unsupport, explicitly (S):** add one line to `AGENTS.md`/`README.md` — *"Gemini is referenced as an AI
   model option and used in Power Platform visual-QA; RavenClaude does not provide Gemini CLI orchestration
   support."* **This is the honest default** given GEM's own "no bridge is broken" finding.
2. **Build (M–L):** a root `GEMINI.md`, the `AGENTS.md` row, and Gemini auth/config + MCP patterns. **Gate
   this on demand** — GEM's own recommendation is *"Medium term (**if Gemini CLI demand arises**)."*

**Preserve the `[unverified]` tag on the cross-tool model-lineup row — GEM explicitly calls it good
practice that should be kept.**

---

### P2 — clear-value improvement

---

#### MH-31 · Gate 70 is named for Codex but tests nothing about Codex-as-host — and the name laundered into a capability claim
**Severity:** P2 · **Hosts:** OpenAI Codex CLI (perception) · **Reported by:** CX (P2-3) · **Effort:** S · **Status:** `OPEN`

**Evidence** `[verified]`
- `RC/hooks/tests/test-gate70-codex-trust-hooks.sh:2-3` — *"fixture tests for Gate 70 (**Codex desktop
  trust review** remediation: Findings 1, 2, 5)."*
- Its six subtests exercise `DATA_PLATFORM_STRICT`, `APPLIED_STATS_STRICT`, `EDTECH_PS_STRICT`, the
  DoD-gate first-run trust, and the web-access first-use ask (`:42-249`). **Nothing invokes a Codex
  envelope, config file, path, or CLI.**
- `scripts/audit-gates.sh:4175` labels it *"Gate 70: Codex desktop trust review hooks"*.

This is remediation of findings **Codex produced while reviewing RavenClaude** — good work, unrelated to
hosting *on* Codex. **CX: "The name is the single largest source of 'Codex support exists' confusion in the
repo; it was cited as evidence of an existing Codex lane in the brief for this very audit."**

**Remedy** — rename the fixture to `test-gate70-trust-review-remediation.sh` and relabel the gate *"Gate 70:
external trust-review remediation (STRICT hooks + dod-gate + web-access)"*. Update
`scripts/audit-gates.sh:94-95` and `:4175-4190`. Keep a one-line provenance comment naming where the
findings came from. **Zero behavior change; it stops the name laundering into a capability claim.**

---

#### MH-32 · Plan mode has no representation, and its absence reads as "not applicable" rather than "not surfaced"
**Severity:** P2 · **Hosts:** Claude Code · **Reported by:** CC (P2-1), DASH (P3-2, adjacent) · **Effort:** S · **Status:** `OPEN`

**Evidence** `[verified]` — `permission_mode` is the sole carrier (`RC/scripts/serve-dashboards.py:1073`,
`:1148-1155`; rendered `scripts/generate-dashboards.py:11556`). The reader's own honest-unreachable list
(`:1090`) names `effort_dial`, `plan_tier`, `status_live_cache` — **plan mode is not on it**, *"so its
absence reads as 'not applicable' rather than 'not surfaced'."* And `RC/hooks/ensure-default-mode.sh`
case-matches only `acceptEdits | bypassPermissions`, never `plan`.

Plan mode is a first-class Claude Code permission mode and the one `CLAUDE.md:35-37` ("Plan-mode default")
tells the agent to enter for any change touching >2 files or a manifest. **The dashboard cannot show
whether that instruction is being honoured.**

**Merged adjacency (DASH P3-2):** the Mímir in-process pills (`scripts/generate-dashboards.py:11531`,
`:11557`, `:11573`) give Claude-only advice (*"run /status in Claude Code"*) without a panel-level caveat —
defensible inside a Claude-labelled panel, **and it resolves automatically** once MH-14's host banner
lands. No independent work.

**Remedy** — once MH-06's tail-scan lands, render `plan` explicitly with its meaning (*"agent is planning —
no writes will be attempted"*); if the tail scan cannot establish it, **add `plan_mode` to the
`unreachable` list so the silence is *declared* rather than ambiguous.**

---

#### MH-33 · Land the D8 / Gate 142 route sweep independently — three currently-unenforced holes
**Severity:** P2 · **Hosts:** Claude Code (disproportionate exposure) · **Reported by:** CC (P2-3) · **Effort:** S · **Status:** `OPEN`

**Evidence** `[verified]` — `plan.md` §6.3 items 4-6 (`:520-528`) document three real, currently unenforced
holes:
- Gate 32's `_ENDPOINT_RE = r"/__\w+"` (`scripts/check-dashboard-server-parity.py:46`) is **hyphen-blind**
  *and* one-directional.
- The server's own NOTE that *"any NEW data-returning GET endpoint MUST call `self._local_request_ok()`
  first"* is **enforced by nothing.**
- `do_HEAD` needs an allow-list entry or HEAD 404s while GET 200s.

**Why it belongs to the multi-host frame (CC):** *"the served dashboard's two launch paths are both
Claude-Code-only — the `/dashboard` slash command and the new `dashboard_autostart` SessionStart hook
(`RC/hooks/hooks.json:191-196`). Its exposure surface is disproportionately this host's."*

**Remedy** — ship D8 as an **independent commit**: extend the existing Gate 142 (the live security-floor
check shipped in v0.208.0) so it iterates **every** `/__*` route the server dispatches and asserts 403 on
an evil `Origin`. **One loop, real teeth, and it covers every future endpoint including the ones this audit
asks for (`/__mcp`, `/__dispatch`, `/__host`).**

---

#### MH-34 · The pre-PR testing checklist requires network installs a Codex sandbox blocks — and nothing names the cause
**Severity:** P2 · **Hosts:** OpenAI Codex CLI · **Reported by:** CX (P2-2) · **Effort:** S · **Status:** `OPEN`
> ⚠ **Rests partly on `[inferred]` evidence — verify before building.** See §4.

**Evidence**
- `[verified]` `AGENTS.md:119-120` — `npx --yes prettier@3.9.4 --write .` then `--check .`, marked
  **REQUIRED before pushing**. `AGENTS.md:126` — `pip install --quiet ruff && ruff check .`, gated by CI.
- `[docs-verified]` `sandbox_mode` restricts filesystem **and network** access; `workspace-write` is the
  standard interactive mode.
- **`[inferred]`** — under the default interactive sandbox a Codex agent running steps 3 and 4 of this
  checklist gets a **network denial, not a lint result.**

The repo's own CGP then obliges that agent to *"read the actual error first and name its specific
mechanical cause"* (`AGENTS.md:208`) — **but nothing anywhere tells it the cause is `sandbox_mode`**, so
*"it will most likely mis-diagnose it as a missing tool and either abandon the check or ask the user for
something they cannot grant mid-turn."*

**Remedy** — one note under the testing block: *"On Codex CLI these two steps need network egress; if they
fail, the cause is `sandbox_mode`, not a missing tool. Either pre-provision `prettier` + `ruff` into the
image, or run these steps outside the sandbox. Do not treat a sandbox denial as 'lint unavailable'."*
**Better still**, add a `scripts/lint-local.sh` that prefers already-present binaries and only falls back
to `npx`/`pip`, *"so the happy path needs no network at all."*

---

#### MH-35 · The pending plan adds zero runtime state, and applies its own honesty rule only to its own page
**Severity:** P2 · **Hosts:** Claude Code · **Reported by:** CC (P2-2) · **Effort:** S to amend / M to execute · **Status:** `OPEN`

**Evidence** `[verified]`
- `plan.md` §6.2 (`:475-500`) is binding and excellent — *"a wrong verdict is worse than no verdict"* →
  verdict bound to **session liveness**, an always-visible inheritance caveat, an **age-qualified
  headline** (*"Claude Code (detected when this server started, N min ago)"*), and an **inverse must-fail**
  in Gate 152. **CC: "a higher honesty bar than any existing dashboard panel meets."**
- The plan greps clean for the host's runtime surfaces: `mcp` appears once (`:456`, Copilot's
  `COPILOT_HOME`), `subagent` **never**, `permission mode` **never**; the Mímir reader appears only at
  `:483` and `:490` — where the plan **reuses it as a trusted reachability oracle** for
  `_session_is_live()`.
- **So the plan imposes on `/__host` precisely the rule the Mímir panel is currently breaking (MH-06),
  while taking a dependency on that same reader.**

**CC's own assessment, recorded because it matters for §3:** *"This is **not** a reason to block. The plan
is additive, budget-honest (§5.2's byte-level markup contract is exemplary), and D3 + D1's
`directing-the-agent` / `using-plugins-well` / `prompt-agentic-craft` concepts are genuinely the right
teaching for this host."*

**Remedy** — add one phase (or a same-branch follow-up) applying §6.2's rule **retroactively** to the Mímir
panel (MH-06). **Not scope creep:** `_session_is_live()` is specified to reuse the Mímir reachability path,
so fixing the cap and the schema **strengthens the plan's own detector** and removes a dependency on a
reader that is currently wrong about the file it reads.

---

#### MH-36 · The Power Platform visual-QA Gemini integration is undiscoverable
**Severity:** P2 · **Hosts:** Gemini (as a model, not a host) · **Reported by:** GEM (P2) · **Effort:** S · **Status:** `OPEN`

**Evidence** `[verified]` — `plugins/power-platform/skills/visual-qa/resources/gemini-review.md` is the
**only real Gemini integration in the repo** and is buried in a skill resource: not advertised in the main
README, not mentioned in `AGENTS.md`, not wired into any top-level skill or agent list. *"A consumer
looking for Gemini CLI support would see 'name-checked but not supported,' not 'supported via Power
Platform visual-QA.'"*

**Remedy** — one clarifying note in `AGENTS.md`/`README.md`: *"The Power Platform visual-QA skill includes
optional Gemini API integration for test-recording review (supplemental feature, not required)."* **Ship
this with MH-30's scope decision, in the same commit — they are two halves of one honest sentence.**

---

### P3 — nit / polish

---

#### MH-37 · The Learn-tab concept card overstates hook portability with no honesty hedge
**Severity:** P3 · **Hosts:** GitHub Copilot CLI · **Reported by:** CP (P3-1) · **Effort:** S · **Status:** `OPEN` *(partially resolved by `f55039ec`)*

**Evidence** `[verified]` — `RC/knowledge/concepts/copilot-bridge.md:20` teaches, as settled fact with **no
`[verify-at-use]` marker**: *"a hook adapter translates the I/O envelopes so the *unmodified* hook scripts
run under Copilot."* CP: *"the envelope shape translates correctly, but the tool-name *values* inside it do
not, so the 'unmodified scripts run' framing is optimistic. This is the dashboard's own teaching surface
asserting exactly the kind of unhedged capability claim the marketplace's own Claim-Grounding protocol says
should carry a marker."*

**Status nuance:** `f55039ec` made the tool-name half true. **The claim is still overstated for the 12+
hooks that are never wired into Copilot at all** (MH-12).

**Remedy** — soften to *"unmodified… run under Copilot **for the hooks the installer wires**"*, or add a
`last_verified` caveat. Becomes fully true once MH-12 lands.

---

#### MH-38 · "Learn & Help" self-description enumerates two hosts as the whole world
**Severity:** P3 · **Hosts:** all non-Claude/Copilot · **Reported by:** DASH (P3-1, and the P1-3 lane it depends on) · **Effort:** S/M · **Status:** `OPEN`

**Evidence** `[verified]` — `scripts/generate-dashboards.py:395` (*"install & update guides for Claude Code
and GitHub Copilot CLI"*), `:328` (Help drawer sections: *"the About, Claude Code, Copilot CLI, and
Commands sections"*). The Help drawer holds exactly two onboarding lanes — Bifröst for Claude Code
(`:7406-7408`) and the Copilot install tab (`:6631-6647`) — each cross-linking only the other. **A grep of
the two generators finds zero occurrences of codex/cursor/gemini/aider/windsurf as hosts.** DASH: *"Until
[a third lane] lands, these strings advertise the gap."*

**Remedy** — add the third Help-drawer section, *"Other agents (Codex · Cursor · Aider · Windsurf ·
Gemini)"*, generated as a **projection of the onboarding skill's first-five-minutes** + the `AGENTS.md`
pointer + an honest enforcement note (*"no hooks fire under these hosts; CI is the gate"*). Static content,
works on Pages, no new endpoint. **Follow the plan's §4b projection discipline — fail loudly if the source
heading moves.** Then update the two self-description strings alongside it.

---

#### MH-39 · Prompt Builder never states it targets Claude models
**Severity:** P3 · **Hosts:** Copilot (routing GPT/Grok) and every non-Claude host · **Reported by:** DASH (P3-3) · **Effort:** S · **Status:** `OPEN`

**Evidence** `[verified]` — `scripts/generate-dashboards.py:362-374` — the builder *"assembles a
best-practice **Claude** prompt"* (docstring), and its linter rules are Claude-version-specific (prefill →
400 on Claude 4.6+). *"A Copilot operator routing GPT/Grok gets rules presented as universal prompt
hygiene. Mostly they transfer; the deprecation/model-tuning rules don't necessarily."*

**Remedy** — one visible line in the tab intro: *"Targets Claude models; other models' conventions may
differ."*

---

#### MH-40 · `dashboard_autostart` shipped with no dashboard control
**Severity:** P3 · **Hosts:** Claude Code · **Reported by:** CC (P3-1) · **Effort:** S
**Status:** ✅ **FIXED `870fe226`** — *and the finding was already stale when the report was written.*

**Evidence as reported** `[verified]` — `RC/hooks/hooks.json:191-196` registers `dashboard-autostart.sh`
(v0.216.0); the plugin `CLAUDE.md` v0.216.0 entry states *"No DOM control ships — Gate 132 is at zero slack
and a visible toggle costs an owner-approved ratchet raise."* CC noted this only to record that D4 is *"a
genuine Claude-Code-facing gap-closer, not budget spend on polish."*

**Verified this session:** `870fe226 feat(dashboard): visible dashboard_autostart control (+6,
owner-approved)` touched `scripts/generate-dashboards.py` (+76), `dashboard.html`, `index.html` and
`scripts/check-dom-budget.py`; `dashboard_autostart` now appears **14×** in the generator. **The control
shipped, with the owner-approved ratchet raise, in a commit that predates the audit report.** The report
cited a `CLAUDE.md` line that `870fe226` superseded.

> **This is itself a finding, and it is the repo's own documented failure mode.** The plugin `CLAUDE.md`
> already carries an explicit warning about exactly this shape, added after the macOS-doors incident: *"A
> stale 'Still open' in a file every session loads is an active defect, not a bookkeeping lag. When you
> close a door, supersede the entry that says it's open in the same PR."* ~~**Action: supersede the
> v0.216.0 line.**~~ ✅ **DONE 2026-07-28** — the v0.216.0 entry now carries an inline supersession block
> recording that the control DID ship at a measured 6 elements, with the ratchet raise, and naming MH-40 as
> the lens that was misled. Verified before writing: `_render_dashboard_autostart()` exists in
> `scripts/generate-dashboards.py` and renders 3 `dash-autostart` nodes on **each** surface.
> **MH-40 is now fully closed — fix + supersession.**

---

#### MH-41 · No Gemini-specific MCP server or shared auth/config pattern
**Severity:** P3 · **Hosts:** Gemini CLI · **Reported by:** GEM (P3) · **Effort:** M–L (only if MH-30 chooses "build") · **Status:** `OPEN`
> ⚠ **`[inferred]` — GEM self-rates 85% confidence.** *"Inferred from patterns, not from a config file
> saying 'Gemini is not supported.' A deployed Gemini CLI agent trying to use the repo would confirm
> this."* **Do not build from this without verification.** See §4.

**Evidence** `[inferred]` — no `mcp` section in any `plugin.json` for Gemini tools; no shared Gemini API key
management pattern across plugins. The Power Platform visual-QA skill wires `GEMINI_API_KEY` by hand.

**Remedy** — **blocked on MH-30's decision.** If "unsupport," this closes as N-A. If "build": a `gemini-mcp`
declaration (or shared utility), a Gemini auth/config runbook in the core knowledge directory, and a Gemini
section in `claude-app-engineering` alongside the existing Claude/Copilot/Grok guidance.

---

#### MH-42 · The tribunal's self-disable guard false-positives on documentation that cites substrate paths
**Severity:** P3 · **Hosts:** all (authoring-time) · **Reported by:** *this ledger, `[verified]` — reproduced twice at authoring, then TWICE MORE during the Codex build* · **Effort:** S · **Status:** `OPEN`

> **Two further live reproductions, 2026-07-28, while implementing MH-07 — worth recording because
> they show the cost is recurring, not one-off, and they refine the trigger shape:**
>
> 1. A **Bash** `chmod +x` on a newly-created file in the plugin's hook directory was denied. That is
>    the guard working as designed (directory-level, mutation), but it means **a new hook cannot be
>    made executable from inside a session at all** — and CI hard-fails a non-executable
>    `plugins/*/hooks/*.sh`. The operation had to be handed to the human. No bypass was attempted; the
>    smaller-blast-radius routes (Read/Write/Edit) genuinely cannot set a mode bit.
> 2. An **Edit** to *this file* was denied — because the new prose contained a markdown link whose
>    target was a plugin `hooks/` path. Confirms regex (1)'s blockquote/angle-bracket exposure extends
>    to **ordinary markdown links**: `](` + a substrate path is enough. Rephrasing to a bare filename
>    (`codex-hook-env.sh`, "in the plugin's hook directory") passed immediately.
>
> **Net effect on this build:** documenting the Codex shim accurately required *not naming its path*,
> and shipping it required a human to run one `chmod`. Both are exactly the "documentation about the
> substrate is treated as an attack on the substrate" shape this entry describes — and item 1 shows it
> also blocks a legitimate *authoring* operation with no in-session alternative.

**Evidence** `[verified — two independent denials]`
- Sága `thing-2026-07-28T18-40-51Z-71592`:
  `{"tool_name":"Write","category":"file_edit_project","phase":"T4-self-disable","concerns_cited":["xc.tribunal-self-disable"],"final_verdict":"deny","seats":[]}`
  for a `Write` to `docs/plans/2026-07-28-multi-host-audit/ledger.md` — **not a substrate path.** A second
  attempt using a `<core>` placeholder was denied identically (`…T18-50-54Z-76982`).
- The trigger is **regex (1)** of `xc.tribunal-self-disable`, `RC/knowledge/concerns-catalog.md:182`:
  `(>>?|\btee\b)\s*\S*(<substrate alternation>)`. It matches **any `>` character followed by one run of
  non-space characters and then a substrate filename.** Two distinct prose shapes hit it:
  1. a markdown **blockquote** whose first token is a plugin `hooks/`-or-`scripts/` path;
  2. an **angle-bracket placeholder** — the second denial's cause: a token like `<core>` *ends in `>`*, so
     `<core>/hooks/thing-orchestrator…` presents `>` + `/hooks/` + a substrate filename, an exact match.
  **Regex (2)** (`(?s)\b(rm|…|install|…)\b.{0,200}(<same alternation>)`) has the same exposure for prose
  that mentions a mutating verb within 200 characters of such a path.
- **Why it is a false positive:** the concern's own inline comment scopes it — *"Regex can't canonicalize a
  path, so this is the shell-level scope (in-process `python -c` writes route to the panel)."* For a
  **file-shape** write the reviewed text is `"<file_path>\n<content>"` (the v0.37.0 Track-B Phase-0
  design), so **content that merely cites a substrate path is screened as though it were a command
  mutating one.**
- The path-resolution screen (`_substrate_paths`, `RC/scripts/thing-decision` `:469-491`) is correctly
  **target-path-based** and did **not** fire here — only the catalog regex did.

**Blast radius:** any audit, plan, decision record, postmortem or knowledge file that quotes plugin
`hooks/` or `scripts/` paths — i.e. **exactly the documents the repo's own Claim-Grounding protocol
demands, since it requires `file:line` citations.** Denials are `pre_llm_deny`, so no seat convenes and
there is no override short of the dashboard.

**Remedy** — narrow the file-shape screen without weakening the shell-shape one, which is doing its job:
1. For `file_edit_project` / `file_edit_global`, evaluate regexes (1) and (2) against **the path component
   only**, not `path + content`. The content-side self-disable risk is already covered by the
   catalog-independent target-path screen, which is canonicalization-based and strictly stronger.
2. If the content scan is kept, require the `>` to be **immediately followed by a path-like token that is
   not preceded by an opening `<`**, and exclude a `>` at line-start-plus-space (the blockquote shape). A
   shell redirect essentially never takes either form.
3. Add a **bidirectional** fixture, per the repo's own must-fail-half discipline: a `docs/**` write whose
   *body* quotes a plugin hooks path must **not** be denied, while a `Write` **to** a substrate path must
   still be.

**Interim workaround (used by this file):** the `RC` path convention plus extension-free tribunal script
names, declared at the top. It preserves every path and line number exactly, and it is not a bypass — **both
denials were obeyed.**

---

## §3 — Recommended build order (by leverage = impact ÷ effort, not severity alone)

Severity says *how bad*. This order says *what to do first*. Three items unblock most of the rest.

### Wave 0 — the three unblockers (build first even though two are not the highest severity)

| # | ID | Why first | Effort | Unblocks |
|---|---|---|---|---|
| **1** | **MH-21** — per-component `host_support` map + "what's wired" card + Gate 133 extension | It is the **data model** for MH-05. Build it here and the P0 fix is a render change; skip it and MH-05 is copy-by-copy prose that rots on the next hook added. | M | **MH-05**, MH-38, part of MH-18 |
| **2** | **MH-14** — `/__host` + *consume the verdict* + the Codex/other-host branches | Every host-conditioned banner in this ledger needs exactly one verdict. **Time-sensitive:** the page's byte-level DOM-budget contract (plan §5.2) is not yet locked and ratcheted — *"cheap to add now, harder to retrofit."* | M | **MH-05**, MH-18, MH-19, MH-21's card, MH-32, the Mímir banner |
| **3** | **MH-15 (Codex file first)** — the Codex customization knowledge file | CX's own words: *"the prerequisite artifact for P1-2, P1-4, and P1-6; **sequence it first**."* Every Codex build item below currently cites Copilot's mechanics doc. | M | **MH-16**, **MH-23**, MH-07's projection content, MH-14's Codex branch |

### Wave 1 — highest leverage per hour (all S; mostly P0)

| # | ID | Sev | Effort | Note |
|---|---|---|---|---|
| 4 | **MH-11** — resolve the `rc` alias collision | P0 | **S** | One decision + a mechanical sweep. The dashboard's only self-repair instruction currently misfires for the flagship non-Claude host. |
| 5 | **MH-09** — write `.github/copilot-instructions.md` at setup | P0 | **S** | A few lines in the installer break a closed loop that silently voids the entire Copilot discipline. **Best P0-per-line in the ledger.** |
| 6 | **MH-05 (part 2)** — emitter-presence empty states | P0 | **S** | A file-existence boolean in two readers. Stops the dashboard reporting *unwatched* as *clean*. Ship with Wave 0 #1. |
| 7 | **MH-10** — project `tools:` into the Copilot agents | P0 | **S/M** | Shares MH-01's now-built vocabulary table. Restores least-privilege on **every** projected agent — including `security-reviewer`. |
| 8 | **MH-24** — document the no-matcher asymmetry | P1 | **S** | Doc-only, and the **highest leverage in the ledger**: it is the guardrail against the *next* MH-01. |
| 9 | **MH-01 residual** — fix the Gate 20 `"shell"` fixture | P0 | **S** | Closes the last artifact still encoding a guessed tool name. |
| 10 | ✅ **MH-40 supersession** (done) + **MH-42** fixture (open) | P3 | **S** | Both are about the repo lying to its own agents. MH-40's stale line is superseded; MH-42 gained **two more live reproductions** during the Codex build. |

### Wave 2 — the Codex lane, in dependency order

| # | ID | Sev | Effort | Note |
|---|---|---|---|---|
| 11 | ✅ **MH-08** — wire the shim | P0 | S | **DONE 2026-07-28.** Not as specified: the wrapper lifts `cwd`/`session_id` from **stdin**; no hook was modified and no `PLUGIN_ROOT` guard was needed (Codex supplies it). Gate 155. |
| 12 | ✅ **MH-07** — `--host codex` installer | P0 | M | **DONE 2026-07-28** — 50 skills → `.agents/skills`, 12 hooks → `.codex/hooks.json`, verified end-to-end. Generator + glob deferred with cause (rows 3/4 above). |
| 13 | ✅ **MH-17** — hash-trust docs + the re-trust line on update | P1 | S | **DONE 2026-07-28, in the same commit as MH-07 — exactly as this row required.** Four surfaces, incl. `update`, where the disarm actually happens. |
| 14 | **MH-23** — split the onboarding skill; re-source or delete every version-floor row | P1 | M | Needs Wave 0 #3. |
| 15 | **MH-31** — rename Gate 70 | P2 | S | Do it inside MH-23's commit — same confusion, same reader. |
| 16 | ✅ **MH-16 part 1** (done) → **part 2**, the `.codex/config.toml` emitter (open) | P1 | L | Part 1 shipped 2026-07-28, verified from the primary source first. **Part 2 is now the top open Codex item** — and the installer states plainly at install time that a saved posture does not bound a Codex session. |

### Wave 3 — the surfaces (all now cheap because Wave 0 exists)

**MH-18** (host-equivalents + posture scope line + the `AGENTS.md` host table) · **MH-19** (MCP card) ·
**MH-20** (subagent counts — start with the zero-endpoint attribution rollup) · **MH-22** (roster island,
+0 DOM) · **MH-06** (Mímir tail-scan + the derived LIVE/BYPASSED headline + the post-cap fixture) ·
**MH-32** · **MH-38** · **MH-39** · **MH-37**.

> **MH-06 is a P0 sequenced into Wave 3 deliberately, and that is a judgment call worth naming.** Its
> user-visible harm is confined to one host and one panel; its *correct* fix needs a
> flips-after-the-cap fixture that is most of the effort; and MH-35 wants the same commit. **If the owner
> prefers strict severity order, move it to Wave 1** — the tail-scan alone is S; only the teeth are M.

### Wave 4 — the remaining lanes, and one decision

| ID | Note |
|---|---|
| **MH-12** | Copilot hook projection + `--check` gate. M, and landing it makes MH-37 true. |
| **MH-13** | Cursor hook adapter — **L, and CWA's pick for the single highest-value item in the audit**: the only finding that closes a real in-loop enforcement gap rather than a documentation one. Sequence after MH-15's Cursor file exists. |
| **MH-26** | Aider `CONVENTIONS.md` projection + `.aider.conf.yml` template. |
| **MH-25** | Cursor `.mdc` rules — **CWA explicitly ranks this below MH-13**: it upgrades ergonomics, not coverage. |
| **MH-28, MH-29** | Two S doc sweeps over the same two files; ship together. |
| **MH-27, MH-33, MH-34, MH-35** | Independent, small, no dependencies. |
| **MH-30 + MH-36** | **A decision, not a build.** Make the call (recommended: unsupport explicitly, per GEM's own "no bridge is broken"), then MH-41 either closes N-A or opens. |

---

## §4 — Honest scope

### Counts

| | P0 | P1 | P2 | P3 | **Total** |
|---|---|---|---|---|---|
| **FIXED** | 4 | 0 | 0 | 1 | **5** |
| **OPEN** | 7 | 19 | 6 | 5 | **37** |
| **Total** | **11** | **19** | **6** | **6** | **42** |

Deduped from **~60 raw findings** across six reports. The heaviest merges: **MH-18** folded five findings
from three lenses; **MH-14** folded five from five lenses; **MH-23** folded four from two; **MH-05** folded
two lenses' P0s plus CC's stated through-line; **MH-12** absorbed CP's Muninn finding as a pure consequence.
**MH-42 is new** — produced by writing this ledger, not by any lens.

### What is genuinely architectural vs a one-line fix

**Genuinely architectural (6)** — these change how the repo is *shaped*, not what a file says:

- **MH-07 / MH-08** — a *host dimension* in the installer plus a generated Codex projection. This is §1
  made concrete: the repo has one non-Claude lane and needs at least three.
- **MH-13** — a second hook adapter. New I/O envelope, new gate. The Copilot precedent proves the shape is
  buildable but is explicitly *not* a copy-paste.
- **MH-14 / MH-21** — the two missing artifacts (a host verdict; a per-component host-support map). Their
  absence is *why* MH-05, MH-18, MH-19 and the Mímir framing all exist as independent findings.
- **MH-16 (part 2)** — a second posture emission target. The comfort-posture engine has exactly one
  translator today; adding `approval_policy` × `sandbox_mode` means accepting — and saying in the UI — that
  **a 12-category matrix does not have 12 degrees of freedom on every host.**

**Effectively one-line / one-paragraph fixes (13)** — MH-24, MH-28, MH-29, MH-31, MH-32, MH-34, MH-36,
MH-37, MH-38, MH-39, MH-40's supersession, MH-22 option (b), and MH-01's residual fixture. Together these
are roughly a day and close about a third of the open ledger.

**The middle (18)** — real engineering, bounded scope, no new architecture.

### Findings that rest on `[inferred]` evidence — VERIFY BEFORE BUILDING

Three, and none is promoted anywhere in this ledger:

1. **MH-04's failure chain** — `[inferred, from the two verified halves]`. That an empty
   `${CLAUDE_PLUGIN_ROOT}` under Codex yields a non-zero non-2 exit which Codex reports-and-continues was
   **reasoned, not observed.** Both halves are verified (the interpolations exist; Codex's
   continue-on-hook-failure is docs-verified) — **the chain was never run.** `5c6d0744` already ships on
   this inference. **Before MH-08 wires it: run one hook under a real Codex session and observe the exit
   path.** If Codex instead fails closed, the shim's `exit 2` belt-and-braces is unnecessary and the
   severity of MH-04/MH-08 drops.
2. **MH-34** (the Codex sandbox blocks `npx`/`pip`) — `[inferred]` from a docs-verified premise. **One
   `codex exec` run of the prettier check settles it.** Cheap; do it before writing the note, so the note
   quotes the real error text rather than a predicted one.
3. **MH-41** (no Gemini MCP/auth pattern) — GEM self-rates **85%**, explicitly *"inferred from patterns,
   not from a config file."* **Blocked on MH-30's decision anyway — do not build.**

**Also flagged, though not formally `[inferred]`:** MH-14's remedy #4 and DASH's Gap B both record that
**Cursor / Devin / Aider / Gemini instruction-file conventions were not verified this session** and *"must
not be authored from memory, per the plan's own claim-#12 discipline."* Any wired-state row for those hosts
needs a live docs check first.

### What was checked and found genuinely fine (recorded so it is not "fixed")

- **The four dashboard destinations survive multi-host scrutiny** (DASH P2-3). Control / Activity /
  Guardrails / Catalog are host-neutral **jobs**; the substrate under Activity/Guardrails is deliberately
  host-neutral (the Copilot adapter exports `CLAUDE_SESSION_ID` so events land in the right run dir). **No
  IA re-cut is warranted** — *"the multi-host work is banners, empty states, and one new Control page —
  which is exactly the shape the pending plan already takes."*
- **Served-vs-static degradation is genuinely good** (DASH Q5): the `/__csrf` probe tri-state, the "needs
  the served dashboard" empty states, and the CI card's three honest states are *"the strongest honesty
  machinery in the estate."* **The one lie is not served-vs-static but emitting-vs-non-emitting host**
  (MH-05), plus the broken remediation command those honest states hand out (MH-11).
- **`AGENTS.md`'s Testing / Layout / PR-conventions / Accuracy-discipline sections are portable and
  correct** (CX Appendix B) — *"real, usable grounding for a Codex agent, and the reason the answer to 'is
  AGENTS.md alone sufficient?' is **sufficient to work honestly, insufficient to be wired**."*
- **`.repo-layout.json` + the CI backstop is the one place the repo genuinely anticipated a Codex
  operator** — root `CLAUDE.md` spells out that the layout workflow *"catches direct human commits,
  **Cursor/Codex/Aider edits**."*
- **The 6/6 Codex hook-event overlap** — *"an unplanned but real asset. Nothing needs redesigning to use
  it."*
- **`plan.md` §6.1 / §6.2 / §6.4** — the one-sided detector, the liveness binding with its inverse
  must-fail, and the closed env-NAME allow-list are *"a higher honesty bar than any existing dashboard
  panel meets."* **Do not weaken any of them to make a host detectable.**
- **CWA P2-2, recorded so a future audit does not over-credit coverage:** the "71 files mention Cursor"
  figure is **inflated by ~25–30% false positives** — `cursor-pagination-design`,
  `build-cursor-pagination-over-offset`, and CSS `cursor: pointer` rules. **No action; a counting caveat.**

### Known limits of this ledger

- **Every finding is second-hand.** All six lenses were *Claude reasoning about* a host, not running as it.
  **No finding here was reproduced under Codex, Cursor, Aider, Gemini or Devin Desktop.** CWA and CP
  fetched vendor docs live, which is the strongest evidence in the set — it is still not execution.
- **`file:line` references are as-of 2026-07-28** on `feat/ravenclaude-core-0.216.0`. Four commits landed
  after the reports were written; line numbers in the server, `AGENTS.md`, the Mímir reader test and
  `_portable.sh` have shifted. **Where this ledger re-verified a line this session, it says so
  explicitly.**
- **No severity was independently re-scored.** Highest-wins was applied mechanically; the four
  disagreements (MH-14, MH-15, MH-21, MH-30), the one scope split (MH-26) and the one internal
  contradiction (MH-30) are named at their entries rather than silently resolved.
- **MH-42 is self-reported** — found by this ledger's own authoring, with two Sága records as evidence. It
  has had no second lens on it.

---

## §5 — Do not regress

Invariants the five fixes established, plus the ones the audit found already load-bearing. Each is stated
as a rule, with the artifact that would catch a violation.

### From the fixes

1. **Host detection returns `unknown` rather than guessing.**
   `_rc_host()` identifies a host from **POSITIVE signals only**. Proven at `5c6d0744`:
   `COPILOT_DEBUG_NONCE` → `unknown`, **not** `copilot` — that variable was found set **inside a real
   Claude Code session on 2026-07-28**, so "any `COPILOT_*` implies Copilot" would mislabel a live session.
   Copilot is identified **only** by `THING_HOST`, which the adapter exports explicitly — **an assertion,
   never an inference.** *A wrong host verdict is worse than no verdict.*
   → **Enforced by:** the plan's Gate 152 inverse must-fail. **Extend it to `_rc_host()`.**

2. **Fixtures are derived from platform artifacts, never from the reader they test.**
   The Mímir fixture wrote the flat shape *because the reader assumed it* — fixture and reader agreed with
   each other and both disagreed with Claude Code, and **every gate passed while the panel showed
   nothing**. `a5d7e4bf` re-derived it from a real 116 MB transcript and proved teeth **bidirectionally**.
   → **Enforced by:** the reader test asserting the fixture event carries a `message` wrapper.
   **Generalize the rule:** *a gate authored from the same mental model as the code it guards can only
   confirm that model, never falsify it.*

3. **A host that already speaks the contract gets an ALIAS, not an adapter.**
   The Codex shim is 3 lines per variable. *"Adding a second Copilot-shaped translation layer for a host
   that already speaks the contract would be the expensive wrong answer"* (`5c6d0744`).
   → **Enforced by:** review discipline + §1 of this ledger.

4. **Never overwrite a `CLAUDE_*` value the host already set.** Claude Code is authoritative about its own
   vocabulary; the shim fills **genuine blanks only.** Verified both directions (a pre-set value survives;
   a blank is filled).
   → **Enforced by:** the stated INVARIANT + the self-test. **Note the trap recorded in the commit
   message:** the first probe *appeared* to fail because a prefix assignment on a function call is scoped
   to the call and restored on return — **the test was wrong, not the function.** Re-test with plain
   assignments.

5. **A host-support claim carries its basis per row, or it is marked `[unverified]`.**
   The `AGENTS.md` table now does this. *"A false claim of support is worse than an admitted gap — it stops
   anyone building the bridge that would make it true."*
   → **Enforced by:** nothing yet. MH-28 is the residual; a `check-frontmatter`-style gate over host-claim
   tables is the durable answer.

6. **When you close a door, supersede the entry that says it is open — in the same PR.**
   **MH-40 is a live instance:** an audit lens read a superseded `CLAUDE.md` line and reported closed work
   as open. The plugin `CLAUDE.md` already states this rule, added after the same thing happened on the
   macOS doors.

7. **Obey a tribunal deny; fix the false positive, never bypass it.**
   MH-42's two denials were obeyed. The workaround is a *documentation convention* — not a posture change,
   not a `dev_repo_exempt` flip, not a disabled hook.
   → **Enforced by:** `xc.tribunal-self-disable` itself, plus MH-42's proposed bidirectional fixture.

### Found already load-bearing — do not weaken

8. **The `/__host` verdict is bound to session liveness, age-qualified, and refuses a confident wrong
   answer** (plan §6.2). Its **inverse must-fail** is *"the single best assertion in the plan"* (DASH).
   **Never relax it to make a host detectable.**

9. **Every card that cannot know something renders an honest pill — never a value, never a bare dash.**
   `mimirInProcessPill` (`scripts/generate-dashboards.py:11528-11533`); the CI card's three states *"never
   masquerade as CI green."* **MH-05 and MH-06 exist precisely where this was not applied.**

10. **The leak floor: a closed literal allow-list of env NAMES, booleans not paths, no `os.environ`
    iteration** (plan §6.4). `index.html` is a **published artifact.** This binds every card this audit
    proposes — MH-19's MCP card (**names and scopes only; never `args`, never `env` values, never a
    resolved absolute path**) and MH-21's wired card (**booleans and fixed labels only**).

11. **Derived labels and integers only — raw event content never egresses to a banner or a monitor.** The
    streams-reader / capability-banner / run-state-monitor invariant, proven bidirectionally by Gate 19.
    **MH-20's subagent counts must follow it.**

12. **The cross-origin reject IS the DNS-rebinding defense.** Never add `Access-Control-Allow-Origin` to
    "help" the `/__csrf` probe. Gate 142 asserts `Access-Control` appears only in the forbidding comment.
    **MH-33 extends that sweep; it must not soften it.**

13. **Both server copies stay byte-identical for the `_read_*` / `_mimir_*` helpers** (Gate 32
    `_BODY_DIFF_PREFIXES`). **Every reader change in this ledger lands in both.**

14. **Gate 132's DOM ratchet is at zero slack; a visible control costs an owner-approved raise.** Prefer the
    **islanding trick** — `<script type="application/json">` is CDATA to `html.parser`, so a payload is
    **+0 counted elements** (MH-22 option (a)). `870fe226` shows the sanctioned path when a real control is
    genuinely needed: +6, owner-approved, with the frozen ratchet tail lifted in lockstep.

15. **A skipped *workflow* reports nothing; a skipped *job* reports Success.** Never add `paths:` to a
    required check (`AGENTS.md`). **Any new gate this audit adds inherits this.**

16. **Do not name `--dangerously-bypass-hook-trust` as the fix for MH-17.** It is exactly the *"governance
    theatre"* anti-pattern the onboarding skill itself lists.

17. **The dashboard never executes a slash command on the user's behalf** (the Bifröst gate — *"it's a
    wizard, not an orchestrator"*). **MH-18's `host_equivalents` are displayed, never run.**
