# caveman-auto-routing.md — caveman auto-routing knowledge file

This file is named as a deliverable in both P5 and P7 of
`.ravenclaude/runs/forge/caveman-routing-decision-tree/plan.md`. P5's own acceptance test (c)
requires *"a dated addendum… committed now"* — that addendum is the section below. P7 will later
add the full contract (Q1–Q4 decisions with runners-up, the runtime version-drift resolution
order, the kill-switch procedure, and the honest limits carried verbatim from the plan) once the
live-shadow soak closes P7's own two-stage entry gate. Nothing in this file is a claim that P7 has
run.

---

## 2026-09-03 — P5 offline replay calibration: the thresholds table's disconfirming probe

**What this is.** `caveman-route.py --replay <transcript>` streams an archived transcript through
the classifier turn-by-turn and emits the verdict trace it *would have* produced. This addendum
runs that mode across 12 real transcripts under `~/.claude/projects/` (P0.5 confirmed 5,534+ exist
on this host and that `caveman-stats.js --session-file <path>` runs non-interactively), correlates
the verdict trace against `caveman-stats.js`'s measured net-token estimate for the same transcript,
and reports the result honestly — including the part that came out weaker/reversed from naive
expectation, per the plan's own explicit instruction not to launder that away.

**Sample.** 12 transcripts: the 11 most-recently-modified **top-level session** transcripts across
this host's `~/.claude/projects/` tree (excluding `subagents/*.jsonl`, which are partial
sub-dispatch transcripts, not full sessions), spanning 6 distinct projects/worktrees, plus this
authoring session's own transcript (independently known tool-heavy, per P0.5's own positive
control) — which happened to also be the most-recently-modified file, so it needed no special
inclusion. Sizes ranged 5 KB–11.3 MB; turn counts 1–711.

| transcript | turns | density* | pct_off** | output tok | Est. net | net/turn |
|---|---:|---:|---:|---:|---:|---:|
| `967c7c3b…` (this session) | 136 | 0.853 | 0.412 | 142,236 | **+94,153** | 692.3 |
| `b4770ccf…` | 9 | 1.000 | 1.000 | 3,610 | **−4,546** | −505.1 |
| `5216c119…` | 38 | 0.921 | 0.711 | 53,458 | **+51,779** | 1362.6 |
| `318603d2…` | 53 | 0.981 | 0.642 | 68,486 | **+60,938** | 1149.8 |
| `40f3dcb2…` | 87 | 0.851 | 0.483 | 100,293 | **+77,508** | 890.9 |
| `878b95d0…` | 2 | 0.000 | 0.000 | 187 | **−2,153** | −1076.5 |
| `37b04c3e…` | 1 | 0.000 | 0.000 | 5 | **−1,241** | −1241.0 |
| `062f27a6…` | 451 | 1.073 | 0.882 | 403,484 | *excluded†* | — |
| `2f7a3803…` | 183 | 0.907 | 0.443 | 109,698 | *excluded†* | — |
| `b64cef65…` | 83 | 0.867 | 0.482 | 74,848 | *excluded†* | — |
| `d021398c…` | 58 | 1.034 | 0.828 | (n/a) | *excluded†* | — |
| `b3bd7749…` | 711 | (n/a) | (n/a) | (n/a) | *excluded†* | — |

\* `density` = unwindowed `tool_use_blocks / responses` over the **whole** transcript (the
classifier's own deduped aggregation, not the trailing-6 window `--replay` uses per turn — this is
a session-level summary statistic computed for this correlation only, not something the classifier
itself produces).
\** `pct_off` = fraction of the `--replay` trace's turn-by-turn verdicts that were `"off"`
(`pct_on` was 0.000 in every one of these 12 — none contained a sustained 4-response clean-prose
streak; expected, since this host's real sessions skew tool-heavy).
† **`caveman-stats.js` genuinely could not produce a net figure for 5 of the 12 transcripts** —
its own stdout states *"Mode was set mid-session — only output after the change is attributed"* and
excludes the whole span rather than guess. This is a real, load-bearing finding in itself (below).

### The finding, reported in two layers because the naive number is misleading on its own

**Layer 1 — the naive, full-sample correlation is POSITIVE, the opposite sign from the naive
expectation.** Across the 7 transcripts with a usable `net`: Pearson r(density, net/turn) = **+0.80**,
r(pct_off, net/turn) = **+0.55**. Taken at face value this says *more* tool-heavy sessions
correlate with *more* net savings — backwards from claims-table row 3's premise that a tool-dense
stretch is where caveman's rule overhead stops paying for itself.

**Layer 2 — the reversal is a confound, and controlling for it flips the sign to the expected
direction.** `caveman-stats.js`'s own net formula is (verified directly from its own output,
`docs/HONEST-NUMBERS.md`-cited): `net = tokens_saved − rule_overhead`, where `rule_overhead` is a
**flat** `1,250 tokens × turns` and `tokens_saved` is a **flat ~65% reduction applied uniformly to
whatever output tokens exist**, regardless of turn shape. Algebraically this collapses to
`net/turn ≈ 1.857 × (output_tokens/turn) − 1250` — and measured directly on this sample,
**r(output_tokens/turn, net/turn) = 0.99999999...** (as close to deterministic as floating point
allows). `caveman-stats.js`'s aggregate net is therefore driven almost entirely by **response
verbosity**, not tool-call density, by construction of its own model. In this small sample the two
shortest sessions (1 and 2 turns) happened to have both zero density *and* the lowest
output-tokens-per-turn — not because prose-only sessions are inherently terse, but because a
1–2-turn session is too short to be a real signal of anything, and its overhead dominates on pure
arithmetic. Excluding those two (`turns < 9`) and recomputing on the remaining **n=5** substantive
sessions: **r(density, net/turn) = −0.40, r(pct_off, net/turn) = −0.62** — moderate, and now in the
**expected** direction (more tool-heavy → lower net-per-turn). The single cleanest, least-confounded
data point in the whole sample — `b4770ccf…`, a sustained 9-turn session the classifier scored
`pct_off = 1.000` (every turn tool-heavy) — is also the only substantive-length session with a
**negative** net (−505/turn), exactly what the premise predicts.

### The honest verdict on row 3 (claims-table's load-bearing inference)

**Weak-to-moderate, and it took controlling for a confound to see it.** The signal exists (n=5,
r=−0.62, direction-consistent with the premise), but:

- **This is not a settlement.** n=5 substantive sessions is not enough to fit or validate any of
  the plan's specific `[unverified]` thresholds (`W=6`, the off-trigger's `≥2`/`≥1.0`, the 4-response
  on-streak). It is evidence the underlying *direction* of the premise is not obviously wrong — no
  more.
- **A genuine instrument mismatch, not just a small-sample problem.** `caveman-stats.js` produces
  **one aggregate number per session** (or per contiguous same-mode span); the classifier's replay
  trace is **turn-by-turn**. Correlating a single scalar against a whole trace necessarily throws
  away exactly the within-session shape-change signal row 3 is about (*"a session's shape can change
  mid-conversation"*) — the two instruments are at different granularities by construction, and no
  amount of additional whole-session sampling fixes that; it would need either a per-turn savings
  breakdown `caveman-stats.js` does not expose, or genuinely single-shape (all-tool or all-prose)
  sustained real sessions to compare cleanly, which are rare in this host's actual usage (every
  substantive session in this sample mixed both).
- **The mode-attribution exclusion (5 of 12, 42%) is itself informative.** A meaningful fraction of
  real transcripts on this host already had caveman manually toggled mid-session, which
  `caveman-stats.js` correctly refuses to attribute rather than guess. Any future, larger replay run
  should expect a comparable exclusion rate and budget the sample accordingly (i.e., sampling *more*
  than the number of comparisons ultimately needed).

**What this changes for P7's entry gate.** Per plan.md, *"if the shadow verdict does not correlate
with the measured net token delta, the thresholds change before the flip — or the flip does not
happen."* This addendum's finding is neither a clean pass nor a clean fail: it is **weak,
direction-consistent evidence once a real confound is controlled for, on a sample too small to
fit numbers from.** The honest reading is that offline replay on this host's available corpus
cannot, by itself, settle the thresholds precisely — which is exactly why plan.md sequences P7's
entry gate as **two stages**, not one: this addendum satisfies stage 1's spirit (replay run,
correlated, reported honestly — including the reversal and its cause) without pretending it
substitutes for stage 2's live shadow soak, which sees genuine per-turn behavior this instrument
mismatch cannot.

**Reproducing this analysis.** The transcript list, `--replay` invocations, and the pure-Python
Pearson-correlation arithmetic used above are one-off / not shipped as a plugin script (per the
plan's file table, only `caveman-route.py` itself — including `--replay` — is a P1/P5 deliverable).
Anyone re-running this: `python3 plugins/ravenclaude-core/scripts/caveman-route.py --replay
<transcript.jsonl>` for the trace, `node <caveman install>/src/hooks/caveman-stats.js
--session-file <transcript.jsonl>` for the net figure (same invocation P0.5 already verified
non-interactive), and a plain Pearson correlation over whatever pairs both instruments can produce
(watch for the mode-attribution exclusion above — a `net` field absent from `caveman-stats.js`'s
output means that transcript should be excluded, not treated as zero).

---

## 2026-09-03 — P5 offline replay, run to exhaustion: the corpus was searched fully, not sampled,
## and the confound-controlled correlation is weaker and non-robust, not stronger

**What this is and why it exists.** P7's own entry criterion frames P5's replay as a *disconfirming
probe*, and its addendum above candidly labeled its own n=5 confound-controlled result "too small a
sample to fit any threshold from." This addendum grows the sample the honest way: instead of drawing
a second, larger *sample*, it runs `caveman-route.py --replay` and `caveman-stats.js --session-file`
against **every single top-level transcript on this host** — 4,189 of the 4,189 top-level (non-
subagent) `.jsonl` files under `~/.claude/projects/`, i.e. the full census P0.5 took (5,534 total,
minus subagent transcripts, excluded by the same convention P5 already used: partial sub-dispatch
transcripts are not full sessions). This is not a stratified sample that happened to be large — it is
the entire available population, run exhaustively, so "was the sample representative?" is no longer a
live question for this host at this moment. Runtime: ~110 seconds total (8-way parallel; each
transcript costs two ~0.03s Python calls plus one ~0.03s Node call).

**The finding that reframes everything below, found before any correlation was computed.** The
instrument-mismatch exclusion P5 flagged as "a real, structural limit" turned out to be **far more
severe at full-corpus scale than P5's small sample suggested, and the mechanism is now understood
precisely.** `caveman-stats.js` attributes a session's whole net figure to the *current* value of a
single, global, cross-session, cross-repo `.caveman-active` mode flag whenever no session-tagged
transition-log row exists for that session — and it does that attribution by comparing the flag's
**current mtime** (whatever it is *at query time*, not at any historical point) against the session's
first timestamped message. On this host, `~/.claude/.caveman-mode-log.jsonl` shows **123 mode-flag
toggles, all within a single ~4-hour window today (06:20–10:16)**, evidently from active development
and testing of this very caveman-routing feature. Because the flag was touched this recently, **every
transcript whose first message predates that window** — which is nearly all of them — fails
`caveman-stats.js`'s uniform-mode check and gets `basis: "flag-mtime"`, excluding its whole-session
net figure. Measured directly: **4,022 of 4,189 transcripts (96.0%)** were excluded this way, vs.
P5's 5 of 12 (42%) on its small, same-day sample. This is not a new confound — it is the *same*
instrument-mismatch P5 already named, now quantified at its true severity and shown to be **driven by
a single global mutable flag's recency, not a fixed property of the corpus**. It will vary from
session to session depending on how recently caveman mode was last toggled on this machine; a re-run
on a "quiet" day (flag untouched for weeks) would very plausibly clear far more of yesterday's
sessions while newly excluding almost nothing from that quiet stretch — and would just as plausibly
newly exclude sessions from *today*, once today's flag-touch train recedes into the past. Sample size
cannot fix this; only a quiet flag-history epoch containing the sessions you want to measure can.

**Exclusion breakdown, full corpus (n=4,189):**

| Category | Count | % of corpus |
|---|---:|---:|
| Empty / no conversation yet | 15 | 0.4% |
| Mid-session mode change (`flag-mtime` basis — instrument mismatch) | 4,022 | 96.0% |
| **Usable net figure** | **152** | **3.6%** |

Of the 152 usable, applying **P5's own exact confound-exclusion criterion, unchanged and untuned**
(`turns < 9` excluded — small-n sessions where fixed per-turn rule overhead dominates the arithmetic):

| Turn-count bucket | Count |
|---|---:|
| 1–2 turns (trivial) | 139 |
| 3–8 turns (near-trivial) | 6 |
| **≥9 turns (substantive — the primary-analysis set)** | **7** |

The gap between 8 and 20 turns has **zero** transcripts in it — there is no data point anywhere near
the boundary, so `turns < 9` is not an arbitrary line on this dataset; it cuts cleanly.

**A methodology bug found and fixed while computing "unwindowed, whole-transcript density."**
`caveman-route.py --replay <path> --window 0` does **not** disable windowing — `main()`'s override
logic is `args.window if args.window and args.window > 0 else knobs["window"]`, and in Python `0` is
falsy, so `--window 0` silently falls through to the **default W=6** knob instead. This was caught
by a direct discrepancy: a transcript whose density P5 originally recorded as 0.981 (53 turns,
`318603d2…`) recomputed as 0.667 under the buggy `--window 0` call. `--window 999999` is the correct
override (any window larger than the transcript's own response count degenerates to the classifier's
cumulative-from-start aggregation, matching P5's stated definition exactly) — verified directly
against the same transcript, which reproduced P5's 0.981 exactly. All density figures below use the
`--window 999999` form. This is a pure analysis-script issue, not a change to `caveman-route.py`
itself (no product code was touched, per this addendum's boundary).

**The 7 substantive transcripts.** Five of the seven are the **same underlying sessions** P5's
original n=5 measured (matched by session id) — they are long-running worktree sessions from this
same feature's own development that were simply still open and had grown since P5 ran; two
(`5e17c36d…`, `6dd38014…`) are genuinely new to this corpus. `density` = the classifier's own
`avg_tool_use_per_response` over the whole transcript (unwindowed, per P5's definition);
`pct_off`/`pct_on` = the default-window (W=6, production settings) `--replay` trace's fraction of
`off`/`on` verdicts; `net`/`net per turn` = `caveman-stats.js`'s figure.

| transcript | turns | density | pct_off | net | net/turn | out tok/turn |
|---|---:|---:|---:|---:|---:|---:|
| `5e17c36d…` | 68 | 0.7792 | 0.382 | +10,147 | 149.2 | 753.4 |
| `40f3dcb2…` | 149 | 0.8412 | 0.510 | +79,238 | 531.8 | 959.4 |
| `6dd38014…` | 56 | 0.8500 | 0.518 | +27,923 | 498.6 | 941.6 |
| `5216c119…` | 138 | 0.9058 | 0.609 | +89,023 | 645.1 | 1020.4 |
| `318603d2…` | 53 | 0.9811 | 0.641 | +60,938 | 1149.8 | 1292.2 |
| `967c7c3b…` (this session) | 168 | 0.8412* | 0.387 | +100,329 | 597.2 | 994.6 |
| `b4770ccf…` | 35 | 1.1143 | 1.000 | +662 | 18.9 | 683.3 |

*`967c7c3b…`'s own density printed 0.8412 in this run's raw output alongside `40f3dcb2…`'s — both
values verified independently from their own `--window 999999` traces; the coincidence is real, not
a copy error.

**Every one of the 7 substantive sessions is net-positive.** None crosses into negative territory —
not even `b4770ccf…`, the most extreme (density 1.11, `pct_off=1.000` — every single trace turn
classified tool-heavy). That matters for the task's requested binary-split analysis: **there is no
net-negative example anywhere in the substantive population, so a clean net-positive/net-negative
separation by density threshold cannot be constructed — there is nothing on the negative side to
separate from.** Mechanically, `net/turn ≈ 1.857 × (output_tokens/turn) − 1250` (P5's own derived
formula, confirmed again this run — see below), and every one of these 7 sessions' output-tokens-per-
turn sits above the ≈673 tok/turn breakeven line, so none crosses zero. `b4770ccf…` sits closest
(683.3 tok/turn, barely above breakeven) — notably, at P5's original measurement it was 9 turns and
net **−505.1/turn** (P5's cleanest confirming data point); it has since grown to 35 turns and flipped
to **+18.9/turn**. The single most extreme, most premise-confirming data point in P5's original
sample turned out to be unstable under its own growth — a warning sign for everything downstream.

### Layer 1 — the naive full-sample correlation reproduces P5's finding, more strongly, at 12× the raw n

Across all 152 transcripts with a usable net figure (the naive, uncontrolled sample — no `turns<9`
exclusion):

- **r(density, net/turn) = +0.830**
- **r(pct_off, net/turn) = +0.681**
- **r(output_tokens/turn, net/turn) = 0.99999992** — the confound, essentially deterministic, exactly
  as P5 found (0.99999999…) — `caveman-stats.js`'s net figure is, by construction of its own formula,
  almost entirely a function of response verbosity per turn, not tool-call density.

This is P5's Layer-1 finding, replicated cleanly at ~12.7× the original raw sample size (152 vs. 12),
same sign, similar magnitude. The confound is not a small-sample artifact — it holds at scale.

### Layer 2 — confound-controlled (turns ≥ 9, n=7): weaker than P5's n=5, and not robust

- **r(density, net/turn) = −0.060** — essentially zero. Not the moderate −0.40 P5 reported.
- **r(pct_off, net/turn) = −0.236** — weak, direction-consistent with the premise, but roughly a
  third the magnitude of P5's −0.62.
- **r(output_tokens/turn, net/turn) = 0.99999999937** — the confound holds identically at this
  smaller n too.

**Leave-one-out sensitivity — this is the decisive finding.** `b4770ccf…` (pct_off=1.000, the single
all-tool-heavy extreme) is the only one of the 7 with a fundamentally different shape from the other
six. Dropping it (n=6, the six "ordinary" substantive sessions):

- **r(density, net/turn) = +0.966**
- **r(pct_off, net/turn) = +0.765**

Both **flip sign, strongly, to the wrong direction** for the premise. The entire weak negative
correlation reported above is carried by exactly one data point. Remove it and the remaining six
sessions show tool-density and net-per-turn moving strongly **together**, the opposite of row 3's
prediction. At n=7 (or n=6), **the sign of the confound-controlled correlation is not a stable
property of this dataset — it is a property of whichever single point happens to be included.**

**A secondary, honest observation, not folded into the primary comparison per P5's own methodology:**
the 6 near-trivial transcripts (turns 3–8, excluded by the `turns<9` criterion) are **uniformly
net-negative** (net/turn ranging −782 to −994), consistent with P5's stated rationale for the
exclusion — a session too short is dominated by fixed per-turn rule overhead regardless of its actual
tool density, exactly the arithmetic artifact the criterion exists to strip out. This is supporting
evidence the exclusion criterion is doing its job, not a data point that should be folded back into
the correlation.

### The honest verdict — searching further did not, and structurally cannot, strengthen this

**This is not a sampling failure.** The full corpus was searched exhaustively — every top-level
transcript on this host, at this moment, was included. There is no larger substantive (turns ≥ 9,
uniform-mode) sample obtainable from this host via offline replay right now; the population is
capped at exactly 7 by the two structural limits above (the instrument-mismatch exclusion rate and
the corpus's own small population of long, real, non-degenerate sessions). Searching more transcripts
tomorrow, next week, or against a different sampling strategy will not change this — 5 of the 7
found are the *same underlying long-running sessions* P5 already measured, simply grown; the corpus's
population of "real, substantive, currently-uniform-mode" sessions on this host is genuinely this
small.

**The correlation did not strengthen with more data — it got weaker, and it stopped being robust.**
P5's original confound-controlled read (n=5, r=−0.40 / r=−0.62) is now, at the true achievable maximum
sample (n=7), r=−0.06 / r=−0.24 — both weaker — **and the sign is not stable under leave-one-out**:
remove the single most extreme point and both correlations flip to strongly positive. A correlation
whose sign depends on the inclusion of one data point is not evidence of a real, reliable relationship
in either direction; it is evidence the sample is too small to say anything reliable about the
relationship's direction at all.

**Specific thresholds are NOT set by this evidence, and none of the `[unverified]` markers in the
plan's thresholds table (`W=6`, the off-trigger's `≥2`/`≥1.0`, the 4-response on-streak) are changed
here.** n=7, with a sign-unstable confound-controlled correlation, is not merely "still small" —
it is a demonstration that this specific offline-replay methodology, run to its full achievable
extent on this host, cannot currently distinguish a real negative relationship from noise. Setting a
numeric threshold from this data would manufacture false confidence that the evidence explicitly does
not support.

**The direct verdict on P7's stage-1 entry gate: NOT CLEARED — functionally a null result, not a
confirmed correlation.** The plan's own gate language: *"If the shadow verdict does not correlate
with the measured net token delta, the thresholds change before the flip — or the flip does not
happen… A null result at stage 1 is a legitimate outcome that stops the plan; it does not license
proceeding to stage 2 to 'see if it works live.'"* This addendum's confound-controlled result — a
correlation whose sign reverses under leave-one-out at the maximum achievable sample size — is not a
disconfirmed (reversed) correlation, but it is also not a demonstrated one. It is functionally
indistinguishable from a null result: no reliable direction can be read from it. Per the plan's own
explicit rule, that is a legitimate stopping outcome, and it does **not** license moving to P7 stage 2
(the live shadow soak) on the strength of this stage alone. This is a *stronger*, more decisive
finding than P5's own read of itself ("weak-to-moderate… on a sample too small to fit numbers from")
precisely because the corpus is now known to be exhausted rather than merely under-sampled: this is
not "gather more offline-replay data and try again" — on this host, right now, there is no more
offline-replay data to gather. If the plan proceeds, the honest paths are (a) wait for this host's
mode-flag history to settle into a longer quiet stretch and re-run against whatever real, substantive,
non-degenerate sessions accumulate during it (not fixable today), (b) run the same methodology against
a different host with a larger, more settled population of real usage, or (c) the plan's own owners
revisit whether offline replay is a viable stage-1 mechanism at all on a host where the underlying
instrument (`caveman-stats.js`) is this sensitive to a single global mutable flag's recent history.

**Reproducing this addendum.** Same invocations as P5's original methodology, with two corrections:
use `--window 999999` (never `--window 0`) to get the classifier's true unwindowed whole-transcript
density, and run against the **full** top-level transcript census (`find ~/.claude/projects -name
'*.jsonl' | grep -v /subagents/`), not a recency-biased slice — on this host that took under two
minutes with 8-way parallelism, so there is no runtime reason to sample rather than run exhaustively.
