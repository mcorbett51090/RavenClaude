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
