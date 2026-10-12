# Software Factory runbook (P0) — the ops default path + escalation diet

> **What this is.** The ops default path for factory work: one written loop from *goal + DoD*
> to *Sage merge*, enterable from any of four harnesses, plus the escalation diet that keeps
> Matthew out of the craft loop. It **extends** the landed Runes / Oath-hook / Strand / Longship
> machinery and the CoS 6-field contract — **no new product, no new CLI, no new name.**
>
> **Companion:** the intake contract template — [`software-factory-rune-contract.md`](../plugins/ravenclaude-core/templates/software-factory-rune-contract.md).
> **Mechanism SSOT:** [`runes-ready-queue.md`](runes-ready-queue.md) · the measured-mechanism concept
> [`runes-ready-queue-oath-hook-longship.md`](../plugins/ravenclaude-core/knowledge/concepts/runes-ready-queue-oath-hook-longship.md) ·
> the CLI itself, `plugins/ravenclaude-core/scripts/runes.py`.

| Field | Value |
|---|---|
| **Scope** | Docs + policy only. No code edit · no SCM mutate · no push · no PR · no posture flip · no Slack/email · no Matthew tip is performed *by this runbook*. |
| **Model / lens** | claude-max · `p0-policy-escalation-honesty` |
| **CLI re-verified against** | `plugins/ravenclaude-core/scripts/runes.py` on current `main` (every subcommand and flag cited below exists there). |
| **Longship `auto_merge`** | **false** — hard-coded in `runes.py`, never flipped by this runbook (see §6, §10). |

Everything below is **Runes / Oath-hook / Strand / Longship / forge / CoS 6-field / Sage** — extended,
not replaced. This is **not** a Longship auto-merge enable, **not** a Platform ask (path-gates are
CLOSED, §9), **not** a live `runes: on` flip (§4 is a documented matrix; the posture key is untouched),
and **not** code. Substrate defects found while verifying the CLI are written up as **Propose→Sage** P1
items (§11), not fixed here — PE does not push.

---

## 1. The one loop (harness-agnostic after intake)

```
  Matthew: goal + DoD  (DoD MUST carry appsec_in_scope Y/N)
        │              entered from Grok bots | Cursor | Claude | SuperGrok
        ▼
  [P0.1] CoS/PE 6-field contract  ──►  rc runes open  (Rune minted on accept)
        ▼
  rc runes ready  →  rc runes claim|sling   (Oath-hook binds: hanging ⇒ MUST-RUN)
        ▼
  agents: implement → PR → review → tweak
        ▼
  [P0.3] 3-model DONE: Claude PASS → Codex PASS → Grok PASS   (never same-model sequential)
        ▼
  craft-approve   ◄── this is polish, NOT merge
        ▼
  rc longship open → rc longship add → rc longship land-request   (records intent; never merges)
        ▼
  [P0.4] CoS tips Sage (6-field)  →  Sage merge-when-green, no --admin
        ▼
  done · [P0.5] Matthew craft-review messages for this loop: 0
```

**Two invariants that carry the whole design:**

1. **craft-approve ≠ merge.** Agents approve polish. **Sage** is the only actor that mutates SCM.
   Longship `land-request` is a *record*, not a merge — verified: it prints
   `"Land request recorded for Sage. No merge performed."` and the Longship doc holds `auto_merge: false`.
2. **entry_surface ≠ the review ladder.** `entry_surface` says *how work got in* (one of four
   harnesses). The 3-model DONE gate says *who signed off* (Claude→Codex→Grok). A Rune with
   `entry_surface: grok_bots` still needs all three model passes; a Rune entered from Claude does **not**
   get to count Claude twice. These two fields are orthogonal and must never be collapsed.

---

## 2. P0.1 — Factory runbook stamp (6-field → Rune + DoD)

**Rule:** when CoS/PE **accepts** a Matthew ask as work, the accept opens a Rune. Not before (no
speculative board), not later (no undocumented craft).

The existing fleet 6-field contract maps onto the factory 1:1 — extend, don't replace:

| 6-field | Factory binding |
|---|---|
| **objective** | `goal` — Matthew's words, not a re-scope |
| **output schema** | `dod` + the DIGEST path the loop must produce |
| **tool allowlist** | harness + CLI pick (Claude Max → Codex → Grok); `rc runes` / `rc longship`; **no SCM** (Sage) |
| **budget** | effort ladder + concurrency levers (real ones only — never `/max-parallel`) |
| **boundary** | `human_gate` + `appsec_in_scope` + NOT-MY-JOB (merge → Sage; money/secrets → Matthew) |
| **done-condition** | `dod` + `3model_pass` + `longship_ready` |

**Required fields on every factory Rune** (full spec, enums, and carriers: the contract template):

`rune_id` · `goal` · `dod` · **`appsec_in_scope`** (Y/N) · **`entry_surface`**
(`grok_bots|cursor|claude|supergrok`) · **`human_gate`** (`none|matthew|appsec|cos|sage`; money walls use `matthew`, §11 F1) ·
`3model_pass` · `longship_ready`

**Where each field actually lives today — read this before promising machine-readability.** The ledger
event schema is a **closed set** (`additionalProperties: false`): `assertedOpen` accepts only
`subject, owner, priority, tags, due, human_gate, formula_ref, strand_id, longship_id, mist`. There is
**no** `appsec_in_scope` and **no** `entry_surface` field to write into.

| Field | Carrier **today** (P0) | Machine-readable? |
|---|---|---|
| `rune_id` | ledger item id (`rc-` + 12 hex) | yes |
| `human_gate` | ledger `human_gate` (`rc runes open --gate …`) | yes |
| `goal` / `dod` | the contract file + the tip; Rune `subject` carries the short title | no (prose) |
| **`appsec_in_scope`** | **Rune `subject` stamp + contract file + PR body** | **no — P1.2 ADD** |
| **`entry_surface`** | **Rune `subject` stamp + contract file** | **no — P1.2 ADD** |
| `3model_pass` | PR body / DIGEST gate line | no — P1 CI label |
| `longship_ready` | Longship doc (`land_requested: true`) | yes |

**Subject-stamp grammar (P0 workaround, invent-free — it is just the title string):**

```
<short title> · appsec:<Y|N> · entry:<grok_bots|cursor|claude|supergrok>
```

`subject` is truncated to **140 chars** by `runes.py`, so put the stamp *after* a short title and keep
the title ≤ ~90 chars. A stamp that got truncated away is a **defective Rune** — open a new Rune that references the old one; do not
hand-edit the ledger (append-only, invariant I2).

**Do not** invent `--appsec-in-scope` / `--entry-surface` flags in docs or tips. Verified this session:
`grep` of `runes.py` finds no such flag (while the same `grep` finds the real `--gate` and `--kind`
flags), so these two are genuinely absent from the parser. Adding them is a P1 item (§11 F3).

---

## 3. Multi-harness entry-surface DoD (Matthew HARD — P0.6 folded)

Factory entry is **one of four surfaces**, and the runbook must not require Claude Code.

| `entry_surface` | Role (existing framing) | Can it run `rc runes` **in-session, on this box**? | Evidence |
|---|---|---|---|
| **`claude`** | Claude Code / Claude Max — heavy craft | **Yes** — native host; hooks + skills + agents + slash all supported | `host-support.json` `claude-code` all-true |
| **`cursor`** | Cursor IDE / cloud agents — repo craft entry | **Yes** — CLI + hooks + skills + agents wired; slash commands **not wired** | `host-support.json` cursor: hooks ✅, skills ✅, agents ✅, slash ❌ |
| **`grok_bots`** | Fleet Grok Bot agents — passive thin relay, CoS delegation | **No** — no host adapter, no install lane | `host-support.json` has a `grok` row with every component `supported: false` ("no --host grok install path"); `scripts/ravenclaude` accepts only `--host copilot\|codex\|cursor\|aider\|gemini` |
| **`supergrok`** | SuperGrok / xAI craft harness | **No** — no adapter, no plugin, no host row | `host-support.json` has **no** `supergrok` row; no `--host supergrok` |

**This is the honest shape of "multi-harness", and the runbook is built on it rather than around it:**

- **Two of the four surfaces are relay-entry, not execution-entry.** `grok_bots` and `supergrok` can
  *originate* a factory item and can carry the contract, but the `rc runes open` call happens on an
  on-box harness (`claude` / `cursor` / or a CoS-side `codex`). That is not a gap in Matthew's lock —
  the lock is about **entry**, and relay entry is the pattern the definition already names (Cursor
  active / Grok bots passive → Claude/SuperGrok, Sage sole SCM). It *is* a gap if anyone claims a Grok
  bot runs the ready-queue itself. It does not.
- **Grok-bot entry already has a governed path:** `plugins/grok-bot-delegation` is the CoS SOP for
  exactly this (tight brief → SendToAgent → coordinate), and it already says *escalate to Matthew only
  for decisions, auth, or irreversible actions*. The escalation diet in §7 **extends** that sentence;
  it does not invent a second policy.
- **`runes: on` auto-orientation is host-conditional (MH-18).** SessionStart Oath-hook
  surfacing/auto-claim fires only on SessionStart-hook hosts. `aider`/`windsurf` are unsupported;
  `grok` is in the map as unsupported on every component and `supergrok` has no row. **The CLI works regardless of posture** — that is
  what makes relay entry viable.

### Entry-surface DoD (must hold for P0 to be called done)

- [x] **E1** — Every factory Rune records `entry_surface` ∈ {`grok_bots`,`cursor`,`claude`,`supergrok`},
  by subject stamp + contract (carrier limits stated, not hidden).
- [x] **E2** — After intake the loop is identical for all four: same Rune → PR → 3-model DONE →
  Longship land-request → Sage merge. No surface gets a private tail.
- [x] **E3** — CoS 6-field / PE pack intake **accepts all four**; relay entry (`grok_bots`,
  `supergrok`) is explicitly specified (§3.1) so it is not a dead end.
- [x] **E4** — 3-model DONE is orthogonal: entry surface never substitutes for a model pass, and never
  double-counts one.
- [x] **E5** — No fifth harness, no new product name, and **Matthew is never asked to pick a harness** —
  mid-craft or at intake. Harness choice is a fleet routing decision under the existing surface ladder.
- [x] **E6** — Nothing in this runbook requires Claude Code. The only Claude-Code-specific artifacts are
  *optional conveniences* (slash commands, agents); the factory path is `rc` CLI + tips.

### 3.1 Relay entry (the two surfaces with no on-box adapter)

```
Matthew (in a Grok bot / SuperGrok session): goal + DoD + appsec_in_scope
        ▼  thin relay — brief only, no craft narration
CoS (grok-bot-delegation SOP) records the 6-field contract
        ▼
on-box harness (claude | cursor | codex) runs:
    rc runes open "<title> · appsec:<Y|N> · entry:grok_bots" [--gate …]
        ▼
…identical tail (claim → craft → 3-model → Longship → Sage)
```

Rule: **the relay does not get to drop a field.** If a relayed brief arrives without `appsec_in_scope`,
the receiving harness does **not** guess and does **not** tip Matthew for a craft-adjacent clarification
— it asks **CoS**, who either has it in the contract or answers from scope. Only if the answer is
genuinely unknown *and* the surface is security-adjacent does it become a HOLD (§9 fail-closed).

---

## 4. P0.2 — Runes posture matrix (documented; no live flip)

Posture key SSOT: `runes: off | on` in `.ravenclaude/comfort-posture.yaml`. **Absent ⇒ off.**

| Where | `runes:` today | Effect |
|---|---|---|
| A factory repo's `.ravenclaude/comfort-posture.yaml` | **key absent ⇒ off** unless explicitly set | No SessionStart auto-orient. **`rc runes` CLI still works.** |
| A consumer repo with no `comfort-posture.yaml` at all | **⇒ off** | same |
| Any other factory repo | assume **off** until its file is read | never assert `on` from memory |

**Factory-host default matrix (recommendation — requires CoS GO to apply, NOT applied here):**

| Host / surface | Recommend `runes:` | Why |
|---|---|---|
| `claude` (Claude Code / Max) on a factory repo | **on** | full hook support; Oath-hook MUST-RUN is the anti-idle mechanism |
| `cursor` on a factory repo | **on** | hooks, skills and agents supported (slash is not); SessionStart Oath-hook orientation applies |
| `codex` / `copilot` / `gemini` (CoS-side) | **off** | relay/assist roles; auto-claim there fragments ownership |
| `grok_bots` / `supergrok` | **n/a** | `grok` row present but unsupported (no `--host grok`); no `supergrok` row — posture key has no meaning; relay only |
| `aider` / `windsurf` | **n/a** | hooks unsupported (`host-support.json`) |

**Auto-claim safety — already landed, re-verified, not re-implemented:**
- `auto_claim_next_ungated` claims only Verðandi Runes: unblocked **and** ungated **and** unclaimed.
- Any `human_gate != none` **refuses** — including `money`. Verified: `claim` on an `appsec`-gated Rune
  → `REFUSED: … human_gate=appsec — Matthew/CoS/AppSec/Sage wall; never auto-claim`.
- Auto-claim **never** touches Longship merge or Sage land.
- Kill switch: set `runes: off` + Save.

**HARD:** no `runes: on` flip in any repo without CoS GO. This section is the matrix, not the act.

---

## 5. P0.3 — 3-model DONE before Longship add

**Gate:** an iterative craft Rune is **NOT DONE** until **three different models** each stamp PASS:
**Claude → Codex → Grok**. Never same-model sequential. No substitutes and no skips: a leg that is MISSING means the Rune is
**NOT_DONE**.

**Placement — this is the part that is easy to get wrong:** the 3-model gate sits **before
`rc longship add`**, not before merge. Reason: the Longship is the delivery batch handed to Sage. A Rune
that enters a Longship un-stamped makes Sage the reviewer of record, which puts the merge authority back
in the craft loop.

Checklist on the craft PR before `rc longship add <ls> <rune>`:

- [ ] Claude pass — stamp + lens named
- [ ] Codex pass — **different** lens (structure/completeness), not a Claude prose redo
- [ ] Grok pass — operator skim lens
- [ ] Each stamp records `Model:` + `Sign-off: PASS`
- [ ] Zero same-model sequential passes; any MISSING leg = NOT_DONE (no ladder skip)
- [ ] CI green under the **existing** required checks (aggregator name intact)
- [ ] `appsec_in_scope` re-checked against what the diff actually touched (§8 mid-flight rule)

**Tip language (paste-ready, for the craft owner → CoS):**

> `3-model DONE: Claude PASS | Codex PASS | Grok PASS` — Rune `<rc-…>`, PR `<#>`, CI green,
> `appsec_in_scope=<Y/N>`. Added to Longship `<ls-…>`. Requesting Sage land. No Matthew decision in this tip.

If any model is MISSING: the honest stamp is `Status: NOT_DONE` and the Rune **stays out of the
Longship**. Do not add-then-promise.

---

## 6. P0.4 — Sage MWG land-request playbook

**Sage is the sole SCM mutate.** Longship never merges. Matthew never clicks merge for an ungated Rune.

```bash
rc longship open --title "<batch title>"          # → ls-<slug>
rc longship add   ls-<slug> rc-<rune> [rc-<rune>…]
rc longship land-request ls-<slug>                # records intent; NO merge
rc longship show  ls-<slug>                       # auto_merge:false · land_requested:true
```

**Verified output shape** (`land-request` on a Longship with one Rune):

```json
{ "auto_merge": false, "land_requested": true,
  "longship_id": "ls-sf-demo-delivery",
  "message": "Land request recorded for Sage. No merge performed.",
  "rune_ids": ["rc-7cad3ad502e5"] }
```

**The tip CoS sends Sage — 6-field, and it contains no Matthew decision:**

1. **objective** — land Longship `ls-<slug>` (Runes `rc-…`), PR `<#>`: merge-when-green, squash, **no
   `--admin`**, no force.
2. **output schema** — one line back: PR, merge SHA, required-checks state; or the named blocker.
3. **tool allowlist** — `gh` read/checks + merge on this PR only. No other repo. No prod dispatch.
4. **budget** — effort 0–1; serial (sole SCM).
5. **boundary** — Sage sole mutate · **no `--admin`** · no force-push (Thing DENY floor) · never BMA ·
   if `appsec_in_scope=Y` and no SHIP/SWC DIGEST path is in this tip → **refuse and bounce to CoS**.
6. **done-condition** — merged green, or a named blocker back to CoS.

**Sage's refusal duties (fail-closed, and they are duties, not options):**

| Sage sees | Sage does |
|---|---|
| `appsec_in_scope=Y`, no AppSec SHIP/SWC DIGEST path in the tip | **Refuse** → CoS. Not a Matthew tip. |
| `human_gate` ∈ {matthew, money} | **Refuse** → CoS; CoS tips Matthew the *gate*, not the PR |
| `human_gate` unknown / absent / unparseable | **Refuse** → CoS (fail-closed on unknown gate) |
| 3-model stamp incomplete | **Refuse** → craft owner (not CoS, not Matthew) |
| Required check red / flaky | Drive or bounce to craft owner; **never** `--admin` |
| Asked to enable Longship auto-merge | **Refuse** — needs AppSec countersign + CoS GO (P1.1) |

**P0 boundary:** Sage still merges **on a CoS tip**. Sage *auto*-MWG straight off the Longship queue is
**P1.1** and is HOLD pending an AppSec countersign DIGEST. Do not pre-enable it by treating this
playbook as the countersign.

---

## 7. P0.5 — The escalation diet (core deliverable)

**Premise:** every tip to Matthew is a debit against "human out of the craft loop." Over-escalation
rebuilds the loop with extra steps — the metric is falsifiable: *escalations to Matthew that are not
forever-gates = **0***.

### 7.1 The closed allowlist — the ONLY things that reach Matthew

If it is not in this table, it is not a Matthew tip.

| # | Bucket | Contains | Co-signer |
|---|---|---|---|
| **M1** | **Money** | purchase · spend · billing · paid API unlock · any live money path | — |
| **M2** | **Secrets** | mint · rotate · dual-write. Never a chat paste; never "just this once" | — |
| **M3** | **Irreversible** | prod-data / vault deletes · SCM force beyond lease · force-push or hard-rule exception · domain/DNS ownership transfer | + AppSec on force-push / hard-rule |
| **M4** | **Live blast / outbound identity** | prod `workflow_dispatch` · prod auth · CSP enforce GO · customer contact · outbound mail · job-apply **send** · anything sent under Matthew's identity. **Never BMA.** | — |
| **M5** | **Capacity** | CreateAgent ADDs · new bot · fleet capacity | — |
| **M6** | **Trust-widening posture** | `auto_install: auto` · `cheap_lane` on · apply-execute unlock · `runes: on` enable · weaken Thing / `guard-destructive` · AppSec policy exception · **Longship auto-merge enable** | **+ AppSec (required)** |
| **IN** | **Goal + DoD** | Matthew → fleet. This is the factory **input**, not an escalation. DoD must carry `appsec_in_scope` Y/N. | — |

Two buckets that look like Matthew and are not:

| # | Bucket | Goes to | Note |
|---|---|---|---|
| **A1** | AppSec ship / no-ship / SWC / NO-SHIP on a security-class tip | **AppSec** via CoS | Forever-human — but the human is **AppSec**. Routing this to Matthew is itself a diet violation. |
| **S1** | Merge execution, rebase, conflict, branch hygiene, drive-to-green | **Sage** (mutate) / craft owner (fix) | Never Matthew, never "just approve this". |

### 7.2 The deny list — what CoS must NOT tip Matthew

| # | Never-tip | Absorbed by | Why it is not a gate |
|---|---|---|---|
| 1 | Craft nits, naming, style, structure preference, refactor taste | craft agents | Definition of "out of the craft loop" |
| 2 | Review comments / re-review requests / "does this look right?" | 3-model ladder | The ladder *is* the reviewer |
| 3 | CI red on a craft PR (lint, types, flake) | craft owner → Sage | Green is the fleet's job |
| 4 | Rebase / conflict / branch hygiene | Sage | S1 |
| 5 | Which model reviews, in what order, or a ladder re-run | fleet | Standing HARD already answers it |
| 6 | **Which harness to use / entry-surface choice** | fleet routing | Explicit pack lock: never make Matthew pick a harness |
| 7 | Merge timing / MWG click on an **ungated** Rune | Sage on CoS tip | The merge-click loop is exactly what P0 removes |
| 8 | AppSec ship/no-ship questions | **AppSec** (A1) | Mis-routing burns the gate *and* the diet |
| 9 | Status pings, progress narration, "are we still good?" | rolling board | A tip with no decision in it is not a tip |
| 10 | A decision already recorded in an SSOT DIGEST | CoS cites the DIGEST | Re-litigation is a second tax on the same decision |
| 11 | Permission the fleet already documented as held | CoS | Ask-for-what-you-have is over-escalation |
| 12 | Process/runbook ambiguity resolvable from SSOT | CoS resolves **and records** | Silent resolution is how runbooks rot |
| 13 | Choosing between two acceptable implementations | craft agents; record the choice | Craft judgment |
| 14 | "Should we add a CI path-filter / reopen the path-gate work?" | **nobody — CLOSED** | Platform fold §9; path-filter-on-required-check Pending-forever risk |
| 15 | "Can we turn on Longship auto-merge to go faster?" | refuse; P1.1 needs AppSec countersign + CoS GO | Not a Matthew ping — a gated ADD |
| 16 | Requests to bypass Thing / force-push "just this once" | **refuse at the agent** (M3/M6 only if a genuine policy change) | A bypass request is not an escalation; it is a denial |

### 7.3 Routing rules

1. **Default is absorb.** Unlisted → fleet. Never "tip Matthew to be safe" — that is the failure mode,
   not the safe choice.
2. **Fail-closed ≠ tip Matthew.** Unknown/absent/unparseable `human_gate`, or a security surface that
   appears mid-flight: **HOLD the land** and tip **CoS**. CoS classifies. Only a *classified* M-bucket
   reaches Matthew. Unknown gate never means "proceed" and never means "interrupt Matthew".
3. **One gate per tip, one decision per tip.** Name the bucket (M1–M6), the exact decision, the default
   if there is no reply (park/HOLD), and reversibility. No bundled craft status.
4. **Batch, don't interrupt.** M-bucket but not blocking → the Monday rolling-board refresh. Interrupt
   only when *blocking* **and** *irreversible if guessed*.
5. **Matthew-facing choices follow the menu HARD:** recommended option **first** and marked **primary**,
   with an explicit recommendation. Never a bare unordered menu.
6. **Budget: ≤1 Matthew tip per Rune; 0 craft-review messages.** A second tip on the same Rune is a
   **diet defect** → record it in the loop DIGEST with the cause.
7. **Anti-starvation (the diet's own failure mode).** Absorbing must not become silence: anything
   HOLDing on an M-bucket for **>1 business day** must appear on the rolling board. A starved
   money/secrets gate is as much a failure as an over-escalation — it is just quieter.
8. **No BMA. Ever.** Not as a relay, not as a convenience, not under Matthew's identity.

### 7.4 Tip template (M-bucket only)

```
GATE: M<n> <bucket>            e.g. M2 Secrets
DECISION (one): <exactly what is being asked — a single yes/no or a named pick>
RECOMMENDED: <option 1, primary> — <one line why>
ALTERNATIVES: <option 2> · <option 3>
BLOCKS: Rune rc-… / Longship ls-… / PR #…  (or: nothing blocked — batched)
IF NO REPLY: <park | HOLD> — default is never "proceed"
REVERSIBLE: yes/no — <how, or why not>
NOT ASKED: no craft review, no merge click, no harness pick
```

---

## 8. AppSec-in-scope routing

**DoD input:** `appsec_in_scope: Y | N`. Matthew declares it. It is a **required** DoD field — a
contract without it is incomplete and gets bounced to CoS (not to Matthew as a craft question, and never
guessed by an agent).

| `appsec_in_scope` | Agents may | Land | Who clears | Rune shape |
|---|---|---|---|---|
| **N** | implement · PR · 3-model review · craft-approve | CI green + 3-model PASS + Sage on CoS tip | Sage | craft Rune **ungated** |
| **Y** | implement · PR · 3-model review · craft-approve | **BLOCKED** until an AppSec **SHIP / SWC** DIGEST exists for this tip | **AppSec**, then Sage | craft Rune **ungated** + a separate **`--gate appsec` land-gate Rune** |

### 8.1 Why `appsec_in_scope=Y` does **not** mean `--gate appsec` on the craft Rune

This is the one place where the obvious implementation is wrong, and it is verified behaviour, not a
reading:

`human_gate` is a **claim-time** wall, not a land-time wall. `runes.py` refuses `claim`/`sling` outright
when `human_gate != none`, and **`--force` does not bypass it** (`--force` only steals a Rune from
another `hook_owner`). Verified:

```
$ rc runes claim rc-7d740dc18b5e
REFUSED: Rune rc-7d740dc18b5e has human_gate=appsec — Matthew/CoS/AppSec/Sage wall; never auto-claim
$ rc runes claim rc-7d740dc18b5e --force
REFUSED: … human_gate=appsec … (identical)
```

So opening the *craft* Rune with `--gate appsec` makes it **unclaimable by anyone** — which contradicts
the AppSec slice ("agents may implement + self-review; land blocked until SHIP/SWC"). It would not fail
loudly; it would just quietly stall the Rune in Skuld and look like fleet idleness.

**Correct P0 pattern — two Runes, both real CLI, verified working:**

```bash
# 1) craft Rune — ungated so agents can actually claim and work it
CRAFT=$(rc runes open "Harden intake token check · appsec:Y · entry:cursor")

# 2) land-gate Rune — the visible AppSec wall, depends on the craft Rune
rc runes open "AppSec SHIP/SWC for $CRAFT · appsec:Y · entry:cursor" --gate appsec --dep "$CRAFT"
```

The craft Rune claims normally and hangs on the Oath-hook as MUST-RUN; the gate Rune sits in **Skuld**
(facet for gated/owed), never auto-claims, never reaches `rc runes ready`, and refuses claim even with
`--force`. The wall is visible and machine-enforced at the queue, while craft proceeds.

Same shape for an M-bucket wall on a Rune whose craft is safe (e.g. code is fine, the *enable* needs
Matthew): craft Rune ungated + `--gate matthew` land-gate Rune with "money" in the subject for money walls (never
`--gate money` on P0 — see §11 F1). When the
**whole** item is the wall (e.g. "mint a secret"), open it gated directly — there is nothing to craft.

### 8.2 Mid-flight security surface (the AppSec silent case)

`appsec_in_scope=N` at intake, and the diff turns out to touch auth / secrets / crypto / untrusted input
/ file upload / deserialization / SQL / shell / egress / third-party integration:

1. **HOLD the land** immediately (do not add to a Longship; if already added, tell Sage to refuse).
2. Open the `--gate appsec` land-gate Rune against the craft Rune.
3. Tip **CoS** (not Matthew) — CoS routes to AppSec (A1).
4. Amend `appsec_in_scope` to **Y** in the contract file and, if the subject stamp is now wrong,
   open a new Rune that references the old one (`runes.py` has no reopen subcommand). Never edit the ledger in place (append-only).
5. Do **not** treat 3-model PASS as a substitute for AppSec countersign. Three models agreeing is craft
   polish; the countersign is a trust boundary. Conflating them is the top-severity risk.

### 8.3 Anti-patterns (carried from the AppSec fold, none of them softened)

- AppSec countersign treated as optional polish.
- "Craft-approve when polished" read as including money / secrets / hard-rule bypass.
- Auto-flipping a security posture default because it was blocking a loop.
- Same-model rubber-stamp on a security tip.
- Routing an AppSec question to Matthew (burns the gate *and* the diet).

---

## 9. Platform slice — CLOSED (no SF work here)

The path-gate roadmap is fully landed (aggregator required check `"Validate manifests and hooks"`).

| Do | Do NOT |
|---|---|
| PR → green under **existing** required checks → Sage | **Never** add `on.pull_request.paths` to a required workflow (Pending-forever) |
| Keep required-check names stable (aggregator name intact) | Do not open a Platform PR "to enable the factory" — none is needed |
| Treat the required-check binding as standing hygiene | Do not reopen path-gates as SF work; do not tip Matthew about them (deny-list #14) |
| forge tips hit the same Validate Marketplace / ratchet rules | No separate forge CI workflow |

Dependabot majors stay **HOLD** pending AppEng — out of path-gate, out of this runbook.

---

## 10. Worked example — one full loop, invent-free

Commands below are the **real** CLI (`rc runes` / `rc longship`). Scenario: AppSec-in-scope work entered
from **Cursor**.

```bash
# ── intake (P0.1) ── CoS accepted a Matthew goal+DoD; DoD says appsec_in_scope=Y
$ export RC_ACTOR=claude-craft
$ rc runes open "SF demo craft · appsec:Y · entry:cursor"
rc-7cad3ad502e5

$ rc runes open "AppSec SHIP/SWC for rc-7cad3ad502e5 · appsec:Y · entry:cursor" --gate appsec --dep rc-7cad3ad502e5
rc-7d740dc18b5e

# ── the gate is real, at the queue ──
$ rc runes claim rc-7d740dc18b5e
REFUSED: Rune rc-7d740dc18b5e has human_gate=appsec — Matthew/CoS/AppSec/Sage wall; never auto-claim
$ rc runes ready          # gated Rune is absent by construction (Skuld facet)

# ── craft proceeds (ungated) ──
$ rc runes claim rc-7cad3ad502e5
claimed: rc-7cad3ad502e5 → hook_owner=claude-craft

$ rc runes hanging
OATH-HOOK MUST-RUN: 1 Rune(s) hang on hook_owner=claude-craft
rc-7cad3ad502e5  [in_progress/verdandi]  gate=none  hook=claude-craft  p3  SF demo craft · appsec:Y · entry:cursor

# … agents implement → PR → 3-model DONE: Claude PASS → Codex PASS → Grok PASS (P0.3)
# … AppSec writes SHIP/SWC DIGEST → the gate Rune is closed by AppSec (P0.4 precondition)
# ⛔ STOP HERE until that DIGEST path exists AND `rc runes show rc-7d740dc18b5e` shows the gate Rune done.
#    No `rc longship add` / `land-request` before then (Sage refuses, §6).

# ── delivery (P0.4) ──
$ rc longship open --title "SF demo delivery"
longship open: ls-sf-demo-delivery -> .ravenclaude/longships/ls-sf-demo-delivery.json
$ rc longship add ls-sf-demo-delivery rc-7cad3ad502e5
$ rc longship land-request ls-sf-demo-delivery
{ "longship_id": "ls-sf-demo-delivery",
  "message": "Land request recorded for Sage. No merge performed.",
  "rune_ids": ["rc-7cad3ad502e5"] }
$ rc longship show ls-sf-demo-delivery
{ "auto_merge": false, "land_requested": true,
  "notes": "Sage sole land/merge. No factory auto-merge. No BMA.", … }

# ── CoS tips Sage (6-field, §6) → Sage merges when green, no --admin ──
```

**Escalation ledger for this loop:** Matthew tips = **0** (the AppSec countersign is A1 → AppSec, not
M-bucket). Matthew craft-review messages = **0**. `entry_surface=cursor` never changed the tail.
Longship `auto_merge` stayed `false`.

*(Caveat, stated rather than implied: the ids/outputs above are a **runbook rehearsal** of the loop on a
throwaway ledger — real Runes, real gates, real Longship doc, but no PR and no Sage merge. The
plan-level "≥1 end-to-end factory loop with a real merge" DoD is satisfied by the **P0 demo**, which
needs a real repo + Sage; this runbook makes that demo executable, and does not claim to be it.)*

---

## 11. Substrate honesty — six findings that P0 must route, not paper over

Found while verifying the CLI this runbook prescribes against `runes.py` on current `main`. **None are
fixed here** (docs-only; PE does not push). Each is a **Propose→Sage / Platform** P1 item.

| # | Finding | Evidence | P0 workaround | P1 ask |
|---|---|---|---|---|
| **F1** | `rc runes open --gate money` writes `human_gate: "money"`, but the ledger schema's `human_gate` enum is `{none, cos, matthew, appsec, sage}` — **`money` is absent** from both `assertedOpen` and `assertedMeta`. The event is written (append does not validate) and is **schema-invalid**. | `runes.py` `HUMAN_GATES` includes `money`; `ledger-event.schema.json` enums do not. | Use `--gate matthew` for money walls and write "money" in the subject; keep the money semantics in the contract file. | Add `money` to both enums (or drop it from `HUMAN_GATES`) — a one-line divergence that silently invalidates the ledger. |
| **F2** | `rc runes open --kind fix\|feature\|chore` writes `kind`, which is **not** in `assertedOpen.properties` (`additionalProperties: false`) → schema-invalid. `--kind` is a documented flag. | `runes.py` `cmd_open` writes `asserted["kind"]`; `docs/runes-ready-queue.md` documents `--kind`. | **Do not use `--kind`** on factory Runes. Use `--priority` and the subject stamp. | Add `kind` to `assertedOpen` (enum `fix\|feature\|chore`), or route it through `tags`. |
| **F3** | **No carrier for the two new HARD contract fields.** `appsec_in_scope` and `entry_surface` cannot be stored as Rune fields — both asserted defs are closed sets. | schema `additionalProperties: false` on `assertedOpen` **and** `assertedMeta`. | Subject stamp + contract file + PR body (§2). Stated as non-machine-readable rather than implied otherwise. | Exactly **plan P1.2**: add `appsec_in_scope` (bool) + `entry_surface` (enum) to `assertedOpen`/`assertedMeta` + `rc runes open` flags + fail-closed on unknown. |
| **F4** | `ledger.py check` returns **UNKNOWN** (exit-blocking, never downgraded to PASS) when `jsonschema` is not importable. So F1/F2 would not be caught locally; they are caught by reading the schema. | `ledger check` → `UNKNOWN (exit 2): validator_unavailable` when `jsonschema` is absent. | Treat local ledger validation as **unproven**, not green. Validate in CI, not on a dev box. | Confirm a CI job runs `ledger.py check` with `jsonschema` present; if none does, that is the real gap behind F1/F2 surviving. |
| **F5** | `human_gate` is a **claim-time** wall; `--force` does not bypass it. Gating a craft Rune `appsec` makes it unworkable by anyone — the AppSec slice would silently stall. | `runes.py` claim gate refuse + `--force` steals `hook_owner` only. Probe: claim and `claim --force` both REFUSED. | The **two-Rune pattern** (§8.1): ungated craft Rune + `--gate appsec` land-gate Rune with `--dep`. | Consider an explicit `land_gate` distinct from `human_gate`, so "may implement, may not land" is one Rune instead of two. Product decision, not a P0 fix. |
| **F6** | **Two of four HARD entry surfaces have no host adapter.** `grok_bots` and `supergrok` cannot run `rc runes` in-session. The `plugins/grok-bot-{creation,delegation}` plugins are Claude-side SOPs for *making and delegating to* Grok bots — not an install lane. | `scripts/ravenclaude` hosts = `copilot\|codex\|cursor\|aider\|gemini`; `host-support.json` has a `grok` row with every component unsupported (no `--host grok`) and no `supergrok` row; the two grok plugins are skills-only. | **Relay entry** (§3.1), documented as relay rather than claimed as parity. | Decide explicitly: relay-forever (document it as the design) **or** a grok host adapter ADD. Do not leave "multi-harness parity" ambiguous. |

---

## 12. P0 DoD status

| DoD item | State | Where |
|---|---|---|
| Written E2E factory loop, Matthew 0 craft-review messages | **DONE (written + rehearsed)** — real-merge demo still owed by the P0 demo | §1, §10 |
| Written escalation matrix (forever vs auto), AppSec-aligned | **DONE** | §7.1–7.4 |
| Runes posture documented for factory hosts | **DONE (doc-only; nothing flipped)** | §4 |
| Multi-harness entry matrix, runbook does not require Claude Code | **DONE** | §3, E1–E6 |
| Every contract example shows `appsec_in_scope` | **DONE** | contract template + §8, §10 |
| Zero BMA / no invented product names | **DONE** | §0, §13 |
| P0.1 stamp · P0.2 doc · P0.3 gate · P0.4 playbook · P0.5 diet | **DONE** | §2 · §4 · §5 · §6 · §7 |
| Platform CLOSED honored (no path-gate ADD, no path filter) | **DONE** | §9 |
| Longship `auto_merge` remains false | **VERIFIED false** | §6, §10 |

---

## 13. Non-claims

- **Not** an AppSec countersign for **P1.1** (ungated Sage auto-MWG) or **P1.4** (tribunal routine
  auto-merge). Both remain HOLD pending a written AppSec DIGEST. This runbook must not be cited as either.
- **Not** a `runes: on` flip. No `.ravenclaude/comfort-posture.yaml` is written by this runbook. Any flip
  needs CoS GO.
- **Not** a code change. F1–F6 are proposals; the only `ravenclaude-core` changes are the contract template and a one-line pointer in the Runes concept doc.
- **Not** a Longship auto-merge enable, and not a weakening of Thing / `guard-destructive` / the
  force-push DENY floor.
- **Not** money, secrets, CreateAgent, prod dispatch, or outbound anything. No Slack, no email, no
  Matthew tip is sent by this runbook.
- **Not** a new product. No fifth harness, no new name.
- The real-merge P0 demo, the Codex pass, and the Grok pass are **outstanding**.
- `skill ≠ meter`.
