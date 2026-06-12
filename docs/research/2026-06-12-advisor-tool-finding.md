# Research finding & panel record — Claude advisor tool (2026-06-12)

A focused news-cadence run for the Tier-A `ai_and_claude_tooling` cluster (per [`docs/research-routine-two-cadence.md`](../research-routine-two-cadence.md)). Yesterday's broad sweep ([`2026-06-11-broad-sweep-findings.md`](2026-06-11-broad-sweep-findings.md)) drained the open **corrections** (shipped in PR #413 + #411); this run picks up the **highest-value queued addition** flagged there — the `claude-app-engineering` advisor tool ("a whole tool absent from the bank") — verifies it against the primary, routes it through two expert panels, and builds it.

## The finding

Anthropic shipped a server-side **advisor tool** for the Claude Messages API (beta header `advisor-tool-2026-03-01`, tool `type: advisor_20260301`). A faster/cheaper **executor** model (top-level `model`) consults a higher-intelligence **advisor** model (model inside the tool def) mid-generation for a plan/course-correction — inside one `/v1/messages` request, no client round-trips; the server forwards the full transcript automatically. A routing-ladder / FinOps play: near advisor-solo quality while most tokens generate at executor rates.

## Verification (primary-source, this session)

- **Primary:** [`platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool`](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) — fetched in full (params, billing via `usage.iterations[]`, pairing matrix, six-code error model, streaming/`pause_turn`, caching break-even ~3 calls, `max_tokens` 2048-recommended).
- **Corroboration:** the [advisor-strategy blog post](https://claude.com/blog/the-advisor-strategy) + SDK code samples across 8 languages (curl/CLI/Python/TS/C#/Go/PHP/Ruby) + independent secondary write-ups.
- **Gap confirmed:** `grep -rin advisor plugins/claude-app-engineering/` returned only the plugin's own *advisory hook / advisory agents* — zero coverage of the API tool. Not a duplicate.
- **Fabrication check:** the tool did **not** match training knowledge (cutoff Jan 2026) and the beta header is dated 2026-03 (post-cutoff), so it was treated as suspect until verified. It verifies cleanly against the primary — concern resolved.

## Panel 1 — Usefulness

Three seats (production Claude-agent developer · marketplace knowledge-curator · SMB-consulting-fit skeptic).

> **VERDICT: USEFUL · CONFIDENCE: high**
> Actionable, in-scope routing-ladder/FinOps capability (house opinions #3, #14), a verified zero-duplication gap, groundable against primary + blog + SDK samples, audience-relevant. Beta status is an already-accepted shape in this bank (Memory tool "public beta", Dynamic Workflows "research preview").
> **CONDITION:** ship dated + `[verify-at-use]`-marked, and surface the **platform-availability restriction** (Claude API + Claude Platform on AWS only; NOT Bedrock/Vertex/Foundry) as a prominent first-class caveat so it doesn't produce dead-end recommendations for Bedrock/Vertex-locked clients. **DISSENT: none.**

## Panel 2 — Detailed review

Three seats (technical-correctness · accuracy/citation · editorial-fit).

> **VERDICT: APPROVE-WITH-CHANGES · CONFIDENCE: high**
> Required: (1) error enumeration must not omit `max_uses_exceeded` — list all six codes; (2) bump `marketplace.json` in lockstep with `plugin.json`; (3)+(4) ground the caching break-even and the Sonnet/Haiku cost-framing claims. Nice-to-have: move the full pairing matrix into the dated capability map (house opinion #14) and trim length.

### Disposition of Panel 2's flags

| Flag | Finding | Action |
|---|---|---|
| caching "breaks even at ~3 calls" — *claimed not in source* | **False positive** — the primary doc states verbatim "Caching breaks even at roughly three advisor calls." The panel's excerpt omitted that line. | Kept; attributed ("Anthropic says"). |
| Sonnet-exec/Haiku-exec cost framing — *claimed unsourced* | **False positive** — the primary's "When to use it" section gives exactly this framing. | Kept; attributed to the advisor-tool docs URL. |
| Error list omits `max_uses_exceeded` | **Valid** | Fixed — all six codes now listed in the Reliability paragraph. |
| `marketplace.json` not bumped | **Valid** | Fixed — `plugin.json` + `marketplace.json` both 0.8.0 → 0.9.0. |
| Pairing matrix duplicated / section long | **Valid (nice-to-have)** | Full matrix now lives only in the capability-map row; the knowledge doc states the rule ("advisor must be ≥ executor") and points to it. |

## Tiebreak

**Not triggered** — both panels concurred (USEFUL + APPROVE-WITH-CHANGES). No third panel convened.

## Build (shipped in this PR — `claude-app-engineering` 0.9.0)

- `knowledge/server-side-tools-and-files.md` — new **Advisor tool** section.
- `knowledge/model-selection-and-2026-capability-map.md` — dated capability-status row (pairing matrix + platform restriction).
- `CHANGELOG.md` + `plugin.json` + `marketplace.json` — version lockstep 0.8.0 → 0.9.0.

## Other queued additions — NOT built this run (honest triage)

Still queued from the 2026-06-11 sweep; each needs its own primary re-verification + panel pass and was deliberately left for a later focused run rather than padded into this PR:

- **microsoft-graph** — `agentUser`/`verifiedIdProfile` GA, programmatic FIDO2 passkey registration, `ownerlessGroupPolicy`.
- **microsoft-fabric** — Fabric Graph GA, Copy-job native CDC + Eventstream Kafka/Service Bus connectors, `onelake-security-and-governance.md` pre-GA "preview" cleanup.
- **microsoft-365-copilot** — Fabric Data Agents in Copilot, policy-based agent-lifecycle rules.
- **tableau** — 2026.2 (Agentic Analytics, Hosted Tableau MCP) — `[verify-at-use]`, primary 403'd on the prior sweep.
- **data-platform** — Snowflake Iceberg v3 GA (lower priority for the SMB framing).
- **azure-cloud** — AKS Azure Linux 2.0 retirement framing.

A one-day-later fresh sweep of the remaining Tier-A plugins surfaced **no net-new** beyond the above — expected per the two-cadence doc (most Tier-A plugins are 0-net-new in any given week).
