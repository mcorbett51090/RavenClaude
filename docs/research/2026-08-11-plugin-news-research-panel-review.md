# Plugin news-research + panel review — 2026-08-11

Scheduled routine: research recent news per active plugin, evaluate findings through expert panels, ship a PR for anything that survives. This is the full audit trail; the accompanying PR implements the two verified corrections.

## Scope + method — why this run is *not* a fresh full sweep

The last full **Tier-A weekly news sweep ran 2026-08-08 — 3 days ago** (see [`2026-08-08-plugin-news-research-panel-review.md`](2026-08-08-plugin-news-research-panel-review.md)). The cadence is **weekly** ([`docs/research-routine-two-cadence.md`](../research-routine-two-cadence.md)). Re-running the full ~28-plugin fan-out over a 3-day news window would sweep almost no net-new dated developments and invites exactly the **fabrication pressure** the two-cadence design exists to prevent. The honest, higher-value move: **pick up the two grounded Microsoft-stack findings the 2026-08-08 sweep explicitly logged "for a full re-audit" and never shipped**, re-verify each against a primary source, run them through the panel funnel, and ship what holds.

Both were logged as out-of-window observations on 2026-08-08 (dated developments predating that week's window):

- (A) `microsoft-365-copilot` called **Agent 365** "emerging / deferred until GA," but Microsoft Agent 365 reached GA 2026-05-01.
- (B) `microsoft-fabric` documented Runtime 2.0 as **Delta 4.1**, behind current Learn docs (Delta Lake 4.2).

**Panel funnel** (per the routine): Panel 1 (usefulness, 3 independent seats) → Panel 2 (detailed, source-verified: an accuracy seat + a design/blast-radius seat) → Panel 3 (tiebreak, only on panel-vs-panel disagreement).

## Grounding (orchestrator, before panels)

Both leads were treated as *unverified* until re-checked this session against primary Microsoft Learn sources via the Microsoft-Learn MCP:

- **A — CONFIRMED.** [`microsoft-agent-365/overview`](https://learn.microsoft.com/microsoft-agent-365/overview): *"As of May 1, 2026, Microsoft Agent 365 is generally available for the Commercial segment on a per user basis."* Corroborated by [Partner Center May-2026 announcement](https://learn.microsoft.com/partner-center/announcements/2026-may) (Microsoft 365 E7 + Agent 365 GA, May 1 2026). **Nuance preserved:** the Agent 365 **SDK / external-platform registry-sync** developer surface is still "(preview)" ([`connect-existing-agents`](https://learn.microsoft.com/microsoft-agent-365/connect-existing-agents)) — the control-plane *service* is GA, the dev surface is not fully. The correction must not overstate the SDK as GA.
- **B — CONFIRMED.** [`runtime-2-0`](https://learn.microsoft.com/fabric/data-engineering/runtime-2-0): *"Apache Spark 4.1 … Python: 3.13 … Delta Lake: 4.2."* [Runtime comparison table](https://learn.microsoft.com/fabric/data-engineering/runtime): *"Delta Lake version | 3.2 | 4.2"* (Runtime 1.3 vs 2.0). Runtime 2.0 remains **public preview** (lifecycle table; GA runtime is still 1.3). The old "Delta 4.1" is simply stale.

## Funnel at a glance

| Stage | Finding A (Agent 365 GA) | Finding B (Fabric Delta 4.2) |
|---|---|---|
| Orchestrator grounding | CONFIRMED (primary) | CONFIRMED (primary) |
| Panel 1 — usefulness (3 seats) | USEFUL ×3 (0.90 / 0.85 / 0.90) | USEFUL ×2 (0.85 / 0.80) · **CHURN ×1 (0.80)** |
| Panel 2 — accuracy (source-verified) | CONFIRMED, no overstatement | CONFIRMED, no overstatement |
| Panel 2 — blast-radius | IMPLEMENT (scoped fan-out) | IMPLEMENT (scoped) |
| Panel 3 — tiebreak | not required (panels agree) | not required (panels agree) |
| **Shipped** | **Yes** (0.5.4 → 0.5.5) | **Yes** (0.8.7 → 0.8.8) |

## Panel detail

### Finding A — `microsoft-365-copilot`: Agent 365 "emerging/deferred until GA" is now false

- **Panel 1 (usefulness):** unanimous USEFUL. Seat A (0.90): the file's own `[verify-at-build]` trigger fired; "emerging/deferred" is flatly false against a primary GA date. Seat B (0.85): telling a consultant a GA governance control plane is still "emerging" makes them skip adopting something deployable now — it changes what they do. Seat C (0.90): "emerging" actively misleads on a claim a reader repeats to a client; the fix must preserve the still-preview SDK nuance rather than flip everything to GA.
- **Panel 2 (accuracy):** CONFIRMED — GA 2026-05-01 (primary quote + Partner Center corroboration); SDK/registry-sync correctly hedged as preview; "partly still preview" framing does not overstate.
- **Panel 2 (blast-radius):** IMPLEMENT with scoped fan-out (below). Key judgment: the fired "deferred until GA" trigger for a **new `agent-365-engineer` agent** is a **product decision for the human maintainer** — record that the trigger fired; do **not** autonomously build the agent. Edit `CLAUDE.md:22` (factual-consistency fix) but leave `CLAUDE.md:128` (a table description with no factual claim).

### Finding B — `microsoft-fabric`: Runtime 2.0 Delta 4.1 → 4.2

- **Panel 1 (usefulness):** 2 USEFUL, 1 CHURN. Seats A (0.85) and C (0.80): a precise, quotable spec on a client-facing capability map is exactly where a wrong version gets repeated; triple-corroborated on primary Learn pages. Seat B (0.80, **dissent**): Delta 4.1→4.2 on a still-preview, non-default runtime moves a bundled-component digit nobody pins production to today — churn.
- **Panel 2 (accuracy):** CONFIRMED — Delta Lake 4.2 (three authoritative Learn pages agree); Runtime 2.0 still public preview; no overstatement.
- **Panel 2 (blast-radius):** IMPLEMENT. Edit `fabric-2026-capability-map.md:5` (header clause) and `:13` (table row + inline note); re-date the Delta portion's "re-verified 2026-06-11" stamp (preserve the OneLake-security stamp on the same clause). Leave `medallion-on-onelake.md:55` (Spark-only, no Delta digit).
- **Orchestrator adjudication of the dissent:** no panel-vs-panel disagreement occurred (both *panels* say ship), so no Panel 3 tiebreak. The intra-Panel-1 dissent is real and recorded. Deciding factor for shipping: line 5 attached a **dated "re-verified 2026-06-11" stamp to the false "Delta 4.1"** — a dated verification vouching for a wrong number on a file whose stated purpose is client-facing quoting with a retrieval date. Correcting a misleading dated stamp is a correctness fix, not churn. The fix is cheap, low-risk, and keeps "public preview" intact (avoiding a second error).

## Shipped edits

**A — `microsoft-365-copilot` (0.5.4 → 0.5.5):**
- `knowledge/copilot-admin-governance-2026.md` — "Agent 365 (track, don't over-invest)" section records the control-plane **service GA (2026-05-01)** with citations; SDK/registry-sync kept `[verify-at-build]` (preview); confidence note split; fired refresh trigger replaced with the remaining "SDK/registry-sync reaches GA" trigger.
- `knowledge/agent-platform-decision-2026.md` + `knowledge/agents-sdk-and-toolkit-2026.md` — `agent-365-engineer` re-eval triggers re-pointed to the still-preview SDK/registry-sync GA (service GA noted inline).
- `CLAUDE.md:22` — deferral note records the GA trigger fired 2026-05-01 and that the agent is a **pending maintainer decision, not yet built**. `:128` left unchanged.
- Lockstep version bump (`plugin.json` + `marketplace.json`) + CHANGELOG top entry.

**B — `microsoft-fabric` (0.8.7 → 0.8.8):**
- `knowledge/fabric-2026-capability-map.md:5` + `:13` — Delta 4.1 → 4.2 (header clause, table cell, inline "Delta 4.0→4.2" note); Delta portion's re-verification stamp re-dated 2026-08-11 with Runtime-2.0 + comparison-table citations; OneLake-security 2026-06-11 stamp preserved; `medallion-on-onelake.md:55` left unchanged.
- Lockstep version bump (`plugin.json` + `marketplace.json`) + CHANGELOG top entry.

## Autonomous-boundary note

The Finding-A GA trigger technically authorizes a new `microsoft-365-copilot` agent (`agent-365-engineer`). Creating a new agent is a **product decision**, not a factual correction — outside this routine's remit and left explicitly to the maintainer (recorded in the knowledge files + `CLAUDE.md`). The routine corrected the stale *fact*; it did not build the agent.

## Net result

Of the two deferred Microsoft-stack findings carried over from 2026-08-08, **both** survived fresh grounding + the panel funnel and shipped as corrections: Agent 365 GA (m365-copilot 0.5.5) and Fabric Runtime 2.0 Delta 4.2 (microsoft-fabric 0.8.8). Consistent with the routine's base rate (2026-08-08: 1 shipped; 2026-07-22: 2; 2026-07-13: 1). No fresh full Tier-A sweep was run — the 3-day window did not warrant one, and chasing it would have manufactured noise rather than signal.
