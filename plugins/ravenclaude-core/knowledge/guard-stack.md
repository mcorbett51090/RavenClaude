# Guard stack — floors that do not weaken each other

**Last reviewed:** 2026-09-16 · **Owner:** AppSec + PE.  
**Claim:** four layers answer different questions. This diagram is **not** permission to merge or weaken any floor.

## Stack

| Layer | Path | Behavior | Soften? |
|---|---|---|---|
| **1. Deterministic hard block** | `hooks/guard-destructive.sh` | `exit 2` on destructive Bash variants | **KEEP** |
| **2. Opt-in tribunal** | Thing + `concerns-catalog.md` | ALLOW / EDIT / DENY; `gate_floor` human ask | **KEEP** floors |
| **3. Cause preflight** | `scripts/preflight-command-review.sh` | `cause_preflight: warn\|off` advisory | advisory |
| **4. OS containment** | containment-posture | below model layer | orthogonal |

```mermaid
flowchart TB
  CMD[Bash / reviewed tool call] --> GD{guard-destructive}
  GD -->|match| BLOCK[DENY exit 2]
  GD -->|clean| TH{Thing on for category?}
  TH -->|off| PF[cause_preflight warn or off]
  TH -->|on| PANEL[Panel ALLOW / EDIT / DENY]
  PANEL -->|DENY| BLOCK
  PANEL -->|EDIT| REVAL[Re-validate rewrite]
  PANEL -->|ALLOW plus gate_floor| ASK[Human ask or auto]
  REVAL --> PF
  ASK --> PF
  PF --> OS[OS / containment posture]
  class BLOCK,GD built
```

## Locks

- No Thing / `gate_floor` / `guard-destructive` / always_screen / pre_llm_deny weaken.  
- No BMA. Docs-only (0.323.12 Phase C).
