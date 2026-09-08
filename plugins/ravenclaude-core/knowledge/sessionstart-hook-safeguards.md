# SessionStart hook safeguards — the ledger, the tier ladder, the honest limits

Built by the `sessionstart-safeguards-multihost` FORGE run (plan: `.ravenclaude/runs/forge/sessionstart-safeguards-multihost/plan.md`). This is the durable reference for two mechanisms that ship together but answer different questions:

1. **Gate 259** (`scripts/check-sessionstart-matcher-regression.py`) — *static* proof that each host's SessionStart wiring matches the canonical manifest (`hooks/hooks.json`): the right hooks, on the right matcher, per host.
2. **Gate 266** (`_host-canary.sh`'s SessionStart lane + `rc hooks selftest`) — *runtime* proof that a host's own adapter (and, where reachable, its own binary) actually dispatches SessionStart and delivers `additionalContext`.

Neither proves the other's claim. A green Gate 259 says nothing about whether a host binary honors its config; a green Gate 266 (Tier A) says nothing about whether the config as written is correct in the abstract — that's what Gate 259 is for. Read §7 before trusting either in isolation.

## 1. The ledger shape (Gate 259)

`_WIRED_SET_LEDGER` in `scripts/check-sessionstart-matcher-regression.py` is a typed, per-host record — not a bare set of basenames. Each entry declares:

| field | meaning |
|---|---|
| `source` | where the truth comes from: `"generator"` (a `scripts/generate-<host>-hooks.py` projector) or `"manifest"` (Claude Code, which has no generator — its wiring *is* `hooks/hooks.json` + the dev-mirror `.claude/settings.json`) |
| `required` | the canonical SessionStart hook set this host must wire, computed as `_ALL_SESSIONSTART_HOOKS` minus that host's own generator's legitimate `_SKIP` exclusions — hand-computed at the time the row was written, deliberately **not** re-derived live from the generator's current `_SKIP` set (a live re-derivation would make a silently-added bad `_SKIP` entry invisible again, one level up — the exact CE-1 regression class this gate exists to catch) |
| `matcher_fidelity` | `"exact"` \| `"none-by-platform"` \| `"none-unverified"` — see §2 |
| `runtime_tier` | the **settled, reportable** tier (`D` \| `A` \| `S`) for this host — see §3; consumed by `rc hooks selftest` as the single source of truth for its tier column |
| `drift_override` (optional) | a dated, reasoned per-host escape when a third-party host CLI's own hook-config shape legitimately drifts — see §6 |

Four independent checks run against this ledger:

- **Check A** — the canonical manifest's own matcher values, asserted directly.
- **Check B** — `hooks.json` ↔ `.claude/settings.json` parity (plugin-canonical vs. marketplace-dev-mirror).
- **Check C** — per-host wired-set: each host's real generator/manifest output, via a per-host extractor (`_extract_gemini`, `_extract_copilot_cli_flat`, `_extract_cursor_flat`, `_extract_manifest`, `_extract_codex`), checked against `required` — this is what catches a hook silently dropped from one host while every other signal still looks clean.
- **Check D** — ledger *completeness*: every host lane discoverable on disk (an adapter, a generator, or a `host-support.json` row) must appear in `_WIRED_SET_LEDGER` **or** `_UNSUPPORTED_HOSTS`, with a **converse** pass that re-checks every `_UNSUPPORTED_HOSTS` entry's own `promotion_criteria` against disk on every run — see §5.

An extractor that returns an empty set for a host with a non-empty `required` set is itself a finding, never a pass (the fail-closed guard Phase 1 added after F-1's positive-control measurement showed Copilot's and Cursor's flat, name-less SessionStart arrays return nothing from the Gemini-shaped reader).

## 2. Matcher fidelity — why "no matcher" means two different things

| host | fidelity | meaning |
|---|---|---|
| claude-code | `exact` | canonical; Check A already asserts the value directly |
| copilot-cli | `exact` | per-entry `matcher` observed in the generator's real output |
| codex | `exact` (since Phase 4 of this run) | native contract; matcher is expressible and, after this run, present — see §4's migration note |
| cursor | `none-by-platform` | Cursor's `sessionStart` event is not in its matcher-capable event list — **not a defect**, a platform fact |
| gemini | `none-unverified` | the generator wires SessionStart unconditionally on purpose; source-filtering semantics were never verified — **a declared residual**, must not silently flip to `exact` |

The gate asserts the *declared* fidelity matches the *emitted* reality, **bidirectionally**: a host that starts emitting matchers while still declared `none-*`, or stops while declared `exact`, fails. This turns three prose comments into one enforced invariant.

## 3. Runtime tier ladder — D / A / S, declared per host, never implied

The genuinely open design question this run settled: not "does one mechanism verify every host," but "which rung can each host actually reach, and does the output say so."

| tier | what it exercises | mechanism | honest ceiling |
|---|---|---|---|
| **D — dynamic-real** | the host's own binary starting a session and firing SessionStart | a bounded, tool-less one-shot spawn (`claude -p` / `copilot -p`) against a **scratch project dir** with a planted probe hook | proves the host really dispatches SessionStart; does not prove `resume`/`compact` sources (no CLI trigger for those) |
| **A — adapter-real** | the adapter's `sessionstart` mode + the context-delivery contract | `_host-canary.sh`'s SessionStart lane: a SessionStart-shaped payload, asserting **both** marker-fired **and** `additionalContext` reaching stdout | proves the seam; a host binary that ignores a correct config is invisible here |
| **S — static-only** | nothing at runtime | declared, with a reason and promotion criteria | must print "static-only — here is why," never silence |

**Per-host settled tier, as measured by this run (not the generic aspirational classification — see the note below):**

- **claude-code → D.** Live positive-and-negative control: a scratch `.claude/settings.json` `SessionStart` hook wired to a planted probe, driven by `claude -p "<no-op>"`, produced the marker before/regardless of the model turn itself; `claude --help --bare` (skip hooks) is the corroborating negative control.
- **copilot-cli → A, measured — not "D-if-present."** Phase 7 drove `copilot -p` against a scratch project with `.github/hooks/` **twice**, independently, with a positive control on the spawn mechanism itself (the spawn genuinely runs and returns real output). SessionStart does **not** fire under `copilot -p`. The generic aspirational classification in `_rc_canary_declared_tier` still reads "D-if-present, else A" — that function was intentionally left alone by this run — but `_WIRED_SET_LEDGER["copilot-cli"]["runtime_tier"]` carries the **settled** value `"A"`, and `rc hooks selftest` reads the ledger's settled value for its tier column and anti-degradation check, printing a `"D unverified"` caveat rather than silently upgrading to the aspirational claim.
- **codex → A.** Blocked from D by a real platform gate: Codex tracks hook trust by hash and skips untrusted hooks (MH-17) — a freshly-written scratch config is untrusted by construction, so a spawned session would report "did not fire" for a *correct* wiring. Declared, not measured-and-failed.
- **cursor → A.** No verified non-interactive one-shot invocation, and Cursor fails **open** on a malformed hook response — an inconclusive D result there would be actively misleading.
- **gemini → A.** Gemini CLI presence on the authoring machine is not established; declared, not measured.
- **grok → S / not-applicable.** See §5.

**The anti-degradation invariant:** every self-test line prints its tier. `PASS (tier A)` and `PASS (tier D)` are different claims and are never collapsed into one summary "all hosts pass." A host declared tier `D` that only achieves `A` is a **FAIL**, never a pass-with-note.

## 4. Codex — the migration this run shipped, and the consumer-visible behavior change

**This is the single most consumer-visible change in this run — read it before the mechanics above.**

Before this run, Codex's SessionStart wiring was a hand-maintained Python heredoc in `wire_codex_hooks()` (`scripts/ravenclaude`) that wired only **2 of the 9** canonical SessionStart hooks (`capability-orientation.sh`, `thing-denial-kb-recall.sh`), with **no matcher on either** — meaning both hooks re-fired on **every mid-conversation compaction** on Codex. This was the exact defect PR #1084 fixed on every other host, still live on the one host that never got a generator.

`scripts/generate-codex-hooks.py` (new, Phase 4) replaces the heredoc with the fourth sibling of the existing `generate-{copilot,cursor,gemini}-hooks.py` projectors. Its SessionStart lane is derived from `hooks.json` directly:

- **6 new SessionStart hooks land on Codex**: `reapply-posture.sh`, `ensure-default-mode.sh`, `keep-awake.sh`, `worktree-guard.sh` (register), `dashboard-autostart.sh`, and `handoff-successor-ack.sh` join the 2 that already fired.
- **All 9 hooks gain a `matcher`** — `capability-orientation.sh` and `thing-denial-kb-recall.sh` **stop re-firing on compaction**, matching every other supported host.
- **PreToolUse / PostToolUse / Stop are reproduced byte-identically** to the pre-Phase-4 hand-list, as literal hardcoded blocks — this run is SessionStart-only in scope; widening those other lanes is a separate, later decision. The byte-identity control (`generate-codex-hooks.py --out X` vs. the prior heredoc's output) is on record in the run dir (`phase4-evidence/a4.1-*.json`, `a4.2-diff-proof.txt`).

### ⛔ Consumers must run `/hooks` inside Codex to re-trust, after updating

**Codex tracks hook trust by hash (MH-17).** Rewriting `.codex/hooks.json` — which every consumer's `ravenclaude update` (or fresh `install --host codex`) will do the moment this ships — marks every hook for review and **Codex skips them until re-trusted**. Concretely: after updating, a Codex consumer's guardrails (posture reapplication, worktree-lease registration, the newly-added hooks, and the two pre-existing ones) are **silently off** until they run `/hooks` inside Codex.

This is not a new risk this run introduces — it's the same MH-17 hazard every Codex hook-file rewrite has always carried — but this run is the first to land a SessionStart rewrite of this size on Codex, so it is the change most likely to actually surprise someone. The installer's existing `_rc_rearm_notice` mechanism prints the re-trust reminder and the before/after hook count on every install/update; it was **not** bypassed or reimplemented for this change.

**Kill switch, shipped in the same commit as the fix:** `RC_CODEX_SESSIONSTART_LEGACY=1` (or `--legacy-sessionstart`) makes `generate-codex-hooks.py` emit the pre-Phase-4 2-hook, matcher-less SessionStart block verbatim — a one-command revert path if the new wiring needs to be backed out on a consumer's machine without a `git revert` + release cycle.

## 5. Grok — the explicit ruling

**Decision: excluded from `_WIRED_SET_LEDGER`, included by name and reason in `_UNSUPPORTED_HOSTS`.** `rc hooks selftest` prints a `SKIP` row for it.

**Basis:** no `grok-hook-adapter.sh`, no `generate-grok-hooks.py`, no `grok` row in `host-support.json`'s `components.hooks` (7 rows exist there today — a positive control that the absence is real, not an oversight), and `scripts/ravenclaude`'s `--host` arm does not know the word. Grok appears only as a **model-routing** key (`substrate-tier-map.json`, `agent-routing-matrix.json`) — a distinct concern, not conflated here.

**Why this isn't a silent omission:** the completeness check (§1, Check D) fires red if a `grok-hook-adapter.sh` ever appears with no ledger entry at all. But a first-pass version of that check would have been a placebo against the *more likely* future failure: once `_UNSUPPORTED_HOSTS["grok"]` ships, it becomes a permanent fixture that a future real Grok adapter would satisfy-by-lookup without ever re-examining whether the exclusion still holds. The **converse pass** closes that: it re-checks every `_UNSUPPORTED_HOSTS` entry's own `promotion_criteria` against disk on every run, so a mis-classified-and-never-revisited host is caught, not just a never-classified one.

**Promotion criteria** (machine-checked, not prose for a future session to re-derive): a `grok` row in `host-support.json` with `supported: true`; a `grok-hook-adapter.sh` with a `sessionstart` mode; a `generate-grok-hooks.py` sibling with the `_SKIP`/`--check` contract; an `--host grok` installer lane. When any of these exist on disk, the completeness check reports a `PROMOTION-CRITERIA-MET` finding naming Grok and the satisfied criterion — never a silent pass.

## 6. `drift_override` — a per-host escape for legitimate third-party drift

`SKIP_GATE_266=1` is a blunt, whole-gate kill switch: it stops Gate 266 from asserting anything, on every host, for every PR, until removed. That's the wrong granularity for the more common real failure mode: **a single third-party host CLI's hook-config shape legitimately changes** (e.g. a Copilot CLI version bump changing its matcher emission) — a class of dependency Gate 266 newly introduces that Gate 259's prior, all-repo-internal lineage never carried.

A `drift_override` entry on one host's ledger row —

```python
_WIRED_SET_LEDGER["<host>"]["drift_override"] = {
    "reason": "...",
    "recorded": "<date>",
    "expires_review": "<date-or-null>",
}
```

— suppresses **only that host's** Tier-A wired-set/matcher-fidelity assertions, visibly (the gate's CI output and `rc hooks selftest`'s row both print `PASS (drift-overridden — see reason)`, never silently). Every other host's assertion stays live and load-bearing. A `drift_override` entry present but malformed (empty reason, no date) is itself a finding — the shape is checked, not just the presence.

**This is not a general "the gate is wrong" button.** An unreviewed override sitting past its `expires_review` date is documentation debt for a maintainer to clear, not a code defect — Phase 10 records that explicitly here so a future reader doesn't mistake a stale override for evidence the gate itself is broken.

## 7. Honest limits (carried verbatim from plan.md §7 — do not paraphrase)

1. **Tier A does not prove the host binary honors the config.** It proves the adapter seam. Already `_host-canary.sh`'s stated M10 limit; the SessionStart lane inherits it verbatim.
2. **Tier D does not exercise `resume` / `clear` / `compact` sources.** A one-shot spawn produces `startup`. The matcher-dispatch *behavior* under `compact` remains statically asserted (check A) and owner-verified. **This is the residual PR #1084's own defect lived in** — say so plainly, and do not let a green self-test imply otherwise.
3. **Gemini's `none-unverified` matcher fidelity is a real, declared residual**, not a pass. Source hooks may still re-fire on compaction there. The gate pins the declaration so it cannot quietly flip.
4. **CI runs Tier A only.** Tier D is on-demand. A green suite is not a claim about any host binary.
5. **The ledger is only as good as each generator's `_SKIP` honesty.** A hook skipped for a bad reason is correctly excluded from `required` by construction. `check-crosshost-hook-coverage.py` covers *resolution*, not *justification*. No mechanism here reads a reason for sense — and none should pretend to.
6. **(new, closes G5 F3) `compact-anchor.sh` on Cursor is structurally, not residually, unclosable.** Cursor's `sessionStart` payload carries no `source` field; `compact-anchor.py:250`'s `source != "compact"` check is therefore always true there, and the hook always silently no-ops. No tier of either mechanism this plan builds can detect this — Tier A drives a synthetic probe script, never the real hook's internal conditional, and Phase 2's matcher-fidelity axis asserts the manifest's `matcher` string, not a hook's own payload-field logic. This is a permanent platform ceiling given Cursor's current documented payload shape, not a future-phase TODO. (Not chased further this run: any other SessionStart hook whose behavior keys on a payload field Cursor/Gemini don't reliably emit — `handoff-successor-ack.sh` is the next most likely candidate, not `_SKIP`'d for Cursor — is a scoped follow-up, per G4a's Finding 2.)
7. **`copilot-cli` coverage is not `Copilot Chat` coverage.** Every mechanism in this plan — the static ledger, Tier A's adapter drive, Tier D's `copilot -p` spawn — reaches the CLI only. Chat's live hook-firing stays `[unverified — premise not disconfirmed]` per `host-support.json`'s own stated Phase-0-payload-dump blocker. The `copilot-cli` key naming (§1.1) and the forced `chat: unverified` annotation (§1.4, A8.7) exist specifically so this limit cannot be silently misread as closed.
8. **A dated `drift_override` entry is a per-host escape for legitimate third-party CLI drift, not a general "the gate is wrong" button.** It requires a reason and a review date; an unreviewed override sitting past its `expires_review` date is a documentation debt, not a code failure, and Phase 10's knowledge doc should say so.

## 8. Cross-references

- Gate 259 engine: [`scripts/check-sessionstart-matcher-regression.py`](../../../scripts/check-sessionstart-matcher-regression.py)
- Gate 266 runtime lane: [`hooks/_host-canary.sh`](../hooks/_host-canary.sh), driven via `rc hooks selftest` in [`bin/rc`](../bin/rc)
- Codex projector: [`scripts/generate-codex-hooks.py`](../../../scripts/generate-codex-hooks.py)
- Registration + kill switch + `drift_override` teeth: [`scripts/audit-gates.sh`](../../../scripts/audit-gates.sh) (search `Gate 266`)
- Per-component host-support source of truth: [`knowledge/host-support.json`](host-support.json)
- Copilot CLI vs. Chat scoping: [`knowledge/copilot-chat-customization.md`](copilot-chat-customization.md)
- Codex hook-trust hazard (MH-17) background: [`knowledge/codex-cli-customization.md`](codex-cli-customization.md)
