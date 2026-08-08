# Verification discipline — how to know a claim is true before you make it

> **Provenance.** Every rule below was paid for. Each was derived from a specific
> false claim made during one long build session on `RavenPower-Website`
> (2026-08-07 → 08), and each carries the incident that produced it. The dates and
> numbers are real; keep them. A rule stated as a principle gets argued away, and
> a rule carrying a receipt does not.
>
> Companion to [`consistency-failure-modes.md`](consistency-failure-modes.md),
> which catalogues defects that ship green. **That file is about the code. This
> file is about the claim.** The two fail together: a defect ships green, and then
> someone reports it fixed.

**The one-line version:** *a claim about coverage, correctness, or completeness is
a measurement or it is a guess — and a guess stated in the past tense is a lie you
have not noticed yet.*

---

## Why this file exists

In a single session an agent produced, in good faith, all of the following — every
one of which passed a build, a full test suite, and a clean `astro check`:

| claim | reality |
|---|---|
| "every email address on the site is fixed" | said twice, wrong twice; a third page was found later |
| "the upload promise is closed" (commit message) | the endpoint existed, the UI did not |
| "`--repeat 3` — identical, 0 findings, ✓ deterministic" | the harness was blind; it bound no arguments and measured nothing |
| "the Cloudflare email decoder 404s, every visitor sees `[email protected]`" | the decoder returns **200**; no visitor ever saw it |

The last one is the most instructive and is worked through in Rule 7. An 85-line
component, ten call sites, a go-live checklist item and two rounds of design
discussion were built on a single `curl` of the wrong URL.

**None of these were caused by weak reasoning.** They were caused by *asserting a
property that had not been measured*, in a form no gate could contradict.

---

## Rule 1 — Turn the claim into a script BEFORE you make the claim

**Incident.** "I fixed every email address on the site." Wrong. Fixed a subset,
said all. Corrected. Said all again. Wrong again — `/call` was still bare. The
claim only became reliable when it stopped being a claim: a script that scans
built output and prints `unwrapped: N`. From then on the answer was a number that
re-derived itself every round, and the third page was found in seconds.

**The rule.** Any claim quantified over a set — *every*, *all*, *none*, *no
remaining*, *N of N* — must be produced **by a script, before you say it**. Not
verified after. Produced by.

**Why "before" is load-bearing.** A script written afterward is written by someone
who already believes the answer, and it will be shaped — unconsciously — to agree.
Written first, it is a question. Written second, it is a rubber stamp.

```bash
# Not: "I checked all the pages."     ← an attention claim, unfalsifiable
# But:
$ ./check-addresses.sh
pages scanned: 10   unwrapped: 0   literal markers: 0
```

Attention does not scale over a set and does not survive a context switch. A
script does both, costs about five minutes, and reruns free forever.

**Applies to:** "all call sites updated", "no other usages", "every route
covered", "nothing else references this", "the whole fleet is on Node 22".

---

## Rule 2 — Assert the property that DEFINES the effect, never that something changed

**Incident.** A CSS lens shipped visibly broken while its test passed: the test
asserted that pixels differed, and pixels differ for a hundred reasons. Later, in
the same repo, extracting an anchor into a child component stopped Astro stamping
`data-astro-cid-…` on it, so a scoped rule compiled to a selector matching
nothing and the page's headline contact email silently dropped to body text. The
page still rendered. Every test passed.

**The rule.** Name the property that makes the feature *the feature*, and assert
exactly that. Never assert a proxy: "it renders", "something changed", "no error
was thrown", "the file contains the string".

| proxy (worthless) | the property (assert this) |
|---|---|
| the page renders | the built selector matches a built element |
| the import is present | the component tag appears in the markup |
| pixels changed | `backdrop-filter` is a computed value on the node |
| the response is 200 | the response body carries the field the caller reads |
| the string is in the file | the string is in the container the consumer parses |

**The diagnostic question:** *could this assertion pass while the user-visible
behaviour is completely broken?* If yes, it is a proxy. Every entry in
`consistency-failure-modes.md` is a proxy that passed.

---

## Rule 3 — Never `grep` your own gate output

**Incident.** `astro check | grep -E "error"` reported clean. It also discarded
six `ts(6133)` **warnings** — unused imports — which were the precise evidence
that an upload UI had never been wired up. The filter removed the only signal
that would have caught it, and did so silently.

**The rule.** Read the gate's own summary line. Do not filter, do not `grep`, do
not `tail -1`, do not `2>/dev/null` a tool whose diagnostics you are relying on.
If output is genuinely too long, raise the gate's own verbosity controls — never
a downstream filter.

```bash
npx astro check 2>&1 | grep error        # ⛔ deletes warnings, silently
npx astro check 2>&1 | tail -4           # ✅ keeps the summary: errors AND warnings
```

**Why it is worse than it looks.** A filter that hides a signal produces the same
output as a run that had no signal. You cannot tell the two apart afterward, and
neither can a reviewer reading your transcript.

---

## Rule 4 — Reach for the platform primitive before hand-rolling string handling

**Incident.** A hand-written `Content-Disposition` header builder called
`encodeURIComponent` on a filename that had been truncated with `.slice(0, 255)`.
Slicing at 255 UTF-16 code units can split a surrogate pair, leaving a lone
surrogate, on which `encodeURIComponent` throws `URIError`. Result: a customer
uploads a file whose emoji straddles index 255, and the operator's download
button returns 500 forever. The fix for a header-injection hole introduced a
crash.

**The rule.** Encoding, escaping, quoting, parsing, normalising — use the
platform's implementation. When you must hand-roll, enumerate the adversarial
input classes *in the test file*: empty, lone surrogate, combining marks, RTL
override, embedded newline/quote/semicolon, > 255 bytes vs > 255 code units, and
the ASCII-only fallback path.

Hand-rolled string code fails on inputs that never appear in development and
always appear in production.

---

## Rule 5 — Run the gate yourself after every agent handoff

**Incident.** Twice in one session a subagent reported its task complete having
left a hard compile error in the tree — once a symbol referenced but never
imported. Both were caught by running `astro check`, which takes about thirty
seconds. Neither was caught by reading the agent's report, which was confident,
detailed, and wrong.

**The rule.** A subagent's report is a **claim**, subject to every rule in this
file. It is never evidence. Run the build, the gate and the tests yourself before
the work is passed on, committed, or described to a human as done.

**Corollary — the report and the tree can disagree in either direction.** An agent
may also report failure on work that is fine. Check the tree, not the prose.

---

## Rule 6 — Prove the instrument before you believe its verdict

**Incident (twice in one session).** A browser harness passed its own `--repeat 3`
determinism check — *"identical across runs, 0 findings, ✓ deterministic"* — across
ten production routes while measuring **nothing**: `page.evaluate(string, arg)`
does not bind the argument, so every probe read `undefined`. Later, a scanner
written to *enforce Rule 1* reported two mangled addresses inside JSON-LD; both
were false. Its `application/ld\+json.*?\[email` pattern ran with `DOTALL` and
matched from the JSON-LD tag to a marker 20KB later in the page footer.

**The rule.** A new checker's first output is a claim about **the checker**, not
about the subject. Before believing any verdict, **plant a defect it must find**
and confirm it fails. Ship the negative control *inside* the checker so it can
never silently go blind:

```python
canary = '<script type="application/ld+json">{"email":"[email protected]"}</script>'
assert len(scan(canary)) == 1, "⛔ SCANNER IS BLIND — its clean verdict means nothing"
```

**⛔ Stability is not validity.** A broken instrument is *more* reproducible than a
working one — it returns the same empty answer every time. Determinism checks,
repeat runs and "consistent across N trials" are evidence about noise, never about
correctness.

**Report the instrument's verdict separately from the subject's.** "0 findings"
and "0 findings, canary ARMED" are different sentences.

---

## Rule 7 — Measure what the user experiences, not the nearest available proxy

**Incident, in full, because it cost the most.** Production HTML contained
`[email protected]` and `href="/cdn-cgi/l/email-protection#<hex>"` — Cloudflare's
Email Obfuscation. `curl` of that href returned **404**, so: the decoder is
broken, every visitor sees a mangled address, this is a P1. Built a component,
converted ten call sites, wrote an 85-line rationale, added a go-live checklist
item, and advised the owner on a `set:html` trade-off.

**All of it was wrong.** `/cdn-cgi/l/email-protection` is *supposed* to 404 — it is
an href placeholder that nothing fetches. The real decoder is elsewhere and
returns 200. Driving a real browser against the supposedly-broken production site
gave:

```
span.__cf_email__ remaining ... 0
href ......................... mailto:matt@ravenpower.net
"[email protected]" in body ... false
```

No user had ever seen the bug. Worse, the "fix" opted 15 addresses out of
Cloudflare's anti-scraping protection — the only thing the feature was doing —
so it published them in plain text to every harvester to repair nothing.

**The rule.** For anything whose truth depends on a runtime the repo cannot see —
a browser, an edge network, a CDN, a mail client, a device — **the source is not
the artifact and `curl` is not a user.** Measure the rendered end state.

**Run the control — don't rely on remembering to.** `rc probe http <url>` (or
`scripts/probe-kit.sh`) probes the thing **and** a known-good control on the same subsystem, and tells
you which of four situations you are in: negative confirmed · **control also failed** (your probe
target is wrong, not the subject) · positive · inconclusive. `rc probe --explain` states what a
negative result does and does not license. The control that would have killed this incident cost ten
seconds, and nobody ran it — because running it required thinking of it first. That is what the kit
removes.

**And the deeper one: a 404 is not a diagnosis.** Before building on a negative
result, establish that you probed the thing that carries the behaviour. One
control request would have settled it in ten seconds — `/cdn-cgi/trace` returns
200, so the edge was healthy and the theory was dead. **Cheap disconfirming probes
come first, because the cost of the wrong ones compounds into everything built on
top.**

---

## The structural rule — a review loop that only reads current state cannot converge

Three rounds of automated code review on one branch:

```
round 1:  7 findings closed
round 2:  7 findings closed   — 2 were defects introduced by round 1's fixes
round 3:  8 findings closed   — 2 were defects introduced by round 2's fixes
```

A steady ~25% of each round was self-inflicted, and the rate was not falling.

**Why.** Each round was a fresh cold read of the *current* tree. But every fix is
new code that has never been reviewed, so there is always something to find — the
loop has no fixed point. Meanwhile the previous round's findings were never
re-checked, so regressions had to be rediscovered from scratch at full price.

**The rule — two changes make it converge:**

1. **Feed every round the previous rounds' closed findings** and ask first: *did
   any of these reopen?* Cheap, targeted, and it catches the regression class
   directly instead of rediscovering it.
2. **Scope each round to the diff since the last round**, not the whole tree.
   Unbounded re-reads find unbounded new opinions.

**And know when to stop.** The expected value of round *N* is
*(real defects found) − (defects introduced)*. That crosses zero. When a round's
findings are mostly the previous round's fixes, **stop and ship** — running
another round is negative-value work that feels like diligence. Shipping the
risky part behind a flag is what makes stopping safe.

---

## What does NOT go away

Stated plainly so nobody plans around a fix that does not exist.

- **No persistent model of the repo.** Every agent starts cold, reads a slice,
  edits. Couplings that no artifact records — Astro scoped CSS ↔ component
  extraction, an edge rewrite ↔ a `<title>` tag — have to be rediscovered by
  breaking them. A maintainer of a year flinches; a cold reader cannot.
- **Fix passes are more dangerous than build passes.** They are surgical edits
  into partially-loaded code, and review loops structurally reward *narrow, cheap*
  edits — exactly the profile that produces non-local damage.
- **Therefore: prefer one wider, well-understood change over five narrow ones.**
  When a fix would touch ten call sites late in a session, the smallest correct
  change is usually one file, and the honest move is often to stop.

These are the residual ~30%. Rules 1–7 address the other ~70%, and that share is
not theoretical — it is the share of the session's false claims that a script, a
control, or an unfiltered gate would have caught before they were spoken.
