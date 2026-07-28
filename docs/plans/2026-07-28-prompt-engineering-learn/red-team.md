# G5 — Red team: `prompt-engineering-learn`

**Adversarial pass over `plan-A.md` + `plan-B.md` as tiebroken by `tiebreaks.md`.** Goal is to break the
plan before it is built, not to improve it. Every finding below carries a this-session probe (command +
output) or a `file:line`. Findings ranked by severity. §9 lists what I attacked and **failed** to break —
recorded so G6 does not re-open settled ground, and so my own falsified hypotheses are visible.

**Attack surface actually exercised this session:** `scripts/serve-dashboards.py` (both copies),
`scripts/check-dashboard-server-parity.py`, `scripts/check-prompt-builder-render.mjs`,
`scripts/check-dom-budget.py` (real measurement + a simulated build), `scripts/check-committed-routes.mjs`,
`scripts/check-router-execution.mjs`, `scripts/concepts.py`, `scripts/generate-dashboards.py`,
`scripts/render-concepts.py`, `scripts/audit-gates.sh`, `.github/workflows/regenerate-artifacts.yml`,
`.github/workflows/validate-marketplace.yml`, the live puppeteer cache, and `git status` on `main`.

---

## Severity ladder

| # | Finding | Severity | Blocks build? |
|---|---|---|---|
| R1 | The 90-day `platform-fact` gate is **already armed** and detonates in ~26 days — and it **aborts the whole post-merge self-heal**, silently | **CRITICAL** | **YES — decide before Phase 1** |
| R2 | A missing concept SVG renders as a **blank well** and **no PR-time gate catches it** | **HIGH** | Blocks merge, not start |
| R3 | Gate 32 is **one-directional and hyphen-blind**; Plan A's `/__host` gets **zero** body-parity enforcement | **HIGH** | **YES — decides the endpoint + function name** |
| R4 | `/__host`'s real leak is an **unbounded env-NAME enumeration in a shareable browser page**, and **no gate covers it** | **HIGH** | **YES — amendment calls this binding** |
| R5 | The ratified one-sided detector **asserts a WRONG host**, via the same inheritance defect that disqualified `COPILOT_DEBUG_NONCE` | **HIGH** | **YES — "a wrong verdict is worse than no verdict"** |
| R6 | The detector renders **"cannot determine" on the launch paths this repo itself ships** | MED-HIGH | No |
| R7 | The measured `+7` is correct **only** for a panel shape no other panel in the repo uses | MED-HIGH | No |
| R8 | Merge skew makes a **pre-approved zero-slack number wrong** through no fault of this change | MED-HIGH | No |
| R9 | Plan A's Gate-144 hardening **works**, but its UX rationale is false and it **cancels** Plan B's `syncSidebar` fix | MEDIUM | No |
| R10 | The second `#/prompt-builder` href trips `check-committed-routes` on **`href_count`** — a field neither plan mentions | MEDIUM | No |
| R11 | `main`'s working tree is **dirty with an entire unrelated in-flight feature**; both plans' `git status` acceptance tests are unsatisfiable | MEDIUM | No |
| R12 | A CSS/shared-token edit stales `feedback-report.html`, whose clean-tree gate **is** live at PR time (5 generators, not 4) | MEDIUM | No |
| R13 | `do_HEAD`'s hardcoded list, and the **"new GET must call `_local_request_ok()`" rule is enforced by nothing** | LOW-MED | No |
| R14 | `#/host-context` belongs in `check-router-execution`'s FLOOR; neither plan names it | LOW | No |
| R15 | `_discover_chrome()` picks Chrome **151** against a mermaid-cli pinned to expect **148**, and the code's own hint installs the wrong one | LOW | No |

---

## R1 — CRITICAL: the staleness gate is already armed, detonates mid-build, and takes the self-heal with it

**Scenario.** The build runs across late August. On **2026-08-23**, four already-shipped `platform-fact`
concepts cross 90 days. From that moment:

1. **Every open PR in the repo goes red**, whether or not it touches concepts —
   `.github/workflows/validate-marketplace.yml:389` runs `python3 scripts/concepts.py --check` at PR time,
   and `concepts.py:301-305` evaluates `_staleness_violations()` **before** the freshness diff and returns 1.
2. **Worse and silent: the post-merge self-heal dies.** `.github/workflows/regenerate-artifacts.yml:178-182`:
   ```
   if ! python3 scripts/concepts.py --check >/dev/null 2>&1; then
     python3 scripts/concepts.py
     python3 scripts/concepts.py --check      # <-- still fails: staleness is not fixable by regeneration
   fi
   ```
   under `set -euo pipefail` (line 164). The job aborts at **step 1b**, before the commit step — so concept
   SVGs, `dashboard.html`, `index.html`, `report.html`, the Copilot package, `feedback-report.html` and
   `docs/concepts.md` **all stop self-healing on main**. Nobody watches post-merge workflows; the first
   symptom is unrelated PRs failing freshness gates weeks later — the exact cross-PR contagion this
   workflow was built to kill.

**Trigger (measured this session, not projected):**
```
$ python3 - (parse concepts.json, kind == platform-fact)
2026-05-25  n=3   expires 2026-08-23  (26d)
2026-05-26  n=1   expires 2026-08-24  (27d)
2026-06-04  n=1   expires 2026-09-02  (36d)
2026-06-05  n=6   expires 2026-09-03  (37d)
2026-07-21  n=6   expires 2026-10-19  (83d)
total platform-fact: 17
```

This plan does **not cause** the first detonation — it inherits it, and then adds a **fifth cluster**
(6 concepts all dated 2026-07-28 → all expiring **2026-10-26**). Plan A §10's risk row calls this
"High (by construction)" and mitigates with `refresh_when:` prose + a CHANGELOG note. That is not a
mitigation for a hard CI gate; it is a reminder.

**Mitigation (all four; the third is the one that matters):**
1. **Before Phase 1**, refresh the four concepts expiring 2026-08-23/24 (re-verify + bump `last_verified`),
   or explicitly accept that CI goes red mid-build and schedule it. Either way it must be a recorded
   decision, not a surprise.
2. **Stagger** the 6 new `last_verified` dates across ≥3 weeks so this change never creates a single-day
   cliff of its own. Six concepts verified on one day is an authoring artifact, not a fact about the
   sources.
3. **Make the self-heal survive a stale platform-fact.** Step 1b must not abort the chain — a *content
   freshness* problem must never disable *artifact healing*. Change it to regenerate, then run a
   staleness-only check that emits `::warning::` and continues (mirroring the render steps at lines
   203-216, which already do exactly this). This is a one-block change and it is the difference between
   "CI is red" and "main silently stops healing."
4. Record the 2026-10-26 expiry in `CHANGELOG.md` **and** as a dated calendar item, per the plan's own
   promise.

---

## R2 — HIGH: 11 concepts can ship with blank diagrams, fully green

**Scenario.** Phase 2 authors 11 concepts. The render step is skipped, fails, or is run on a host where
the Chromium lane is broken. The concepts merge. The Learn cards render with an **empty diagram well**.
Scope's success signal — *"a Prompt engineering category whose cards render diagrams"* — is not met, and
**every gate is green**.

**Trigger — a chain of four deliberate PR-time removals plus one silent fallback:**

- `scripts/generate-dashboards.py:1301-1305`:
  ```python
  def _inline_concept_svg(plugin_dir, rel):
      if not rel: return ""
      p = plugin_dir / rel
      return p.read_text(...).strip() if p.is_file() else ""     # <-- missing file → "" , no error
  ```
- `scripts/audit-gates.sh` (concept region): *"the 'clean tree must_pass' was intentionally removed. Concept
  SVGs are no longer sync-gated on PRs."*
- Same file: *"the 'concepts.py freshness (clean tree)' must_pass gate was RELOCATED to
  regenerate-artifacts.yml."*
- `generate-dashboards.py --check` (Gate 13) is likewise relocated off the PR path.
- The self-heal *would* render them post-merge — but `regenerate-artifacts.yml:205-208` swallows a render
  failure as `::warning::` and continues.

The **only** PR-time file-existence check on concept artwork is the `stepper SVGs (each declared step has a
committed .step-N.svg)` **must_pass** gate — and it fires only for concepts that *declare* `steps`.

**Two consequences G6 must carry:**
- **Plan A's "ship NO steppers in v1" is load-bearing for CI, not just for budget.** Plan B leaves a
  stepper open on `prompt-prefill-deprecated` (§2 row 4). A declared stepper with no committed
  `.step-N.svg` **hard-fails a PR-time must_pass gate that the self-heal cannot rescue.** Adopt A's ruling
  and say *why*.
- The overview SVG has the inverse problem: no gate at all.

**Mitigation.** Add a PR-time `must_pass` in the **exact shape of the existing stepper gate** (pure JSON +
`os.path.isfile`, CI-safe, no Chromium): *every concept in `concepts.json` carrying a non-empty `svg` has a
committed file at that path*, with a `must_fail` half that deletes one SVG. If that is judged out of scope,
the floor is a Phase-2 acceptance criterion: `git status` must show **11 added** `visuals/<id>.svg` files,
verified by name, not by "the render ran."

---

## R3 — HIGH: Gate 32 is one-directional and hyphen-blind; `/__host` gets no body parity under Plan A

Three independent defects in the gate both plans lean on. All verified.

**(a) The parity check is one-directional.** `scripts/check-dashboard-server-parity.py:166-169`:
```python
root = endpoints(root_path); plugin = endpoints(plugin_path)
expected = root - INTENTIONALLY_EXCLUDED
missing  = expected - plugin
```
An endpoint present **only in the plugin copy** is never reported. The `only_in_plugin` body-drift check
(`:248-251`) applies **only** to functions matching `_BODY_DIFF_PREFIXES = ("_read_", "_mimir_")` or the
five exact names in `_BODY_DIFF_NAMES`.

**(b) The endpoint regex truncates at a hyphen — proven:**
```
$ python3 -c "import re; print(re.compile(r'/__\w+').findall('/__host-context'))"
['/__host']
```
`\w` does not match `-`. Today the gate sees `/__knowledge` and `/__concern`, not
`/__knowledge-health` / `/__concern-stats` — confirmed by running `endpoints()` over both copies.
**Plan B §7 item 6 states the gate "auto-detects the new `/__host-context` token via its
`_ENDPOINT_RE = r"/__\w+"` regex". That is factually wrong** — it detects `/__host`. Consequence: a later
one-copy rename of the suffix (plugin serves `/__host-detail`) leaves the token set identical, the gate
green, and the consumer's dashboard 404-ing. Same class as the `/__saga` incident this gate exists to
prevent.

**(c) Plan A's chosen shape has no mechanical body parity at all.** Plan A §4c calls `/__host` "hand-
duplicated" and §10 mitigates with *"diff the two copies explicitly before commit."* The two copies are
**2,489 vs 2,398 lines and already differ** (`diff -q` → DIFFERENT) — a raw diff is not a usable pre-commit
check, and human discipline is the weakest available control when a naming convention buys mechanical
enforcement for free.

**Mitigation (binding, and it must be settled before a line is written because it fixes two names):**
1. Endpoint is **`/__host`** — no hyphen — so the gate's token equals the route.
2. The reader is a **module-level `def _read_host(...)`** in both copies. `_BODY_DIFF_PREFIXES` then
   enforces byte-identity (modulo the documented `REPO_ROOT`/`PROJECT_ROOT` variance) for free. This is
   Plan B's insight (`_read_host_context`) and it is strictly better than Plan A's; adopt it, minus the
   hyphen.
3. If the reader ever cannot carry the `_read_` prefix, add its exact name to `_BODY_DIFF_NAMES` in the
   same commit — the file's own CODE-SHAPE RULE (`:68-72`) already mandates this pattern.
4. Add one line to the gate: warn when any `/__*` string in either file contains a character outside
   `\w`, so the truncation trap is surfaced rather than rediscovered.

---

## R4 — HIGH: what actually leaks from `/__host` is a NAME enumeration in a shareable page

The plans treat "names only, never values" as the whole invariant. It is not, for this sink.

**Scenario.** The implementer builds the amendment's *"cannot determine — here's why"* state honestly, and
the natural way to explain *why* is to show what was found. The endpoint returns the presence of every
`CLAUDE_*` / `COPILOT_*` / auth-shaped name — or, following the repo's own precedent, iterates
`os.environ`. `scripts/capability-orientation.py:152` does exactly that today:
```python
extra = sorted(k for k in os.environ if k not in claimed and _SECRET_NAME_RE.match(k))
```
**That precedent's sink is the model's context.** `/__host`'s sink is a **browser page** — screenshotted,
pasted into Slack, and whose static twin (`index.html`) is **published to GitHub Pages**. Names alone
disclose the machine's credential inventory: `ANTHROPIC_API_KEY`, `AWS_SECRET_ACCESS_KEY`,
`RAVENCLAUDE_NOTIFY_WEBHOOK`, and any client-named token. That is a different exposure class than an
agent-context banner, and neither plan distinguishes them.

**Secondary leaks, all reachable from the plans as written:**
- **Paths, not booleans.** Plan B §2 card 3 wants *"the hooks registration path for the detected host"* and
  `.claude/skills/` *"(dir + count)"*. An absolute path discloses `$HOME` and the username. Gate 19's own
  runtime half exists precisely because a raw **path** in a deny event was a leak — the same rule applies.
- **Ordering.** Negligible on its own; noted and dropped.
- **Error text.** `send_error(403, "refused: cross-origin or non-local Origin/Host")` is clean today, but
  nothing stops a new handler echoing the query string. Keep the fixed-string convention.
- **Gate 19 does not and will not cover this.** It is scoped to `capability-orientation.sh` (audit-gates
  §Gate 19 fixture). Plan A §8.2 correctly says *"only if capability-orientation is touched; this plan does
  not"* — and then proposes a **one-time manual grep** as the control (§Phase 4 acceptance, "Leak test").
  A manual grep is not a control; it does not survive the next edit.

**Mitigation:**
1. The reader returns a **closed literal allow-list** of probed names — the ~5 detection signals and
   nothing else — emitting `[{name, present: bool}]`. **Never** iterate `os.environ`. Encode the
   allow-list as a module constant so the diff shows any widening.
2. The wired-state card emits **booleans keyed by a fixed relative-path list**; never an absolute path,
   never a directory listing, never a count derived from enumerating user files.
3. **Build the gate in Gate 19's exact bidirectional shape** — plant both a secret *value* and an
   unlisted secret-shaped *name* in the server's env; assert neither appears in the `/__host` JSON; then a
   `must_fail` half that removes the allow-list and proves the detector catches the leak. Plan B's
   proposed `check-host-context-render.mjs` (Gate ~152) is the right vehicle and Plan A has none — this is
   the single strongest argument for adopting B's gate.

---

## R5 — HIGH: the honest-unknown detector asserts a WRONG host

This is the finding the amendment's own binding words most directly forbid (*"a wrong verdict is worse than
no verdict"*), and **both plans ship it**.

**The symmetry both panels missed.** The amendment disqualified `COPILOT_DEBUG_NONCE` because it was
observed *inside a Claude Code session* — i.e. because env vars **propagate**. Neither plan tested the
inverse. Verified this session:
```
$ python3 -c "print([k for k in os.environ if 'CLAUDE' in k or 'COPILOT' in k])"
['CLAUDECODE','CLAUDE_CODE_CHILD_SESSION','CLAUDE_CODE_ENTRYPOINT','CLAUDE_CODE_EXECPATH',
 'CLAUDE_CODE_SESSION_ID','CLAUDE_CODE_SSE_PORT','CLAUDE_EFFORT','CLAUDE_PID','COPILOT_DEBUG_NONCE']

$ bash -c 'nohup python3 -c "import os; print(\"CLAUDECODE\" in os.environ)"'
True                      # survives detach; inherited by grandchildren
```
`CLAUDECODE` is exported, reaches grandchildren, and **survives `nohup`/detach**.

**Scenario (concrete, and this repo makes it likely, not exotic).** The dashboard server is deliberately
**long-lived and reuse-first**:
- `scripts/open-dashboard.sh` (v0.208.0 L lane) probes-then-**reuses** an existing server for the checkout.
- The in-flight `plugins/ravenclaude-core/hooks/dashboard-autostart.sh` — **present untracked in this very
  working tree** — states verbatim: *"NEVER DUPLICATES. It probes 127.0.0.1:<port> first; if a dashboard
  already answers there it does nothing at all."*

So: start `rc dashboard` inside a Claude Code session → end the session → open a **GitHub Copilot CLI**
session in the same repo → autostart finds a live dashboard and stands down → the user opens **Host &
context** → the reused server's environment still carries `CLAUDECODE=1` → the page renders **"You're in
Claude Code"** on a Copilot host. High confidence, no hedge, and — because the detector is deliberately
one-sided — **there is no Copilot signal that could contradict it.** One-sidedness makes this worse, not
safer.

Plan A's degradation (§4c) covers **served vs static** only; it does not cover *served by a dead session*.
Plan B is better here (§4's always-visible caveat, *"Detected once, when this dashboard server started"*)
but still renders the unqualified headline **"You're in Claude Code"**.

**Mitigation, in ascending order of correctness:**
1. **Floor (adopt regardless):** Plan B's always-visible inheritance caveat verbatim, plus the headline
   qualified with age — *"Claude Code (detected when this server started, N min ago)"*. Never an
   unqualified present-tense assertion.
2. **Right fix:** bind the verdict to **liveness**, not presence. Capture `CLAUDE_CODE_SESSION_ID` at
   server start (a **hash prefix**, never the value — R4) and compare it against the session id the
   *current* session writes under `.ravenclaude/runs/<session>/`. No live match ⇒ *"cannot determine — this
   server was started by a different session."* This is the same reachability question `_read_mimir`
   already answers (`cwd == project_root && status == "busy"` against `~/.claude/sessions/<pid>.json`) —
   reuse it, do not invent a second mechanism.
3. **The must-fail half neither plan has.** Both plans test the *forward* direction (`CLAUDECODE` unset +
   `COPILOT_DEBUG_NONCE` set ⇒ "cannot determine"). Add the **inverse**: `CLAUDECODE` set on a server whose
   session is gone ⇒ must **not** render an unqualified "Claude Code". That assertion is the amendment's
   binding constraint made mechanical; the forward one alone is not.

---

## R6 — MED-HIGH: false "cannot determine" on the launch paths this repo ships

**Scenario.** The owner's acceptance test — *"Control shows a Host & context page that correctly names this
host"* — fails on a genuine Claude Code session, because the *server* never saw the CLI's environment.

**Triggers, all first-party paths in this repo:**
- The **VS Code task** `ravenclaude setup` installs (`.vscode/tasks.json`, v0.44.0) — launched by VS Code,
  not by the CLI.
- The **Codespace `postStartCommand`** (`templates/codespace-copilot/`) — runs before any interactive
  session exists.
- `open-dashboard.sh`'s **probe-then-reuse**: a server started earlier from a plain terminal is reused by a
  later Claude Code session → no `CLAUDECODE` → "cannot determine".

The page is then honest but useless on the most common launch routes, which is exactly the outcome that
makes an owner say "it doesn't work."

**Mitigation.** Before rendering "cannot determine", probe a **second, session-scoped** source: the
freshest `.ravenclaude/runs/<id>/` for this project, or the `~/.claude/sessions/<pid>.json` match
`_read_mimir` already implements. Frame the state as *"cannot determine from this server's environment"*
and name the launch paths that do/don't inherit — that turns a dead end into the teaching the page exists
for.

---

## R7 — MED-HIGH: the `+7` is right only for a shape no other panel in the repo uses

**I confirmed the tiebreak's number empirically**, then found the way it breaks.

Simulated the exact markup into copies of both surfaces and measured with the real gate:
```
inserted: <a class="ds-sub ds-xref" href="#/prompt-builder">        (relink)
          <a class="ds-sub" href="#/host-context" data-tab=...>     (sidebar)
          <button class="tab-btn" ... data-tab="host-context">      (tab-bar)
          <section id="panel-host-context"><div id="hc-root"></div>
            <noscript><p>…</p></noscript></section>
$ python3 scripts/check-dom-budget.py --count <simulated dashboard.html> -> 6121
$ python3 scripts/check-dom-budget.py --count <simulated index.html>     -> 7007
```
**T1's `6,114 → 6,121` / `7,000 → 7,007` is exactly right — for that markup.**

**How it goes wrong.** That 4-element panel body is unique to `panel-prompt-builder`. Verified against the
shipped `dashboard.html`:
```html
<section class="tab-panel" id="panel-prompt-builder" ...>
<div id="pb-root" class="pb-root"></div>
<noscript><p class="pb-noscript">…</p></noscript>
</section>
```
No heading. No intro paragraph. Every other panel authored in the house style opens with them — e.g.
`panel-plugin-vars`: `<h2 class="pp-title">` + `<p class="pp-sub">`. An implementer writing the Host &
context page *in the house style* adds those two → **6,123 / 7,009** → Gate 132 **fails after the owner
already approved 6,121**. Two more traps in the same neighbourhood:
- `<noscript>` contents **are counted** (`html.parser` puts only `script`/`style` in CDATA — the gate's own
  docstring), so a two-paragraph noscript is another +1.
- **Plan B's content spec is written in the wrong shape.** §2 lists *"Four card hosts"*; §6 estimates ~+38
  from the `panel-mimir` analog. T1 ruled the JS-built pattern, but B's *content* section was never
  rewritten to match. If G6 folds B's card list in verbatim, the approved number is wrong by ~+30.
- The new row must be **appended last**: `budget_for()` is `RATCHET[surface][-1][1]` — a row inserted mid-
  table silently puts a different budget in force.

**Mitigation.** Write the shape into the plan as a **byte-level contract, not a description**: the panel's
static markup is exactly `section > div#hc-root` + `noscript > p` — no `<h2>`, no `<p class="…-sub">`, no
card hosts, exactly one `<p>` in the noscript; the title, precedence table, detector and wired-state cards
are all JS-built into `#hc-root` (the `pbEl` pattern). Put the sentence *"any static element beyond these
four re-opens the owner gate"* **inside the ratchet row's own text**, where the next author will read it.

---

## R8 — MED-HIGH: merge skew makes a pre-approved zero-slack number wrong

**Scenario.** The owner approves `7,000 → 7,007`. Before this PR merges, an unrelated plugin-add PR lands.
`index.html` regenerates; Gate 132 measures 7,008; CI fails on a number the owner already signed; a second
owner round-trip is needed for a delta this change did not cause.

**Trigger — documented twice in the ratchet's own history:**
- `reland-11-plugins` row: *"Each plugin adds exactly **ONE** counted element to the portal Marketplace
  list."*
- PR-C row (both tables): *"the +1 is MARKETPLACE DATA growth … landed post-PR-B via **merge-skew**."*

Budget is at **exact zero slack** by design, so there is no absorption. Plan A compounds it by asking for
sign-off *before* any markup exists (§Phase 1); T4 already reversed that ordering — good — but neither plan
protects the window between the ask and the merge.

**Mitigation.** Keep T4's ordering, and add one hard step to the DoD: **rebase → run both generators →
`check-dom-budget.py --count` → reconcile the ratchet row → push**, as one uninterrupted sequence
immediately before merge. Record the owner approval as *"+7 attributable to this change"* rather than as
the literal `6121/7007`, so a data-driven ±1 is a reconciliation, not a re-approval. (The monotonic
assertion itself fails loudly, so a botched lockstep lift is noisy — that part is fine.)

---

## R9 — MEDIUM: Plan A's Gate-144 hardening holds, but its rationale is false and it cancels B's fix

**The mitigation works — verified.** `scripts/check-prompt-builder-render.mjs:280`:
```js
const i = src.indexOf('<a class="ds-sub" href="#/prompt-builder"');
```
This is an **exact-prefix** match. A secondary link written `<a class="ds-sub ds-xref" href="#/prompt-builder">`
cannot match it (the literal requires `ds-sub"` immediately followed by ` href=`), so `homeDestination()`
can only ever resolve the Control link — **including under a `ds-group` reorder**. Plan A's §Phase 3
hardening is sound. The portal half is also safe: `navBranch(html,"control")` slices from
`if (id === "control")` (`_index_dashboard_template.py:1043`) to the next `if (id === "` (`:1066`), so a
link added to the `catalog` branch (`:1096`) is outside the slice.

**What is false is the UX claim.** `generate-dashboards.py:9580-9584`:
```js
function syncSidebar(tab) {
  document.querySelectorAll(".ds-sub").forEach(a => a.classList.remove("active"));
  const el = document.querySelector('.ds-sub[data-tab="' + tab + '"]');   // FIRST match only
  if (el) el.classList.add("active");
}
```
With `data-tab` **omitted** on the secondary link (Plan A §Phase 3), clicking the Learn & Help entry routes
correctly but the highlight **jumps to the Control link** — the user clicks under "Learn & Help" and the
sidebar lights up "Control". Plan A claims omitting `data-tab` *"is honest about what it is and avoids a
dead-looking nav item."* It produces a **worse** artifact than the one it avoids.

**And the two plans' mitigations do not compose.** Plan B §5.3 correctly identifies the `querySelector`
singular bug and proposes `querySelectorAll(...).forEach(el => el.classList.add("active"))`. If G6 adopts
A's omit-`data-tab`, that selector matches exactly one node and **B's fix becomes a no-op** — the plan
ships with the highlight-jump defect and a fix that provably does nothing.

**Mitigation.** Take **all three**, they are orthogonal: keep `ds-xref` (it is what makes Gate 144
order-independent), **keep `data-tab="prompt-builder"`** on the secondary link, and take B's
`querySelectorAll` change. Then both entries light. Extend Gate 144's must-fail proof accordingly: after
the group reorder, assert `homeDestination` still derives `control` **and**
`querySelectorAll('.ds-sub[data-tab="prompt-builder"]').length === 2`.

---

## R10 — MEDIUM: the relink alone trips `check-committed-routes` on `href_count`

**Scenario.** Phase 3 lands the relink. No new route is added. `check-committed-routes.mjs` fails anyway,
and the message ("href_count 24 != fixture 23") reads like a laundering attempt rather than an expected
delta.

**Trigger.** `scripts/check-committed-routes.mjs:261-262` asserts `href_count` **exactly**, not merely the
distinct-route set:
```js
live.href_count === fx.href_count,
`${kind}: href_count ${live.href_count} != fixture ${fx.href_count}`
```
The committed fixture has `dashboard.href_count: 23 / distinct_static: 16`. A second
`href="#/prompt-builder"` makes it 24 while `distinct_static` stays 16.

Plan A lists the gate but frames it as *new-route* enumeration (§8.1 row 6); the relink is not a new route
and trips it anyway. Plan B never mentions the gate at all (already noted in `gap-delta.md` §1.6 — this
finding sharpens *why*: it is not only the new route).

**Mitigation.** The DoD must run `node scripts/check-committed-routes.mjs --emit` **after the relink** and
again **after the new route**, and the PR body must state the expected `href_count` deltas per surface
(+1 relink, +1 host-context, +1 more if a portal `navChildren` catalog link is added) so a reviewer can
distinguish a legitimate delta from a laundered one — that is the whole point of the PB-2 floor.

---

## R11 — MEDIUM: `main`'s tree is dirty with an entire unrelated in-flight feature

**Trigger — measured:**
```
$ git rev-parse --abbrev-ref HEAD  ->  main
$ git status --porcelain
 M .claude-plugin/marketplace.json      M plugins/ravenclaude-core/CLAUDE.md
 M .claude/settings.json                M plugins/ravenclaude-core/dashboard-assets/shared-tokens.css
 M .ravenclaude/comfort-posture.yaml    M plugins/ravenclaude-core/dashboard.html
 M feedback-report.html                 M plugins/ravenclaude-core/hooks/hooks.json
 M index.html                           M scripts/_index_dashboard_template.py
 M plugins/.../plugin.json              M scripts/audit-gates.sh
 M plugins/.../CHANGELOG.md             M scripts/check-prompt-builder-render.mjs
 … (23 modified total)                  M scripts/generate-dashboards.py
                                        M scripts/render-concepts.py
                                        M tests/fixtures/routes/committed-routes.json
?? plugins/ravenclaude-core/hooks/dashboard-autostart.sh
?? plugins/ravenclaude-core/hooks/tests/test-gate151-dashboard-autostart.sh
```
This is the v0.216.0 Gate-151 autostart feature plus today's Gate-144 rewrite, **uncommitted on `main`**.

**Consequences for these plans:**
- Plan A's Phase-0 acceptance — *"`git status` shows changes confined to `scripts/render-concepts.py`"* —
  **can never pass**.
- **T5 is overstated.** `tiebreaks.md` says `render-concepts.py` is "DONE … carry it as a completed
  prerequisite." It is **uncommitted** (`git log -- scripts/render-concepts.py` → last commit is
  `8706301a feat(learn): nine concepts…`). A fresh clone, CI, or another worktree does **not** have the
  fix. It is a completed *edit*, not a completed *prerequisite*.
- Any `git checkout -- <path>` style revert during the build (the pattern the self-heal itself uses)
  risks destroying the autostart work.
- The plan's branch will carry unrelated changes into its PR unless the tree is cleaned first.

**Mitigation.** **Phase −1**: land (or stash-to-a-branch) the in-flight Gate-151 + Gate-144 +
`render-concepts.py` work on its own PR *first*. Then `/forge`'s worktree provisioning (v0.210.0,
`forge/<slug>`) gives this run a genuinely clean tree. I verified `HEAD` and the working tree **both**
measure 6,114 / 7,000, so the DOM baseline happens to be safe — but that is luck, not design, and it will
not hold once the autostart work is regenerated.

---

## R12 — MEDIUM: a CSS/token edit stales `feedback-report.html`, whose PR gate IS live

**Scenario.** The Host & context page needs styling. The implementer adds `.hc-*` rules to
`plugins/ravenclaude-core/dashboard-assets/shared-tokens.css` (the natural home). `feedback-report.html`
goes stale. `audit-gates.sh:4313-4314` runs `feedback-report freshness (clean tree)` as **must_pass** and
the PR fails on a file the change never mentions.

**Trigger — the asymmetry, confirmed:**
```
$ grep -l shared-tokens scripts/*.py
scripts/_index_dashboard_template.py   scripts/generate-bi-report.py
scripts/generate-feedback-report.py    scripts/generate-dashboards.py
scripts/generate-index-dashboard.py
```
**Five** generators, not four — `tiebreaks.md` T3's note that the union is incomplete in both plans is
confirmed, and `generate-bi-report.py` is the fifth neither plan lists either.

The asymmetry is deliberate and documented in `regenerate-artifacts.yml:32-44`:
- `concepts.json` + `report.html` — self-heal owns them, **PR gates removed**.
- `feedback-report.html` + `docs/concepts.md` — self-healed **and** their **PR-time gates KEPT**.

So the self-heal does not save your PR for these two. This already fired this session (`feedback-report.html`
is modified in the working tree right now).

**Mitigation.** Two layers:
1. **Prefer a panel-scoped style block inside `generate-dashboards.py`** over a `shared-tokens.css` edit.
   That confines the blast radius to the two dashboards and avoids the trap entirely.
2. If a shared-token edit is unavoidable, derive the regen chain **mechanically**, not from prose:
   `for g in $(grep -l shared-tokens scripts/*.py); do python3 "$g"; done` — which picks up
   `generate-feedback-report.py` and `generate-bi-report.py` that neither plan names.

---

## R13 — LOW-MED: `do_HEAD`'s hardcoded list, and an un-gated security rule

**(a)** `scripts/serve-dashboards.py:1566` enumerates every `/__*` prefix for HEAD in one literal
condition. `/__host` not added there falls through to `super().do_HEAD()` → **404 on HEAD while GET returns
200**. Cosmetic, but the `/__csrf` served-mode probe is a HEAD request — an inconsistent HEAD surface is
exactly the kind of thing a future probe trips over. Both copies.

**(b) The more important half.** `serve-dashboards.py:1575-1577`:
```python
# NOTE: static GETs are intentionally ungated. Any NEW data-returning GET
# endpoint added here MUST call self._local_request_ok() first (as
# _handle_read does) — do not let it ride the static path.
```
**Nothing enforces this.** `grep -n '_local_request_ok' scripts/audit-gates.sh scripts/check-*.py` returns
one hit, and it is a *comment* inside Gate 142's block. A `/__host` handler shipped without the guard is
CSRF-reachable from any page the user visits, and every gate stays green.

**Mitigation.** Add `/__host` to the `do_HEAD` list in both copies. More valuably: extend **Gate 142**
(which already machine-checks the security floor against a live server) to iterate **every** `/__*` route
the server dispatches and assert an evil-`Origin` request returns 403. That converts the comment into a
gate and covers every future endpoint, not just this one — a one-loop change with real teeth.

---

## R14 — LOW: `#/host-context` is missing from the router-execution FLOOR

`scripts/check-router-execution.mjs:81` — the FLOOR contains `{control: #/settings, #/pipeline,
#/web-access}`, i.e. **every other Control destination**. Both plans name `required_routes` in
`tests/fixtures/routes/committed-routes.json`; that is a *different* fixture. Omitting the FLOOR means the
new page's **click-reachability and highlight are never executed**, only text-parsed — the exact gap
(`G2/G3`) this gate was written to close.

**Mitigation.** Add `{ section: "control", route: "#/host-context" }` to `FLOOR`; `--selftest` then proves
the mutation makes it red, for free.

---

## R15 — LOW: `_discover_chrome()` picks 151 against a mermaid-cli that expects 148

**Measured:**
```
$ ls ~/.cache/puppeteer/*/*
chrome/mac_arm-148.0.7778.97 (353M)   chrome/mac_arm-151.0.7922.47 (355M)
chrome-headless-shell/mac_arm-148… (1.5M — truncated)   chrome-headless-shell/mac_arm-151… (195M)

$ _discover_chrome()  ->  .../chrome/mac_arm-151.0.7922.47/…/Google Chrome for Testing
$ MMDC_VERSION        ->  11.15.0          # its puppeteer-core resolves 148.0.7778.97
```
The sort is `key=lambda p: p.name, reverse=True` — newest-first by **string**, so 151 wins. And
`_chrome_hint()` tells the user to run `npx --yes puppeteer browsers install chrome` — **unpinned**, which
installs latest and then wins the sort. The function's own docstring warns: *"Installing a newer Chrome CAN
therefore change the chosen engine."*

**I tried to prove the consequence and failed.** Rendered an identical 4-node `flowchart LR` under both:
```
148 exit=0   out148.svg 13,596 bytes
151 exit=0   out151.svg 13,596 bytes
cmp -> BYTE-IDENTICAL
```
So the "re-render churns all 186 committed SVGs" risk that Plan A §10 flags as **Medium** is **not
reproducible** for a representative flowchart on this host. I am reporting the finding as **LOW**, with the
falsification stated, rather than padding it to Medium.

The residual concern is CI, and it is real but conditional: `regenerate-artifacts.yml:138-145` documents
that pointing mermaid-cli at a non-version-matched Chrome *"launches but then fails inside mermaid.js at
render time (renderMermaid → fromText, a CDP/version mismatch — observed 2026-07-27)"*, and the self-heal
**swallows a render failure as `::warning::`** (`:205-208`). If attempt 1 ever regresses on the runner,
attempt 2's repair path produces a *silent* no-heal.

**Mitigation.** Pin the hint (`browsers install chrome@148.0.7778.97`), and prefer an exact match to the
version mermaid-cli expects over newest-first when one is present in the cache. Both are one-liners.

---

## §9 — Attacked and NOT broken (do not re-open)

Recorded so G6 spends no budget here, and so my falsified hypotheses are visible.

- **"Concept cards will consume DOM budget."** Falsified independently three times — both panels and my own
  measurement. `panel-learn` is islanded into a `<script type="application/json">`; `html.parser` treats it
  as CDATA. HEAD and working tree both measure 6,114 / 7,000. **T1 stands; concept authoring is budget-free.**
- **"Gate 19 will fail because `/__host` touches env."** It cannot — Gate 19's fixture drives
  `hooks/capability-orientation.sh` only. Plan A §8.2 states this correctly. The *problem* is the absence
  of coverage (R4), not a failing gate. No finding.
- **"Plan A's `ds-xref` mitigation doesn't actually hold for `homeDestination`."** It holds — the exact-
  prefix `indexOf` cannot match `class="ds-sub ds-xref"`. Verified against the real generator markup,
  including under a group reorder. The defect is elsewhere (R9).
- **"The `+7` estimate is wrong."** It is right — simulated and measured at 6,121 / 7,007. The risk is
  drift *away* from the shape that produces it (R7), not the arithmetic.
- **"The monotonic ratchet lift will silently pass a bad value."** It fails loudly
  (`check-dom-budget.py:671-674` prints `FAIL: ratchet table is not monotonically non-increasing`). The only
  real hazard is inserting the new row anywhere but last (`budget_for` reads `[-1]`) — folded into R7 as a
  one-line note rather than inflated into its own finding.
- **"Chrome 148 vs 151 will churn every committed SVG."** Attempted; byte-identical output. Downgraded into
  R15 with the falsification stated rather than asserted as a Medium risk.
