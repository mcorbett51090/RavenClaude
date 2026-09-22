# P-1 — substrate probe result (run 2026-08-08)

**Verdict: the substrate question is NOT cleanly settled. Route T is available but carries an
unmitigated silent-failure hazard; Route P remains unverified; Route N is materially more likely than
`plan.md` §2.6 assumed.** `T-SHAPE` must not be built until the hazard below is designed for.

This is the plan's own first phase, run before anything was built — which is the entire point. It
changed the plan.

---

## Q1–Q2 — can a negative result be recovered from the transcript? **YES**

Measured against this session's own transcript (`9.0M`, the one containing Incident 1):

| question | measured |
|---|---|
| lines carrying `toolUseResult` | **801** |
| occurrences of the incident's probe target (`email-protection`) | **64** |
| `toolUseResult` lines containing a `404` | **49** |

So the evidence `T-SHAPE` needs — *a negative-result probe happened* — is genuinely present in the
transcript and is greppable. Route T's data half is real.

## Q3 — can a hook locate the transcript? **YES, and my first probe answered this WRONGLY**

⛔ **My probe's Q3 was a proxy and it produced a false positive.** It counted files matching
`transcript_path` under `hooks/` and reported *"hooks already reading it: 1"*. The single hit is a
**comment** in `gemini-hook-adapter.sh:8` describing Gemini's stdin contract. **No hook in this repo
reads `transcript_path`.** Counting matches is not counting reads — verification-discipline Rule 2,
violated inside the probe written to enforce it.

Settled properly against the authoritative source
([code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks), retrieved 2026-08-08):
`transcript_path` **is** a documented **common input field** delivered to every hook event, PreToolUse
included. Route T's addressing half is real.

## ⛔ THE FINDING THAT CHANGES THE PLAN — the transcript lags, and Route T fails OPEN

Same source, verbatim:

> "The transcript file is **written asynchronously and may lag the in-memory conversation**, so it may
> not yet include the current turn's most recent messages when a hook fires."

`T-SHAPE` fires on `PreToolUse(Write)` and must see a negative-result probe **from earlier in the same
turn** — probe-then-immediately-build is the common shape, and it is Incident 1's shape. If the
transcript has not flushed, the hook reads a file that does not contain the evidence and concludes
*"no unresolved negative probe"*.

**That is the exact failure this plan exists to prevent**: a check that reports clean because it could
not see, indistinguishable from a check that reports clean because there was nothing there. It is
`consistency-failure-modes.md`'s shape and verification-discipline Rule 6's shape at once, and it
would be **invisible** — the gate would be green in CI, its canary would pass (a canary tests the
matcher against a fixture, not the substrate's timing), and it would silently never fire in
production.

**Neither panel raised this. Neither did my probe.** It came from reading the source rather than
inferring the contract — the same move that settled Incident 1.

### Mitigations, none free

| option | cost |
|---|---|
| **Freshness assertion** — hook checks the transcript tail for the current `session_id`/recent entries; if it cannot confirm freshness, emit `UNKNOWN` rather than `CLEAN` | needs a decision on what `UNKNOWN` does. Fail-closed on every fast turn is friction that gets the gate disabled; fail-open is the silent blindness above. **This is a real Team-Lead decision, not a detail.** |
| **Route P instead** (`PostToolUse(Bash)` → probe log) | not lag-bound, but `tool_response` is **still unverified** (below) and it needs a Bash matcher that does not exist |
| **Accept Route N** — ship `T-PROSE` only | loses the half that fires on Incident 1's exact replay; `plan.md` §8 already states this plainly |

## Q4 / Route P — **still unverified after two documentation fetches**

- `hooks.json` PostToolUse matchers today: `Edit|Write|MultiEdit`, `WebFetch`. **No Bash matcher.**
  Route P requires adding one (plan.md Q-2, ~2 ms per Bash call).
- Two fetches of the hooks reference both truncated before the PostToolUse field list. **`tool_response`
  is neither confirmed nor refuted**, and whether it carries Bash stdout/exit-code is unknown.
- ⚠️ Carried forward as `[unverified]`. **Settling route:** fetch `code.claude.com/docs/llms.txt`
  (the full-text export the docs site itself points to for truncated sections), or — better, since it
  measures rather than reads — register a stdin-dumping PostToolUse hook on `Bash` **in a scratch
  project**, trigger it, and read what actually arrives. ⛔ Do **not** do this by editing the live
  worktree's `.claude/settings.json`: that mutates the running session's own hook wiring.

## What this unblocks and what it does not

- ⛔ **BLOCKED:** P1's `T-SHAPE` half, and therefore the §8.1 replay claim that the mechanism fires on
  Incident 1 unconditionally. That claim is **not currently supported**.
- ✅ **UNBLOCKED, unchanged:** P0 (`classify_claim.py` + canary), P3's `T-PROSE` half, P4 (pre-commit
  diff budget), P5 (review reopen ledger), P6 (probe-kit). All five were already day-one parallel and
  none depends on the substrate.

**Recommendation:** proceed with the five unblocked phases; hold `T-SHAPE` until the freshness
decision is made. Do not build a detector whose blindness is invisible.

---

# ✅ ROUTE P CONFIRMED — measured, not read (2026-08-08, same session)

**The lag hazard above is MOOT. `T-SHAPE` is unblocked and does not need the transcript at all.**

Three documentation fetches returned "not documented / truncated / cannot confirm". The question was
settled in ~2 minutes by **measuring it**: an isolated scratch project (never the live worktree's
`.claude/settings.json`) with a `PostToolUse(Bash)` hook that dumps its entire stdin, driven by a
headless `claude -p` session running Incident 1's own probe.

What actually arrives:

```
TOP-LEVEL KEYS: ['cwd', 'duration_ms', 'effort', 'hook_event_name', 'permission_mode',
                 'prompt_id', 'session_id', 'tool_input', 'tool_name', 'tool_response',
                 'tool_use_id', 'transcript_path']

tool_response PRESENT: True   (dict)
  keys: ['interrupted', 'isImage', 'noOutputExpected', 'stderr', 'stdout']
    stdout = '404'      ← the exact negative result that started Incident 1
    stderr = ''
    interrupted = False
```

**Why this beats Route T outright, rather than merely tying it:**

| | Route T (transcript) | **Route P (tool_response)** |
|---|---|---|
| when the evidence lands | asynchronously, **may lag the current turn** | **synchronously, at tool completion** |
| failure mode if it lags | reads a transcript missing the evidence, reports "clean" — **fails open, silently, canary still green** | none — the write happens before the next tool call can fire |
| cost | bounded transcript tail read per new-file Write | ~2 ms per Bash call |
| new matcher needed | no | **yes** — `PostToolUse` currently matches only `Edit\|Write\|MultiEdit` and `WebFetch` |

The ~2 ms/Bash-call cost is real and is the price of not having a silent-blindness window. Owner
decision 2026-08-08: **take the friction.** *"Failing silently is no bueno."*

**Claims settled by this measurement:**
- `tool_response` is present on `PostToolUse` for `Bash` — **CONFIRMED** (was `[unverified]` in plan.md §2.6)
- it carries real `stdout` / `stderr`, so a 4xx/5xx, a "not found", or an empty result is detectable
- `transcript_path` is present on `PostToolUse` too — Route T remains a *fallback*, not the primary
- `duration_ms`, `effort`, `prompt_id`, `tool_use_id` are also available (unused, but free)

⚠️ Scope of the claim: measured on **Claude Code 2.1.226, macOS**, one tool (`Bash`). Not verified for
`WebFetch`, and not verified on other hosts. The `WebFetch` matcher already exists, so that half is
cheap to confirm when it matters.
