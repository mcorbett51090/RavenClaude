# Command-review gap-closure plan — bounded autonomy in the portable hook layer (2026-05-29)

> Companion to [`command-review-autonomy-assessment-2026-05-29.md`](command-review-autonomy-assessment-2026-05-29.md) §8. Synthesizes the two-reviewer panel (security-engineer + systems-architect) re-assessment under the **corrected constraint**: the owner runs **GitHub Copilot CLI** routing across **Claude + ChatGPT + Grok**, so native Claude Code `auto` mode (and its "free" 3/20 runaway brake) is **unavailable**. **Every gap must be closed in the portable hook layer** — nothing may depend on `auto`. Goal: move the tribunal from *bounded destruction + low-touch disposition* (≈48–51/100) to *bounded autonomy* (≈66–68/100 ceiling for this architecture) **without betting on a control plane Copilot can't reach.**

## The binding constraint (stated once, governs everything below)

Code-grounded, both panels independently: the Copilot bridge wires only **SessionStart / PreToolUse / PostToolUse** (`scripts/ravenclaude:160-171`); `copilot-hook-adapter.sh` has **no `stop` mode** and its `posttool` mode **discards hook output**. The plugin's `hooks.json` Stop hook is the *Claude Code* path, which Copilot bug [#2540](https://github.com/github/copilot-cli/issues/2540) says doesn't fire. So **under Copilot today: PreToolUse can block; PostToolUse fires but cannot block (output discarded); Stop is not wired at all.** Any "block at turn-end" gate therefore needs bridge work *first*. The seats are also **Claude-CLI-only** (`thing-seat.sh:146,240`) — in a GPT/Grok-routed session the panel may abstain entirely (safe-but-absent judgment).

Notation: **[D]** deterministic / no model · **[L]** LLM-in-loop · effort S/M/L.

---

## Phase 0 — Extend the Copilot bridge (DEPENDENCY for the two headline gates) · [D] · M · low risk

Without this, the DoD gate and the turn-end half of the runaway brake are vapor on Copilot.

1. Add a `stop` mode to `copilot-hook-adapter.sh` (translate Claude Stop `decision:"block"` / exit-2 → Copilot's stop-block shape; **fail-OPEN on adapter error** so a broken Stop hook can't wedge a session).
2. Stop **discarding** PostToolUse output in the adapter's `posttool` mode, so a PostToolUse `block` can feed an error back.
3. Wire a `Stop` entry in the installer's hooks generator (`scripts/ravenclaude:162`) and add the new hooks to the Claude-Code `hooks.json` Stop block alongside `remind-tests.sh`.
4. **Owner-verify against a live Copilot CLI** whether it exposes a blocking Stop event. If it does **not**, the documented fallback is a **PostToolUse-driven** DoD check (PostToolUse *can* block once output isn't discarded) — weaker than a true Stop gate but portable. Record the result in the CLAUDE.md "GitHub Copilot CLI bridge" VERIFY notes.

---

## Gap 1 — Hallucination → Stop-hook **definition-of-done gate** · [D] (+ optional [L]) · M · medium risk

*The single highest-leverage item — closes "hallucinating" + half of "rabbit holes." Blocked by Phase 0.*

- New `hooks/dod-gate.sh`, Stop event. Reads a new `definition_of_done:` block in `comfort-posture.yaml` (`cmd: "npm test && npm run lint"`) — dashboard-authorable, never hard-coded. Runs it; on non-zero exit emits `decision:"block"` with the failing output (capped + control-stripped, reusing the `thing-seat.sh:294` discipline) so the agent keeps working instead of the human being the verification loop.
- **Anti-deadlock:** a max-consecutive-block counter in a per-session file under `.ravenclaude/runs/thing/` (the proven `fatigue` counter pattern, `thing-orchestrator.sh:516`) — Claude Code force-overrides Stop after 8, **but Copilot has no such guarantee, so the counter must be ours.**
- **Fail-safe:** no `definition_of_done` configured → `exit 0` (advisory `remind-tests.sh` remains the no-config fallback).
- Optional **[L]** second gate: an adversarial fresh-context diff reviewer (`Read,Grep,Glob` only) that surfaces only correctness/requirement gaps.
- **Composition:** fires at Stop, orthogonal to the tribunal's PreToolUse action-gating (tribunal = "is this action safe?"; DoD = "is the work actually done/correct?").

---

## Gap 2 — Rabbit-holing → hard **iteration / runaway brake** as a hook · [D] · M · medium risk

*The capability with NO other home now that `auto`'s 3/20 brake is unavailable. Ports cleanly via PreToolUse for the deny; fuller counting needs Phase 0.*

- New `hooks/runaway-brake.sh`. Per-session counter file (same `safe_sid` pattern as the fatigue counter). Track **consecutive identical/near-identical tool calls** (hash `tool_input` via the existing `thing-decision.py:384 cache_identity`) **and** a total tool-call ceiling. Defaults mirror the lost native semantics: **3 consecutive / 20 total**, dashboard-tunable via a `runaway:` posture block.
- **Action:** on threshold, **PreToolUse deny** every subsequent mutate ("runaway brake tripped — session paused; raise the limit or intervene"). PreToolUse is the one event guaranteed wired + blocking under Copilot → **this item ports cleanly** by incrementing in `thing-orchestrator.sh` (already runs on every reviewed PreToolUse call). Counting *all* tool calls (not just reviewed mutates) via PostToolUse is more complete and needs Phase 0's non-discarding posttool.
- **Reset** on SessionStart (extend `reapply-posture.sh`). Log every trip to Sága.
- **Risk:** false trip on a legitimate tight retry loop → key on the *consecutive-identical* signal, keep the ceiling generous, make it configurable.

---

## Gap 3 — Turn the multi-model "limitation" into a strength → **cross-vendor seats** + per-vendor golden set · [L] · M–L · medium risk

*Uniquely enabled by the owner's Claude+GPT+Grok access; `auto` (single-vendor) structurally cannot offer this.*

- Extend `_DIVERSITY_PREF` (`thing-decision.py:937`) and `thing-seat.sh:240` so a seat's "model" can name a non-Claude backbone, dispatched via Copilot's model routing rather than always `claude -p`. The per-seat-subprocess architecture is already the right shape (Forseti→Claude, Mímir→GPT, Heimdall→Grok). The verdict-JSON extractor (`thing-seat.sh:260` `raw_decode`) is already vendor-agnostic.
- **Gate it on Gap 5's per-vendor golden set** — never trust a vendor seat whose verdict quality on this rubric is unmeasured.
- Hardens the panel that already runs against *correlated* hallucination (cross-vendor anti-correlation); does **not** by itself close the hallucination gap (Gap 1 does).

---

## Gap 4 — Measure the panel → **golden-set eval + a "does `claude -p` run inside Copilot?" probe** · [L harness] · M · low risk · *do EARLY*

- Golden set of `{dangerous, benign, injection, scope-violating}` payloads with known verdicts, run as a regression gate, **per seat-vendor** (pin a Claude, a GPT, a Grok model; assert each clears the set). Use `THING_SEAT_MOCK_VERDICT` (`thing-seat.sh:109`) for the deterministic aggregation assertions (CI-cheap, no credits) and a credentialed non-CI lane for live per-vendor quality.
- **The probe is the point:** assert that `claude -p` actually resolves + returns a parseable verdict *from inside a Copilot session* — §8's sharpest risk is that it silently doesn't, degrading the whole panel to abstain-deny. Run this early to learn whether the owner's panel even convenes.

---

## Gap 5 — Containment residual → **OS sandbox / container posture** · [D config] · S–M · *honest caveat*

- **Honest flag (both panels):** Claude Code's sandbox (Seatbelt/bubblewrap, `denyRead`/`denyWrite`, `autoAllowBashIfSandboxed`) is a **Claude-Code feature** with no evidence Copilot CLI honors it — so the assessment's original "sandbox posture" rec **likely does not port.** Do not promise OS isolation via Claude's sandbox under Copilot.
- **Portable alternative:** make the real blast-radius boundary the **devcontainer + git worktree** the bridge already scaffolds (`templates/codespace-copilot/`, `ravenclaude init-codespace`). Have `ravenclaude setup` seed `denyRead: ["~/.aws","~/.ssh"]` where the host supports it, and otherwise write a `.ravenclaude/README.md` note recommending the container/worktree as the sanctioned containment posture. This is containment *depth*, not a new gate — the property the tribunal structurally cannot provide (survives a mislabeled/injected command because the OS, not the model, enforces it).

---

## Gap 6 — Scope confinement → **task-scope / SPEC gate** · [D] · S–M · low risk

- Extend the **existing** `enforce-layout.sh` (already wired PreToolUse on Write/Edit/MultiEdit under both hosts — Claude via `hooks.json`, Copilot via the `file-pretool` adapter mode, so **zero new wiring**) to also reject writes outside a task-declared scope set: read an optional `.ravenclaude/task-scope.json` (`{"in_scope":[globs],"spec":"SPEC.md"}`); a write matching no `in_scope` glob → deny with the suggested-location pattern it already uses.
- **Fail-safe:** absent file → no-op (today's behavior). Bounds *exploration breadth* where Gaps 1–2 bound *depth*.

---

## Gap 7 (owner-requested) — **Disclaimer in command review: scope + when it's optional** · [D docs/UI] · S · low risk

Make the tribunal's *purpose and applicability* explicit so a Claude-Code-only user isn't sold a layer they may not need, and a Copilot/multi-model user understands what it's for. Surface the same disclaimer in **(a)** the dashboard's Command-review panel (`_render_command_review_block` in `scripts/generate-dashboards.py`), **(b)** the `thing` SKILL.md, and **(c)** the plugin CLAUDE.md command-review section. Wording (canonical):

> **When command review is for you.** The Thing exists to put *portable, model-agnostic* guardrails on **agentic AI that routes across multiple model vendors** (e.g. GitHub Copilot CLI using Claude + ChatGPT + Grok), where Claude Code's native **`auto` permission mode is unavailable** (it is Anthropic-API/Claude-only). In that setup the Thing is the only layer that delivers a deterministic catastrophe floor, a self-tamper guard, secret-egress prevention, cross-vendor anti-correlated review, and low-touch ALLOW/EDIT/DENY disposition.
>
> **If you run *only* Claude Code, native `auto` mode may be sufficient** — it provides a hardened classifier plus a non-configurable 3-consecutive/20-total runaway brake that this tribunal does not yet replicate. On pure Claude Code, prefer `auto` for containment and treat the Thing as an *optional* add-on for its domain concerns, audit trail, and yes/no decision-routing. The tribunal earns its cost most clearly where `auto` cannot run.

This is a deterministic, zero-runtime-cost honesty surface — it ports trivially (it's text in the generator + skill + constitution).

---

## Recommended sequence

**Phase 0 (bridge) → Gap 4 (eval + Copilot probe — learn if the panel even runs) → Gap 2 (runaway brake — ports via PreToolUse) → Gap 1 (DoD gate — needs Phase 0) → Gap 3 (cross-vendor seats, gated on Gap 4) → Gap 6 (scope gate) → Gap 5 (container/worktree posture) → Gap 7 (disclaimer — ship anytime, S).**

Gaps 1 + 2 alone move the score ≈51 → ≈66–68 and convert the tribunal from "bounded destruction + low-touch disposition, two holes" into bounded autonomy that works under Copilot CLI **without ever depending on a Claude-only mode.** Gap 7 ships immediately (cheap, honesty-first). Each item is **[D]eterministic** except Gaps 3–4 (which measure/diversify the LLM panel, not gate on it).

## Migration / non-breaking posture

Every item defaults OFF or no-op-when-unconfigured (the marketplace discipline): no `definition_of_done`/`runaway:`/`task-scope.json` → today's behavior. The Phase-0 bridge change is additive (new modes/entries). Nothing breaks a consumer's `/plugin marketplace update` or `ravenclaude update`.
