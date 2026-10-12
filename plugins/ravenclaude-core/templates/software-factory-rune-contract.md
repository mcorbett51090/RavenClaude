# Software Factory Rune contract (template — P0 required fields)

> **What this is.** The one intake contract for factory work. It **extends** the fleet **CoS 6-field**
> contract and the landed **Runes** ready-queue — no new product, no new CLI, no new name. Copy the
> paste-ready block in §3 per factory item; fill it in at intake.
>
> **Runbook:** `docs/software-factory-runbook-p0.md` (the ops default path this contract feeds).
> **Substrate:** the CLI is `plugins/ravenclaude-core/scripts/runes.py`; the ledger event schema is
> `plugins/ravenclaude-core/templates/ledger/ledger-event.schema.json`; the human-facing Runes doc is
> `docs/runes-ready-queue.md`. Every subcommand/flag cited here was re-verified against `runes.py` on
> current `main`.

| Field | Value |
|---|---|
| **Authority** | Matthew lock: human = **goal + DoD only** (DoD **MUST** carry `appsec_in_scope`). Agents PR / review / tweak / **craft-approve**. **Sage merges.** CoS tips Matthew **only** forever-gates. |
| **Locks** | craft-approve ≠ merge · Longship `auto_merge: false` · no money/secrets/CreateAgent auto · no BMA · no force-push weaken · no new CI path-filter on required workflows · `entry_surface` ≠ the 3-model review ladder |

---

## 1. Required fields (all eight — a contract missing any is INCOMPLETE)

| # | Field | Type / enum | Set by | Carrier **today** | Machine-readable? |
|---|---|---|---|---|---|
| 1 | `rune_id` | `rc-` + 12 hex | `rc runes open` (minted) | ledger item id | **yes** |
| 2 | `goal` | prose, Matthew's words | **Matthew** | contract file + Rune `subject` (short title) | no |
| 3 | `dod` | checklist, falsifiable | **Matthew** | contract file | no |
| 4 | **`appsec_in_scope`** | **`Y` \| `N`** | **Matthew** (in the DoD) | **Rune `subject` stamp + contract file + PR body** | **no — P1.2 ADD** |
| 5 | **`entry_surface`** | **`grok_bots` \| `cursor` \| `claude` \| `supergrok`** | intake (CoS/PE) | **Rune `subject` stamp + contract file** | **no — P1.2 ADD** |
| 6 | `human_gate` | `none` \| `matthew` \| `appsec` \| `cos` \| `sage` (`money` accepted by `runes.py` but schema-invalid — use `matthew`, F1) | intake (CoS/PE) | ledger `human_gate` via `--gate` | **yes** |
| 7 | `3model_pass` | `claude:PASS\|FAIL\|MISSING` + `codex:…` + `grok:…` | each reviewing model | PR body + loop DIGEST gate line | no — P1 CI label |
| 8 | `longship_ready` | bool | craft owner after 3-model PASS | Longship doc (`land_requested`) | **yes** |

**Optional (real flags only, verified present in `runes.py`):** `--dep <rune-id>` (repeatable) ·
`--priority 1..4` · `--strand-id` · `--formula-ref <pack path>` · `--longship-id` · `--mist`.

**Do NOT use `--kind`.** It is a documented flag that writes a field the ledger schema rejects
(`assertedOpen` is `additionalProperties: false`). Use `--priority` + the subject stamp instead. See
runbook §11 F2.

**Do NOT invent flags.** There is no `--appsec-in-scope` and no `--entry-surface` flag in `runes.py`
(verified this session: a `grep` of `runes.py` matches the real `--gate`/`--kind` flags but returns
nothing for these two). Fields 4 and 5 live in the subject stamp and this contract file until P1.2 adds
them to the schema.

---

## 2. Enum definitions (normative)

### `appsec_in_scope`

| Value | Meaning | Consequence |
|---|---|---|
| **`Y`** | The tip touches a security-sensitive surface: auth, secrets, crypto, sessions, untrusted input parsing, file upload, deserialization, SQL, shell, network egress, third-party integration, CSP, prod money path. | Agents implement + self-review + 3-model. **Land BLOCKED** until an AppSec **SHIP / SWC** DIGEST exists for this tip. Open a separate `--gate appsec` land-gate Rune (§5). |
| **`N`** | None of the above. | Agents PR → 3-model → craft-approve → Longship → **Sage** on a CoS tip. AppSec stays silent **unless** a security surface appears mid-flight → then HOLD + tip **CoS** and amend to `Y`. |

**No third value.** Absent / blank / "maybe" = **INCOMPLETE contract** → bounce to CoS. An agent must
never guess it, and this is **not** a reason to tip Matthew.

### `entry_surface`

| Value | Surface | On-box execution today |
|---|---|---|
| `claude` | Claude Code / Claude Max | **Yes** — native host |
| `cursor` | Cursor IDE / cloud agents / DA | **Yes** — `rc` CLI + hooks + skills + agents (slash commands not wired; `host-support.json`) |
| `grok_bots` | Fleet Grok Bot agents (passive thin relay, CoS delegation) | **No host adapter — relay entry.** The `rc runes open` happens on an on-box harness |
| `supergrok` | SuperGrok / xAI craft harness | **No host adapter — relay entry** |

Exactly four values. **No fifth harness.** `entry_surface` records *how work entered* — it is
**orthogonal** to `3model_pass` and never substitutes for or double-counts a model sign-off. Matthew is
**never** asked to pick a harness.

### `human_gate`

| Value | Wall | Auto-claim | Notes |
|---|---|---|---|
| `none` | — | **eligible** (Verðandi) | The normal craft Rune, including when `appsec_in_scope=Y` (§5) |
| `matthew` | Matthew forever-gate (M1–M6) | refused | money · secrets · irreversible · live blast · capacity · trust-widening posture |
| `appsec` | AppSec ship/no-ship (A1) | refused | the **land-gate** Rune for `appsec_in_scope=Y` |
| `cos` | CoS classification / relay decision | refused | use when the gate itself is unknown (fail-closed) |
| `sage` | SCM mutate / land execution (S1) | refused | Sage sole mutate |
| `money` | money wall | refused | **CAVEAT:** accepted by `rc runes open --gate money` (`money` is in `runes.py` `HUMAN_GATES`) but **absent from the ledger schema enum** → writes a schema-invalid event. **P0: use `--gate matthew` and write "money" in the subject.** Runbook §11 F1 |

`human_gate != none` refuses **claim/sling outright**, and `--force` does **not** bypass it (`--force`
only steals from another `hook_owner`). So a gate is a *claim-time* wall, not a land-time wall — which is
why `appsec_in_scope=Y` uses the two-Rune pattern in §5.

**Fail-closed:** unknown / absent / unparseable gate → **HOLD the land**, tip **CoS**, never proceed,
never interrupt Matthew.

---

## 3. Paste-ready contract block

```yaml
# CONTRACT — factory Rune
rune_id:          rc-............          # filled from `rc runes open` output
goal:             |                        # Matthew's words — do not re-scope
                  <one or two sentences>
dod:                                       # falsifiable; Matthew owns this list
  - <observable outcome 1>
  - <observable outcome 2>
appsec_in_scope:  Y | N                    # REQUIRED — Matthew, in the DoD
entry_surface:    grok_bots | cursor | claude | supergrok   # REQUIRED
human_gate:       none | matthew | appsec | cos | sage   # P0 set; `money` is in runes.py but schema-invalid → use matthew + "MONEY" in subject (§2, F1)
3model_pass:      claude:MISSING  codex:MISSING  grok:MISSING
longship_ready:   false
# optional
deps:             []                       # --dep <rune-id>
priority:         3                        # --priority 1..4
formula_ref:      <PE pack path>           # --formula-ref
land_gate_rune:   rc-............          # the --gate appsec|matthew Rune, if any
appsec_digest:    <path>                   # REQUIRED before land when appsec_in_scope=Y
```

### Subject-stamp grammar (because fields 4–5 have no schema carrier)

```
<short title> · appsec:<Y|N> · entry:<grok_bots|cursor|claude|supergrok>
```

`subject` is truncated to **140 chars** by `runes.py` — keep the title ≤ ~90 chars so the stamp
survives. **A Rune whose stamp got truncated is defective: open a new Rune that references the old one.** Never hand-edit the ledger
(append-only, invariant I2).

---

## 4. 6-field mapping (this contract IS a 6-field contract)

| CoS 6-field | Factory binding |
|---|---|
| **objective** | `goal` |
| **output schema** | `dod` + the loop DIGEST path |
| **tool allowlist** | harness/CLI pick (Claude Max → Codex → Grok) · `rc runes` / `rc longship` · **no SCM (Sage)** |
| **budget** | effort ladder + real concurrency levers (never `/max-parallel`) |
| **boundary** | `human_gate` · `appsec_in_scope` · NOT-MY-JOB: merge → Sage; money/secrets → Matthew; AppSec verdict → AppSec |
| **done-condition** | `dod` + `3model_pass` (3× PASS) + `longship_ready` |

---

## 5. Open pattern (normative — three shapes only: A, B, C)

**A. `appsec_in_scope=N`, no forever-gate — one ungated Rune:**

```bash
rc runes open "<title> · appsec:N · entry:<surface>"
```

**B. `appsec_in_scope=Y`, or a forever-gate on the *land* while craft is safe — two Runes:**

```bash
CRAFT=$(rc runes open "<title> · appsec:Y · entry:<surface>")          # ungated; `open` prints only the new id on stdout (runes.py cmd_open)
rc runes open "AppSec SHIP/SWC for $CRAFT · appsec:Y · entry:<surface>" --gate appsec --dep "$CRAFT"  # the visible land wall
```

The craft Rune claims and hangs on the Oath-hook (MUST-RUN); the gate Rune sits in **Skuld**, never
appears in `rc runes ready`, and refuses claim even with `--force`.

**C. The whole item *is* the wall** (e.g. "mint a secret", "approve spend") — nothing to craft:

```bash
rc runes open "<title> · appsec:<Y|N> · entry:<surface>" --gate matthew
```

**Never** put `--gate appsec` on the craft Rune of an `appsec_in_scope=Y` item. It is unclaimable by
anyone (including AppSec) and stalls silently as apparent fleet idleness.

---

## 6. Worked examples

### 6.1 Ungated · entry `grok_bots` (relay entry)

```yaml
rune_id:         rc-a1b2c3d4e5f6
goal:            "Restore the dependency-sweep note in the ops README so the weekly pattern is documented."
dod:
  - README ops section names the weekly sweep + the skill that runs it
  - no version numbers asserted that are not verified in-repo
appsec_in_scope: N
entry_surface:   grok_bots        # Matthew asked in a Grok bot session; CoS relayed the 6-field
human_gate:      none
3model_pass:     claude:PASS  codex:PASS  grok:PASS
longship_ready:  true
```

```bash
rc runes open "Restore ops README dependency-sweep note · appsec:N · entry:grok_bots"
```

Tail: claim → PR → 3-model → craft-approve → `rc longship add` → `land-request` → CoS tips Sage →
merge-when-green. **Matthew tips: 0.**

### 6.2 AppSec-in-scope · entry `cursor` (two-Rune pattern)

```yaml
rune_id:         rc-7cad3ad502e5          # craft Rune, UNGATED
goal:            "Intake tokens must be rejected when the signature check is skipped."
dod:
  - skipped-signature path returns 401 with a test proving it
  - no secret value in any log line or test fixture
appsec_in_scope: Y
entry_surface:   cursor
human_gate:      none                     # on the CRAFT Rune — deliberately
land_gate_rune:  rc-7d740dc18b5e          # --gate appsec --dep rc-7cad3ad502e5
appsec_digest:   <REQUIRED before land — path to AppSec SHIP/SWC DIGEST>
3model_pass:     claude:PASS  codex:PASS  grok:PASS
longship_ready:  false                    # stays false until appsec_digest exists
```

```bash
CRAFT=$(rc runes open "Reject intake token on skipped sig check · appsec:Y · entry:cursor")
rc runes open "AppSec SHIP/SWC for $CRAFT · appsec:Y · entry:cursor" --gate appsec --dep "$CRAFT"
```

Sage **refuses** this land if the tip carries no `appsec_digest` path. The AppSec verdict goes to
**AppSec** (A1), **never** to Matthew.

### 6.3 Money wall · entry `supergrok` (forever-gate, F1 workaround)

```yaml
rune_id:         rc-9f8e7d6c5b4a
goal:            "Unlock the paid tier on the data API so the nightly pull stops truncating."
dod:
  - spend approved by Matthew with the monthly ceiling written down
  - key delivered by the human secret path (no chat paste)
appsec_in_scope: Y                        # secret handling
entry_surface:   supergrok                # relay entry — no on-box adapter
human_gate:      matthew                  # NOT --gate money: schema enum lacks `money` (F1)
3model_pass:     claude:MISSING  codex:MISSING  grok:MISSING   # no craft loop — the whole item is the wall
longship_ready:  false
```

```bash
rc runes open "Unlock paid data API tier (MONEY) · appsec:Y · entry:supergrok" --gate matthew
```

CoS tips Matthew **once**, as **M1 Money** (co-stamped **M2 Secrets** for the key), using the runbook
§7.4 template: one decision, recommended option first and marked primary, default on no reply = **park**.
No craft content in that tip.

### 6.4 Ungated · entry `claude` (on-box craft)

```yaml
rune_id:         rc-0f1e2d3c4b5a
goal:            "Fix the broken cross-link from the Runes concept doc to the ready-queue doc."
dod:
  - link resolves; repo doc/link check passes
appsec_in_scope: N
entry_surface:   claude           # Matthew started it in a Claude Code session on the box
human_gate:      none
3model_pass:     claude:PASS  codex:PASS  grok:PASS
longship_ready:  true
```

```bash
rc runes open "Fix Runes concept → ready-queue cross-link · appsec:N · entry:claude"
```

Same tail as 6.1. **Matthew tips: 0.**

---

## 7. Validation rules (fail-closed)

| Check | On violation |
|---|---|
| All eight required fields present | **INCOMPLETE** → bounce to **CoS**. Never guess; never tip Matthew for it. |
| `appsec_in_scope` ∈ {Y, N} | INCOMPLETE → CoS |
| `entry_surface` ∈ the four values | INCOMPLETE → CoS. A fifth value is a lock violation, not a new option. |
| `human_gate` ∈ {none, matthew, appsec, cos, sage} (`money` = schema-invalid on P0 → open as `matthew` + "MONEY" in subject, F1) | **Unknown gate ⇒ HOLD the land + tip CoS.** Never proceed. |
| `appsec_in_scope=Y` **and** no `appsec_digest` at land time | **Sage refuses** → CoS. Not a Matthew tip. |
| `3model_pass` has any `MISSING`/`FAIL` | Rune **stays out of the Longship**. Status is `NOT_DONE`; do not add-then-promise. |
| Same model stamped twice in `3model_pass` | Gate **void** — re-run on a different model. |
| Subject stamp truncated / absent | Rune is **defective** → open a new Rune that references the old one. Never hand-edit the ledger. |
| Gate on the craft Rune of an `appsec_in_scope=Y` item | **Wrong shape** → use §5 pattern B. |
| Security surface appears mid-flight while `appsec_in_scope=N` | HOLD land · open the `--gate appsec` Rune · amend to `Y` · tip **CoS** |

---

## 8. Refusals / anti-patterns

- **Craft-approve read as merge.** Agents approve polish; **Sage** merges. Longship `land-request`
  records intent and prints *"No merge performed."*
- **AppSec countersign treated as optional polish**, or 3-model PASS offered as a substitute for it.
- **Routing an AppSec question to Matthew.** A1 → AppSec. Mis-routing burns the gate and the escalation
  diet at once.
- **Guessing `appsec_in_scope`.** Bounce to CoS instead.
- **Making Matthew pick a harness**, at intake or mid-craft.
- **Counting the entry surface as a review pass**, or counting one model twice.
- **Inventing `--appsec-in-scope` / `--entry-surface` / `/max-parallel`** or any other CLI that does not
  exist.
- **`--kind`** on a factory Rune (writes a schema-rejected field).
- **Enabling Longship auto-merge**, weakening Thing / `guard-destructive`, or force-pushing "just this
  once" — refuse at the agent; only a genuine policy change is M3/M6.
- **Adding `on.pull_request.paths` to a required workflow**, or reopening path-gate work as SF work —
  **CLOSED**.
- **BMA / outbound under Matthew's identity.** Never.

## 9. Non-claims

Contract template only. Opens no Rune, flips no posture (`runes:` untouched), mutates no SCM, sends
nothing. Does **not** authorize P1.1 ungated Sage auto-MWG or P1.4 tribunal auto-merge — both HOLD
pending a written AppSec countersign. The `money` gate caveat (F1) and the missing carriers for fields
4–5 (F3) are **open P1 asks**, documented rather than worked around silently. `skill ≠ meter`.
