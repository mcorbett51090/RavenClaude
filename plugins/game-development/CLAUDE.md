# Game Development Plugin — Team Constitution

> Team constitution for the `game-development` Claude Code plugin. Bundles **4** specialist agents anchored on game production, design, and live-ops — vertical-explicit but segment-flexible (indie | mobile/F2P | premium | live-service | studio).
>
> Designed for a producer, designer, or studio lead accountable for shipping and operating a game on a budget — assumes the user owns a production or live-ops number, not a generic 'how to make games' tutorial.
>
> **Orientation:** this file is **domain-specific** to game development. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`gamedev-producer`](agents/gamedev-producer.md) | The engagement — scoping the project, framing the milestone plan, routing, and synthesizing a production plan. | "Will we ship on budget?"; "frame the milestone plan"; first contact |
| [`game-designer`](agents/game-designer.md) | Design — core loops, the game economy, progression, and the design doc. | "Design the core loop"; "balance the economy"; game design |
| [`gameplay-engineer`](agents/gameplay-engineer.md) | Build feasibility — technical risk, prototyping, content pipelines, and engineering-cost reality, as technical decision-support. | "Is this feature feasible?"; "what's the tech risk?"; engineering feasibility |
| [`live-ops-analyst`](agents/live-ops-analyst.md) | The numbers — retention (D1/D7/D30), monetization (ARPDAU/conversion), the live-service roadmap, and the scorecard. | "Why is retention dropping?"; "read our monetization"; live-ops analytics |

**Team growth ships as skills + knowledge + templates, not as new parallel agents** (marketplace house rule). When a new capability is needed, add a skill or knowledge file the existing 4 can reach — don't fork a fifth agent unless a genuinely new lane appears.

---

## 2. What this team is and is not

**Is:** a production-and-design team for a game studio. It scopes builds, designs loops and economies, plans production, and reads live-ops. It produces deliverables a studio acts on.

**Is not:** a game engine, an LiveOps/analytics platform, or a publishing/legal/store-policy authority. It does not build the game or sign deals and stores no player PII.

---

## 3. House opinions (the team's standing biases)

1. **Prove the fun in a vertical slice before the full build.** A vertical slice that proves the core loop is the cheapest way to de-risk a game; scaling content before the loop is fun is how studios build expensive games nobody plays. [unverified — training knowledge]
2. **The core loop is the product — design it before the features.** Retention lives in the second-to-second and session-to-session loop; features layered on a weak loop don't save it. Design the loop, then the meta.
3. **Scope is the enemy — burn down risk, not just tasks.** Most game projects fail on scope, not talent; production tracks the riskiest unknowns (fun, tech, content cost) to burn down first, not just a task list.
4. **Retention before monetization — D1/D7/D30 are the vital signs.** A game that doesn't retain can't monetize; early retention (D1/D7/D30) is the first gate, and monetization design follows a retaining loop, not the other way around.
5. **Design the economy as a system, not a price list.** Sources, sinks, and progression pacing make or break a game economy; an economy balanced by intuition inflates or starves and breaks retention.
6. **Content cost-per-hour is a real constraint — budget it.** Player-hours of content carry a production cost; a campaign or live-service roadmap that ignores content cost-per-hour overruns the budget.
7. **Live-service is an operating model, not a launch.** A live game is a content-and-events cadence with a team and a roadmap after ship; treating launch as the finish line strands the game.
8. **Date and source any benchmark or market figure.** Retention, ARPDAU, and market figures vary hugely by genre and platform; mark a figure `[unverified — training knowledge]` or `[ESTIMATE]` unless cited and dated.

---

## 4. Anti-patterns the team flags

- Violating §3 #1 — prove the fun in a vertical slice before the full build.
- Violating §3 #2 — the core loop is the product — design it before the features.
- Violating §3 #3 — scope is the enemy — burn down risk, not just tasks.
- Violating §3 #4 — retention before monetization — D1/D7/D30 are the vital signs.
- Violating §3 #5 — design the economy as a system, not a price list.
- Violating §3 #6 — content cost-per-hour is a real constraint — budget it.
- Violating §3 #7 — live-service is an operating model, not a launch.
- Violating §3 #8 — date and source any benchmark or market figure.
- An external market / competitor / benchmark number with no source URL + date.
- A recommendation with no owner, no date, and no expected metric movement.

---

## 5. Knowledge bank

The research-grounded reference the agents point to. Read the relevant file in full when the situation matches.

| File | Covers |
|---|---|
| [`knowledge/gamedev-kpi-glossary.md`](knowledge/gamedev-kpi-glossary.md) | Game-development KPI glossary |
| [`knowledge/gamedev-production-economics.md`](knowledge/gamedev-production-economics.md) | Game production economics |
| [`knowledge/gamedev-market-context.md`](knowledge/gamedev-market-context.md) | Game retention benchmarks & market context (2025) |
| [`knowledge/gamedev-decision-trees.md`](knowledge/gamedev-decision-trees.md) | Game-development decision trees (production / design / live-ops; **Mermaid** D1-retention, feature-feasibility, monetization-model) |
| [`knowledge/gamedev-runtime-performance-decision-trees.md`](knowledge/gamedev-runtime-performance-decision-trees.md) | **Mermaid** — runtime/engineering lane: frame-over-budget (CPU-vs-GPU split, GC hitch, draw-call batching) + memory-budget trees, with the FPS→ms-budget arithmetic |
| [`knowledge/gamedev-architecture-and-networking-decision-trees.md`](knowledge/gamedev-architecture-and-networking-decision-trees.md) | **Mermaid** — expensive-to-reverse choices: engine selection, ECS-vs-OOP runtime architecture, and the networking-model tree (rollback / server-authoritative / lockstep by felt metric) |

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)): the **canonical knowledge** above (high trust, follow without disclaimer — traverse the relevant Mermaid tree top-to-bottom before choosing) and the **scenarios bank** (low/medium trust, surface with the mandatory unverified preamble) — [`scenarios/`](scenarios/), runtime field notes (frame-time GC hitch, draw-call batching, netcode lag/rollback, save-system migration). Scenarios are a secondary source; they never replace the knowledge bank or a measured profile of the actual game.

---

## 6. Output Contract

Every agent ends a substantive deliverable with this block:

```
**Deliverable:** <what this is>
**Segment:** <indie | mobile/F2P | premium | live-service | studio>
**Metrics cited:** <metric — value — window — baseline> (one per line; §3 #1)
**Assumptions / data gaps:** <what to validate against the client's actual data>
**Recommended next actions:** <item — owner — date — expected movement>
**Sources:** <URL — retrieval date> for every external number (§3 cite-or-mark rule)
```

## 7. Structured Output Protocol (required)

After the Markdown report, emit the cross-plugin Structured Output Protocol JSON block (see [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)):

```
---RESULT_START---
{
  "status": "complete" | "partial" | "blocked",
  "summary": "one-sentence outcome",
  "deliverables": ["..."],
  "handoff_recommendation": {"to_specialist": "<agent name or null>", "reason": "..."},
  "confidence": 0.0,
  "risks_or_open_questions": ["..."],
  "next_actions": [{"item": "...", "owner": "...", "date": "YYYY-MM-DD", "expected_movement": "..."}],
  "metrics_cited": [{"metric": "...", "value": "...", "window": "...", "baseline": "..."}]
}
---RESULT_END---
```

The lead is [`gamedev-producer`](agents/gamedev-producer.md) — first contact for any new problem; it scopes and routes to the right specialist.

---

## 8. Scenarios bank & runnable tooling (added v0.2.0)

- **Scenarios bank** — [`scenarios/`](scenarios/) holds dated, scope-tagged, unverified engineering narratives (the marketplace scenarios pattern; see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)). Surface a matching scenario only as a *secondary* source, behind the mandatory unverified-scenario preamble, never overriding the cited knowledge bank or a measured profile (§3 #8). Scenarios carry no studio/player PII (§2). The most-likely-to-benefit specialist is [`gameplay-engineer`](agents/gameplay-engineer.md) (frame-time, draw-call, netcode, save-migration narratives); the lead and `live-ops-analyst` check the bank when a situation matches.
- **Runnable calculator** — [`scripts/gamedev_budget.py`](scripts/gamedev_budget.py) (stdlib only, Python 3.9+) removes arithmetic error from three recurring runtime decisions: `frame-budget` (FPS→ms budget + under/at-risk/over-budget verdict with headroom), `cpu-gpu` (which side bounds the frame, quantifying "is the GPU idle?"), `memory-budget` (total vs budget + dominant category + per-category share). It is a **calculator, not a data source** — the user supplies every input; outputs are decision-support, never a profile of the actual game (§3 #8). Pairs with the runtime-performance decision trees; owned primarily by `gameplay-engineer`.

## 9. Technical-runtime tier — LSP code intelligence + recommended (not bundled) MCP

Game development is a **code** domain, so the plugin ships runtime-tier wiring — but with an honest accounting of what the engine ecosystem actually supports.

### 9a. LSP — bundled C# config (binary installed separately)

The plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence — go-to-definition, find-references, diagnostics — for the game-scripting language where a clean stdio LSP exists. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section, 2026-06-05): a `.lsp.json` entry needs `command` + `extensionToLanguage`; `transport` defaults to `stdio` (a `socket` transport is also supported).

| Language | Server | `command` | Install (consumer, separate) `[verify-at-use]` |
|---|---|---|---|
| C# (Unity / Godot-C# / general) | Roslyn-backed C# language server | `csharp-language-server --stdio` | `dotnet tool install --global csharp-ls` **or** the maintained Roslyn wrapper — re-confirm the current package/binary name at use |

**Why only C#:** C# is the broadest game-scripting language (Unity, Godot's C# path) **and** has a maintained LSP that proxies the Roslyn server over **stdio** — the transport `.lsp.json` expects. **GDScript is deliberately NOT in `.lsp.json`:** Godot's GDScript LSP is **built into the Godot editor and served over TCP**, requiring a running (or `--headless`) editor instance on a port — it is not a standalone stdio binary, so it doesn't fit the `command + --stdio` shape without a community TCP↔stdio bridge (e.g. `opencode-godot-lsp`). Bundling a config that needs a running engine + a bridge would fail loudly for most consumers; we document the reality instead of shipping a broken entry `[verify-at-use — GDScript LSP transport]`. **Unreal C++** is served by `clangd` against a generated `compile_commands.json` — genuinely useful but consumer-build-specific (the compile DB is per-project), so it's a `claude mcp`/manual-config recommendation, not a bundle.

**The plugin ships the *config*, not the *binary*.** If the C# server binary isn't on `PATH`, it shows `Executable not found in $PATH` in the `/plugin` Errors tab and C# intelligence degrades — Claude Code and every other tool keep working (loud-but-non-fatal). The exact package/binary name for the C# Roslyn LSP is **version-volatile** `[verify-at-use]` — the Roslyn `Microsoft.CodeAnalysis.LanguageServer` is not published as a clean standalone stdio binary (it's designed to pair with an editor extension and ships inside the C# Dev Kit), so consumers use a maintained community wrapper that downloads + proxies it over stdio; re-confirm the current wrapper's binary name before quoting it.

### 9b. Recommended (not bundled) MCP servers — engine editor bridges

This plugin **bundles no MCP server**, on purpose. Per [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**. Every game-engine MCP server is the opposite: an **editor bridge** that requires a **running engine instance**, is **per-project**, and is **write-capable** (it creates/edits assets, scenes, scripts, Blueprints). All three disqualify bundling — so we document the recommend-not-bundle paths instead of shipping an `mcpServers` entry. These are **real, researched servers — not invented**:

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Unity MCP** (e.g. CoplayDev `unity-mcp`, CoderGamester `mcp-unity`) | Bridges to a **running Unity Editor**; **write-capable** (manage assets, control scenes, edit scripts); needs the Editor open + a per-project package install → fails the zero-config + read-only bar. | Consumer installs the Unity-side package + the MCP server per the project's repo, with the Editor running; gate write verbs through `ravenclaude-core/security-reviewer`. |
| **Godot MCP** (community `godot-mcp`) | Launches/controls the **Godot editor**, runs the project, captures debug output → engine-bound + **write/exec-capable**; per-project. | Consumer-configured against their Godot install; `security-reviewer` sign-off before write/exec verbs. |
| **Unreal MCP** (community, e.g. `chongdashu`/`ChiR24`) | A UE **C++ plugin** exposes editor actions over TCP + a Python MCP server; **write-capable** (actor/Blueprint creation, viewport control); needs the UE plugin built into the project → per-project, write-capable, not zero-config. | Consumer builds the UE plugin into their project + runs the MCP server; `security-reviewer` gate. |

**Why none are bundled (the load-bearing reasoning):** every engine MCP is an editor automation bridge — it cannot operate without a running, per-consumer engine instance, and it mutates the project. The doctrine's decision table sends "per-consumer config OR write-capable" straight to **recommend, don't bundle**, and a write-capable server additionally requires a `security-reviewer` gate before any consumer adopts it. If a genuinely zero-config, read-only, broadly-useful game server ever appears (a read-only asset/manifest inspector, say), revisit with the doctrine block in [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 4. No server was invented to fill the slot.

> Verified 2026-06-05 via web research: Unity MCP (CoplayDev `unity-mcp`, CoderGamester `mcp-unity`), `godot-mcp` (Coding-Solo), and Unreal MCP (`chongdashu`, `ChiR24`) all exist as **editor-bridge, write-capable, per-project** servers; the C# Roslyn LSP standalone-binary nuance + GDScript's editor-bound TCP LSP per the Godot LSP docs / community bridges. Package names, binary names, transports, and licenses are volatile — re-confirm at use before quoting.

## 10. Value-add completeness (build-out 2026-06-05)

PR #315 added the consolidated knowledge decision-trees + `best-practices/` + `templates/`. This build-out adds the net-new gap (scenarios bank + runtime tier + complementary trees). Every value-add menu item is dispositioned honestly below.

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — README + 4 dated, schema-validated runtime field notes (frame-time GC hitch, draw-call/batching perf, netcode lag/rollback, save-system migration), matching the marketplace 9-field schema and the `scenarios/README.md` index. Net-new (the plugin had none). |
| 2 | **NEW decision trees (complementing #315)** | **BUILT** — 2 new Mermaid knowledge files: `gamedev-runtime-performance-decision-trees.md` (frame-over-budget CPU-vs-GPU/GC/draw-call + memory-budget) and `gamedev-architecture-and-networking-decision-trees.md` (engine selection + ECS-vs-OOP + networking-model). Chosen because #315's trees were production/design/live-ops (D1-retention, feature-feasibility, monetization-model) — the runtime/engineering and expensive-to-reverse-architecture lanes were the gaps. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §9b. Every engine MCP (Unity / Godot / Unreal) is a **write-capable, per-project editor bridge needing a running engine** → fails the zero-config + read-only bar. Documented the real, researched recommend-not-bundle servers with a `security-reviewer` gate. No server invented. |
| 4 | **LSP server** | **BUILT (C# only) + honest N-A for the rest** — `.lsp.json` ships a C# (Roslyn-backed, stdio) entry, the one game-scripting language with a clean standalone stdio LSP. GDScript (editor-bound TCP) and Unreal C++ (`clangd` + per-project compile DB) are documented recommend/N-A in §9a, not shipped as broken entries. |
| 5 | **Runnable script** | **BUILT** — `scripts/gamedev_budget.py` (stdlib, Python 3.9+, `ruff`-clean): `frame-budget` / `cpu-gpu` / `memory-budget`. Real runtime value — pairs with the runtime-performance trees, removes arithmetic error from the FPS→ms-budget and memory-budget decisions. Calculator, not a data source (§9a/§3 #8). |
| 6 | **bin/ · monitors · output-styles · settings · themes** | **N-A** — no groundable, broadly-valuable, zero-config instance. A "build-status" monitor would need a per-consumer CI endpoint (not zero-config); output-styles/themes overlap the §6 Output Contract; the calculator covers the one real runtime-script need. The advisory hook already covers anti-pattern flagging. |
| 7 | **skills / hooks / commands / templates** | **Coverage sufficient** — #315 already shipped 5 skills, 5 commands, 4 templates (`engagement-brief`, `exec-readout`, `live-ops-event-brief`, `scorecard`), and 1 advisory hook. The new runtime trees + scenarios + calculator extend reach without a new agent (team-growth-as-knowledge house rule); a runtime-perf *skill* would gold-plate the `gameplay-engineer` + the two new trees. No gap this round. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top `0.2.0` entry. No `NOTICE.md` (nothing third-party is bundled — the script is original stdlib-only; all engine/LSP/MCP facts are cited inline, not vendored). |

## 11. Milestones

- **v0.1.0** — initial release: 4 agents, 5 skills, 3 templates, 5 commands, 1 advisory hook, 4-file research-grounded knowledge bank, 8 best-practice rules.
- **v0.1.x** — consolidated knowledge decision-trees (Mermaid D1-retention / feature-feasibility / monetization-model), `best-practices/` (20 rules), `templates/` (PR #315).
- **v0.2.0** — code-runtime value-add build-out: scenarios bank (4 runtime field notes), 2 new Mermaid decision-tree knowledge files (runtime-performance; architecture-and-networking with engine-selection + ECS-vs-OOP + networking-model), `.lsp.json` (C# Roslyn stdio), `scripts/gamedev_budget.py` (frame/CPU-GPU/memory budget), recommend-not-bundle engine-MCP doctrine, CHANGELOG. Engine-MCP + GDScript-LSP dispositioned with researched reasons (§9–§10).
