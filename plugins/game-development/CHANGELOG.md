# Changelog — game-development

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Code-runtime value-add build-out. PR #315 added the consolidated production/design/live-ops decision-trees + `best-practices/` + `templates/`; this build-out adds the net-new gap — a scenarios bank, the runtime/engineering tier, and complementary trees. Every value-add menu item was dispositioned (built or recorded N-A with a researched reason); see [`CLAUDE.md`](CLAUDE.md) §10 "Value-add completeness".

### Added

- **scenarios/ bank (4 runtime field notes).** `frame-time-gc-hitch` (read the percentile, not the average; a periodic hitch is a GC/allocation problem, not a GPU one), `draw-call-batching-perf` (a CPU-bound frame with an idle GPU → batch via atlases/instancing, don't cut poly/texture), `netcode-lag-rollback` (pick the netcode model from the genre's felt metric; a buffer is not a substitute for rollback), `save-system-migration` (version + migration-chain a persisted save; never deserialize an old save into a new structure). README + the marketplace 9-field schema.
- **2 new Mermaid decision-tree knowledge files.** `knowledge/gamedev-runtime-performance-decision-trees.md` — frame-over-budget (CPU-vs-GPU split, GC hitch, draw-call batching, fill/vertex bound) + memory-budget trees, with the FPS→ms-budget arithmetic. `knowledge/gamedev-architecture-and-networking-decision-trees.md` — engine selection (known-engine-first; Unity/Unreal/Godot leans), ECS-vs-OOP (prove the bottleneck first), and the networking-model tree (rollback / server-authoritative / lockstep / state-sync by felt metric). Complements #315's production/design/live-ops trees.
- **LSP code-intelligence config.** `.lsp.json` (referenced from `plugin.json` `lspServers`) configuring a C# (Roslyn-backed, stdio) language server — the broadest game-scripting language with a clean standalone stdio LSP (Unity, Godot-C#). Ships the config, not the binary; loud-but-non-fatal if missing.
- **Runnable calculator.** `scripts/gamedev_budget.py` (stdlib only, Python 3.9+, `ruff`-clean): `frame-budget` (FPS→ms budget + verdict + headroom), `cpu-gpu` (which side bounds the frame), `memory-budget` (total vs budget + dominant category). A calculator, not a data source — pairs with the runtime-performance trees.
- **CLAUDE.md** §5 (knowledge + scenario banks), §8 (scenarios + script), §9 (LSP + recommend-not-bundle engine MCP), §10 (value-add completeness), §11 (milestones).

### Decisions (recorded, not built)

- **No bundled MCP server.** Every game-engine MCP (Unity MCP — CoplayDev `unity-mcp` / CoderGamester `mcp-unity`; `godot-mcp`; Unreal MCP — `chongdashu`/`ChiR24`) is a **write-capable, per-project editor bridge that needs a running engine** → fails the doctrine's zero-config + read-only bar. Documented the real, researched recommend-not-bundle paths (each gated through `security-reviewer`) instead of shipping an `mcpServers` entry. No server invented.
- **GDScript LSP not shipped in `.lsp.json`.** Godot's GDScript LSP is **editor-bound and served over TCP** (needs a running/`--headless` editor on a port), not a standalone stdio binary, so it doesn't fit the `command + --stdio` shape without a community TCP↔stdio bridge. Documented as recommend/N-A rather than shipped as a broken entry. Unreal C++ (`clangd` + a per-project `compile_commands.json`) is likewise consumer-build-specific → recommend, not bundle.
- **No `bin/`, monitors, output-styles, settings, or themes** — none cleared the "groundable + broadly valuable, zero-config, doesn't duplicate an existing surface" bar. The calculator covers the one real runtime-script need; a build-status monitor would need a per-consumer CI endpoint.
- **Skills/commands/templates/hooks coverage held sufficient** — #315's surface plus the new trees + scenarios + calculator extend reach without a new agent (team-growth-as-knowledge house rule).

### Verify-at-use

- The C# Roslyn LSP standalone binary/package name (the Roslyn `Microsoft.CodeAnalysis.LanguageServer` isn't published as a clean standalone stdio binary — consumers use a maintained wrapper that downloads + proxies it over stdio); the GDScript LSP transport (editor-bound TCP) and the TCP↔stdio bridge option; engine licensing/royalty/pricing terms (Unity/Unreal/Godot) and engine-native ECS/networking feature availability; the Unity/Godot/Unreal MCP package names + licenses; engine profiler/tool names (Unity Profiler/Frame Debugger, Unreal Insights/RenderDoc, Godot profiler) and the per-engine term for "draw calls". All version-volatile — re-confirm against the vendor before quoting.

### Sources (retrieved 2026-06-05)

- Claude Code plugins reference — `.lsp.json` / `lspServers` format (`command` + `extensionToLanguage` required; `transport` defaults to `stdio`, `socket` supported); monitors component. https://code.claude.com/docs/en/plugins-reference
- C# / Roslyn LSP: dotnet/roslyn issue #71474 (Microsoft.CodeAnalysis.LanguageServer not a standalone server), SofusA/csharp-language-server (stdio wrapper), OmniSharp.
- GDScript LSP (editor-bound TCP, `--headless`/`--lsp-port`): Godot forum + godot-vscode-plugin + opencode-godot-lsp bridge.
- Engine MCP servers: CoplayDev/unity-mcp, CoderGamester/mcp-unity, Coding-Solo/godot-mcp, chongdashu + ChiR24 Unreal MCP.

## [0.1.x] — earlier

Consolidated knowledge decision-trees (Mermaid D1-retention / feature-feasibility / monetization-model), `best-practices/` (20 named rules), `templates/` (PR #315).

## [0.1.0] — initial

4-agent game-development team (gamedev-producer, game-designer, gameplay-engineer, live-ops-analyst): 5 skills, 3 templates, 5 commands, 1 advisory hook, a 4-file research-grounded knowledge bank, 8 best-practice rules. A production-and-design team that scopes to a vertical slice, designs retaining loops/economies, runs production on milestones + risk burn-down, and reads live-ops.
