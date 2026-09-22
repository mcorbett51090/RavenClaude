# Handoff taxonomy — glossary (mechanisms KEEP)

**Last reviewed:** 2026-09-16 · **Owner:** Experience + PE.  
**Claim:** one glossary so operators stop asking “which handoff?”.  
**Non-goal:** do **not** collapse or delete mechanisms; do **not** replace them with “just `/compact`.”

## Default vs earn-it

| Reach for | When | Why |
|---|---|---|
| **`/compact`** | **default** — context hot, mid-task | same process; keeps tools + thread |
| **`/handoff`** | plugin/hook must go live; next reader ≠ this session; task genuinely done | see `skills/session-handoff/SKILL.md` earn-it table |

## Mechanism glossary

| Name | Role | Writes brief? | Fresh interactive session? |
|---|---|---|---|
| **`/handoff` + `session-handoff`** | Write run-dir brief + optional **new interactive** session (unbounded TUI) | yes (via writer) | **yes** (optional; write-without-spawn is supported) |
| **`context-handoff.py`** | `write` / detached `fill` / `finalize` of `handoff.md` | yes | no |
| **`handoff-nudge`** | Stop advisory when context hot | **never** | no |
| **`precompact-digest`** | PreCompact **archival** digest (detached; not a fresh window) | digest file | no |
| **`session-relay`** | Peer live session via ListAgents/SendMessage | no (relay) | **no** — not a new session |
| **`cheap-lane-delegation`** | Bounded off-Claude job (returns) | n/a | **no** — **not** handoff |

## Anti-confusion one-liners

- **Nudge ≠ write.** `handoff-nudge` only advises; it never authors `handoff.md`.  
- **PreCompact ≠ persist-through-compact.** Digest is archival-only; compaction APPENDS.  
- **Relay ≠ handoff.** Live peer message ≠ new empty window.  
- **Cheap-lane ≠ handoff.** One bounded Grok/Copilot job with `advise|agent` is cheap-lane; quota/host-switch/fresh window is session-handoff.  
- **`/fork` is never the answer** for a reset (copies bloated history).

## Pointers

- Skill: [`skills/session-handoff/SKILL.md`](../skills/session-handoff/SKILL.md)  
- Command: [`commands/handoff.md`](../commands/handoff.md)  
- Pins / fill tier: [`unified-model-matrix.md`](unified-model-matrix.md) surfaces `handoff_fill`  
- Routing nav: [`routing-map.md`](routing-map.md)
