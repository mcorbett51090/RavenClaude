# Evidence base — three incidents from one session (2026-08-07 → 08)

All three are **real, measured, and from the same session**. Do not treat these as hypotheticals.
Design against these, not against a general notion of "being careful".

---

## Incident 1 — THE EXPENSIVE ONE: unbounded construction on an unfalsified premise

**Observation (true).** Production HTML contained `[email protected]` and
`href="/cdn-cgi/l/email-protection#<hex>"` — Cloudflare Scrape Shield's email obfuscation.

**Probe (true result, wrong target).**

    GET https://www.ravenpower.net/cdn-cgi/l/email-protection   ->  404

**Inference (FALSE).** "The decoder is broken, therefore every visitor sees a mangled address and a
dead link. P1."

**What got built on it, before anyone tested it:**
- an 85-line `Email.astro` component whose *entire reason to exist* was this premise
- 10 call sites converted to it
- 15 `<!--email_off-->` marker pairs across 5 files
- a long header comment asserting the cause as established fact ("measured 2026-08-07")
- a go-live checklist item added to the owner's cutover doc and pushed to `main`
- two turns of detailed owner-facing analysis of a `set:html` architectural trade-off,
  including a recommended Cloudflare dashboard change

**The truth, found ~14 hours later:**

    GET /cdn-cgi/l/email-protection   -> 404   # a PLACEHOLDER href. Nothing ever fetches it.
                                               # It is SUPPOSED to 404.
    GET /cdn-cgi/scripts/<id>/cloudflare-static/email-decode.min.js -> 200   # the real decoder
    GET /cdn-cgi/trace                -> 200   # so the edge is healthy; the Worker is NOT
                                               # swallowing /cdn-cgi/* either

Real browser against production, with none of the "fix" deployed — i.e. against the allegedly
broken state:

    span.__cf_email__ remaining ... 0
    href ......................... mailto:matt@ravenpower.net
    link text .................... matt@ravenpower.net
    "[email protected]" in body ... false

**No user had ever seen the reported bug.** Worse: the "fix" opted 15 addresses out of the
anti-scraping protection that was the only thing the feature was doing — publishing them in plain
text to harvesters, to repair nothing.

**Cost asymmetry, which is the whole point:** the disconfirming probe (`/cdn-cgi/trace`, or one
browser load) cost **~10 seconds**. The construction cost several hours, touched 16 files, reached
the owner's checklist, and shaped two turns of architectural advice.

**⛔ The critical structural detail — this is what a mechanism must target.** The wrong hypothesis
was cheap and normal. The damage came from the hypothesis being **silently promoted to a premise by
being written down**. Once it was prose in a component header, it was repo fact, and every
downstream artifact cited it instead of re-testing it. Nothing in the process ever returned to ask
whether it was true.

**Note on why existing FORGE G1 would NOT have caught it.** G1 validates *provenance*: is this claim
backed by a source or an in-session tool call? "The decoder is broken" WAS backed by an in-session
tool call (the 404). G1 has no notion of **inferential distance** — the gap between
`GET X returned 404` (verified observation) and `the decoder is broken` (unverified inference).
The observation was true; the inference was false; G1 checks only the former.

---

## Incident 2 — a generator reported success while deleting 806 files

While fixing four version-pin audit failures, the whole `regenerate-artifacts` battery was run
instead of only what the change needed. `render-trees.py` **printed `ok`** and deleted 800+ tree
SVGs plus 186 concept visuals — it requires a renderer not present on that host.

Caught **only** because an unrelated gate (Gate 141, plugin-detail island render) had passed on the
first audit run and failed on the second. The generator's own report said success. Nothing in the
commit path flagged that a documentation change was about to delete 806 tracked files.

Relevant existing machinery that did NOT fire: the repo has a `diff-budget` skill and 688 audit
gates. Neither is wired to run automatically before a commit.

---

## Incident 3 — a review loop that could not converge

    round 1:  7 findings closed
    round 2:  7 findings closed   — 2 were defects introduced by round 1's fixes
    round 3:  8 findings closed   — 2 were defects introduced by round 2's fixes

~25% of every round was self-inflicted and the rate was not falling. Each round was a fresh cold
read of the *current* tree, so previously-closed findings were never re-checked and regressions had
to be rediscovered at full price. A loop that only reads current state has no fixed point: every fix
is new code that has never been reviewed.

---

## What is already shipped (do not re-propose these)

`knowledge/verification-discipline.md` (PR #849, this branch) states seven rules as **prose**, wired
into 5 agents + `spawn-team` Step 7:

1. Turn a coverage claim into a script BEFORE making it
2. Assert the property that DEFINES the effect, never a proxy
3. Never `grep` your own gate output
4. Platform primitive over hand-rolled string handling
5. Run the gate yourself after every agent handoff
6. Prove the instrument before believing its verdict (negative control; stability ≠ validity)
7. Measure what the user experiences, not the nearest proxy
   + the structural review-loop rule (feed prior findings back; check reopens first; know when to stop)

**These are prose, and prose gets copy-pasted past.** The repo's own catalogue says so. The question
this run must answer is what **mechanism** — gate, script, artifact contract, checkpoint — catches
Incident 1's shape *before* the construction phase, not after.
