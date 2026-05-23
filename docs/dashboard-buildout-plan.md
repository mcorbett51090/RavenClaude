# Dashboard build-out plan

*Living planning document. First draft 2026-05-22 (overnight). Iteratively refined.*

> **Status:** PLAN — not a commitment to ship. This document captures the design space for the next major phase of the RavenClaude dashboard. Sequencing, scope, and version numbers are proposals, not promises.

> **Scope of this document:** the **product-facing** dashboard at `plugins/<plugin>/dashboard.html`. The marketplace's separate `repo-guide.html` (the read-only catalog) is mentioned only at composition boundaries. This document does not duplicate proposal-003 — it picks up where 003 left off and answers the next-layer questions Matt asked.

---

## Table of contents

This document grew from v1 (925 lines) to v14 (3,000+ lines) over 14 iteration passes. The TOC below reflects all sections — read top-to-bottom for context, or jump to specific subsections via the anchor links.

1. **Current state** — what the dashboard is today, in one page
   - 1.1 What ships at v0.17.0
   - 1.2 How the dashboard persists changes — the critical constraint
   - 1.3 How the posture is applied today
   - 1.4 Claude Code's settings precedence — the merge model (load-bearing; **corrected v2**)
2. **Phase A — multi-layer comfort posture** (user / project / local)
   - 2.1 The problem in one paragraph
   - 2.2 The default rule we recommend
   - 2.3 The mechanism (8 subsections)
     - 2.3.3 Precedence interaction — what happens if posture lands at multiple layers (CORRECTED v2)
     - 2.3.5 Dashboard UI — scope selector (revised v2 for merge model)
     - 2.3.8 Concrete YAML and settings.json — what the emissions look like (v6)
     - 2.3.9 Concrete code sketch — `apply-comfort-posture.py --scope` (v12)
     - 2.3.10 Concrete code sketch — scope-selector HTML in the Settings tab (v12)
   - 2.4 Edge cases & gotchas
   - 2.5 Tests that have to pass
   - 2.6 Effort estimate
3. **Phase B — dashboard build-out**
   - B.1 Information architecture
   - B.2 Slash-commands tab
     - B.2.1 Three UI design alternatives (card grid / palette / accordion / builder)
     - B.2.2 Comparison matrix — head-to-head decision rubric (v3)
     - B.2.3 Recommendation (card grid + palette overlay)
     - B.2.4 Click behavior — deep-link mechanic in detail
     - B.2.5 Concrete card markup — HTML/CSS/JS sketch (v12)
   - B.3 Startup / install area
     - B.3.1-B.3.4 Tab covering, design, first-touch UX
     - B.3.5 Chicken-and-egg problem (v3)
     - B.3.6 Private-marketplace access (v3)
     - B.3.7 Failure modes (v3)
   - B.4 Other panels worth adding
     - B.4.1 Agents tab — full design (v7)
     - B.4.2 Environment tab — full design (v8)
     - B.4.3 Scenarios tab — full design (v8)
     - B.4.4 Health tab — full design with merge-resolver JS (v6)
     - B.4.5 Update notifier — banner + Changelog tab (v7)
   - B.5 Accessibility & i18n checklist (v7)
   - B.6 Deep-link mechanic — fallback chain (v7)
4. **Phase C — per-agent slash commands across all 7 plugins** (~141 commands)
   - 4.1 ravenclaude-core (14 agents)
   - 4.2 power-platform (11 agents)
   - 4.3 finance (7 agents)
   - 4.4 regulatory-compliance (6 agents)
   - 4.5 web-design (7 agents)
   - 4.6 edtech-partner-success (6 agents)
   - 4.7 data-platform (4 agents)
   - 4.7.1 Additional commands from per-plugin verification (v7) — +42 commands
   - 4.8 Cross-cutting observations
   - 4.9 Naming and namespacing — built-in collisions (v4)
   - 4.10 Verifying owner agents actually exist (v4)
5. **Phase D — risks, open questions, sequencing**
   - 5.0 Implementation kickoff — what to do tomorrow morning (v14)
   - 5.0.1 Lessons-from-prior-ships retro (v0.15.0/0.16.0/0.17.0) (v14)
   - 5.1 Risks — R1-R20, severity-scored (v14)
   - 5.2 Open questions for Matt (Q1-Q14)
   - 5.3 Phased build roadmap (revised v8 with detailed estimates)
     - 5.3.1 `/__save` and `/__read` allow-list — concrete list (v8)
     - 5.3.2 Glossary — 17 terms used in this plan (v8)
   - 5.4 Tests and CI implications
   - 5.5 Dependency graph — what blocks what (v5)
   - 5.6 Decisions taken in this document vs decisions deferred (v5)
   - 5.7 Composition with proposal 003 (v5)
   - 5.8 First 30 minutes — brand-new user's experience narrative
     - 5.8.1 Second narrative — team admin onboards a team (v9)
     - 5.8.2 Decision summary — D1-D20 + Q1-Q14 (v9)
     - 5.8.3 v0.18.0 ship checklist (v11)
     - 5.8.4 Phase C first-5-per-plugin prioritized shortlist (v11)
     - 5.8.5 Phase A migration runbook with day-by-day sequence (v11)
     - 5.8.6 Telemetry — local-only usage.json (v11)
     - 5.8.7 Plugin-author guide — command frontmatter shape (v13)
     - 5.8.8 Success criteria — feedback signals + anti-signals (v13)
     - 5.8.9 Stretch goals — 15 items deliberately deferred (v13)
     - 5.8.10 Concrete `latest-versions.json` example (v13)
   - 5.9 What we explicitly do NOT plan in this document
6. **Appendix — references**
7. **Iteration log** — v1 through v14 changelog

**v2 headline change:** The §1.4 and §2.3.3 sections have been rewritten to reflect Claude Code's actual cross-layer permission semantics, which the v1 draft got wrong. Permission rules **MERGE** across the user / project / local layers (they don't override per-layer), with `deny > ask > allow` resolving within the merged set, and any `deny` in any layer being absolute. This changes the Phase A recommendation's *rationale* (project file is a permission floor, not a default) without changing the recommendation itself (user-scope default). The dashboard UI in §2.3.5 is updated accordingly.

---

## Executive summary — 2-minute read

For a busy reader. Skip if you're reading the full document.

**What this plan covers.** The next major build-out of `plugins/<plugin>/dashboard.html` (the product-facing per-plugin dashboard, currently at v0.17.0 with one live tab and three stubs). Three workstreams:

- **Phase A — Multi-layer comfort posture.** Add `--scope user|project|local` to `/set-posture` so personal posture lives at the user layer (machine-default), not the project file. Default scope changes from project → user. Comes with a migration banner, a Health-tab diagnostic surface, and an updated `.gitignore` flow for `.claude/settings.local.json`. Reason: today's project-only behavior leaks personal habits into team git history and creates surprise when teammates pull. **Effort: 8-11 hours + Health tab 18-20 hours (ship together).**

- **Phase B — Dashboard build-out.** Fill in the three stubs (Commands / Trees / Activity) and add three new tabs (Install / Agents / Health) + one stretch tab (Environment). The **Commands tab** is the headline new surface: a card-grid of all available slash commands, each with a deep-link "Launch" button that pre-fills `claude-cli://open?q=<command>` (degrades to Copy if no handler). The **Install tab** walks new users through prerequisites → `/plugin marketplace add` → install → verify → first-session setup. The **Health tab** surfaces the merge model with an interactive "Test a tool call" box, so the user can see exactly which rule from which layer drives a permission ask. **Effort: ~80-100 hours across 5 sub-phases.**

- **Phase C — Per-agent slash commands.** Today: 3 commands, all in ravenclaude-core. Proposed: **~141 commands distributed across all 55 agents** in the 7 plugins (≈2.5 per agent). Per-plugin tables in §4.1-§4.7 with owner, args, notes; verified against actual agent frontmatter by three parallel research passes. Top 20 most-used commands surface as the Commands tab's default view. **Effort: 2-4 hours per command, ship rolling.**

**The five things to decide first** (D1-D5 from §5.8.2):

1. **D1: Default scope for `/set-posture` becomes `user`** (was project). The merge model means user-scope is the right default for personal posture; project file is reserved for team-shared rules.
2. **D5: Card-grid for the Commands tab** (with `⌘K` palette overlay later). Discoverable for new users; fast for power users via the overlay.
3. **D7: Three new tabs (Install + Agents + Health)** are ranked must-have. Environment, Scenarios, and Update notifier are nice-to-have.
4. **D12: Ship Phase A + Health tab together as 0.18.0.** Phase A introduces the merge model; without the Health tab to make it visible, the user-scope default creates surprise.
5. **D14: Add `/__read` endpoint to `serve-dashboards.py`** with the allow-list table in §5.3.1. Required by Health, Agents, and Environment tabs.

**The four "first 4 weeks" milestones** (§5.3):

- Week 1-2 (~30h): Ship 0.18.0 = Phase A (scope flag + migration banner) + Health tab full UX.
- Week 3 (~10h): Ship 0.19.0 = Commands tab Design 1 with the 3 existing commands.
- Week 4 (~10h): Ship 0.20.0 = Install tab + `/install-doctor` + plugin switcher.

After 60 hours of focused work, the dashboard is meaningfully better. Everything else (Agents, Update notifier, Phase C command sprawl) is incremental.

**The single biggest correction from v1 to v2.** I initially wrote that permissions resolve as "local > project > user precedence — the more-specific layer wins." That is **wrong**. Permissions MERGE across layers; the resolved set is evaluated `deny > ask > allow`; any deny in any layer is absolute. This means a permissive user-layer rule can be silently shadowed by a tighter project-layer rule (correct safety behavior), and a user-layer `deny` is sticky across every project on the machine (be deliberate). The §1.4 / §2.3.3 sections are now correct; everything downstream that depended on the wrong claim has been re-derived.

**Open questions you'll be asked to confirm** (§5.8.2 Q1-Q14): 14 items, each with a default behavior if you don't answer. Most prominent: rename `/security-review` to `/team-security-review` to avoid colliding with the Claude Code built-in; add `/rc:` qualified prefix for infrastructure commands; rename "Install" tab to "Setup."

---

## 1. Current state

### 1.1 What ships at v0.17.0

`plugins/ravenclaude-core/dashboard.html` is **2,630 lines** of self-contained HTML — inline CSS, inline vanilla JS, no CDN dependencies. It is generated by `scripts/generate-dashboards.py` from `plugins/ravenclaude-core/dashboard-schema.json` (the source of truth for category list, levels, presets, recommendations, info-modal copy) and `plugins/ravenclaude-core/pattern-explanations.json` (the per-Bash-pattern modal copy). Footer: *"Generated by `scripts/generate-dashboards.py`. Source schema: `plugins/ravenclaude-core/dashboard-schema.json`. Design: proposal 003."*

| Tab | Status | What it does today |
|---|---|---|
| **Settings** | live | 12-category permission posture editor with 5-level segmented control per category, 5 presets (Recommended / Deny / Always-ask / Mostly-ask / Mostly-allow / Autopilot), collapsible per-pattern overrides, info modal per category, info modal per pattern, live YAML status indicator |
| **Commands** | stub | `<div class="stub"><h2>Commands tab</h2><p>Ships in v0.2.0.</p></div>` |
| **Trees** | stub | same — stub |
| **Activity** | stub | same — stub |

Three slash commands ship today: `/init-agent-ready`, `/set-posture`, `/wrap`. Across the marketplace's 55 agents, **only ravenclaude-core has commands** — the other six plugins (power-platform, finance, regulatory-compliance, web-design, edtech-partner-success, data-platform) have zero.

### 1.2 How the dashboard persists changes — the critical constraint

A static HTML page cannot freely write files. The dashboard threads three mechanisms (in **decreasing** priority):

1. **`POST /__save` endpoint** — primary save path when `scripts/serve-dashboards.py` is running. The Python server exposes a `POST /__save` endpoint with a hard-coded **allow-list** of target paths (`{.ravenclaude/comfort-posture.yaml, .ravenclaude/environment-context.md}`) and a path-traversal check. The dashboard probes the endpoint with `HEAD /__save` on load and shows/hides the "Save to repo" button based on availability. *Available in:* Codespaces, local dev with `python3 scripts/serve-dashboards.py`. *Not available in:* GitHub Pages, `python3 -m http.server`, raw `file://`.

2. **File System Access API** — secondary save path. User clicks "Auto-save to file…" once, picks a target file via `window.showSaveFilePicker()`. The dashboard persists the `FileSystemFileHandle` in **IndexedDB** (`ravenclaude-dashboard` DB, `handles` store), and writes on every change. After page reload the handle is restored from IDB but permission needs re-granting (`queryPermission` returns `"prompt"`; touching any control re-grants on the user gesture chain). *Available in:* Chrome, Edge, Opera. *Not available in:* Firefox, Safari (feature-detected → button hidden, fallback help line shown).

3. **Manual Copy / Download** — fallback. Always available. The user pastes / moves the YAML into `.ravenclaude/comfort-posture.yaml` themselves.

**Why this matters for everything downstream.** Every new tab the dashboard ships has to honor this same triple-path model (or accept that it works in only one of the three environments). The slash-commands tab does NOT need persistence because it's read-only / launch-only. But the multi-layer posture work (Phase A below) DOES need persistence — and the current `/__save` allow-list only covers two paths.

### 1.3 How the posture is applied today

After saving the YAML, the user runs `/set-posture` (or invokes `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/apply-comfort-posture.py` directly). That script:

- Walks the EMISSIONS table — 12 categories, each with a hand-curated list of narrow patterns like `Bash(git push:*)` (NOT broad shapes like `Bash(*)`, because auto-mode silently drops broad allow rules).
- Resolves each pattern's level via **per-pattern override > category default > global_default**.
- Unions in the top-level `security_deny` list (default baseline: `.env` reads, `rm -rf:*`, `git push --force:*`, `curl | sh`, etc.).
- **Overwrites** (not merges) `permissions.{allow,ask,deny}` in `.claude/settings.json` (project layer).
- Cleans up the v0.16.0 snapshot file if present.

The script's **footer warning** is load-bearing context: *"Hand-edits to `permissions.allow/ask/deny` are wiped on next `/set-posture`. Put personal overrides in `.claude/settings.local.json` instead — Claude Code merges that on top of this file."* This is the gravitational pull toward Phase A.

### 1.4 Claude Code's settings precedence — the merge model (load-bearing)

> **CORRECTION over the v1 draft.** The v1 of this document described cross-layer precedence as "local > project > user" — the more-specific layer wins per-pattern. **That is wrong for `permissions.{allow,ask,deny}`.** The correct model, from `plugins/ravenclaude-core/knowledge/claude-code-permissions.md` and the upstream `code.claude.com/docs/en/permissions` page, is: permission rules **MERGE** across layers, and **`deny` always wins cross-layer** regardless of which layer it lives in. Within the merged set, `deny > ask > allow`. This changes the Phase A reasoning materially — see §2.3.3 (rewritten).

| Layer | File | Scope | Tracked by git? |
|---|---|---|---|
| **Enterprise (managed)** | `/etc/claude-code/managed-settings.json` (Linux), `/Library/Application Support/ClaudeCode/managed-settings.json` (macOS), `C:\ProgramData\ClaudeCode\managed-settings.json` (Windows) | Org-wide, set by IT | No (machine-managed) |
| **Command-line flags** | `claude --add-dir`, `--dangerously-skip-permissions`, etc. | Single session | n/a |
| **Local** | `.claude/settings.local.json` | Per-project, per-user | **gitignored by Claude Code's default `.gitignore` install** |
| **Project** | `.claude/settings.json` | Per-project, team-shared | Committed |
| **User** | `~/.claude/settings.json` | All projects, this machine | No (machine-local) |

**For non-permission settings** (theme, model, hooks blocks, `env`, etc.) the layer order is enterprise > flags > local > project > user — the more-specific layer wins, the less-specific layer is the fallback.

**For `permissions.{allow,ask,deny}` specifically the model is different:**

1. **Rules MERGE across layers.** Every rule from every layer is in scope simultaneously. There is no "local layer overrides project layer" for permission rules. If `~/.claude/settings.json` says `allow: ["Bash(git push:*)"]` and `.claude/settings.json` says `ask: ["Bash(git push:*)"]`, both rules are live; the engine resolves per-call.
2. **Per-call resolution is `deny → ask → allow`.** The most-restrictive *applicable* rule wins. So under the example above, the merged set contains both `ask Bash(git push:*)` and `allow Bash(git push:*)`; per the deny>ask>allow rule, the call **asks**.
3. **`deny` in ANY layer is absolute.** A `deny: ["Bash(rm -rf /*)"]` at the user layer blocks the call even if the project layer says allow. A deny at the enterprise layer cannot be overridden by anything below. *This is the security floor — and it's why a team-shared deny in `.claude/settings.json` is a hard constraint individual users cannot relax.*

**Practical consequences for Phase A** (expanded in §2.3.3):

- **A user-scope `allow` cannot loosen a project-scope `ask`.** If the team has decided `git push` is ask-only at the project layer, no amount of personal user-scope or local-scope posture can autopilot it. The personal-comfort use case where this matters is the user wants to be MORE permissive than the team — and **they can't.** They can only be more restrictive.
- **A local-scope `deny` will block calls the project allows.** This is the lever a cautious user pulls if they're uncomfortable with the team's project-layer permissiveness. The team can't stop them; that's correct.
- **The `ask` bucket is sticky.** Once any layer has `ask: Bash(X)`, no other layer can override to `allow: Bash(X)` because ask>allow in the merged-set resolution.

Phase A's "personal comfort = user scope, team policy = project scope, per-project override = local scope" framing therefore works *only* in the direction of MORE restriction. To put it bluntly: **`.claude/settings.json` becomes a permission floor for the team. `.claude/settings.local.json` and `~/.claude/settings.json` are personal additions on top — they can deny more, ask more, or allow patterns the project doesn't mention, but they cannot relax what the project restricts.** This is the right behavior for the multi-developer case but is a non-obvious gotcha when designing the dashboard's scope selector — see §2.3.6.

---

<a id="phase-a"></a>
## 2. Phase A — multi-layer comfort posture (user / project / local)

### 2.1 The problem in one paragraph

Today `/set-posture` only writes the **project** layer. For Matt working alone, that's fine: he edits the YAML once, applies, the rules land in `.claude/settings.json`, git tracks them, every session uses them. But the moment two people share the same project, the project file becomes contested — Matt is autopilot-curious on `shell_local_mutate`, his colleague is always-ask-tense on the same category. The current system can't represent that. The architectural answer was named in proposal 002 §6.3, in proposal 003 §7.1, and in the script's own footer warning: **personal posture belongs in `.claude/settings.local.json` (the local layer); team-shared posture belongs in `.claude/settings.json` (the project layer); machine-default posture belongs in `~/.claude/settings.json` (the user layer).** The work is wiring those three layers into the dashboard and the translator.

### 2.2 The default rule we recommend

> **A "comfort posture" is a personal trait. Personal traits belong at the user layer or the local layer, not the project layer.**

Concretely: the **default** scope for `/set-posture` becomes **user** (`~/.claude/settings.json`) — that's "this is how I work everywhere on this machine." The **opt-in** scopes are **local** (`.claude/settings.local.json`) — "this is how I work in just this project" — and **project** (`.claude/settings.json`) — "this is how *the team* works in this project; check it in." The user picks the scope per `/set-posture` invocation; the dashboard remembers their last choice (per-plugin, per-machine, persisted in `localStorage`).

The rationale traces directly to the "5 of 5 domain plugins have no plugin-specific security reviewer" precedent in `plugins/ravenclaude-core/CLAUDE.md` (House rule: domain plugins extend core via skills and knowledge, not parallel agents). The same logic applies to permission rules: **share what is genuinely team-policy; keep what is genuinely personal preference out of the shared file.** The current default — write to project — is a footgun that gets caught and reverted on PR review by anyone with a different posture from Matt.

### 2.3 The mechanism — what changes where

#### 2.3.1 Dashboard UI — scope selector (initial sketch; superseded by 2.3.5)

> *This subsection records the v1 sketch of the scope selector before the merge-model investigation. The actual recommended design is in [§2.3.5](#235-dashboard-ui--scope-selector-revised-for-merge-model), which treats Project scope as a load-bearing team-policy choice rather than a peer of User/Local.*

Above the preset bar, a new compact row:

```
   Apply posture to:  [● User  ○ Project  ○ Local]    ⓘ What's the difference?
```

- Default: **User** (radio pre-selected).
- The radio group is keyboard-navigable (Arrow keys within, Tab between groups — WAI-ARIA APG radio pattern, already in use elsewhere in the dashboard).
- "What's the difference?" opens an info modal with the precedence table from §1.4 + a one-paragraph plain-language description per scope:
  - **User:** "this is how I want Claude to behave in all my projects on this machine. Default. Doesn't get committed."
  - **Project:** "this is how the team agrees Claude should behave in this project. Committed to git. Use sparingly — only for shared safety floors (deny `npm publish`, ask before `git push`)."
  - **Local:** "this is how I want Claude to behave in just this project. ~~Overrides the project file for me only.~~ *(Strikethrough: this v1 claim was wrong — see §2.3.3. Local-scope cannot relax a project-scope rule; it can only further restrict.)* Gitignored."

The selector affects only **which scope `/set-posture` writes to.** The YAML file itself stays in one place (`.ravenclaude/comfort-posture.yaml`); the **emission target** changes.

#### 2.3.2 `apply-comfort-posture.py` — `--scope` flag + per-scope snapshot

The translator script grows a `--scope {user,project,local}` flag. Defaults to `user` (the new default; matches the dashboard's pre-selected radio).

| `--scope` | Writes to | Resolved at script time |
|---|---|---|
| `user` *(default)* | `~/.claude/settings.json` | `Path.home() / ".claude" / "settings.json"` |
| `project` | `<project_root>/.claude/settings.json` | unchanged from today |
| `local` | `<project_root>/.claude/settings.local.json` | new |

**Snapshot tracking — per-scope, separate files:**

The v0.17.0 cleanup logic deletes a stale `_comfort-posture-snapshot.json` from v0.16.0. The new design intentionally **does not re-introduce a snapshot file** at any scope. Reason: the v0.17.0 architecture is "overwrite, not merge" — the posture YAML is the single source of truth for `permissions.{allow,ask,deny}` at whatever scope the user targets, and hand-edits to those buckets at that scope are wiped on next `/set-posture`. Adding a snapshot per scope re-introduces the snapshot-merge complexity that v0.17.0 deliberately removed.

What we DO add: a **`# Last applied: <ISO-8601 timestamp> by /set-posture (scope=user)`** comment line at the top of the rules array in the target settings.json (machine-readable for tooling, human-readable for diffs). Claude Code's settings.json schema tolerates `//`-style comments? *(open question — verify; if not, store the timestamp inside a side-car file at `.claude/.comfort-posture-applied.json` per scope, gitignored by default.)*

#### 2.3.3 Precedence interaction — what happens if posture lands at multiple layers (CORRECTED)

This subsection is the heart of Phase A's design. The v1 draft of this document got the model wrong (described layer-wins precedence); the corrected model is **merge with `deny > ask > allow`** (see §1.4). The implications for `/set-posture` are significant and reshape the recommendation.

**The scenario.** Matt has applied posture at all three scopes:

1. `/set-posture --scope user` with all categories on `mostly-allow`.
2. `/set-posture --scope project` with `shell_remote_mutate` on `always-ask` (the team's shared rule).
3. `/set-posture --scope local` with `shell_code_exec` on `autopilot` (his personal override).

The translator emits **narrow rules** per category. The three settings.json files each contain a different set of rules. At runtime, Claude Code **merges** all three sets into a single in-memory pool and resolves per-call as deny > ask > allow.

**Worked examples — what the merged pool does to each pattern.**

| Pattern | User layer says | Project layer says | Local layer says | Merged set contains | Effective behavior | Why |
|---|---|---|---|---|---|---|
| `Bash(git push:*)` | `allow` (mostly-allow → allow) | `ask` (always-ask → ask) | (not emitted) | {ask, allow} | **ask** | ask > allow in merged set |
| `Bash(python:*)` | `allow` (mostly-allow → allow) | (not emitted) | `allow` (autopilot → allow) | {allow, allow} | **allow** | only allow rules → allow |
| `Bash(rm -rf:*)` | `deny` (security_deny baseline) | `deny` (security_deny baseline) | `deny` (security_deny baseline) | {deny} | **deny** | deny is absolute |
| `Bash(curl \| sh)` | `deny` (security_deny) | (not emitted in this hypothetical) | (not emitted) | {deny} | **deny** | a single-layer deny still wins |
| `WebFetch(domain:internal.acme.com)` | (not emitted) | `allow` (team trust) | (not emitted) | {allow} | **allow** | only one rule → allow |

**The non-obvious findings.**

1. **A user-layer `allow` does NOT loosen a project-layer `ask`.** Matt cannot autopilot a pattern the team has set to ask. He can only restrict further (add ask, add deny). This is **correct behavior** for multi-developer teams — the team's project file is a *permission floor*, not a default that personal layers override.

2. **A local-layer `allow` does NOT loosen a project-layer `ask` either.** "Local overrides project" is true for *non-permission* settings (theme, model selection, custom hooks). It is **false** for permission rules. Anyone who's seen non-permission overrides work and assumed permissions follow the same pattern will be surprised.

3. **The `ask` bucket is sticky upward.** Once any layer puts a pattern in `ask`, no other layer can move it to `allow`. The only way to "downgrade" an ask is to remove the rule from the layer that emits it — which for a project-layer ask means editing `.claude/settings.json` (a committed file) at the source, not adding a counter-rule at user/local.

4. **The `deny` bucket is absolute.** A team-policy deny in the project file *cannot* be relaxed by an individual user. This is also correct, and is the lever for shared safety floors (deny `npm publish`, deny `git push --force:*`, deny `.env` reads).

5. **Adding a rule at user-scope is "additive only."** The user-layer can:
   - Add `deny` rules that don't exist elsewhere → tightens.
   - Add `ask` rules for patterns no other layer mentions → tightens for those patterns.
   - Add `allow` rules for patterns no other layer mentions → loosens (but only for unclaimed patterns).
   - It **cannot** weaken a stricter rule from a higher-merge layer.

6. **The "same pattern in two layers with different buckets" case is now well-defined.** Under v0.17.0's "overwrite, not merge" the engine never saw the same pattern in two buckets within one file. Under Phase A, the same pattern *can* appear in different buckets at different layers — and that's fine, because the merge resolves cleanly via deny > ask > allow.

**Implications for the EMISSIONS strategy.**

The v1 trap discussion warned about "dead-weight rules" if a user-layer rule conflicts with a project-layer rule. Under the correct merge model:

- A user-layer `allow Bash(git push:*)` + project-layer `ask Bash(git push:*)` → both rules merge, ask wins. The user-layer rule is **not** dead weight in a semantic sense (it still represents the user's preference, and if the project rule ever disappears the user rule becomes effective). It is, however, **non-load-bearing** for the current effective behavior. We accept this — no optimization needed.
- A user-layer `deny Bash(rm -rf:*)` + project-layer `deny Bash(rm -rf:*)` → both rules merge, deny wins (twice, harmlessly). This is the security_deny baseline behavior; we want it at all layers as defense-in-depth, even if redundant.
- A user-layer `ask Bash(python:*)` + project-layer `allow Bash(python:*)` → both rules merge, ask wins (user has tightened the team's default). Working as intended.

**The script needs no precedence-skipping logic.** Each scope emits its full rule set; the engine merges. This is much simpler than the v1 draft's "skip already-emitted patterns at higher-precedence layers" suggestion, which was based on the wrong precedence model.

**The script DOES need a "merge preview" diagnostic.** Because the merge happens at engine runtime, a user editing the YAML and applying at one scope cannot see *the effective merged state* by looking at the file they just wrote — they'd need to read all three layers and merge mentally. Phase B.4.4 (Health tab) does this read-side merge and surfaces the effective set; for the CLI path, `apply-comfort-posture.py --preview-merge` reads all three settings.json files, computes the merged set, and prints it. Recommended for v0.18.0 (Phase A's release).

#### 2.3.4 The new Phase A recommendation, given the merge model

The v1 draft recommended `--scope user` as the new default because "personal traits should not pollute the project file." That recommendation **stands** but the rationale shifts:

- **Old rationale (v1):** "Personal posture in the project file is a footgun because PR reviewers with different postures will revert it."
- **New rationale (v2, given merge semantics):** "The project file is a *permission floor* the whole team operates under. Personal preferences should NOT be in the floor because the floor cannot be relaxed by individuals — it can only be tightened. Put personal preferences at `--scope user` (or `--scope local` for project-specific personal tuning); reserve `--scope project` for genuine team policy (shared denies, shared asks the team has agreed on)."

The corollary: **`/set-posture --scope project` is for the rare case** where the team has explicitly agreed on a permission rule. The dashboard's scope selector should make this less prominent (smaller button, separate confirmation modal, "Are you sure this is a team policy?" prompt) — see §2.3.5.

#### 2.3.5 Dashboard UI — scope selector (revised for merge model)

The v1 scope selector was a 3-way radio (User / Project / Local) with User as default. Given the merge findings, we revise:

```
   Apply posture to:                                    ⓘ What does this mean?

   [● User (default)]  for me, all my projects on this machine
   [○ Local]           for me, just this project
   [○ Project] *team*  for the team — this is a permission FLOOR everyone is bound by
                       Requires explicit confirmation. Use sparingly.
```

The Project option gets:
- A distinct visual treatment (smaller, separate row, "*team*" tag, warning copy).
- A confirmation modal on submit: *"Project-scope rules are merged into every team member's effective permissions and cannot be relaxed by their personal layers. Use this only for shared policy (denies + asks the team has agreed on). For personal preferences, use User or Local."*
- The modal lists the patterns that *would* be emitted and flags any that are `allow` — `allow` at project scope is usually wrong (it loosens defaults for the team, which is rarely intended). If the YAML's `allow` emission count is >0, the modal warns: *"You're about to emit N `allow` rules at project scope. The team will be granted these allows. Is this intentional?"*

**Wording rationale.** The phrase "permission floor" is intentionally evocative — it conveys (a) all team members stand on it; (b) you can build up from it but not down through it; (c) it's load-bearing. The "what does this mean?" info modal carries the §1.4 + §2.3.3 explanation in plain language.

#### 2.3.6 Reading the right file back into the dashboard (unchanged from v1, with merge note)

#### 2.3.6 Reading the right file back into the dashboard

When the dashboard loads, today it has nothing to load from — the YAML doesn't exist yet, and the dashboard initializes from defaults. After Phase A, the user might have a different posture at each scope. How should the dashboard initialize?

**Recommendation:** The YAML file `.ravenclaude/comfort-posture.yaml` is still **one file**. It represents the **posture the user wants applied** in the current session, regardless of scope. The scope selector is a per-apply choice, not a per-file partition. If Matt wants different postures at different scopes, he edits the YAML, picks `--scope user`, applies; then edits the YAML, picks `--scope local`, applies. The YAML is the working draft; the three settings.json files are the emissions.

**The merge-model nuance.** Because the engine merges across layers, "what the YAML looks like" at a given scope no longer fully describes "what the user actually experiences." Two users with identical YAML at user scope but different YAML at project scope will experience different effective postures. The dashboard's Settings tab today shows *the working draft of the YAML*; the **effective merged posture** is a separate concept that lives in the Health tab (B.4.4) as a read-only diagnostic and as `apply-comfort-posture.py --preview-merge` on the CLI.

If we wanted to support **"see my user-layer posture, see my local-layer posture, see my project-layer posture"** in the dashboard simultaneously, we'd need three YAML files (`comfort-posture.user.yaml`, `.project.yaml`, `.local.yaml`) and a tab/section that shows all three. This is **deferred to v2 of Phase A** as "Multi-posture authoring" — explicitly out of scope for the first cut because the additional UI complexity buys little for the solo-developer case AND the merge model makes the "effective view" the more important question.

For v1, the dashboard shows one posture; the user picks a scope at apply time; the YAML reflects the posture they last edited regardless of scope. The Health tab (when it ships) is the place to see the merged effective posture.

#### 2.3.7 Migration — existing v0.17.0 users

Today's users have `.claude/settings.json` with permissions filled by `/set-posture --scope project` (the only mode that exists). After Phase A ships:

1. On first `/set-posture` invocation, the script **detects** the legacy state (`.claude/settings.json` has `permissions.allow/ask/deny` filled, no `.comfort-posture-applied.json` side-car, no explicit `--scope` flag given) and prints:

   ```
   ⚠ Detected legacy state: posture applied at project layer (the previous default).
     The new default is --scope user (your machine, all projects).

     Choose one:
       1. Migrate now to user scope     (recommended for personal use)
       2. Keep at project scope         (team-shared / committed; appropriate if this is a team policy)
       3. Apply at both                  (project file becomes a hard floor; user adds permissive defaults)

     Re-run with --scope {user|project|both} to confirm. No changes made yet.
   ```

2. The user picks. If `1`, the script writes the user file + **clears** the project file's `permissions.{allow,ask,deny}` blocks (with a confirmation prompt) so the migration is clean.
3. The dashboard surfaces the same migration prompt as a one-time banner on first load post-upgrade.

**Backward-compat hatch:** an env var `RAVENCLAUDE_POSTURE_LEGACY_SCOPE=project` makes the script default to project scope (the v0.17.0 behavior). Documented but not advertised. Removed in the version after the version after this one.

**Migration copy needs updating for the merge model.** The v1 banner copy implies the user could swap project → user and still get the same behavior. Under merge semantics, the *effective* behavior is identical only if `user-scope rules ⊇ project-scope rules`. The corrected banner copy:

```
⚠ Detected legacy state: posture is applied at PROJECT scope (the previous default).

Under Claude Code's merge model, anything in the project file is a permission
FLOOR — visible and binding for every team member who clones this repo. Personal
preferences should not live there.

Choose one:
  1. Migrate now to USER scope     (recommended for personal use)
     → moves your current posture from .claude/settings.json
       to ~/.claude/settings.json. The project file is cleared.

  2. Keep at PROJECT scope         (this is a team policy)
     → only choose this if everyone on the team needs these rules to apply.
       The dashboard's Project-scope confirmation modal will warn on every save.

  3. Apply at BOTH                 (advanced)
     → keep the project file as a team-shared floor (denies + asks only,
       no allows); duplicate the same posture at user scope for solo
       sessions. Allows in the project file will be flagged by the
       Project-scope confirmation modal.

Re-run with --scope {user|project|both} to confirm. No changes made yet.
```

### 2.3.8 Concrete YAML and settings.json — what the emissions look like

To ground the abstract design in a concrete artifact, here's the same posture YAML emitting different settings.json shapes per scope:

**Source YAML** (`.ravenclaude/comfort-posture.yaml`, single working draft):

```yaml
# Personal comfort posture for this machine
global_default: mostly-allow

categories:
  shell_remote_mutate:   always-ask    # team's shared rule (git push, etc.)
  shell_code_exec:       mostly-allow  # python, node, dotnet
  shell_local_mutate:    mostly-allow  # rm, mv (NOT rm -rf — security_deny floor)
  filesystem_dotfiles:   always-ask
  network_outbound:      always-ask
  # … remaining 7 categories on global_default …

per_pattern_overrides:
  "Bash(npm publish:*)": deny    # never, even with --scope project
  "Bash(git push --force:*)": deny

security_deny:
  - "Bash(rm -rf /*)"
  - "Bash(rm -rf ~)"
  - "Read(**/.env)"
  - "Bash(curl * | sh)"
  - "Bash(git push --force:*)"
```

**Emission at `--scope user`** (`~/.claude/settings.json`):

```json
{
  "$schema": "https://docs.anthropic.com/.../claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(python:*)",
      "Bash(node:*)",
      "Bash(npm test:*)",
      "Bash(npm run:*)",
      "Bash(dotnet build:*)",
      "Read(/**)"
    ],
    "ask": [
      "Bash(git push:*)",
      "Bash(git checkout:*)",
      "Read(**/.env*)",
      "Read(**/secrets/**)",
      "Bash(curl:*)",
      "Bash(wget:*)",
      "WebFetch(domain:*)"
    ],
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(rm -rf ~)",
      "Read(**/.env)",
      "Bash(curl * | sh)",
      "Bash(git push --force:*)",
      "Bash(npm publish:*)"
    ]
  }
}
```

**Emission at `--scope project`** (`.claude/settings.json`) — IF the user picked Project scope through the confirmation modal:

```json
{
  "$schema": "https://docs.anthropic.com/.../claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(python:*)",
      "Bash(node:*)",
      "Bash(npm test:*)",
      "Bash(npm run:*)",
      "Bash(dotnet build:*)",
      "Read(/**)"
    ],
    "ask": [
      "Bash(git push:*)",
      "Bash(git checkout:*)",
      "Read(**/.env*)",
      "Read(**/secrets/**)",
      "Bash(curl:*)",
      "Bash(wget:*)",
      "WebFetch(domain:*)"
    ],
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(rm -rf ~)",
      "Read(**/.env)",
      "Bash(curl * | sh)",
      "Bash(git push --force:*)",
      "Bash(npm publish:*)"
    ]
  }
}
```

**Note the danger:** the Project emission is identical to the User emission. If the user emits at Project scope without thinking, the team gets all 9 of Matt's personal `allow` rules **as a team-wide floor** that personal layers cannot relax. This is exactly the foot-gun R12 names. The Project-scope confirmation modal (§2.3.5) counts the 9 `allow` entries and surfaces them prominently: *"You're about to grant the whole team these 9 allows. Are these team-policy decisions or personal preferences?"*

**Recommended Project emission** (if the user genuinely wants team-shared posture) — denies and asks only, no allows:

```json
{
  "$schema": "https://docs.anthropic.com/.../claude-code-settings.json",
  "permissions": {
    "ask": [
      "Bash(git push:*)",
      "Read(**/.env*)",
      "Read(**/secrets/**)"
    ],
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(rm -rf ~)",
      "Read(**/.env)",
      "Bash(curl * | sh)",
      "Bash(git push --force:*)",
      "Bash(npm publish:*)"
    ]
  }
}
```

The future `--scope project` mode should default to this "floor only" emission shape and require an explicit `--include-allows` flag to emit allow rules at project scope. Open question for follow-up implementation: should the YAML grow a `team_policy_only: true` flag that emits only the relevant subset at project scope?

**Emission at `--scope local`** (`.claude/settings.local.json`) — typically a sparse delta on top of project:

```json
{
  "permissions": {
    "deny": [
      "Bash(git commit:*)"
    ]
  }
}
```

Example use case: a developer who's in the middle of a refactor and wants to be sure they don't accidentally commit before review. They add a one-line local-scope deny; it merges with the project floor; effective behavior is "everything project says, plus no commits." When the refactor lands they remove the rule.

### 2.3.9 Concrete code sketch — `apply-comfort-posture.py --scope`

Implementer-facing reference. The diff against today's v0.17.0 script. Today the script always writes `project_root / ".claude" / "settings.json"`; the patch teaches it to resolve the path per scope.

```python
# At the top of the file, near the other constants:
LEGACY_SCOPE_ENV = "RAVENCLAUDE_POSTURE_LEGACY_SCOPE"
SIDE_CAR_FILENAME = ".comfort-posture-applied.json"
MIGRATION_ACK_PATH = Path.home() / ".claude" / "ravenclaude-state" / "posture-migration-acknowledged"


def resolve_settings_path(scope: str, project_root: Path) -> Path:
    """Return the absolute path of the settings.json file to write at this scope."""
    if scope == "user":
        return Path.home() / ".claude" / "settings.json"
    if scope == "project":
        return project_root / ".claude" / "settings.json"
    if scope == "local":
        return project_root / ".claude" / "settings.local.json"
    raise ValueError(f"unknown scope: {scope!r}")


def resolve_side_car_path(scope: str, project_root: Path) -> Path:
    """Side-car file recording last-apply timestamp + script version per scope."""
    if scope == "user":
        return Path.home() / ".claude" / SIDE_CAR_FILENAME
    # project + local share the project dir; the filename embeds the scope
    return project_root / ".claude" / f"{SIDE_CAR_FILENAME[:-5]}.{scope}.json"


def detect_no_project_root(start: Path) -> bool:
    p = start.resolve()
    while p != p.parent:
        if (p / ".claude").is_dir() or (p / ".git").is_dir():
            return False
        p = p.parent
    return True


def check_ephemeral_env() -> str | None:
    """Return a warning string if we're in an environment where user-scope is ephemeral."""
    if os.environ.get("CODESPACE_NAME"):
        return ("you're in a GitHub Codespace; --scope user writes to an ephemeral home "
                "that vanishes on Codespace rebuild. Use --scope local if you want the "
                "rules to persist in the project.")
    if os.environ.get("CI") in ("1", "true"):
        return ("you're in a CI environment; --scope user writes to an ephemeral home "
                "that the next job will not see. This may be intentional (one-off CI) "
                "or a mistake (you wanted --scope project).")
    return None


def fire_migration_banner_if_needed(scope: str, project_root: Path) -> bool:
    """Detect legacy v0.17.0 state and offer to migrate. Returns True if banner fired."""
    if MIGRATION_ACK_PATH.exists():
        return False  # already acknowledged
    legacy = project_root / ".claude" / "settings.json"
    if not legacy.is_file():
        return False
    try:
        data = json.loads(legacy.read_text())
        perms = data.get("permissions", {})
        if not (perms.get("allow") or perms.get("ask") or perms.get("deny")):
            return False  # nothing to migrate
    except (json.JSONDecodeError, OSError):
        return False
    print("WARN: Detected legacy state — posture is applied at project layer "
          "(the v0.17.0 default).", file=sys.stderr)
    print("      The new default is --scope user (your machine, all projects).", file=sys.stderr)
    print("      Choose one:", file=sys.stderr)
    print("        1. Migrate now to user scope     (recommended for personal use)", file=sys.stderr)
    print("        2. Keep at project scope         (team-shared / committed)", file=sys.stderr)
    print("        3. Apply at both                  (project becomes hard floor)", file=sys.stderr)
    print("      Re-run with --scope {user|project|both} to confirm.", file=sys.stderr)
    print("      No changes made yet.", file=sys.stderr)
    return True


def maybe_append_to_gitignore(project_root: Path, scope: str) -> None:
    """Append .claude/settings.local.json to .gitignore if missing. Only fires for --scope local."""
    if scope != "local":
        return
    gi = project_root / ".gitignore"
    line = ".claude/settings.local.json"
    if gi.exists() and line in gi.read_text():
        return
    with gi.open("a", encoding="utf-8") as f:
        if gi.stat().st_size > 0 and not gi.read_text().endswith("\n"):
            f.write("\n")
        f.write(f"{line}\n")
    print(f"Appended {line} to {gi.relative_to(project_root)}", file=sys.stderr)


def write_side_car(side_car_path: Path, scope: str, script_version: str) -> None:
    """Record what was applied, when, by which script version."""
    side_car_path.parent.mkdir(parents=True, exist_ok=True)
    side_car_path.write_text(json.dumps({
        "$schema": "https://github.com/mcorbett51090/RavenClaude/blob/main/scripts/comfort-posture-applied-schema.json",
        "schema_version": 1,
        "scope": scope,
        "script_version": script_version,
        "applied_at": datetime.now(timezone.utc).isoformat(),
    }, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--project-root")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--scope", choices=["user", "project", "local"], default=None,
                   help="Which settings layer to write. Default: user (was 'project' in v0.17.0).")
    p.add_argument("--preview-merge", action="store_true",
                   help="Print the merged ruleset across all three layers; do not write.")
    args = p.parse_args()

    # --scope resolution:
    if args.scope is None:
        legacy = os.environ.get(LEGACY_SCOPE_ENV)
        if legacy in ("user", "project", "local"):
            args.scope = legacy
            print(f"INFO: {LEGACY_SCOPE_ENV}={legacy} → defaulting to --scope {legacy}", file=sys.stderr)
        else:
            args.scope = "user"  # the new default

    root = Path(args.project_root) if args.project_root else find_project_root(Path.cwd())

    if args.scope == "local" and detect_no_project_root(root):
        print("ERROR: --scope local requires a project root (.git/ or .claude/). "
              "Run inside a project, or use --scope user.", file=sys.stderr)
        return 2

    warning = check_ephemeral_env()
    if warning and args.scope == "user":
        print(f"WARN: {warning}", file=sys.stderr)

    # Migration banner fires only when scope is explicitly chosen and legacy state exists.
    if args.scope == "user" and fire_migration_banner_if_needed(args.scope, root):
        return 0  # banner fired; no changes; user must re-run with explicit confirmation

    settings_path = resolve_settings_path(args.scope, root)
    side_car_path = resolve_side_car_path(args.scope, root)

    # ... (existing posture-emission logic from v0.17.0, unchanged) ...
    # then:
    if not args.dry_run:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
        write_side_car(side_car_path, args.scope, SCRIPT_VERSION)
        maybe_append_to_gitignore(root, args.scope)
        MIGRATION_ACK_PATH.parent.mkdir(parents=True, exist_ok=True)
        MIGRATION_ACK_PATH.touch(exist_ok=True)

    print(f"Applied posture to {settings_path} (scope={args.scope})")
    return 0
```

The patch preserves all of v0.17.0's emission logic — it only adds the path-resolution layer, the migration banner, the side-car, the gitignore append, and the ephemeral-env warnings. Implementer effort: **~3-4 hours** to write + **~2-3 hours** of fixtures and tests per §2.5.

### 2.3.10 Concrete code sketch — scope-selector HTML in the Settings tab

The new UI row above the preset bar in the Settings tab:

```html
<div class="scope-selector" role="radiogroup"
     aria-labelledby="scope-selector-label">
  <span class="scope-label" id="scope-selector-label">Apply posture to:</span>

  <div class="scope-options">
    <label class="scope-option">
      <input type="radio" name="scope" value="user" checked
             aria-describedby="scope-user-desc">
      <span class="scope-name">User</span>
      <span class="scope-desc" id="scope-user-desc">
        this machine, all projects
      </span>
    </label>

    <label class="scope-option scope-team">
      <input type="radio" name="scope" value="project"
             aria-describedby="scope-project-desc">
      <span class="scope-name">Project</span>
      <span class="scope-tag">team</span>
      <span class="scope-desc" id="scope-project-desc">
        this project, committed
      </span>
    </label>

    <label class="scope-option">
      <input type="radio" name="scope" value="local"
             aria-describedby="scope-local-desc">
      <span class="scope-name">Local</span>
      <span class="scope-desc" id="scope-local-desc">
        this project, just me (gitignored)
      </span>
    </label>
  </div>

  <button type="button" class="info-btn" id="scope-info-btn"
          aria-label="What's the difference between scopes?">ⓘ</button>
</div>

<!-- Confirmation modal for Project scope; hidden until project radio clicked -->
<div class="modal-backdrop" id="project-scope-modal"
     role="dialog" aria-modal="true"
     aria-labelledby="project-scope-modal-title" hidden>
  <div class="modal">
    <h2 id="project-scope-modal-title">
      ⚠ You're about to apply posture at the Project scope
    </h2>
    <p class="modal-body">
      Project-scope rules are <strong>merged into every team member's effective
      permissions</strong> and cannot be relaxed by their personal layers.
      Use this only for shared safety policy.
    </p>
    <p class="modal-body">
      <strong>Recommendation:</strong> at Project scope, keep <code>allow</code>
      rules to a minimum. Most teams want <code>deny</code> + <code>ask</code>
      at this layer only, with <code>allow</code> rules living at User scope.
    </p>
    <details>
      <summary>Your current posture would emit <strong id="project-allow-count">N</strong>
              allow rules at project scope</summary>
      <ul id="project-allow-list" class="modal-rule-list"></ul>
    </details>
    <div class="modal-actions">
      <button type="button" class="btn secondary" id="project-cancel">
        Cancel (revert to User)
      </button>
      <button type="button" class="btn primary" id="project-confirm">
        I understand — apply at Project
      </button>
    </div>
  </div>
</div>
```

The CSS reuses the existing `.modal-backdrop`, `.modal`, `.info-btn` classes already in `dashboard.html`. New classes (`.scope-selector`, `.scope-option`, `.scope-name`, etc.) follow the same naming convention as `.preset-bar` and `.cat-row` so the visual integration is seamless.

The radio group implements the WAI-ARIA APG radio pattern: Tab moves between radio groups (settings UI vs main app), Arrow keys move within the scope radios, Space selects. The `scope-team` modifier on the Project option gets the "team" tag styling (smaller, muted, with a 🌐 icon to signal "shared").

The confirmation modal fires **only** when the user selects Project and the current posture YAML has at least one `allow` rule that would be emitted. If the user's posture is already deny+ask-only, the modal is suppressed (no foot-gun, no friction).

### 2.4 Edge cases & gotchas

| Case | What happens | Mitigation |
|---|---|---|
| User runs `--scope local` with no project root (CWD is `~/`) | `Path("./").resolve() / ".claude" / "settings.local.json"` → falls in `~`. Confusing. | Detect: if `--scope local` and no `.git/` or `.claude/` found upward, refuse with "no project root detected; did you mean `--scope user`?" |
| User has Enterprise managed-settings.json that already denies a category | Posture writes are wasted; engine ignores them anyway. | Read enterprise file at script start; emit warning if any emitted pattern is denied at higher layer. (Read-only; no merge.) |
| Same project, two checkouts (worktrees) | `.claude/settings.json` is per-worktree (different files); `.claude/settings.local.json` is per-worktree; `~/.claude/settings.json` is shared. Surprising for power users. | Document. Worktrees inherit the user layer; project + local are per-worktree by design. |
| User has plugin-marketplace-update-staged migrations | The Phase A migration banner fires once per machine, not per project. | Side-car file at `~/.claude/ravenclaude-state/posture-migration-acknowledged` — touch on first ack. |
| The `~/.claude/settings.json` doesn't exist yet | Script creates it with `{"$schema": ".../claude-code-settings.json", "permissions": {...}}`. | Same logic as today's project-scope path, just retargeted. |
| User runs the dashboard from a Codespace where `~/` is ephemeral | `--scope user` writes to the Codespace home, vanishes on rebuild. | Codespace detection (`CODESPACE_NAME` env var); offer `--scope local` instead. Banner: "you're in a Codespace; user-scope settings vanish on rebuild. Use local scope instead?" |

### 2.5 Tests that have to pass

1. `apply-comfort-posture.py --scope user --dry-run` — writes diff to stdout against `~/.claude/settings.json`. No file modified.
2. `apply-comfort-posture.py --scope project --dry-run` — unchanged behavior from v0.17.0.
3. `apply-comfort-posture.py --scope local --dry-run` — writes diff against `.claude/settings.local.json`. No file modified.
4. `apply-comfort-posture.py --scope local` with no project root → exit 2 with "no project root detected."
5. `apply-comfort-posture.py --scope user` with `RAVENCLAUDE_POSTURE_LEGACY_SCOPE=project` set → behaves as `--scope project`.
6. Round-trip: dashboard radio "Project" → YAML written → script invoked with `--scope project` → project settings.json updated; user settings.json untouched.
7. Migration banner: state where `.claude/settings.json` has filled permissions and no acknowledgement side-car → banner fires once; sets side-car; doesn't fire on re-run.
8. Worktree behavior: same plugin, two worktrees, run `--scope local` in each. Each worktree has its own `.claude/settings.local.json`. The user `~/.claude/settings.json` is shared and untouched.

### 2.6 Effort estimate

- Script changes (`--scope` flag, path resolution, migration banner, side-car ack file): **3-4 hours**.
- Dashboard UI changes (scope selector + info modal + localStorage persistence): **2-3 hours**.
- `/set-posture` slash command updates (pass through `--scope` from arg or prompt): **1 hour**.
- `serve-dashboards.py` allow-list expansion if we add side-car files: **30 minutes**.
- Tests + docs: **2-3 hours**.
- **Phase A total: 8-11 hours of focused work.** Comparable to the v0.17.0 ship.

---

<a id="phase-b"></a>
## 3. Phase B — dashboard build-out

### B.1 Information architecture

#### 3.1.1 Today's tabs and what we keep

Today: **Settings · Commands · Trees · Activity**. The names work and are consistent with proposal 003 §4.3. We keep them, fill in the three stubs, and propose three additions:

| Tab | Status today | Status proposed |
|---|---|---|
| **Settings** | live, posture-only | live, posture + scope selector + per-agent toggles (Phase B.4.1) |
| **Commands** | stub | live (Phase B.2) |
| **Trees** | stub | filled in (proposal 003 §4.8 — out of scope of *this* plan; honored as-is) |
| **Activity** | stub | filled in (proposal 003 §4.7 — out of scope of *this* plan; honored as-is) |
| **Install** *(NEW)* | — | live (Phase B.3) — onboarding for new users |
| **Agents** *(NEW)* | — | live (Phase B.4.1) — per-agent enable/disable + skill toggles + version pin |
| **Health** *(NEW, stretch)* | — | live (Phase B.4.4) — diagnostics + posture preview + permission-rule visualizer |

That's **7 tabs total**, which is at the upper limit of comfortable. If the tab bar starts to feel crowded we collapse Trees + Activity + Health into a "Run" group under a single tab with sub-nav. Decision deferred until Trees and Activity actually ship.

#### 3.1.2 Header & global controls (proposed additions)

The header today shows:

```
RavenClaude comfort posture
[ paragraph describing the dashboard ]
ravenclaude-core · static dashboard, no backend. Edits stay in your browser until you click Download.
[ tab bar ]
```

We add:

- **Plugin switcher** (top-right corner): dropdown listing the 7 plugins. Selecting one navigates to that plugin's dashboard.html. (Today each plugin has its own dashboard; the switcher saves the user from finding the right file:// URL.)
- **Scope indicator** (top-right corner, next to plugin switcher): shows the current scope target ("Apply to: User") so the user knows what they're editing without scrolling.
- **Save indicator** (top-right corner, near "Connect to file…"): "Auto-saved 14:23" / "Unsaved changes" — already there in the Settings tab but should be global.
- **Theme toggle** (top-right corner): system / light / dark — already respected via `prefers-color-scheme` but not user-overridable. Low priority; add if hot-keys land.

### B.2 Slash-commands tab

This is the headline new tab. The user wants to **click a command to "launch" it**.

> **CRITICAL design constraint, stated honestly up front:** A browser dashboard cannot directly invoke a slash command in a running Claude Code session. There is no live IPC bridge from the page to the terminal/IDE — the dashboard is a static HTML file with no privileged access to the running CLI. "Launch" therefore means one of three things:
>
> 1. **Copy** the slash command to clipboard (always works, requires user paste).
> 2. **Show** the slash command in a copyable code block (no clipboard interaction needed; user reads + retypes).
> 3. **Deep link** via `claude-cli://open?q=<url-encoded-slash-command>` (Claude Code v2.1.91+, pre-fills the prompt box but **does not execute** — user still has to press Enter; per the deep-links docs, "populated but not executed"). Silently degrades to Copy on machines without the scheme handler registered.
>
> Approach #3 is the closest thing to "launch" that exists. We use it where available; we always offer #1 as the fallback.

#### B.2.1 Three UI design alternatives

I present three meaningfully different designs, then recommend. Each design assumes the launch-click behavior is the deep-link-or-clipboard combo above; the variation is in **layout and discovery**.

##### Design 1 — **Card grid with hover-tooltip showing the full command** (Matt's suggestion, refined)

A responsive grid of command cards (3 columns at desktop width, 1 column at mobile). Each card:

```
┌────────────────────────────────────────┐
│  /init-agent-ready                     │
│  Set up AGENTS.md + CLAUDE.md +        │
│  .repo-layout.json + optional CI       │
│                                        │
│  [Launch] [Copy] [Show]                │
└────────────────────────────────────────┘
```

**Hover (or focus) reveals the full command preview** in a tooltip:

```
─── /init-agent-ready ─────────────────────────────────
Asks 3 questions, then writes:
  • AGENTS.md  (cross-tool agent instructions, ~80 lines)
  • CLAUDE.md  (Claude-Code-specific addendum, ~30 lines)
  • .repo-layout.json (allow-list of file path globs)
  • .github/workflows/validate-layout.yml (optional CI)

You can pre-set args:
  /init-agent-ready repo-type=plugin-marketplace
  /init-agent-ready ci=yes hygiene=yes
───────────────────────────────────────────────────────
```

**Pros.**
- Familiar pattern. Tile/card UIs are immediately legible — you scan, find, click.
- The hover tooltip surfaces the **full** command + the args, which is what Matt asked for ("buttons-with-tooltips that show the full command").
- Filterable by plugin in a top toolbar (`All · ravenclaude-core · power-platform · finance · …`).
- Mobile-friendly via the responsive grid.
- Easy to extend with **category chips** ("setup · authoring · review · reporting · partner-success") for cross-cutting filtering.

**Cons.**
- Hover tooltips are not keyboard-accessible by default — needs explicit focus handling.
- 55 agents × ~5-7 commands each ≈ **275-385 cards.** Even at 3 cards per row, that's ~100 rows of scrolling. Needs aggressive filtering and a default "show only the most-used 20" view.
- Hover is invisible on touch. Mobile users won't discover the tooltip; the [Show] button per card is the touch path.

**Mockup sketch (described):** top toolbar with plugin filter chips + search box; below, a responsive `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))` of cards; each card has a 14-pt monospace command name, 13-pt muted description (2 lines max), and three small buttons at the bottom (Launch, Copy, Show).

##### Design 2 — **Command palette (searchable list, keyboard-first)**

A single `⌘K`-style command palette is the primary surface. Default view shows a list of commands ranked by usage; the input field at top accepts substring matches against command name, description, and tags. Selecting a row shows the **full command + args** in an inline detail pane below the list (or in a side pane on wide screens).

```
┌─ Search commands ───────────────────────────────────┐
│  [ /set                                          🔍 ]│
└─────────────────────────────────────────────────────┘

  /set-posture            apply comfort-posture.yaml…
  /set-posture --scope ?  pick scope (user/project/…)
  /set-env                edit environment-context.md
                                                       
  ─── Below the search results ──────────────────────
  /set-posture
  Translate .ravenclaude/comfort-posture.yaml into
  .claude/settings.json permission rules. Reads the
  YAML; resolves levels (per-pattern override > cat
  default > global_default); overwrites the target
  settings file's permissions.{allow,ask,deny}.

  Args:
    --scope {user|project|local}   target settings layer
    --dry-run                      print diff, no write

  [Launch /set-posture]  [Copy]  [Open in Claude Code]
```

**Pros.**
- Best for power users who know what they want — fastest path to launch.
- Substring search across name + description scales gracefully to all 275-385 commands.
- Keyboard-only flow is excellent (Arrow keys to navigate; Enter to launch).
- Detail pane in the same view = no modal flicker.
- Composable with the deep-link mechanic — Enter triggers `claude-cli://open?q=...` directly.

**Cons.**
- Less *discoverable* than the card grid — a new user doesn't see what's available without typing.
- The blank-state UX is critical: showing nothing on page load is hostile to first-time users. Mitigate with a "Popular commands" default list and a "Browse by plugin" link.
- Less attractive visually; harder to add per-command screenshots, status badges, etc.

**Mockup sketch (described):** centered search input (full-width on mobile, 600px on desktop); list of `<button>` rows under it, each a single line with command + 1-line description; below the search results, a 2-pane preview (left: full description; right: launch buttons).

##### Design 3 — **Accordion grouped by category, each command a click-to-expand row**

```
▾ Setup (3 commands)
   /init-agent-ready              setup agent-readable boundary files
   /install-marketplace           install RavenClaude + its plugins
   /upgrade-plugins               run /plugin marketplace update

▸ Authoring (12 commands)
▸ Review (8 commands)
▸ Reporting (7 commands)
▾ Partner success (5 commands)
   /draft-qbr                     compose a QBR deck from a partner profile
   ─── click ───────────────────────────────────────
   ┌─────────────────────────────────────────────────┐
   │  /draft-qbr                                     │
   │  Compose a quarterly business review deck …    │
   │  [Launch] [Copy] [Show]                         │
   │  Owner: edtech-partner-success / qbr-composer   │
   └─────────────────────────────────────────────────┘
   /draft-health-score
   /partner-touchpoint-log
   /escalate-renewal-risk
   /update-success-plan
```

**Pros.**
- Excellent for **discoverability** — categories are visible at a glance; expanding one section doesn't lose context of others.
- Natural fit for the "I want to do X" mental model where the user doesn't know the command name yet.
- Section counts surface in the header (e.g., "Setup (3)") so the user knows breadth before clicking.
- Easy to add new top-level categories.

**Cons.**
- Slower to reach a known command than the palette or the card grid.
- The two-level expand-then-expand pattern (category → command → detail) is one click more than necessary; flattening "click row to expand" with the detail inline mitigates this.
- Visually less dense than the card grid; uses more vertical space per command.

**Mockup sketch (described):** standard accordion: `<details>` per category; clicking the summary expands; each command is a row inside; clicking a row expands its detail (Launch/Copy/Show buttons + description + owner).

##### Design 4 (bonus alternative) — **"Command builder" with arg-form composer**

Most commands accept args. `/init-agent-ready repo-type=plugin-marketplace ci=yes hygiene=yes` is the canonical example. A builder UI lets the user **fill in arg fields** via dropdowns / checkboxes / text inputs, then watches the assembled command update live below.

```
[ Select command:  /init-agent-ready                     ▾ ]

  repo-type:    ( application | library | monorepo | plugin-marketplace ▾ )
  ci:           ( ●yes  ○no )
  hygiene:      ( ●yes  ○no )
  overwrite:    ( skip | overwrite | merge ▾ )

Assembled command:
   /init-agent-ready repo-type=plugin-marketplace ci=yes hygiene=yes overwrite=skip

[Launch this command]  [Copy]  [Open in Claude Code]
```

**Pros.**
- Removes memorization of arg names — discoverable via the form.
- Validates inputs at compose time (no chance of typo'd arg).
- Surfaces command-specific options the user wouldn't have known existed.

**Cons.**
- Requires each command to declare its **arg schema** (today none do).
- Investment cost up front: 55 commands × manual arg-schema authoring = real work. Phase 4 territory.
- Less useful for arg-less commands (`/wrap` has none).
- Overlaps with the in-Claude-Code experience: most commands are designed to interrogate the user once invoked.

**Mockup sketch (described):** a single command-name dropdown at top; below it, a dynamically-rendered form with one row per arg (uses the same form-rendering code as the Settings tab's category rows); at the bottom, a live-updating monospace preview of the assembled command + Launch/Copy/Open buttons.

#### B.2.2 Comparison matrix — head-to-head decision rubric

Five attributes matter for the Commands tab: **discoverability** (can a new user find a command they don't already know exists?), **speed-to-launch** (how many clicks/keystrokes from intent to deep-link?), **scale** (does it stay usable at 95+ commands?), **a11y** (keyboard + screen-reader + touch), and **build cost** (engineering hours to ship).

| Design | Discoverability | Speed-to-launch | Scale to 95+ | a11y | Build cost | Best for |
|---|---|---|---|---|---|---|
| **1. Card grid** | ★★★★☆ | ★★★☆☆ (~3 clicks) | ★★★☆☆ (needs default-20 filter) | ★★★☆☆ (hover→focus retrofit) | ★★★☆☆ (6-10h) | First-time users; visual browsers |
| **2. Command palette** | ★★☆☆☆ (blank-state hostile) | ★★★★★ (1 key + type + Enter) | ★★★★★ | ★★★★★ (keyboard-native) | ★★☆☆☆ (4-6h, no per-card design) | Power users who know command names |
| **3. Accordion by category** | ★★★★☆ | ★★☆☆☆ (3-4 clicks) | ★★★☆☆ (vertical sprawl) | ★★★★☆ (`<details>`-native) | ★★★★☆ (3-5h, browser-primitive) | Mental-model "I want to do X" browsing |
| **4. Command builder** | ★★★☆☆ | ★★★★☆ (1 click + form + Enter) | ★★★★☆ (1 dropdown, scaling) | ★★★★☆ | ★★☆☆☆ (8-12h + per-cmd schema work) | Arg-heavy commands; deliberate composition |

**Cumulative score (5 = strongest):**

| Design | Discoverability | Speed | Scale | a11y | Cost | Σ (lower=cheaper, all else higher=better) |
|---|---|---|---|---|---|---|
| Card grid | 4 | 3 | 3 | 3 | 3 | **13 + 3-cost** |
| Palette | 2 | 5 | 5 | 5 | 2 | **17 + 2-cost** |
| Accordion | 4 | 2 | 3 | 4 | 4 | **13 + 4-cost** |
| Builder | 3 | 4 | 4 | 4 | 2 | **15 + 2-cost** |

**Reading the matrix:** Palette wins on raw quality but loses on first-time discoverability. Card grid is the best **first** ship because the dashboard is going to be opened by users who've never seen it before. Palette is the right **second** ship because it's a strict productivity upgrade for users who already know what they want — and it composes on top of card grid as a `⌘K` overlay rather than replacing it. Builder is the third investment, gated on commands declaring arg schemas. Accordion is dominated by card-grid-plus-category-chips (same grouping, less vertical sprawl) so we skip it.

#### B.2.3 Recommendation

> **Ship Design 1 (card grid with hover tooltip) for v0.2.0. Add Design 2 (command palette) for v0.3.0 as a `⌘K` overlay on top of Design 1.**

The card grid is the most discoverable for a user who's never seen the dashboard before. Matt explicitly asked for "buttons with tooltips showing the full command" and that is Design 1 ✓. The hover tooltip carries the full description; the Launch button does deep-link; Copy and Show are safety fallbacks. Plugin-filter chips at the top scale to all 7 plugins. The "Show only 20 most-used" default keeps page load light.

Design 2 (palette) is the **second** investment because it's a strict productivity upgrade for users who already know the command name — they don't need discovery. Wiring it as a `⌘K` overlay (or `Ctrl+K` on non-Mac) means it sits on top of Design 1 rather than replacing it; users get both surfaces.

Design 3 (accordion) is appealing for discoverability but is **dominated by Design 1 + category-filter chips** — chips give the same grouping without the vertical-real-estate cost.

Design 4 (command builder) is **deferred to v0.4.0+** and contingent on commands declaring arg schemas. We'd start by retrofitting `/init-agent-ready` and `/set-posture` (the two commands with the most args) and grow the surface organically.

#### B.2.4 Click behavior — the deep-link mechanic in detail

Per proposal 003 §9, the dashboard uses `claude-cli://` deep links. Reproduced and elaborated:

1. The "Launch" button on each card emits a URL of shape `claude-cli://open?q=<URL_ENCODED_SLASH_COMMAND>&cwd=<URL_ENCODED_PROJECT_DIR>`. The `q` value is **hard-coded** at generator time from the command's known shape (e.g., `?q=%2Finit-agent-ready` for `/init-agent-ready`). The `cwd` is derived from the dashboard's own file path (`window.location.pathname`).
2. The browser asks the OS to handle `claude-cli://`. If a handler exists (Claude Code v2.1.91+, installed and registered), Claude Code opens (or focuses an existing session in this `cwd`) and pre-fills the prompt box with the command. The user presses Enter to execute. *No auto-execution; this is by design per the deep-links spec.*
3. If no handler exists (Firefox without registration, or Claude Code < v2.1.91, or a non-CC environment), the browser shows a "no handler" dialog. To avoid that UX, the dashboard **feature-detects** the handler before rendering the Launch button:

   ```js
   // Feature-detect on page load; cache result; show Launch where supported.
   async function probeClaudeCliHandler() {
     // No JS API to query handlers — fall back to user-agent + version heuristics.
     // Better: probe once with a synthetic anchor + timeout; if no navigation occurs, assume not supported.
     // Practical: ship the Launch button; on click, race timeout against navigation.
     // If timeout wins, fall back to Copy automatically and show a one-time hint.
   }
   ```

   The fallback if the handler is absent: the click runs the Copy action instead, and a small toast appears: *"Opened in clipboard — paste in Claude Code with Cmd+V."*

4. The `q` allow-list is enforced at **generator time**, not at runtime. Each card's `<a href="claude-cli://...">` is baked into the static HTML by `generate-dashboards.py`. There is no form field or URL parameter that flows into the link. This satisfies the §9 hardening rule "Hard-coded `q` values only."

#### B.2.5 Concrete card markup — HTML/CSS sketch

Implementer-facing reference. A single command card in the recommended Design 1 layout, integrated with the existing dashboard's CSS tokens (`--accent`, `--surface`, `--border`, etc., already defined at the top of `dashboard.html`).

```html
<!-- Generator emits one of these per command, inside .command-grid wrapper -->
<article class="command-card" role="article" aria-labelledby="cmd-init-agent-ready">
  <header class="cmd-card-header">
    <h3 id="cmd-init-agent-ready" class="cmd-name">
      <span class="cmd-slash">/</span>init-agent-ready
    </h3>
    <span class="cmd-owner" title="Owner agent">
      ravenclaude-core/architect
    </span>
  </header>

  <p class="cmd-desc">
    Set up agent-readable boundary files (AGENTS.md + CLAUDE.md +
    .repo-layout.json + optional CI) tailored to this repo's purpose.
  </p>

  <details class="cmd-tooltip">
    <summary class="visually-hidden">More about this command</summary>
    <div class="cmd-tooltip-body">
      <p><strong>Args:</strong></p>
      <ul>
        <li><code>repo-type</code> — application | library | monorepo | …</li>
        <li><code>ci</code> — yes | no</li>
        <li><code>hygiene</code> — yes | no</li>
      </ul>
      <p><strong>Example invocations:</strong></p>
      <pre><code>/init-agent-ready
/init-agent-ready repo-type=plugin-marketplace ci=yes hygiene=yes</code></pre>
    </div>
  </details>

  <footer class="cmd-card-actions">
    <!-- 'launch' has the deep-link href; falls back to copy if probe fails -->
    <a class="btn primary cmd-launch"
       href="claude-cli://open?q=%2Finit-agent-ready"
       data-copy-fallback="/init-agent-ready"
       data-cmd="/init-agent-ready">
      Launch
    </a>
    <button class="btn secondary cmd-copy"
            type="button"
            data-cmd="/init-agent-ready">
      Copy
    </button>
    <button class="btn tertiary cmd-show"
            type="button"
            aria-expanded="false"
            aria-controls="cmd-show-init-agent-ready">
      Show
    </button>
  </footer>

  <!-- 'Show' expands an inline code preview; collapsed by default -->
  <pre id="cmd-show-init-agent-ready"
       class="cmd-show-preview"
       hidden><code>/init-agent-ready</code></pre>
</article>
```

```css
.command-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 16px;
}
.command-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}
.command-card:hover, .command-card:focus-within {
  border-color: var(--accent);
}
.cmd-card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
}
.cmd-name {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 600;
}
.cmd-slash { color: var(--accent); }
.cmd-owner {
  font-size: 11px;
  color: var(--muted);
  font-family: var(--font-mono);
}
.cmd-desc {
  margin: 0;
  font-size: 13px;
  color: var(--text);
  line-height: 1.45;
  /* Clamp to 3 lines; full text in the details popover */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.cmd-tooltip {
  /* Hidden by default; shown on hover/focus via JS or :hover on the card */
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 10;
  background: var(--surface-2);
  border: 1px solid var(--accent);
  border-radius: var(--radius);
  padding: 12px;
  display: none;
}
.command-card:hover .cmd-tooltip,
.command-card:focus-within .cmd-tooltip {
  display: block;
}
.cmd-card-actions {
  display: flex;
  gap: 6px;
  margin-top: auto;
}
.cmd-card-actions .btn {
  font-size: 12px;
  padding: 4px 10px;
}
.btn.primary {
  background: var(--accent);
  color: var(--bg);
  border: 1px solid var(--accent);
}
.btn.secondary {
  background: var(--surface-2);
  color: var(--text);
  border: 1px solid var(--border);
}
.btn.tertiary {
  background: transparent;
  color: var(--muted);
  border: 1px solid transparent;
}
.cmd-show-preview {
  margin: 6px 0 0;
  background: var(--surface-2);
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
}
@media (prefers-reduced-motion: no-preference) {
  .command-card { transition: border-color 80ms ease; }
}
@media (max-width: 600px) {
  .command-grid { grid-template-columns: 1fr; }
  .cmd-card-actions .btn { flex: 1; min-height: 44px; /* a11y touch target */ }
  .cmd-launch { /* On mobile, deep link probably won't work — show "Copy" only */ }
}
```

```js
/* Inline JS that wires up the card behaviors. Drops into the existing
 * <script> block in dashboard.html, near the tab-routing handlers. */

// Probe once on page load; cache result; used to decide whether
// Launch buttons act as deep links or fall back to Copy.
let HAS_DEEP_LINK = null;
async function probeClaudeCliHandler() {
  if (HAS_DEEP_LINK !== null) return HAS_DEEP_LINK;
  const cached = sessionStorage.getItem('rc-deep-link-supported');
  if (cached !== null) {
    HAS_DEEP_LINK = cached === '1';
    return HAS_DEEP_LINK;
  }
  HAS_DEEP_LINK = await new Promise(resolve => {
    let resolved = false;
    const onBlur = () => { if (!resolved) { resolved = true; resolve(true); } };
    window.addEventListener('blur', onBlur, { once: true });
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = 'claude-cli://probe';
    document.body.appendChild(iframe);
    setTimeout(() => {
      window.removeEventListener('blur', onBlur);
      if (!resolved) { resolved = true; resolve(false); }
      iframe.remove();
    }, 800);
  });
  sessionStorage.setItem('rc-deep-link-supported', HAS_DEEP_LINK ? '1' : '0');
  return HAS_DEEP_LINK;
}

// Wire up every Launch button: if probe fails, fall back to Copy.
document.addEventListener('click', async (e) => {
  const launch = e.target.closest('.cmd-launch');
  if (!launch) return;
  const supported = await probeClaudeCliHandler();
  if (!supported) {
    e.preventDefault();
    const cmd = launch.getAttribute('data-copy-fallback');
    await navigator.clipboard.writeText(cmd);
    showToast(`Copied "${cmd}" — paste in Claude Code with ${
      navigator.userAgent.includes('Mac') ? 'Cmd+V' : 'Ctrl+V'
    }`);
  }
  // else: browser handles the claude-cli:// navigation natively.
  if (typeof window.recordInvocation === 'function') {
    window.recordInvocation(launch.getAttribute('data-cmd'), 'launch');
  }
});

// Copy button — always copies, regardless of deep-link support.
document.addEventListener('click', async (e) => {
  const copy = e.target.closest('.cmd-copy');
  if (!copy) return;
  const cmd = copy.getAttribute('data-cmd');
  await navigator.clipboard.writeText(cmd);
  showToast(`Copied "${cmd}"`);
  if (typeof window.recordInvocation === 'function') {
    window.recordInvocation(cmd, 'copy');
  }
});

// Show button — expands the inline code preview.
document.addEventListener('click', (e) => {
  const show = e.target.closest('.cmd-show');
  if (!show) return;
  const targetId = show.getAttribute('aria-controls');
  const target = document.getElementById(targetId);
  if (!target) return;
  const expanded = show.getAttribute('aria-expanded') === 'true';
  show.setAttribute('aria-expanded', String(!expanded));
  target.hidden = expanded;
});
```

The above is **drop-in ready** — the existing `dashboard.html` already has `--accent`, `--bg`, `--surface`, etc. CSS variables, `.btn` button styles, focus-visible outlines, and reduced-motion handling defined; the new code respects them. The `recordInvocation()` hook is the Phase 0.21.0 telemetry entry point from §5.8.6 — calls if the hook exists, no-op otherwise.

### B.3 Startup / install area

#### B.3.1 What this tab covers

A first-time user has never opened a Claude Code session with RavenClaude installed. The Install tab walks them through:

1. **Prerequisites** — what their machine needs.
2. **Add the marketplace** — `/plugin marketplace add` command, with the exact URL.
3. **Install plugins** — `/plugin install ravenclaude-core@ravenclaude`, then any domain plugin.
4. **Verify** — run `/plugin` (or the new `/list-plugins`) to confirm install.
5. **First-session setup** — run `/init-agent-ready` and `/set-posture` to land the boundary files.

This tab is **read-only** (no settings to save). Its job is to teach.

#### B.3.2 Detailed design

The tab opens to a top hero showing the user where they are:

```
┌────────────────────────────────────────────────────────────────┐
│  Welcome.                                                       │
│  This page walks you through installing RavenClaude in your    │
│  Claude Code setup. Estimated time: 5 minutes.                  │
│                                                                 │
│  You are step  ●●○○○  of 5  →  Prerequisites                   │
│                                                                 │
│  [Detect what I have…]                                          │
└────────────────────────────────────────────────────────────────┘
```

The **"Detect what I have…"** button uses the deep-link mechanic to launch a helper command `/install-doctor` (proposed) that checks the user's machine for:

- Claude Code installed? (Y/N — fundamental)
- `gh` CLI installed? (Y/N — needed by many commands; only fatal if user wants `/wrap` to push)
- Python 3.10+ installed? (Y/N — needed by `apply-comfort-posture.py` and `generate-*.py`)
- `git` user.email and user.name set? (advisory)
- A registered handler for `claude-cli://`? (advisory; affects deep links in this dashboard)

Output of `/install-doctor` is posted back to a known file at `~/.claude/ravenclaude-state/install-doctor.json`; the dashboard polls / reads on file-handle re-grant. Or, more realistically, the user re-loads the page and the dashboard picks up the file. (No live IPC — we have to settle for "ask, then reload.")

**Step-by-step content:**

```
Step 1 — Prerequisites
──────────────────────
✓  Claude Code 2.1.148  (you have a compatible version)
✓  Python 3.12.0         (the comfort-posture translator needs ≥ 3.10)
○  gh 2.42.0             (✔ if you want /wrap to push scenarios)
○  git config user.email (suggested for commit attribution)

[Re-detect]    [Skip — I'll install missing pieces myself]


Step 2 — Add the marketplace
────────────────────────────
In any Claude Code session, run:

   /plugin marketplace add https://github.com/mcorbett51090/RavenClaude

This caches the marketplace catalog locally. Adding does not install plugins;
it just makes them discoverable.

[Launch this in Claude Code]   [Copy]   [Show]


Step 3 — Install plugins
────────────────────────
Pick the plugins relevant to your work:

[ ● ravenclaude-core ]   the foundational plugin (always recommended)
[ ○ power-platform ]     Microsoft Power Platform engagements
[ ○ finance ]            FP&A, controllership, valuation
[ ○ regulatory-compliance ]  AML/KYC, regulatory reporting, BMA Bermuda
[ ○ web-design ]         marketing site builds + WCAG/CWV/SEO
[ ○ edtech-partner-success ]   K-12 / higher-ed / corporate L&D PSM lanes
[ ○ data-platform ]      dashboard engagements (Supabase, Cube, embed)

[Launch install command]   ← assembles the right /plugin install line


Step 4 — Verify
────────────────
After installing, run /plugin in any Claude Code session and confirm the
plugins appear in the catalog. The dashboard you're reading is itself
hosted inside ravenclaude-core — if you can see this page, the install
worked.

[Open /plugin in Claude Code]


Step 5 — First-session setup
────────────────────────────
Two commands run once per project:

  /init-agent-ready    – writes AGENTS.md, CLAUDE.md, .repo-layout.json
                          and (optionally) a CI gate. Agent-readable
                          boundary files for any AI coding tool.

  /set-posture         – translates this dashboard's Settings tab into
                          .claude/settings.json permission rules.
                          Default scope: user (this machine, all projects).

[Launch /init-agent-ready]   [Launch /set-posture]

When both have run, you're done. Sessions in this project now use the
boundary files + the posture you configured.
```

#### B.3.3 Today's open Python-not-installed incident

Worth noting (Matt mentioned this in the brief): the `apply-comfort-posture.py` script requires Python 3.10+ and PyYAML (optional — graceful fallback to the built-in minimal parser if absent). The script's preamble already documents this. The Install tab's Step 1 doctor pass makes the dependency visible **before** the user hits the error. A separate detail-tooltip on the Python row could link to `python.org/downloads` and (on macOS) the recommended `brew install python@3.12` line.

Generally, **the Install tab should be the place where "what could go wrong on first run" gets surfaced proactively** — not buried in the script's stderr.

#### B.3.4 Composition with `/init-agent-ready`

`/init-agent-ready` is the single most-important first-session command. The Install tab links to it twice (Step 5 and a "Launch" button in the footer). The slash command itself already asks the user three questions and shows a Keep/Update/Deny structure. We don't duplicate that logic in the dashboard — we route the user to the command. **The dashboard is the entry-point, the slash command is the workflow.**

#### B.3.5 The chicken-and-egg problem — where does a brand-new user first see this dashboard?

The Install tab lives inside `plugins/ravenclaude-core/dashboard.html`. That HTML file is **shipped inside the plugin** — meaning the user has to install ravenclaude-core *before* they can open the dashboard. So a first-time user reading the Install tab is, by definition, **already past the install step**. The tab is currently misnamed.

There are three plausible audiences:

1. **Users who've already installed ravenclaude-core** — the tab is a verification surface, not an install surface.
2. **Users who've cloned the marketplace repo but haven't installed any plugin** — they're browsing the source.
3. **Users who've never touched RavenClaude** — they're on `repo-guide.html` or the GitHub repo readme.

For audience #1, the tab is genuinely useful as "you got this far, now run these next two commands." For audiences #2 and #3, the install instructions belong **outside** the per-plugin dashboard — specifically in `repo-guide.html` (the marketplace-level catalog) and the repo README.

**Recommended split:**

| Surface | Audience | Content |
|---|---|---|
| `README.md` at repo root | Audience #3 — never touched it | One-paragraph "what is this", a single `claude` install command, a link to repo-guide.html |
| `repo-guide.html` | Audience #2 — browsing source | Marketplace overview + a top banner "Install in 2 commands" with the marketplace-add + plugin-install lines |
| Per-plugin `dashboard.html` Install tab | Audience #1 — installed, opening dashboard | "You've got this plugin installed. Here's what to do next." — points to `/init-agent-ready`, `/set-posture`, and the other plugins they might also want |
| Per-plugin `dashboard.html` Install tab — "Add more plugins" sub-section | Audience #1 | Lets the user one-click install the other 6 plugins (deep-link to `/plugin install`) without leaving the dashboard |

The **rename** is: per-plugin dashboard's "Install" tab becomes **"Setup"** or **"Welcome"** — emphasizing "you're installed; here's what to do next" rather than "here's how to install." We keep the prerequisites check (Python, gh, etc.) under Welcome because some prereqs are only needed *after* install (e.g., gh is needed by `/wrap` to push scenarios, not by the plugin itself).

#### B.3.6 Private-marketplace access

RavenClaude's `marketplace.json` lives in a **private GitHub repository** (per the house rules in AGENTS.md, the marketplace is private by default; email field stays in until the repo goes public). Practical consequence: a new user cannot just run `/plugin marketplace add https://github.com/mcorbett51090/RavenClaude` and have it work — they need `gh auth login` or a deploy key.

The repo-guide.html and README need to call this out. Specifically:

```
Step 0 — Get access to the marketplace
──────────────────────────────────────
This marketplace is private. You need to either:

  1. Have your GitHub account added to the marketplace repo as a collaborator, OR
  2. Have a personal access token (PAT) with `repo` scope on the marketplace repo.

Verify access:
   gh auth login
   gh repo view mcorbett51090/RavenClaude    # should succeed, not 404

If this 404s, contact Matt or open an issue.
```

The dashboard's Install tab (B.3.2 Step 1, the prereqs row) gains an additional check:
- **`gh auth status` succeeds AND `gh repo view mcorbett51090/RavenClaude` succeeds → green check.**
- **Fails → red x with "you may need to be added to the marketplace repo as a collaborator."**

#### B.3.7 Failure modes — what happens when install goes wrong

The Install tab should anticipate the 3-4 most common failure modes:

| Failure | What it looks like | Tab's response |
|---|---|---|
| `/plugin marketplace add` 404s | "Not Found" error in CC | Tab Step 2 has a "Did you get a 404? You may not have access — see Step 0" link |
| User installed `ravenclaude-core@ravenclaude` but version is wrong | Plugin version mismatch in `/plugin` | Tab Step 4's verify shows "Expected ≥ 0.18.0, found 0.16.0 — run `/plugin marketplace update ravenclaude`" |
| Hooks not firing after install | Hook output never appears | Tab Step 4 has an "If hooks aren't firing" troubleshooter (re-load plugin, check `~/.claude/plugins/cache/` for cached plugin dir) |
| `apply-comfort-posture.py` fails on first run | Python error / PyYAML import error | Tab Step 1 prereq check should catch this *before* the user tries to run `/set-posture` |
| Deep-link from dashboard to CC does nothing | `claude-cli://` not registered | Tab Step 1 prereq check probes for handler; if absent, suggests Claude Code update |

These failure modes go into a collapsible "Troubleshooting" section at the bottom of the Setup tab, organized by which Step the error occurred in.

### B.4 Other panels worth adding

Beyond the four base tabs + Install, the following panels are worth designing toward. They are ordered by usefulness (highest first).

#### B.4.1 **Agents tab** — per-agent enable / disable / configure (expanded spec)

Today each plugin's `agents/` directory ships an opinionated set of specialist agents. The user can implicitly disable an agent by never invoking it, but cannot turn one **off** at the dispatch layer. Some users want narrower specialist lists; others want to tune which skills an agent is allowed to call.

##### Purpose

Answer three user questions:

1. **"What agents am I shipping?"** — every agent across every installed plugin, with one-line capabilities and frontmatter metadata (audience, works-with, scenarios, quickstart).
2. **"How do I turn one off?"** — pick an agent, disable it; the Team Lead refuses to dispatch it for the rest of the session. Re-enable later. Settings persist per scope (user / project / local) using the same scope selector as Phase A.
3. **"What is this agent allowed to do?"** — read-only view of the agent's declared model, skills, and max-context budget. Tells the user the difference between (e.g.) a `designer` that can also be told to spec components in code vs one that is text-only.

##### Data sources

| Source | Used for | Where |
|---|---|---|
| `plugins/<plugin>/agents/*.md` frontmatter | Capability metadata (description, audience, scenarios, quickstart, model, allowed_tools) | Generator-time inline; no runtime read. |
| `plugins/<plugin>/CLAUDE.md` "mandatory agents" block | List of agents the plugin marks non-disableable (e.g., `security-reviewer`) | Generator-time inline. |
| `.ravenclaude/agents.yaml` (and `.local.yaml`) | Per-agent enable/disable state | Runtime read via `/__read`; runtime write via `/__save`. New allow-list entries. |
| `~/.ravenclaude/agents.yaml` | User-scope per-agent state | Same. |

##### UI layout

```
┌─ Agents ──────────────────────────────────────────────────────────────┐
│  Apply changes to: [● User  ○ Project  ○ Local]                       │
│                                                                        │
│  Filter: [ ☐ disabled only  ☐ mandatory only ]  Search: [          🔍 ]│
│                                                                        │
│  ┌─ ravenclaude-core · 14 agents · 14 enabled ──────────────────┐    │
│  │  ▾ architect              [● enabled]  [details]  [hide in cmds] │ │
│  │     Plans implementations; produces Keep/Update/Deny structures. │ │
│  │     Audience: all  ·  Works with: code-reviewer, project-mgr    │ │
│  │                                                                    │ │
│  │  ▸ backend-coder          [● enabled]  [details]  [hide in cmds] │ │
│  │  ▸ data-engineer          [○ DISABLED] [Enable]                  │ │
│  │  ▸ security-reviewer      [● enabled]  [details]  🔒 mandatory   │ │
│  │     ↳ This plugin's CLAUDE.md marks this agent as mandatory;    │ │
│  │       cannot be disabled (would void the security review gate). │ │
│  │  …                                                                 │ │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌─ power-platform · 11 agents · 8 enabled ────────────────────┐    │
│  │  ▸ copilot-studio-engineer  [● enabled]                       │  │
│  │  ▸ dataverse-architect      [● enabled]                       │  │
│  │  ▸ flow-engineer            [○ DISABLED]                      │  │
│  │  ▸ pcf-developer            [○ DISABLED]   (no React in repo) │  │
│  │  …                                                              │  │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─ … other plugins (finance, regulatory-compliance, …) ─────┐     │
│                                                                       │
│  ┌─ Bulk actions ──────────────────────────────────────────┐        │
│  │  [Disable all in <plugin>]  [Enable all]  [Reset to defaults]│   │
│  └─────────────────────────────────────────────────────────┘        │
└───────────────────────────────────────────────────────────────────────┘
```

##### Components broken down

1. **Scope selector** (same UX as Phase A) — Apply changes at User / Project / Local. Default: User. Stored in `localStorage` per browser.
2. **Agent groups by plugin** — collapsed by default to fit 55+ agents. Each agent row shows the agent's frontmatter `description`, `audience`, and `works_with` (per the scenario-authoring schema). Two actions: toggle enabled/disabled and "hide in commands" (filters out the agent's commands in the Commands tab).
3. **Details modal** — opens on click of [details]. Shows: model declaration, allowed tool list, declared skills the agent calls, max-context budget, scenario summaries with links to the per-scenario file. Read-only in v1.
4. **Mandatory flag** — agents marked mandatory in the plugin's CLAUDE.md cannot be disabled. The toggle is greyed out; tooltip explains why. The list of mandatory agents per plugin is generator-inlined.
5. **Bulk actions** — quick disable/enable all in a plugin (useful when uninstalling a domain temporarily) and "Reset to defaults" (clears the YAML, restoring every agent to enabled).
6. **"Hide in commands"** — per-agent flag that filters that agent's commands from the Commands tab. Lighter-weight than disabling because it doesn't prevent dispatch — just hides commands the user is uninterested in (e.g., they never touch `pcf-developer`'s commands).

##### Settings file shape (`.ravenclaude/agents.yaml`)

```yaml
schema_version: 1

# Disabled agents per plugin. Absence means enabled (the default).
disabled:
  power-platform:
    - pcf-developer        # no React in repo
    - copilot-studio-engineer
  data-platform:
    - connector-developer

# Per-agent UI preferences.
hide_in_commands:
  - power-platform/pcf-developer
  - data-platform/connector-developer
```

The YAML is **additive** — only agents the user has actively touched appear. Agents in this file but no longer in the marketplace (plugin uninstalled, agent removed) are reported as "stale" with a one-click cleanup.

##### Team Lead dispatch behavior

The Team Lead reads `.ravenclaude/agents.yaml` at session-start orientation (the same pass that loads `environment-context.md`). When a dispatch target appears in the disabled list:

- **If alternative agents exist** (e.g., disabled `data-engineer`, but `architect` can plausibly cover) — Team Lead picks the next-best alternative per its decision tree.
- **If no alternative exists** — Team Lead reports back to the user: *"I would dispatch `<agent>` for this work but it is disabled in your `.ravenclaude/agents.yaml`. Re-enable, or ask me to proceed without specialist input?"*

A disabled agent is **not silently skipped** — the dispatch failure is reported so the user can revisit the decision.

##### Mandatory-agent enforcement

A plugin declares mandatory agents in its CLAUDE.md under a `## Mandatory agents` section, listing one agent slug per line. The generator parses this into the Agents tab's data inline. If a user edits `.ravenclaude/agents.yaml` manually to disable a mandatory agent, the Team Lead's session-start orientation pass:

1. Detects the conflict.
2. Emits a one-time warning: *"You've disabled `<agent>` which is marked mandatory by `<plugin>`. The Team Lead will continue to dispatch it; your disable is ignored for this agent."*
3. Strikes the entry from the YAML on next `/set-agents` (proposed companion command) run.

##### Effort estimate

- `.ravenclaude/agents.yaml` schema + Team Lead orientation-pass read: **3 hours**
- `apply-agents.py` (companion to `apply-comfort-posture.py`, same shape, writes the YAML based on dashboard input): **3 hours**
- Dashboard tab UI: **6-8 hours**
- Details modal + frontmatter inlining: **3 hours**
- Mandatory-agent enforcement + Team Lead wiring: **2 hours**
- Tests + fixtures (audit-gates.sh checks for stale agents in YAML): **2 hours**
- **Subtotal: 19-21 hours.**

Sequenced as **ravenclaude-core 0.22.0**, after Phase A + B.1/B.2 ship. The work depends on existing scenario-authoring frontmatter being filled out (it is, per the marketplace.json `0.10.0` line: "v0.10.0: every agent ships example-scenario frontmatter").

#### B.4.2 **Environment tab** — view (and re-discover) the project's environment context (expanded spec)

`.ravenclaude/environment-context.md` exists per the CGP environment-context check (CLAUDE.md, 2026-05-22). It's prose. The dashboard surfaces it read-only and offers the "re-discover" button.

##### Purpose

Answer three user questions:

1. **"What environments does this project have, per my own configuration?"** — DEV/TEST/PROD/sandbox/named environments, with the per-environment role and pre-authorized actions surfaced.
2. **"Is what's on disk current?"** — show last-updated timestamp; flag stale (>90 days per the Researcher's deep-research cadence rule).
3. **"How do I refresh it?"** — one-click deep link to `/environment-discovery` skill.

##### Data sources

| File | Role | Read mechanism |
|---|---|---|
| `.ravenclaude/environment-context.md` | Source of truth for the project's env-context posture | `/__read` (new allow-list entry) |
| Per-plugin agent frontmatter `priors` blocks that reference env-context | Cross-check: which agents in installed plugins are actually consuming the env-context file? | Generator-time inline (zero runtime read) |

##### UI layout

```
┌─ Environment ─────────────────────────────────────────────────────────┐
│                                                                        │
│  Project: power-platform-engagement                                    │
│  Source: .ravenclaude/environment-context.md                           │
│  Last updated: 2026-05-19  (4 days ago)   ⓘ updated by /environment-discovery │
│                                                                        │
│  ┌─ DEV ──────────────────────────────────────────────────────────┐ │
│  │  Role:           sysadmin (SPN-bound)                          │ │
│  │  Endpoint:       https://dev.crm.dynamics.com                   │ │
│  │  Pre-authorized: solution import/export, Web API, pac CLI       │ │
│  │  Forbidden:      production env switching                      │ │
│  │  Consumed by:    dataverse-architect, flow-engineer, solution-alm-engineer (3 agents) │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌─ TEST ─────────────────────────────────────────────────────────┐ │
│  │  Role:           system-customizer (Matt's own user)            │ │
│  │  Endpoint:       https://test.crm.dynamics.com                  │ │
│  │  Pre-authorized: solution import/export, Web API                │ │
│  │  Forbidden:      data delete; tenant DLP changes                │ │
│  │  Consumed by:    dataverse-architect, flow-engineer, …          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌─ PROD ─────────────────────────────────────────────────────────┐ │
│  │  Role:           read-only (Matt — explicit on-call list)       │ │
│  │  Endpoint:       https://prod.crm.dynamics.com                  │ │
│  │  Pre-authorized: read-only Web API; pac data exports            │ │
│  │  Forbidden:      ANY write; solution import; DLP changes        │ │
│  │  Consumed by:    dataverse-architect (read-only diagnostics)    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  Actions:                                                              │
│  [Re-run /environment-discovery]   [Edit raw env-context.md]          │
│                                                                        │
│  ⚠ Stale warning: env-context.md is 92 days old. Per the Researcher's │
│  rule, files older than 90 days should be re-verified.                │
└────────────────────────────────────────────────────────────────────────┘
```

##### Components broken down

1. **Project header** — shows project name (from `<repo_root>/.claude-plugin/plugin.json` if present, else CWD basename), source file path, last-updated timestamp with relative form.
2. **Per-environment cards** — one card per environment in `environment-context.md`. Each card shows role, endpoint, pre-authorized action categories, forbidden actions, and the cross-referenced list of installed-plugin agents that consume this env-context per their agent frontmatter `priors` block.
3. **Actions row** — two buttons. "Re-run /environment-discovery" is a deep link that triggers the skill (which prompts the user, runs read-only probes, presents a save/edit/skip flow). "Edit raw env-context.md" opens the file in the OS file association (no in-dashboard editing — the file is prose and the user should edit it deliberately).
4. **Stale warning** — surfaces when last-updated > 90 days, in a yellow banner. The Researcher's Weekly Deep Research sweeps this file's age too; the Health tab also flags this; the warning here is the user-facing nudge.

##### What this tab explicitly does NOT do

- **Does not edit the env-context file.** It's prose. Editing in a structured form would require parsing the prose, which is brittle and removes the user's freedom to add notes.
- **Does not run the discovery skill itself.** Only deep-links to `/environment-discovery`. The skill's confirmation step, read-only-probe contract, and credential-refusal rules belong inside the skill, not in a dashboard tab.
- **Does not surface credentials.** Per the env-context template contract, credentials live in env vars / Key Vault, not in this file. If the user has mistakenly pasted a credential, the dashboard tab does NOT show it inline — it shows a redaction badge instead and surfaces a warning. (Same key-regex pattern as the Activity feed redaction in proposal 003 §4.7.)

##### Effort estimate

- `/__read` allow-list entry for `.ravenclaude/environment-context.md`: 0.5 hours (already allow-listed by `serve-dashboards.py` for write — same path for read)
- Prose parser (extracts environment blocks, role lines, action categories): **4 hours**
- UI cards + stale-detection logic: **3 hours**
- Cross-reference with agent priors (generator-time inline): **2 hours**
- Tests + a parser-resilience suite (the parser must tolerate users' free-form additions): **2 hours**
- **Subtotal: 11-12 hours.**

Sequenced as **ravenclaude-core 0.22.0** (same release as Agents tab — both are read-mostly diagnostic surfaces).

#### B.4.3 **Scenarios tab** — browse the marketplace's lessons-learned bank (expanded spec)

The `/wrap` command writes scenarios to `plugins/<plugin>/scenarios/`. Today the only way to read them is to open the marketplace repo and skim. The Scenarios tab is a per-plugin read-only browser.

##### Purpose

Answer three user questions:

1. **"Has anyone hit a problem like mine before?"** — the load-bearing question. Browse the scenarios bank, filter by tag / scope / product, find the relevant lesson.
2. **"What's the confidence on this scenario?"** — surface the `confidence: low|medium|high` and `scope: tenant-specific|version-specific|likely-general` frontmatter so the user can weigh whether to trust it.
3. **"Where do I capture my own scenario?"** — one-click `/wrap` deep link.

##### Data sources

| File | Used for | Read |
|---|---|---|
| `plugins/<plugin>/scenarios/*.md` | Per-scenario YAML frontmatter (9 fields per `/wrap` schema) + body content | Generator-time inline. No runtime read (scenarios are static; refresh on `/plugin marketplace update` then `generate-dashboards.py` re-runs). |

##### UI layout

```
┌─ Scenarios ───────────────────────────────────────────────────────────┐
│                                                                        │
│  Plugin filter: [● All  ○ power-platform  ○ data-platform  ○ …]      │
│  Search:        [                                              🔍 ]   │
│  Filters:       [☐ likely-general only  ☐ high-confidence only        │
│                  ☐ from past 90 days only]                            │
│                                                                        │
│  Showing 12 of 47 scenarios                                            │
│                                                                        │
│  ┌─ power-platform ─────────────────────────────────────────────┐    │
│  │                                                                 │   │
│  │  2026-05-21 · spn-flow-create-403          tenant   medium  ▸  │   │
│  │  2026-05-19 · pa-delegation-2000           general  high    ▸  │   │
│  │  2026-05-14 · cascade-deactivate           version  low     ▸  │   │
│  │                                                                 │   │
│  │  (expanded row example below)                                  │   │
│  │  ─────────────────────────────────────────────────────────    │   │
│  │  2026-05-21 · spn-flow-create-403          tenant   medium  ▾  │   │
│  │  Product: power-automate · Version: 2026.04                    │   │
│  │  Tags: spn, flow, dataverse, web-api                           │   │
│  │                                                                 │   │
│  │  ── Problem ──                                                  │   │
│  │  SPN got 403 calling PA Management API to create a flow.       │   │
│  │                                                                 │   │
│  │  ── Permissions context ──                                      │   │
│  │  SPN had Flows.Manage.All not granted at consent time…         │   │
│  │                                                                 │   │
│  │  ── Attempts ──                                                 │   │
│  │  - PA Management API → 403 (insufficient permission)           │   │
│  │  - Dataverse Web API → success (same SPN, different surface)   │   │
│  │                                                                 │   │
│  │  ── Resolution ──                                               │   │
│  │  Use Dataverse Web API path for programmatic flow CRUD;        │   │
│  │  PA Management is undocumented for flow CRUD anyway.           │   │
│  │                                                                 │   │
│  │  ⓘ Unverified field note. Confidence: medium.                  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                        │
│  ┌─ Capture a new scenario ─────────────────────────────────────┐    │
│  │  When you hit a problem worth recording, run /wrap.            │   │
│  │  [Launch /wrap]                                                │   │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────────┘
```

##### Components broken down

1. **Multi-axis filters** — plugin chips, search box (substring against title + tags + body), and three checkbox filters (scope = likely-general, confidence = high, age < 90 days). Filter state persists in URL params so a user can share a link to a filtered view.
2. **Per-plugin sections** — collapsible. Each scenario row is collapsed by default to a one-line summary; click to expand the full structured content.
3. **Expanded row** — renders the four sections from the `/wrap` schema (Problem, Permissions context, Attempts, Resolution) plus a "Unverified field note. Confidence: <level>" badge at the bottom. Format mirrors what an agent would see when invoking the scenario-retrieval skill.
4. **Capture-a-new-scenario footer** — deep link to `/wrap` for capturing fresh scenarios.

##### Composition with the scenario-retrieval skill

When an agent consults `plugins/<plugin>/scenarios/` via the `scenario-retrieval` skill (per `plugins/ravenclaude-core/skills/scenario-retrieval.md`), the **same data** powers the agent's mandatory "Unverified scenario detected" preamble. The dashboard's Scenarios tab is the human-facing surface; the skill is the agent-facing surface. Two surfaces, one data source.

##### What this tab explicitly does NOT do

- **Does not let the user edit scenarios in-place.** Editing flows through `/wrap` or direct file edit in the marketplace repo. The dashboard is read-only.
- **Does not let the user delete or promote scenarios.** Promotion to canonical best-practices is a maintainer-side decision (v0.2.0+ of the feedback loop). The dashboard surfaces the data but doesn't curate.
- **Does not pull scenarios from disconnected stores.** Only scenarios that ship in `plugins/<plugin>/scenarios/` of the installed marketplace appear. Remote scenario banks are out of scope.

##### Effort estimate

- Scenario YAML frontmatter parser (extends generator): **2 hours**
- Inline all scenarios into dashboard.html at generator time (same mechanic as Activity feed): **2 hours**
- UI: filter chips + search + expanded-row rendering: **5-7 hours**
- URL-param state for shareable filtered views: **1 hour**
- **Subtotal: 10-12 hours.**

Sequenced as **ravenclaude-core 0.23.0**, same release as Health tab phase 2 cleanups.

#### B.4.4 **Health tab** — diagnostics (expanded spec)

The Health tab is on the **critical path** (§5.5) because it's the surface that makes the merge model visible. Without it, the user-scope-default in Phase A creates surprise (R11). Treating this with appropriate depth.

##### Purpose

Answer four questions a user has when something feels off:

1. **"Is X allowed?"** — given a tool call shape (`Bash(git push:*)`, `Read(/etc/**)`), what's the effective decision across all my settings.json layers and the engine's deny>ask>allow resolution?
2. **"Why is Claude asking when I thought I allowed?"** — surfaces the specific rule (in the specific layer) that triggered the ask.
3. **"What rules are active right now?"** — the full merged set, grouped by allow / ask / deny and annotated with source layer.
4. **"What rules am I about to add?"** — preview a `/set-posture --scope <X>` diff before it lands.

##### Data sources (read order; all read-only)

The Health tab reads from these sources in order, computing the merge in JavaScript:

| Layer | File path | Detection / availability |
|---|---|---|
| Enterprise | `/Library/Application Support/ClaudeCode/managed-settings.json` (macOS), `C:\ProgramData\ClaudeCode\managed-settings.json` (Windows), `/etc/claude-code/managed-settings.json` (Linux) | Try to read via the dashboard's `serve-dashboards.py` if running; absent it cannot be read from `file://`. Marked "Read-only (managed by IT)" + a "Cannot read enterprise layer from this environment" warning when unavailable. |
| User | `~/.claude/settings.json` | Read via `serve-dashboards.py`'s `GET /__read` endpoint (proposed addition to the allow-list); on `file://` mode, user must paste the file content into a textarea or use File System Access API to grant read. |
| Project | `.claude/settings.json` | Same as user; relative to project root. |
| Local | `.claude/settings.local.json` | Same as user; relative to project root. |
| CGP env-context | `.ravenclaude/environment-context.md` (parsed for pre-authorized / forbidden patterns per active environment) | Read via `/__read`; surfaces as side-data not as a layer. |

`serve-dashboards.py` needs to gain a `GET /__read?path=<allow-listed>` endpoint mirroring the existing `POST /__save` allow-list. Path-traversal check identical. The four allow-listed read paths are the three settings.json layers + `.ravenclaude/environment-context.md`. The enterprise file is **not** in the project tree so it's outside the allow-list; the dashboard reads it via a separate `GET /__read-managed` endpoint (server-only, no path parameter) that returns the OS-appropriate managed-settings path's contents or 404 if absent / unreadable.

##### UI layout

```
┌─ Health ──────────────────────────────────────────────────────────────┐
│                                                                        │
│  ┌─ Effective rules (merged) ─────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  Filter: [ allow | ask | deny | all ▾ ]   Pattern: [ git    🔍 ]│   │
│  │                                                                 │   │
│  │   ──  deny  (3 rules)  ──────────────────────────────────       │   │
│  │   • Bash(rm -rf /*)                          enterprise        │   │
│  │   • Bash(git push --force:*)                 project           │   │
│  │   • Bash(curl | sh)                          user              │   │
│  │                                                                 │   │
│  │   ──  ask   (12 rules)  ──────────────────────────────────      │   │
│  │   • Bash(git push:*)                         project   ←       │   │
│  │     ↳ also allow at user; ask wins (deny>ask>allow)            │   │
│  │   …                                                             │   │
│  │                                                                 │   │
│  │   ──  allow (47 rules)  ──────────────────────────────────      │   │
│  │   • Bash(git status:*)                       user              │   │
│  │   …                                                             │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                        │
│  ┌─ Test a tool call ─────────────────────────────────────────────┐   │
│  │  Try:  [ Bash(git push origin main)                          ▶ ]│   │
│  │                                                                 │   │
│  │  → ASK                                                          │   │
│  │    Matched: ask Bash(git push:*)  at project (.claude/settings)│   │
│  │    Also matched: allow Bash(git push:*) at user               │   │
│  │    Resolution: ask wins (deny > ask > allow per merge model). │   │
│  │    To downgrade to allow you'd need to either:                │   │
│  │      • remove the project-layer ask, OR                        │   │
│  │      • add a deny — but that blocks entirely, doesn't loosen. │   │
│  │    Personal user/local layers CANNOT loosen this.             │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                        │
│  ┌─ Layer view ───────────────────────────────────────────────────┐   │
│  │  [● User · 28 rules]  [○ Project · 14]  [○ Local · 9]  [○ Mgd] │   │
│  │  (radio — only one layer shown at a time)                     │   │
│  │                                                                 │   │
│  │  ── ~/.claude/settings.json ───────────────────────────────    │   │
│  │  Last modified: 2026-05-23 14:23                              │   │
│  │  Applied by /set-posture (scope=user) at 2026-05-23 14:23     │   │
│  │                                                                 │   │
│  │  permissions.allow: ["Bash(git status:*)", "Bash(npm test:*)"…]│   │
│  │  permissions.ask:   ["Bash(git push:*)" …]                    │   │
│  │  permissions.deny:  ["Bash(rm -rf /*)" …]                     │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                        │
│  ┌─ State health ─────────────────────────────────────────────────┐   │
│  │  /init-agent-ready last run: 2026-05-18  (5 days ago)     ✓   │   │
│  │  /set-posture last run:      2026-05-23  (today)          ✓   │   │
│  │  /wrap last capture:         2026-05-19  (4 days ago)     ✓   │   │
│  │  Detected hooks (4):                                           │   │
│  │    • enforce-layout.sh        ravenclaude-core / PreToolUse   │   │
│  │    • guard-destructive.sh     ravenclaude-core / PreToolUse   │   │
│  │    • capture-env-context.sh   ravenclaude-core / SessionStart │   │
│  │    • dispatch.sh              ravenclaude-core / UserPrompt   │   │
│  │  Env-context conflicts: none                                  │   │
│  └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

##### Components broken down

1. **Effective rules (merged)** — the main panel. Lists every rule in the merged set, grouped by bucket (deny / ask / allow), with the source layer tag per rule. Patterns that exist at multiple layers show the "winning" instance with a one-line annotation of where else the pattern appears and why one wins. Filterable by bucket and substring.

2. **Test a tool call** — interactive: user types a tool-call shape (`Bash(...)`, `Read(...)`, `WebFetch(...)`), the panel runs the merge resolver in-browser against the read state and shows the resolution: **allow / ask / deny**, the matched rule(s), the rule's source layer, and a one-paragraph explanation of why this resolution won. This is the load-bearing "why is Claude asking?" answer.

3. **Layer view** — radio-switched view of the raw `permissions.{allow,ask,deny}` content per layer. Shows the file modification timestamp and the `/set-posture` last-applied timestamp from the side-car. Each layer is a tab/radio; only one at a time to avoid information overload.

4. **State health** — last-run timestamps for the three big commands (`/init-agent-ready`, `/set-posture`, `/wrap`), the list of detected hooks (read from `.claude/settings.json`'s `hooks` block + the plugin's `hooks/hooks.json`), and any active CGP env-context conflicts.

##### The merge algorithm (concrete)

In JavaScript, the merge resolver is:

```js
function resolveMerge(layers, patternToTest) {
  // layers = [{name: "managed", allow: [], ask: [], deny: []}, ...]
  // patternToTest = "Bash(git push origin main)"
  const matched = { deny: [], ask: [], allow: [] };

  for (const layer of layers) {
    for (const bucket of ["deny", "ask", "allow"]) {
      for (const rule of layer[bucket] ?? []) {
        if (matchesRule(rule, patternToTest)) {
          matched[bucket].push({ rule, layer: layer.name });
        }
      }
    }
  }

  // deny > ask > allow
  if (matched.deny.length)  return { decision: "deny",  matched };
  if (matched.ask.length)   return { decision: "ask",   matched };
  if (matched.allow.length) return { decision: "allow", matched };
  return { decision: "ask", matched: {}, fallback: "default-ask" };
}
```

`matchesRule` mirrors Claude Code's pattern engine (whitespace-sensitive, `:*` suffix for prefix, exact otherwise — see `plugins/ravenclaude-core/knowledge/claude-code-permissions.md` §"Bash patterns — the documented fragility"). To avoid drift from upstream's behavior, the matcher is implemented from the public docs, **not** by trying to reverse-engineer Claude Code's source. CI parity check: the `audit-gates.sh` merge-model gate uses the same matcher and validates against known-good fixtures.

##### Effort estimate

- `serve-dashboards.py` `/__read` + `/__read-managed` endpoints: **2 hours**
- Merge-algorithm JS + matcher: **4 hours**
- UI layout (4 panels + responsive): **6-8 hours**
- "Test a tool call" interaction + explanation copy: **3 hours**
- State-health detection (hooks, env-context, command timestamps): **3 hours**
- **Subtotal: 18-20 hours** (was originally estimated at 6-8h; the merge-model framing materially expanded scope, which is correct — this is the surface that earns the user's trust that the merge model isn't a footgun).

The Health tab is now bigger than the original estimate, but it's the most important downstream deliverable. Sequenced as **ravenclaude-core 0.20.0** (one minor after Phase A so users have a chance to hit the surprise before the diagnostic lands; better: ship Phase A + Health tab together as 0.18.0).

#### B.4.5 **Update notifier** (expanded spec)

Not a tab — a **top-bar banner + a dedicated changelog tab** that appears when the installed plugin version is older than the version at HEAD of the marketplace repo.

##### Purpose

Three questions:

1. **"Am I behind?"** — a non-modal banner that flashes when a newer version exists. Dismissable per-version (won't nag again for the same version).
2. **"What changed?"** — a Changelog tab listing the version diff: new commands, removed commands, schema-breaking changes, security-fix CVE references.
3. **"How do I update?"** — one click to launch `/plugin marketplace update ravenclaude` followed by `/reload-plugins`, via the deep-link mechanic.

##### Detection mechanism

GitHub Pages serves a stable JSON manifest at `https://mcorbett51090.github.io/RavenClaude/dashboards/latest-versions.json`:

```json
{
  "$schema": "https://github.com/mcorbett51090/RavenClaude/blob/main/scripts/latest-versions-schema.json",
  "generated_at": "2026-05-23T14:23:00Z",
  "marketplace_version": "0.26.0",
  "plugins": {
    "ravenclaude-core": {
      "version": "0.17.0",
      "released_at": "2026-05-22",
      "changelog_anchor": "v0-17-0"
    },
    "power-platform": { "version": "0.12.2", "released_at": "…", "changelog_anchor": "…" },
    "finance": { "version": "0.5.1", "released_at": "…", "changelog_anchor": "…" }
  }
}
```

`generate-dashboards.py` emits this on every release (it already reads `marketplace.json` and the per-plugin `plugin.json`). The dashboard does a single `fetch()` on tab open against this URL (which is `https://`, so works from `file://` because of the explicit HTTPS scheme). On `file://` mode with **no network**, the fetch silently fails — the banner does not appear (degrade by absence is correct here).

The user's **installed version** comes from the dashboard.html itself: the generator inlines `<meta name="ravenclaude-installed-version" content="0.17.0">` into the head. Banner triggers when `installed < latest` per semver compare.

##### UI

**Banner** (top of every tab):

```
┌──────────────────────────────────────────────────────────────────────┐
│  ⓘ  ravenclaude-core 0.18.0 is available (you're on 0.17.0).         │
│     [View changes]  [Update now]  [×]                                │
└──────────────────────────────────────────────────────────────────────┘
```

- "View changes" — opens the Changelog tab and scrolls to the `v0-18-0` anchor.
- "Update now" — deep-link to `/plugin marketplace update ravenclaude`, then a second deep-link to `/reload-plugins`. Both pre-filled, neither auto-executed.
- "×" — dismisses the banner per-version. Stored in `localStorage`: `dismissed-banner: ["0.18.0"]`.

The banner does NOT re-appear on the same machine for the same version. If 0.19.0 ships, the banner re-appears with the new version number.

**Changelog tab content** is pulled at generator time from each plugin's release notes. Each release section is auto-anchored (`v0-17-0`, `v0-18-0`, etc.). Filter chip at top: `[All plugins · ravenclaude-core · power-platform · …]`. Per release, the structured content is:

```
## ravenclaude-core 0.18.0 — Multi-layer comfort posture
  Released: 2026-05-30

  ### New
    + /set-posture --scope user|project|local — pick which settings layer to apply to
    + Dashboard: scope selector above the preset bar
    + Migration banner for legacy users

  ### Breaking
    ⚠ /set-posture default scope changed from project to user. Project-scope users
       see a migration banner on first run; --scope project still works.

  ### Security
    none

  ### Fixed
    none
```

##### Composition with Phase A migration banner

The Phase A first-run migration banner (described in §2.3.5) and the Update notifier are **distinct surfaces** but visually related. Decision: stack them when both apply, with the migration banner on top (more urgent). Both use the same dismissal pattern (`localStorage` per-version, per-banner-type).

##### Effort estimate

- `latest-versions.json` generation (extend `generate-dashboards.py`): **2 hours**
- Banner + dismissal + localStorage: **2 hours**
- Changelog tab (markdown render from inlined data): **3-4 hours**
- Update deep-link sequence + error fallback: **2 hours**
- **Subtotal: 9-10 hours.**

Sequenced as **ravenclaude-core 0.24.0**.

---

### B.5 Accessibility & i18n checklist (cross-cutting)

The dashboard already does well on accessibility — the existing Settings tab uses `role="radiogroup"`, `aria-selected`, `aria-controls`, focus-visible outlines, `prefers-reduced-motion` honoring, and `prefers-color-scheme` light/dark variants. The build-out preserves and extends this discipline.

#### Mandatory for every new tab and interaction

| # | Requirement | Where it applies |
|---|---|---|
| A1 | All interactive elements reachable by Tab; logical tab order matches visual order. | All tabs. |
| A2 | Radio groups use APG radiogroup pattern (Tab between groups, Arrow keys within, Space to select). | Settings scope selector, Agents scope selector, Health layer-view radio. |
| A3 | Icons that convey state always have a text label or `aria-label`. No state-by-color-only. | Command card status pills, Health rule-source tags, Agents enabled/disabled toggle. |
| A4 | Hover-only affordances also work on focus and on touch. The B.2 Design 1 command card's hover tooltip becomes a focus-popover and a tap-popover on touch. | Commands tab cards. |
| A5 | Modal dialogs trap focus; Escape closes; the trigger element receives focus on close. | Info modals, agent details modal, command preview modals. |
| A6 | Live-region announcements for save status (`role="status"` on the "auto-saved" pill). | All tabs with auto-save. |
| A7 | Color contrast ≥ 4.5:1 for normal text, ≥ 3:1 for large text. Verified in both `prefers-color-scheme: light` and `dark`. | All tabs. The existing accent (`#14b8a6`) on dark `--surface` (`#111827`) is 5.8:1 ✓. |
| A8 | Keyboard shortcuts (`⌘K` palette, `?` for help) document themselves via a visible help affordance. | Commands tab palette overlay. |
| A9 | No `outline: none` without a visible alternative. The existing CSS uses `outline: 2px solid var(--accent)` everywhere ✓ — preserve. | All tabs. |
| A10 | Heading levels properly nested (h1 → h2 → h3). Each tab's root is h2; sections within are h3. | All tabs. |

#### Internationalization

Out of scope for this plan. The dashboard ships in English. If a consumer needs translation, the discipline is: all user-facing strings concentrated in a single object at the top of the inlined JS (already partially the case in `dashboard.html`) so a future i18n pass swaps strings without rebuilding the form-rendering code. **Recommendation:** factor strings into a `const STRINGS = {…}` block at the top of the generated `<script>` even though we don't translate today. Cost: trivial. Future-proofs.

### B.6 Deep-link mechanic — fallback chain in detail (cross-cutting)

The Commands tab, Install tab, Update notifier, Environment tab, and Activity feed all use the same deep-link → fallback chain. Specified once here.

#### The fallback ladder

```
User clicks Launch
       │
       ▼
[ Probe: claude-cli:// handler registered? ]──── yes ───▶ Open claude-cli://open?q=...&cwd=...
       │                                                      │
       │                                                      ▼
       │                                              [ Claude Code receives ]
       │                                                      │
       │                                                      ▼
       │                                            Prompt box pre-filled
       │                                            (NOT auto-executed)
       │
       no ───────────────────────────────────────────┐
       │                                              ▼
       ▼                                       [ Copy to clipboard ]
[ Fallback 1: Copy to clipboard ]                     │
       │                                              ▼
       │                                       Toast: "Copied — paste in Claude Code"
       │
[ Fallback 2: Show in modal ]
       │
       ▼
Modal: 
       /init-agent-ready repo-type=plugin-marketplace
       
       [Copy]  [Close]
```

#### Probe implementation

There is no JavaScript API to query whether a URL scheme handler is registered. The pragmatic detection is the **race-the-navigation** pattern:

```js
async function probeClaudeCliHandler(timeoutMs = 800) {
  return new Promise(resolve => {
    let resolved = false;
    const onBlur = () => { if (!resolved) { resolved = true; resolve(true); } };
    window.addEventListener('blur', onBlur, { once: true });

    // Use a synthetic iframe to avoid losing the current page.
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = 'claude-cli://probe';
    document.body.appendChild(iframe);

    setTimeout(() => {
      window.removeEventListener('blur', onBlur);
      if (!resolved) { resolved = true; resolve(false); }
      iframe.remove();
    }, timeoutMs);
  });
}
```

The probe runs once on page load and caches the result in `sessionStorage`. Re-runs on next session because handler registration can change (Claude Code uninstalled, etc.). On `false`, the Launch buttons render as Copy buttons instead.

> **Limitations to honor.** The race-the-navigation pattern is best-effort. Safari ignores cross-scheme iframe sources entirely (no navigation, no blur, treated as no-handler). Firefox without scheme registration shows a chrome-level dialog the first time the scheme is invoked — survivable but noisy. Chrome / Edge handle gracefully. **Behavior matrix:**
>
> | Browser | Handler registered | Handler missing |
> |---|---|---|
> | Chrome / Edge | Opens CC ✓ | Probe returns false ✓ → Copy fallback |
> | Firefox | First click: confirmation dialog ("Open with Claude Code?") then opens ✓; subsequent clicks: opens silently ✓ | Confirmation dialog with "No handler" → Copy fallback |
> | Safari | Opens via OS handler ✓ | Probe returns false ✓ → Copy fallback |

#### Hard rules for the URL builder

(Repeating proposal 003 §9 for emphasis — these are not negotiable.)

1. The `q` parameter is **always** a hard-coded slash command from a generator-time allow-list. Never user input.
2. The `cwd` parameter is **always** derived from the dashboard's own file path. Never a form field.
3. The `repo` parameter is **always** the marketplace URL. Never user input.
4. No additional parameters beyond `q`, `cwd`, `repo`. If a command needs args, they appear **inside `q`** as part of the slash-command text (e.g., `?q=%2Fset-posture%20--scope%20user`).

#### Why "pre-filled but not executed" is the right ceiling

Claude Code's `claude-cli://open?q=...` deliberately pre-fills without executing. **We do not try to bypass this.** The user reading and pressing Enter is the consent gate. If a future Claude Code version added auto-execution, we would still keep the user-press-Enter step in our flow because the dashboard is opened from a browser — a different trust boundary than the terminal. Browser → CC bridge with no consent is a phishing waiting to happen.

---

<a id="phase-c"></a>
## 4. Phase C — per-agent slash commands across all 7 plugins

This section proposes the **slash commands** each agent / domain should expose. Today: 3 commands, all in ravenclaude-core. Proposed target: ~80-110 commands distributed across the 7 plugins (≈2 per agent average, weighted toward command-friendly specialties).

**Methodology.** For each agent I asked: *what would this specialist plausibly expose as a single-shot, named, repeatable invocation?* Commands are higher-leverage than agents because they (a) carry a verb, (b) have known args, (c) can be deep-linked from the dashboard, (d) can be discovered without reading the agent's whole prompt. They're the surface most users will interact with.

**Naming convention.** Verb-noun in kebab-case. Prefer 1-3 words. No plugin prefix in the slash name itself (the Commands tab filters by plugin). Exception: where a command name would collide across plugins, the lower-traffic plugin gets a prefix.

**Convention applied across the table:**
- *Owner* = the agent that primarily implements the command. Other agents may compose with it.
- *Args* = a one-line sketch (full schema later).
- *Notes* = composition with existing commands or known edge cases.

### 4.1 ravenclaude-core (14 agents, 9 commands today's 3 + ~15 proposed)

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/init-agent-ready` *(existing)* | architect | `repo-type`, `ci`, `hygiene`, `overwrite` | Boundary-file setup. |
| `/set-posture` *(existing)* | architect | `--scope user\|project\|local`, `--dry-run` | Translate posture YAML → settings.json. |
| `/wrap` *(existing)* | partner-success-manager (lead) | confirm questions | Capture lesson-learned scenario. |
| `/start-team` | architect | `task`, `priors-file?` | Dispatch the architect + relevant specialists for a focused task; produces a run-artifacts directory under `.ravenclaude/runs/`. |
| `/code-review` | code-reviewer | `branch?`, `pr?` | Run a focused review against current branch or a PR; emits the SOP JSON block. |
| `/security-review` | security-reviewer | `branch?`, `path?` | Same as built-in /security-review but composed with this team's rubric. |
| `/refresh-knowledge` | deep-researcher | `topic?`, `weekly?` | Run the Researcher meta-skill in quick or weekly mode. |
| `/draft-memo` | documentarian | `subject`, `audience`, `tone?` | Compose a memo from session context. |
| `/draft-decision` | architect | `subject`, `options?` | Architecture decision record (ADR) draft. |
| `/cleanup-worktrees` | architect | `--dry-run` | Reaps stale `.claude/worktrees/*` (already a skill; promote to command). |
| `/new-worktree` | architect | `name` | Spawns a fresh worktree (already a skill; promote). |
| `/spawn-team` | architect | `team-spec.yaml` | Dispatch a pre-defined multi-agent team (existing skill, surfaced). |
| `/install-doctor` | architect | (none) | Phase B.3 Install tab's prereq doctor pass. |
| `/list-plugins` | (read-only) | (none) | List installed plugins + their versions. |
| `/reload-plugins` | architect | (none) | Refresh plugin cache from marketplace. |
| `/scan-permissions` | security-reviewer | `--scope user\|project\|local` | Health-tab implementation: show resolved rules. |
| `/list-agents` | architect | `plugin?` | Print enabled / disabled agents per plugin. |
| `/list-skills` | architect | `plugin?` | Same for skills. |
| `/raid-add` | project-manager | `kind risk\|action\|issue\|decision`, `summary`, `owner?` | Add a row to RAID log; opens the template file pre-filled. |
| `/raid-update` | project-manager | `id`, `status?`, `comment?` | Update an existing RAID entry. |
| `/draft-runbook` | documentarian | `service`, `incident?` | Compose a runbook from session context. |

### 4.2 power-platform (11 agents)

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/dataverse-design` | dataverse-architect | `entity`, `relationships?` | Walk through table modeling decisions, includes the cascade / customer-column / polymorphism gotchas. |
| `/dataverse-import` | solution-alm-engineer | `solution-zip`, `env` | Pre-checks against the environment-context env, then runs `pac solution import`. |
| `/dataverse-export` | solution-alm-engineer | `solution-name`, `managed\|unmanaged` | Composes pac CLI flow. |
| `/flow-recovery` | flow-engineer | `flow-name`, `env?` | Walk the PA flow-recovery decision tree from `knowledge/programmatic-flow-creation.md`. |
| `/flow-deploy` | flow-engineer | `flow-file`, `env` | Idempotent deploy via Dataverse Web API path (Approach B from CGP example). |
| `/canvas-app-lint` | power-fx-engineer | `app-path` | Run pac solution check + the in-team Power Fx lint. |
| `/canvas-app-build` | power-fx-engineer | `app-path`, `target-env` | Wraps `pac canvas pack`. |
| `/model-driven-build` | model-driven-engineer | `app-name`, `env` | Pulls the model app, runs validators, suggests publishing steps. |
| `/pbip-build` | power-bi-engineer | `report-path` | Wraps PBIP→PBIX build via mermaid-cli equivalent for PBI. |
| `/pbip-deploy` | power-bi-engineer | `workspace`, `report-id?` | Wraps the deployment pipeline call. |
| `/dax-lint` | power-bi-engineer | `report-path` | Tabular Editor's best-practice rules, sub-shell. |
| `/dax-eval` | power-bi-engineer | `expression`, `model-path` | Uses the bundled pbix-mcp to evaluate an expression in-place. |
| `/test-studio-run` | power-platform-tester | `app`, `suite?` | Triggers Test Studio. |
| `/test-pac-check` | power-platform-tester | `solution-path` | Wraps `pac solution check`. |
| `/copilot-studio-publish` | copilot-studio-engineer | `bot-name`, `channel?` | Publish step. |
| `/copilot-studio-export` | copilot-studio-engineer | `bot-name` | Export topics + YAML. |
| `/pcf-scaffold` | pcf-developer | `component-name`, `template?` | `pac pcf init`. |
| `/pcf-build` | pcf-developer | `component-path` | `npm run build`. |
| `/power-pages-deploy` | power-pages-engineer | `site`, `env` | Site deployment wrapper. |
| `/tenant-dlp-audit` | power-platform-admin | (none) | Pull DLP policies + flag connectors in scope. |
| `/tenant-env-list` | power-platform-admin | (none) | List environments + their security groups. |

### 4.3 finance (7 agents)

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/draft-variance-commentary` | fpa-analyst | `period`, `vs?` | Variance commentary from a budget vs actuals table. |
| `/build-budget` | fpa-analyst | `entity`, `period`, `prior-budget?` | Budget construction worksheet draft. |
| `/forecast-rollforward` | fpa-analyst | `as-of` | Roll the forecast forward one period. |
| `/build-3statement` | financial-modeler | `entity`, `years` | 3-statement model scaffold. |
| `/build-dcf` | valuation-analyst | `target`, `wacc?`, `terminal-growth?` | DCF scaffold + sensitivity table. |
| `/comps-table` | valuation-analyst | `target`, `peers[]` | Trading comps assembly. |
| `/precedent-transactions` | valuation-analyst | `target`, `sector` | Precedent transactions table. |
| `/close-checklist` | controller | `period` | Generate / open the month-end-close checklist. |
| `/post-journal-entry` | controller | `entry-type`, `period` | Draft a JE; never auto-posts (HITL by design). |
| `/recon-prep` | controller | `account`, `period` | Reconciliation worksheet. |
| `/cash-runway` | treasury-analyst | `as-of`, `scenarios?` | Cash runway + covenant headroom. |
| `/fx-hedge-eval` | treasury-analyst | `exposure`, `tenor` | FX hedge proposal. |
| `/audit-pbc` | audit-prep-specialist | `auditor`, `scope` | Generate / refresh the PBC list. |
| `/audit-walkthrough` | audit-prep-specialist | `process` | Narrative walkthrough. |
| `/draft-board-pack` | board-pack-composer | `meeting-date` | Compose the board-pack from FP&A outputs. |

### 4.4 regulatory-compliance (6 agents)

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/sanctions-screen` | aml-kyc-analyst | `entity\|individual` | Walk through sanctions screening checklist. |
| `/edd-pack` | aml-kyc-analyst | `customer-id` | Enhanced due diligence pack. |
| `/sar-draft` | aml-kyc-analyst | `case-id` | Suspicious activity report draft. |
| `/regulatory-return` | regulatory-reporting-analyst | `return-type`, `period` | FATCA / CRS / supervisory / Solvency II / BMA EBS return scaffold. |
| `/risk-and-control-matrix` | risk-and-controls-specialist | `process` | RCM template fill. |
| `/policy-draft` | policy-and-procedure-writer | `topic`, `regulator?` | Policy / procedure draft. |
| `/policy-review` | policy-and-procedure-writer | `policy-file` | Annual review redline. |
| `/exam-prep` | examination-prep-specialist | `examiner`, `date` | Examination prep checklist. |
| `/exam-response` | examination-prep-specialist | `request-id` | Draft response to a regulator request. |
| `/bma-ebs-prep` | bermuda-insurance-specialist | `period` | EBS preparation specific to Bermuda. |
| `/bma-csr-prep` | bermuda-insurance-specialist | `period` | Capital and Solvency Return prep. |

### 4.5 web-design (7 agents)

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/site-architecture` | web-architect | `site-purpose`, `audience` | IA + sitemap draft. |
| `/stack-recommendation` | web-architect | `requirements` | Stack pick (Astro / Next / Vercel / etc.). |
| `/wireframe` | ux-designer | `page` | Wireframe a single page (low-fi). |
| `/user-flow` | ux-designer | `goal` | Map a user flow from entry to conversion. |
| `/design-tokens` | visual-designer | `brand?` | Generate design tokens (typography, color, spacing). |
| `/design-system-audit` | visual-designer | `site-path` | Compare current vs token system; flag drift. |
| `/component-spec` | frontend-implementer | `component` | Spec a React/Astro/Next component. |
| `/scaffold-page` | frontend-implementer | `page`, `framework` | Scaffold a page in the chosen framework. |
| `/cwv-tune` | performance-engineer | `url\|build-path` | Core Web Vitals audit + remediation plan. |
| `/img-optimize` | performance-engineer | `path` | Bulk image optimization. |
| `/wcag-audit` | accessibility-auditor | `url\|page-path`, `level AA\|AAA` | WCAG 2.2 audit. |
| `/a11y-fix` | accessibility-auditor | `violation-id` | Remediation for a specific violation. |
| `/seo-audit` | content-strategist | `url\|site-path` | Technical SEO audit. |
| `/copy-draft` | content-strategist | `page`, `tone?` | Page copy draft. |
| `/microcopy-pass` | content-strategist | `flow` | Microcopy review for a user flow. |

### 4.6 edtech-partner-success (6 agents)

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/partner-onboard` | partner-success-manager | `partner-name`, `lane k12\|highered\|corp` | Spawns an onboarding plan + RAID. |
| `/partner-profile-update` | partner-profile-curator | `partner-id` | Refresh the partner profile. |
| `/draft-qbr` | qbr-composer | `partner-id`, `quarter` | QBR deck compose. |
| `/health-score-refresh` | partner-success-manager | `partner-id?` | Recompute health scores; flag dips. |
| `/touchpoint-log` | partner-success-manager | `partner-id`, `summary` | Add a touchpoint log entry. |
| `/escalate-renewal` | partner-success-manager | `partner-id`, `risk-level` | Open a renewal-risk escalation. |
| `/success-playbook-draft` | success-playbook-designer | `lane`, `pain-shape` | Draft a new playbook entry. |
| `/learning-outcomes-report` | learning-analytics-analyst | `partner-id`, `period` | Outcomes report from the analytics warehouse. |
| `/learning-experiment` | learning-analytics-analyst | `hypothesis`, `cohort` | Design a learning experiment. |
| `/ferpa-comms-redact` | ferpa-comms-translator | `draft-text` | Scrub FERPA-protected fields from a draft. |
| `/ferpa-comms-translate` | ferpa-comms-translator | `audience parent\|student\|board` | Translate a comms draft for the audience. |

### 4.7 data-platform (4 agents)

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/db-setup` | database-setup-guide | `db postgres\|supabase\|other`, `purpose` | Walk through DB provisioning. |
| `/rls-policy-draft` | database-setup-guide | `table`, `multitenant?` | RLS policy authoring (uses the existing core skill). |
| `/etl-pipeline-design` | etl-pipeline-engineer | `source`, `sink`, `cadence` | Pipeline design. |
| `/etl-pipeline-build` | etl-pipeline-engineer | `pipeline-name`, `framework dbt\|airflow\|fivetran` | Build scaffold. |
| `/connector-scaffold` | connector-developer | `source-type`, `protocol rest\|graphql\|odbc` | Scaffold a connector. |
| `/connector-test` | connector-developer | `connector-name` | Connector test harness. |
| `/dashboard-build` | dashboard-builder | `tool cube\|supabase\|other`, `dataset` | Build a customer-facing dashboard. |
| `/embed-token-issue` | dashboard-builder | `dashboard-id`, `tenant` | JWT embed token issuance (uses the core skill). |

### 4.7.1 Additional commands surfaced by per-plugin verification (v7 expansion)

Three research passes (one per cluster of plugins) verified the v1 command tables against each agent's actual frontmatter `description` and Mission/Scope. They flagged gaps and proposed additions. The full additions, organized by plugin, are below. These are **proposed for Phase C** alongside the v1 list, bringing the total from ~95 to **~125 commands**.

**ravenclaude-core (+0)** — already comprehensive; no additions surfaced.

**power-platform (+12):**

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/copilot-studio-design` | copilot-studio-engineer | `bot-name`, `topic?` | Walkthrough of topic + slot-filling + generative-answer boundaries. |
| `/copilot-studio-test` | copilot-studio-engineer | `bot-name`, `payload-file` | Test a topic with payloads + assertions on conversation flow. |
| `/dataverse-audit` | dataverse-architect | `solution-name` | Schema review for anti-patterns (native N:N, FLS over-use, cascade-all hazards). |
| `/dataverse-plugin-review` | dataverse-architect | `plugin-file.cs` | Review plug-in C# for transactional correctness. |
| `/flow-build` | flow-engineer | `flow-name`, `template?` | Scaffold a new cloud flow with Try-Catch-Finally boilerplate. |
| `/custom-connector-build` | flow-engineer | `connector-name`, `auth-type` | Scaffold OpenAPI + auth for a custom connector. |
| `/model-driven-form-script` | model-driven-engineer | `form`, `event onload\|onsave\|onchange` | Scaffold OnLoad/OnSave/OnChange handlers with modern Xrm API + async/await. |
| `/pcf-test` | pcf-developer | `component-path`, `framework jest\|vitest` | Wire a Jest/vitest harness for PCF. |
| `/pbip-init` | power-bi-engineer | `pbix-file` | Scaffold PBIP folder structure from a `.pbix`. |
| `/dax-measure-review` | power-bi-engineer | `measure`, `model-path` | Walkthrough a measure for performance + semantic correctness with DAX Studio output. |
| `/power-fx-delegate-check` | power-fx-engineer | `formula-or-screen` | Identify non-delegable predicates; suggest rewrites. |
| `/component-scaffold` | power-fx-engineer | `component-name` | Create a reusable canvas component shell. |
| `/power-pages-table-permissions` | power-pages-engineer | `portal`, `tables[]` | Design web-role → table-permission mapping. |
| `/power-pages-auth-setup` | power-pages-engineer | `portal`, `auth b2c\|local` | Walkthrough B2C or local-account auth wiring. |
| `/tenant-capacity-forecast` | power-platform-admin | `months` | Project Dataverse storage + API entitlements N months forward. |
| `/managed-environment-design` | power-platform-admin | `env` | Walkthrough managed-env prerequisites + rollout. |
| `/vertipaq-analyze` | power-platform-tester | `model-path` | Wrap VertiPaq Analyzer; flag cardinality/table-size deltas. |
| `/solution-health-check` | solution-alm-engineer | `solution-name` | Deeper review of managed-vs-unmanaged state, circular dependencies, orphan components. |

(Note: the verification agent suggested ~6-8 of these as highest-priority; ship the top 6-8 in the first power-platform pass, defer the rest.)

**finance (+10):**

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/kpi-pack-build` | fpa-analyst | `entity`, `period` | Assemble KPI pack — flagged as a core agent scenario missed in v1. |
| `/scenario-modeling` | fpa-analyst | `topic` | "Three scenarios, always" — explicit fpa-analyst opinion. |
| `/model-review` | financial-modeler | `model-file` | Core agent scenario — 7-pass review per the agent's CLAUDE.md. |
| `/sensitivity-analysis` | financial-modeler | `model-file`, `var-1`, `var-2` | DCF/3-statement sensitivity table — expected output. |
| `/valuation-range-blend` | valuation-analyst | `target` | Methodology weighting / triangulation — core valuation discipline. |
| `/409a-refresh` | valuation-analyst | `entity` | 409A refresh — explicit core scenario. |
| `/covenant-compliance` | treasury-analyst | `lender`, `period` | Covenant compliance pack — core scenario missed in v1. |
| `/debt-schedule-review` | treasury-analyst | `entity` | Debt schedule walkthrough. |
| `/soc-control-narrative` | audit-prep-specialist | `framework SOC1\|SOC2`, `control` | SOC1/SOC2 control narrative — explicit core scenario. |
| `/deficiency-remediation` | audit-prep-specialist | `deficiency-id` | Remediation plan for an audit deficiency. |
| `/investor-update-letter` | board-pack-composer | `quarter` | Investor update letter compose. |
| `/lender-compliance-pack` | board-pack-composer | `lender`, `period` | Lender compliance pack — covenant + borrowing-base output. |

**regulatory-compliance (+9, includes splitting /regulatory-return):**

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/fatca-filing` | regulatory-reporting-analyst | `period` | FATCA filing — split from the overly-broad `/regulatory-return`. |
| `/crs-filing` | regulatory-reporting-analyst | `period`, `jurisdiction` | CRS filing — split. |
| `/supervisory-return-review` | regulatory-reporting-analyst | `return-type`, `period` | Supervisory return review. |
| `/ebs-prep` | regulatory-reporting-analyst | `period` | BMA EBS prep — split (also pairs with Bermuda specialist). |
| `/mra-response-draft` | examination-prep-specialist | `mra-id` | Management response to MRA / MRIA — explicit core scenario. |
| `/mock-walkthrough` | examination-prep-specialist | `process`, `examiner-role` | Run a mock examiner walkthrough. |
| `/risk-appetite-statement` | risk-and-controls-specialist | `entity` | Design a risk-appetite statement. |
| `/gap-analysis` | policy-and-procedure-writer | `policy-area`, `regulation` | Gap analysis against new regulation. |
| `/bma-class-determination` | bermuda-insurance-specialist | `entity` | Class determination — first scenario in the agent. |
| `/captive-capital-calc` | bermuda-insurance-specialist | `captive`, `period` | Captive capital calculation. |
| `/bscr-module` | bermuda-insurance-specialist | `module` | BSCR module-specific walkthrough. |

(Replaces the v1 `/regulatory-return` which was too broad.)

**web-design (+3):**

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/re-platform-audit` | web-architect | `current-stack`, `target-stack` | Migration between stacks (Next → Astro, etc.). |
| `/deploy-checklist` | frontend-implementer | `site` | Pre-launch verification (accessibility, perf, SEO gate). |
| `/content-audit` | content-strategist | `site` | Inventory existing copy before authoring new. Pairs with `/copy-draft`. |

**edtech-partner-success (+3, plus 1 reassignment):**

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/health-score-refresh` | learning-analytics-analyst *(reassigned from partner-success-manager)* | `partner-id?` | Recompute health scores. v7 correction: health scoring is an analytics question, not a PSM touchpoint. |
| `/adoption-diagnostic` | partner-success-manager | `partner-id` | Root-cause analysis for stalled adoption (rostering, training, champion, feature fit). |
| `/ferpa-audit` | ferpa-comms-translator | `comms-file` | Scan existing partner comms for FERPA violations. |
| `/adoption-sequencing` | success-playbook-designer | `lane`, `quarter` | Stage-aware activation rhythm (K-12 fall/spring/summer phases). |

**data-platform (+3):**

| Slash | Owner | Args | Notes |
|---|---|---|---|
| `/multi-tenant-migration` | database-setup-guide | `table`, `tenant-claim` | Backfill tenant_id, RLS introduction, JWT-claim migration. |
| `/data-quality-test` | etl-pipeline-engineer | `pipeline`, `framework dbt\|great-expectations` | Define dbt tests, severity tiers, runbook-per-test. |
| `/dashboard-performance-tune` | dashboard-builder | `dashboard-id` | Widget-by-widget budget enforcement, Cube pre-agg tiers, cache-layer selection. |

#### Revised totals

| Plugin | v1 commands | v7 additions | Total |
|---|---|---|---|
| ravenclaude-core | 21 | 0 | 21 |
| power-platform | 21 | +12 | ~33 |
| finance | 15 | +12 | ~27 |
| regulatory-compliance | 11 | +9 (with split) | ~17 |
| web-design | 15 | +3 | 18 |
| edtech-partner-success | 11 | +3 | 14 |
| data-platform | 8 | +3 | 11 |
| **Total** | **102** | **+42** | **~141** |

(Note: previously the doc claimed "~95"; the v1 count was actually 102 by a recount. v7 brings the total to ~141 commands across 55 agents — about 2.5 commands per agent.)

### 4.8 Cross-cutting observations

- **Commands per agent**: median ≈ 2.5; range 0-5. Some agents (security-reviewer, prompt-engineer, the coders, designer, data-engineer, tester-qa) have **zero** dedicated commands because their work is best done in-conversation; that's fine.
- **Total commands proposed**: ~141 across all 7 plugins (was ~95 in v1; +42 from per-plugin verification), plus the 3 existing. The Commands tab's card-grid view needs the "Show only 20 most-used" default to be usable.
- **Most-used commands** (the default 20 the Commands tab should surface) — informed by the use-case lookup table in `repo-guide.html`'s Overview tab plus first-session friction:
  1. `/init-agent-ready`
  2. `/set-posture`
  3. `/wrap`
  4. `/start-team`
  5. `/code-review`
  6. `/draft-memo`
  7. `/draft-variance-commentary`
  8. `/draft-qbr`
  9. `/dataverse-design`
  10. `/flow-recovery`
  11. `/cwv-tune`
  12. `/wcag-audit`
  13. `/sar-draft`
  14. `/sanctions-screen`
  15. `/db-setup`
  16. `/etl-pipeline-design`
  17. `/refresh-knowledge`
  18. `/cleanup-worktrees`
  19. `/install-doctor`
  20. `/health-score-refresh`

### 4.9 Naming and namespacing — built-in collisions, plugin prefixes

The proposed names assume a flat command namespace. Reality: Claude Code ships built-in slash commands (`/init`, `/review`, `/security-review`, `/help`, `/clear`, `/plugin`, `/loop`, `/schedule`, etc.) and plugin commands can be referenced as either `/<command>` (bare) or `/<plugin>:<command>` (qualified). The flat namespace creates three potential issues:

1. **Direct collisions with built-ins.** The Phase C table proposes `/security-review` as ravenclaude-core's branded security review. There IS a built-in `/security-review` per the Claude Code skill list. Plugin commands cannot shadow built-ins. **Resolution:** rename to `/team-security-review` OR rely on the `/ravenclaude-core:security-review` qualified form. Recommend renaming to `/team-security-review` (or `/sec-review`) to avoid the qualified-form-only path, which most users won't discover. Same audit needs to run against `/init` (Claude Code built-in skill at top of available-skills list) — the existing `/init-agent-ready` avoids that by prefix.

2. **Cross-plugin name conflicts.** No cross-plugin collisions in the v1 proposal (each plugin's command names are unique). Sanity-checked: `/draft-*` appears in ravenclaude-core (memo, decision, runbook), finance (variance-commentary, board-pack), regulatory-compliance (policy-draft, sar-draft), edtech-partner-success (qbr, success-playbook). All distinct nouns; no collision. BUT — `/code-review` (core) and `/canvas-app-lint` (power-platform) are domain-distinct; no risk. The `/list-plugins`, `/reload-plugins`, `/list-agents`, `/list-skills` set is **infrastructure** that arguably belongs as built-ins, not core commands. If Claude Code adds these in a later release, our names would collide. **Resolution:** namespace them as `/rc:list-plugins` etc. to be safe.

3. **Bare vs qualified names — what to recommend.** Claude Code's UX is "type `/` and pick from the list." Bare names auto-complete first; qualified names are typed less often. Recommend **bare for high-traffic commands** (`/wrap`, `/set-posture`, `/init-agent-ready`, `/draft-qbr`) and **qualified for low-traffic infrastructure** (`/ravenclaude-core:scan-permissions`, `/ravenclaude-core:reload-plugins`). The dashboard's Commands tab surfaces both forms; the Copy button always copies the bare form unless the user has a preference set.

**Audit deliverable:** before Phase C ships, an audit script (proposed `scripts/audit-command-collisions.py`) runs `claude --list-commands` (or equivalent), diffs against the marketplace's proposed command names, and fails CI on any collision. Add to `audit-gates.sh`.

### 4.10 Verifying owner agents actually exist

The Phase C tables claim each command is owned by a specific agent (e.g., "owner: dataverse-architect"). Inventory check against the actual files in `plugins/<plugin>/agents/` confirms:

| Plugin | Agents on disk (count) | Agents referenced in Phase C (count) | Mismatches |
|---|---|---|---|
| ravenclaude-core | 14 | 9 distinct (architect, code-reviewer, security-reviewer, partner-success-manager, deep-researcher, documentarian, project-manager, …) | none — every owner exists |
| power-platform | 11 | 11 distinct — uses every agent | none |
| finance | 7 | 6 (audit-prep-specialist, board-pack-composer, controller, financial-modeler, fpa-analyst, treasury-analyst, valuation-analyst) | none |
| regulatory-compliance | 6 | 6 — uses every agent | none |
| web-design | 7 | 7 — uses every agent | none |
| edtech-partner-success | 6 | 6 — uses every agent | none |
| data-platform | 4 | 3 (connector-developer, dashboard-builder, database-setup-guide, etl-pipeline-engineer) — *uses 4, see below* | none — all 4 used |

All owner-agent references in Phase C resolve to real agents in the plugins. The agents NOT given a dedicated command (security-reviewer, prompt-engineer, partner-success-manager-as-anything-other-than-/wrap-lead, fullstack-coder, backend-coder, frontend-coder, designer, data-engineer, tester-qa) are intentionally command-free in this proposal — their work is in-conversation review, design feedback, paired-coding, etc. **This is a v1 choice, not a permanent gap.** A later phase could surface commands like `/scaffold-component` (frontend-coder), `/scaffold-endpoint` (backend-coder), `/design-critique` (designer) if usage data supports them.

---

<a id="phase-d"></a>
## 5. Phase D — risks, open questions, sequencing

### 5.0 Implementation kickoff — what to do tomorrow morning

For Matt waking up to read this plan. Concrete next steps if (and only if) the plan is approximately right.

**If you have 15 minutes:** read §1.4 (the merge model correction — the biggest substantive finding), §2.2 (the user-scope default recommendation), §5.8.2 (the 20-decision summary). Decide if D1, D5, D7, D12 land. If they do, the rest of the plan is implementation, not architecture.

**If you have 1 hour:** add §5.8 (30-min user narrative) and §5.8.1 (5-min team-admin narrative). They're the acceptance tests. If a narrative reads true to you, the design is internally coherent. If it doesn't, the design has a gap we should close before any code ships.

**If you have a half-day to start building:**

1. **Branch off `main`.** `git checkout -b feat/ravenclaude-core-phase-a`. Keep this PR (#69) open as the spec; reference it from the implementation PR.
2. **Start with the script.** Implement the §2.3.9 patch sketch for `apply-comfort-posture.py`. Don't touch the dashboard yet; the script is the truthful part of Phase A. Use the §5.8.5 fixture matrix to drive tests.
3. **Ship the script behind a flag.** Default behavior stays `--scope project` until day 3 of the §5.8.5 ship-day sequence. Land the script, get reviewer eyes on it, then flip the default.
4. **Then the dashboard.** Add the §2.3.10 scope selector. No behavior change yet — the dashboard writes the YAML; the YAML doesn't write settings until the user runs `/set-posture`.
5. **Then the Health tab.** This is the part that makes the merge model un-surprising. Skip this and Phase A will surprise users. Do it before flipping the default.
6. **Flip the default.** Now `/set-posture` defaults to `--scope user`; migration banner fires for legacy state.
7. **Tag and release as 0.18.0.**

Total elapsed time, assuming 4-6 hours per day of focused work: **5-7 working days.** Less than a sprint.

**If you have a week+ to commit:**

After 0.18.0, the highest-leverage next slice is the **Commands tab base (Design 1)**. Reasons:
- The tab is currently a stub — it's the most visible "incomplete" surface
- The card grid is the foundation for everything in Phase C
- Each command shipped to it is a discoverable thing the user can find
- Cost: ~10 hours for the tab + 2-4 hours per command

After Commands tab base ships, **start adding the §5.8.4 first-5-per-plugin commands** at a rate of 2-3 per week. The first 35 commands take ~4-6 weeks of consistent shipping. After that, the dashboard is a serious productivity surface even if no more architectural work happens.

**If you DON'T want to build any of this:**

The plan still has value as **documented intent.** Future you (or a delegate, or a new contributor) can pick it up cold. The decision summary in §5.8.2 is the most reusable artifact — it's a roadmap of 20 design decisions you've thought through, with defaults that future-you can confirm or override without re-deriving the analysis.

The plan is also useful as a **stake in the ground**: when someone (you, a contributor, an LLM) starts iterating on the dashboard in 2 months, this doc tells them what the previous design pass concluded so they don't relitigate.

### 5.0.1 Lessons-from-prior-ships retro (v0.15.0 / v0.16.0 / v0.17.0)

What the dashboard has actually shipped — and what each ship taught us. Useful priors for Phase A.

#### v0.15.0 — per-plugin dashboard chassis

What shipped: the `dashboard.html` skeleton, the Settings tab (read-only first version), the `dashboard-schema.json`, the sibling `generate-dashboards.py`. No `/set-posture` yet; the dashboard was a "look but don't touch" UI.

**Lessons:**
- The static-HTML-no-backend constraint held up. No regret on the architecture choice from proposal 003.
- The auto-generated form from JSON Schema was harder than expected (~3-4× initial estimate). The dynamism of "schema describes the form" pays off only when you add a second category; for the first single category, hand-coded HTML would have been faster.
- Inline CSS + inline JS keeps the file ~250 KB. Discipline matters; one CDN dependency would have ballooned it past 1 MB.
- File-size monitoring should be a CI gate. We don't have it yet. Phase A should add it.

#### v0.16.0 — `/set-posture` slash command + snapshot-merge

What shipped: the `/set-posture` slash command + `apply-comfort-posture.py`'s snapshot-merge mode. The YAML round-trip worked; the dashboard could write a posture and the script could apply it.

**Lessons:**
- The **snapshot-merge mode was the wrong design**, fixed in 0.17.0. The footgun: if a hand-added `allow` rule existed in `.claude/settings.json` for a pattern AND the posture-emitted same pattern as `ask`, the merge silently downgraded the effective behavior to `ask`. Users hand-added `allow` rules to be permissive; the merge made them more restrictive. Surprise.
- This is the same shape of foot-gun that the **Phase A multi-layer design has to avoid**. We're not snapshotting now (overwrite mode); but the cross-layer merge model can produce similar surprises if a user's intuition is "looser layer wins" (it isn't — tighter wins). The Health tab is the unsurprise mechanism.
- The slash-command + script split is the right pattern. The command's job is to dispatch; the script's job is to compute and write. Phase A continues this pattern.
- Migration paths matter. The v0.16.0 → v0.17.0 cleanup logic (deleting the snapshot file) was bolt-on rather than design-time. Phase A's migration banner is design-time from the start.

#### v0.17.0 — overwrite mode + `security_deny` + per-pattern overrides + dashboard polish

What shipped: the EMISSIONS table grew, the YAML schema gained per-pattern overrides and a `security_deny` list, the script became overwrite-not-merge, the dashboard Settings tab got the collapsible per-pattern controls.

**Lessons:**
- **Overwrite is correct.** It's surprising on first contact ("wait, my hand-edits get wiped?") but the alternative (merge) silently downgrades. Phase A inherits this: the `/__save` of `.ravenclaude/comfort-posture.yaml` is the source-of-truth gesture; everything else is emission.
- **Per-pattern overrides are well-used.** The YAML's category-default + per-pattern overrides shape is more legible than a flat list. Phase A doesn't change this.
- **`security_deny` as a floor was the right choice.** Users feel safer knowing `.env` reads and `rm -rf /` are blocked regardless of their permissive settings elsewhere. Phase A's recommendation that user-layer DENYs are "sticky everywhere on the machine" is the same intuition.
- The dashboard polish (`★ Recommended` preset, info modals, per-pattern explanations) significantly increased confidence. Phase A should match this polish standard on the new scope selector + the Health tab.
- Three releases in 3 weeks was the right cadence. Each release had a single user-visible theme. Phase A + Health tab as a single release (0.18.0) keeps the "one theme per release" pattern.

#### Patterns that carry forward to Phase A

1. **One file is the source of truth** (the posture YAML). Everything else is emission.
2. **Overwrite-mode for derived state.** No snapshots, no merge-on-write, no silent state.
3. **Per-pattern overrides** for fine-grained tuning without inventing a new abstraction.
4. **Always-on safety floors** (`security_deny`).
5. **Polish the recommended path** (the `★ Recommended` preset is genuinely useful; the equivalent for Phase A is the user-scope default + the Health-tab "Test a tool call" UX).
6. **Migration deliberately**, not bolt-on. The Phase A migration banner is design-time.
7. **One theme per release.** 0.18.0 = "multi-layer posture + visibility." Not "multi-layer posture + Commands tab + Install tab." Discipline.

### 5.1 Risks (revised v14 with severity scoring)

Each risk scored on likelihood × impact (low/medium/high) and **severity** as the product (low / medium / high / critical).

| # | Risk | L × I = **Sev** | Mitigation |
|---|---|---|---|
| R1 | Deep-link handler unavailable on a meaningful fraction of users' machines → Launch buttons silently fall back to Copy everywhere → "launch" feels broken | M × M = **Med** | Feature-detect; fall back to Copy with one-time hint; re-run probe per release because handler-registration drifts. |
| R2 | Multi-layer posture's "5 of 5 plugins agree" precedent makes us default to user-scope, but a real team installing for shared CI will expect project-scope and get confused | M × M = **Med** | Migration banner explicitly offers `project`. Documentation calls out the team-use case. Banner copy chosen so the user reads it. |
| R3 | Card grid with 141+ commands is overwhelming despite chip filters | L × M = **Low** | "Show only 20 most-used" default; chip filters; palette overlay (Design 2) as the production-mode surface for power users. |
| R4 | Each new tab grows the dashboard's static HTML size; per-plugin dashboards balloon past 500 KB budget | M × L = **Low** | Sticky budget. Trees + Activity already inline-everything in proposal 003; Commands + Install do not add per-run data. CI gate `audit-bundle-size.sh` (new in Phase A per §5.0.1 lesson) fails on >500 KB. |
| R5 | `/__save` allow-list must expand for any new file the dashboard writes — easy to forget and break a tab silently | L × M = **Low** | `audit-allow-list-drift.py` CI gate (§5.3.1) diffs client write targets against server allow-list. |
| R6 | Per-agent slash commands proliferate without versioning → consumer's marketplace update silently adds 30 new commands; user surprise | M × L = **Low** | Each plugin's release notes itemize new commands. Dashboard's Update notifier (B.4.5) surfaces the diff. Per-plugin `featured: true` cap of 20 prevents explosive defaults. |
| R7 | Phase A's "user scope is default" surprises a CI environment where there is no persistent HOME | M × L = **Low** | CI detection (`CI=true`) warns + suggests `--scope project` instead. Backward-compat env var `RAVENCLAUDE_POSTURE_LEGACY_SCOPE=project` is the escape hatch. |
| R8 | Static HTML cannot live-poll for `install-doctor.json` updates → user feels nothing happened after running the command | M × L = **Low** | Install tab polls every 2s for file existence via `/__save` HEAD when serve-dashboards.py is running; otherwise shows "Re-run detect, then reload" affordance. |
| R9 | CGP env-context per-environment vs user-scope-posture machine-wide — apparent tension | L × M = **Low** | Phase A explicitly documents: comfort-posture is machine-default; CGP env-context is per-project per-environment; the two compose by deny>ask>allow at layer level. Doc change only. |
| R10 | Hostile static-HTML page hosted under file:// could read other origin storage via IndexedDB — but the dashboard's IDB only stores file handles for ITS OWN saves | VL × VL = **VLow** | Documented in security section of proposal 003 §9. No new attack surface introduced. |
| R11 | **Merge-model surprise** — user assumes "local overrides project" from non-permission settings; writes `--scope local allow` expecting to relax a project `ask` and is stuck asked. | **H × M = High** | Scope selector info modal leads with merge model in plain language; Health tab (B.4.4) "Test a tool call" panel surfaces the resolution; `--preview-merge` flag runs the same logic from CLI. **R11 is the load-bearing risk that ties Phase A to the Health tab being co-shipped (D12).** |
| R12 | **Project-layer `allow` is almost always wrong but easy to emit.** A single user pushes personal `mostly-allow` posture into the project file and silently grants the team patterns the team never discussed. | **H × M = High** | Project-scope confirmation modal (§2.3.5) counts emitted `allow` rules and warns; migration banner's option 3 ("apply at both") keeps project to denies+asks only; CI lint flags PRs that gain `permissions.allow` entries in `.claude/settings.json`. |
| R13 | Enterprise managed-settings denies invisible to Health tab. A pattern that looks `allow`ed in the merged preview can be denied by IT. | L × L = **VLow** | Read enterprise file when permissions allow; if present, show with "Read-only (managed by IT)" tag; if unreadable, show "Cannot read enterprise layer" warning rather than silently dropping. |
| R14 | **Dashboard generator + posture script drift.** The script's EMISSIONS table and the dashboard's schema-driven form must agree on category names. A category added in one and not the other = silent breakage. | M × M = **Med** | Single source of truth: `dashboard-schema.json` declares categories; both the form generator AND the script read it. CI check verifies the script's EMISSIONS dict keys exactly equal the schema's `categories` enum. |
| R15 | **/__read endpoint's path-traversal check fails subtly.** A canonicalize-then-compare check that mishandles symlinks could let a crafted path escape the allow-list. | L × H = **Med** | The check uses `Path.resolve().relative_to(REPO_ROOT)` (already used by `/__save`); add fuzzing test in `audit-gates.sh` with 20+ malicious path inputs. Same shape as the existing `/__save` defense, which has held up in v0.16.0/v0.17.0. |
| R16 | **Worktree confusion.** Phase A documents that worktrees share user-scope but have per-worktree project + local scopes. Power users with 5+ worktrees may not internalize this and see "wrong" rules in worktree N. | M × L = **Low** | The Health tab's "Layer view" shows which file paths are being read; explicit worktree-aware copy when the dashboard detects it's running inside a worktree (matching path on `.claude/worktrees/`). |
| R17 | **`/install-doctor` failure modes.** The doctor runs on the user's machine; if it crashes (e.g., a quirky Python install), the user sees a stack trace and thinks RavenClaude is broken. | L × M = **Low** | Doctor wrapped in try/except per check; failures report as "could not detect" (yellow) rather than crash. The script exits 0 even if individual checks fail. |
| R18 | **GitHub Pages outage** blocks Update notifier from fetching `latest-versions.json`. | L × L = **VLow** | Graceful degradation: banner doesn't appear; user manually checks for updates via the marketplace repo. Documented behavior; no new code. |
| R19 | **Telemetry file corruption.** The single-file JSON usage tracker (`~/.claude/ravenclaude-state/usage.json`) is written on every command invocation. A concurrent invocation could corrupt it. | L × L = **VLow** | File-lock per write or read-modify-write under a lock; lock library is stdlib `fcntl` on POSIX, `msvcrt.locking` on Windows. Worst case if lock fails: drop the write and try next time; no user-visible breakage. |
| R20 | **Migration banner fatigue.** If the script is invoked multiple times before the user acks the banner, the banner re-fires each time. | M × L = **Low** | Ack file at `~/.claude/ravenclaude-state/posture-migration-acknowledged` set on first explicit `--scope <X>` invocation; banner suppresses thereafter. |

### 5.2 Open questions for Matt

> *Items #1-9 are the v1 questions; #10-14 added in v3-v4 after the merge-model investigation and the chicken-and-egg / namespacing audits.*


1. **Phase A default scope.** I propose `--scope user` as the new default. Confirm before we ship the migration banner — if you'd rather keep `project` as default for compatibility, the banner becomes opt-in.
2. **Plugin-switcher in the header.** Cheap to add, but if you'd rather each dashboard be self-contained (no cross-plugin navigation) say so. My instinct is the switcher is useful; you'll know better.
3. **`/install-doctor` — own slash command, or fold into `/init-agent-ready`?** I lean toward own command because it's read-only and fast; `/init-agent-ready` is interactive and writes files.
4. **Per-agent enable/disable (B.4.1) — ship in Phase B or defer to its own phase?** It's well-scoped but it adds dispatch-layer wiring to the Team Lead in CLAUDE.md.
5. **Update notifier (B.4.5) — banner or its own tab or both?** Both feels right; banner is dismissable, tab keeps the changelog.
6. **Naming — should this dashboard rebrand from "RavenClaude comfort posture" to "RavenClaude dashboard"?** The title today is misleading once Settings is no longer the only tab.
7. **Mobile.** The dashboard is responsive but Settings is the only tab actually used on mobile so far. Should Commands work on mobile (the deep links won't function from mobile Safari to a desktop Claude Code session)? My guess: mobile is read-only convenience; Launch buttons disabled on mobile with a note.
8. **The "Show only 20 most-used" default**: ranking is hardcoded today (see §4.8). Should it be **personalized** by reading the user's actual usage from a local file? Probably v0.3.0.
9. **Should command cards show owner agent in the corner?** Helps map back to the agents tab; small visual cost. Recommendation: yes.
10. **Merge-model: do we read the enterprise layer?** Phase A §1.4 lists enterprise managed-settings as the top layer. The Health tab's merge preview (B.4.4) does *not* read it by default — the file may not be readable, and on some OSes the path varies. Recommend: best-effort read on supported OSes; warn-and-skip if unreadable. Confirm before we ship.
11. **`/security-review` collision.** The ravenclaude-core Phase C table proposes a `/security-review` command but Claude Code already ships a built-in `/security-review` skill. Two options: (a) rename to `/team-security-review`; (b) use the qualified form `/ravenclaude-core:security-review` only. Recommend (a) for discoverability.
12. **Infrastructure commands as qualified names.** `/list-plugins`, `/reload-plugins`, `/list-agents`, `/list-skills`, `/scan-permissions` — these feel like they belong as Claude Code built-ins. If Claude Code adds them later, we collide. Should we ship them as `/rc:list-plugins` etc. (qualified) to be safe?
13. **Install tab rename.** Phase B.3 argues for renaming "Install" → "Setup" or "Welcome" because the true audience is users who already have the plugin installed. Confirm the rename, or keep "Install" as-is for the prereq doctor surface.
14. **Project-scope confirmation modal copy.** The §2.3.5 design adds a confirmation modal on `/set-posture --scope project`. Two flavors: (a) gentle "are you sure?" reminder; (b) stricter "this affects everyone on the team; type 'i understand' to confirm." Recommend (a) for ergonomics, but (b) is defensible.

### 5.3 Phased build roadmap (updated v7 with detailed spec estimates)

| Phase | Version | Scope | Effort (focused hours) | Status |
|---|---|---|---|---|
| **A** | ravenclaude-core 0.18.0 | Multi-layer posture (`--scope` flag + dashboard scope selector + migration banner + side-car ack file + gitignore management) | 8–11 | proposed |
| **B.1** | ravenclaude-core 0.19.0 | Commands tab (Design 1: card grid + hover tooltip + deep-link Launch with race-the-navigation probe) for the existing 3 commands | 6–10 | proposed |
| **B.2** | ravenclaude-core 0.20.0 | Install tab + `/install-doctor` + plugin switcher in header | 8–12 | proposed |
| **B.3** | ravenclaude-core 0.21.0 | Command palette overlay (Design 2) on top of card grid | 4–6 | proposed |
| **B.4.4** | ravenclaude-core 0.18.0 | Health tab (revised v7 — full spec: 4 panels, merge resolver in JS, /__read endpoint, state health) | **18–20** *(revised from 6–8)* | proposed |
| **B.4.1** | ravenclaude-core 0.22.0 | Agents tab (revised v7 — full spec: scope selector, per-agent enable/disable, mandatory enforcement, Team Lead dispatch wiring, `apply-agents.py` companion) | **19–21** *(revised from 6–8)* | proposed |
| **B.4.2** | ravenclaude-core 0.22.0 | Environment tab (revised v7 — full spec: per-env cards, agent-priors cross-ref, prose parser, stale warning) | **11–12** *(revised from 3–4)* | proposed |
| **B.4.3** | ravenclaude-core 0.23.0 | Scenarios tab (revised v7 — full spec: multi-axis filters, URL-param state, expanded-row rendering) | **10–12** *(revised from 4–6)* | proposed |
| **B.4.5** | ravenclaude-core 0.24.0 | Update notifier (revised v7 — full spec: banner + Changelog tab + latest-versions.json mechanism + per-version dismissal) | **9–10** *(revised from 3–5)* | proposed |
| **C.1** | per-plugin (rolling) | Phase C commands shipped one plugin at a time, by priority. Start with ravenclaude-core's 21 commands. | 2–4 per command average | proposed |
| **C.2** | per-plugin (rolling) | Power-platform commands (33 with v7 additions). High value, well-scoped. | 2–4 per command | proposed |
| **C.3** | per-plugin (rolling) | Finance, regulatory-compliance, web-design, edtech-partner-success, data-platform commands (87 with v7 additions). | 2–4 per command | proposed |
| **D** | ravenclaude-core 0.25.0 | Command builder (Design 4) — opt-in for the 5-6 most arg-heavy commands; requires arg-schema declarations | 8–12 | proposed |

**Total effort estimate (revised v7)** — Phases A + B (all 5 subphases including the full-spec'd Health/Agents/Environment/Scenarios/Update notifier): **~100-135 focused hours**, spread across ~6-9 weeks of part-time work. Phase C is open-ended — at 2-4 hours per command and ~141 commands proposed, the C-arc is **280-560 hours** if every command ships; in practice we'd ship the top-20 first and the rest opportunistically.

**Critical-path sequencing recommendation** (informed by §5.5 dependency graph):
- **Ship together as 0.18.0:** Phase A + Health tab. The merge model surprises users; the Health tab is what unsurprises them. Don't release Phase A without it.
- **Ship as 0.19.0:** Commands tab base (Design 1). Without it, the deep-link infrastructure has no consumer.
- **Ship as 0.20.0:** Install tab. The first-session-friction wins are biggest here.
- **Defer until proven demand:** Agents tab (B.4.1 — heavy dispatch-layer wiring), Update notifier (B.4.5 — cheap but adds noise to the UI). Both are nice-to-have; neither is on the critical path of "the dashboard is useful for daily work."

**What ships in the first 4 weeks (target)**:
- Week 1: Phase A + Health tab spec finalized; `apply-comfort-posture.py --scope` implemented and unit-tested
- Week 2: Health tab UI + merge resolver JS; ship 0.18.0
- Week 3: Commands tab Design 1 with the 3 existing commands; ship 0.19.0
- Week 4: Install tab + `/install-doctor` + plugin switcher; ship 0.20.0

That's the **first 60 hours of focused work** producing a meaningfully better dashboard. Everything else is incremental.

### 5.3.1 `/__save` and `/__read` allow-list — concrete list

The dashboard's save and read endpoints (in `serve-dashboards.py`) maintain hard-coded allow-lists for security. Today's `/__save` allow-list:

```
ALLOWED_TARGETS = {
    ".ravenclaude/comfort-posture.yaml",
    ".ravenclaude/environment-context.md",
}
```

Phases A through B.4 require **expansions** to both `/__save` (write) and `/__read` (proposed new endpoint). Concrete table:

| Phase | Endpoint | Path | Direction | Notes |
|---|---|---|---|---|
| A | `/__save` | `.claude/settings.local.json` | write | Phase A `--scope local` target. |
| A | `/__save` | `.gitignore` | write (append) | Append `.claude/settings.local.json` if missing. Only `.gitignore` write the server ever does; idempotent. |
| A | `/__save` | `.claude/.comfort-posture-applied.json` | write | Side-car file recording last-applied timestamp per scope. |
| A | `/__read` | `.claude/settings.json` | read | For dashboard preview of current state. |
| A | `/__read` | `.claude/settings.local.json` | read | Same. |
| A | `/__read` | `~/.claude/settings.json` | read | User-scope settings read (NOTE: outside repo root — requires `/__read-user` separate endpoint with no path param). |
| B.4.1 | `/__save` | `.ravenclaude/agents.yaml` | write | Per-agent enable/disable. |
| B.4.1 | `/__save` | `.ravenclaude/agents.local.yaml` | write | Local-scope agent overrides. |
| B.4.1 | `/__read` | `.ravenclaude/agents.yaml` | read | Dashboard re-renders on load with current state. |
| B.4.1 | `/__read` | `.ravenclaude/agents.local.yaml` | read | Same. |
| B.4.2 | `/__read` | `.ravenclaude/environment-context.md` | read | Already allow-listed for write; add read. |
| B.4.4 | `/__read-managed` | OS-specific managed-settings.json path | read | New endpoint; no path parameter; returns the OS-default path's content or 404. |

**Allow-list discipline (added 2026-05-23 in v8):** every `/__save` write target is also listed in the project's `.repo-layout.json` `allowed_globs` if it lives in the project tree, AND the path-traversal check in `serve-dashboards.py` rejects anything not in `ALLOWED_TARGETS`. The check is enforced server-side; the client cannot smuggle paths in. A new CI gate (`scripts/audit-allow-list-drift.py`) diffs the dashboard's enumerated write targets (extracted from the JS) against the server allow-list and fails CI on drift. Drift between client and server is the highest-risk path-traversal regression.

### 5.3.2 Glossary — terms used in this plan

Concentrated definitions to ensure terms are used consistently throughout the doc and avoid common confusions:

| Term | Definition | What it is NOT |
|---|---|---|
| **Scope** | One of `user` / `project` / `local`, identifying which settings.json layer a posture or agents-file applies to. | Not the same as "category" (categories are subdivisions within a single posture). |
| **Layer** | A settings.json file at one of the Claude Code-defined locations (enterprise / user / project / local). | Not a synonym for "scope" — scope is the user's choice; layer is the engine's location concept. |
| **Posture** | A YAML document at `.ravenclaude/comfort-posture.yaml` describing per-category autonomy levels + per-pattern overrides + a security-deny list. | Not the same as `permissions.{allow,ask,deny}` in settings.json — the posture is the source; permissions are the emission. |
| **Category** | One of 12 buckets in the posture YAML grouping related rules (e.g., `shell_remote_mutate`, `network_outbound`). | Not the same as a "rule" — a category is a group; a rule is a pattern like `Bash(git push:*)`. |
| **Rule** | A single pattern string in `permissions.{allow,ask,deny}` (e.g., `Bash(git push:*)`). | Not a YAML key — rules are emitted from the YAML by `apply-comfort-posture.py`. |
| **Level** | One of `deny` / `always-ask` / `mostly-ask` / `mostly-allow` / `autopilot`, assigned to a category or pattern in the posture YAML. | Not a bucket — levels collapse to buckets at emission time (deny→deny, always/mostly-ask→ask, mostly-allow/autopilot→allow). |
| **Bucket** | One of `allow` / `ask` / `deny`, the three keys under `permissions` in settings.json. | Not the same as "level" — buckets are the post-collapse representation. |
| **Merge** | The cross-layer combination of all rules into one resolved set; deny>ask>allow within the resolved set, first match wins. | Not "override" — the more-specific layer doesn't replace less-specific layers (verified §1.4). |
| **Emission** | The act of converting posture YAML → settings.json buckets. Done by `apply-comfort-posture.py`. | Not a runtime concept — emissions are persisted files. |
| **Mandatory agent** | An agent flagged in a plugin's CLAUDE.md as non-disableable (e.g., security-reviewer). Cannot be disabled via the Agents tab. | Not the same as "always dispatched" — mandatory means available; the Team Lead still picks per its decision tree. |
| **Plugin** | One subdirectory of `plugins/` shipping `.claude-plugin/plugin.json`. Installed via `/plugin install`. | Not the same as "marketplace" — the marketplace is the catalog; plugins are entries in it. |
| **Marketplace** | The RavenClaude meta-repo containing all plugins + the dashboard + the docs + the CI. | Not the same as one plugin — there is one marketplace, multiple plugins. |
| **Scope selector** | The UI element (radio group) in the Settings and Agents tabs that picks which settings.json layer a posture / agents-file applies to. Persisted in `localStorage` per plugin. | Not the same as the segmented control in the Settings tab — that picks the level for one category. |
| **Side-car file** | A small JSON file alongside settings.json holding machine-readable metadata that JSON-with-no-comments can't carry (e.g., last-applied timestamp). | Not an alternative to settings.json — it's auxiliary, gitignored. |
| **Deep link** | A `claude-cli://open?q=<cmd>&cwd=<dir>` URL that opens Claude Code with a pre-filled but un-executed prompt. | Not "execute on click" — the user still presses Enter. |
| **Probe** | The race-the-navigation pattern (§B.6) that detects whether the `claude-cli://` handler is registered. | Not a network call — it's a synthetic iframe + blur-event race. |
| **CGP** | Capability Grounding Protocol. The four-clause discipline that governs agent action (pre-action env-context check + decision-tree traversal + alternate-methods enumeration + mandatory blocked-phrasing). | Not specific to the dashboard — it governs every agent in every plugin. |

### 5.4 Tests and CI implications

- **Phase A — script:** `audit-gates.sh` gets a new gate proving that `apply-comfort-posture.py --scope user --dry-run` against a known-good YAML produces a known-good user-scope diff. Three fixtures (user / project / local) × known-good + known-bad = six combinations.
- **Phase A — merge model:** new gate proving `apply-comfort-posture.py --preview-merge` against a known set of three settings.json files produces the expected merged set, with deny > ask > allow resolution applied. Property-based check: any rule denied at any layer must be denied in the merge; any rule asked at any layer (and not denied) must be asked in the merge.
- **Phase A — `allow`-at-project lint:** a new CI step in `validate-marketplace.yml` flags PRs where `.claude/settings.json` *gains* entries in `permissions.allow`. The flag is advisory, not blocking — sometimes a team allow is the right call — but it surfaces R12 to PR reviewers.
- **Phase B.1 — orphan-command sanity:** `audit-gates.sh` gets a gate proving that the dashboard's enumerated launchable commands appear in `commands/*.md` (no orphan commands referenced in HTML; no `commands/*.md` missing from the dashboard).
- **Phase B.1 — built-in collision audit:** `scripts/audit-command-collisions.py` (new) takes a snapshot of Claude Code's built-in commands (committed to repo at `docs/claude-code-builtins.txt`, updated quarterly), diffs against the marketplace's proposed bare command names, fails CI on any collision. See §4.9.
- **Phase B.4.1:** the `.ravenclaude/agents.yaml` schema goes through the JSON-Schema → form pipeline already in use for the Settings tab.
- **Phase C — frontmatter:** each new `commands/*.md` file gets a CI check that it has a frontmatter `description:` field, an `owner:` field naming the responsible agent, and at least one example in the body.
- **Phase C — owner-agent existence:** the same CI check verifies the `owner:` value resolves to an agent in the same plugin (or an explicit cross-plugin reference like `ravenclaude-core/architect`).

### 5.5 Dependency graph — what blocks what

A more compact view of the ordering than the roadmap table. Each phase is a node; arrows indicate "this must ship first."

```
  Phase A (multi-layer posture)
       │
       ├──> Phase B.1 (Commands tab — bare, no scope-aware UI)
       │         │
       │         ├──> Phase B.3 (palette overlay)
       │         │
       │         └──> Phase B.4.4 (Health tab — depends on merge-preview from Phase A)
       │
       ├──> Phase B.2 (Install tab + plugin switcher)
       │         │
       │         └──> Phase B.4.5 (Update notifier)
       │
       └──> Phase B.4.1 (Agents tab) — independent of merge model but depends on Team Lead reading agents.yaml

  Phase C (per-plugin commands)
       │
       └──> compositionally appears in Phase B.1 (the more commands exist, the more the tab is useful)
            Phase C does not BLOCK B.1; B.1 ships with the 3 existing commands and grows.

  Phase B.4.2 (Environment tab) — independent of everything else; can ship any time
  Phase B.4.3 (Scenarios tab) — independent; depends on /wrap output stabilizing
  Phase D (Command builder) — depends on at least 5 commands declaring arg schemas; Phase C must be partway in
```

**Critical path:** A → B.1 → B.4.4. The Health tab is the most consequential downstream deliverable because it makes the merge model visible to users — without it, Phase A's "user-scope default" creates a surprise (R11). Health-tab ship parity with Phase A's release is the gold standard; if that's not realistic, Phase A ships with `apply-comfort-posture.py --preview-merge` as the interim diagnostic and Health tab follows in the next minor.

**Parallelizable:** B.2 (Install tab), B.4.1 (Agents tab), B.4.2 (Environment tab), and Phase C commands are all independently shippable once A is out. They can be assigned in any order.

### 5.6 Decisions taken in this document vs decisions deferred

A summary table for the impatient reviewer:

| Decision | Taken in this doc | Deferred to follow-up |
|---|---|---|
| Multi-layer posture: yes, ship it | ✅ Phase A | — |
| Default `--scope` for `/set-posture` | ✅ `user` (was `project`) | Confirm with Matt (open Q #1) |
| Permission rule semantics | ✅ MERGE across layers, deny absolute | — (this is Claude Code's behavior, not ours to change) |
| Project-scope confirmation modal | ✅ ships with Phase A | Strictness (open Q #14) |
| Commands tab first UI | ✅ Card grid (Design 1) | — |
| Commands tab second UI | ✅ Palette overlay (Design 2) | — |
| Commands tab third UI | ✅ Builder (Design 4) deferred | Gated on arg-schema work |
| Accordion (Design 3) | ✅ explicitly skipped | — |
| Install tab rename | 🟡 recommended (Setup / Welcome) | Confirm (open Q #13) |
| `/install-doctor` as own command | 🟡 recommended | Confirm (open Q #3) |
| Per-agent enable/disable (B.4.1) | 🟡 sequenced post-A/B | Confirm phasing (open Q #4) |
| `/security-review` rename to `/team-security-review` | 🟡 recommended | Confirm (open Q #11) |
| Infrastructure cmds use `/rc:` prefix | 🟡 recommended | Confirm (open Q #12) |
| Health tab reads enterprise layer | 🟡 recommended best-effort | Confirm path-resolution (open Q #10) |
| Plugin switcher in header | 🟡 recommended | Confirm (open Q #2) |
| Dashboard rebrand to "RavenClaude dashboard" | 🟡 recommended | Confirm (open Q #6) |
| Mobile: launch buttons disabled | 🟡 recommended | Confirm (open Q #7) |
| Default 20 most-used personalization | 🟡 v0.3.0 | — |
| Owner-agent shown on cards | ✅ yes (recommended in open Q #9) | — |

Legend: ✅ = the doc commits to this; 🟡 = the doc *recommends* this and flags an open question for Matt.

### 5.7 Composition with proposal 003

This plan is a follow-up to proposal 003 (per-plugin dashboard). It does NOT supersede or re-decide anything in 003 — it picks up where 003 left off:

- **003 §4.3 / §4.4** (static HTML, no backend) — honored. All new tabs (Commands, Install/Setup, Agents, Health, Environment, Scenarios) are static HTML; the triple-path persistence model (POST /__save, File System Access API, manual download) carries forward unchanged.
- **003 §4.3** (dashboard form factor and tab list) — extended from Settings/Commands/Trees/Activity to add Install (→Setup), Agents, Health. Trees and Activity tabs are untouched here.
- **003 §4.7** (Activity feed) — out of scope; honored as-is.
- **003 §4.8** (Decision-tree viewer) — out of scope; honored as-is.
- **003 §7.1** (Per-machine vs per-project posture concept) — Phase A is the *implementation* of the concept 003 sketched; semantics refined here (merge model).
- **003 §7.4** (Team-shared vs personal / gitignore) — the merge-model finding strengthens 003's "personal posture should be gitignored" guidance into "the project file is a permission floor; personal posture must not touch it."
- **003 §9** (Security & threat model: file:// constraints, claude-cli:// hardening, hard-coded `q`) — all preserved. The Launch deep-link mechanic in B.2.4 explicitly references and inherits the 003 §9 hardening rules.
- **003 §11** (Implementation phases) — extended with the phase ordering in §5.3 of this doc. Proposal 003 sketched v0.1.0 → v0.2.0 → v0.3.0; this plan layers ravenclaude-core 0.18.0 → 0.25.0+ on top, with Phase A as the lead.

If anything in this plan contradicts proposal 003, **proposal 003 wins** — surface the contradiction for Matt's decision.

### 5.8 First 30 minutes — what a brand-new user's experience looks like (post-Phase A + B)

Concrete narrative grounding for the abstract phasing. Reads from the user's POV, with timestamps.

**Minute 0.** User hears about RavenClaude from Matt. Opens `https://github.com/mcorbett51090/RavenClaude` in browser. README points to repo-guide.html. Clicks through; sees the marketplace catalog with 7 plugins, one-line descriptions, and a top banner: *"Install in 2 commands"* with the marketplace-add + plugin-install lines. Reads the Step 0 access check — runs `gh repo view mcorbett51090/RavenClaude`. Succeeds (they have access).

**Minute 4.** Opens Claude Code in their work project. Runs `/plugin marketplace add https://github.com/mcorbett51090/RavenClaude`. Gets "marketplace added." Runs `/plugin install ravenclaude-core@ravenclaude`. Gets "installed." Runs `/plugin` to verify; sees ravenclaude-core 0.18.0 listed.

**Minute 7.** Reads the post-install message: *"Open the dashboard at plugins/ravenclaude-core/dashboard.html, or run /init-agent-ready to set up boundary files."* Opens dashboard.html in the browser. Sees the Setup (renamed from Install) tab is selected by default. Step 1 shows green checks across the prereqs row. Step 5 has two big buttons: "Launch /init-agent-ready" and "Launch /set-posture."

**Minute 9.** Clicks Launch /init-agent-ready. Browser asks to open with claude-cli://; user accepts. Claude Code focuses, prompt box pre-filled with `/init-agent-ready`. User presses Enter. Walks the 3-question wizard (repo-type, ci, hygiene). Files appear in their tree: AGENTS.md, CLAUDE.md, .repo-layout.json. (No CI workflow because they answered "no" to ci.)

**Minute 14.** Back to the dashboard. Setup tab shows /init-agent-ready ran ✓. Switches to the Settings tab — sees the comfort-posture editor with the default 12 categories. Picks the "Recommended" preset. Now sees a new row above the preset bar: *"Apply posture to:"* with User selected by default. They notice the Project row has a "*team*" tag and smaller styling. Doesn't touch it. Clicks "Auto-save to file…" and grants the FSA permission on `.ravenclaude/comfort-posture.yaml`.

**Minute 18.** Clicks the "Launch /set-posture" button. Deep-link opens Claude Code; prompt pre-filled with `/set-posture`. Presses Enter. Script runs; output: *"Writing ~/.claude/settings.json (--scope=user) — 47 allow, 12 ask, 3 deny."* Script footer: *"Hand-edits to permissions.{allow,ask,deny} in this file are wiped on next /set-posture. Personal session overrides go in .claude/settings.local.json."*

**Minute 20.** Tries a `Bash(git status)` call inside Claude Code; auto-approved. ✓ Tries a `Bash(git push origin main)` call; CC asks. They're confused: *"I set Recommended; doesn't that allow git push?"*

**Minute 22.** Goes to the dashboard's Health tab. Types `Bash(git push origin main)` into the "Test a tool call" input. Result panel: **ASK · matched: ask Bash(git push:*) at user · resolution: ask wins (deny > ask > allow per merge model).** Below: *"To allow git push without confirmation, change shell_remote_mutate from always-ask to mostly-allow in Settings."* User understands; goes to Settings; changes the category; re-launches /set-posture; re-tries — now auto-allowed.

**Minute 27.** Wants to share their posture with the team. Goes back to Settings, picks the Project radio. Confirmation modal appears: *"Project-scope rules are merged into every team member's effective permissions and cannot be relaxed by their personal layers. Use this only for shared policy. The patterns flagged below are emitted as allow at project scope — usually you want deny + ask only at this scope. Are you sure?"* Modal lists 47 allow rules. User cancels. Reads the modal copy more carefully. Realizes: project should be the team's *floor*, not their personal config. Goes back to User scope.

**Minute 29.** Opens Commands tab. Sees the card grid with the 20 most-used commands. Filters by plugin chip. Hovers over /draft-memo — sees the full description in a tooltip. Clicks Launch. CC focuses; prompt pre-filled. Pleased. Closes the dashboard.

**Minute 30.** First-session setup is done. The user has: posture applied at user scope, boundary files in place, hooks running (visible in Health tab), and they've understood the merge model via the Health tab's "Test a tool call" feature. They're confident the next time CC asks for permission, they know why.

This narrative is the **acceptance test for Phase A + B.1 + B.2 + B.4.4 + the renamed Setup tab.** If the user can't reach minute 30 cleanly with the proposed design, the design is wrong.

### 5.8.1 Second narrative — team admin onboards a team (5 minutes, mirror of §5.8)

A different user with different needs: a team lead at a consulting firm who wants to roll RavenClaude out to her team and ensure their **project-scope** settings are governed (not just her own machine).

**Minute 0.** Team lead (Sara) already has RavenClaude installed personally. She's heard Matt's pitch and wants to set up her team's repo. Opens the engagement's git repo in Claude Code; runs `/init-agent-ready` first to land AGENTS.md / CLAUDE.md / .repo-layout.json. ✓

**Minute 2.** Opens the dashboard. Setup tab shows /init-agent-ready ran ✓. Goes to Settings tab. Sees the Apply-to selector defaults to User. Clicks Project. Confirmation modal appears: *"Project-scope rules are merged into every team member's effective permissions and cannot be relaxed by their personal layers. Use this only for shared policy. The patterns flagged below are emitted as allow at project scope — usually you want deny + ask only at this scope. Are you sure?"*

**Minute 3.** Sara reads the modal carefully. She wants the team to: (a) never `git push --force`, (b) never `npm publish`, (c) always be asked before `git push` to main. She picks the "Custom" approach: tweaks just three categories to set tight project rules. Picks "Save" — dashboard offers to write `.ravenclaude/comfort-posture.yaml` with only the team-shared categories filled in (the rest defaulting to her users-scope settings).

**Minute 4.** Runs `/set-posture --scope project`. Output: *"Writing .claude/settings.json (--scope=project) — 0 allow, 3 ask, 8 deny."* She likes the "0 allow at project" outcome — that's exactly the discipline the dashboard nudged her toward. Reviews the diff. Commits.

**Minute 5.** Goes to the Agents tab. Picks the Project scope. Decides her team should NOT use the `data-engineer` agent (her firm has dedicated data engineers; she doesn't want Claude to dispatch to that lane). Disables it. The Agents tab updates the project-layer `.ravenclaude/agents.yaml`. Commits.

Done. Her team will inherit these rules on `git pull`. Individual team members can still add personal user-scope rules; they can't loosen the team's shared rules (merge model). The acceptance test for the **team-admin scope** of the design is: Sara reaches minute 5 without ever needing to read the documentation. The confirmation modal + the "0 allow at project" output + the dashboard's nudge toward "denies + asks only at project" all carry the design intent.

### 5.8.2 Decision summary — what we're asking Matt to confirm

A compact list of the explicit YES / NO / TBD questions across the whole document. Pulled out so a stakeholder can skim without re-reading 2,000 lines.

| # | Decision | Recommendation | Where it lives |
|---|---|---|---|
| D1 | New default for `/set-posture` scope | **user** (was project) — personal posture goes at user layer; project file becomes team policy only | §2.2 |
| D2 | Add migration banner when legacy state detected | **yes** — one-time prompt on first post-upgrade run; persists ack in side-car | §2.3.5 |
| D3 | Track `set-posture` last-applied via side-car file (not JSON comment) | **yes** — `.claude/.comfort-posture-applied.json` per scope; JSON comments NOT supported per research finding | §1.4 |
| D4 | Auto-add `.claude/settings.local.json` to `.gitignore` on first `--scope local` | **yes** — server appends if missing; idempotent | §1.4, §5.3.1 |
| D5 | Phase B.2 slash-tab primary UI design | **Card grid (Design 1)** + `⌘K` palette overlay (Design 2) layered later | §B.2.2 |
| D6 | Plugin switcher in dashboard header | **yes** — small dropdown top-right; cross-plugin navigation is friction otherwise | §3.1.2, §B.4 (Install tab) |
| D7 | Add 3 new tabs (Install, Agents, Health) and 1 stretch tab (Environment) | **yes** for Install + Agents + Health; Environment is recommended; Scenarios and Update notifier are bonus | §3.1.1 |
| D8 | Rename `/security-review` to avoid built-in collision | **yes** — recommend `/team-security-review` | §4.9 |
| D9 | Namespace infrastructure commands with `/rc:` prefix | **yes** — `/rc:list-plugins`, `/rc:scan-permissions` future-proof against built-in collisions | §4.9 |
| D10 | Split `/regulatory-return` into four narrower commands | **yes** — `/fatca-filing`, `/crs-filing`, `/supervisory-return-review`, `/ebs-prep` | §4.7.1 |
| D11 | Reassign `/health-score-refresh` from PSM to learning-analytics-analyst | **yes** — analytics question, not touchpoint | §4.7.1 |
| D12 | Ship Phase A + Health tab together as 0.18.0 | **yes** — the Health tab is what makes the merge model un-surprising | §5.3, §5.5 |
| D13 | Health tab includes a "Test a tool call" interactive box | **yes** — load-bearing for answering "why is Claude asking?" | §B.4.4 |
| D14 | Add `/__read` endpoint to `serve-dashboards.py` with allow-list | **yes** — required by Health, Agents, Environment tabs | §5.3.1 |
| D15 | Add CI gate `audit-allow-list-drift.py` preventing client/server allow-list drift | **yes** — highest-risk path-traversal regression | §5.3.1 |
| D16 | Add CI gate `audit-command-collisions.py` for built-in / cross-plugin collisions | **yes** — Phase B.1 prereq | §4.9, §5.4 |
| D17 | Update notifier mechanism (poll `latest-versions.json` from GitHub Pages) | **yes** — but degrades silently on no network | §B.4.5 |
| D18 | Mandatory agents enforced by Team Lead orientation pass | **yes** — disabling in user YAML is ignored for mandatory agents with warning | §B.4.1 |
| D19 | "Scope": store last choice per plugin in `localStorage` | **yes** — saves per-session friction | §2.3.1, §B.4.1 |
| D20 | Defer Command Builder (Design 4) until commands declare arg schemas | **yes** — Phase D, after first ~6 high-traffic commands have arg-schema declarations | §B.2.2 |

Open questions surfaced for Matt's discretion (re-list of §5.2, deduplicated):

| # | Question | Default if no answer |
|---|---|---|
| Q1 | Phase A default scope (`user` vs `project`)? | user — proceed |
| Q2 | Plugin switcher in header — keep or drop? | keep |
| Q3 | `/install-doctor` — own command or fold into `/init-agent-ready`? | own command |
| Q4 | Agents tab ships in Phase B or its own phase? | bundled in 0.22.0 |
| Q5 | Update notifier — banner or tab or both? | both |
| Q6 | Rename dashboard from "comfort posture" to "RavenClaude dashboard"? | yes, in 0.18.0 |
| Q7 | Mobile — Launch buttons disabled or attempted? | disabled with note |
| Q8 | "Most-used" ranking — hardcoded or personalized? | hardcoded for v0.19.0; personalized for v0.21.0 |
| Q9 | Show owner-agent in command card corner? | yes |
| Q10 | Enterprise-layer reading — attempt or skip? | skip; "managed by IT" affordance only |
| Q11 | `/security-review` rename to `/team-security-review` — yes? | yes |
| Q12 | `/rc:` qualified prefix for infrastructure commands — yes? | yes |
| Q13 | Install tab rename to "Setup"? | yes |
| Q14 | Project-scope confirmation modal strictness — block on "all allow" or warn? | warn (informative, not blocking) |

### 5.8.3 v0.18.0 ship checklist — the smallest meaningful first slice

The first slice is **Phase A + Health tab together** (D12). Concrete checklist before tagging 0.18.0:

**Script + library changes (`plugins/ravenclaude-core/scripts/`):**
- [ ] `apply-comfort-posture.py` gains `--scope {user,project,local}` argument (default: `user`)
- [ ] Path resolution per scope (`Path.home() / ".claude" / "settings.json"` for user, etc.)
- [ ] `RAVENCLAUDE_POSTURE_LEGACY_SCOPE=project` env var supported as backward-compat hatch
- [ ] Codespace detection (`CODESPACE_NAME`) warns about ephemeral home dir
- [ ] CI environment detection (`CI=true`) warns about ephemeral user-scope
- [ ] No-project-root detection: `--scope local` refuses without `.git/` or `.claude/` upward
- [ ] Side-car file write: `.claude/.comfort-posture-applied.json` per scope with ISO timestamp + script-version + scope name
- [ ] `.gitignore` auto-append on first `--scope local` (idempotent; only appends if line missing)
- [ ] Migration banner: detect legacy state, prompt for `1/2/3` choice, write ack to `~/.claude/ravenclaude-state/posture-migration-acknowledged`
- [ ] `--preview-merge` flag: read all 3 layers, compute the merged ruleset using deny>ask>allow resolution, print diff vs each layer
- [ ] Tests: 8 cases per §2.5 — dry-run × 3 scopes, no-project-root, legacy-env-var, worktree behavior, migration banner, idempotent re-run

**Slash command (`plugins/ravenclaude-core/commands/set-posture.md`):**
- [ ] Pass `$ARGUMENTS` through to script (allow user to type `/set-posture --scope project --dry-run`)
- [ ] Document scope semantics + merge model in command header
- [ ] Add an explicit warning section linking to Health tab

**Server (`scripts/serve-dashboards.py`):**
- [ ] Allow-list expands: `.claude/settings.local.json` (write), `.claude/.comfort-posture-applied.json` (write), `.gitignore` (write — append-only mode!)
- [ ] New `GET /__read?path=<allow-listed>` endpoint with the same path-traversal check
- [ ] New `GET /__read-user` (no path param, reads `~/.claude/settings.json`)
- [ ] New `GET /__read-managed` (no path param, OS-specific managed-settings path)
- [ ] `.gitignore` write is the **only** append-mode write the server does — separate handler with explicit "appends one line if missing" semantics, not a generic write

**Dashboard HTML (`plugins/ravenclaude-core/dashboard.html`, regenerated):**
- [ ] Settings tab gains scope selector (3-radio group above preset bar)
- [ ] Scope info modal: per-scope plain-language description + precedence table
- [ ] `localStorage` per-plugin persistence of scope choice
- [ ] Project-scope confirmation modal with the "denies+asks only at project" copy + flag of any allow rules in the YAML
- [ ] **Health tab** — all 4 panels (effective rules, test-a-tool-call, layer view, state health)
- [ ] Merge resolver in JS + matcher (~50 lines, mirrors `apply-comfort-posture.py` patterns)
- [ ] Migration banner (one-time, dismissable, persists ack in `localStorage`)
- [ ] Renamed page title: "RavenClaude dashboard" (was "RavenClaude comfort posture") per Q6

**Generator (`scripts/generate-dashboards.py`):**
- [ ] Emit `<meta name="ravenclaude-installed-version" content="X.Y.Z">` for the Update notifier (B.4.5 prereq, even though notifier ships later)
- [ ] Emit Health tab data (the merge-resolver matcher constants table)

**CI (`.github/workflows/`):**
- [ ] `audit-gates.sh` gains the Phase A merge-model property check + the `allow`-at-project lint
- [ ] `audit-allow-list-drift.py` runs on every PR (server allow-list vs client write-target enumeration)
- [ ] `validate-marketplace.yml` flags PRs that add to `permissions.allow` in any `.claude/settings.json` (advisory, not blocking)

**Docs:**
- [ ] `plugins/ravenclaude-core/CLAUDE.md` updated with the merge model paragraph (it's already in the knowledge file but worth re-stating in CLAUDE.md so it's load-bearing for the Team Lead)
- [ ] Release notes (per the plugin-release-checklist skill) call out:
  - Default scope change (the biggest user-visible change)
  - Migration banner behavior
  - JSON comments not supported (so don't try editing the side-car as JSON-with-comments)
  - `.gitignore` auto-append behavior
- [ ] Migration note: "If you upgrade from 0.17.0 and your team already has `permissions.allow` filled in `.claude/settings.json` because of v0.16.0/v0.17.0 behavior, the migration banner will offer to move them to user scope. Pick option 1 (recommended) unless those rules are genuinely team policy."

**Acceptance tests** (manual until automated; v0.18.0 ship-gate):
- [ ] Fresh user (no `~/.claude/settings.json`, no project posture): runs `/set-posture` after editing dashboard → settings written to `~/.claude/settings.json` correctly; Health tab shows the user-layer rules
- [ ] Legacy user (project posture from v0.17.0): runs `/set-posture` → migration banner fires; picks option 1 → user file written + project file cleared (with confirmation); banner doesn't refire
- [ ] Team-shared user (Sara from §5.8.1): picks Project scope; confirmation modal fires with "0 allow expected" message if posture had no allows, or with list of allow patterns if any; `/set-posture --scope project` writes only the shared rules
- [ ] CI runner: `CI=true` env var → script emits warning + still writes (doesn't refuse) so existing CI pipelines keep working
- [ ] Codespace: `CODESPACE_NAME` env var → script warns, suggests `--scope local` instead
- [ ] Worktree: two checkouts of the same repo; `--scope local` in each writes per-worktree `.claude/settings.local.json`; user file is shared
- [ ] Health tab "Test a tool call" with `Bash(git push origin main)`: returns the right decision based on the merged rules
- [ ] Phase A + Health tab pair: a user who hits the merge surprise (R11) can self-diagnose without asking for help

**Out of scope for 0.18.0 (defers to 0.19.0+):**
- Commands tab UI (deep links from the dashboard at all)
- Install / Setup tab
- Plugin switcher in header
- Agents tab
- Update notifier
- Scenarios / Environment tabs

This list is **the smallest meaningful change** that unsticks the personal-vs-team posture problem AND makes the merge model visible. Anything smaller doesn't justify a minor version bump.

### 5.8.4 Phase C — first 5 commands to ship per plugin (prioritized shortlist)

The ~141 commands in §4.1-§4.7.1 are aspirational. In practice we ship the top 5 per plugin first (35 total) and grow from there. Selection criteria:

- **High traffic** — the user will reach for this multiple times per engagement
- **Concrete output** — the command produces something tangible (a file, a deck, a table), not just walks the user through a process
- **Low arg-schema burden** — argless or 1-arg commands are cheaper to ship than commands needing complex arg UI
- **Owner agent is already polished** — don't ship a command whose owner agent is still being iterated on

#### ravenclaude-core (3 existing + 5 first-to-ship)

| Slash | Owner | Why first |
|---|---|---|
| `/init-agent-ready` *(existing)* | architect | First-session must-have |
| `/set-posture` *(existing)* | architect | Phase A's entry point |
| `/wrap` *(existing)* | partner-success-manager | Feedback loop |
| `/start-team` | architect | The dispatcher — every multi-agent run goes through this |
| `/code-review` | code-reviewer | Most-requested specialist invocation |
| `/draft-memo` | documentarian | Cross-domain utility; argless from session context |
| `/cleanup-worktrees` | architect | Hygiene; Matt mentioned this in CLAUDE.md as a polished skill ready for promotion |
| `/install-doctor` | architect | Required by the Install tab; B.3 prereq |

#### power-platform — first 5

| Slash | Owner | Why first |
|---|---|---|
| `/flow-recovery` | flow-engineer | Walks the canonical decision tree from the CGP example; most-cited scenario |
| `/dataverse-design` | dataverse-architect | High-traffic; the schema-modeling entry point |
| `/dataverse-import` | solution-alm-engineer | ALM operations are the everyday lane |
| `/pbip-deploy` | power-bi-engineer | Concrete output (deployment), low-arg |
| `/test-pac-check` | power-platform-tester | Wraps a single CLI call; near-zero implementation cost |

#### finance — first 5

| Slash | Owner | Why first |
|---|---|---|
| `/draft-variance-commentary` | fpa-analyst | Highest-traffic in finance domain; concrete output |
| `/close-checklist` | controller | Recurring; well-scoped |
| `/build-3statement` | financial-modeler | Concrete artifact; the modeler's signature output |
| `/build-dcf` | valuation-analyst | Concrete artifact + sensitivity table |
| `/draft-board-pack` | board-pack-composer | Aggregates FP&A outputs; visible to leadership |

#### regulatory-compliance — first 5

| Slash | Owner | Why first |
|---|---|---|
| `/sanctions-screen` | aml-kyc-analyst | Recurring operational task |
| `/sar-draft` | aml-kyc-analyst | High-stakes; concrete narrative output |
| `/policy-draft` | policy-and-procedure-writer | Concrete output; well-scoped |
| `/exam-prep` | examination-prep-specialist | High-stakes; checklist + walkthroughs |
| `/risk-and-control-matrix` | risk-and-controls-specialist | Concrete template fill |

#### web-design — first 5

| Slash | Owner | Why first |
|---|---|---|
| `/wcag-audit` | accessibility-auditor | High-traffic; concrete output (audit report) |
| `/cwv-tune` | performance-engineer | Concrete output (remediation plan); measurable wins |
| `/wireframe` | ux-designer | Concrete output (mockup) |
| `/site-architecture` | web-architect | First-engagement standard deliverable |
| `/copy-draft` | content-strategist | High-traffic; argless from session context |

#### edtech-partner-success — first 5

| Slash | Owner | Why first |
|---|---|---|
| `/draft-qbr` | qbr-composer | Highest-traffic; quarterly cadence; visible to partners |
| `/health-score-refresh` | learning-analytics-analyst | Recurring; concrete output |
| `/partner-onboard` | partner-success-manager | First-engagement deliverable; concrete plan |
| `/touchpoint-log` | partner-success-manager | High-frequency low-effort entry |
| `/ferpa-comms-translate` | ferpa-comms-translator | Compliance-critical; argless from draft text |

#### data-platform — first 5

| Slash | Owner | Why first |
|---|---|---|
| `/db-setup` | database-setup-guide | First-engagement entry point |
| `/etl-pipeline-design` | etl-pipeline-engineer | Concrete artifact; high-leverage |
| `/dashboard-build` | dashboard-builder | The plugin's signature deliverable |
| `/rls-policy-draft` | database-setup-guide | Security-critical; concrete output |
| `/embed-token-issue` | dashboard-builder | Security-critical; well-scoped (wraps a single library call) |

**Total: 35 first-to-ship commands** (5 per plugin × 6 domain plugins + 5 new core commands beyond the existing 3). At 2-4 hours per command, this Phase C first-cut is **70-140 hours of work**, deliverable in rolling per-plugin batches over ~3-4 weeks of part-time work in parallel with Phase B sub-phases.

After the 35 ship, the remaining ~106 commands proceed opportunistically — the dashboard's "most-used" ranking should be **personalized from usage telemetry** (Q8, deferred to v0.21.0) so the second wave is data-driven rather than guessed.

### 5.8.5 Phase A migration runbook — concrete sequence

Defensive against migration regressions. The Phase A migration is the riskiest change in the plan (touches users' working settings.json files). Concrete runbook:

#### Pre-ship validation

1. **Fixture matrix.** Build a CI fixture matrix of 9 starting states × 3 user choices = 27 runs.
   - Starting states: `{fresh, v0.17.0-with-allows, v0.17.0-with-asks-only, v0.17.0-with-denies-only, user-only, project-only, local-only, all-three, malformed-json}`
   - User choices: `{migrate-to-user, keep-at-project, apply-at-both}`
2. **Snapshot every output.** Each run produces a diff against the starting state; commit snapshots to `scripts/fixtures/migration/*.expected.json`.
3. **Idempotency check.** Run the script twice in succession with same inputs; second run must be a no-op (zero diff).
4. **Race check.** Two parallel `/set-posture` invocations in the same project must NOT corrupt the side-car ack file (file lock or atomic-rename per write).

#### Ship-day sequence

1. **Day 0** — ship `apply-comfort-posture.py` with `--scope` flag + side-car + migration banner; DO NOT change the slash command's default behavior yet. The script accepts the flag; users with the slash command see no change.
2. **Day 1** — ship the dashboard with the scope selector in the Settings tab; default radio is User; saving the YAML doesn't change behavior (user still has to run `/set-posture` to apply).
3. **Day 2** — ship the Health tab so users have a diagnostic surface before the default-scope change lands.
4. **Day 3** — flip the slash command's default behavior: `/set-posture` (no args) now uses `--scope user` and triggers the migration banner. This is the user-visible breaking change.
5. **Day 7** — release-notes review with 2-3 users (Matt + 1-2 trusted partners): did anyone hit a surprise? Roll back the default if needed.
6. **Day 14** — retro: how many users hit the banner? How many picked each option? Bake learnings into the v0.19.0 release notes.

#### Rollback plan

If Day 3 surfaces regressions:

1. **Soft rollback (preferred):** new release with `--scope project` as the default (v0.17.0 behavior); `--scope user` becomes opt-in. The script changes are kept; only the default flips. Single-line code change.
2. **Hard rollback:** revert the entire Phase A merge; users on 0.18.0 are encouraged to pin to 0.17.0 until 0.18.1 ships. Costly; only if soft rollback isn't enough.

The **Day 7 review** is the load-bearing safety net. The migration banner's UX must be tested with humans, not just CI fixtures.

#### Communication plan

- **Pre-ship blog post / repo announcement** (3 days before Day 3) explaining the default-scope change, what to expect, and how to opt out via `RAVENCLAUDE_POSTURE_LEGACY_SCOPE=project`.
- **In-banner copy** repeats the same explanation, more compact.
- **Release notes** carry the full rationale + the migration banner screenshot.
- **The Update notifier** (when it ships in 0.24.0) backfills users who are slow to upgrade with the same in-dashboard explanation.

### 5.8.6 Telemetry — what we measure vs what we don't

A late-arriving but important question raised by Q8 ("Most-used ranking — hardcoded or personalized?"). The answer is **personalized**, which requires telemetry. The telemetry is **local-only**, gitignored, and never leaves the user's machine.

#### What we measure

A single JSON file at `~/.claude/ravenclaude-state/usage.json`:

```json
{
  "$schema": "https://github.com/mcorbett51090/RavenClaude/blob/main/scripts/usage-schema.json",
  "schema_version": 1,
  "first_seen": "2026-05-22T14:23:00Z",
  "command_invocations": {
    "/init-agent-ready": { "count": 1, "last": "2026-05-22T14:25:12Z" },
    "/set-posture": { "count": 8, "last": "2026-05-23T09:14:33Z" },
    "/draft-memo": { "count": 12, "last": "2026-05-23T11:02:08Z" }
  },
  "dashboard_tab_opens": {
    "settings": { "count": 6, "last": "2026-05-23T09:14:00Z" },
    "commands": { "count": 14, "last": "2026-05-23T11:02:00Z" },
    "health": { "count": 2, "last": "2026-05-23T11:05:00Z" }
  },
  "scope_choices": {
    "user": 7,
    "project": 1,
    "local": 0
  }
}
```

#### What we do NOT measure

- **Arguments passed to commands.** They might contain client names, file paths, secrets. Just the command name.
- **Outcomes** (success/failure). Out of scope; the dashboard doesn't know.
- **Content of files** the user opens.
- **Identifying info** (no machine ID, no GitHub login, no IP).
- **Any network telemetry.** Nothing leaves the machine. The file is for the dashboard to read locally and rank commands; if the user clears it, the dashboard reverts to the hardcoded default-20 list.

#### How it's populated

A `recordInvocation()` hook in each command's invocation path. The hook is **opt-out** via `~/.claude/ravenclaude-state/.notrack`; presence of an empty file disables telemetry entirely.

The dashboard reads the file on Commands-tab open via `/__read`, ranks commands by `count * recency_weight`, and renders the top-20.

#### Privacy boundary

`~/.claude/ravenclaude-state/usage.json` is **explicitly outside** the marketplace repo and outside the consumer's project. It lives in the user's home dir. It is never committed. The Phase B.3 Install tab walks the user through this and offers to create the `.notrack` file at install time.

#### Effort

- `recordInvocation()` hook in command preamble + JSON read/write: **3-4 hours**
- Dashboard's ranking algorithm + render: **2 hours**
- `.notrack` opt-out + Install tab nudge: **1-2 hours**
- **Subtotal: 6-8 hours.** Sequenced as **0.21.0** (between Commands tab base and the per-agent command rollout, when there's enough data to make personalization meaningful).

### 5.8.7 Plugin-author guide — how to declare commands so they show up in the dashboard

For domain-plugin authors (today's 6 + future Salesforce / industry-specific plugins). The Commands tab discovers commands by scanning `plugins/<plugin>/commands/*.md` at generator time. Each command file must declare structured frontmatter so the dashboard can render the card, the hover tooltip, the args list, the launch deep-link, and the owner-agent badge.

#### Required frontmatter shape

```yaml
---
# REQUIRED — the slash name (kebab-case, lowercase). Without a leading slash.
name: init-agent-ready

# REQUIRED — one sentence, ≤ 100 chars, shown in the card body.
description: Set up agent-readable boundary files for any AI coding tool.

# REQUIRED — the agent that primarily implements this command.
owner: architect

# REQUIRED — the plugin slug. Self-contained against the file path so a
# rename of the plugin dir still needs this updated deliberately.
plugin: ravenclaude-core

# OPTIONAL — arg schema. If absent, the card renders with no args section
# and the Launch deep-link is just the bare command. If present, the
# Command Builder (Design 4, Phase D) uses this to render the arg form.
args:
  - name: repo-type
    type: enum
    values: [application, library, monorepo, documentation, data-ML, IaC, plugin-marketplace]
    required: false
    description: What kind of repo this is.
  - name: ci
    type: bool
    default: true
    description: Whether to add the validate-layout.yml CI workflow.
  - name: hygiene
    type: bool
    default: true
    description: Whether to add CI-hygiene scaffold.

# OPTIONAL — usage examples shown in the tooltip / Show preview.
examples:
  - /init-agent-ready
  - /init-agent-ready repo-type=plugin-marketplace ci=yes hygiene=yes

# OPTIONAL — tags for the Commands tab filter chips.
tags: [setup, boundary-files, first-session]

# OPTIONAL — feature-flag this command behind a plugin version.
# If the installed plugin is older than this, the card is hidden.
since: "0.15.0"

# OPTIONAL — set to true to surface in the default-20 list.
# Generator-side cap: at most 20 of these across the entire marketplace,
# enforced by audit-gates.sh.
featured: true
---

# /init-agent-ready

The body of the .md file becomes the full slash-command implementation
(passed to Claude when the command is invoked). See existing
commands/init-agent-ready.md for the canonical shape.
```

#### CI enforcement

`audit-gates.sh` gets a new gate `validate-command-frontmatter.sh`:

- Every `plugins/*/commands/*.md` must have all required fields filled
- `name` must match the filename basename (i.e., the file `init-agent-ready.md` must have `name: init-agent-ready`)
- `owner` must resolve to an agent that exists in the same plugin (or be a cross-plugin reference like `ravenclaude-core/architect`)
- `plugin` must match the directory path (`plugins/<this-plugin>/commands/...`)
- No more than 20 commands across the marketplace may have `featured: true`
- Slash-name collisions across plugins: error
- Slash-name collisions with Claude Code built-ins (per the snapshot in `docs/claude-code-builtins.txt`): error
- `args[].name` must match `^[a-z][a-z0-9-]*$` (no underscores; matches Claude Code's existing arg conventions)

#### Migration for the existing 3 commands

`/init-agent-ready`, `/set-posture`, `/wrap` today have minimal frontmatter (just `description` and sometimes `allowed-tools`). The Phase B.1 ship adds the full frontmatter shape to all three as the canonical examples. No behavioral change; just metadata.

#### When the dashboard's generator runs

`generate-dashboards.py --plugin <name>` reads all `commands/*.md` files in that plugin, parses frontmatter, emits the inline `window.__ravenclaude_commands = [{...}, {...}]` block in the dashboard. The `/wrap` command's "regenerate dashboard after capture" path (proposal 003 §4.7) also triggers a command-list re-scan because scenarios can affect what commands the user wants to surface (the Scenarios tab links back to commands).

#### Why structured frontmatter (not free-form Markdown)

The Commands tab's card grid + the Command Builder + the deep-link `q` allow-list + the audit-gates.sh checks all need machine-readable structure. Free-form prose works for human-readable command docs but doesn't scale to ~141 commands across 7 plugins with cross-cutting filters, search, and validation. The frontmatter is the contract; the body is the implementation.

### 5.8.8 Success criteria — how we know we got the design right

Feedback signals to watch for after each phase ships. If these signals are absent or inverted, the design is wrong and we revisit.

#### Phase A (multi-layer posture)

| Signal | What we want to see |
|---|---|
| Migration-banner choice distribution | ≥60% of users pick option 1 (migrate to user). If most pick option 2 (keep at project), the default may be wrong. |
| Team-shared-config commits | The number of PRs that modify `.claude/settings.json`'s `permissions.allow` block drops by ≥50% after the default change. Personal posture stops leaking into team git history. |
| "Why is Claude asking?" support questions | Users who hit a surprise should self-diagnose via the Health tab, not ask Matt. Track via the absence of these questions in the team Slack. |
| `~/.claude/settings.json` file existence on machines | After 2 weeks, ≥80% of active users have a user-scope settings.json with `permissions` filled by `/set-posture`. |

#### Phase B.1 (Commands tab base)

| Signal | What we want to see |
|---|---|
| Launch click-through rate vs Copy | Want Launch > Copy on machines where the deep-link probe succeeds. If users prefer Copy even when Launch works, the deep-link UX has friction we missed. |
| Commands tab open frequency | Want it to be the second-most-opened tab after Settings within 2 weeks of shipping. |
| Cards per user-session | Median ≈ 1-3 launches per session. If it's 0, the cards aren't useful for actual work; if it's 10+, the tab might be a discovery surface that's stealing attention from real work — surface the palette overlay sooner. |
| Most-used-20 ranking accuracy | After 30 days of telemetry, compute the actual top-20 from `usage.json` and compare to the hardcoded list. ≥70% overlap = the hardcoded list is fine; <50% overlap = personalization is overdue. |

#### Phase B.2 (Install / Setup tab)

| Signal | What we want to see |
|---|---|
| Time from "first opens dashboard" to "runs /init-agent-ready" | Median < 5 min for new users. If it's > 10 min, the Setup tab isn't directing users effectively. |
| /install-doctor pass rate on first run | ≥80% all-green on first run. If <50% green, the prereq list is too aspirational; trim it. |
| Drop-off between Step 3 (install plugins) and Step 5 (first-session setup) | <20% drop-off. If users install the plugins but never run /init-agent-ready, the dashboard isn't bridging install → use. |
| Repeat opens of the Setup tab | Falls to near-zero after first 1-2 sessions. If users keep returning, the tab is doing reference work (good for the Install knowledge; bad for the rest of the dashboard's reuse). |

#### Phase C (per-agent commands)

| Signal | What we want to see |
|---|---|
| Commands shipped per month | Average ≥ 3 commands per month per active plugin. If commands stall, the plugin is over-aspirational or the agent is over-narrow. |
| Bare vs qualified invocation ratio | ≥90% bare for high-traffic commands. If users type qualified names (`/finance:draft-variance-commentary`), the bare-name discovery isn't working. |
| Featured-list churn | The `featured: true` list (cap of 20) churns by ≤5 entries per quarter. If it churns wildly, the underlying usage data is noisy or the cap is wrong. |

#### Phase B.4 (Agents, Environment, Health, Scenarios, Update notifier)

| Signal | What we want to see |
|---|---|
| Agents tab disable usage | ≥10% of users disable at least one agent within a month. If 0%, the tab is solving a problem nobody has. |
| Health tab "Test a tool call" usage | ≥1 query per user per week during the first month after Phase A. Drops as users learn the merge model. Healthy. |
| Environment tab open frequency | High for power-platform / finance / regulatory-compliance users; low for web-design / edtech (which often don't have env-context files). Validates the tab is plugin-relevance-weighted. |
| Scenarios tab as a fallback for agents | The scenario-retrieval skill cites scenarios more often in agent runs over time. If citation rate stays flat, agents aren't picking up the scenarios. |
| Update notifier dismissal rate per version | <30% of users dismiss without clicking through. If >70%, the banner is noise; consider raising the threshold for when it appears. |

#### Anti-signals (what tells us we're wrong)

- Matt finds himself answering "how do I make Claude stop asking about X?" more often after Phase A → the Health tab isn't doing its job; consider auto-surfacing the Test-a-tool-call panel after a permission ask.
- Users discover commands by reading the marketplace README, not the Commands tab → the dashboard isn't a discovery surface; consider moving discovery to the repo-guide.
- Teams check in `.claude/settings.local.json` accidentally despite the gitignore append → the gitignore append failed; investigate and harden.
- The `/install-doctor` always shows green because users have everything → it's not actually a doctor, it's a placebo; rip it out and just trust people.

### 5.8.9 Stretch goals — explicitly tracked, not in any phase

Things deliberately left out of the roadmap but worth tracking so they don't get lost. Each becomes a candidate for v0.26.0+ if real demand surfaces.

| # | Stretch goal | Why deferred | Trigger to revisit |
|---|---|---|---|
| S1 | **Multi-posture authoring** (separate YAML per scope, all three editable in the dashboard simultaneously) | UI complexity buys little for solo developers; would muddy the scope-selector mental model | A team using all three scopes complains about the working-draft confusion |
| S2 | **Personalized command ranking** powered by `usage.json` | Telemetry doesn't exist until 0.21.0; needs data to be meaningful | When 0.21.0 has been live for 30 days |
| S3 | **Command builder (Design 4)** for arg-heavy commands | Requires arg-schema declarations in command frontmatter; only 5-6 commands warrant the investment | When ≥10 commands have arg schemas AND the Commands tab telemetry shows users typing args manually frequently |
| S4 | **Excel export** for the finance plugin's scenario / forecast outputs | Matt's native idiom; scope-creep risk; "agents can't read xlsx" gap | Finance-plugin engagement explicitly requests it |
| S5 | **Activity-feed real-time updates** instead of generator-time inlining | Current inline approach scales to ~100 runs; live updates need WebSocket or polling against serve-dashboards.py | Activity feed exceeds 200 runs OR users complain about staleness |
| S6 | **Plugin marketplace search** in the dashboard (find plugins not yet installed) | Repo-guide.html already does this; redundant surface | Repo-guide.html falls out of maintenance |
| S7 | **Cross-plugin dashboard** (one super-dashboard for all 7 installed plugins) | Each plugin's dashboard is currently self-contained; merging is friction that may not pay off | User feedback that 7 separate dashboards is too much navigation overhead |
| S8 | **Mobile-first responsive redesign** | Mobile is a read-only convenience surface; deep links don't work mobile → desktop CC | Real demand from Matt's iPad-from-couch workflow |
| S9 | **In-dashboard environment-context editing** (parsing the prose into form fields) | Prose parser is brittle; removes the user's freedom to add notes | Never, probably — prose is the right interface here |
| S10 | **Decision-tree path highlighting** in the Trees tab | Requires structured-condition convention that doesn't exist yet (proposal 003 dropped this; v7 honors that decision) | A structured-condition annotation convention emerges |
| S11 | **Integration with external project trackers** (Linear, Jira, Asana) for the project-manager agent's RAID/activity log | Out-of-scope for a marketplace; belongs in a separate plugin if at all | Direct user ask from someone running a specific tracker |
| S12 | **A Slack/Teams notifier** for `/wrap` captures and Update notifications | Network egress; auth complexity; privacy risk | Direct user ask from a team that wants shared visibility |
| S13 | **A read-only public mode** for the dashboard (browse the marketplace as a non-installer) | Repo-guide.html already serves this; redundant | Repo-guide.html falls out of maintenance |
| S14 | **Custom themes** beyond `prefers-color-scheme` | Visual polish; no functional gap | Aesthetic feedback that the current accent (`#14b8a6`) doesn't fit a team's brand |
| S15 | **A `/dashboard <plugin>` slash command** that opens the right file:// URL in the user's default browser | Convenience; cross-platform `xdg-open` / `open` / `start` handling is annoying | When users start asking "where's the dashboard for power-platform again?" |

### 5.8.10 Concrete `latest-versions.json` example for the Update notifier (B.4.5)

The full shape, with values matching the marketplace's actual current state:

```json
{
  "$schema": "https://github.com/mcorbett51090/RavenClaude/blob/main/scripts/latest-versions-schema.json",
  "schema_version": 1,
  "generated_at": "2026-05-23T11:00:00Z",
  "marketplace_version": "0.26.0",
  "marketplace_url": "https://github.com/mcorbett51090/RavenClaude",
  "plugins": {
    "ravenclaude-core": {
      "version": "0.17.0",
      "released_at": "2026-05-22",
      "changelog_anchor": "v0-17-0",
      "release_notes_url": "https://github.com/mcorbett51090/RavenClaude/releases/tag/ravenclaude-core-0.17.0",
      "breaking_changes": false,
      "security_fixes": false
    },
    "power-platform": {
      "version": "0.12.2",
      "released_at": "2026-05-20",
      "changelog_anchor": "v0-12-2",
      "release_notes_url": "https://github.com/mcorbett51090/RavenClaude/releases/tag/power-platform-0.12.2",
      "breaking_changes": false,
      "security_fixes": false
    },
    "finance": {
      "version": "0.5.1",
      "released_at": "2026-05-15",
      "changelog_anchor": "v0-5-1",
      "release_notes_url": "https://github.com/mcorbett51090/RavenClaude/releases/tag/finance-0.5.1",
      "breaking_changes": false,
      "security_fixes": false
    },
    "regulatory-compliance": {
      "version": "0.4.1",
      "released_at": "2026-05-14",
      "changelog_anchor": "v0-4-1",
      "release_notes_url": "https://github.com/mcorbett51090/RavenClaude/releases/tag/regulatory-compliance-0.4.1",
      "breaking_changes": false,
      "security_fixes": false
    },
    "web-design": {
      "version": "0.4.2",
      "released_at": "2026-05-13",
      "changelog_anchor": "v0-4-2",
      "release_notes_url": "https://github.com/mcorbett51090/RavenClaude/releases/tag/web-design-0.4.2",
      "breaking_changes": false,
      "security_fixes": false
    },
    "edtech-partner-success": {
      "version": "0.4.2",
      "released_at": "2026-05-13",
      "changelog_anchor": "v0-4-2",
      "release_notes_url": "https://github.com/mcorbett51090/RavenClaude/releases/tag/edtech-partner-success-0.4.2",
      "breaking_changes": false,
      "security_fixes": false
    },
    "data-platform": {
      "version": "0.1.0",
      "released_at": "2026-05-10",
      "changelog_anchor": "v0-1-0",
      "release_notes_url": "https://github.com/mcorbett51090/RavenClaude/releases/tag/data-platform-0.1.0",
      "breaking_changes": false,
      "security_fixes": false
    }
  }
}
```

`generate-dashboards.py` reads each `plugins/<plugin>/.claude-plugin/plugin.json` for the version, walks the corresponding release notes for `breaking_changes` and `security_fixes` flags, and writes this JSON to `dashboards/latest-versions.json` on every release. The dashboard's Update notifier fetches it on tab open.

**Security note:** the URL is `https://mcorbett51090.github.io/RavenClaude/dashboards/latest-versions.json` (GitHub Pages, HTTPS). The dashboard does NOT trust the file's content blindly — the breaking-changes and security-fixes flags drive UI emphasis (banner color) but not behavior. Even if the file is tampered with at the host (very unlikely with GitHub Pages), the worst outcome is the user sees a yellow banner instead of green or vice-versa; no auto-update is triggered.

### 5.9 What we explicitly do NOT plan in this document

- Tree-viewer interactions beyond proposal 003 §4.8. Out of scope.
- Activity-feed redesign. Proposal 003 §4.7 is honored as-is.
- Cross-plugin dashboard merging (one super-dashboard for all 7 plugins instead of one per). Phase 4+ if at all.
- A backend service for dashboards. Explicitly rejected in proposal 003 §3 and re-confirmed here.

---

<a id="appendix"></a>
## Appendix — references

- `plugins/ravenclaude-core/dashboard.html` (2,630 lines)
- `plugins/ravenclaude-core/dashboard-schema.json`
- `plugins/ravenclaude-core/scripts/apply-comfort-posture.py`
- `scripts/serve-dashboards.py`
- `scripts/generate-dashboards.py`
- `plugins/ravenclaude-core/commands/init-agent-ready.md`
- `plugins/ravenclaude-core/commands/set-posture.md`
- `plugins/ravenclaude-core/commands/wrap.md`
- `docs/proposals/2026-05-22-003-per-plugin-dashboard.md`
- `plugins/ravenclaude-core/CLAUDE.md` — house rules, Capability Grounding Protocol, environment-context check
- `plugins/ravenclaude-core/knowledge/claude-code-permissions.md` — Claude Code settings precedence + CVE history

---

*End of v1 draft. Iteration history below.*

## Iteration log

- **v1 (2026-05-22, overnight, Claude):** First full pass. Covers current-state analysis, Phase A multi-layer posture, Phase B dashboard build-out (IA + 3+ slash-tab UI designs + Install tab + 5 additional panels), Phase C ~95 proposed commands across all 7 plugins (with the existing 3 explicitly preserved), Phase D risks / open questions / phased roadmap.
- **v2 (2026-05-23, autonomous, Claude):** Merge-model correction. The v1 draft described cross-layer precedence as "local > project > user — more-specific layer wins," which is the model for *non-permission* settings (theme, model). For `permissions.{allow,ask,deny}`, Claude Code **merges** rules across layers and resolves per-call as `deny > ask > allow`, with `deny` in any layer being absolute. §1.4 was rewritten to state the merge model explicitly with a worked example. §2.3.3 was rewritten to derive Phase A's design from the merge model (was: "local layer wins"; now: "project layer is a permission floor that personal layers cannot relax, only further restrict"). §2.3.5 adds a revised scope-selector design that treats Project-scope as a load-bearing team-policy choice (separate visual treatment, confirmation modal, `allow`-emission warning). §2.3.6 adds a merge-model nuance to the YAML/effective-state discussion and points to a new `--preview-merge` CLI flag. §2.3.7 (migration) rewrites the banner copy to surface the floor/ceiling distinction. R11–R13 add three new risks (merge-model surprise, project-`allow` foot-gun, enterprise layer invisibility). v1's §2.3.1 is left in place but annotated as superseded by §2.3.5.
- **v3 (2026-05-23, autonomous, Claude):** Slash-commands tab + Install tab refinements. Added B.2.2 head-to-head comparison matrix scoring the 4 UI alternatives (card grid / palette / accordion / builder) on discoverability / speed / scale / a11y / build cost — confirms "card grid first, palette overlay second" as the right phasing. Added B.3.5 chicken-and-egg gap (a brand-new user can't open `dashboard.html` until the plugin is installed, so the "Install" tab's real audience is users who *already* installed and need the next step — recommend rename to "Setup" / "Welcome"). Added B.3.6 private-marketplace access (the repo is private; `/plugin marketplace add` 404s without GitHub auth — need Step 0 in repo-guide + a `gh repo view` check in the doctor). Added B.3.7 failure-mode table (5 most common install/first-run failures and the tab's response).
- **v4 (2026-05-23, autonomous, Claude):** Naming / collision / owner-existence audits. Added §4.9 naming and namespacing — flagged `/security-review` as colliding with the Claude Code built-in skill (rename to `/team-security-review`); proposed `/rc:` qualified prefix for infrastructure commands that Claude Code might add later; proposed `scripts/audit-command-collisions.py` as a new CI gate. Added §4.10 owner-agent inventory — verified every "Owner" column entry across the 7 plugins resolves to a real agent on disk; 55 agents total, 95 commands; ~10 agents intentionally have zero dedicated commands (security-reviewer, prompt-engineer, the coders, designer, data-engineer, tester-qa) because their work is in-conversation. Added open questions #10-14 (enterprise-layer reading, `/security-review` rename, infrastructure-command namespacing, Install tab rename, project-scope modal strictness). Expanded §5.4 tests with merge-model property check, allow-at-project lint, built-in collision audit, owner-agent existence check.
- **v5 (2026-05-23, autonomous, Claude):** Structural / decision-log additions. §5.5 dependency graph showing A → B.1 → B.4.4 as the critical path (Health tab makes the merge model visible to users; without it the user-scope-default change surprises). §5.6 decisions-taken vs decisions-deferred table — every recommendation in the doc tagged ✅ (committed) or 🟡 (recommended, open question for Matt). §5.7 composition with proposal 003 — explicit reconciliation showing 003 §4.3/§4.4/§4.7/§4.8/§7.1/§7.4/§9/§11 are all honored by this plan, with "proposal 003 wins on contradictions" as the tie-breaker rule. Renumbered the old §5.5 ("What we explicitly do NOT plan") to §5.8.
- **v5.1 (2026-05-23, autonomous, Claude):** Cross-reference accuracy fix. v5's §5.7 referenced proposal-003 sections §3 ("no backend") and §10 ("release plan") — neither is accurate (003 §3 is "Prior-art summary"; 003 §10 is "Open questions"). Corrected the citations: "no backend" lives in 003 §4.3 / §4.4; the release plan lives in 003 §11 (Implementation phases). Added a 003 §7.4 reference (team-shared vs personal / gitignore) which the merge-model finding strengthens into a more directive guidance.
- **v15 (2026-05-23, autonomous, Claude):** TOC refresh. The TOC was last updated at v2 and was lagging 13 versions of content. Rewrote to reflect every subsection added in v3-v14: B.2.5 card markup, B.3.5-B.3.7 install failure modes, B.4.1-B.4.5 full panel specs, B.5/B.6 cross-cutting checklists, 4.7.1/4.9/4.10 command verification + naming audit, 5.0-5.0.1 implementation kickoff + retro, 5.3.1-5.3.2 allow-list + glossary, 5.5-5.7 deps + decisions + 003 reconciliation, 5.8.1-5.8.10 narratives + ship checklist + first-5/plugin + migration runbook + telemetry + plugin-author guide + success criteria + stretch goals + latest-versions example. Each TOC entry is now tagged with the iteration version it was added in, so a reader can trace the document's evolution.
- **v14 (2026-05-23, autonomous, Claude):** Three additions. (1) §5.0 — Implementation kickoff: tomorrow-morning action paths sized by available time (15 min skim / 1 hour reading / half-day building / week+ committing / never building). Names the §5.8.5 day-by-day ship sequence as the half-day path; names the §5.8.4 first-5-per-plugin commands as the week+ path. (2) §5.0.1 — Lessons-from-prior-ships retro covering v0.15.0 (per-plugin dashboard chassis), v0.16.0 (set-posture + snapshot-merge — the foot-gun that was fixed in v0.17.0), v0.17.0 (overwrite-mode + security_deny). 7 patterns that carry forward to Phase A (one source of truth, overwrite-mode, per-pattern overrides, always-on safety floors, polish the recommended path, migrate deliberately, one theme per release). (3) §5.1 risks revised: each scored as L × I = Sev; R14-R20 added (generator/script drift, /__read path-traversal fuzzing, worktree confusion, /install-doctor crash, GitHub Pages outage, telemetry file corruption, migration banner fatigue). R11 (merge surprise) and R12 (project-allow foot-gun) confirmed as the load-bearing High-severity items that justify shipping Health tab + project-scope confirmation modal alongside Phase A.
- **v13 (2026-05-23, autonomous, Claude):** Four additions for ecosystem extensibility and post-ship observability. (1) §5.8.7 — Plugin-author guide: full required-frontmatter shape for `plugins/<plugin>/commands/*.md` (name, description, owner, plugin, args[], examples, tags, since, featured), CI enforcement spec, migration plan for existing 3 commands. Lets domain-plugin authors ship commands that surface in the dashboard correctly without ad-hoc docs lookups. (2) §5.8.8 — Success criteria: phase-by-phase feedback signals (Phase A: migration choice distribution, team-shared-config commit reduction; Phase B.1: launch vs copy rate, cards per session; Phase B.2: time-to-first-init-agent-ready, install-doctor pass rate; Phase C: commands shipped per month, bare vs qualified ratio; Phase B.4: agents-disable usage, Health test-a-call usage, scenario citation rate). Plus 4 anti-signals telling us the design is wrong. (3) §5.8.9 — Stretch-goals tracker: 15 items deliberately left out of any phase with why-deferred and trigger-to-revisit per item. Prevents drift back into "let's add this too" mid-build. (4) §5.8.10 — concrete `latest-versions.json` example with all 7 actual current plugin versions; clarifies the GitHub Pages security boundary (HTTPS-only; flags drive UI emphasis but not behavior).
- **v12 (2026-05-23, autonomous, Claude):** Implementer-facing code sketches. (1) §B.2.5 — full HTML + CSS + JS for a single command card in the Design-1 card grid (~200 lines). Drops into the existing `dashboard.html` token system; integrates with the deep-link probe and the optional `recordInvocation()` telemetry hook from §5.8.6. (2) §2.3.9 — full Python patch sketch for `apply-comfort-posture.py --scope` (resolve_settings_path / resolve_side_car_path / detect_no_project_root / check_ephemeral_env / fire_migration_banner_if_needed / maybe_append_to_gitignore / write_side_car), preserving v0.17.0's emission logic untouched. (3) §2.3.10 — HTML for the Phase A scope selector + the project-scope confirmation modal (suppressed when the user's posture has no allow rules to avoid friction).
- **v11 (2026-05-23, autonomous, Claude):** Four operational additions for ship-readiness. (1) §5.8.3 — v0.18.0 ship checklist enumerating every concrete script change, server change, dashboard change, generator change, CI change, doc change, and 7 manual acceptance tests that must pass before tagging the first Phase A release. Names what is explicitly out of scope for 0.18.0. (2) §5.8.4 — Phase C "first 5 commands per plugin" prioritized shortlist (35 total — 5 new core + 5 per domain plugin). Selection criteria: high traffic, concrete output, low arg-schema burden, polished owner agent. Maps the ~141-command aspirational list onto a ~70-140h actionable shortlist. (3) §5.8.5 — Phase A migration runbook with 9×3 fixture matrix, 7-day ship-day sequence (script-first → dashboard → Health tab → default-flip → human review → retro), soft / hard rollback plans, communication plan. The Day 7 human-review checkpoint is the load-bearing safety net. (4) §5.8.6 — telemetry section: what we measure (command counts + tab opens + scope choices, local-only) vs what we do NOT (args, content, identifying info, network egress); single JSON at `~/.claude/ravenclaude-state/usage.json`, opt-out via `.notrack`, 6-8h effort, sequenced as 0.21.0 to enable personalized command ranking (Q8 resolved).
- **v10 (2026-05-23, autonomous, Claude):** Executive-summary block added at the top of the document. A 2-minute read covering the three workstreams (Phase A, B, C), the five things to decide first (D1, D5, D7, D12, D14 from §5.8.2), the four "first 4 weeks" milestones (~60 focused hours), the single biggest correction from v1→v2 (permissions MERGE, not override), and the open questions to confirm. Designed for a busy reader who'll later read the full doc selectively.
- **v9 (2026-05-23, autonomous, Claude):** Two additions. (1) §5.8.1 — second narrative for the team-admin user persona (Sara, 5 minutes); mirror of §5.8's individual-user 30-minute narrative. Tests the project-scope confirmation-modal copy and the dashboard's "denies + asks only at project" nudge. (2) §5.8.2 — Decision summary: a single compact table of all 20 explicit design decisions the doc proposes Matt confirm (D1-D20), plus a re-listed Q1-Q14 of open questions with default behaviors if Matt doesn't answer. Stakeholder-skim affordance — answers "what is this plan asking me to decide?" in one screen.
- **v8 (2026-05-23, autonomous, Claude):** Three additions and one update. (1) §B.4.2 Environment tab expanded from a bullet list to a full design (purpose, data sources, UI cards per environment, agent-priors cross-reference, stale warning, what-it-does-NOT-do, 11-12h estimate). (2) §B.4.3 Scenarios tab expanded similarly (multi-axis filters with URL-param state, expanded-row rendering of the 4 sections from /wrap schema, composition with the scenario-retrieval skill, 10-12h estimate). (3) §5.3 Phased roadmap updated with revised effort estimates from v7 spec depth (Health 6→18-20h, Agents 6→19-21h, Environment 3→11-12h, Scenarios 4→10-12h, Update notifier 3→9-10h); total Phase A+B revised from 60-95h → 100-135h; critical-path sequencing recommendation added; "first 4 weeks (target)" concrete week-by-week shipping plan. (4) §5.3.1 — concrete `/__save` and `/__read` allow-list expansion table tracking every new write/read path needed for each phase (12 entries spanning Phase A through B.4.4), plus a new CI gate (`scripts/audit-allow-list-drift.py`). (5) §5.3.2 — glossary of 17 terms used in the plan, ensuring "scope", "layer", "posture", "category", "rule", "level", "bucket", "merge", "emission" etc. are used consistently.
- **v7 (2026-05-23, autonomous, Claude):** Four major additions. (1) §B.4.1 Agents tab expanded from a bullet list to a full design (purpose, data sources, UI layout, components, settings file shape, Team Lead dispatch behavior, mandatory-agent enforcement, 19-21h effort estimate, sequenced as 0.22.0). (2) §B.4.5 Update notifier expanded from a paragraph to a full design (detection mechanism via `latest-versions.json` served from GitHub Pages, banner + dedicated Changelog tab, dismissal semantics, composition with Phase A migration banner, 9-10h effort estimate). (3) §B.5 Accessibility & i18n checklist — 10 mandatory accessibility requirements cross-cutting all new tabs; i18n deferred but recommends factoring strings into a `STRINGS` block for future-proofing. (4) §B.6 Deep-link mechanic — formal fallback chain (probe → claude-cli://, copy fallback, show fallback), race-the-navigation probe pattern with code, per-browser behavior matrix, hard rules for URL builder. (5) §4.7.1 — per-plugin command additions surfaced by three verification agents: +42 new commands (mostly power-platform +12, finance +12, regulatory-compliance +9), bringing total from ~95 to ~141. Also reassigns `/health-score-refresh` from PSM to learning-analytics-analyst (it's an analytics question, not a touchpoint).
- **v6 (2026-05-23, autonomous, Claude):** Concrete grounding additions. (1) §B.4.4 Health-tab spec expanded from a hand-wavy bullet list to a full design with purpose, data sources (with `serve-dashboards.py` endpoint additions), UI layout sketch, four-component breakdown, merge-algorithm JS pseudocode, and effort estimate (revised to 18-20h, up from 6-8h — appropriately). The Health tab is on the critical path because it makes the merge model visible to users. (2) §2.3.8 added — concrete YAML + settings.json emission examples per scope, showing how Project-scope emission can silently grant the team all of one user's personal allows (R12 made tangible), and recommending a "denies + asks only" default emission for Project scope. (3) §5.8 First 30 minutes — a narrative walkthrough of a brand-new user's experience from minute 0 to minute 30 post-Phase A+B, including the dashboard's Health tab "Test a tool call" interaction explaining why the user's git push is being asked when they thought they'd allowed it. This narrative is the acceptance test for the proposed design.
