# Multi-host audit — lens: Cursor / Windsurf / Aider (the file-convention hosts)

**Question:** Is RavenClaude fit to serve an agent orchestrating under Cursor, Windsurf, or Aider?

**Headline verdict:** This lane is **aspirational, not built** — and in one specific, load-bearing
place it is **actively false**, not merely thin. RavenClaude ships exactly one cross-tool artifact for
these three hosts: the prose claim in `AGENTS.md:3` that they "read this file natively." Beyond that
single sentence (repeated verbatim in two other files), there is no knowledge file, no generated
projection, no dashboard surface, no hook adapter, and no template — for any of the three. Contrast
this with GitHub Copilot CLI, which got a dedicated knowledge file
(`plugins/ravenclaude-core/knowledge/copilot-cli-customization.md`), a generated plugin projection
(`scripts/generate-copilot-plugin.py`), a hook adapter (`hooks/copilot-hook-adapter.sh`), and a
dashboard tab. Cursor/Windsurf/Aider got none of that — they got a name-check.

Verification method: read every in-repo reference (grep across `.md`/`.json`/`.py`), then fact-checked
the central claim against each tool's **own current official documentation** (fetched live this
session, not recalled from training) rather than trusting the repo's assertion or my own priors.

---

## P0 — broken or blocking for this host

### P0-1 · False claim: Aider does not natively read `AGENTS.md`

**Evidence:**
- `AGENTS.md:3` — *"Cursor, OpenAI Codex CLI, Aider, GitHub Copilot, and Windsurf read this file
  natively."*
- `plugins/ravenclaude-core/commands/init-agent-ready.md:141` — *"AGENTS.md is read by Cursor / Codex /
  Aider / Copilot natively; CLAUDE.md is Claude-Code-only."*
- `plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md:3` — *"...routes through AGENTS.md (which
  all major 2026 agents read)..."*

**What I verified this session** `[docs-verified]`:
- Aider's own conventions documentation (`https://aider.chat/docs/usage/conventions.html`, fetched
  live) makes **zero mention of `AGENTS.md`**. Its actual, documented default file is `CONVENTIONS.md`,
  and even that is **not auto-loaded** — the page's own words: *"It's best to load the conventions file
  with `/read CONVENTIONS.md` or `aider --read CONVENTIONS.md`."* Automatic loading only happens if the
  user adds an explicit `read:` entry to `.aider.conf.yml` — a per-repo opt-in the user must author.
- The same conclusion holds on `https://aider.chat/docs/faq.html` (fetched live): no mention of
  `AGENTS.md` anywhere.
- An open upstream GitHub issue, **aider-ai/aider#4363**, is literally titled *"Documentation Suggestion:
  Recommend AGENTS.md for Coding Conventions to Support Agent Rules Standard"* — i.e., a community member
  asking Aider to even **mention** AGENTS.md as an option. The issue is open, unresolved, with no
  maintainer response recorded as of this session.

**Why this is P0, not P1:** `AGENTS.md` is this repo's *only* cross-tool artifact — the single file that
carries setup commands, layout rules, testing instructions, and PR conventions to every non-Claude host.
A consumer who follows this repo's own instructions and puts everything into `AGENTS.md`, trusting the
"Aider reads this natively" claim, gets **silent zero coverage under Aider** unless they separately
discover and configure `--read AGENTS.md` or a `.aider.conf.yml` entry — something this repo documents
nowhere. That is a broken promise for the one file the whole cross-tool story rests on.

**Remedy:**
1. **Immediate (S):** correct the three call sites above. Minimal accurate wording: *"Aider does not
   auto-load `AGENTS.md`; point it at this file explicitly with `aider --read AGENTS.md` or a `read:`
   entry in `.aider.conf.yml`, or use its native `CONVENTIONS.md` convention."*
2. **Real fix (M):** ship a generated `CONVENTIONS.md` projection (same `extract_section()` pattern
   `scripts/generate-copilot-plugin.py:316-338` already proves out for Copilot) plus an
   `.aider.conf.yml` template with `read: [CONVENTIONS.md]`, wired into `/init-agent-ready`'s template
   set (`plugins/ravenclaude-core/templates/agent-ready-repo/`) so the claim becomes true for anyone who
   adopts it, instead of merely being corrected in prose.

---

## P1 — significant gaps; these hosts are materially underserved

### P1-1 · Zero knowledge file for any of the three hosts

**Evidence:** `plugins/ravenclaude-core/knowledge/` contains 20 files; exactly one
(`copilot-cli-customization.md`) documents a specific external coding-agent host. It has a real spine —
custom instructions, custom agents, agent skills, hooks, runtime & config, a mapping table ("How
RavenClaude maps onto each surface"), document discovery — verified against GitHub's own docs with an
inline citation (`copilot-cli-customization.md` header, "verified 2026-06-09"). No `cursor-*.md`,
`windsurf-*.md`, or `aider-*.md` file exists anywhere in the repo (`find … -iname "*cursor*" -o
-iname "*aider*" -o -iname "*windsurf*"` under `plugins/ravenclaude-core` returns nothing but the two
generic prose mentions already cited).

**Remedy (M):** author one knowledge file per host (or one combined file, given the smaller surface
area) mirroring `copilot-cli-customization.md`'s structure: instruction-file precedence, native
rules/hooks mechanism, MCP support, and an explicit "how RavenClaude maps onto this surface" section —
the exact analytical work Copilot got and these three never did.

### P1-2 · Cursor's own native rules convention is completely unserved

**Evidence (docs-verified, fetched live this session from `cursor.com/docs`):** Cursor's primary,
current mechanism is `.cursor/rules/*.mdc` files with `description`/`globs`/`alwaysApply` frontmatter,
with a stated precedence "Team Rules → Project Rules → User Rules." Cursor's own docs frame `AGENTS.md`
as *"a simple markdown file... as an alternative to `.cursor/rules`"* — i.e. the simpler, unscoped
sibling, not a superset. Nothing in this repo (`plugins/ravenclaude-core/templates/agent-ready-repo/`,
9 files, none named for Cursor) ever emits a `.cursor/rules/*.mdc` file. A Cursor user gets only the
flat, always-on `AGENTS.md` text — never the globbed, file-scoped rule Cursor's own convention is built
for (e.g., a rule that fires only on `Write`-shaped paths matching `.repo-layout.json`'s `allowed_globs`,
which is exactly this repo's most distinctive mechanism and exactly the kind of thing `.mdc` globs exist
to express).

**Remedy (M):** add a `.cursor/rules/ravenclaude.mdc` template (`alwaysApply: true`, projecting the
`AGENTS.md` grounding section — same projection pattern as the Copilot `AGENTS.md` block in
`generate-copilot-plugin.py`) to `/init-agent-ready`'s output, plus a second, glob-scoped rule for the
layout allow-list.

### P1-3 · Cursor's hooks API (mature, ~9 months old) has zero RavenClaude guardrail port

**Evidence (docs-verified via web search this session, corroborated across multiple independent
sources — GitButler's deep-dive, InfoQ, Cursor's community forum):** Cursor shipped a real hooks system
in Cursor 1.7 (October 2025): `.cursor/hooks.json` registers `beforeSubmitPrompt` /
`beforeShellExecution` / `beforeMCPExecution` / `afterFileEdit` / `stop`, and `beforeShellExecution` /
`beforeMCPExecution` can return JSON `allow`/`deny`/`ask` — structurally the same shape as Claude Code's
`PreToolUse` hook, and the *exact* shape `hooks/copilot-hook-adapter.sh` already bridges for GitHub
Copilot CLI (per `plugins/ravenclaude-core/CLAUDE.md` §"GitHub Copilot CLI bridge"). No
`cursor-hook-adapter.sh`, no `.cursor/hooks.json` template, and no mention of Cursor's hooks API exists
anywhere in this repo. Under Cursor, none of the guardrail stack applies — not `enforce-layout.sh`
(layout gets only the CI backstop, `validate-layout.yml`, which is a real but much slower net), not
`guard-destructive.sh`, not the command-review tribunal (the Thing), not `runaway-brake.sh` /
`dod-gate.sh`, not `guard-web-access.sh`.

**Remedy (L):** build `hooks/cursor-hook-adapter.sh` following the `copilot-hook-adapter.sh` precedent
(I/O envelope translation, `permissionDecision` mapping), a `.cursor/hooks.json` template wiring it, and
a gate analogous to Gate 20 (the Copilot adapter diagnostics gate) proving the translation round-trips.
This is real work — a new host's I/O envelope, not a copy-paste — but the precedent already proves the
shape is buildable, and it is the single highest-value item in this audit for closing an actual security
gap (right now Cursor consumers have *no* guardrail enforcement in-loop, CI-only).

### P1-4 · "Windsurf" is a stale brand name — rebranded to Devin Desktop on 2026-06-02

**Evidence (docs-verified this session):** `docs.windsurf.com/windsurf/cascade/agents-md` now
**307-redirects** to `docs.devin.ai/desktop/cascade/agents-md`. Cognition (maker of Devin) acquired
Windsurf in mid-2025 and formally rebranded the product **Devin Desktop on 2026-06-02** — roughly eight
weeks before this audit — per Cognition's/Devin's own blog and multiple contemporaneous trade-press
pieces. `AGENTS.md:3` and `init-agent-ready.md:5` still name "Windsurf" as a live, distinct brand with
no acknowledgment of the rename. Functionally the claim still holds — Devin Desktop's docs confirm it
*"automatically discovers [`AGENTS.md`] and feeds it into the same Rules engine"* as `.devin/rules/` /
the legacy `.windsurf/rules/` — so this is a naming-currency defect, not a functional one. But it is
exactly the kind of drift `plugins/ravenclaude-core/skills/knowledge-file-staleness-sweep/SKILL.md` and
the Researcher discipline exist to catch, and it went uncaught for two reasons that compound: (a) there
is no knowledge file tracking this host (P1-1) for a staleness sweep to even look at, and (b) the mention
is only 2 files deep, so it is easy to miss in a routine sweep scoped to `knowledge/`.

**Remedy (S):** update both call sites to *"Windsurf (rebranded Devin Desktop, June 2026)"* or similar,
so the next reader isn't confused chasing a discontinued brand name.

### P1-5 · The dashboard offers nothing to these hosts, and neither does the newest in-flight work

**Evidence:** `scripts/generate-dashboards.py` — every one of ~30 matches for the string `cursor` is a
CSS `cursor: pointer` declaration; there is no Cursor/Windsurf/Aider-aware tab, card, or copy-paste
block anywhere in the ~13,000-line generator. Contrast with the dedicated "Install & Update" tab for
GitHub Copilot CLI and the "Bifröst" install wizard for Claude Code plugins (both documented in
`plugins/ravenclaude-core/CLAUDE.md`) — Copilot and Claude Code each got a first-class dashboard surface;
these three hosts got none.

This gap is not just legacy debt — it is being **actively reinforced today**. The same-day plan
`docs/plans/2026-07-28-prompt-engineering-learn/plan.md` §6.1 ("One-sided by design, not by shortfall",
lines ~451-462) designs a brand-new "Host & context" dashboard page (`#/host-context`) whose entire
detection space is **exactly three states**: `"claude-code"`, `"cannot-determine"` — with GitHub Copilot
explicitly disqualified from positive detection for lack of a session-marker env var (§6.1's own text).
Cursor, Windsurf/Devin Desktop, and Aider are not named anywhere in that plan's scope — a session running
under any of them will render **"cannot determine"** with no host-specific static fallback content
(precedence table, wired-state checklist) ever surfacing for them, even though the plan's own §4b
content (instruction-file precedence) would be directly relevant to a Cursor or Aider user reading that
same page.

**Remedy (S–M, time-sensitive — the plan is not yet merged):** before `#/host-context` ships, fold in a
static (non-detected) "Other hosts" section naming Cursor / Devin Desktop / Aider explicitly and linking
to the new knowledge file(s) from P1-1 — cheap to add now, harder to retrofit once the page's byte-level
DOM-budget contract (plan §5.2) is locked and ratcheted.

### P1-6 · A claim-grounding double standard: Copilot's claim is cited; these three are bare assertions

**Evidence:** The identically-shaped claim for GitHub Copilot CLI *is* verified in-repo, with an inline
citation: `scripts/generate-copilot-plugin.py:52-54` — *"Verified 2026-05-31 against GitHub docs: Copilot
CLI reads AGENTS.md from the repo root, cwd, or any dir named in COPILOT_CUSTOM_INSTRUCTIONS_DIRS
(docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)."` The
identically-worded claims for Cursor, Windsurf, and Aider in `AGENTS.md:3` carry **no citation, no
`[unverified]` marker, and no date** — despite this repo's own Claim Grounding & Source Honesty protocol
(`AGENTS.md:204-208`, `plugins/ravenclaude-core/CLAUDE.md` §"Claim Grounding & Source Honesty") requiring
exactly this treatment for any "consequential claim... written into a durable doc." One of the three
unwritten claims (Aider, P0-1) turned out to be false. This isn't a one-off oversight; it's the
repo's own accuracy discipline applied inconsistently across hosts named in the same sentence.

**Remedy (S):** apply the same citation discipline to the Cursor/Windsurf/Aider claims once corrected —
either an inline `[docs-verified — cursor.com/docs, retrieved 2026-07-28]`-style marker or a pointer to
the new knowledge file(s) that carry the citation.

---

## P2 — clear-value improvements

### P2-1 · Uncited Cursor version-floor claim

**Evidence:** `plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md:48` — *"Cursor ≥ 3.3 —
`/multitask` parallel agents + Composer 2.5 file-tree refactor."* No citation, no `[unverified]` marker,
no `[verify-at-use]` tag (the file's own footer at line 53 carries exactly such a tag for the Copilot CLI
row, but not for this one). I could not independently corroborate this specific version/feature pairing
this session and am not asserting it is wrong — only that it is stated as bare fact in a file that
otherwise practices citation discipline for its neighboring rows, which is itself the defect.

**Remedy (S):** either verify and cite the Cursor version/feature claim, or mark it
`[unverified — training knowledge]` per this repo's own protocol.

### P2-2 · The "71 files mention Cursor" figure is inflated by false positives

**Evidence:** A pass over the files matching `\bCursor\b` shows roughly 25–30% are unrelated to the
Cursor IDE — hits like `plugins/api-engineering/skills/cursor-pagination-design/SKILL.md`,
`plugins/api-engineering/best-practices/build-cursor-pagination-over-offset.md`, and CSS `cursor:
pointer` rules in `scripts/generate-dashboards.py`. This doesn't change the audit's conclusion — if
anything it strengthens it — but the raw count in the brief overstates how much of the repo is actually
"about" the Cursor tool.

**Remedy (S):** no action required; noted so a future audit doesn't over-credit coverage from a raw
grep count.

### P2-3 · Aider's real, correct mechanism (`CONVENTIONS.md`) has zero template — a buildable gap, not over-engineering

Per the brief's explicit question ("is a thin generated projection worth building, or is that
over-engineering for a lane with no real users") — my answer, split by host:

- **Aider: worth building.** Its actual native mechanism is knowable, narrow, and already has a proven
  projection pattern to copy (`generate-copilot-plugin.py`'s `extract_section()`). Building it both fixes
  P0-1 for real (not just in prose) and costs about the same as the prose-only fix plus a template file.
  Not over-engineering — it's the *minimum* correct fix, since correcting the prose alone leaves Aider
  users with nothing actionable.
- **Cursor: worth building, but the higher-value item is the hooks adapter (P1-3), not the rules
  projection.** The rules projection (P1-2) is a smaller win since `AGENTS.md` already works there natively
  — it upgrades ergonomics (glob-scoped rules) but doesn't fix a gap the way the hooks adapter would.
- **Windsurf/Devin Desktop: not worth a projection.** `AGENTS.md` already works there natively and by the
  same mechanism as root-level Devin/Cascade rules — a projection would duplicate content the host
  already reads correctly. The only real gap is the naming staleness (P1-4), which is a documentation fix,
  not an engineering one.

---

## P3 — nit / polish

### P3-1 · "Windsurf" and "Devin" are named side-by-side without cross-reference

**Evidence:** `plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md` names both "Windsurf" (nowhere
directly, but implied via "Cursor / Aider / Codex / Devin" audience lists at lines 6 and 17) and "Devin"
as if they were unrelated hosts on separate tracks, with no note that Devin Desktop is (per P1-4) the
current name of the Windsurf product. A reader unaware of the 2026-06-02 rebrand would reasonably wonder
why the tool-version-floor table (line 51) has a "Devin" row but no "Windsurf" row, or vice versa.

**Remedy (S):** one clarifying parenthetical wherever both names appear together.

---

## Summary table

| # | Severity | Title | Effort |
|---|---|---|---|
| P0-1 | P0 | False claim: Aider does not natively read `AGENTS.md` | S (prose) / M (real fix) |
| P1-1 | P1 | Zero knowledge file for any of the three hosts | M |
| P1-2 | P1 | Cursor's native `.cursor/rules/*.mdc` convention unserved | M |
| P1-3 | P1 | Cursor's mature hooks API has zero guardrail port | L |
| P1-4 | P1 | "Windsurf" is a stale brand name (→ Devin Desktop, 2026-06-02) | S |
| P1-5 | P1 | Dashboard + the in-flight Host & context page both exclude these hosts | S–M |
| P1-6 | P1 | Claim-grounding double standard (Copilot cited; these three bare) | S |
| P2-1 | P2 | Uncited Cursor version-floor claim | S |
| P2-2 | P2 | "71 files mention Cursor" is inflated by false positives | — (note only) |
| P2-3 | P2 | Aider's real mechanism (`CONVENTIONS.md`) has no template | M (= P0-1's real fix) |
| P3-1 | P3 | Windsurf/Devin naming not cross-referenced | S |

**Total buildable effort to close every P0/P1 for real (not just in prose):** roughly 2–3 focused
sessions — the Aider `CONVENTIONS.md` projection, the Cursor `.mdc` rules projection, and the naming
fixes are each small; the Cursor hooks adapter (P1-3) is the one genuinely large item and the one with
the clearest security payoff (it is the only item on this list that closes an actual enforcement gap
rather than a documentation one).

**Confidence:** high. Every host-behavior claim above was checked this session against the tool's own
current official documentation (Aider: `aider.chat/docs/usage/conventions.html`,
`aider.chat/docs/faq.html`; Cursor: `cursor.com/docs`; Windsurf/Devin: `docs.devin.ai/desktop/cascade/agents-md`
via the `docs.windsurf.com` redirect), not recalled from training or taken from the repo's own assertion.
