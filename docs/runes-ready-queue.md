# Runes ready-queue & Oath-hook

**Status:** shipped in `ravenclaude-core` (ledger projection + thin CLI)  
**Cosmology SSOT:** [`norse-mythology-feature-map.md`](./norse-mythology-feature-map.md) — do not invent a second cosmology.  
**Naming SSOT:** CoS + Matthew GO (2026-09-15), **Longship** amend (delivery was briefly Hird; superseded).

## Product one-liner

Runes are the work; `rc runes ready` is the queue; claim/sling binds the Oath-hook; strands instantiate formulas (PE packs); **Longships** batch delivery to Sage (**never** auto-merge).

## Locked names

| Concept | Name | CLI |
|---------|------|-----|
| Work unit | **Rune** | `rc runes …` |
| Ready-queue | Runes ready | `rc runes ready` (alias `rc ready`) |
| Claim / bind | claim / sling onto hook | `rc runes claim\|sling <id>` |
| GUPP | **Oath-hook** | SessionStart `oath-hook.sh` · `rc runes hanging` |
| Formula | PE pack = formula | — |
| Molecule | **strand** | `rc strand apply <pack>` |
| Delivery batch | **Longship** | `rc longship open\|add\|land-request\|show` |

**Facet labels only (not the Norns panel):** Verðandi = ready-now · Skuld = owed/backlog/gated.

## Hard non-reuse

Do **not** reuse Thing / Huginn–Muninn / Thor–Forseti / Hliðskjálf / Norns panel as the queue. No Gas Town / Beads UX names. No BMA. Sage sole SCM — Longship `land-request` records intent only; it does **not** merge.

## Human gates

`human_gate`: `none` \| `cos` \| `matthew` \| `appsec` \| `sage`. Money / delete / AppSec / Matthew walls never auto-claim.

## Implementation

- Projection over `.ravenclaude/ledger/` via `ledger.py` (`hook` + `meta` events; `longship_id` on items).
- CLI: `plugins/ravenclaude-core/scripts/runes.py`
- Oath-hook: `hooks/oath-hook.sh` + `scripts/oath_hook.py` on SessionStart.

Was briefly named Hird for delivery; Matthew amend → **Longship** everywhere (`longship_id`, `rc longship*`).

## Dashboard opt-in → automatic (Matthew LOCK 2026-09-15)

| State | Behavior |
|-------|----------|
| **Off (default)** | Absent `runes:` key or `runes: off`. No automatic SessionStart orientation. **CLI still works.** |
| **On** | Every SessionStart: Oath-hook surfaces **hanging MUST-RUN** + **ready summary**, and may **auto-claim** the next **ungated** ready Rune. |

- **Posture key SSOT:** `runes: off \| on` in `.ravenclaude/comfort-posture.yaml` (absent ⇒ off). emitYaml writes only when `on`.
- **Surfaces:** Settings (**⚙ Runes at session start**) **and** Pipeline → SessionStart card share **one** state; **Save & apply** round-trips either.
- **Kill switch:** set **Off** + Save.
- **Auto-claim refuse:** `human_gate` in {matthew, appsec, cos, sage, money} (or any gated). **Never** auto Longship merge / Sage land.
- **Host caveat (MH-18):** fires only on SessionStart-hook hosts — see `plugins/ravenclaude-core/knowledge/host-support.json`. Do not claim Copilot/Cursor/etc. without that map.

## Auto-create-from-ask + flat taxonomy (Matthew LOCK)

When CoS/agent **accepts** a Matthew request as work → open a Rune:

```bash
rc runes open "<title>" [--gate matthew|appsec|cos|sage|money] [--kind fix|feature|chore]
```

- **Shape:** **flat Runes + strands only**. Kind is an optional **tag**, not a hierarchy level.
- **No** epic → feature → fix tree. Do not invent epic boards.
- Create on **accept**, not before. Dashboard On does not invent asks — it orients/claims.

## Factory surface

All Runes behavior ships in **ravenclaude-core** (CLI + hooks + skill) for **any harness** — not CoS-only.

