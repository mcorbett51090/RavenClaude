# Dashboard UX build plan — cold gap analysis (2026-05-30)

**Reviewer role:** senior engineer + security reviewer · **Mode:** adversarial cold review (I did not write the plan)
**Plan under review:** [`dashboard-ux-build-plan.md`](./dashboard-ux-build-plan.md)
**Inputs reviewed:** [`ux-dashboard-analysis.md`](./ux-dashboard-analysis.md), [`ux-handoff-repo-inventory.md`](./ux-handoff-repo-inventory.md)
**Code verified this session:** `scripts/generate-dashboards.py`, `scripts/serve-dashboards.py`, `plugins/ravenclaude-core/scripts/serve-dashboards.py`, `scripts/render-concepts.py`, `scripts/concepts.py`, `scripts/check-dashboard-server-parity.py`, `scripts/check-dashboard-roundtrip.mjs`, `scripts/audit-gates.sh`, `scripts/open-dashboard.sh`.

---

## 1. Verdict

**SOUND-WITH-FIXES** — but two of the four P0 features in the plan rest on **factually wrong premises about the code** and must be re-scoped before any build:

1. The plan's core mechanism for "Commands execute on click" (`/__run` widened, "lands in BOTH server copies") is **contradicted by Gate 32**, which exists specifically to keep `/__run` **out** of the bundled/consumer server. The consumer dashboard (what `/dashboard` actually launches) has **no `/__run` at all and cannot get one** without rewriting the parity gate's documented exclusion. Class-A "Run" buttons are a **root-dev-server-only** feature, full stop.
2. The plan's "reuse `render-concepts.py` to pre-render ~32 decision-tree SVGs" treats `render-concepts.py` as a general Mermaid renderer. It is **not** — it is hard-bound to the `concepts.py` concept-file schema and iterates `load_concepts()` only. There is no general "render arbitrary Mermaid block" entry point. This phase is **net-new infrastructure**, not a reuse, and is too heavy for the same PR.

The Overview tab (Phase 1) and the consolidation work (Phase 4) are sound and low-risk. The plan's *security instinct* is correct (allow-list, fixed argv, no shell, CSRF, 127.0.0.1) — but it under-states how little of the "execute" story survives the parity constraint, and over-states the reuse available for Mermaid. Fix the framing and re-sequence per §4 and it's safe to execute.

---

## 2. P0 gaps (must fix before building)

### P0-A — `/__run` widening into "BOTH copies" is impossible by design; the consumer dashboard can never run Class-A commands

**The gap.** The plan (line 11, 21) asserts *"Any `/__run` change lands in BOTH"* server copies. That is false and, if attempted, will **fail CI**.

**Evidence (verified):**
- `scripts/check-dashboard-server-parity.py:44` — `INTENTIONALLY_EXCLUDED = {"/__run"}`. The gate asserts every root `/__` endpoint **except `/__run`** exists in the plugin copy. `/__run` is the *one* documented allowed divergence.
- The plugin server (`plugins/ravenclaude-core/scripts/serve-dashboards.py`) has **no `/__run`**: no `_handle_run`, no `ALLOWED_ACTIONS`, and its `do_HEAD` (lines 284–297) does **not** answer `HEAD /__run` (it lists `/__save`, `/__classify`, `/__read`, `/__saga`, `/__runs` only). Its module docstring (lines 15–17) states the omission is intentional: *"No `/__run` endpoint … intentionally absent here."*
- `CLAUDE.md` (plugin) confirms: the bundled server is *"`/__save` + `/__read` + `/__classify` only, no `/__run`, binds 127.0.0.1."*
- `scripts/open-dashboard.sh:19` launches **`$ROOT/plugins/ravenclaude-core/scripts/serve-dashboards.py`** — the *plugin* (no-`/__run`) copy. So even the marketplace's own one-command launcher does not get `/__run`. `/__run` lives **only** in `scripts/serve-dashboards.py` (the root dev server), and the maintainer reaches it by running that file directly.

**Why it matters.** The headline ask is "commands clickable + execute." Under the real architecture, Class-A "▶ Run" buttons work **only** when the page is served by the *root dev server* — i.e. for the maintainer, in this repo. Every consumer who runs `/dashboard` (or `bash scripts/open-dashboard.sh`) gets the plugin server, where `HEAD /__run` 404s and every Run button stays permanently disabled. The plan does not acknowledge this; it would ship "Run" buttons that are dead for 100% of consumers and call it done.

**Concrete fix.**
1. **Drop "lands in BOTH" entirely.** It is wrong. State explicitly that `/__run` (and any new action) is **root-dev-server-only**, and that the consumer dashboard renders Class-A commands as Copy-only (Class B treatment) because its server has no `/__run` by design.
2. The Class-A Run-button JS must degrade to **disabled + "served by the dev server only"** when `HEAD /__run` 404s — which it already does for the Install tab (`scripts/generate-dashboards.py:5559`, `data-run-action` buttons start `disabled` and enable on the probe). Reusing that mechanic is correct **and self-degrades on the consumer server** — so the *mechanic* is safe; the **plan's claim that consumers get execution is the bug.**
3. If the maintainer genuinely wants consumers to click-run install/update, that is a **separate, deliberate decision** to add `/__run` to the plugin server and **rewrite `INTENTIONALLY_EXCLUDED`** — a real security-surface expansion on the *consumer-facing* server, out of scope for a UX PR and not what the plan describes.

### P0-B — first cut should ship ZERO new `/__run` actions (security delta = 0)

**The gap.** Open question #2 asks exactly this; the plan's body (line 21, Phase 2) nonetheless bakes in two **new** actions, `open-dashboard` and `set-posture`. Both are questionable:

- **`open-dashboard` → `bash scripts/open-dashboard.sh`.** The script **exists** (verified) and takes no caller args in the proposed argv, so it is fixed-argv/no-shell-interpolation. **But it is not non-destructive in the way "status" is:** it `pkill -f "serve-dashboards.py"` (line 25 — kills the very server handling the request, so the `/__run` response may never return), spawns a **detached background** server via `nohup … & disown` (lines 29–30, survives the request), and opens a browser. Running "launch a new detached server" *from inside the running server* via an HTTP POST is a footgun (orphaned processes, port races, the handler killing its own parent). Allow-listing it buys little — the user already has a dashboard open — and adds a process-spawning action to the audited surface.
- **`set-posture` (apply).** The apply path is **already reachable**: `/__save` to `POSTURE_TARGET` auto-runs `_apply_posture()` (`scripts/serve-dashboards.py:576–610`), which runs `apply-comfort-posture.py --project-root <root>`, fixed argv. Exposing a **standalone** `set-posture` button that re-applies *without a save* is a new entry point to an existing capability — low marginal value, and it muddies "apply == consequence of save."

**Why it matters.** Every entry on `ALLOWED_ACTIONS` is attack surface that a security reviewer must re-audit forever. The plan's own load-bearing constraint is "preserve the security envelope / security delta." Two new actions is a non-zero delta for marginal UX gain, and `open-dashboard`'s process semantics are actively worse than the read-only `status` precedent.

**Concrete fix (answers open question #2 = YES, defer):** **Ship PR-1 with NO new actions.** Wire the Commands tab over the **existing** `install`/`update`/`status` only (these are the only commands whose effect is genuinely a fixed shell action already trusted), and treat all four *slash* commands (`/dashboard`, `/set-posture`, `/init-agent-ready`, `/wrap`) as **Class B** (Copy + "runs inside Claude Code" pill + exact `/name`). Security delta = 0. Defer any `/__run` widening to a separate, security-reviewed PR with its own gate (P0-D) — **if** it is wanted at all after P0-A reframes who can even use it.

### P0-C — Mermaid pre-render is net-new infra, not a `render-concepts.py` reuse; too heavy for the UX PR

**The gap.** The plan (line 26) says *"extend/reuse `render-concepts.py`'s normalize pipeline."* `render-concepts.py` does **not** generalize to arbitrary Mermaid:

**Evidence (verified):**
- `scripts/render-concepts.py:35` imports `concepts as concepts_mod`; `main()` (line 173) and `_check()` (line 135) iterate **`concepts_mod.load_concepts(root)`** only. There is no "render this Mermaid string from a decision-tree doc" path exposed.
- `concepts.py:189 load_concepts()` parses **concept files** with a strict frontmatter schema (`id`/`kind`/`summary`/`sources`/`diagram`/`diagram_mini`, validated, `ConceptError` on any miss). Decision-tree docs (`plugins/*/knowledge/**/*.md`, `*/skills/**/*.md`) are **not** concept files and carry none of that schema. `_decision_trees_inventory()` (`generate-dashboards.py:764`) records only `{owner, title, when, path}` — it **does not even extract the Mermaid block**.
- The source-hash manifest (`.render-manifest.json`), the `--check` gate (Gate 23, `audit-gates.sh:1179`), and the `_source_hash()` keying are all **per-concept**. None of it covers decision-tree SVGs.
- **Scale is also off.** The plan says "~32 decision trees → 32+ SVGs." Verified: **38** `## Decision Tree:` sections across the plugins, and the docs containing them hold **~75 `` ```mermaid `` fences** (many docs have multiple diagrams; some trees have none). So it is potentially ~75 SVGs to render+commit, not 32 — and the count grows with the in-flight power-platform/salesforce build-out the plan itself notes.

**What IS reusable:** the *pure* helpers `_normalize()`, `_theme_style()`, `_render_one()` (string ops + one mmdc call). The **driver, inventory, manifest, and `--check` gate are all net-new.** Calling this a "reuse" hides a meaningful chunk of work and a new CI gate (a `--check` that re-derives decision-tree diagram hashes, plus mermaid-cli availability — `render-concepts.py` already documents that CI never needs Chromium *because* the `--check` reads a committed manifest; a new tree-SVG gate must replicate that discipline or it will demand a browser in CI).

**Why it matters.** Bundling ~75 build-time SVGs + a new inventory + a new manifest + a new audit-gate fixture-pair into the same PR as the Overview tab and the Commands rework makes the PR large, slow to review, and high-risk for the freshness gates. It is the single most likely phase to blow the PR's CI budget.

**Concrete fix (answers open question #1):** **Defer SVG pre-render.** Ship Guidance interactivity in PR-2+ as **raw Mermaid inside `<details>` rendered to SVG via the same offline build-time path the concepts use — but only after a dedicated inventory + manifest + `--check` gate is built and audited** (its own PR). For PR-1, the cheap, static-safe, zero-new-dependency win is **best-practice preview-on-click** (first heading + first paragraph / `**Status:**`, already parsed by `_best_practices_inventory()` at `generate-dashboards.py:791`) and a **text/source preview** of decision-tree docs in a `<details>` — no mermaid-cli, no manifest, no new gate. SVG rendering is a follow-on once the gate exists. Do **not** embed a client-side Mermaid CDN/JS lib — the plan is correct that the dashboard ships none and that constraint must hold (`render-concepts.py:9–12` is explicit about why).

### P0-D — if any action is added, the "fixed-argv integrity" gate must land in the SAME PR (answers open question #4 = YES)

**The gap.** The plan (line 23) makes the integrity gate *"if feasible."* If P0-B is honored (no new actions), this is moot for PR-1. But the moment a new `ALLOWED_ACTIONS` entry is added, an assertion that **no action maps to an interpolated/shell argv** must be a hard gate in the same PR — `audit-gates.sh` is the meta-test and the repo's own rule (AGENTS.md) is "new gates add a fixture-pair in the same PR."

**Concrete fix.** When/if widening: add a Gate (alongside 32/35) that imports the root server, asserts each `ALLOWED_ACTIONS` member resolves to an argv whose elements are **literals + the validated action name + the fixed `--project <root>`** and contains **no shell metacharacters / no f-string interpolation of body fields** — with a must-fail fixture (an action wired to `f"... {body['x']}"`) and a must-pass (the real table). Mirror `_handle_run`'s structure: `argv = ["bash", str(SCRIPT), action]` (`serve-dashboards.py:635`) is the only safe shape.

### P0-E — Gate 35 round-trip is brittle to symbol renames; Overview must not touch the serializer symbols

**The gap.** Gate 35 (`check-dashboard-roundtrip.mjs`) **extracts named symbols by string** from `dashboard.html`: `const CR_DEFAULT`, `TIER_DEFAULT`, `RUNAWAY_DEFAULT`, `DOD_DEFAULT`, `CR_SEATS`, `TIER_SEATS`, `TIERS`, `DECISION_REVIEW_VALUES`, `DECISION_REVIEW_DEFAULT`, `function freshTiers()`, `quoteYamlKey(`, `applyGuardrailConfig(`, `emitYaml()` (lines 47–62). If any are renamed/removed, `extract()` **throws** and the gate fails hard.

**Why it matters.** The Overview tab and Commands rework *shouldn't* touch these — but the round-trip checker also hard-fails if a new `<script>` block becomes the **largest** one (it picks `app = the single longest <script>`, line 23). If a future phase inlines a large block of Overview/Commands JS that exceeds the posture-app script, the extractor reads the **wrong** script and every `extract()` throws.

**Concrete fix.** Keep all new tab JS **inside the existing app `<script>`** (so it stays the largest by construction), or verify after each phase that `node scripts/check-dashboard-roundtrip.mjs` still passes (it's already in the per-phase checklist, line 37 — good; just call out *why* it can break from a UI-only change). Adding an Overview tab itself adds **no posture keys** → emit/hydrate unaffected (plan line 18 is correct on this point).

### P0-F — freshness gate (Gate 13) + default-tab change interaction

**The gap (minor but real).** Gate 13 (`audit-gates.sh:309`) runs `generate-dashboards.py --check` — the committed `dashboard.html` must be byte-identical to a fresh generation. Moving `active`/`aria-selected="true"` from Settings (`generate-dashboards.py:6743`, `:6756`) onto a new Overview panel changes the template, so **the committed `dashboard.html` MUST be regenerated and committed in the same change** or Gate 13 fails. The plan says "regenerate dashboard.html" (line 18, 37) — adequate, but flag that *both* the tab-bar button block (`:6743`) and the panel block (`:6756`) plus the `render_dashboard()` slot + `_PAGE_TEMPLATE` (`generate-dashboards.py:116/127/6726`) must move in lockstep, or the active tab and rendered panel disagree.

---

## 3. P1 gaps (should fix)

- **Tooltip a11y.** The plan mandates `title=` + `aria-describedby` + an always-visible "what this runs" line (good — not hover-only). Verify: `title=` is **not** reliably keyboard/touch accessible and screen-reader support is uneven; the *always-visible* literal-argv line is the real a11y guarantee, the `title=`/`aria-describedby` is secondary. Make the always-visible line the primary, normatively required element; treat `title=` as progressive enhancement. Also ensure `aria-describedby` points at a real element id (the always-visible line), not a tooltip that only exists on hover.
- **Static-host degradation of Run buttons.** Already handled by the `HEAD /__run` probe pattern (`generate-dashboards.py:5559`) — but per P0-A, on the **consumer/plugin server** this means Run is *always* disabled, not just on `file://`. The disabled-state help text must say "available only on the dev server," not "run `serve-dashboards.py`" (which the consumer *is* already running, just the no-`/__run` copy). Misleading copy is a real defect here.
- **Default-tab change risk (open question #3).** Low risk, agreed — but the *tab-bar `aria-selected`* and the *panel `active` class* and any **localStorage last-tab restore** logic must agree. If the app restores the last-viewed tab from localStorage, a first-run user gets Overview but a returning user keeps Settings — verify whether that's desired (probably yes) and that no JS hard-codes `settings` as the fallback.
- **Naming.** "Preview a command's review" (relabel of "Test a command") is good and removes the Commands/Test-a-command collision. Keep "Commands" as the tab label; do not rename to "Run commands" (over-promises given most are Class B / consumer-disabled).

---

## 4. Recommended phase re-ordering / de-scoping

**PR-1 (ship first — lowest risk, highest value, security delta = 0):**
1. **Overview tab** (Phase 1) — purely additive, generator-discovered, no server change, no new gate. Regenerate `dashboard.html`; Gate 13 + Gate 35 pass unchanged. This is the single highest first-run-value, lowest-risk item.
2. **Commands tab rework over the EXISTING 3 actions only** — Class A = `install`/`update`/`status` (reuse the Install-tab `data-run-action` + `HEAD /__run` mechanic, which self-degrades to disabled on the consumer server); Class B = all four slash commands (Copy + "runs inside Claude Code" pill + exact `/name`). Mandatory always-visible "what this runs" line + a11y. **No `/__run` widening. No new gate.** Honest disabled-state copy per P1.
3. **Guidance: best-practice preview-on-click + decision-tree text/source preview** in `<details>` (build-time, static-safe, no mermaid-cli, no manifest).
4. **P1 consolidation** (Phase 4) — headers, relabels, cross-links. Freshness only.

**PR-2 (separate security review):** `/__run` widening — *only if* P0-A reframing shows it's still wanted, with P0-D's integrity gate in the same PR, and an explicit decision on whether it touches the **consumer** server (a real surface expansion) or stays root-dev-only.

**PR-3 (separate infra PR):** decision-tree Mermaid → SVG pre-render — net-new inventory + `.render-manifest`-style manifest + `--check` gate + audit-gates fixture pair, mirroring `render-concepts.py`'s CI-no-Chromium discipline. ~75 SVGs committed.

One minor version bump per PR (the plan's "one bump for the whole effort" is wrong if this is 3 PRs — bump per user-visible PR per AGENTS.md).

---

## 5. Answers to the plan's 5 open questions

1. **Mermaid pre-render scale — right call?** **Not in this PR, and "reuse" is a mischaracterization.** Pre-render to SVG is the *right end state* (dependency/CDN-free, offline, byte-deterministic — `render-concepts.py:9–12`), but it is **net-new infra** (new inventory, manifest, `--check` gate, ~75 SVGs — not 32), not a `render-concepts.py` reuse. **Defer to its own PR.** For now ship text/source preview + best-practice preview (zero new deps). Do **not** add a client-side Mermaid lib.
2. **`/__run` widening surface — two new actions or none?** **None.** Ship Commands-as-buttons over the existing `install`/`update`/`status` only; slash commands → Class B. Security delta = 0. `open-dashboard` is process-spawning (kills the serving process, detaches a new one) and worse than the read-only `status` precedent; `set-posture`-apply already rides `/__save`. Defer any widening to a security-reviewed PR — and note (P0-A) it would only ever help the maintainer's root server unless you also expand the *consumer* server's surface.
3. **Overview-as-default — muscle-memory risk?** **Low; proceed.** Make Overview the default. Verify the tab-bar `aria-selected`, the panel `active` class, and any localStorage last-tab restore all agree, and that no JS hard-codes `settings` as the fallback. Returning users keeping their last tab (if restore exists) is fine.
4. **Dedicated audit-gate for allow-list argv integrity?** **Yes — but only when an action is actually added** (moot for the recommended PR-1, which adds none). The moment `ALLOWED_ACTIONS` grows, the integrity gate ships in the *same* PR with a must-fail (interpolated argv) + must-pass (real table) fixture pair, per the repo's "new gate ⇒ fixture pair same PR" rule.
5. **Anything missed at the implementation level?** Yes — the big one: **the plan's premise that `/__run` changes land in BOTH server copies is false** (Gate 32 `INTENTIONALLY_EXCLUDED = {"/__run"}`; the plugin server has no `/__run` and `open-dashboard.sh` launches *that* copy) — so Class-A execution is **root-dev-server-only** and **dead for every consumer**, which the plan never states. Also: (a) Gate 35's string-extraction is brittle if a new tab's `<script>` becomes the largest block or renames a serializer symbol (P0-E); (b) the consumer disabled-state copy must say "dev server only," not "run serve-dashboards.py" (the consumer already runs it, just the no-`/__run` build); (c) `title=` tooltips are not a sufficient a11y guarantee — the always-visible literal-argv line is (P1); (d) `_decision_trees_inventory()` doesn't currently extract Mermaid at all, so even the "embed the mermaid block" step is new generator code.

---

*Claims marked against verified `file:line` are this-session-checked. No claim in this doc relies on training recall about the codebase; where I could not verify behavior at runtime (e.g. whether the consumer dashboard JS has a localStorage last-tab restore), I phrased it as a conditional to verify, not a fact.* `[unverified — runtime: localStorage last-tab restore behavior; the round-trip "largest <script>" collision is a code-read inference, not an observed failure.]`
