<!-- RAVENCLAUDE-STAGING-METADATA
type: best-practice
topic: architecture
proposed-by: consumer engagement — BTCSIReporting (Copilot CLI) prompting on nearly every turn despite broad allow rules
proposed-on: 2026-07-16
target-file: docs/best-practices/comfort-posture-behavioral-flags-vs-permissions.md
status: pending
-->

# Comfort posture has two orthogonal surfaces — `allow` rules don't silence behavioral flags; tune `design_checkins` / `orchestrator` / `decision_review` separately

**Status:**
- **Primary diagnostic** — when a Copilot-CLI (or Claude Code) agent prompts on nearly every turn despite broad `allow` rules, check these three flags first.

**Domain:** Agent design / comfort posture (cross-domain).

**Applies to:** `ravenclaude-core` on any host — especially GitHub Copilot CLI, where the base model is more conservative and calls `ask_user` more readily than Claude.

---

## Why this exists

The comfort posture has **two orthogonal control surfaces that are easy to conflate**: permission rules (`categories.*` → `allow`/`ask`/`deny`, which control tool-call approval dialogs) and behavioral flags (`design_checkins`, `decision_review`, `orchestrator`, which control whether the agent *pauses to think out loud with the human*). Setting every category to `allow` removes click-to-approve on tool calls and has **zero** effect on the behavioral flags — they are deliberately decoupled, so relaxing permissions to move faster never silently mutes design check-ins. An operator who only knows the permission surface will crank everything to `allow`, still get prompted on every turn, and conclude the posture is broken when three separate behavioral knobs are the real driver.

## How to apply

**One diagnostic, three knobs, in priority order:**

```bash
grep -E "design_checkins|^orchestrator:|decision_review" .ravenclaude/comfort-posture.yaml
```

Expected output for low-prompt operation:

```yaml
design_checkins: false     # primary driver — absent OR true means it's firing
orchestrator: full         # absent ≠ "full" for the AGENTS.md condition check (see below)
decision_review: binding   # or advisory — binding is fine once design_checkins is off
```

1. **`design_checkins` (primary).** A behavioral flag read by the Team Lead — pause and surface a Keep/Update/Deny prompt at every structural/architectural decision. **Default is `true`**, so an absent key fires it. Set `design_checkins: false` → the agent proceeds on best judgment and **reports** the choice instead of asking (reporting is not silenced). Does NOT suppress: PROD approval gates, standing explicit-approval rules (PROD import, mass PATCH, solution delete), or the decision tribunal.
2. **`orchestrator` (relay-mode gap).** `CLAUDE.md` documents "absent = `full`", but `copilot/AGENTS.md`'s relay-mode activation requires condition 3 to be the **literal** `orchestrator:` set to `decide` or `full` (not `off`) — an absent key fails that check, so relay never fires and the more-conservative base Copilot model handles the turn. **Fix: add `orchestrator: full` explicitly**, next to `orchestrator_scope` for readability.
3. **`decision_review` (contributing).** `binding` routes every yes/no decision through the Thing tribunal. Leave `binding` if you want hard-stop confirmation on high-stakes binary decisions; set `advisory` if you want the tribunal to suggest without blocking. Keep it `binding`/`advisory` per taste — just ensure `design_checkins` is `false` first, since that's the loud one.

The three surfaces at a glance:

| Surface | Controls | Suppressed by `allow`? |
|---|---|---|
| `categories.*` (allow/ask/deny) | tool-call approval dialogs | N/A — these *are* the allow rules |
| `design_checkins` | whether the agent pauses for design decisions | **No** — decoupled by design |
| `decision_review` | whether yes/no decisions route through the tribunal | **No** |
| `orchestrator` | whether non-Claude-Code hosts relay to Claude | N/A — relay mode, not permissions |

## Edge cases / when the rule does NOT apply

- **What still prompts by design** (not suppressible by these flags): PROD approval gates, standing rules requiring explicit approval, and the decision tribunal for genuinely high-stakes yes/no calls. `design_checkins: false` should never be read as "silence the safety gates."
- **Relay on a Claude host.** When Copilot CLI is already running on Claude, relay mode calls `claude -p` as a subprocess per turn — intentional: the subprocess runs in a clean context without the project's CLAUDE.md loaded (the bounded, auditable egress path). Adds latency; not a bug.
- **The `orchestrator` absent-vs-`full` discrepancy is arguably a plugin bug to fix**, not just a config workaround — `CLAUDE.md`'s documented default and `copilot/AGENTS.md`'s condition check disagree. The workaround (set it explicitly) holds today; the durable fix is reconciling the two docs. Flag for the review expert.

## See also

- [`plugins/ravenclaude-core/knowledge/concepts/comfort-posture.md`](../../plugins/ravenclaude-core/knowledge/concepts/comfort-posture.md) — the comfort-posture concept.
- [`plugins/ravenclaude-core/copilot/AGENTS.md`](../../plugins/ravenclaude-core/copilot/AGENTS.md) § "Relay mode" — the three relay-activation conditions (condition 3 is the literal-key requirement).
- [`plugins/ravenclaude-core/skills/set-posture/SKILL.md`](../../plugins/ravenclaude-core/skills/set-posture/SKILL.md) — the (category, level) → permission-rule translation pipeline.
- [`plugins/ravenclaude-core/knowledge/orchestrator-data-egress.md`](../../plugins/ravenclaude-core/knowledge/orchestrator-data-egress.md) — orchestrator scopes + the ZDR attestation.

## Provenance

Consumer engagement (BTCSIReporting, Copilot CLI), 2026-07-16: the agent prompted on nearly every turn despite broad `allow` rules and `defaultMode: bypassPermissions`. Root-caused to three compounding behavioral flags — `design_checkins: true` (primary), an absent `orchestrator:` key defeating relay-mode condition 3, and `decision_review: binding`. Fixed (commit `5a90961c`, branch `dev`) by setting `design_checkins: false` and adding `orchestrator: full`; `decision_review: binding` left intact so PROD/destructive gates still block. The `copilot/AGENTS.md:69` literal-key requirement was re-confirmed against this repo's source on 2026-07-16.

---

_Last reviewed: 2026-07-16 by consumer-engagement contribution (comfort-posture prompt-frequency root-cause)_
