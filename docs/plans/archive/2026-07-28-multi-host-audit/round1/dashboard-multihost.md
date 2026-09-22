# Dashboard multi-host audit — round 1

**Lens:** the RavenClaude dashboard judged as a MULTI-HOST surface (Claude Code · Copilot CLI · Codex · Cursor · Gemini · Aider · Windsurf).
**Date:** 2026-07-28 · **Files read this session:** `scripts/generate-dashboards.py` (targeted regions of 13,740 lines), `scripts/_index_dashboard_template.py`, `scripts/generate-index-dashboard.py` (grep-verified), `plugins/ravenclaude-core/scripts/serve-dashboards.py` (full), `plugins/ravenclaude-core/dashboard-assets/shared-tokens.css`, `docs/plans/2026-07-28-prompt-engineering-learn/plan.md` (full), `plugins/ravenclaude-core/bin/rc`, `scripts/ravenclaude` (alias lines), `plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md` (header).

**Framing fact the whole audit hangs on** `[verified]`: the dashboard's live data (Heimdall, Víðarr, Saga, Activity, Mimir, Streams) is written by **hooks**, and hooks fire only under (a) Claude Code natively and (b) Copilot CLI via `copilot-hook-adapter.sh` + `.github/hooks` wiring. Codex / Cursor / Gemini / Aider / Windsurf have **no adapter and no hook path** — the repo's own `AGENTS.md` § "Layout & boundary rules" names CI as the backstop that "catches … Cursor/Codex/Aider edits, and any case where the hook didn't fire." The dashboard renders identical copy to all seven hosts and conditions on none of this.

---

## P0 — dashboard states something FALSE to a non-Claude operator

### P0-1 · Pipeline map asserts guardrails are live ("always" badges) on hosts where no hook ever fires `[verified]`
- **Evidence:** `scripts/generate-dashboards.py:588-907` — `_PIPELINE_LANES` renders every stage with a badge; `reapply-posture`, `guard-destructive`, `enforce-layout`-class stages carry `"badge": "always"` (e.g. `:597`, `:785`, `:800`) with copy like *"Right when the robot wakes up, it loads your settings"* (`:592`) and *"Turns each rule into a real Claude Code permission"* (`:602`). Nothing in the lane data or the render is host-conditioned. Under a Codex/Cursor/Gemini/Aider/Windsurf session none of these hooks execute (no wiring exists — see framing fact), yet the operator's dashboard shows the full guardrail pipeline as active. Under Copilot it is true only if `ravenclaude install` was actually run (the `.github/hooks` wiring), which the page also never checks.
- **Why P0:** "the brake is on" shown to a driver whose car has no brake line. It invites exactly the trust the guardrails exist to earn.
- **Remedy:** (1) add a small static per-stage host-support map (`claude-native | copilot-adapter | none`) alongside `_PIPELINE_STAGE_HOOKS` and render a host-scope line per stage; (2) once the planned `/__host` endpoint exists (see P2-1), render a page-level banner: "Enforcement verified for: Claude Code" / "This host cannot be determined — stages below describe Claude Code + Copilot enforcement; other hosts rely on the CI backstop only"; (3) for Copilot, key the wired-state on `.github/hooks/*.json` presence (a boolean file check, same shape as the plan's §4d card).
- **Effort:** M.

### P0-2 · "Your perimeter has been quiet" renders *unwatched* as *clean* `[verified]`
- **Evidence:** `scripts/generate-dashboards.py:10878` (Heimdall: `"No recent events — your perimeter has been quiet."`) and `:11310` (Víðarr: `"No security events. Your perimeter has been quiet."`). Both fire whenever the served endpoints return zero events. On a host with no hook wiring the JSONL substrate (`.ravenclaude/runs/*/hook-events.jsonl`, `posture-events.jsonl`) is never written, so the panels *always* render "quiet" — asserting surveillance-and-no-findings when the true state is no-surveillance. (Contrast: the Heimdall CI card was deliberately built with three honest states so its empty state "never masquerades as CI green" — the hook cards never got the same treatment for the no-emitter case.)
- **Why P0:** an operator doing a security review under Cursor/Codex reads a green audit log that is structurally incapable of ever showing an event.
- **Remedy:** distinguish "zero events, emitters present" from "zero events, no emitter has ever written here": if no `hook-events.jsonl` / `posture-events.jsonl` exists at all, render "No guardrail telemetry has ever been recorded in this project — hooks emit it under Claude Code and (after `ravenclaude install`) Copilot CLI; other hosts do not emit it," not "quiet." A pure server-side file-existence boolean in `_read_hook_events` / `_read_vidarr_events` (both copies, per the parity discipline) carries it.
- **Effort:** S.

### P0-3 · The dashboard's universal "open it via `rc dashboard`" instruction is broken by the dashboard's own Copilot setup `[verified]`
- **Evidence:** the launch remediation shown in ~10 empty states and the portal banner is literally `rc dashboard` — `scripts/generate-dashboards.py:10491,10709,10738,10854,11086,11147,11284,11371,11507,11672`; `scripts/_index_dashboard_template.py:987` (`const SERVED_CMD = "rc dashboard"`). But the dashboard's own Install & Update tab tells the Copilot operator to create `alias rc='bash scripts/ravenclaude update && copilot --plugin-dir plugins/ravenclaude-core/copilot'` (`scripts/generate-dashboards.py:1582-1586`), and the installer writes the same alias into the shell rc file (`scripts/ravenclaude:46`, printed again at `:246`). In an interactive shell an alias shadows a PATH binary, so for exactly the Copilot operator, `rc dashboard` runs *update-then-launch-Copilot* with a stray `dashboard` argument — not `plugins/ravenclaude-core/bin/rc dashboard` (the dispatcher whose `dashboard` verb the message intends; `bin/rc:1-24`).
- **Why P0:** the dashboard's only self-repair instruction, followed as written after the dashboard's own onboarding, does the wrong thing for the flagship non-Claude host. (The generated `copilot/AGENTS.md` DASHBOARD_BLOCK dodges this by using the full `bin/rc` path — the agent path works, the human path doesn't.)
- **Remedy:** resolve the name collision once: either rename the installer alias (e.g. `rcc`), or make the alias point at `bin/rc` and teach `bin/rc` an `update`/launch verb, or change every empty-state string to the unambiguous full-path form. One decision, then a mechanical sweep of `SERVED_CMD` + the `sagaEmptyPanel`/`hmEmpty` call sites.
- **Effort:** S.

---

## P1 — a host is materially underserved

### P1-1 · Mimir "Session" — the Activity destination's session panel — is Claude-only with no host framing `[verified]`
- **Evidence:** `plugins/ravenclaude-core/scripts/serve-dashboards.py:1038-1253` — `_read_mimir` reads only `~/.claude/**` + `.claude/settings.json`; the honest empty state (`exists: False`, `:1119-1121`) is documented as "first-time host." `scripts/generate-dashboards.py:7266-7272` (panel intro: "Claude Code session state for this project"), `:11560-11575` ("No live Claude Code session found for this project"), `:11617` ("No recent JSONL sessions for this project"). Portal nav labels it plainly **Session** (`scripts/_index_dashboard_template.py:1073`).
- **The gap:** a Copilot/Codex operator with a *live session right now* opens "Session" and sees empty Claude-shaped cards. The wording is technically honest ("no live **Claude Code** session") but the panel never says the load-bearing thing: *this panel cannot see non-Claude sessions at all*. "No recent JSONL sessions" reads as "you have no history," not "your history lives somewhere I don't read." There is no equivalent panel for any other host's session state.
- **Remedy:** (1) when `/__host` (P2-1) says the host isn't Claude Code — or can't be determined — render a header card: "This panel reads Claude Code's on-disk session state (`~/.claude/`). Sessions from other hosts are not visible here." (2) longer-term, a per-host reader behind the same card contract (Copilot's on-disk session state would be a candidate — `[inferred]`, its paths are unverified this session; do not build from memory).
- **Effort:** S (banner) / L (readers).

### P1-2 · The posture editor's Deny/Ask/Allow promise is host-unconditioned, and its fallback is a Claude-only slash command `[verified]`
- **Evidence:** category intro — "you pick **Deny** (never), **Ask** (check with me first), or **Allow**" (`scripts/generate-dashboards.py:2132-2141`); Save & apply runs `apply-comfort-posture.py` whose sole output is `.claude/settings.json` (`plugins/ravenclaude-core/scripts/serve-dashboards.py:142-145,1837-1852`); the no-server fallback says "run `/set-posture`" (`scripts/generate-dashboards.py:6600`) — a Claude Code slash command (Copilot "has no user slash commands yet," per the plugin CLAUDE.md § Copilot bridge). `.claude/settings.json` permission rules are read by Claude Code's permission engine; under Copilot the posture's teeth are the hooks + the Thing (which the command-review disclaimer at `:2304-2321` does explain — for the tribunal only, not for the plain category levels), and under the other five hosts nothing reads it.
- **The gap:** the editor's central interaction ("Ask = check with me first") describes enforcement only one host delivers, one host partially delivers via a different mechanism, and five hosts don't deliver at all — with no scope note anywhere on the Settings tab.
- **Remedy:** one host-scope line under the category intro mirroring the command-review disclaimer's honesty: "These levels bind Claude Code's permission engine. Under Copilot CLI, enforcement comes from the wired hooks + command review; under other hosts the posture is advisory and CI is the backstop." Condition the `/set-posture` hint on host (or add the shell equivalent alongside).
- **Effort:** S.

### P1-3 · Onboarding lanes exist for exactly two hosts; the other five have none — despite the repo already shipping the content `[verified]`
- **Evidence:** the Help drawer holds exactly an "Install & Update — Claude Code" lane (Bifröst, `scripts/generate-dashboards.py:7406-7408`) and an "Install RavenClaude — GitHub Copilot CLI" lane (`:6631-6647`), each cross-linking only the other ("**Using Claude Code instead?**" / "**Using GitHub Copilot CLI instead?**"). Grep of `generate-dashboards.py`, `_index_dashboard_template.py`, and `generate-index-dashboard.py` finds **zero** occurrences of codex/cursor/gemini/aider/windsurf as hosts. Meanwhile `plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md` exists precisely for "GitHub Copilot CLI / Cursor / Aider / Codex / Devin" and has a ready-made "first five minutes" sequence.
- **Remedy:** a third Help-drawer section, "Other agents (Codex · Cursor · Aider · Windsurf · Gemini)", generated as a projection of `codex-onboarding`'s first-five-minutes + the AGENTS.md pointer + an honest enforcement note ("no hooks fire under these hosts; CI is the gate"). Static content, works on Pages, no new endpoint. Follow the plan's §4b projection discipline (fail loudly if the source heading moves).
- **Effort:** S/M.

### P1-4 · The Commands catalog teaches Claude-only invocation for every command `[verified]`
- **Evidence:** `scripts/generate-dashboards.py:1670-1762` — every Class-B card renders "copy it, then paste into Claude Code" (`:1710-1719`), and the tab intro says "Copy a command and paste it into your Claude Code session" (`:1750-1754`). No card carries a non-Claude alternative even where one exists and is documented elsewhere in the same file: `/dashboard` ≡ `rc dashboard`, `/stream` ≡ `rc streams …` (`bin/rc` usage text), `/set-posture` ≡ the Run button's `apply-comfort-posture.py`. A Copilot/Codex operator browsing the catalog is handed instructions that cannot work in their host, with no signpost.
- **Remedy:** extend the data-driven classifier: an optional `host_equivalents` map (command → `{copilot: "...", shell: "..."}`) sourced from command frontmatter, rendered as a second line on the card ("Not in Claude Code? run: `…`"). Where none exists, say so ("Claude Code only").
- **Effort:** M.

### P1-5 · The cross-tool instruction file's only dashboard-launch route is a Claude-only slash command `[verified]`
- **Evidence:** root `AGENTS.md` § Setup commands — "open the dashboard's **Install a plugin (Bifröst)** tab (`/dashboard` → `#/bifrost`)". `AGENTS.md` is the file "Cursor, OpenAI Codex CLI, Aider, GitHub Copilot, and Windsurf read … natively" (its own opening line), and `/dashboard` exists only in Claude Code. The Copilot-specific fix (the generated DASHBOARD_BLOCK in `copilot/AGENTS.md`, per plugin CLAUDE.md v0.158.0) covers one host; the file the other five read still routes them to a command their host doesn't have. Net effect: an operator under Codex/Cursor has no in-band way to learn how to launch the dashboard at all.
- **Remedy:** amend the root `AGENTS.md` line to lead with the host-agnostic path (`bash plugins/ravenclaude-core/bin/rc dashboard` — full path, per P0-3) and mark `/dashboard` as the Claude Code shorthand.
- **Effort:** S.

---

## P2 — clear-value improvement

### P2-1 · The pending "Host & context" plan is the right v1 shape — approve it, with two extensions `[verified]` (plan read in full)
- **Assessment of `docs/plans/2026-07-28-prompt-engineering-learn/plan.md`:** the Control-side page (D3) is exactly the right first move for host-awareness, and its hard edges are correct, not timid: the one-sided detector (§6.1 — Claude Code positively detectable; Copilot has **no documented session signal**, so "GitHub Copilot CLI" is *never rendered*, enforced by Gate 152), the liveness binding (§6.2 — a reused server must not assert a stale host; the inverse must-fail is the single best assertion in the plan), the closed env-NAME allow-list + booleans-not-paths leak floor (§6.4), and `/__host`/`_read_host` naming that buys Gate-32 body parity for free (§6.3). Control = "what am I in / what is wired" is the right destination; ALT-5's rejection is sound.
- **Gap A — the verdict is an island.** As planned, `/__host` feeds only the new page. The three P0/P1 surfaces above (Pipeline badges, Heimdall/Víðarr "quiet", Mimir's framing) each need exactly this verdict to become honest. Extend the plan (or a fast-follow) so the client caches the `/__host` result once and the other panels consume it for their host-scope banners — otherwise the dashboard will contain one honest page surrounded by the same unconditioned ones.
- **Gap B — a two-host worldview.** §4b/§4d source the precedence table from `copilot-cli-customization.md` + `code.claude.com/docs/en/memory`, and the wired-state file list is `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`, comfort-posture, environment-context, `.github/copilot-instructions.md` — Claude + Copilot only. The page's teaching copy should at least *name* the other five hosts and state that they read `AGENTS.md` (the repo's own claim) and nothing else here is wired for them; wired-state rows for their instruction files can follow once sourced (`[inferred]` — their exact file conventions were not verified this session and must not be authored from memory, per the plan's own claim-#12 discipline). Also worth a row: `.github/hooks/` presence (the Copilot enforcement wiring — more load-bearing than `copilot-instructions.md` for what the dashboard claims elsewhere).
- **Effort:** S (consume-the-verdict banners ride the existing JS panels; the page itself is already planned).

### P2-2 · Publish the per-stage host-support matrix as data, not prose `[verified]`
- **Evidence:** `_PIPELINE_STAGE_HOOKS` (`scripts/generate-dashboards.py:889-907`) already maps stage → hook; the plugin CLAUDE.md already knows per-surface facts (monitors are "Claude-Code-only"; slash commands don't port; hooks port via the adapter). Nothing machine-readable states, per hook, which hosts execute it — which is why every dashboard surface (and Gate 133) is silent on host scope.
- **Remedy:** add a `host_support` field per stage (`{claude: native, copilot: adapter, other: none}`) next to `_PIPELINE_STAGE_HOOKS`, render it in the stage detail, and let Gate 133 require it — the P0-1 fix then becomes data-driven instead of copy-by-copy.
- **Effort:** M.

### P2-3 · The four destinations survive multi-host scrutiny — keep the IA, fix the interiors `[verified]`
- **Assessment:** Control (posture) / Activity (what happened) / Guardrails (what tripped) / Catalog (what's installed) are host-neutral *jobs* — nothing about the cut is Claude-shaped, and the substrate under Activity/Guardrails (`.ravenclaude/runs/**`, streams, Saga) is deliberately host-neutral (the Copilot adapter exports `CLAUDE_SESSION_ID` so events land in the right run dir). What is Claude-shaped is specific interiors: Mimir under Activity (P1-1), the Pipeline under Control (P0-1), the Help lanes (P1-3). No IA re-cut is warranted; the multi-host work is banners, empty states, and one new Control page — which is exactly the shape the pending plan already takes.
- **Effort:** — (a conclusion, not a work item).

---

## P3 — nits / polish

### P3-1 · "Learn & Help" self-description enumerates two hosts as the whole world `[verified]`
- **Evidence:** `scripts/generate-dashboards.py:395` ("install & update guides for Claude Code and GitHub Copilot CLI"), `:328` (Help drawer sections: "the About, Claude Code, Copilot CLI, and Commands sections"). Once P1-3 lands, these strings must grow a third clause; until then they advertise the gap.
- **Remedy:** wording change alongside P1-3. **Effort:** S.

### P3-2 · Mimir's in-process pills give Claude-only advice without the panel-level caveat `[verified]`
- **Evidence:** `scripts/generate-dashboards.py:11531` (pill title "In-process only — run /status in Claude Code to see this live"), `:11557`, `:11573`. Defensible inside a Claude-labeled panel; becomes fine automatically once P1-1's host banner exists.
- **Remedy:** none beyond P1-1. **Effort:** —.

### P3-3 · Prompt Builder never states it targets Claude models `[verified]`
- **Evidence:** `scripts/generate-dashboards.py:362-374` — the builder "assembles a best-practice **Claude** prompt" (docstring), and its linter rules are Claude-version-specific (prefill → 400 on Claude 4.6+). A Copilot operator routing GPT/Grok gets rules presented as universal prompt hygiene. Mostly they transfer; the deprecation/model-tuning rules don't necessarily.
- **Remedy:** one visible "Targets Claude models; other models' conventions may differ" line in the tab intro. **Effort:** S.

---

## Answers to the audit's five direct questions

1. **Panels showing Claude-only state without honest empty states for other hosts:** Mimir (P1-1) is the clean case; Heimdall/Víðarr are worse — their empty state is *affirmatively misleading* on non-hooked hosts (P0-2). Pipeline asserts state rather than showing it (P0-1).
2. **Language assuming slash commands / Claude features:** Commands tab (P1-4), Settings `/set-posture` fallback (P1-2), root `AGENTS.md` `/dashboard` (P1-5), Mimir `/status` pills (P3-2). Plan mode / subagents / MCP language on the dashboard is largely confined to appropriately-scoped contexts (the command-review disclaimer at `:2304-2321` and the orchestrator knob at `:981-988` are the two places the dashboard is *already* explicitly host-aware — they are the house style the rest should copy).
3. **Can a Copilot/Codex operator launch it, and does it tell them anything true about their session?** Copilot: launchable (the `copilot/AGENTS.md` DASHBOARD_BLOCK full-path route works) but the human-facing `rc dashboard` instruction is broken by the prescribed alias (P0-3); the dashboard then tells them nothing about their session (P1-1) and misstates their guardrail state (P0-1/P0-2). Codex/Cursor/Gemini/Aider/Windsurf: no in-band launch route at all (P1-5), and once launched, the same misstatements plus zero onboarding (P1-3).
4. **Do the four destinations still make sense?** Yes — keep them (P2-3). The Claude-shape lives in interiors, not the IA.
5. **Served-vs-static degradation:** genuinely good — the `/__csrf` probe tri-state, the "needs the served dashboard" empty states, and the CI card's three honest states are the strongest honesty machinery in the estate. The one lie in the degradation story is not served-vs-static but *emitting-vs-non-emitting host* (P0-2), plus the broken remediation command the honest states hand out (P0-3).

## Counts
P0: 3 · P1: 5 · P2: 3 · P3: 3
