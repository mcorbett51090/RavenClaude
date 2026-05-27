---
name: thing
description: "Command review (the Thing) — the opt-in command-review tribunal that votes ALLOW/EDIT/DENY on shell commands (and ALLOW/DENY on file edits) a comfort-posture category is set to review. Read this when wiring, debugging, or explaining the tribunal: the PreToolUse orchestrator, the reviewer panel + tie-breaker, the deterministic concern evaluator, the tier model, the dashboard-configurable panel, the per-category toggle, the audit trail, and the fail-closed rules. T5 = tiered routing (low→extreme) where a clean low-risk read gets no LLM panel, seat count + confidence escalate with the tier, and a dashboard-configurable gate_floor decides which confident allows you confirm; live for six command categories (ALLOW/EDIT/DENY) — the five shell categories plus network_write (curl/wget/gh writes, v0.40.0) — plus six tool-shape categories that are ALLOW/DENY-only (a seat EDIT is coerced to DENY): file_edit_project, file_edit_global, file_read_project, file_read_global, network_read, mcp_tools."
---

# Skill: command review (the Thing)

**Command review** — technical noun *the tribunal*, Norse codename *the Thing (Þing)* — is an opt-in panel of reviewer agents that adjudicates shell commands instead of interrupting you. It sits **on top of** the comfort-posture system: comfort-posture decides the policy (allow / ask / deny per category); the tribunal is the adjudicator you can switch on for a category so that, instead of stopping to ask you, a reviewer renders a verdict in seconds.

The authoritative design is [`docs/tribunal-review-feature-design.md`](../../../../docs/tribunal-review-feature-design.md); the concern catalog the tribunal cites is [`knowledge/concerns-catalog.md`](../../knowledge/concerns-catalog.md). This skill documents **what actually ships today** and how to operate it.

## What ships (T5)

The tribunal is a real **panel**: up to three reviewer seats run in parallel, a tie-breaker is convened only when they disagree, and a seat may **rewrite** a risky command (the rewrite is re-validated against the concern catalog before it runs). T5 makes routing **tiered** and adds a configurable **human gate**.

| Dimension | T5 reality | Arrives later |
| --- | --- | --- |
| Seats | **Up to 3** — Forseti (security-reviewer), Mímir (code-reviewer), Heimdall (prompt-engineer) — **+ Thor** (architect) convened only on a split or low-confidence panel | Domain specialist seats (T7) |
| Verdicts | **ALLOW / EDIT / DENY** (+ fail-closed DENY, or an `ask` when the gate surfaces a command) | — |
| Categories | **6 command** (5 shell + `network_write` — curl/wget/gh writes, v0.40.0; ALLOW/EDIT/DENY) + **6 tool-shape** (`file_edit_project`, `file_edit_global`, `file_read_project`, `file_read_global`, `network_read`, `mcp_tools`; **ALLOW/DENY-only**, v0.38.0–v0.39.0) | the deterministic MCP `mcp.allowed_servers` allowlist (§MCP identity) |
| **Tiers** | Every command resolves to `low`→`medium`→`high`→`extreme` = its category **base tier** (`category_tier_map`) bumped up by a deterministic high/critical concern. **`low` runs no panel** (clean reads are free); seat count + the confidence bar escalate with the tier; `extreme` carries a mandatory Forseti seat | — |
| Routing | Tier-driven: `low` → deterministic screen only (0 seats), `medium` → 2 seats, `high`/`extreme` → 3 seats; unarguable critical → pre-LLM DENY | — |
| **Human gate** | `gate_floor` (`medium`..`extreme`, default `high`) = lowest tier whose **confident ALLOW** is surfaced to you as `ask`. Reads are never surfaced; high-blast allows always are; DENY/EDIT stay autonomous | — |
| Injection defense | Pre-LLM `triggers` screen on **every** command (catalog-driven) + Heimdall (the LLM injection seat) from the first mutate tier + each seat's own check + adversarial envelope | — |
| Panel config | Per-seat model, per-tier seats + confidence, and `gate_floor` — **set from the dashboard** | — |
| Default | **OFF for every category** | unchanged — always opt-in |

## Turning it on

The on/off toggle is a **per-category `thing:` field in `.ravenclaude/comfort-posture.yaml`**, set from the dashboard's **Command review** toggle on the Settings tab (live for the five shell categories plus `network_write`, `file_edit_project`, `file_edit_global`, `file_read_project`, `file_read_global`, `network_read`, and `mcp_tools` — every category except the deterministic MCP allowlist follow-up). The dashboard's **Command-review panel** section sets the per-seat models, the **comfort level** (`gate_floor`), and — behind an Advanced expansion — the per-tier seats + confidence, all serialized as a top-level `command_review:` block. Turning a category on writes:

```yaml
categories:
  shell_readonly:
    user: allow
    local: allow
    project: inherit
    thing: on # ← command review for this category
```

The extra `thing:` key is ignored by `apply-comfort-posture.py` (it only reads the layer keys), so it never disturbs the permission translation.

> **Cost & latency, stated plainly.** Each reviewed command convenes one to three `claude -p` seats **in parallel**, so a verdict lands in roughly the time of the slowest seat (seconds), not the sum — but it still spends real credits on every reviewed command. `shell_readonly` is the highest-frequency category (`ls`, `cat`, `grep`, `git status`); leaving its toggle ON taxes daily work and is best used as a **validation switch**. The categories where review actually earns its cost are `shell_remote_mutate` (push / publish / PR mutations), `shell_code_exec` (python/node/bash -c/eval), `shell_package_install` (supply-chain: global installs, unpinned versions, cred-in-registry-URL, tarball-from-`/tmp`), and `shell_local_mutate` (destructive local: `rm`, `git reset --hard`, force-deleting `main`, recursive `chmod 000/777`) — turn those on for high-stakes sessions. The six **tool-shape** categories review file edits/reads, web fetches/searches, and MCP calls instead of shell commands (all **ALLOW/DENY-only** — a seat rewrite is coerced to DENY): `file_edit_project`/`file_edit_global` catch posture writes into `.claude/`/`.ravenclaude/`, shell-init / cron / system-dir writes, conflict markers, and vendored-file edits; `file_read_project`/`file_read_global` catch reads of `.env`/keys/`~/.ssh`/`/etc/shadow` (reads are base-tier `low`, so only a secret/credential read escalates to a seat — clean reads stay free); `network_read` catches the cloud-metadata SSRF endpoint, localhost, and IP-only/IDN domains in a `WebFetch`; `mcp_tools` catches third-party-write verbs and broad-data reads. All toggles are **off by default**.

## How a reviewed command flows

```mermaid
flowchart TD
  A[Bash PreToolUse] --> B{posture file has<br/>thing: on anywhere?}
  B -- no --> Z[exit 0 · normal flow]
  B -- yes --> C[thing-decision.py + thing-concerns.py:<br/>category · toggle · tier · routing]
  C -- toggle off / unknown cat --> Z
  C -- unarguable critical<br/>pre_llm_deny --> DENY[DENY · no LLM call]
  C -- clean low read<br/>tier=low --> ALLOW[allow · no panel]
  C -- tier ≥ medium --> E[run convened seats IN PARALLEL<br/>thing-seat.sh · panel deadline + kill]
  E -- ≥2 abstain / inconclusive --> DENY
  E -- any injection_detected --> DENY
  E -- split / low confidence --> T[convene Thor]
  T --> AGG[aggregate]
  E --> AGG
  AGG -- cited critical + allow --> DENY
  AGG -- edit --> RV{re-validate:<br/>concerns⊆orig−cited?}
  RV -- ok --> EDIT[allow + updatedInput]
  RV -- fail --> DENY
  AGG -- deny --> DENY
  AGG -- allow --> GATE{not a read AND<br/>tier ≥ gate_floor<br/>or high-blast?}
  GATE -- yes --> ASK[ask · you confirm]
  GATE -- no --> ALLOW
  DENY & ALLOW & EDIT & ASK --> L[(Sága log)]
  L --> OUT[emit permissionDecision]
```

Components (all under the plugin):

- `hooks/thing-orchestrator.sh` — the **Lawspeaker**. PreToolUse(Bash) hook. Short-circuits with a single `grep` when no toggle is set; otherwise calls thing-decision, fans the routed seats out in parallel under a panel deadline, runs the aggregation state machine, re-validates EDITs, logs, and emits the verdict.
- `scripts/thing-decision.py` — classifies a command into a comfort-posture category (reusing the EMISSIONS table — one source of truth), reads the toggle, resolves the panel config (precedence: `comfort-posture.yaml command_review:` > `thing.yaml` > defaults), and merges in routing from thing-concerns — all in one call.
- `scripts/thing-concerns.py` — the **deterministic concern evaluator**. Reads the catalog's machine-readable `triggers` to return matched concerns + max severity + which seats to convene, and enforces the **EDIT-safety invariant** (`concerns(revised) ⊆ concerns(original) − {cited}`). No live model — reproducible + CI-testable.
- `scripts/thing-seat.sh` — invokes ONE reviewer seat (role via `THING_SEAT_ROLE`) via `claude -p` and returns its verdict JSON (now including `edited_command`). A role-aware `THING_SEAT_MOCK_VERDICT` test hook lets CI/gate-audit exercise the whole panel with no live model.
- `templates/thing.yaml` — optional advanced config (panel models, **`tiers`** = per-tier seats + confidence + mandatory seats, **`category_tier_map`**, **`gate_floor`**, seat/panel timers, audit dir); `schema_version: 4`. Absent ⇒ defaults; legacy `seat:` maps to Mímir; a leftover T3 `timeout_posture:` is ignored.

## Verdict semantics & fail-closed rules

| Situation | Verdict emitted |
| --- | --- |
| **Clean low-risk command** (tier `low`, deterministic screen clean) | `allow` — **no panel convened** (zero cost) |
| Panel agrees allow, confidence ≥ tier threshold, no critical cited, tier **below** `gate_floor` (or a read) | `allow` (the command runs autonomously) |
| Panel agrees allow but the tier is **at/above `gate_floor`**, or the command is **high-blast** (irreversible), and it is **not** a read | `ask` — surfaced to you for confirmation (the tribunal already cleared it) |
| Panel votes deny, or a critical concern is cited | `deny` (blocked — beats `--dangerously-skip-permissions`) |
| A seat proposes EDIT and the revision passes the safety invariant | `allow` + `updatedInput:{command:<revised>}` (the rewrite runs autonomously) |
| EDIT revision fails the invariant (new concern / cited not removed) | `deny` |
| Pre-LLM unarguable-critical `triggers` hit (`pre_llm_deny`) | `deny` immediately, no LLM call |
| Any seat reports `injection_detected: true` | `deny` (unilateral) |
| Seats split or a seat's confidence < tier threshold | Thor convened; Thor's verdict decides |
| ≥2 convened seats (or the whole panel) abstain / inconclusive | `deny` — abstention always fails **closed** at every tier (an escalated read that abstains denies too) |
| `thing.yaml` present but malformed | `ask` |
| `jq` missing | block (exit 2) — detect-and-deny |

> **Reads are never surfaced.** A read-shaped category (`file_read_*`, `shell_readonly`, `network_read`) never emits `ask`: a clean read auto-allows, and an escalated read (a concern bumped it to `medium`+) is auto-decided by the panel — `allow` or `deny`, never a prompt. The `gate_floor` knob and the high-blast override both yield to this rule.

The platform **fails open** on hook timeout, so the orchestrator enforces its own **panel deadline** (`panel_deadline_seconds`, default 75 s, under the 90 s hook timeout), killing straggler seats, and emits an explicit fail-closed verdict rather than letting the tool slip through. Each seat additionally has a soft cap (`seat_timeout_seconds`, default 45 s — parallel `claude -p` cold-starts run ~24-29 s, well over the original 18 s, which abstained the whole panel on modest machines; raise it if your parallel seat latency is higher).

Every verdict writes one JSON entry to `.ravenclaude/runs/thing/<id>.json` (the Sága log) — command, category, `phase`, per-seat verdicts, concerns cited, final verdict, the revised command on EDIT, and duration. Gitignored by default.

## Known limitations (so they don't surprise you)

- **Compound / control-flow commands classify by their leading segment.** `ls | grep x` reviews as `shell_readonly`; a bare `for …; do …; done` classifies as nothing and is **not** reviewed (falls through to normal flow).
- **Deterministic routing is regex-based.** `triggers` are added for the cross-cutting concerns plus the live categories' deterministic concerns; concerns without `triggers` (the `judgment_only` ones and the not-yet-live categories) rely on the seats' own judgment, not the pre-LLM screen. For the file shape, triggers run against the reviewed text `"<file_path>\n<content>"`, so a path-anchored regex screens the path and a content regex screens the body.
- **EDIT only when deterministically verifiable.** An EDIT is accepted only if the cited concern has `triggers` (so the invariant can confirm removal); otherwise it fails closed to DENY. **File edits are ALLOW/DENY-only** regardless — a seat EDIT verdict on a `file_edit_project` call is coerced to DENY (there is no machine-checkable `concerns(revised) ⊆ concerns(original)` invariant for free-form file content).
- **Every category is live (v0.40.0); one engine follow-up remains.** All file edits + reads (project & global), `WebFetch`/`WebSearch` → `network_read`, `mcp_tools`, and now `network_write` are reviewed when toggled on. A `..`/`~`/outside-project path resolves to the stricter `file_edit_global` / `file_read_global` (never silently to the project category). The remaining follow-up is the deterministic **`mcp.allowed_servers` allowlist** (design §MCP identity) — until it ships, the three MCP server-identity concerns (`mcp.unknown-server` / `mcp.unverified-server` / `mcp.tool-shadowing`) are seat-judged rather than deterministically denied.
- **`network_write` is command-shaped (curl/wget/gh), so ALLOW/EDIT/DENY.** Unlike the tool-shape categories it is reached via Bash, so a seat may rewrite a risky write (re-validated against the catalog) instead of only DENYing. `classify()` carries a flag-aware override that re-routes implicit-POST forms (`curl -d`/`--data`/`-F`/`-T`, `wget --post-data`, `gh api -X POST`) — which the space-delimited EMISSIONS prefix matcher misses — into `network_write`, so a write can't auto-allow as a "read". Base tier `medium`: it always convenes a panel.
- **Reads are cheap by design.** `file_read_*` and `network_read` are base-tier `low`, so a clean read convenes **no** panel (zero cost); only a high/critical concern (a secret-file/credential read, the cloud-metadata endpoint) escalates a read to a seat. WebFetch reviews the **URL only**; WebSearch reviews the **query**.

## Auth note

On a Claude **subscription / OAuth** login the seat uses plain `claude -p` (default) — `claude -p --bare` is faster/cleaner but refuses OAuth and demands `ANTHROPIC_API_KEY`, so it is opt-in via `THING_SEAT_BARE=1` for API-key users. The seat runs from a scratch directory so the consumer's project `CLAUDE.md` is never auto-loaded into the review (keeps it fast, cheap, deterministic).
