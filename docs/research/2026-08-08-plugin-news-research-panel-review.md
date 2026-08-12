# Plugin news-research + panel review — 2026-08-08

Scheduled routine: research recent news per active plugin, evaluate findings through expert panels, ship a PR for anything that survives. This is the full audit trail; the accompanying PR implements only the one verified correctness fix.

## Scope + method

**Tier-A weekly news cadence** (~28 vendor-API-anchored plugins), per [`docs/research-routine-two-cadence.md`](../research-routine-two-cadence.md) and [`.ravenclaude/plugins/sweep-tiers.yaml`](../../.ravenclaude/plugins/sweep-tiers.yaml). The ~150 Tier-B domain-craft verticals are **not** swept for weekly news (chasing weekly deltas there produces fabrication pressure, not signal — the routine's anti-churn mandate). Last full Tier-A sweep: 2026-07-22 (2 findings shipped).

- **Research fan-out (6 parallel grounded-research agents, all Tier-A plugins covered)** by cluster: `ai-claude` (claude-app-engineering, ai-rag-engineering, ml-engineering, ravenclaude-core) · `microsoft` (power-platform, microsoft-fabric, microsoft-365-copilot, microsoft-graph) · `cloud-a` (aws/azure/gcp-cloud, finops-cloud-cost) · `cloud-b` (cloud-native-kubernetes, terraform-iac, devops-cicd, observability-sre, platform-engineering-idp) · `data-bi` (data-platform, data-streaming-engineering, analytics-engineering, database-engineering, tableau) · `security-web` (security-engineering, cybersecurity-grc, auth-identity, web-design, frontend-engineering). Each agent read the plugin knowledge files **and** web-searched (Microsoft-Learn MCP for the MS stack), and was required to **ground every candidate**: quote the exact now-stale text from a real `file:line` + name a real dated (on/after 2026-07-01) development + cite a primary source verified in-session. "The plugin probably says X" was disqualified by construction. The AI model-lineup / capability-map files were excluded (self-maintaining on a separate weekly upstream cadence).
- **Panel funnel:** Panel 1 (usefulness, 3 seats) → Panel 2 (source-verified detailed review, accuracy seat + design/blast-radius seat) → Panel 3 (tiebreak, only on disagreement).
- **Orchestrator verification:** the single survivor's stale quote was re-confirmed against the actual file and its development independently re-checked against the primary source (the npm v12.0.0 GitHub release page) before editing.

Workflow run: `wf_a6ba8ebc-6b8` (8 agents, 0 errors).

## Funnel at a glance

| Stage | Result |
|---|---|
| Plugins researched | ~28 Tier-A (6 parallel grounded-research agents, web-searched) |
| Clusters returning zero findings | 5 of 6 (ai-claude, microsoft, cloud-a, cloud-b, data-bi) |
| Grounded candidate findings | **1** (security-engineering P2) |
| Panel 1 — usefulness | 1/1 advanced (USEFUL, ~0.80) |
| Panel 2 — detailed, source-verified | 1/1 IMPLEMENT (source re-verified true) |
| Panel 3 — tiebreak | not required (no panel disagreement) |
| **Shipped in this PR** | **1 finding, 1 knowledge file (+ lockstep version bump + CHANGELOG)** |

**Why so few:** the accuracy-first / anti-churn discipline working as intended. Five of six clusters found the plugins meticulously hedged (`[verify-at-use]` / `[verify-at-build]`, dated review stamps) and every checkable dated claim accurate as of 2026-08-08. Representative confirmations below (recorded so a later sweep doesn't re-chase).

## Finding + verdicts

### F1 — security-engineering: npm v12 install-script hardening row stale (est.→GA) · **P2 · shipped**

- **Stale text** (`knowledge/security-engineering-decision-trees.md:113`): _"**npm v12 (est. July 2026): install scripts OFF by default** … Warnings today on npm ≥ 11.16.0; preview with `npm approve-scripts --allow-scripts-pending`."_
- **Development:** **npm v12.0.0 shipped GA on 2026-07-08**, flipping the row from an estimated/upcoming change to released reality — and, materially, the approval command the file names (`npm approve-scripts --allow-scripts-pending`) is the **pre-GA preview** path. The GA flow per the release page is `npm install-scripts approve` (record approvals) then `npm rebuild` (execute newly-approved scripts). Primary: [npm v12.0.0 release](https://github.com/npm/cli/releases/tag/v12.0.0) — _"Dependency lifecycle scripts are now blocked by default unless allowed by the root package's `allowScripts` policy"_; _"run `npm install-scripts approve` to record approvals and `npm rebuild` to execute newly approved scripts."_ (Secondary blogs still echoing the preview command are pre-GA changelog framing — the primary release page governs.)
- **Panel 1:** USEFUL (~0.80). A monotonic non-reverting release-status flip (est.→GA) plus a *wrong command* is a durable correctness fix, not churn — a user copying the preview command today would hit a no-op.
- **Panel 2:** IMPLEMENT, source re-verified. Accuracy seat independently re-confirmed the GA date and the corrected command against the release page. Design/blast-radius seat confirmed the same claim appears in `agents/supply-chain-security-engineer.md:46` but is **already** framed as GA-adoptable with no est./preview language → **no fan-out** (editing it would introduce, not remove, inconsistency).
- **Orchestrator note (accuracy discipline):** Panel 2 additionally suggested documenting a `strict-allow-scripts` hard-fail CI knob and a soft-skip default. **Neither could be confirmed against the primary source this session** (the release page did not mention them; the WebFetch of the release page returned only the approval flow), so both were **omitted** rather than written as fact into a claim-grounded file.
- **Shipped edits (single `0.3.6 → 0.3.7` bump):**
  - `knowledge/security-engineering-decision-trees.md:113` — "est. July 2026" → "released 2026-07-08"; preview command replaced with the GA approval flow (`npm install-scripts approve` + `npm rebuild`), with the preview path noted as superseded; citation now leads with the v12.0.0 release page; `[verify-at-build]` retained. Header `Last reviewed` line gains a dated correction parenthetical.
  - `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` security-engineering entry → **0.3.7** (lockstep).
  - `CHANGELOG.md` — top `[0.3.7]` entry.

## Zero-finding cluster confirmations (anti-churn record)

- **ai-claude** — claude-app-engineering files freshly corrected 2026-08-06 (memory-tool GA; Managed Agents headers) and heavily hedged; Advisor tool still public beta (`advisor-tool-2026-03-01`), verified in-session. The new `mid-conversation-tool-changes-2026-07-01` beta is an *addition* (not a contradiction of a stated fact) → not a staleness candidate. ai-rag-engineering pins no versioned third-party facts (all `[unverified — training knowledge]` framing). ml-engineering: Vertex AI→Gemini Enterprise Agent Platform rebrand already reflected (announced 2026-04-22, pre-window). ravenclaude-core CLI-customization facts docs-verified late-July 2026.
- **microsoft** — Fabric Runtime 2.0 still public preview (correct); Runtime 1.3 EOS 2026-09-30 correct + hedged; Fabric CLI v1.5 GA current; M365 Copilot Cowork/Credits GA 2026-06-16 current; federated-MCP GA 2026-06-02 current; Graph FIDO2/agentUser/User.Create GA dates correct + hedged. **Two out-of-window observations flagged for the maintainer** (belong to a full re-audit, not this weekly tier — both predate 2026-07-01 and sit on `[verify-at-build]`-hedged lines): (a) `microsoft-365-copilot` admin-governance calls **Agent 365** "emerging, deferred until GA" but Microsoft Agent 365 reached **GA 2026-05-01** ($15/user/mo standalone); (b) Fabric Runtime 2.0's "Delta 4.0→4.1" is behind current Learn docs (Delta Lake 4.2) — a minor component bump on a still-preview runtime.
- **cloud-a** — AWS Graviton5 M9g/M9gd GA 2026-06-10 current + latest; AWS FinOps Agent still public preview; Azure `Microsoft.FileShares` NFS-only-at-GA still correct; AzureLinux3 AKS default current; GCP CUD-sharing default-on 2026-06-16 + Cloud Run service-health GA both dated + hedged. finops-cloud-cost references no FOCUS spec version (all `[unverified]`, routed to live pricing).
- **cloud-b** — k8s 1.36 still latest GA (1.37 scheduled 2026-08-26, forward-looking); Gateway API v1.6.1 (2026-07-16) is a conformance-only patch on a current v1 anchor; OpenTofu 1.12.4/1.12.5 patches don't invalidate the "pin ≥1.12.3" security guidance; Terraform 1.15 still latest GA (1.16 only beta). All excluded as patch churn under hedged anchors.
- **data-bi** — dbt Fusion GA-on-Snowflake / preview-elsewhere, PG18, Flink 2.x, Kafka 4.x all current as of 2026-07 and unregressed; no dated status flip found.

## Feedback-loop note (tiering health)

No Tier-A plugin returned an empty *and* consistently-empty history warranting demotion this run; no Tier-B plugin surfaced through the fan-out. `security-engineering` continues to earn its Tier-A slot (a real, primary-sourced weekly delta). No manifest change proposed.

## Net result

Of ~28 Tier-A plugins swept, **1 finding** survived grounding + panel review and shipped: a P2 correctness fix (security-engineering npm v12 est.→GA plus a corrected approval command). Consistent with the routine's base rate (2026-07-22: 2 shipped; 2026-07-13: 1; 2026-07-08: 3). The five zero-finding clusters are the anti-churn discipline working as designed. Two out-of-window Microsoft observations were logged for a full re-audit rather than force-fit into the weekly tier.
