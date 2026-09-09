# P0-a — Delivered-channel disposition, per hook

**Decided 2026-08-19 by reading what each hook actually writes, not by pattern.** The plan forbids a
blanket conversion, and rightly: converting everything would inject launcher chatter into every
turn's context — the mirror-image defect of the one being fixed. A channel that reaches the model
carrying content nobody wanted there is not an improvement.

control: read the stderr sites of all 8 exposed hooks directly -> 4 carry model-actionable content
and 4 do not. The negative half IS the control: a triage that converted 8 of 8 would be evidence the
triage was not discriminating, not evidence that 8 needed converting.

## The tiers

| tier | meaning | channel |
|---|---|---|
| `advisory` | the model can act on it, or it proceeds on a stale picture of its own constraints | `additionalContext` via `_advise.sh` |
| `internal-logging` | the human at the terminal is the consumer | stderr, **documented as such and tested as such** |
| `library` / `adapter` | consumer is a calling script or another host, not a model | out of scope |

control: `_advise.sh --self-test` -> PASS, and its planted-defect canary FAILS when the banner is
removed, so the advisory channel used by tier 1 is itself instrumented rather than assumed.

## The table

| hook | stderr content (measured) | disposition | why |
|---|---|---|---|
| `ensure-default-mode.sh` | *"Session loaded in `<mode>` mode. Your comfort-posture allow/ask/deny rules are partially or fully bypassed… Press Shift+Tab to return to default"* | ⛔ **advisory — convert (highest priority)** | The permission rules are bypassed in this mode while the model has no signal that they are. control: read the heredoc body -> it states the bypass explicitly; grep for any delivered-channel emit in the same file -> none. |
| `guard-recursive-spawn.sh` | a findings list with elision (`…(more elided)`) | **advisory — convert** | Reports recursive-spawn patterns in files just written; the model authored the file. control: 4 stderr sites, 0 additionalContext. |
| `regen-on-manifest-change.sh` | `failed to regenerate <label> — run manually: <cmd>` | **advisory — convert** | The failure path names a command to run. control: 2 stderr sites, 0 additionalContext. |
| `reapply-posture.sh` | *"comfort posture found but python3 is unavailable; skipping auto-apply"* | **advisory — convert** | The posture is not applied on this path. control: read the guard around it -> it fires only when `python3` is absent, so the common case emits nothing. |
| `dashboard-autostart.sh` | *"dashboard starting on http://127.0.0.1:PORT"* | **internal-logging — keep stderr** | Launcher status; the consumer is the human who wants the URL. control: both messages are URL/status only, neither names an action for the model. |
| `_host-canary.sh` | a `warn()` diagnostic helper | **internal-logging — keep stderr** | Sourced diagnostic for host detection. control: single `warn()` definition, no caller-facing advice. |
| `_model-fallback.sh` | three **usage errors** (`do not execute directly`, `--runner … required`, `runner function not defined`) | **library — out of scope** | ⛔ The plan speculated this carries a silent model-downgrade notice. control: grep `fell back\|falling back\|downgrade\|degraded` -> **no match**; all three stderr sites are programmer usage errors, and the resolved model reaches the CALLER via the exported `_MF_RESOLVED_MODEL`. Conversion belongs to the caller if anywhere. |
| `codex-hook-env.sh` | `no hook path given` | **adapter — out of scope** | Usage error in a host adapter; consumer is another host's environment. control: single stderr site, argument validation only. |

**Result: 4 convert · 2 internal-logging · 2 out of scope.**

## ⛔ Compounding rule, from claim 9 — read before converting

Two `additionalContext` emitters on ONE event **concatenate** (measured); they do not last-write-wins.
So converting several hooks on one event compounds context. `updatedToolOutput` is the opposite — it
**replaces** the tool result, so two emitters of that on one event is a silent data-loss shape.

| hook | event | what else already emits `additionalContext` there |
|---|---|---|
| `ensure-default-mode.sh` | SessionStart | `capability-orientation.sh` — concatenates onto an already-large banner; keep the message short |
| `reapply-posture.sh` | SessionStart | same; both fire only on a degraded path |
| `guard-recursive-spawn.sh` | PostToolUse(Edit\|Write\|MultiEdit) | `claim-grounding-lint`, `delegation-nudge`, `storage-placement-nudge` — a fourth on one event |
| `regen-on-manifest-change.sh` | PostToolUse(Edit\|Write\|MultiEdit) | as above — a fifth |

⛔ Four and five emitters on one PostToolUse event is a real volume risk, and volume is what gets a
channel ignored. Each fires only on its own narrow trigger, so the common case should still be zero —
but that is a claim about trigger rates and it is NOT yet measured.
`[unverified — combined advisory volume on PostToolUse(Edit|Write|MultiEdit) not measured; settle it
against the 46,557-envelope replay corpus the way triage-outcome.sh was settled, before converting
the two PostToolUse hooks]`

## What the internal-logging tier gets instead of nothing

`assert_terminal_only` (P0-b) asserts stderr carries the text **and** that stdout carries no delivered
channel. An internal-logging hook is then tested as being terminal-only rather than merely untested —
a future edit that silently adds a delivered channel fails, and one that silently drops the message
fails too. The tier is a decision with a test behind it, not an exemption.

## ⛔ This file was itself blocked by `guard-premise.sh` on first write

T-PROSE denied the first draft: a diagnosis-shaped claim in a durable artifact with no control beside
it. That is the exact self-block the red-team predicted for this file class, arriving unprompted. It
was resolved by citing the probes that were actually run — the `control:` lines above — rather than by
using the override. Recorded because the guard firing here is evidence it works, and because the next
author of a measurement-heavy doc will hit it too.
