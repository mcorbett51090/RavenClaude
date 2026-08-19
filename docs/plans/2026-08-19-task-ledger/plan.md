# G6 — plan.md: the durable task/change ledger (`forge/task-ledger`)

Run `forge/task-ledger` · Gate G6 (synthesis) · 2026-08-19
Inputs merged: `scope.md`, `research.md`, `claims-table.md` (+ G3b SETTLEMENTS), `probe-jsonl-merge.md`,
`probe-storage-tier.md`, `probe-append-atomicity.md`, `cross-run-reconciliation.md`, `plan-A.md`,
`plan-B.md`, `gap-delta.md`, `critic-brief.md`, `red-team.md`.

**This is the single authoritative plan.** Where the two panels disagreed, this document states the
resolution and the reason; nothing is left as "either." Where an adjudicated ruling was handed down,
it is encoded here and is NOT re-argued.

---

## 0. The claim, stated at its true size — read this before §1

The critic's ruling P2 stands and is encoded at the top rather than buried in a limits section:

> **This does not make Claude Code's prompt-suggester better. Within a single turn it does not
> change what the owner feels.** The suggester still addresses 1–2 of 4 items and cannot be modified
> (`scope.md:25-31`, verified in-session). What this ships is: the next turn, the next session, and
> the next worktree start from the **complete** set; a loss becomes **auditable and recoverable**
> instead of invisible; and an **in-turn nag** fires when a turn ends with action-shaped prose and no
> ledger event — that nag is the only lever in this entire design that acts on the felt problem in
> the turn where it happens.

No heading in the shipped spec may read "THE DROPPED-ITEM GUARANTEE" without that paragraph in the
same breath (critic §7 must-not-do #12). §21 restates the full honest limit list.

---

## 1. Adjudicated rulings — where each one is encoded

| Ruling | Substance | Encoded in |
|---|---|---|
| **A** | Empty/unreadable ledger ⇒ **UNKNOWN, never a clean pass**. Three-valued gate; UNKNOWN blocks. | §8 |
| **B** | **Harvest from existing structured output is the PRIMARY write path** (~85% vs ~15%); in-turn nag with its negative control; CLI is secondary/manual. | §6 |
| **C** | Projection order bug fixed: **read → sort (total order) → dedupe (documented tiebreak) → fold**; collision canary. | §7 |
| **D** | plan-B's incremental **checkpoint is DELETED** entirely (108 ms/yr full fold; its `ts > last_ts` filter silently drops merged events forever). | §7.4 |
| **E** | The axes are not orthogonal. **Verification is stored in exactly ONE place** (`verify` events); `awaiting_verification` and the completed-requires-verification rule are **derived**. | §5 |
| **F** | Owner defect **D3** delivered by an append-only **`provenance` backfill event** emitted post-merge. | §10 |
| **G** | The binding cost is **context tokens**. Brief cap + ageing/rollup + degrade-to-count-digest-pointer. | §9 |
| **H** | **G-LED-07 upheld** — `blocked` derived, never stored — with (1) derivation over `state != done`, (2) the gate emitting the **literal runnable command**, (3) conditional on `ext:<class>:<slug>` external refs. | §5.3, §11 |
| **I** | Four measured bugs fixed, each with a canary: `anyOf` not `oneOf`; semantic (not byte) freshness compare; `redact` in the type enum; higher-entropy `item_id` + mint-time collision check. | §11.3 |
| **J** | **Portability solved**: resolved-path config, and a consumer repo with neither `docs/pm/` nor `.ravenclaude/`. | §3 |
| **K** | Storage path picked + justified; **Phase-0 committability canary with a positive control**. | §3, §11.2 |
| **L** | Append atomicity promoted to **HARD REQUIREMENTS**; the unmeasured gap named and given a settling step. | §6.4, §20 |
| **M** | `set_conservation.py` is the **SSOT owned and shipped by this run**; `verify-before-assert` is its **second caller**; mutual pre-build gate; FORGE registers cross-run deps in the ledger. | §14 |
| **N** | The enumeration checker must be tested against **both** failure directions (under-match and over-match) with fixtures for each. | §11.4 |
| **O** | **No silent truncation, anywhere.** Count + digest + pointer + a `truncated` marker. | §9.3 |

---

## 2. The architecture in one page

```
  WRITE PATH (three lanes, one append primitive)
   1. HARVEST  (PRIMARY, ~85%)  agents already emit `next_actions` -> ledger.py append
   2. NAG      (in-turn)        action-shaped prose + 0 events this turn -> warn (neg. control)
   3. CLI      (secondary)      `rc ledger open|state|verify|link|redact`
                     |
                     v   exactly ONE write() syscall, O_APPEND, never read-modify-write
   ONE SOURCE OF TRUTH
   <ledger_dir>/<YYYY-MM>.jsonl        append-only, COMMITTED, merge=union (scoped)
                     |
                     |  project(): READ -> SORT -> DEDUPE -> FOLD -> DERIVE -> CHECK -> RENDER
                     |             (pure function of (ledger bytes, now); no checkpoint)
                     v
   ledger.py project
        +--> <view_path>                 GENERATED Markdown view (the extended task-list template)
        +--> <ledger_dir>/open-set.json  the Set-Conservation block (SCP)
        +--> verdict PASS | FAIL | UNKNOWN   <- the ratchet; UNKNOWN blocks

  BACKFILL (append-only, post-merge CI):  provenance event  -> binds item -> PR/merge_commit  [D3]
  READ-ONLY BRIDGE (never writes):        ~/.claude/tasks/<uuid>/*.json -> ledger.py bridge
  CROSS-RUN:                              set_conservation.py  <- task-ledger AND verify-before-assert
```

### 2.1 Invariants — everything in this plan enforces one of these

| # | Invariant | Enforced by |
|---|---|---|
| **I1** | A fact is stored in exactly ONE place. `blocked`, `stale`, `dormant`, `awaiting_verification`, counts, digests are **folds**. | G-LED-07, G-LED-08 |
| **I2** | No record is ever rewritten in place. A change is a new event that supersedes; a correction is a `redact`; a late fact is a `provenance` event. | G-LED-09 |
| **I3** | Records are order-independent. The projection imposes a **total** order before it dedupes. | G-LED-04 + shuffled-order canary + collision canary |
| **I4** | **Absence of a closing event means OPEN.** Dropping requires an affirmative append. Absence of the ledger means **UNKNOWN**, never zero. | fold default + §8 three-valued gate |
| **I5** | A model-asserted field is enum-constrained, pointer-typed and gate-resolved, or not stored. | G-LED-01/02/03/06 |
| **I6** | **No render, brief, or gate output ever truncates silently.** | G-LED-11 + ruling O |

---

## 3. Storage, path resolution, and portability (rulings J + K)

### 3.1 The decision, and why

**MEASURED** (`probe-storage-tier.md`, both controls fired):

| candidate | verdict |
|---|---|
| `.ravenclaude/runs/**/ledger.jsonl` | ⛔ **IGNORED** (`.gitignore:4`) — appends succeed, exit 0, never reach main |
| `.ravenclaude/ledger/2026-08.jsonl` | ✅ commits |
| `docs/pm/ledger.jsonl` | ✅ commits |

**Decision:**
- **Source of truth:** `.ravenclaude/ledger/<YYYY-MM>.jsonl` (default `ledger_dir`).
- **Generated view:** `docs/pm/task-list.md` **when `docs/` exists**, else `.ravenclaude/ledger/task-list.md`.

**Justification (this settles plan-B's governance objection, gap-delta disagreement #4):**
1. The JSONL is **machine substrate, not a human document.** A consumer's `docs/` tree is swept by
   docs-site builds, link checkers, spell checkers and (in this repo) `prettier --check .` on the
   whole tree. An 11 MB append-only JSONL under `docs/` is a whole-tree-linter hazard by construction.
2. `docs/pm/` **does not exist in this repo** (critic M1/M2, B-5) and is not on `AGENTS.md`'s own
   committed-tier list (`docs/plans/`, `docs/decisions/`, `docs/research/`) — B reached for a habitual
   path in the very section warning against reaching for habitual paths. A consumer may have no
   `docs/` at all (ruling J).
3. `.ravenclaude/` is already the agent-substrate namespace the installer owns on every host.
4. B's residual objection — that this is an **undocumented third tier** one directory below the
   gitignored `runs/` — is **valid and is closed here, not waved away**: this change adds a third row
   to `AGENTS.md`'s canonical storage-contract table (`.ravenclaude/ledger/` = *committed agent
   substrate*), so no future `.gitignore` tidy-up to `.ravenclaude/**` can happen without contradicting
   the table it must read. And the **committability canary (§11.2) runs on every PR**, so even if
   someone does it anyway, it fails loud instead of silently.
5. The human-readable view stays in `docs/` where a human will look for it — the one place B was right.

### 3.2 Path resolution — the algorithm, for any repo

`rc ledger init` writes `.ravenclaude/ledger-config.json`:

```json
{ "config_version": 1,
  "ledger_dir": ".ravenclaude/ledger",
  "view_path": "docs/pm/task-list.md",
  "brief_max_items": 12,
  "brief_max_bytes": 4096,
  "dormant_after_days": 90,
  "aging_policy": "rollup",
  "max_record_bytes": 8192 }
```

Resolution order (first hit wins), applied by **every** consumer of a path — writer, projector, gates,
hooks, CI:

1. `RC_LEDGER_DIR` / `RC_LEDGER_VIEW` — **test harness only**, never documented as a user knob.
2. `.ravenclaude/ledger-config.json` keys, if the file exists and parses.
3. Defaults: `ledger_dir = .ravenclaude/ledger`; `view_path = docs/pm/task-list.md` if `docs/` exists
   at repo root, **else `.ravenclaude/ledger/task-list.md`**.
4. If `.ravenclaude/ledger-config.json` exists but does **not** parse → **UNKNOWN, hard stop.** Never
   fall through to the default: a mangled config that silently reverts to defaults writes the ledger
   to a second location and splits the source of truth.

**`rc ledger init` — the portable install, and what it does in a repo that has neither directory:**

| step | action | failure behaviour |
|---|---|---|
| 1 | `mkdir -p <ledger_dir>`; write `ledger-config.json` | — |
| 2 | **Committability canary on the RESOLVED path**, with positive control (§11.2) | If the resolved ledger path IS ignored → **REFUSE**, print the offending `.gitignore:<line>` and the one-line fix. Never proceed. |
| 3 | Append `<ledger_dir>/*.jsonl merge=union` to `.gitattributes` — **scoped, never blanket `*.jsonl`** | If `.gitattributes` is absent, create it |
| 4 | If `.repo-layout.json` exists, append `<ledger_dir>/**` (and `view_path`'s dir) to `allowed_globs` | If absent (most consumer repos), skip silently — the layout gate is RavenClaude-specific |
| 5 | If `docs/` absent → set `view_path` inside `<ledger_dir>` and say so in the init output | — |
| 6 | Print the retention posture (§12.4) and the host tier (§13) | — |
| 7 | Append a `ledger_init` event so the ledger is non-empty from minute one | This is what makes ruling A's UNKNOWN distinguishable from "never enabled" |

Step 7 is load-bearing: it gives `rc ledger status` a positive control. A ledger with **zero** events in
an **initialised** repo is UNKNOWN (something is wrong); a repo with **no config at all** is
"not enabled" and every hook no-ops. Those two are different and must never be conflated.

### 3.3 In-repo edits this change requires (RavenClaude itself)

- `.gitattributes`: `.ravenclaude/ledger/*.jsonl merge=union`
- `.repo-layout.json`: add `.ravenclaude/ledger/**` and `docs/pm/**`
- `AGENTS.md`: the third storage-tier row (§3.1 point 4)
- `.gitignore`: **no change** — but the canary now guards it forever

---

## 4. The record schema

One file per month. One line per **event**. There is no item record — an item is the fold over the
events sharing its `item_id` (I1). UTF-8, no BOM, one JSON value per line, `\n` terminated, no blank
lines, **no header line and no summary line, ever** (claim 15).

### 4.1 Event types — SIX, and why each exists

| type | Purpose | Why it cannot be folded into another |
|---|---|---|
| `open` | Mints an item: `subject`, `owner`, `priority`, `tags`. | Nothing else creates identity. |
| `state` | Sets `state`; on `done` also `resolution` + its required pointer. | The lifecycle axis. |
| `verify` | Sets `verification`, `verified_by`, `evidence`. **The ONE storage site for verification** (ruling E). | A verifier is usually a different actor at a different time; merging forces one actor to assert both. |
| `link` | Adds/clears a `blocked_on` edge (ledger id **or** `ext:<class>:<slug>`). | Blockers change independently of state; `blocked` is derived from them (ruling H). |
| `redact` | `{redacts: <event_id>, reason_class: enum}` — the erasure path. | **Was a fifth type A's own §1.1 enum omitted, so G-LED-01 rejected every one and the erasure path was inert (ruling I).** It is in the enum here. |
| `provenance` | Post-merge backfill: `{pr, merge_commit, merged_at}` for an item. | **Delivers D3** (ruling F). The PR number does not exist at completion time; nothing else can supply it later without violating I2. |

Two auxiliary types round out the detectors and are **declared in the same enum** (the A-3 lesson —
a type used anywhere must be in the enum Phase 0 builds the schema from):

| type | Purpose |
|---|---|
| `bridge_health` | The Claude Code Tasks rot detector's finding, **appended into the ledger** rather than left as a render-time flag (gap-delta §4; plan-B §1.5). Carries a typed `metrics` object — B-4's defect (its own `payload` could not serialise it) is fixed. |
| `ledger_init` | Written by `rc ledger init` (§3.2 step 7) so "empty" and "not enabled" are distinguishable. |

**`note` is REFUSED** (A §1.1; gap-delta disagreement #1; critic B-3). A free-prose event has no
machine consumer and is the largest secret/PII ingress surface in the design. `subject` is the ledger's
**only** prose field, capped at 140 chars and scrubbed.

### 4.2 Trust boundary — structural, not a convention

`machine` ≡ SLSA `internalParameters` (platform-controlled); `asserted` ≡ `externalParameters`
(caller-supplied, untrusted) — claim 20.

- `machine.*` is written by `ledger.py` only. An event whose `machine` block is absent or carries an
  unknown key is REJECTED.
- `asserted.*` is enum-constrained, pointer-typed, or the one capped prose field.
- `machine.worktree` stores the **worktree NAME** (`forge-task-ledger`), never an absolute path
  (red-team #6: A's own example embedded `/Users/m/...`, leaking an OS username into a permanently
  retained committed artifact).
- `machine.pr` is `null` at append. **`null` means "not yet resolved", never "no PR"**; it is resolved
  by the `provenance` event (§10) and rendered `—`, never "none".

**Accepted residual-trust gap, stated rather than implied** (red-team #3, MEASURED): `enforce-layout.sh`
and `guard-premise.sh` are registered on `Write|Edit|MultiEdit` only — **neither fires on `Bash`**. A
hand-crafted `Write` of a full event with a fabricated `machine.actor` passes both. "There is no CLI
flag that sets `machine`" is true and irrelevant — the Write tool is not a CLI flag either. G-LED-10
(§11.1) raises the cost (it flags events whose `machine.emitter` is absent or malformed), but **the
ledger does not authenticate authorship, and signing is out of scope for v1.** This is written down as
a gap, not papered over.

### 4.3 Identity (ruling I)

- `event_id` = **ULID**, 26 chars Crockford base32. Lexicographically time-sortable, 80 bits of
  randomness, no coordinator. It is the CloudEvents `id`; `machine.source` is the CloudEvents `source`
  (claim 19).
- `item_id` = `rc-` + **12 hex** of `sha256(source ‖ ts ‖ subject ‖ 64-bit nonce)`.
  **Entropy raised from A's 8 hex and B's 4-hex floor.** MEASURED birthday probabilities (critic M6):
  B's 4 hex = **49.6% at 300 items**; A's 8 hex at 10,000 = **1.16e-2** (A's own text said 1.2e-5 — a
  **1000× understatement** that would have been cited by someone). 12 hex (48 bits) at 10,000 items
  ≈ **1.8e-7**.
- **Mint-time collision check is mandatory**, not a comment: the minter folds the local ledger, re-rolls
  the nonce on collision, **max 8 attempts, then hard-fails**. It never silently reuses an id.
- **Never sequential.** Spec-kit's `T001` needs a central allocator and collides across worktrees
  (claims 13, 2).
- `item_id` pattern is pinned `^rc-[0-9a-f]{12}$`. Beads-style hierarchical suffixes are **not** adopted
  (B allowed `(\.[0-9]+)*`); `split_into` carries the hierarchy explicitly and a parseable-suffix id is
  a second, silent representation of the same fact (I1).

### 4.4 Refused fields

| Field | Verdict | Reason |
|---|---|---|
| `confidence` | REFUSED in the ledger | Unfalsifiable; a future agent reads "0.9" as verification. Claim 44 is a **ruling**, not a fact (G3b). **Scope narrowed from plan-A:** this refusal covers the LEDGER only. `project-manager.md`'s per-invocation handoff `confidence` (an escalation-routing signal with its own consumers, incl. the ≥0.7 Cited-Adjudicator threshold) is **NOT touched** — gap-delta disagreement #6, adopted. Phase 8 adds one clarifying sentence distinguishing the two namespaces. |
| `cost` | REFUSED unless `machine`-sourced with a named source field | The Actions API reports `billable.total_ms = 0` for every run; an unsourced cost is worse than none. |
| `effort_estimate` | REFUSED | No consumer, no verification path. |
| `stale`, `age`, `blocked`, `dormant`, `awaiting_verification` | REFUSED as stored | Derived (I1, ruling E, ruling H). |
| free-prose `evidence` | REJECTED BY GATE | §12.2 grammar; claim 43. |
| `note` event | REFUSED | §4.1. |

Refusal is **structural**: `additionalProperties: false` at every object level means a fixture carrying
`confidence` fails validation, rather than relying on a convention someone can forget (plan-B's
$comment discipline, adopted).

---

## 5. The axes — collapsed, with the derivation shown (ruling E + ruling H)

**The measured problem:** both plans kept `awaiting_verification` (which means *done AND unverified*)
**and** required verification for `resolution: completed`. Verification was therefore stored in up to
THREE places. plan-A killed stored `blocked` one row earlier on exactly this argument
(`plan-A.md:196-198`: *"two hand-maintained copies of one fact is the failure this repo has already
paid for"*) and did not apply it consistently. This section applies it consistently.

### 5.1 Axis 1 — `state` (STORED, 4 members)

| Member | Failure it prevents | Stored? |
|---|---|---|
| `proposed` | The owner's core defect: an unaddressed item lands here instead of evaporating. | ✅ |
| `ready` | An agent starting work whose prerequisite does not exist. Encodes *acceptance*. | ✅ (see note) |
| `in_progress` | Two worktrees doing the same item (claim 32). Carries `actor` + `worktree`. | ✅ |
| `blocked` | An item sitting `in_progress` for weeks *looking* alive. | ❌ **DERIVED** (ruling H) |
| `awaiting_verification` | Merely-claimed-done. | ❌ **DERIVED** (ruling E) |
| `done` | A binary "Done" that cannot distinguish shipped from abandoned. Requires a `resolution`. | ✅ |

*Note on `ready`:* the critic recommended cutting it (one operator, no second party to accept). It is
**KEPT** for one concrete reason: the migration maps every legacy `Blocked` row somewhere, and with the
derivation corrected to `state != done` (ruling H correction 1) `ready` is no longer load-bearing for
blocked-ness, so keeping it costs nothing and cutting it costs a migration decision. **It is
additively cuttable at any time** — the ledger is an event log, so removing an enum member needs no
data migration. Trigger to cut: 6 months with fewer than 5 items ever entering `ready` distinctly.

### 5.2 Axis 2 — `resolution` (STORED, required only when `state = done`, 7 members)

| Resolution | Required companion (gate-checked) | Failure it prevents | Precedent |
|---|---|---|---|
| `completed` | *(no verification requirement at write time — see §5.4)* | "Done" meaning "I typed the code." | Jira *Done*; GitHub `completed` (23, 24) |
| `superseded_by` | `superseded_by: <item_id>` — must exist, must not cycle | Re-doing an overturned decision | MADR (28); Beads `supersedes` (3) |
| `split_into` | `split_into: [ids]`, `len ≥ 2`, all exist | Conservation arithmetic silently losing scope | the conservation requirement |
| `descoped` | `decided_by`, `decided_on` | An owner ruling being re-litigated | Jira *Won't do*; GitHub `not_planned` |
| `obsolete_upstream` | ≥1 `evidence` pointer naming the upstream change | "Fixing" a thing that no longer exists | the runner-image / Node-20 incidents |
| `reverted` | `reverted_by: git:<sha>` or `pr:<n>` + a display-only successor row | The worst false green: Done for code no longer in the tree | Fowler compensating events (18) |
| `failed` | `attempts: <int ≥ 1>` + ≥1 `evidence` pointer | Retrying the identical failed route (MAST *Step Repetition*, 30) | MAST |

**Cut from plan-A's eight: `merged_into`.** It is byte-for-byte the same shape as `superseded_by` —
one pointer to one surviving item, same existence + acyclicity check — so it is a second word for one
mechanism. GitHub's `duplicate` + `duplicate_issue_id` precedent (claim 24) is preserved by
`superseded_by`; a duplicate is expressed as `superseded_by: <the survivor>` with `tags: ["duplicate"]`.

**Divergence from the critic, stated and settled rather than left dangling:** the critic recommended
cutting `obsolete_upstream` into `descoped` as well (6 resolutions). It is **KEPT**, because `descoped`
**requires `decided_by` + `decided_on`** and the entire distinction A drew is that for an upstream
obsolescence **nobody decided** (`plan-A.md:214`). Folding it would force the author to fabricate a
decider — manufacturing exactly the kind of false attribution this run exists to stop. Net: 7
resolutions, one cut, one kept-with-reason. Both are additively restorable/cuttable.

Also dropped as collapsing onto a kept member: `wontfix` → `descoped`; `on_hold`/`deferred` → the
`blocked` overlay or a low-priority `ready`; `triage` → `proposed`; `partial` → ambiguous between
`split_into` and *done-unverified*, and hiding two situations behind one word is the drop mechanism.

### 5.3 Axis 3 — `verification` (STORED — and this is its ONLY storage site)

| Value | Gate condition |
|---|---|
| `unverified` | default when no `verify` event exists. **Not stored as a value** — it is the fold's default. |
| `self_verified` | ≥1 resolvable `evidence` pointer; `verified_by == actor` allowed |
| `independently_verified` | ≥1 resolvable `evidence` pointer **and** `verified_by ≠ machine.actor` |
| `verification_failed` | The item is rendered OPEN with `⚠ verification_failed` and counted in `open_count`. **The projector never appends** — a read must not mutate the source of truth. |

### 5.4 The derivations — the whole of ruling E, written as code

```python
# ---- the ONE stored fact ------------------------------------------------
#   verification lives only on `verify` events. Nothing else stores it.
verification = last_verify_event.verification if any_verify_event else "unverified"

# ---- everything else about verification is a FOLD ----------------------
awaiting_verification = (state == "done"
                         and resolution == "completed"
                         and verification == "unverified")

completed_unverified  = awaiting_verification        # same predicate, display label only

blocked = (state != "done"                            # ruling H correction 1
           and any(b for b in blocked_on if unresolved(b)))

dormant = (open and (now - last_event_ts).days > cfg.dormant_after_days)

stale   = (now - last_event_ts).days > cfg.stale_days   # default 7, from the incumbent template

open    = (state != "done")
          or (verification == "verification_failed")
          or awaiting_verification          # <- replaces the write-time "completed requires verification"
```

**What this buys, concretely:**
- `resolution: completed` **no longer requires** a `verification` value at write time. The write path
  gets simpler AND the outcome gets stricter: a `completed` item with no `verify` event stays in
  `open_count`, appears in the SessionStart brief, and shows as `⚠ done, unverified` in the view. A
  gate that *refused the write* would have been trivially satisfiable by writing a `verify` event with
  a junk evidence pointer; a derivation that *keeps it open* cannot be.
- `awaiting_verification` as a state member is gone. plan-A's own migration already produced exactly
  this shape for every legacy `Done` row (`plan-A.md:535`), so the machinery is the one already there.
- CE-1's genuine ambiguity ("a `verification_failed` item at `awaiting_verification` is open twice
  over") disappears: there is one predicate, `open`, and it is a disjunction over derivations, not a
  negotiation between three stored fields.

### 5.5 `blocked_on` — the external-ref grammar the amendment depends on (ruling H condition)

Deriving `blocked` is **only safe with first-class external refs.** plan-B's `blocked_on` is
regex-pinned to `^rc-…` (`plan-B.md:596`) and cannot express "blocked on an owner decision" — B had the
worse half of both designs (a stored `blocked` that drifts, and no way to say what it is blocked on).
This plan adopts plan-A's form **and closes the rot vector gap-delta found in it**:

- `blocked_on` member ::= `<item_id>` | `ext:<class>:<slug>`
- `<class>` ∈ **closed enum** `{owner-decision, upstream, vendor, external-run, migration, access}`
- `<slug>` is **normalised at write time**: lowercase, kebab-case, `[a-z0-9-]{1,48}`. `add` and `clear`
  therefore cannot diverge on casing or whitespace.
- **Near-miss diagnostic:** an unresolved `add` with a `clear` in the same item's history at Levenshtein
  distance ≤ 2 is surfaced as `probable-typo` in the view and in `ledger.py check` output — never
  silently "still blocked, no diagnostic."
- Canary: `add ext:upstream:x-y` then `clear ext:upstream:X_Y` → must normalise-and-resolve; `clear
  ext:upstream:x-z` → must surface `probable-typo`.

### 5.6 G-LED-07's message must be a runnable command (ruling H correction 2)

The view shows `blocked` (read vocabulary) while the gate rejects it (write vocabulary), so an agent
**will** write `state:"blocked"` and be refused. The rejection is not allowed to be a description:

```
G-LED-07: `state: "blocked"` is derived and cannot be stored.
Run exactly this:
  rc ledger link --item rc-a3f8c1d2e4b7 --add "ext:owner-decision:copilot-version-floor"
(classes: owner-decision|upstream|vendor|external-run|migration|access)
```

This owner has documented **five consecutive blocks to change one regex**. A gate whose message is a
description rather than a command is the same shape (`guard-blocks-its-own-repair.md`).

---

## 6. The write path — adoption is the binding constraint (ruling B)

Measured estimate the ruling rests on: plan-A's voluntary CLI path ≈ **15%** sustained adoption;
plan-B's harvest-from-existing-structured-output ≈ **85%**. A convention nobody writes to reads as
coverage and is **worse than none** — a 60%-populated ledger is a fabricated complete set, which is
defect D1 one layer down and harder to see.

### 6.1 Lane 1 — HARVEST (PRIMARY)

`hooks/ledger-harvest.sh` (`Stop`, and `PostToolUse` on `Task` completion) parses the **already-emitted**
Structured Output Protocol block that `project-manager.md` and its peers produce for Team-Lead routing
— fields `next_actions` and `risks_or_open_questions` — and appends one `open` event per entry.

- **Zero new model behaviour.** It is retrieval, not obligation; it cannot be "forgotten."
- Idempotency: `item_id` is minted from `sha256(session_id ‖ turn_seq ‖ normalised_subject ‖ nonce)`
  and the harvester **looks up an existing item with the same normalised subject in the same session
  before minting** — so re-running a turn does not double-write.
- Off-by-one is itself a dropped-item bug: canary feeds `next_actions: ["X","Y"]` and asserts **exactly
  2** events, no more, no fewer.
- **Failure is never silent** (§6.3 heartbeat).

### 6.2 Lane 2 — the in-turn NAG (the only lever on the felt problem)

`hooks/ledger-nag.sh` (`Stop`, advisory): if the turn's response carries action-item-shaped language
(numbered follow-ups, "next step", "still need to", "remaining") **and** the ledger recorded 0 events
this turn → print a non-blocking warning naming the count and the one-line capture command.

- **Negative control is mandatory and shipped** (canary C-NAG-B): a fixture with 4 follow-ups **and** 4
  matching events must **not** fire. A nag with no negative control is the "probes that fail toward
  clean" trap.
- **Honest limits, both stated:** (a) a regex for action-item-shaped language is satisfied by prose
  *describing* action items — C-NAG-B bounds the false-positive rate; **nothing bounds the
  false-negative rate**. (b) It needs the assistant's prose, and **whether a `Stop` payload carries it
  is UNSETTLED** — plan-A asserts flatly that no hook event carries the model's prose answer; plan-B
  designs on the assumption that one does; critic M9 measured that only `gemini-hook-adapter.sh` and
  one test read `transcript_path` in the entire plugin, so **there is no in-repo precedent and neither
  panel ran the probe.** This is a **pre-build gate on Phase 5** (§20, U-11), not a design choice.
  If the probe says no: the nag degrades to a `transcript_path` re-read, and if that is also
  unavailable the lane ships **absent** on that host and the cross-host matrix says so — never
  wired-and-silent.

### 6.3 Lane 3 — the CLI (SECONDARY / manual)

`rc ledger open|state|verify|link|redact|backfill-pr`. This is plan-A's path, demoted to secondary:
the manual escape hatch for hosts with no hooks (§13 text floor) and for deliberate curation. It is
**not** the mechanism the guarantee rests on.

### 6.4 The append primitive — HARD REQUIREMENTS (ruling L)

MEASURED (`probe-append-atomicity.md`; the first attempt failed *in the instrument* — `multiprocessing`
`spawn` re-imported `<stdin>` so **zero bytes were ever written concurrently**, and reading that as
"atomicity is broken" would have been exactly backwards):

| record size | writers | expected | got | malformed |
|---|---|---|---|---|
| ~200 B | 8 | 1600 | 1600 | 0 |
| 1 KB | 6 | 180 | 180 | 0 |
| 16 KB | 6 | 180 | 180 | 0 |
| 64 KB | 6 | 180 | 180 | 0 |

Promoted to requirements, enforced by test, not left as implementation detail:

1. **Exactly ONE `write()` syscall per record.** `os.write(fd, one_complete_bytes_object)`. Buffered IO
   and `print()` are **forbidden on the append path** — a flush mid-record breaks atomicity.
2. **`O_APPEND` on every open.** A seek-then-write loses the kernel's atomic offset update.
3. **Never read-modify-write the ledger.** That is not an append and inherits none of this.
4. **`max_record_bytes` = 8192, gate-enforced.** This keeps every record an order of magnitude below
   the largest measured-safe size, so the >64 KB unmeasured region is unreachable by construction.
5. **`errors[]` non-empty ⇒ `ledger.py check` exits non-zero** (red-team #4). A malformed/torn line must
   flip the exit code, not merely populate a field the Markdown view happens to render. Fixture:
   `bad-truncated-line.jsonl` (a byte-truncated record) must FAIL.

**NOT measured — do not claim** `[unverified — premise not disconfirmed: atomicity measured on
macOS/APFS at ≤64 KB only]`: **Linux/ext4 (the CI runners)**, **network/virtualised filesystems**
(NFS/SMB/container bind mounts — the known-weak case for `O_APPEND`), and **records above 64 KB**.
Settling step: §20, U-10.

### 6.5 The heartbeat — the append's own dropped-item detector

This repo's hook style is deliberately fail-open, which is correct for a *guard* and catastrophic for an
*append*. So: **before** attempting the JSONL write, the hook increments an attempt counter with a single
`echo >>` to `.ravenclaude/runs/task-ledger/heartbeat.log` (gitignored, local, and deliberately on a
different substrate so one failure mode cannot take out both). A gate compares
`attempts_this_session` to `lines_appended_this_session`; a gap is the tell. Canary: force a permission
error on the ledger path and assert the mismatch is **detected**, not swallowed.

---

## 7. The projection algorithm (rulings C + D)

Pure function of **(ledger bytes, `now`)** — `now` is an **explicit parameter**, defaulting to the
`machine.ts` of the newest event, so the projection is a function of the ledger alone and A-2's
"same input bytes → same output bytes" claim is actually true (A's `stale = now - ts` made wall-clock a
hidden input; its test A3.5 passed only because the two runs were seconds apart — a test built to pass).

```
project(ledger_dir, now=None) -> (items, errors, scp, markdown, verdict)

1. READ    every <ledger_dir>/*.jsonl in sorted filename order.
           A line failing JSON parse -> errors[{kind:"malformed_line", file, lineno}]. NEVER skipped.
           A blank line is malformed (jsonlines rule 2, claim 15).
           POSITIVE CONTROL: assert >=1 line parsed before ANY count is trusted.
           0 parseable lines in an INITIALISED repo -> verdict = UNKNOWN (ruling A), not "0 open".

2. SORT    *** BEFORE dedupe. This is ruling C. ***
           total order = (machine.ts ASC, event_id ASC, sha256(canonical_json_bytes) ASC)
           The third key makes the order TOTAL even for two records sharing ts AND event_id —
           which is exactly the same-id/different-bytes pair the union merge is measured to produce.
           File order is NEVER used: union merge leaves lines "in random order" (claim 16).

3. DEDUPE  by event_id, keeping the FIRST in the total order of step 2.
           *** DOCUMENTED TIEBREAK: first in (ts, event_id, sha256(bytes)). ***
           IF two events share event_id but differ in ANY byte ->
               errors[{kind:"event_id_collision", event_id, kept_sha, dropped_sha}]  and the gate FAILS.
           (git union dedupes only BYTE-IDENTICAL lines — probe Arm C. So the only pairs reaching
            this step are same-id/different-bytes pairs: the collision gate, not the dedupe, is doing
            the work. Stated explicitly so nobody later "optimises" the gate away.)

4. GROUP   by item_id. An event whose item_id has no `open` event -> errors[{kind:"orphan_event"}].

5. FOLD    per item, in total order:
             open       -> initialise (subject, owner, priority, tags); state := proposed
             state      -> if asserted.prev_state != current: errors[{kind:"divergence", ...}]
                           and CONTINUE with the later-ts event as winner (last-write-wins, DETECTED —
                           no lock, and no lost update that is also invisible)
             verify     -> set verification, verified_by, evidence[]   <- the ONE storage site
             link       -> add|clear a normalised blocked_on member
             redact     -> blank the target's `asserted` fields to [redacted:<reason_class>]
             provenance -> resolve pr/merge_commit (§10 fold rule)
             bridge_health / ledger_init -> recorded, not item-bearing

6. DERIVE  (never stored): blocked, awaiting_verification, dormant, stale, open   -- exactly §5.4.
           resolution == reverted with no successor -> a DISPLAY-ONLY "auto: needs re-open" row.
           The projector NEVER appends.

7. CHECK   referential integrity + conservation. Errors are RETURNED, not raised, and a non-empty
           errors[] flips the exit code (§6.4 req 5).

8. SCP     over the open set, via set_conservation.py (§14) with set_kind="open_items".

9. RENDER  sorted by (priority ASC, state ordinal ASC, item_id ASC) -> byte-stable, so a hand-edit
           shows as a diff. Apply the truncation contract (§9.3) to EVERY list.
```

### 7.1 The collision canary (ruling C, mandatory)

`tests/fixtures/ledger/collision-deterministic.jsonl` plants **two records sharing one `event_id` and
differing in exactly one byte**, and the test asserts **three** things:
1. `errors[]` contains `event_id_collision` and the exit code is non-zero;
2. the **survivor is the deterministic one** named by the §7 step-3 tiebreak — asserted by
   `kept_sha`, not by eyeball;
3. the same fixture **shuffled** produces the identical survivor and byte-identical Markdown.

Without (2) and (3) the fixture would pass while the projection remained nondeterministic — two
machines rendering different Markdown from the same merged ledger, with nothing reporting it.

### 7.2 Order-independence canary

`shuffled-order.jsonl` (same events, reversed + interleaved) must produce a **byte-identical**
projection to `canonical.jsonl`. This is the single most important test in the plan.

### 7.3 Unrecognised values are rendered, never dropped

plan-B's best projection idea, adopted: an event carrying a value outside the enum (schema drift, a
future version) renders under a visible `## Unrecognized (schema drift?)` heading. There is **no silent
`default: skip`** anywhere in the renderer — that inversion would make the safety property the design
exists to deliver destroy itself.

### 7.4 The checkpoint is DELETED (ruling D)

plan-B made an incremental fold "the design from day one." It is removed entirely:

- **MEASURED (critic M4):** a full parse + dedupe + sort + fold of one year (18,250 events, 11 MB) is
  **108 ms**; 50,000 events is **257 ms**. B's own acceptance test ("confirm regeneration stays
  sub-second") **passes with the checkpoint deleted** — it was written to confirm the design, not to
  test it.
- It is a second copy of derived state on disk (an I1 violation), and B hung **three** mechanisms off
  it, so one stale checkpoint corrupts three.
- Decisively: `plan-B.md:629` filters `e.ts > checkpoint.last_ts` **before** dedupe. A union merge
  routinely lands events **older** than the checkpoint (a sibling branch's work, merged today,
  timestamped last week). Those are filtered out **permanently and silently** — a dropped-item bug
  inside the anti-dropped-item mechanism. Deleting the checkpoint deletes the bug.

Revisit trigger, so this is a decision and not a taboo: a measured full fold exceeding **2 s** on the
target hardware. The answer at that point is finer shards (§12.3), never a re-parse filter keyed on a
timestamp.

---

## 8. THE RATCHET — the three-valued conservation gate (ruling A, highest priority)

**The measured defect this section exists to fix:** with an EMPTY ledger, `A \ C` and `C \ A` are both
empty, every conservation gate PASSES GREEN, and G-LED-01…09 all pass on a ledger with zero events. The
mechanism is **inert exactly when it is most needed** — the never-recorded case is defect **D1 itself**.
That is a probe failing toward green, inside the plan whose own canary section quotes "a broken probe
fails toward clean" as the owner's #1 documented trap.

### 8.1 The Set-Conservation block (SCP) — the shared primitive

```json
{ "scp_version": 1,
  "set_kind": "open_items",
  "count": 4,
  "ids": ["rc-1f0c9a3b2d41", "rc-77b04e19a8c2", "rc-a3f8c1d2e4b7", "rc-e40d2288ff10"],
  "digest": "sha256:9c1f4a7d2b03",
  "basis": "ledger:.ravenclaude/ledger@6f2a1b9c",
  "coverage": { "turns_with_action_language": 19, "turns_with_events_recorded": 12 },
  "truncated": false,
  "computed_at": "2026-08-20T09:44:12.771Z" }
```

`ids` sorted lexicographically and deduped. `set_kind ∈ {"open_items", "causes"}` — the second is
`verify-before-assert`'s, **same module** (§14).
`digest = sha256(scp_version ‖ "\n" ‖ set_kind ‖ "\n" ‖ "\n".join(sorted ids))[:12]`.
`basis` names WHERE the set came from, so a claim can be re-derived.

`set_conservation.py --verify` invariants: `count == len(ids) == len(set(ids))`; `ids == sorted(ids)`;
`digest` recomputes; every id matches `^rc-[0-9a-f]{12}$`.

### 8.2 The three-valued output — this is the ruling

`rc ledger check-enumeration --claimed <scp.json>` emits **exactly one of three verdicts**, and
**UNKNOWN blocks with the same force as FAIL**:

| verdict | exit | when |
|---|---|---|
| **PASS** | 0 | ledger readable **AND** ≥1 event parsed (positive control) **AND** `A \ C = ∅` **AND** `C \ A = ∅` **AND** digest recomputes **AND** the independent lower bound (§8.3) ≤ recorded count |
| **FAIL** | 1 | a **determinate** mismatch: `A \ C ≠ ∅` (under-enumeration — the check the requirement asks for, listing every missing `item_id` + subject); `C \ A ≠ ∅` (over-enumeration — a claim the ledger says is closed: fabricated or stale, both unexplained); digests differ while sets match (corrupt SCP); any broken SCP invariant; non-empty `errors[]` |
| **UNKNOWN** | 2 | **`<ledger_dir>` absent while `ledger-config.json` exists** · **`ledger-config.json` present but unparseable** · **0 parseable lines in an initialised repo** · any file unreadable · `basis` unresolvable · a shard that fails to parse · **the independent lower bound (§8.3) > 0 while recorded events this turn = 0** · the coverage denominator unavailable |

**UNKNOWN is never downgraded to PASS.** It has its own message (`basis_unreadable`, `ledger_empty`,
`config_unparseable`, `unrecorded_lower_bound`) and its own escape: `rc ledger explain` prints the exact
cause and the runnable repair. An empty result **needs a positive control** or it is a broken probe, not
a pass — this gate implements that rule on itself.

### 8.3 The independent lower bound — what makes the ratchet ENGAGE on an empty ledger

The conservation check alone can only detect under-enumeration *relative to what is already recorded*.
So the gate takes a **second, independent** input that does not come from the ledger:

```
lower_bound(turn) = count(next_actions harvested from this turn's structured-output blocks)
                  + (1 if the nag detector matched action-shaped prose else 0)
```

- `lower_bound > 0` and `recorded_this_turn == 0` → **UNKNOWN**. This is the only path in the entire
  design that fires when the ledger is empty, and it is why harvest (§6.1) is not optional.
- `lower_bound` is derived from a source the model does not control for this purpose (a field it already
  emits for Team-Lead routing), which is what makes it independent rather than circular.
- If the harvest lane is **unavailable on this host** (§13 text floor), `lower_bound` is **unknown, not
  zero** → the gate reports UNKNOWN-degraded once per session and the host's tier line says so. It never
  reports PASS on an absent denominator.

### 8.4 Coverage — the honest health metric for the whole convention

Neither panel proposed one. `coverage = turns_with_events_recorded / turns_with_action_language`,
computed per rolling 2 weeks, rendered on the view and in the brief:

```
coverage: 12/19 turns (63%) — 7 turns ended with action language and recorded nothing
```

This is the number that distinguishes *"3 open items"* from *"3 recorded open items out of an unknown
total"*, and it is the only detector for the coverage-theatre failure (critic P3, red-team #8). Paired
with the **cadence-divergence** signal (red-team #8): `commits_last_2w / ledger_events_last_2w`; a ratio
crossing 10:1 against a near-1:1 healthy baseline prints one non-blocking line. Both are advisory,
because a low number is a fact about behaviour, not a defect in a diff.

### 8.5 Where the enforcement actually lives, and the honest limit

The guarantee does **not** live in end-of-turn shaping — the suggester is not ours and may surface
nothing (SETTLED, `scope.md`). It lives in three places that run regardless of what the model says:

1. **Harvest** (§6.1) — the write happens without anyone remembering.
2. **SessionStart** (`ledger-session-brief.sh`) — the open set is printed into the next session's
   context, in a different worktree, after a compaction, with no transcript. Silence in turn *N* is not
   loss: the item is still `proposed` and still enumerated in turn *N+1*. This is I4 made operational
   and is the whole answer to the scope doc's success signal.
3. **CI** (`validate-ledger.yml`) — the full gate set on every PR, on every host, including hosts that
   can run no hooks at all. **No `paths:` filter** (repo rule: a path filter on a required check hangs
   the PR forever).

**Limit, stated plainly:** no hook event carries the model's prose answer *(pending U-11)*. The Stop gate
enforces "an SCP block exists and matches the ledger", not "the sentence listed all four." That is a real
gap and it is the correct place to stop — the durable artifact is the guarantee, the prose is assistance
(owner ruling R1).

### 8.6 Stop-gate scoping — so the ratchet does not train learned disregard

Red-team #5 is a real erosion risk: open items are *designed* to persist for weeks, so
"block whenever any item is open" fires on nearly every turn forever, and the response is to paste
boilerplate and stop reading the gate. `dod-gate.sh`'s consecutive-block cap (real, default 8, confirmed
by critic M8) caps damage per session, not frequency — a gate that trips on 7 of 8 turns is still
adoption death, just capped. Therefore:

- The Stop gate fires **only** on turns that (a) invoked `ledger.py`, (b) harvested ≥1 item, or (c)
  matched the nag detector. Not "any turn while any item is open."
- It checks the **delta the turn touched**, not the global open set. This also kills A-4: at 60 open
  items the model is never asked to emit 60 ids.
- It ships **advisory** and is promoted to blocking **only after** the false-positive rate is measured
  against this repo's own recent session transcripts (§20, U-12). Measure before block.
- It adopts `dod-gate.sh`'s consecutive-block cap so an unfixable mismatch cannot deadlock a session.

---

## 9. Context budget: the cap, the ageing policy, and truncation (rulings G + O)

**The measured framing:** both plans costed the log in **bytes** (A ≈600 B/line — accurate, critic M3
measured its own example at **662 B**; B 300–500 B — **~35% low**). Disk is not the problem. The binding
cost is that **the open set is injected into every session and grows monotonically by construction** — a
solo operator opens faster than he closes, and that asymmetry *is* the reported defect. At ~200 chars per
rendered item, 40 open items ≈ 2K tokens **every session**; 200 items ≈ 10K tokens. This user already runs
**131 plugins disabled** to stay inside a contended context budget.

### 9.1 The cap

| knob | default | meaning |
|---|---|---|
| `brief_max_items` | **12** | items rendered in the SessionStart brief |
| `brief_max_bytes` | **4096** | hard byte ceiling (≈1K tokens); whichever binds first wins |
| `dormant_after_days` | **90** | an open item with no event for this long is `dormant` |
| `aging_policy` | **`rollup`** | `rollup` \| `auto_descope` |

Selection order for the 12 (total and deterministic, so two runs agree):
`(touched_in_last_7_days DESC, priority ASC, last_event_ts DESC, item_id ASC)`.

### 9.2 The ageing / rollup policy

- At `dormant_after_days` an open item derives `dormant`. **It is NOT auto-closed** under the default
  policy: auto-closing is the ledger dropping an item, which is the defect. Instead the brief renders
  **one rollup line**:
  `dormant: 23 items (digest sha256:4b91…) — rc ledger open --dormant`
- **Dormant items are excluded from the brief's 12-item budget but INCLUDED in `open_count` and in the
  SCP `ids`.** Ageing must never weaken conservation — the digest still covers all 47.
- Closing one requires an explicit `state` event with `resolution: descoped` + `decided_by` +
  `decided_on`. `rc ledger sweep --dormant` walks them interactively and emits real events.
- `aging_policy: auto_descope` is available for a consumer who wants the critic's stronger rule (an item
  untouched 90 days auto-transitions to `done/descoped` with `decided_by: "aging-policy"`). It is **not
  the default**, and `rc ledger status` prints which policy is active, because the trade is real:
  auto-descope bounds the set but silently closes work.

### 9.3 The truncation contract (ruling O) — applies to every brief, projection and gate output

Reading a truncated list as a complete one is a **measured defect from this session**. So no surface may
truncate silently. When a rendered set exceeds its display cap, the render MUST emit, in this order:

1. the **full COUNT** of the set (not the shown count),
2. the **digest** over the full sorted id set (the same `sha256` the SCP uses),
3. a **pointer** — the literal runnable command that prints the rest,
4. a machine-readable `truncated: true` in the SCP / JSON output.

```
OPEN: 47 items · digest sha256:9c1f4a7d2b03 · showing 12 by (recency, priority)
  … 12 rows …
⚠ RENDER TRUNCATED — 35 not shown.  Full set:  rc ledger open --all
dormant: 23 of the 47 · digest sha256:4b91c2ad77e5 · rc ledger open --dormant
```

**G-LED-11** fails any render whose displayed row count is less than `count` while `truncated` is
absent or false. Canary: a 40-item fixture with `brief_max_items: 12` must produce the count, the
digest, the pointer and `truncated: true`; a 5-item fixture must produce `truncated: false` and **no**
truncation banner (negative control — a truncation marker that is always on is as useless as one that is
never on).

---

## 10. Owner defect D3 — the `provenance` backfill event (ruling F)

**The measured undelivery:** both plans capture `machine.pr` optimistically at append time. The
`state: done` event is appended **on the branch**, typically before the PR merges and often before
`gh pr view` can resolve one — so in the **normal** case the completing event carries `pr: null`, not in
an edge case. plan-A then "carries forward the most recent non-null `pr`", which yields either nothing or
a **stale earlier PR** — silently attributing the completion to the wrong PR, which is worse than `—`.
Neither plan had an event that could supply the PR later, and plan-A's invariant I2 forbids rewriting the
original. **The owner's explicitly-named third defect was not delivered.** It is delivered here.

### 10.1 The event

```json
{ "schema_version": 1,
  "event_id": "01K3H2P7Q9…",
  "item_id": "rc-a3f8c1d2e4b7",
  "type": "provenance",
  "machine": { "ts": "2026-08-21T14:02:11.004Z",
               "source": "RavenClaude/main/1a2b3c4d",
               "pr": 981,
               "merge_commit": "1a2b3c4d5e6f…",
               "merged_at": "2026-08-21T13:58:40Z",
               "branch": "main",
               "worktree": "RavenClaude",
               "actor": "github-actions:ledger-backfill",
               "host": "ci",
               "emitter": "ledger.py@1.0.0" },
  "asserted": {} }
```

`asserted` is **empty by construction** — a provenance event carries only machine-observed facts, so
there is nothing for a model to assert and nothing to scrub.

### 10.2 Who emits it

`.github/workflows/ledger-backfill-provenance.yml`, on `push` to the default branch:

1. Compute the merge commit and its PR number (`gh api` / the `push` payload).
2. Fold the ledger **as of the merge commit** and again **as of its first parent**; the item_ids whose
   events appear in the former and not the latter are **the items this merge shipped**.
3. Append one `provenance` event per such item, in one commit, with `[skip ci]`.
4. **Idempotent:** an item that already has a `provenance` event with the same `merge_commit` is skipped.
5. Failure is loud: if the PR number cannot be resolved, it appends **nothing** and fails the job — a
   guessed PR is worse than `—`.

Manual path for hosts/repos without Actions: `rc ledger backfill-pr --item rc-… --pr 981`, which
performs the same append with `actor` set to the human/agent.

### 10.3 The fold rule (deterministic, documented)

```
provenance_events(item) sorted by the §7 total order
pr_resolved      = first(provenance_events).pr            # FIRST wins: the merge that shipped it
merge_commit     = first(provenance_events).merge_commit
also_shipped_in  = [e.pr for e in provenance_events[1:]]  # re-merges, cherry-picks: recorded, not lost
if no provenance event:
    pr_resolved = most recent non-null machine.pr on the item's OWN events   # pre-merge best effort
    if still None: render "—"  and count the item in `pr_unresolved`
```

`pr_unresolved` is rendered as a count on the view. An item that is `done` with `pr_unresolved` after
7 days is surfaced in the brief — that is the tell that the backfill workflow is not running, and
without it the backfill would be exactly the kind of gate that is present but inert.

**Canary:** a fixture with a `state: done` event carrying `pr: null` plus a later `provenance` event must
fold to `pr: 981`; the same fixture **without** the provenance event must fold to `—` and increment
`pr_unresolved` — **never** to a carried-forward earlier PR.

---

## 11. The gates and their canaries

### 11.1 The gate set

| ID | Gate | Fails when |
|---|---|---|
| G-LED-01 | JSON Schema | any line violates `ledger-event.schema.json` (`required` + `enum` + `additionalProperties:false` at **every** object level, `if/then` discrimination **per `type`** so a `state` event cannot smuggle `verify` fields) |
| G-LED-02 | Referential integrity + pointers | a `resolution` lacks its required companion; a pointer names a nonexistent id; a cycle in `superseded_by`; `split_into` < 2 members; `verified_by == actor` while `independently_verified` |
| G-LED-03 | Evidence grammar | any `evidence` string fails the typed grammar (§12.2) — prose fails |
| G-LED-04 | Order-independence + collision | `event_id_collision`; or the shuffled-input projection differs byte-for-byte from canonical; or the collision survivor is not the documented one |
| G-LED-05 | Conservation / enumeration | the three-valued verdict is FAIL **or UNKNOWN** (§8.2) |
| G-LED-06 | Secret **and PII** scan | any `asserted` string matches `_scrub.sh` `_secret_patterns` after scrubbing, **or** the new PII pattern layer (§12.1) |
| G-LED-07 | Derived-not-stored | a `state` event carries `state:"blocked"` or `"awaiting_verification"`; or any event carries `stale`/`age`/`dormant`/`confidence`/unsourced `cost`. **Message must be the runnable `rc ledger link …` command** (ruling H) |
| G-LED-08 | Projection freshness — **semantic, not byte** | committed view or `open-set.json` differs from regeneration **after excluding volatile fields** (ruling I) |
| G-LED-09 | Append-only | the PR diff modifies or deletes an existing ledger line (only `+` lines allowed) |
| G-LED-10 | Emitter integrity (advisory) | an event whose `machine.emitter` is absent/malformed, or whose `machine` block carries an unknown key. **Advisory** — §4.2 states honestly that authorship is not authenticated |
| G-LED-11 | Truncation contract | a render shows fewer rows than `count` without `truncated: true` + count + digest + pointer (ruling O) |
| G-LED-12 | **Committability** | `git check-ignore` matches the resolved ledger path (ruling K) |
| G-LED-13 | **Union-merge regression** | the three-arm probe, **including Arm B, the control**, does not reproduce (§11.5) |
| G-LED-14 | Record size | any record exceeds `max_record_bytes` (8192) — keeps the unmeasured >64 KB atomicity region unreachable (§6.4) |

### 11.2 The committability canary (ruling K) — with its positive control

`tests/ledger/test_committable.py`, run at `rc ledger init` **and** on every PR:

```
assert git check-ignore --quiet <resolved ledger path>   ->  NO MATCH   (exit 1)   [the subject]
assert git check-ignore --quiet .ravenclaude/runs/_canary.jsonl -> MATCH (exit 0)  [POSITIVE CONTROL]
```

**The positive control is the point.** Without it, a `git check-ignore` that is broken, absent, or run
outside a git repo returns "no match" for everything and the canary passes **by being blind** — the
purest form of the failure this whole run exists to stop. If the control does **not** fire, the test is a
HARNESS FAILURE, not a pass. Measured basis: `.ravenclaude/runs/**` **is** gitignored (`.gitignore:4`), so
the control has a real subject that will keep firing.

### 11.3 The four measured bugs, each with its canary (ruling I)

| Bug | Fix | Canary |
|---|---|---|
| **B-1** plan-B's `evidence` `oneOf` over pattern branches. MEASURED through `Draft202012Validator` with a live positive control: `null` → **INVALID** (a `pattern` is vacuously satisfied by a non-string, so `null` matches all three branches and `oneOf` demands exactly one); `ci-run:123` → **INVALID** (matches two branches). **B's own declared CI-run form is rejected by B's own schema, and every event without evidence fails validation.** | **`anyOf`, not `oneOf`; hoist `null` out of the constrained branch** (`"type": ["string","null"]` with the `anyOf` applying only when a string). | Validate `null`, `ci-run:17233441209`, `path:scripts/ledger.py#L204`, `git:6f2a…`, `pr:981`, `run:172…`, `cmd:audit-gates@0`, `url:https://…` → **all VALID**; `"it works now"` → **INVALID**. Run with a live `{"not":{}}` control alongside so a dead validator cannot manufacture a pass. |
| **A-1** plan-A's G-LED-08 byte-diffs `open-set.json`, which contains `computed_at` regenerated to *now* → **RED on 100% of PRs forever**. | **Semantic compare**: normalise both sides to canonical JSON with the volatile set `{computed_at, coverage.*, basis@<sha>}` **excluded**, then compare — and compare the `digest`, which is exactly what the digest is for. | Regenerate twice 5 minutes apart → G-LED-08 PASSES. Mutate one `id` in the committed file → G-LED-08 FAILS (negative control, so the exclusion has not simply disabled the gate). |
| **A-3** plan-A's `redact` event is absent from the §1.1 four-type enum Phase 0's schema is built from → G-LED-01 rejects every redact and **the erasure path is inert**. | `redact` (and `provenance`, `bridge_health`, `ledger_init`) are **in the type enum** (§4.1), with per-type `if/then` field discrimination. | `good-redact.jsonl` must **PASS** G-LED-01 and must blank the target's `asserted` fields in the projection. A run of the full erasure sequence end-to-end (§12.4 tier 1). |
| **B-2/A-1.5** `item_id` entropy. MEASURED: B's 4-hex floor = **49.6% collision at 300 items**, no re-roll; A's arithmetic was **1000× optimistic** (stated 1.2e-5, actual 1.16e-2 at 10k) though its decision was right. | **12 hex** (§4.3) **AND** a mint-time collision check with re-roll, max 8 attempts then hard fail. | Mint 100,000 ids → zero collisions; **force** a collision by pinning the nonce → the minter re-rolls and logs; pin it 9 times → **hard fail**, never a silent reuse. |

### 11.4 The enumeration checker must fail in BOTH directions (ruling N)

Discovered live in this run: **a heading that MENTIONS a phase is not a phase.** A strict anchored regex
found **0 phases** in plan-B (which writes `### 2.1 Phase 0 — …`); a loosened regex then produced **2
FALSE bares** (sections titled "… (Phase 0 deliverable)"). Under-match said "nothing here"; over-match
said "two are broken"; **only inspection was right.** This is a real failure mode of the very checker
this run ships, so it is a first-class cause in its taxonomy and is tested in both directions:

| fixture | content | must |
|---|---|---|
| `enum-undermatch.md` | phases written as `### 2.1 Phase 0 — X` (a form the naive anchored regex misses) | the checker finds **all** phases — a **0-result is a HARNESS FAILURE, not a pass** |
| `enum-overmatch.md` | a section titled `## Conservation (Phase 0 deliverable)` that is **not** a phase, plus a real phase | the checker finds **exactly the real one** — a mention is not a member |
| `enum-positive-control.md` | a known-good document with a known count | the checker returns that exact count |

The rule generalised into the checker's contract: **an enumeration checker that has never been shown a
false positive and a false negative has not been tested.** Both fixtures are wired into
`scripts/audit-gates.sh`, and the harness asserts each fixture is non-empty and parses before trusting
any result.

### 11.5 The full canary table

Fixtures live in `tests/fixtures/ledger/`, wired into `scripts/audit-gates.sh` per
`docs/best-practices/ci-gate-audit.md` (each gate must **fail on known-bad AND pass on known-good**).

| # | Canary | Expected |
|---|---|---|
| C01 | `good-full.jsonl` — all 7 resolutions, all 4 verifications, all 8 event types | **PASS all gates** (the positive control: without it, a gate that fails everything looks perfect) |
| C02 | `bad-superseded-no-target.jsonl` | FAIL G-LED-02 |
| C03 | `bad-supersede-cycle.jsonl` (A ⇄ B) | FAIL G-LED-02 |
| C04 | `bad-split-one-child.jsonl` | FAIL G-LED-02 |
| C05 | `bad-dangling-ref.jsonl` | FAIL G-LED-02 |
| C06 | `bad-prose-evidence.jsonl` (`"I ran the tests and they passed"`) | FAIL G-LED-03 |
| C07 | `good-evidence-null.jsonl` + `good-evidence-ci-run.jsonl` | **PASS** G-LED-01 (the B-1 regression) |
| C08 | `collision-deterministic.jsonl` (same `event_id`, one byte different) | FAIL G-LED-04 **and** the survivor is the documented one, shuffle-invariant (§7.1) |
| C09 | `shuffled-order.jsonl` | PASS G-LED-04 **and** byte-identical projection to `canonical.jsonl` |
| C10 | `bad-truncated-line.jsonl` (a torn record) | `errors[]` non-empty → **non-zero exit** (red-team #4) |
| C11 | `bad-count-short.json` (SCP claiming 3 of 4 open) | FAIL G-LED-05 |
| C12 | **empty ledger, initialised repo** | **UNKNOWN (exit 2)** — never PASS (ruling A) |
| C13 | **`lower_bound = 4`, recorded = 0** | **UNKNOWN (exit 2)** (§8.3) |
| C14 | `bad-secret-in-subject.jsonl` (`ghp_` + 32 chars) | FAIL G-LED-06 |
| C15 | `bad-pii-in-subject.jsonl` (an email address) | FAIL G-LED-06 (the new PII layer) |
| C16 | `bad-blocked-stored.jsonl` | FAIL G-LED-07, **message contains a runnable `rc ledger link` command** |
| C17 | `bad-awaiting-verification-stored.jsonl` | FAIL G-LED-07 (ruling E) |
| C18 | `bad-inplace-rewrite.patch` | FAIL G-LED-09 |
| C19 | freshness: regenerate twice 5 min apart / mutate one id | PASS / FAIL G-LED-08 (A-1 both directions) |
| C20 | truncation: 40 items @ cap 12 / 5 items @ cap 12 | count+digest+pointer+`truncated:true` / **no banner** (ruling O, both directions) |
| C21 | committability: resolved path / `.ravenclaude/runs/_canary.jsonl` | NO MATCH / **MATCH** (positive control fires) |
| C22 | **union-merge, three-arm, promoted from `probe-jsonl-merge.md`** | Arm A: 5 lines, 0 lost, 0 markers · **Arm B (no `merge=union`): CONFLICT, exit 1** · Arm C: byte-identical line appears once |
| C23 | **append atomicity**: 6–8 concurrent writers, one worktree, one file | all lines intact, 0 malformed (red-team #4, now a standing test not a one-off probe) |
| C24 | `ext:` normalisation / near-miss | `ext:upstream:X_Y` clears `ext:upstream:x-y`; `ext:upstream:x-z` surfaces `probable-typo` |
| C25 | `provenance` fold | `pr: null` + provenance → `981`; without provenance → `—` + `pr_unresolved`, **never a carried-forward earlier PR** |
| C26 | `state: "frobnicated"` | rendered under `## Unrecognized`, **never omitted** |
| C27 | item with only a `proposed` event | appears under `## Open` (I4, planted **permanently**, checked on every regeneration) |
| C28 | harvest: `next_actions: ["X","Y"]` | **exactly 2** events |
| C29 | nag positive / **nag negative control** | 4 follow-ups + 0 events → FIRES · 4 follow-ups + 4 events → **does NOT fire** |
| C30 | heartbeat mismatch | forced permission error → attempts > appended, **detected** |
| C31 | bridge rot | pinned fixture with `status`→`state` → `bridge_health` event **appended**, not a silent zero-import |
| C32 | bridge positive control | real `~/.claude/tasks/` → **> 0** bridged events (an empty result is broken, not "no tasks") |
| C33 | **T-PROSE self-block** | write the real Phase-0 spec doc through the **real installed** `guard-premise.sh` — record pass/fail as a **finding either way**, never assumed |
| C34 | cross-worktree write | a mutating cross-worktree ledger write is **DENIED** by `worktree-guard.sh` — confirms the read-only constraint is load-bearing |
| C35 | enumeration under-match / over-match | §11.4, both fixtures |
| C36 | `item_id` collision | 100k mints clean; forced collision re-rolls; 9 forced → hard fail |
| C37 | schema refusal | a fixture carrying `payload.confidence` **FAILS** validation (structural, not conventional) |
| C38 | `set_kind: "causes"` | the same module, same shape, for `verify-before-assert` (§14) |

**Instrument controls, because a broken probe fails toward clean** (the owner's #1 documented trap): the
audit harness asserts, before trusting **any** result, that each fixture **exists, is non-empty, and
parses to ≥1 event**. An empty or missing fixture is a **HARNESS FAILURE**, not a pass. C01 is the
positive control proving the suite can return "pass" at all.

**Anti-inverted-audit control:** each gate's audit entry keys on **what EXECUTES**, never on a label
string. This repo has already been burned by a batched header making `grep "Gate N"` report **7 false
unruns**. Plus **unrun detection** (deliberately unwire one gate from the workflow — the audit must
report it unrun; the repo has shipped "39 of 49 gates invoked by no workflow") and **masking detection**
(two bad fixtures in one step — the audit must report both, not stop at the first red).

---

## 12. Security: scrub, PII, retention, erasure

### 12.1 What may never enter the ledger

No raw command text. No stdout/stderr. No request/response payloads. No URL query strings or fragments.
No tokens, keys or connection strings. Same rule, same reason and the **same code** as `log-probe.sh`:
`ledger.py` calls the existing `hooks/_scrub.sh` `_scrub_reason()` on every `asserted` string before
append (critic M7 measured that it exists — 5,954 B, function at line 78 — so the reuse claim is real,
not aspirational), and G-LED-06 re-scans on commit as the backstop. One pattern list, a fourth consumer,
not a fourth copy.

**NEW — the PII layer (red-team #6).** `_secret_patterns` is credential-shaped. A subject like
`"Fix billing issue for jane.doe@client.com"` passes it untouched — not a secret, but PII, and given this
owner's live production context (customer data, webhook_events, sessions) a plausible real input, not a
contrived one. Two changes:
1. A PII pattern layer alongside the secret layer: email addresses, E.164 phone numbers, and a
   `--pii-extra <regexfile>` hook for a consumer's own identifiers. Matches are replaced with
   `[PII:<class>]` at write time and G-LED-06 fails on any survivor.
2. `machine.worktree` stores a **name**, never an absolute path (§4.2) — A's own worked example embedded
   an OS username into a permanently retained committed artifact.

Honest limit: a pattern layer cannot catch a customer's *name* in prose. The structural mitigation is
that `subject` is the ledger's **only** prose field, capped at 140 chars and never free-form-extended —
`note` is refused precisely to keep the surface this small.

### 12.2 The evidence grammar — a resolvable pointer or nothing

`evidence` is an array of strings, each matching **exactly one** form (`anyOf` over these, per §11.3):

| Form | Example | Resolvable by |
|---|---|---|
| `path:<repo-relative>#L<n>[-L<m>]` | `path:scripts/ledger.py#L204-L260` | file exists, line range in bounds |
| `git:<40-hex>` | `git:6f2a1b9c…` | `git cat-file -e` |
| `pr:<int>` | `pr:981` | `gh pr view` (offline: format-only) |
| `run:<int>` | `run:17233441209` | Actions run id (offline: format-only) |
| `ci-run:<token>` | `ci-run:17233441209` | accepted form (B-1 regression) |
| `cmd:<label>@<exit>` | `cmd:audit-gates@0` | a **label**, never the command text |
| `url:<https origin+path>` | `url:https://git-scm.com/docs/gitattributes` | query + fragment **STRIPPED at write time** |

Anything else — including a grammatically perfect English sentence — fails G-LED-03. This is claim 43
made mechanical, and it encodes the repo's own lesson that *a grep is satisfied by the thing being
described*.

### 12.3 Retention

The ledger is a committed repo artifact, so retention is git's: **permanent**. That is a deliberate trade
(a dropped item must not be recoverable-in-principle-only) and it is why prevention carries the weight.

Volume: ~662 B/line measured. At 50 events/day ≈ **11 MB/year**. Fold cost at that size: **108 ms**
(critic M4). **No compaction in v1** — compaction means rewriting, and rewriting is I2's failure mode.
Monthly shards (`<YYYY-MM>.jsonl`) bound any single file.

Two escape valves plan-A left implicit, named here (gap-delta disagreement #5):
- **Within-month runaway** (e.g. Phase 8's bulk migration landing thousands of rows in one calendar
  month): a **one-time, history-preserving re-shard** — `git mv` a mid-month split into
  `<YYYY-MM>a.jsonl` / `<YYYY-MM>b.jsonl`, **never an in-place rewrite**. The projector globs `*.jsonl`
  so nothing else changes.
- **Migration cutover diff size** (red-team #7): `rc ledger migrate --chunk <n>` splits the import across
  commits when the source backlog exceeds `n` rows. The "monthly shards keep a PR diff small" argument is
  a steady-state argument and does not cover a one-time bulk import.

Revisit trigger for compaction: **>20,000 lines in one shard**, and the answer is finer shards, not
rewritten ones.

`[unverified — training knowledge, not re-checked this session]`: plan-B's GitHub diff-collapse threshold
(~20,000 changed lines / ~1 MB). Settling step: §20, U-13.

### 12.4 Erasure — three tiers, and the third is refused rather than overclaimed

1. **Wrong content (no secret).** Append a `redact` event: `{type:"redact", redacts:"<event_id>",
   reason_class: "wrong_content"|"pii"|"secret"}` — **enum only, no free-text reason** (a free-text
   reason would reintroduce the prose ingress `note` was refused for). The projection blanks the
   target's `asserted` fields to `[redacted:<reason_class>]`; `machine` survives — it is the audit trail
   and contains no user content. Forward-fix, append-only, I2 intact.
2. **A secret actually landed.** Redaction does **not** erase it: git history still has the bytes. The
   only correct sequence is **(a) rotate the credential immediately, (b) append the `redact` event,
   (c) escalate to the repo's existing secret-remediation path** (`git-filter-repo`/BFG + force-push).
   **The ledger cannot erase.** Claiming otherwise would be the exact false assurance this repo documents
   as worse than an admitted gap. The same non-erasure applies to **PII**, which §12.1 now at least
   detects.
3. **Opt-out.** The convention is opt-in per repo (R3). A repo that cannot accept permanent retention
   does not enable it; `rc ledger status` prints the retention posture so nobody enables it unaware.

---

## 13. Cross-host matrix — no wired-and-silent cells

Tiers: **enforcing** = a hook can block; **advisory** = a hook fires but cannot block; **text floor** =
no hook at all, CLI + CI only.

| Host | Hooks | Tier | Harvest | Nag | Stop gate | Basis |
|---|---|---|---|---|---|---|
| claude-code | native | **enforcing** | ✅ | ✅ *(pending U-11)* | advisory → blocking after U-12 | verified |
| copilot CLI | `.github/hooks` via adapter | **enforcing** | ✅ | ⚠ pending U-11 | same | verified; installer warns below v1.0.52 |
| codex | `.codex/hooks.json` native | **enforcing** | ✅ | ⚠ | same; **installer prints the `/hooks` re-trust notice** — hash-trust means a silent disarm after every `git pull` | verified |
| gemini | `.gemini/settings.json` | **enforcing** | ✅ | ⚠ | same; tool-name normalisation via adapter | docs-verified |
| cursor | `.cursor/hooks.json` | **advisory only** | ✅ | ⚠ | **NOT wired** — Cursor fails OPEN on a malformed hook response, so a blocking gate there is a gate that reports clean when it breaks. CI is the enforcement. | docs-verified, never run live |
| aider | none | **text floor** | ❌ | ❌ | ❌ | verified: no hooks API. Gets `rc ledger` CLI + CI + a projected `CONVENTIONS.md` section stating there is no in-loop enforcement |
| Copilot **Chat** | unconfirmed | **text floor** | ❌ | ❌ | ❌ | docs-verified only. **Do NOT claim CLI coverage as Chat coverage.** |
| windsurf / Devin | none wired | **text floor** | ❌ | ❌ | ❌ | verified: no adapter, no install path; product renamed |

- `rc ledger status` prints the host's tier **verbatim**, so a Cursor user reads "advisory — CI is the
  enforcement" rather than assuming Claude Code's coverage.
- `knowledge/host-support.json` gains a `ledger` component row in the same change — **one map, not a
  second list**.
- **On a text-floor host `lower_bound` is UNKNOWN, not zero** (§8.3) — the ratchet degrades to
  UNKNOWN-degraded and says so, never to PASS.
- **CI is the universal floor.** `.github/workflows/validate-ledger.yml` runs `rc ledger check` on every
  PR, **no `paths:` filter** (repo rule).
- **Pre-wiring gate (P5-G2):** a fail-open/fail-closed audit per host before wiring, and a live host
  canary — a planted violation must actually block. **A host whose canary cannot be confirmed ships as
  text floor, not as assumed-working.**
- The cross-host claim table is **diffed against `AGENTS.md`'s own table as a CI check**, so a future
  edit there that is not mirrored here fails loud rather than drifting (plan-B Phase 6, adopted).

---

## 14. Cross-run reconciliation with `verify-before-assert` (ruling M)

**This is the orchestrator's error, and it is the deliverable's own argument restated as evidence.**
Two FORGE runs were driven concurrently. `verify-before-assert` was synthesized into `plan.md` **first**,
and its brief never mentioned a shared enumeration primitive — because the shared primitive was
identified later, while scoping `task-ledger`. Red-team #1 verified on disk: that plan (103,505 B, past
critic, past red-team, past tiebreak) contains **zero occurrences** of `set_conservation`, `set_kind`,
`scp_version` or "Set-Conservation", and independently specifies its own ledger at
`.ravenclaude/runs/cause-triage/<scope>/open.jsonl` with its own `enumerate_causes(...)`.

A requirement was discovered, recorded in ONE place, and never propagated to the sibling that had already
moved past it. **That is the same defect both runs exist to fix, committed at the orchestration layer.**

### 14.1 The binding ruling

- **`set_conservation.py` is the SSOT, owned and shipped by THIS run** (Phase 2 here). It emits/verifies
  `{set_kind, count, sorted ids, sha256 digest, basis, coverage, truncated}` with
  **`set_kind ∈ {open_items, causes}`**.
- **`verify-before-assert` is its SECOND CALLER, never a second implementation.** Its `plan.md` **must be
  amended** so its cause enumeration consumes `set_conservation.py` with `set_kind="causes"`, and its
  `.ravenclaude/runs/cause-triage/**` store is retrofitted onto the same block shape.
- **Mutual pre-build gate.** Neither run may ship its enumeration mechanism until the other's consumption
  is wired. Not a one-way dependency.
- **Sequencing:** `verify-before-assert` Phase 0 (delivery-channel bake-off + H-a/H-b discrimination) is
  INDEPENDENT and may proceed now. Its enumeration-dependent phases **BLOCK on task-ledger Phase 2**.
- **Acceptance test C38:** the identical module, called with `set_kind="causes"` and that run's own
  `basis` string, returns the same shape and passes the same invariants. If it cannot, the schema is
  wrong here, not there.
- **Fallback, named so the dependency is not unbounded** (critic P4): if `verify-before-assert` does not
  land, the SCP is ~40 lines inline and the `set_kind` discriminator serving one caller is removed. The
  module survives; the generalisation does not have to.

⛔ Note the storage-tier trap on the sibling's side: `.ravenclaude/runs/**` is **gitignored**
(`probe-storage-tier.md`). A cause-ledger there is local-only by design — acceptable for a per-run triage
store, **not** acceptable for anything expected to travel. The amendment must state which it is.

### 14.2 The generalisable fix — FORGE registers cross-run dependencies in the ledger

Concurrent planning runs need a **shared open-question register** both read at every gate boundary. A
requirement discovered in run B after run A has passed the relevant gate is invisible to A **by
construction**. That is precisely the "no closing event = still open" inversion this ledger proposes,
applied to the FORGE pipeline itself. So, folded in as a Phase 5 deliverable:

- `/forge` appends an `open` event per **cross-run dependency** it declares, tagged
  `tags: ["forge","cross-run"]`, with `blocked_on: "ext:external-run:<sibling-slug>"`.
- A sibling run's later discovery therefore surfaces as an **OPEN ITEM against an already-synthesized
  plan**, in that plan's own SessionStart brief, instead of being silently lost.
- Canary: register a dependency from run A, close it from run B, and assert run A's brief shows it opened
  and then cleared — and that an **unclosed** one is still present after a compaction in a different
  worktree.

---

## 15. Phases

Every phase carries a literal `depends_on_claims:` line naming claims-table rows; `[]` where genuinely
none. A downstream deterministic gate reads this field.

### Phase 0 — Specification, JSON Schema, fixtures, canaries (no runtime)

depends_on_claims: [13, 15, 19, 20, 23, 24, 28, 40, 43]

**Deliverables**
- `plugins/ravenclaude-core/knowledge/task-ledger-spec.md` — §3–§12 of this plan, normative.
- `templates/ledger/ledger-event.schema.json` — draft 2020-12, `additionalProperties:false` everywhere,
  **per-`type` `if/then` discrimination**, `anyOf` evidence (§11.3), `redact`/`provenance`/
  `bridge_health`/`ledger_init` in the type enum, `item_id` pinned `^rc-[0-9a-f]{12}$`.
- `tests/fixtures/ledger/*` — canaries **C01–C38** (§11.5), including the enumeration under/over-match
  fixtures (§11.4) and the committability canary with its positive control (§11.2).
- `templates/ledger/ledger-config.schema.json`.

**Pre-build gates**
- **P0-G1** Re-fetch claim 24 (GitHub `state_reason` + `duplicate_issue_id`) — the sole precedent for the
  mandatory-pointer rule.
- **P0-G2** Re-fetch claim 23 (Jira status vs resolution) — claims-table marks it as *carrying the entire
  two-axis design*.
- **P0-G3** `cat plugins/ravenclaude-core/templates/task-list.md` (claim 40) — confirm the migration
  source is unchanged.
- **P0-G4** **T-PROSE self-block probe (red-team #2, C33).** `guard-premise.sh` fires on a Write to a
  **durable** path (its own test: not under `.ravenclaude/`, not scratch) containing a named subject plus
  a certainty word (`measured|verified|confirmed|established|proven|validated`) within ±6 lines with no
  `premise-ok:` citation. The spec doc is durable by that test and its natural voice is exactly this
  run's claims-table style. **Write the real spec doc through the real installed hook before Phase 0 is
  declared done.** If denied: restructure citations into `| Claim | # |` table rows and add inline
  `premise-ok: claims-table.md#N`. Record the outcome as a finding **either way** — never assume.

**Acceptance tests**
- A0.1 `python3 -m json.tool` on every schema; every fixture validates or fails **as its filename
  declares**.
- A0.2 `good-full.jsonl` exercises all 7 resolutions, all 4 verifications, all 8 event types — asserted
  by a **coverage counter**, not by eyeball.
- A0.3 The schema REJECTS an unknown top-level key (negative control for `additionalProperties:false`)
  and rejects `payload.confidence` (C37).
- A0.4 **C21 committability canary passes AND its positive control fires.**
- A0.5 **C35** enumeration checker: correct on the under-match fixture and on the over-match fixture; a
  0-result is a HARNESS FAILURE.
- A0.6 **C07** — `evidence: null` and `evidence: "ci-run:…"` both VALID (the B-1 regression), run beside
  a live `{"not":{}}` control.

---

### Phase 1 — Projector core, fixture-driven (parallel with Phase 2)

depends_on_claims: [16, 17, 18, 38, 42]

*(Un-bundled from plan-A's monolith per gap-delta §5: the fold/sort/dedupe/render logic needs only Phase
0's fixtures, not the writer. This removes the projector from the critical path.)*

**Deliverables**
- `ledger.py project` — the §7 algorithm. **No checkpoint** (ruling D). `now` an explicit parameter.
- The derivations of §5.4, the truncation contract of §9.3, the `## Unrecognized` bucket of §7.3.

**Pre-build gates**
- **P1-G1** Read `docs/best-practices/ci-gate-audit.md` before writing any gate — repo rule.
- **P1-G2** Fix `stale_days` from the incumbent template's existing rule (>7 days), not by invention.

**Acceptance tests**
- A1.1 **Order-independence (C09):** `canonical.jsonl` and `shuffled-order.jsonl` produce byte-identical
  Markdown. *The single most important test in the plan.*
- A1.2 **Collision determinism (C08):** non-zero exit, colliding id named, **survivor is the documented
  one**, and identical under shuffle.
- A1.3 `blocked` / `awaiting_verification` / `dormant` never appear as stored values, and **do** appear in
  the rendered view (C16, C17, §5.4).
- A1.4 `resolution: reverted` with no successor renders a "needs re-open" row and the **ledger file is
  byte-unchanged** after projection (the projector never appends).
- A1.5 Regeneration is idempotent: two consecutive runs, identical bytes; and two runs **5 minutes
  apart** are identical (A-2 — `now` is a parameter).
- A1.6 A `verification_failed` item and a `completed`-without-`verify` item are **both counted in
  `open_count`** (ruling E).
- A1.7 **C20** truncation, both directions.
- A1.8 **C10** a torn line flips the exit code.

---

### Phase 2 — `set_conservation.py` (SSOT) + the writer + repo wiring

depends_on_claims: [2, 15, 16, 17, 19, 33, 42]

**Deliverables**
- `scripts/set_conservation.py` — `build`/`verify`/`diff` over any `set_kind`. **No ledger knowledge**;
  the ledger and `verify-before-assert` are both callers.
- `scripts/ledger.py` — `init|open|state|verify|link|redact|backfill-pr|bridge|project|check`. Machine
  block captured by the script (`git rev-parse`, `git status --porcelain`, `gh pr view` best-effort).
  `_scrub.sh` + the PII layer applied to every asserted string. **§6.4 atomicity requirements.**
- `bin/rc ledger …` dispatch; `.gitattributes` scoped `merge=union`; `.repo-layout.json` globs;
  the `AGENTS.md` third-tier row.

**Pre-build gates**
- **P2-G1 — MUTUAL CROSS-RUN GATE (ruling M).** Amend `verify-before-assert`'s `plan.md` to consume
  `set_conservation.py` with `set_kind="causes"` **before** either enumeration mechanism ships. Two
  incompatible primitives is an explicit failure of this plan. Fallback named in §14.1.
- **P2-G2** Re-run the union-merge probe **with its Arm B control** in this worktree. Arm A alone proves
  nothing — a clean merge may be trivially clean; the control is the mechanism proof.
- **P2-G3** Re-run the **committability** check on the resolved path with its positive control
  (§11.2) — the ledger MUST be committed; `runs/**` deliberately is not.
- **P2-G4 — atomicity on Linux (ruling L, U-10).** Re-run `probe-append-atomicity.md`'s worker-file method
  on an **ext4 CI runner** before relying on `O_APPEND` there. Until it runs, the CI lane carries
  `[unverified — atomicity measured on macOS/APFS ≤64 KB only]`.
- **P2-G5** Claim-33 positive control: one Claude API call with a `required` + `enum` schema, confirming
  a conforming response. A documented guarantee is not an observed one.

**Acceptance tests**
- A2.1 Append never rewrites: after N appends `git diff` shows only `+` lines (G-LED-09 self-test).
- A2.2 **C23** concurrent same-worktree appends: 6–8 writers, one file, all lines intact, 0 malformed.
- A2.3 Two worktrees on divergent branches append 2 events each; merge → 5 lines, 0 lost, 0 conflict
  markers — against **real ledger records**, not scratch lines.
- A2.4 **C14/C15** planted `ghp_`-shaped token and planted email are `[REDACTED]`/`[PII:email]` **on
  disk** (write-side canary, not only the gate side).
- A2.5 `machine.pr` is `null`, not `"none"`; `machine.worktree` is a **name**, not an absolute path.
- A2.6 **C36** 100k mints collision-free; forced collision re-rolls; 9 forced → hard fail.
- A2.7 **C14 (record size)** a 9 KB record fails G-LED-14.
- A2.8 `set_conservation --verify` fails on: count≠len(ids); a duplicate id; unsorted ids; a mutated
  digest — **four separate negative controls**; and digest is stable under input reordering.
- A2.9 **C38** `set_kind="causes"` returns the same shape through the same code path.
- A2.10 **C34** a mutating cross-worktree ledger write is DENIED by `worktree-guard.sh`; the read path
  (`git show <ref>:<path>`) succeeds. Cross-worktree access is **read-only by construction** — this
  sidesteps the guard rather than fighting it.
- A2.11 `rc ledger init` in a scratch repo with **no `docs/`, no `.ravenclaude/`, no
  `.repo-layout.json`** succeeds, resolves `view_path` inside `<ledger_dir>`, and appends `ledger_init`
  (ruling J).
- A2.12 `rc ledger init` where the resolved path IS gitignored → **REFUSES**, prints `.gitignore:<line>`.

---

### Phase 3 — Projector integration + the extended Markdown view

depends_on_claims: [18, 38, 40]

**Deliverables**
- `templates/task-list.md` extended (§16 below): new columns, `## Closed — not completed`, the generated
  header, the coverage line, the truncation banner.
- `<ledger_dir>/open-set.json` emitted alongside; G-LED-08's **semantic** comparator.

**Pre-build gates** — P3-G1: Phase 1 and Phase 2 merged.

**Acceptance tests**
- A3.1 **C19** freshness both directions (regenerate 5 min apart → PASS; mutate an id → FAIL).
- A3.2 The generated header is present verbatim and a hand-edit shows as a diff.
- A3.3 **C27** an item with only a `proposed` event appears under `## Open`, on **every** regeneration.
- A3.4 **C26** an out-of-enum value renders under `## Unrecognized`, never omitted.

The generated view's header, verbatim:

```
<!-- GENERATED by `rc ledger project` from <ledger_dir>/*.jsonl — DO NOT EDIT.
     Edits here are DISCARDED on the next regeneration. Change the ledger instead.
     One-line capture:  rc ledger open "subject"   (or let harvest do it) -->
```

*(The "DO NOT EDIT" header removes the one zero-friction path a solo operator actually uses — typing a
line into a Markdown file. The one-line capture command in the header is the replacement, per critic P3.)*

---

### Phase 4 — The gate suite + the CI workflow

depends_on_claims: [3, 15, 24, 28, 43]

**Deliverables**
- `ledger.py check` implementing **G-LED-01…14**.
- `.github/workflows/validate-ledger.yml` — **no `paths:` filter**.
- `scripts/audit-gates.sh` entries: each gate proven to **fail on known-bad AND pass on known-good**.

**Pre-build gates**
- **P4-G1** Phase 3 merged (G-LED-05/08/11 need the projection). *G-LED-01/02/03/06/07/09/12/13/14 need
  only Phase 0 and may ship as soon as it lands (gap-delta §5.2).*
- **P4-G2** Read `docs/best-practices/ci-gate-audit.md` — repo rule, required reading.
- **P4-G3 Inverted-audit control:** every audit entry keys on what **EXECUTES**, not on a label.

**Acceptance tests**
- A4.1 Every canary C01–C38 produces its declared verdict. **No skips.**
- A4.2 **Unrun detection:** unwire one gate from the workflow — the audit must report it unrun.
- A4.3 **Masking detection:** two bad fixtures in one step — the audit must report **both**.
- A4.4 **Harness self-check:** truncate a fixture to zero bytes — the audit must report **HARNESS
  FAILURE**, not PASS.
- A4.5 **C12/C13** the empty ledger and the `lower_bound > 0, recorded = 0` case both return
  **UNKNOWN (exit 2)** — never PASS (ruling A).
- A4.6 **C22** the three-arm union-merge regression, **including Arm B**, runs in CI. *(plan-A ran the
  probe once as a pre-build gate and never again — a future `.gitattributes` edit silently dropping
  `merge=union` would then have no detector. B's standing version is the durable one.)*

---

### Phase 5 — Harvest, nag, session brief, Stop gate, cross-host, FORGE cross-run registration

depends_on_claims: [30, 32, 33, 41]

**Deliverables**
- `hooks/ledger-harvest.sh` (**PRIMARY write path**, ruling B) + the heartbeat side-channel (§6.5).
- `hooks/ledger-nag.sh` (advisory, with its negative control).
- `hooks/ledger-session-brief.sh` (SessionStart) — the capped brief + rollup + truncation contract.
- `hooks/ledger-stop-check.sh` (Stop) — delta-scoped, advisory-first (§8.6).
- `hooks/hooks.json` + `.claude/settings.json` dev-mirror entries; `knowledge/host-support.json` `ledger`
  row; `rc ledger status`.
- FORGE cross-run dependency registration (§14.2).

**Pre-build gates**
- **P5-G1** Phase 4 merged.
- **P5-G2** **Fail-open/fail-closed audit per host before wiring.** Cursor fails OPEN on a malformed hook
  response — a blocking gate there reports clean when broken. Ship advisory or not at all; **never a
  wired-and-silent cell.**
- **P5-G3 (U-11, R15) — does a `Stop` payload carry the model's prose?** plan-A asserts no; plan-B designs
  on yes; critic M9 found **no in-repo precedent** (only `gemini-hook-adapter.sh` and one test read
  `transcript_path`) and **neither panel ran the probe.** Read a real Stop payload. If it does not:
  the nag falls back to a `transcript_path` re-read, and if that is unavailable it ships **absent** on
  that host and the matrix says so.
- **P5-G4 (U-12)** Measure the Stop gate's false-positive rate against this repo's own recent session
  transcripts **before** promoting it from advisory to blocking (red-team #5).
- **P5-G5** Adopt `dod-gate.sh`'s consecutive-block cap (real, default 8) so a mismatch cannot deadlock a
  session.

**Acceptance tests**
- A5.1 **The scope doc's success signal, end to end:** create 4 open items in worktree A; start a fresh
  session in worktree B, on a different branch, with no transcript, after a compaction; the SessionStart
  brief enumerates **all 4** with state, resolution, verification and the PR/worktree each was addressed
  in. *(Cross-worktree visibility arrives at merge — see §21 limit 3 and Phase 8a.)*
- A5.2 A turn whose SCP names 3 of 4 touched items → the gate reports FAIL and **names the 4th by id**.
- A5.3 A turn that harvests 4 and records 0 → **UNKNOWN** (C13).
- A5.4 Deleting `<ledger_dir>` while `ledger-config.json` exists → **UNKNOWN**, not a clean pass; deleting
  **both** → hooks no-op silently, exit 0, session unaffected (opt-in per R3).
- A5.5 Corrupting the ledger → `basis_unreadable`, exit 2.
- A5.6 **C28/C29/C30** harvest exactly-2; nag fires; **nag negative control does NOT fire**; heartbeat
  mismatch detected.
- A5.7 **C20** the brief at 47 open items shows 12 + count + digest + pointer + `truncated: true`; the
  dormant rollup is one line; `open_count` and the SCP `ids` still cover all 47 (§9.2).
- A5.8 **Host canary:** on each enforcing host a planted violation must actually block. A host whose
  canary cannot be confirmed ships as **text floor**.
- A5.9 §14.2 cross-run registration canary.

---

### Phase 6 — `provenance` backfill (delivers D3)

depends_on_claims: [21, 22]

**Deliverables**
- `.github/workflows/ledger-backfill-provenance.yml` (§10.2), `rc ledger backfill-pr`, the §10.3 fold
  rule, and the `pr_unresolved` surfacing.
- Optional sub-feature: a `Ledger-Item: rc-…` git trailer, so a commit can name its item.

**Pre-build gates**
- **P6-G1 (claim 22)** Verify `git log -1 --format=%B | git interpret-trailers --parse` on a real test
  commit carrying the trailer **before** shipping the trailer sub-feature. It is WARN-tier and
  **explicitly unverified**; it gates the sub-feature only, not the phase.

**Acceptance tests**
- A6.1 **C25** the fold rule, both directions (with and without the provenance event).
- A6.2 The workflow is **idempotent** — re-running on the same merge appends nothing.
- A6.3 An unresolvable PR number appends **nothing** and fails the job (never a guessed PR).
- A6.4 A `done` item still `pr_unresolved` after 7 days is surfaced in the brief — the tell that the
  backfill is not running.

---

### Phase 7 — Claude Code Tasks bridge (read-only) — OFF the critical path

depends_on_claims: [5, 6, 7, 8, 9, 10]

**READS** `${CLAUDE_CODE_TASK_LIST_ID:+~/.claude/tasks/$CLAUDE_CODE_TASK_LIST_ID}` else every
`~/.claude/tasks/<uuid>/*.json`. **NEVER WRITES** — not the task JSON, not `metadata`, not the `.lock`;
opened `O_RDONLY`, the lock neither acquired nor created. It is another process's private state under an
active lock, and `AGENTS.md` classifies `~/.claude/` as host-private that never crosses over.

**Mapping (one-way, idempotent)**

| Claude Code | Ledger |
|---|---|
| `id` | `machine.claude_task_id` (machine half — observed, not asserted) |
| `subject`/`description` | `asserted.subject` (capped 140, scrubbed); description discarded |
| `blockedBy[]` | one `link{op:"add"}` per entry |
| `blocks[]` | **not imported** — the inverse edge of another item's `blockedBy`; importing both stores one fact twice |
| `status: pending` | `state: proposed` |
| `status: in_progress` | `state: in_progress` |
| `status: blocked` | **no state event** — emit the `link` events; `blocked` is derived |
| `status: completed` | **`state: done` + `resolution: completed` + NO `verify` event** → derives `awaiting_verification` and stays in `open_count` (§5.4) |

That last row is load-bearing. Claude Code Tasks has no verification concept and no terminal reason
(claim 7). Importing its `completed` as a verified done would manufacture the exact false green the
verification axis exists to prevent. Under ruling E this needs no special case — the derivation does it.

**Identity — A's coupling defect, fixed (critic P1).** plan-A minted
`item_id = sha256("<list_uuid>:<id>")[:8]`, making ledger identity a function of a foreign, undocumented,
machine-local store: if a task list is recreated or the uuid scheme changes, the same logical item mints
a **different** id and the ledger silently doubles (and A's own "run twice" test could not detect it).
**Fix:** the bridge **looks up an existing item by `machine.claude_task_id`** and mints only on miss.

**Absence and drift**
- Path missing → exit 0, one `bridge_unavailable` line, ledger untouched. The bridge is never
  load-bearing.
- Dir exists, zero files → **UNKNOWN**, logged `bridge_empty_dir`, **not "no open tasks"** (claim 5's own
  settling gate says an empty listing is a broken probe, not a refutation).
- Schema drift → a pinned fixture `knowledge/claude-code-tasks-schema-2026-08-19.json`, an
  expected-key **hit rate** per run, and on any drop a **`bridge_health` event appended into the ledger**
  with `verification: verification_failed` — the rot is representable inside the artifact whose job is
  visibility, not left in a stderr nobody tails. *(This is plan-B's best single idea; plan-A's "skip +
  log + `degraded` marker" defaults to a silent zero-import on a total rename.)*
- An unrecognised `status` is skipped + counted, **never guessed**.

**Pre-build gates**
- **P7-G1 (claim 9)** `in_progress`/`blocked` are `[unverified — training knowledge]`; the docs page 404s
  and neither value appeared in the 35 local records. Observe a task in each state or locate the live
  docs URL. Until settled, an unobserved status is "skip + log", never a guessed mapping.
- **P7-G2 (claim 10)** Settle v2.1.16 / `CLAUDE_CODE_TASK_LIST_ID` from the changelog — the env var
  selects **which list** to read; guessing wrong reads the wrong list.
- **P7-G3** Re-run the claim-5/6 probe **with its positive control**: the listing must be non-empty AND
  contain a `.lock` before any key claim is trusted.

**Acceptance tests**
- A7.1 An audit wrapper proves **zero write syscalls** under `~/.claude/` — asserted, not assumed.
- A7.2 Bridge run twice → zero duplicate items; **and** with a *recreated* task-list uuid → still zero
  duplicates (the P1 regression).
- A7.3 **C32** positive control: a real run produces **> 0** bridged events.
- A7.4 **C31** rot canary: `status`→`state` on a copy of the fixture → `bridge_health` appended.
- A7.5 `~/.claude/tasks` absent → exit 0, ledger byte-unchanged. Empty dir → `bridge_empty_dir` as
  **UNKNOWN**.
- A7.6 **Permanent, stated gap:** this bridge and its rot detector can **never** run as a GitHub Actions
  gate — `~/.claude/tasks` does not exist on a runner. It is session-start / on-demand only, and this
  sentence ships in the doc. An unstated gap reads as coverage.

---

### Phase 8 — Migration, docs, release

depends_on_claims: [23, 40, 44]

**Deliverables**
- `rc ledger migrate --from <task-list.md> [--chunk N]` — one-shot, refuses to run twice, prints both
  lossy classes with counts.
- `templates/task-list.md`, `agents/project-manager.md`, `skills/structured-output/SKILL.md` updated
  **together** so the three cannot disagree.
- `plugin.json` version bump + `sync-plugin-versions.py` + `generate-copilot-plugin.py` (repo rule).

**Migration mapping**

| Old `Status` | New | Lossy? |
|---|---|---|
| `Not started` | `state: proposed` | no |
| `In progress` | `state: in_progress` | no |
| `Blocked` | `state: ready` + `link{op:"add", blocked_on:"ext:migration:unknown"}` | **yes — the blocker is unknown.** Renders `⚠ blocker unrecorded`, deliberately noisy so it gets fixed. Safe under the corrected derivation (`state != done`), so it does not depend on `ready` surviving. |
| `Done` | `state: done`, `resolution: completed`, **no `verify` event** | **yes — and the loss is the point.** The old vocabulary has no evidence, so *done-unverified* is the honest import. Each one stays in `open_count` and renders `⚠ done, unverified` — an explicit "we said done and never checked" backlog rather than a silent blessing. |

`project-manager.md`'s per-invocation `{"status": "complete"|"partial"|"blocked", "confidence": …}`
block is **NOT restructured** (gap-delta #6). Phase 8 adds **one sentence** distinguishing
*per-invocation handoff status* (ephemeral, Team-Lead routing, its own `confidence` consumers) from
*ledger item state* (durable, three-axis). Two same-shaped vocabularies in one file with no
distinguishing note is how drift starts.

**Pre-build gates**
- **P8-G1 (claim 44)** The `confidence` refusal is a **ruling**, not a settleable fact. Scoped to the
  ledger only (§4.4). No owner sign-off is needed for the narrowed scope; **any future proposal to strip
  `confidence` from the agent handoff block is a separate owner/tribunal decision.**
- **P8-G2** Consumer-impact simulation: on `/plugin marketplace update`, a repo with no
  `ledger-config.json` must be **entirely unaffected**. If not, a migration note is mandatory.
- **P8-G3 (red-team #7)** Measure this FORGE run's own ledger-event rate before sizing the migration; if
  the source backlog is large, chunk the commit.

**Acceptance tests**
- A8.1 Migrating the template's example rows yields a valid ledger; both lossy classes printed with
  counts.
- A8.2 Every migrated `Done` row appears in `open_count` as `⚠ done, unverified`.
- A8.3 `migrate` run twice → refuses, exit 1, ledger unchanged.
- A8.4 A repo with the plugin installed and no ledger config: `rc ledger status` says "not enabled",
  every hook no-ops, CI passes.

---

### Phase 9 — DEFERRED, with explicit triggers

depends_on_claims: []

- **9a — cross-branch open-set union.** `rc ledger open --all-branches` reads
  `git show <ref>:<ledger_dir>/*.jsonl` across local branches (read-only, so `worktree-guard` is
  sidestepped by construction), making an item opened in worktree A visible from worktree B **before** a
  merge. **Trigger:** the first real instance of a dropped item caused by branch isolation. Shipping it
  early would hide the merge-based guarantee under an optimisation.
- **9b — `cleanup-worktrees` integration.** Teach the existing skill to read the ledger before archiving:
  if a branch's ledger tail holds open items absent from `main`'s ledger, **warn before archive/delete.**
  A cross-cutting dependency on an existing skill, not a new mechanism. Trigger: 9a, or the first
  archived branch found to have carried unmerged items.
- **9c — compaction.** Trigger: >20,000 lines in one shard. The answer will be finer shards (§12.3),
  never rewritten records (I2).

---

## 16. The extended `task-list.md` view (extend, do not fork)

The template keeps its identity (Active / Recently completed / Backlog / Conventions) and becomes
**generated**, gaining columns and sections:

```
| ID | Task | Owner | Due | Priority | State | Resolution | Verification | PR | Worktree | Evidence | Last update |
```

plus `## Closed — not completed` (every item whose `resolution ≠ completed`, so superseded/descoped/
obsolete/reverted work stays visible instead of vanishing into "Done"), the **coverage line** (§8.4), the
**dormant rollup** (§9.2), the **truncation banner** when it applies (§9.3), and `## Unrecognized (schema
drift?)` when it is non-empty (§7.3).

`evidence` renders as an **inert table cell** — a bare `path:line` / URL / run-id token, never a sentence
— and dates live in dedicated columns rather than inline prose. That is both the T-PROSE mitigation
(red-team #2) and the correct rendering of a pointer-typed field.

---

## 17. The reconciled dependency DAG

```
                          P0  spec + schema + fixtures + canaries
                          (incl. C21 committability, C33 T-PROSE, C35 enumeration both-directions)
                             |
              +--------------+--------------+
              |                             |
              v                             v
     P1  projector CORE               P2  set_conservation.py (SSOT)
         (fixture-driven)                 + writer + init + repo wiring
         [ ∥ with P2 ]                    [ P2-G1 = MUTUAL cross-run gate ]
              |                             |
              +--------------+--------------+
                             v
                          P3  projector INTEGRATION + extended view
                             |
                             +---------------------------+
                             |                           |
                             v                           |
                          P4b projection gates           |   P4a schema/reference gates
                          (G-LED-04,05,08,11)            |   (01,02,03,06,07,09,12,13,14)
                             |                           |   <-- needs P0 ONLY; ships early
                             v                           |
                          P5  harvest + nag + brief + Stop + cross-host + FORGE cross-run
                             |                \
                             |                 +--> P6  provenance backfill  (needs P2 + P4a)  [D3]
                             |                 +--> P7  bridge (read-only)   (needs P2)
                             v
                          P8  migration + docs + release
                             |
                             v
                          P9  deferred (9a cross-branch union · 9b cleanup-worktrees · 9c compaction)
```

**Critical path:** `P0 → P2 → P3 → P4b → P5 → P8`.
**Parallelisable:** P1 ∥ P2 · P4a as soon as P0 lands · P6 ∥ P7 after P2/P4a.

Two de-serialisations adopted from gap-delta §5, because plan-A's stated path cost calendar time for no
correctness benefit:
1. **The projector core does not need the writer.** Fold/sort/dedupe/render and the order-independence
   property need only Phase 0's fixtures. Only the *integration* pass needs both.
2. **Nine gates are not one phase.** G-LED-01/02/03/06/07/09/12/13/14 operate purely on raw JSONL
   fixtures and can ship the moment Phase 0 lands. Only G-LED-04/05/08/11 are projection-dependent.

**Off the critical path by design:** P7 (bridge). If `~/.claude/tasks` vanishes in a Claude Code release
the ledger is unaffected — the bridge reads a second store, it never becomes one.

**Longest pre-build gate:** **P2-G1**, the mutual cross-run gate (§14), because it requires an amendment
to another run's already-synthesized plan. It blocks the SSOT module and therefore P3 onward. P5-G3
(does a Stop payload carry prose?) is cheap but must run before the nag is designed on.

---

## 18. Combined risk matrix

Probability = estimated chance it bites within 6 months **given this plan as written** (i.e. after the
fixes). Impact: **Critical** = the stated guarantee is false; **High** = the ledger is wrong or unusable;
**Med** = friction/erosion; **Low** = cosmetic.

| # | Risk | P (as planned) | Impact | Mitigation in this plan | Residual |
|---|---|---|---|---|---|
| R1 | **Nobody writes to it; the ledger stays near-empty and every gate passes green** | was 0.7 → **0.25** | Critical | Harvest = PRIMARY (§6.1); three-valued gate with an **independent lower bound** so UNKNOWN fires on an empty ledger (§8.2/8.3); coverage metric (§8.4); cadence divergence | The nag's false-negative rate is unbounded; harvest only covers agents that emit the block |
| R2 | B's `ts > last_ts` checkpoint filter silently drops merged events | **0** | Critical | **Checkpoint deleted** (ruling D, §7.4) | none — the code does not exist |
| R3 | B's `oneOf` evidence schema rejects `null` and `ci-run:` | **0** | High | `anyOf` + hoisted `null` + canary C07 with a live control (§11.3) | none |
| R4 | A's G-LED-08 red on 100% of PRs from day one | **0** | High | Semantic compare excluding volatile fields + C19 both directions (§11.3) | a new volatile field added later without updating the exclusion set — C19's negative control catches it |
| R5 | Open set grows unbounded and eats the context budget it is injected into | 0.6 → **0.2** | High | Cap + deterministic selection + dormant rollup + count/digest/pointer (§9) | the default `rollup` policy bounds the *brief*, not the *set*; `auto_descope` is opt-in |
| R6 | **D3 not delivered** — `machine.pr` null on the completing event | 0.75 → **0.15** | High | `provenance` backfill event + workflow + fold rule + `pr_unresolved` tell (§10) | a repo with no Actions relies on the manual `backfill-pr` |
| R7 | Axes not orthogonal; coders guess | 0.5 → **0.05** | High | Verification stored in ONE place; `awaiting_verification` and completed-requires-verification **derived** (§5.4) | none material |
| R8 | Same-`event_id`/different-bytes pair yields a nondeterministic projection | 0.4 → **0.05** | High | Sort **before** dedupe, total order with a third key, documented tiebreak, collision gate + shuffle-invariant survivor canary (§7.1) | a same-id pair is still a minting bug — the gate names it rather than hiding it |
| R9 | Consumer repo: hardcoded path collides or is gitignored there | 0.5 → **0.1** | Med | `ledger-config.json`, resolution order, `rc ledger init` running the committability canary **on the resolved path**, refusal on a gitignored path (§3.2) | a consumer editing `.gitignore` after init — caught by G-LED-12 in their CI only if they run it |
| R10 | A's G-LED-01 rejects every `redact`; erasure path inert | **0** | Med | `redact` in the type enum + `good-redact.jsonl` must PASS (§11.3) | none |
| R11 | `item_id` collision | 0.5 → **~0** | High | 12 hex + mint-time check + re-roll + hard fail (§4.3) | none at any realistic scale |
| R12 | `.gitattributes merge=union` silently removed | 0.3 → **0.05** | Critical | **C22 standing CI test** of the three-arm probe **including Arm B, the control** | a control that stops firing — the harness asserts Arm B produces a CONFLICT, so a dead control is a failure |
| R13 | `note` accretes prose/secrets past the scrubber | **0** | Med-High | `note` refused; `subject` capped at 140 and the only prose field (§4.1) | a customer name inside 140 chars — §12.1 states this honestly |
| R14 | Bridge re-derives `item_id` from a foreign uuid; a recreated list doubles every item | 0.3 → **0.05** | High | Look up `machine.claude_task_id`, mint only on miss; A7.2 tests the recreated-uuid case (§Phase 7) | none material |
| R15 | The nag needs response prose; **no in-repo precedent, and the two plans contradict each other** | **0.5 — OPEN** | Med | **P5-G3 pre-build gate**: read a real Stop payload before designing on it; documented fallbacks (§6.2) | genuinely unsettled until the probe runs |
| R16 | Claude Code Tasks schema rots; a silent zero-import | 0.5 → **0.1** | Low-Med | Pinned fixture + hit rate + **`bridge_health` event appended into the ledger**; empty dir is UNKNOWN (§Phase 7) | the detector itself can never run in CI — stated, not hidden |
| R17 | `stale` makes the projection a function of wall-clock | **0** | Med | `now` is an explicit parameter defaulting to the newest `machine.ts` (§7) | none |
| R18 | **Coverage-theatre**: partially populated but read as complete | 0.5 → **0.2** | Critical | The coverage metric is the only honest detector (§8.4); UNKNOWN on an unavailable denominator; the truncation contract (§9.3) | the metric is advisory — a low number is a fact about behaviour, and nothing forces a response to it |
| R19 | **Cross-run primitive collision** — the sibling run already shipped its own | **1.0 today** | High | Ruling M: SSOT here, sibling amended to consume it, **mutual pre-build gate P2-G1**, C38 | the amendment is work in another run's plan and is not done yet |
| R20 | **T-PROSE blocks Phase 0's own spec doc** | 0.4 | Med | P0-G4 probes the **real installed hook** before Phase 0 is done; mitigations are table-form citations + `premise-ok:` (§Phase 0) | if it fires, the finding is escalated, not worked around |
| R21 | Bash-invoked writer bypasses layout + premise guards; **authorship is not authenticated** | 0.3 | Med | Named as an **accepted residual-trust gap** (§4.2); G-LED-10 advisory raises the cost; signing out of scope for v1 | real and stated |
| R22 | **PII** in `subject`; erasure impossible | 0.4 | Med-High | PII pattern layer + `[PII:<class>]` + G-LED-06 + `machine.worktree` as a name (§12.1) | a customer's *name* in prose is not pattern-catchable — stated |
| R23 | Stop-gate false-positive erosion trains learned disregard | 0.6 → **0.15** | Med | Delta-scoped trigger, advisory until **measured** (P5-G4), block cap (§8.6) | the measurement has not been run |
| R24 | Volume estimate untested against actual FORGE cadence; migration cutover unsized | 0.35 | Low-Med | P8-G3 measures this run; `migrate --chunk`; one-time re-shard escape valve (§12.3) | GitHub's diff threshold is `[unverified]` (U-13) |
| R25 | Atomicity unmeasured on Linux/CI, network FS, >64 KB | 0.3 | High | Hard requirements (§6.4); `max_record_bytes` 8192 makes >64 KB unreachable; **P2-G4** re-runs on ext4 | network FS remains unmeasured and marked `[unverified]` |
| R26 | `ext:` blocker never clears due to a typo → item blocked forever, silently | 0.4 → **0.1** | Med | Closed `<class>` enum, write-time slug normalisation, **near-miss (≤2 edit distance) `probable-typo` diagnostic** (§5.5), canary C24 | a typo at distance ≥3 with no matching add still reads as still-blocked — but it is *visible* as blocked, not invisible |

---

## 19. Red-team mitigation register — every finding, its disposition

| RT # | Finding | Severity | Disposition in this plan |
|---|---|---|---|
| **1** | Sibling run `verify-before-assert` already shipped its own independent ledger/`enumerate_causes`; the shared-primitive gate **already failed** | HIGH, verified live | **§14 in full.** `set_conservation.py` is the SSOT owned/shipped here; the sibling is amended to be its second caller; **mutual pre-build gate P2-G1** blocks both; C38 proves one module serves both `set_kind`s; §14.2 makes FORGE register cross-run deps in the ledger so this class surfaces as an OPEN ITEM next time; §14.1 names the fallback if the sibling does not land. |
| **2** | `guard-premise.sh` T-PROSE plausibly blocks Phase 0's own spec doc | MED-HIGH | **P0-G4 + canary C33.** Write the real doc through the **real installed hook** before Phase 0 is declared done; mitigations are `| Claim | # |` table rows and inline `premise-ok: claims-table.md#N`; the outcome is recorded as a finding **either way**. §16 renders `evidence` as an inert cell and keeps dates in columns for the same reason. |
| **3** | Layout + premise guards are **Bash-blind**; the "`ledger.py` only" trust boundary is unenforced | MED | **§4.2 states it as an accepted residual-trust gap** rather than implying enforcement ("no CLI flag sets it" is true and irrelevant — the Write tool is not a CLI flag). G-LED-10 (advisory) raises the cost. Signing is explicitly out of scope for v1. The layout-glob late-signal is accepted: CI is the backstop and Phase 2 adds the glob. |
| **4** | Concurrent same-file appends in **one** worktree never tested; `errors[]` may not flip the exit code | HIGH | **SETTLED by measurement** (`probe-append-atomicity.md`: atomic at 200 B/1 KB/16 KB/64 KB with 6–8 writers) **and promoted to HARD REQUIREMENTS** (§6.4: one `write()`, `O_APPEND`, never RMW, `max_record_bytes` 8192). **`errors[]` non-empty ⇒ non-zero exit**, with fixture C10 (a torn line). Standing test C23. Honest gap (Linux/CI, network FS, >64 KB) named with settling step U-10 / P2-G4. |
| **5** | `scp_missing` Stop-gate false-positive erosion — a block on nearly every turn trains learned disregard | MED | **§8.6.** Trigger scoped to turns that touch the ledger, harvest, or match the nag — **not** "any turn while any item is open." Checks the **delta**, not the global set (this also kills A-4). Ships **advisory** and is promoted only after the false-positive rate is **measured** against this repo's own transcripts (**P5-G4 / U-12**). Adopts `dod-gate.sh`'s block cap. |
| **6** | Scrub covers credentials, not **PII**; `machine.worktree` embeds an absolute path/username | MED | **§12.1.** A PII pattern layer (email, E.164, `--pii-extra`) with `[PII:<class>]` replacement and G-LED-06 enforcement (canary C15). `machine.worktree` stores a **name**, never a path. §12.4 extends the honest non-erasure statement to PII explicitly. The un-catchable residue (a customer's name in prose) is stated, and `note`'s refusal is what keeps the surface to one 140-char field. |
| **7** | Volume estimate untested against actual FORGE cadence; the one-shot migration commit is unsized | LOW-MED | **P8-G3** measures this run's own ledger-event rate before Phase 8 ships; `rc ledger migrate --chunk N`; §12.3 adds the within-month **one-time history-preserving re-shard** escape valve plan-A left implicit. GitHub's diff threshold stays `[unverified]` with settling step U-13. |
| **8** | Adoption collapse has **no measurable week-3 tell** — only qualitative levers | MED | **§8.4.** Two numeric signals neither panel proposed: **coverage** (`turns_with_events_recorded / turns_with_action_language`, rendered on the view and the brief) and **cadence divergence** (`commits_2w / ledger_events_2w`, one non-blocking line when it crosses ~10:1 against a ~1:1 healthy baseline). Both advisory by design. |

---

## 20. Every unsettled claim, and the concrete step that settles it

Rows marked **SETTLED** are recorded so nobody re-opens them. Rows marked **OPEN** each gate a named
phase and carry the exact command or observation that closes them.

| ID | Claim / question | Status | Concrete settling step | Gates |
|---|---|---|---|---|
| **U-1** | #4 — Beads' migration rationale (Dolt, recurring `metadata` conflicts) | OPEN, WARN | Fetch `https://github.com/steveyegge/beads/blob/main/docs/FAQ.md` **and** issue #2466 directly before any design text asserts the rationale. | **Nothing.** Cited nowhere load-bearing — deliberately. |
| **U-2** | #9 — Claude Code's full status enum (`in_progress`, `blocked`) | OPEN, BLOCK | Observe a task written in each state on disk, **or** locate the live docs URL (`code.claude.com/docs` index, `claude --help`) — the documented page 404s at two paths and neither value appeared in the 35 local records. Until then an unobserved status is **skip + log**, never a guessed mapping. | **P7-G1** |
| **U-3** | #10 — Tasks shipped v2.1.16; `CLAUDE_CODE_TASK_LIST_ID` selects the list | OPEN, BLOCK | Fetch the Claude Code CHANGELOG / release notes for 2.1.16. The env var selects *which list* — guessing wrong reads the wrong list. | **P7-G2** |
| **U-4** | #22 — `git interpret-trailers --parse` extracts `Ledger-Item:` | OPEN, WARN | `git log -1 --format=%B \| git interpret-trailers --parse` on a real test commit carrying the trailer. | **P6-G1** (gates the trailer sub-feature only) |
| **U-5** | #26 — GitHub Projects' built-in Status defaults | OPEN, BLOCK-marked | Fetch the single-select-fields child doc, or `gh api graphql` for `ProjectV2SingleSelectField` options on a real project. | **Nothing.** Listed only as a trap not to repeat. |
| **U-6** | #27 — Linear's six fixed state types | OPEN, BLOCK | Fetch `https://linear.app/docs/configuring-workflows` or the GraphQL `WorkflowState.type` docs. Snippet-level agreement is not a read; the sixth type was itself inconsistent across snippets. | **Nothing.** Corroborating only. |
| **U-7** | #31 — MAST category percentages | OPEN, WARN | Fetch `https://arxiv.org/pdf/2503.13657` and confirm the taxonomy table before quoting any percentage. | **Nothing.** Percentages decorative; the taxonomy is what the design uses. |
| **U-8** | #39 — OpenTelemetry GenAI conventions | OPEN, BLOCK | Fetch `https://opentelemetry.io/docs/specs/semconv/gen-ai/` (or the new dedicated repo). `research.md` already marks it **"do not build on"** — keep that marker until settled. | **Nothing.** Nothing is built on it. |
| **U-9** | #44 — refuse `confidence` | **SETTLED as a RULING, not a fact** (G3b) | Not empirically testable at cheap-floor cost. Adopted as a ruling, **scoped to the ledger only** (§4.4). Any future proposal to strip `confidence` from the agent handoff block is a **separate owner/tribunal decision**. | P8-G1 |
| **U-10** | Append atomicity on **Linux/ext4 (CI runners)**, **network/virtualised FS**, **records >64 KB** | OPEN — `[unverified — measured on macOS/APFS ≤64 KB only]` | Re-run `probe-append-atomicity.md`'s **worker-file** method (never `multiprocessing` from a heredoc — that failure wrote zero bytes and would have read as "atomicity is broken") on an **ext4 CI runner**. Network FS stays unmeasured and marked. `max_record_bytes: 8192` makes >64 KB unreachable by construction. | **P2-G4** |
| **U-11** | **Does a `Stop` hook payload carry the model's prose answer?** plan-A: no. plan-B: designed on yes. critic M9: **no in-repo precedent** (only `gemini-hook-adapter.sh` + one test read `transcript_path`) — **neither panel ran the probe** | **OPEN — one of the two plans is wrong about a load-bearing fact** | Read a **real** Stop payload and confirm. If absent: fall back to a `transcript_path` re-read; if that is also unavailable, the nag ships **absent** on that host and the cross-host matrix says so. | **P5-G3** |
| **U-12** | The Stop gate's false-positive rate | OPEN | Measure against this repo's own recent session transcripts **before** promoting the gate from advisory to blocking. | **P5-G4** |
| **U-13** | GitHub's diff-collapse threshold (~20,000 lines / ~1 MB) | OPEN — `[unverified — training knowledge]` | Re-check current GitHub docs before the number is cited as fact in a shipped doc. | Nothing blocks; §12.3 carries the marker |
| **U-14** | Whether `verify-before-assert` will actually consume `set_conservation.py` | **OPEN — this is R19** | Amend that run's `plan.md` (§14.1). Mutual pre-build gate. Fallback if it does not land: inline the ~40-line SCP and drop the `set_kind` discriminator. | **P2-G1** |
| **U-15** | #33 — the structured-output conformance **guarantee** | Doc-READ; **observation OPEN** | One live Claude API call with a `required` + `enum` schema, confirming a conforming response. **A documented guarantee is not an observed one.** | **P2-G5** |
| — | #16, #17, #42 | **SETTLED by `probe-jsonl-merge.md`** (with #17's premise **corrected**: union dedupes only **byte-identical** lines, so application-level dedupe survives for a narrower reason) | Nothing further — but **P2-G2 re-runs the control anyway**, because a probe's validity is a property of the run, not of the file that records it, and **C22** makes it a standing CI test. | P2-G2, C22 |
| — | Storage tier | **SETTLED by `probe-storage-tier.md`** (both controls fired) | `.ravenclaude/runs/**` is gitignored; the chosen path commits. **C21** makes it a standing canary with a positive control. | P0-G4/A0.4, P2-G3 |
| — | Same-worktree append atomicity | **SETTLED by `probe-append-atomicity.md`** at ≤64 KB on macOS/APFS | Promoted to hard requirements (§6.4). The unmeasured region is U-10. | P2-G4 |

---

## 21. What this does NOT fix — stated honestly, because an admitted gap beats a false assurance

1. **Within a single turn, this does not change what the owner feels.** Claude Code's prompt-suggester
   still addresses 1–2 of the 3–4 items an output ends with. It is a product feature, it is not ours, and
   a search of `plugins/ravenclaude-core/{hooks,scripts,skills}` found no suggestion generator
   (verified in-session). **Any design whose guarantee depended on changing it would be invalid.** What
   this ships is that **loss becomes auditable and recoverable across turns, sessions and worktrees** —
   and the **in-turn nag (§6.2) is the only lever in this entire design that acts on the felt problem in
   the turn where it happens**, and it is advisory, regex-shaped, with an unbounded false-negative rate,
   and dependent on an **unsettled** question about the Stop payload (U-11).
2. **The Stop gate verifies the artifact, not the prose.** It enforces "an SCP block exists and matches
   the ledger", never "the sentence listed all four." No hook event carries a model's chat answer.
3. **Cross-worktree visibility arrives at merge, not instantly.** Two branches that have not merged each
   see their own ledger. Mitigated by union merge (measured: zero loss) and, if it ever bites, Phase 9a.
   It does not weaken the guarantee *within* a lineage, which is where the owner's dropped items live.
4. **The ledger cannot erase.** A `redact` event blanks the projection; git history still holds the
   bytes. A leaked secret needs rotation + the existing secret-remediation path. The same applies to PII,
   which §12.1 now at least *detects*.
5. **Authorship is not authenticated.** Neither `enforce-layout.sh` nor `guard-premise.sh` fires on
   `Bash`, and a hand-crafted `Write` can fabricate a `machine` block. G-LED-10 raises the cost; signing
   is out of scope for v1.
6. **Adoption is behavioural where hooks exist and honestly absent where they do not.** aider, Copilot
   **Chat**, windsurf/Devin get the committed Markdown view, the CLI, and CI — nothing in-loop. Cursor is
   advisory and has never been lived-tested.
7. **The bridge can never be a CI gate.** `~/.claude/tasks` does not exist on a runner, so the rot
   detector runs session-start / on-demand only. Permanent and structural.
8. **The coverage metric is advisory.** It can tell you the convention has decayed; it cannot make anyone
   respond. Nothing in this plan forces a response to a falling number.
9. **Ageing does not shrink the open set** under the default `rollup` policy — it bounds what the *brief*
   costs, not what exists. `auto_descope` is available and is not the default, because auto-closing is
   the ledger dropping an item.
10. **An upstream fix is the only thing that fixes the felt problem at source, and it is not engineering.**
    File the dropped-item behaviour with Anthropic as a product report. Zero cost, complementary rather
    than alternative, and **neither panel mentioned it.** Ship it as a one-line non-engineering action
    alongside Phase 0.

---

## 22. Claim-dependency summary (for the downstream deterministic gate)

| Phase | depends_on_claims |
|---|---|
| P0 | [13, 15, 19, 20, 23, 24, 28, 40, 43] |
| P1 | [16, 17, 18, 38, 42] |
| P2 | [2, 15, 16, 17, 19, 33, 42] |
| P3 | [18, 38, 40] |
| P4 | [3, 15, 24, 28, 43] |
| P5 | [30, 32, 33, 41] |
| P6 | [21, 22] |
| P7 | [5, 6, 7, 8, 9, 10] |
| P8 | [23, 40, 44] |
| P9 | [] |

**Unsettled claims that gate a phase:** **9, 10** (P7-G1/G2) · **22** (P6-G1, sub-feature only) · **33**
(P2-G5, the observation half) · **44** (P8-G1, a ruling not a fact).
**Cited nowhere load-bearing, deliberately:** **4, 26, 27, 31, 39.**
**Settled by probe:** **16, 17, 42** (`probe-jsonl-merge.md`) · storage tier (`probe-storage-tier.md`) ·
same-worktree append atomicity ≤64 KB on APFS (`probe-append-atomicity.md`).

---

## 23. Alternatives considered

| # | Approach | Trade-off | Verdict |
|---|---|---|---|
| A1 | **File-per-record** (`<ledger_dir>/<event_id>.json`) — changesets' and Claude Code's own choice (14, 5) | Zero merge semantics at all; but thousands of inodes, no natural fold order, unreadable PR diffs, and it forfeits the union result actually measured | **Documented fallback**, triggered by repeated real-world union-ordering anomalies |
| A2 | **Mutable single-file state table** (YAML/JSON list, edited in place) | Trivially readable and trivially broken: probe **Arm B CONFLICTS** on concurrent edit, and it reintroduces the in-place rewrite that pushed Beads off JSONL | **Rejected by measurement**, not preference |
| A3 | **External DB (Dolt / SQLite)** — Beads' current answer | Real queries and cell-level merge; but a binary dependency disqualifies "portable convention, opt-in per repo" (R3), and Beads' own reported pain (recurring `metadata` conflicts) shows it **moved** the merge problem | Rejected; Beads' data model still borrowed (hash ids, `supersedes` as an edge) |
| A4 | **GitHub Issues as SSOT** | Mature API, real gates, human-visible; but needs network + auth, cannot record a pre-PR turn, and dies in an offline worktree — exactly where items get dropped | Rejected |
| A5 | **Extend Claude Code Tasks in place** (write provenance into `metadata`) | Zero new surface; refused — host-private state under an active lock, `metadata` is an unschematized bag that will rot, it never travels with a PR, and it dies on a machine change. **Decisive:** the owner's dropped items are prose at the tail of a response and **never become Tasks at all**, so a sidecar cannot represent the very items this exists to stop losing | Rejected → **read-only bridge** (Phase 7) |
| A6 | **Explicit-CLI-only writes** (plan-A's primary) | Zero ambiguity about responsibility; but ~15% sustained adoption, and it revives "the suggester might not surface it" one layer down | **Demoted to secondary** (ruling B) |
| A7 | **Hook-only auto-append with no heartbeat** | Lowest friction; but this repo's hooks are deliberately fail-open, so a swallowed append ends the turn clean and nobody knows | Adopted **with** the heartbeat side-channel (§6.5), never without |
| A8 | **Incremental fold with a checkpoint** (plan-B) | Optimises a **108 ms/yr** operation; costs a second copy of derived state, three coupled mechanisms, and a silent drop of union-merged events | **Deleted** (ruling D). Revisit trigger: a measured full fold >2 s |
| A9 | **Store `blocked` and `awaiting_verification`** | Familiar vocabulary; but two hand-maintained copies of one fact is the failure this repo has already paid for, and a stored `blocked` whose blocker closes stays blocked forever | **Derived** (rulings E, H) — both still render, only the second copy goes |
| A10 | **TTL hard-delete of closed items** | Simplest retention; destroys the audit trail and contradicts "state is purely derivable from the log" | Rejected in favour of **no compaction in v1** + finer shards (§12.3) |
| A11 | **`docs/pm/` for the JSONL** (plan-B) | Already inside a documented committed tier, covered by `docs/**`; but it is a whole-tree-linter hazard, `docs/pm/` does not exist here, and a consumer may have no `docs/` at all | Rejected for the **source of truth**; **adopted for the human view** where `docs/` exists (§3.1) |
| A12 | **Auto-descope dormant items** (critic's aging rule) | Bounds the open set; but silently closes work, which is the defect | Available as **opt-in `aging_policy: auto_descope`**; default is `rollup` (§9.2) |
| A13 | **Cut `obsolete_upstream` into `descoped`** (critic P4) | 6 resolutions instead of 7; but `descoped` requires `decided_by`/`decided_on` and the whole distinction is that **nobody decided** — folding it forces a fabricated decider | **Kept**, with the divergence stated (§5.2). `merged_into` **was** cut on the same test |

---

*End of plan. Every conflict between plan-A, plan-B, the gap-delta, the critic brief and the red-team is
resolved above with its reason; nothing is left as "either."*
