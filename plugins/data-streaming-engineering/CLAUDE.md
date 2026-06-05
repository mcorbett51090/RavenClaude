# Data Streaming Engineering Plugin — Team Constitution

> Team constitution for the `data-streaming-engineering` Claude Code plugin — **3** specialist agents for real-time data infrastructure done right — event streaming and CDC (Kafka/Pulsar/Kinesis), stream processing with correct time/windowing/state, and delivery semantics (exactly-once vs at-least-once) — distinct from data-platform's batch ELT. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`streaming-architect`](agents/streaming-architect.md) | Streaming architecture: the streaming-vs-batch decision, the topology (sources/topics/processors/sinks), the platform choice (Kafka/Pulsar/Kinesis), delivery-semantics strategy, and the CDC approach | "do we need streaming or is batch fine?", "design our event streaming topology", "Kafka or Kinesis?", "how should we do CDC?" |
| [`kafka-pipeline-engineer`](agents/kafka-pipeline-engineer.md) | The streaming platform and ingestion: topic/partition design, keys and ordering, the schema registry + compatibility/evolution, producers/consumers and consumer groups, CDC (Debezium) pipelines, and connector configuration | "design our Kafka topics", "our schema change broke consumers", "set up CDC from Postgres", "how should we partition this?" |
| [`stream-processing-engineer`](agents/stream-processing-engineer.md) | Stream processing: event-time vs processing-time, windowing (tumbling/sliding/session), watermarks and late data, stateful processing + checkpointing, stream-stream and stream-table joins, and backpressure handling (Flink / Kafka Streams) | "our windowed aggregation is wrong", "handle late-arriving events", "join two streams", "our processor is falling behind" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Stream only when latency demands it.** Real-time infra is operationally heavy. If the business need is hourly/daily, batch ELT (data-platform) is simpler and cheaper. Streaming is for genuine low-latency needs, not fashion.
2. **Event-time, not processing-time, for correctness.** Events arrive late and out of order. Window and aggregate on the event's own timestamp with watermarks — processing-time aggregations are wrong the moment the network hiccups.
3. **Pick the delivery semantic deliberately.** At-least-once + idempotent consumers is the pragmatic default; exactly-once costs throughput and complexity and is only truly end-to-end with transactional sinks. Name what you need.
4. **Partition for parallelism and ordering — they conflict.** Order is per-partition only. Choose the partition key for the ordering guarantee you need; over-partitioning kills order, under-partitioning kills throughput.
5. **Schemas evolve; govern them.** A schema registry with compatibility rules (backward/forward) keeps a producer change from breaking every consumer. An unversioned event payload is a future outage.
6. **State and backpressure are first-class.** Stream processors hold state (checkpoint it) and must handle backpressure (a fast producer + slow consumer = unbounded lag or OOM). Design both, don't discover them.

## 3. Seams (the bridges to neighbouring plugins)

- **Batch ELT, warehouse loading, and scheduled pipelines** → `data-platform`; this team owns real-time/streaming, that one owns batch. The litmus: sub-minute latency need → here; hourly/daily → there.
- **The transform layer (dbt) consuming streamed data once landed** → `analytics-engineering`.
- **Event/AsyncAPI contracts for the streams** → `api-engineering` (AsyncAPI); we own the transport + processing.
- **Microsoft Fabric Real-Time Intelligence (Eventstream/Eventhouse/KQL)** → `microsoft-fabric` (the Microsoft-native streaming lane).
- **App-side messaging/queues and the outbox in service code** → `backend-engineering`; we own the streaming platform and CDC.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/data-streaming-engineering-decision-trees.md`](knowledge/data-streaming-engineering-decision-trees.md) — ten `## Decision Tree:` Mermaid graphs (streaming-vs-batch, delivery-semantics, windowing, schema-compatibility, replay/recovery, CDC-connector-failure, Kafka-platform-selection, stream-stream-join, **backpressure-vs-skew-vs-under-provisioning**, **stateful-recovery sizing**) + a dated capability map. **Traverse the relevant tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — five field notes (consumer-lag/rebalance storm, exactly-once redesign, schema-evolution break, out-of-order/watermark/late-data, partition-skew/hot-key). Secondary source; never replaces the knowledge bank. The most-likely-to-benefit specialists — `kafka-pipeline-engineer`, `stream-processing-engineer` — should check the bank when a situation matches.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binary installed separately)

Stream processing is a **code** domain (Flink / Kafka Streams jobs, producers/consumers, connector and schema definitions), so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence — go-to-definition, find-references, diagnostics — instead of grep-and-guess. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section) and the jdtls LSP plugin (2026-06-05); LSP support landed in Claude Code 2.0.74 `[verify-at-use]`.

It configures three language servers covering this domain's common languages:

| Language | Server | `command` | Install (consumer, separate) `[verify-at-use]` |
|---|---|---|---|
| Java | Eclipse JDT.LS (jdtls) | `jdtls` | `brew install jdtls` (needs JDK 17+/21+) — Flink / Kafka Streams jobs |
| Python | Pyright | `pyright-langserver --stdio` | `pip install pyright` **or** `npm install -g pyright` — PyFlink / confluent-kafka-python |
| TypeScript/JS | typescript-language-server | `typescript-language-server --stdio` | `npm install -g typescript-language-server typescript` — KafkaJS |

**The plugin ships the *config*, not the *binary*.** Per the plugins reference: "LSP plugins configure how Claude Code connects to a language server, but they don't include the server itself." If a server's binary isn't on `PATH`, it shows `Executable not found in $PATH` in the `/plugin` Errors tab and that one language degrades — Claude Code and all other tools keep working (the same **loud-but-non-fatal** posture as a missing MCP prerequisite). LSP servers start only after the workspace is trusted; `/reload-plugins` picks up a config change mid-session. Package names, the install paths, and the 2.0.74 LSP-support version are version-volatile — re-confirm at use.

## 7. Recommended (not bundled) MCP server — Confluent / Kafka

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a write-capable or per-consumer-configured server is **recommend-not-bundle**. The streaming-useful servers all fail the bar.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Confluent MCP** ([`@confluentinc/mcp-confluent`](https://github.com/confluentinc/mcp-confluent), MIT, first-party) | **Per-tenant + authenticated** (Confluent Cloud / Kafka API keys + secrets + bootstrap-server URLs; or OAuth-PKCE) — can't hardcode a consumer-specific cluster/secret — **and write-capable** (create/delete topics, produce messages, deploy Flink SQL, manage connectors). Both disqualify bundling; the write path is an Absolute-rule `security-reviewer` gate. | `npx -y @confluentinc/mcp-confluent@<pinned> --init-config` (or `--init-oauth-config`); secrets as **references** (env-var names / vault), never literals; `security-reviewer` sign-off before the write verbs are enabled. |

**Why none are bundled (the load-bearing reasoning):** the official Confluent server is the obvious candidate and is MIT/first-party, but it needs a consumer-specific cluster + credentials *and* carries write verbs — the rule's decision table sends "per-consumer config OR write-capable" to **recommend, don't bundle**, and the credential handling is an Absolute-rule "reference-not-literal" + `security-reviewer` situation. No zero-config, read-only, broadly-useful streaming server was found to exist (the Apache first-party **KIP-1318** MCP server is still a proposal as of 2026-06; community Go/Python Kafka servers are still per-cluster-configured). If a genuinely zero-config read-only server appears, revisit with the doctrine block in [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 4.

> Verified 2026-06-05 against the [confluentinc/mcp-confluent](https://github.com/confluentinc/mcp-confluent) repo: package `@confluentinc/mcp-confluent`, MIT, static-API-key or OAuth-PKCE auth, read **and** write tools (topics / produce / consume / Flink SQL / connectors). Package name, license, auth modes, and the tool surface are volatile — re-confirm at adoption.

## 8. Runnable sizing tool

[`scripts/stream_sizing.py`](scripts/stream_sizing.py) (stdlib only, Python 3.8+, `ruff`-clean) removes arithmetic error from three recurring sizing decisions: `partitions` (minimum partition/parallelism count for a throughput target + a hot-key skew warning), `poll-budget` (does a consumer's per-poll work fit inside `max.poll.interval.ms`? — the rebalance-storm guard), and `watermark` (translate an observed event-time lateness distribution into a watermark bound + allowed-lateness grace). It is a **calculator, not a data source** — the user supplies every input; outputs are decision-support, not a provisioning guarantee. Owned primarily by `kafka-pipeline-engineer` (partitions/poll-budget) and `stream-processing-engineer` (watermark).

## Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason):

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — completed the bank to 5 scenarios (exactly-once redesign, schema-evolution break, out-of-order/watermark/late-data, partition-skew/hot-key) joining the pre-existing consumer-lag/rebalance storm. Matches the `scenarios/README.md` index + 9-field schema. |
| 2 | **Decision-tree knowledge** | **BUILT** — 2 NEW `## Decision Tree:` sections added to the knowledge file (backpressure-vs-skew-vs-under-provisioning; stateful-recovery sizing), complementing #315's existing eight — chosen because they were the gaps and they ground the new scenarios + the runtime tier. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §7. The official Confluent MCP (`@confluentinc/mcp-confluent`, MIT) is per-tenant + authenticated + write-capable; no zero-config read-only streaming server exists to bundle. Documented the `claude mcp add`/`npx` path with a `security-reviewer` gate. No invented servers. |
| 4 | **LSP server** | **BUILT** — `.lsp.json` (jdtls / pyright / typescript-language-server) wired via `plugin.json` `lspServers`. Genuinely useful for a code domain (Flink/Kafka-Streams Java, PyFlink, KafkaJS); binaries install separately (§6). |
| 5 | **Runnable script (`scripts/`)** | **BUILT** — `stream_sizing.py` (partitions / poll-budget / watermark). The one runtime item with real, groundable streaming value; ties directly to the sizing best-practices and the lag/skew/late-data scenarios. |
| 6 | **bin/ executables / monitors / output-styles / settings / themes** | **N-A** — none clears the "groundable + broadly valuable, doesn't duplicate an existing surface" bar. The single stdlib `scripts/stream_sizing.py` covers the calculator need; there is no build/long-running process to monitor and no streaming-specific tool-permission surface beyond `ravenclaude-core`. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 7 skills, 4 commands, 4 templates, 1 advisory antipattern hook already cover platform/CDC/schema-evolution/stream-processing/lag-triage/streaming-vs-batch. The new trees + script + scenarios extend reach without a new agent (team-growth-as-knowledge house rule). |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top `0.3.0` entry. No `NOTICE.md` (nothing third-party is bundled — the script is original stdlib-only; the Confluent server is referenced, not vendored). |

## Milestones

- **v0.2.x** — 3-agent streaming team: 7 skills, 8-tree decision-tree knowledge bank + dated capability map, best-practices, 4 templates, 4 commands, 1 advisory hook, first scenario.
- **v0.3.0** — value-add build-out: scenarios bank completed (5 scenarios), 2 new Mermaid decision trees, `scripts/stream_sizing.py` (3 modes), `.lsp.json` (jdtls/pyright/typescript-language-server), CHANGELOG. MCP dispositioned recommend-not-bundle (Confluent); bin/monitors/output-styles/themes dispositioned N-A with reasons.
