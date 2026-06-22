# Changelog — data-streaming-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.1] — 2026-06-22

Weekly news-cadence sweep correction (Tier-A, `data_and_bi`). See [`docs/research/2026-06-22-weekly-sweep-findings.md`](../../../docs/research/2026-06-22-weekly-sweep-findings.md).

### Fixed

- **Re-anchored stale framework version stamps in `knowledge/data-streaming-engineering-decision-trees.md`.** The three per-tree "Last verified" lines (stream-stream join; backpressure-vs-skew; stateful-recovery sizing) were stamped against **Apache Flink 1.19 / Kafka Streams 3.7** — two major lines stale. Flink 2.x (current stable 2.2.x) and Kafka 4.x (KRaft-only; Kafka Streams ships within Kafka) are both GA. Re-anchored the version stamps to Flink 2.x / Kafka 4.x with `[verify-at-use]` on exact patch numbers; the documented join/backpressure/checkpoint semantics are version-stable, so only the anchors changed. Top "Last reviewed" bumped to 2026-06-22.

## [0.3.0] — 2026-06-05

Value-add build-out against the full menu, mirroring the `backend-engineering` recipe. Every menu item was dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank completed (5 field notes).** Added the four scenarios the `scenarios/README.md` index already referenced but that did not yet exist on disk: `exactly-once-redesign` (EOS only covers Kafka hops; the non-transactional sink needs an idempotent write), `schema-evolution-break` (a rename/type-change is a new topic + migration, and a `NONE`-mode registry governs nothing — add a CI compatibility check), `out-of-order-watermark-late-data` (size the watermark to p99 lateness + allowedLateness + a side output + an idempotent sink), and `partition-skew-hot-key` (a hot key is a keying problem, not a scaling one). Joins the pre-existing `consumer-lag-rebalance-storm`. All match the 9-field schema.
- **Two NEW decision-tree knowledge sections** in `knowledge/data-streaming-engineering-decision-trees.md`, complementing #315's eight trees (which already cover streaming-vs-batch, delivery-semantics, windowing, schema-compatibility, replay, CDC-failure, Kafka-platform, stream-stream-join): **"A processor is falling behind — backpressure vs. skew vs. under-provisioning?"** and **"Stateful recovery — how do I size and restore operator state?"**. Each is a `## Decision Tree:` Mermaid graph + rationale-per-leaf + a tradeoffs table, dated and `[verify-at-use]`-marked.
- **Runnable sizing tool** — `scripts/stream_sizing.py` (stdlib only, Python 3.8+, `ruff`-clean): three modes — `partitions` (minimum partition/parallelism count for a throughput target + a hot-key skew warning), `poll-budget` (does a poll batch fit inside `max.poll.interval.ms`? — the rebalance-storm guard), and `watermark` (lateness distribution → watermark bound + allowed-lateness grace). A calculator, not a data source; outputs are decision-support.
- **LSP code-intelligence config.** `.lsp.json` (referenced from `plugin.json` `lspServers`) configuring jdtls (Java — Flink / Kafka Streams), Pyright (Python — PyFlink / confluent-kafka-python), and typescript-language-server (TS/JS — KafkaJS). Ships the config, not the binary; binaries install separately (loud-but-non-fatal if missing). Verified against the Claude Code plugins reference + the jdtls LSP plugin (2026-06-05).
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP tier), §7 (recommended-not-bundled MCP servers), §8 (sizing tool), and the value-add completeness disposition table + milestones.

### Decisions (recorded, not built)

- **No bundled MCP server.** The official Confluent MCP server (`@confluentinc/mcp-confluent`, MIT) is **per-tenant + authenticated** (Confluent Cloud / Kafka API keys + bootstrap servers) **and write-capable** (create/delete topics, produce, deploy Flink SQL) — squarely **recommend-not-bundle** per `docs/best-practices/bundled-mcp-servers.md`, with a `security-reviewer` gate on the write path. No zero-config, read-only streaming MCP server was found to exist to bundle (the Apache first-party KIP-1318 server is still a proposal). Documented the recommended `claude mcp add …` path instead of an `mcpServers` entry. No invented servers.
- **No `bin/`, output-styles, monitors, settings defaults, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate an existing surface or a neighbouring plugin" bar.
- **Skills/commands/templates/hooks coverage held sufficient** — 7 skills, 4 commands, 4 templates, 1 advisory hook already cover the surface; the new trees + script + scenarios extend reach without a new agent.

### Verify-at-use

- LSP support landed in Claude Code 2.0.74; the jdtls install path (Homebrew `jdtls`, JDK 17+/21+), the `gopls`-style stdio invocation, and the Pyright/typescript-language-server package names — all version-volatile, re-confirm against the vendor before quoting.
- `@confluentinc/mcp-confluent` package name, license (MIT), auth modes (static API keys / OAuth-PKCE), and the read+write tool surface — confirmed 2026-06-05 against the GitHub repo; re-confirm at adoption.

## [0.2.x] — earlier

3-agent data-streaming-engineering team (streaming-architect, kafka-pipeline-engineer, stream-processing-engineer): 7 skills, a decision-tree knowledge bank (8 Mermaid trees + a dated capability map), best-practices, 4 templates, 4 commands, 1 advisory hook, and the first scenario (consumer-lag-rebalance-storm). Seams to data-platform, api-engineering, microsoft-fabric, backend-engineering.
