# Repo review — decisions needed (2026-08-31)

Autonomous scheduled repo review: 5 expert finder panels (shell, python gates,
manifests/schemas, CI workflows, docs/cross-references), each independently
verified by re-reading the cited code before anything was implemented. Two
prior reviews (#829, #830) had already swept most of the executable-code
surface, so this pass targeted **gate-invisible** defects — things that pass
every existing CI gate but are still wrong.

**6 candidate findings surfaced, 1 rejected on verification, 5 confirmed and
implemented (P2/P3, all mechanical) in the accompanying PR.** No P0/P1 —
this repo's gate corpus is unusually hardened against the classes of bug the
panels hunted for. **2 additional items below are judgment calls, not
mechanical fixes, and are left for review rather than guessed at.**

## What was implemented in the PR (no decision needed)

| Pri | Fix | File(s) |
|---|---|---|
| P2 | `\b` (a GNU grep extension, undefined in POSIX ERE) in the SSN/credit-card-PAN/IBAN rules meant stock/BSD grep (macOS) silently matched nothing — a fail-open secret scan on the highest-sensitivity data in the marketplace. Replaced with portable `(^|[^X])...([^X]|$)` boundaries; 13/13 existing acceptance tests still pass. | `plugins/finance/hooks/scan-finance-secrets.sh` |
| P2 | Marketplace catalog's own headline description claimed "144 domain plugins"; actual count is 179 (180 total incl. core). No existing gate validates this specific number. | `.claude-plugin/marketplace.json` |
| P3 | Schema documented an unused `requires.ravenclaude-core` convention; all 179 domain plugins actually use `requires.plugins: ["ravenclaude-core@>=X.Y.Z"]`, which went completely unvalidated. Schema now validates the real shape (verified against all 180 manifests + the audit-gates good/bad fixtures). | `schemas/plugin.schema.json` |
| P3 | A security-rationale comment justifying a SHA pin named a stale SHA/version (`c5a7806`/v6.1.0) that no longer matched the actual pin (`5f6978f`/v8.1.1) — the action had been bumped without updating its own audit trail. | `.github/workflows/quarantine-intake.yml` |
| P3 | A milestone note's line-number citation (`audit-gates.sh:761`) pointed at unrelated code; the actual retired-Gate-11 reference is at line 1128. | `plugins/ravenclaude-core/CLAUDE.md` |

**Rejected on verification:** the shell-panel also flagged `scripts/dod-fast.sh`'s
`python3 -m ruff` fallback as "not a supported entry point on most installs."
This session installed `ruff` fresh and confirmed `python3 -m ruff --version`
works correctly (ruff has shipped a `__main__` since v0.1.9). Not a defect —
included here only so the rejection is visible, not silently dropped.

---

## Decision 1 — extend `check-css-token-hygiene.py` to catch a multi-line variant of the exact defect it exists for?

**Finding (P3, verified this session).** `scan_text()` in
`scripts/check-css-token-hygiene.py` matches its rule 2 (a hardcoded
`#fff`/`#000`/`white`/`black` foreground on a themed fill —
the *1.95:1 on accent / 2.76:1 on dark-theme danger* defect the gate's own
header documents as the motivating case) **per physical line**
(`text.splitlines()`, matched line-by-line). A declaration authored as

```css
background: var(--danger);
color: white;
```

on two separate lines is invisible to the gate; only the single-line form
`background: var(--danger); color: white;` is caught. Today every source the
gate scans writes this single-line, so it's green — but a future template or
generator edit that reflows a themed-fill declaration across lines would ship
the identical unreadable-text defect this gate was built to catch, with CI
staying green.

**Why this wasn't auto-fixed.** The obvious fix — join each `{...}` block
into one string before matching — is exactly what this file's own header
warns against: rule 4 (`_has_bare_link_colour`) **already tried scanning
whole-document text once**, found it invented false-positive "rules" out of
unrelated braces (Python f-strings / dict literals in the `scripts/generate-*.py`
sources this gate also scans), and was rewritten to scope itself to `<style>`
blocks only, with the lesson written into the code as a comment: *"a checker
that cries wolf gets ignored."* Rules 1–2 scan `.py` generator sources
directly (no `<style>` tag to scope to), so a naive brace-matching join risks
reintroducing that exact false-positive class across ~283 Python files. A
narrower windowed-join (e.g., look ahead a bounded few lines for the closing
`;`) is possible but is itself a judgment call about how much false-positive
risk is acceptable in a gate whose entire value proposition is precision.

**Options, cheapest first:**
1. **Leave as-is**, documented as a known static-lint scope limit (the file's
   own header already says the gate is "a static text lint," not a
   contrast-ratio computer). Lowest risk, status quo.
2. **Bounded multi-line window** — join each line with the next N (e.g. 2)
   lines only when scanning `.css`/`.html` template sources (not `.py`
   generator sources, where the false-positive risk lives), leaving rule 2's
   Python-source coverage as single-line. Narrows the blast radius to the
   file types where a themed-fill declaration is actually likely to reflow.
3. **Full block-join for `<style>`-scoped surfaces only** (mirroring rule 4's
   already-proven scoping), skip `.py` sources entirely for rule 2 (accept
   that generators are less likely to hand-format across lines than authored
   CSS).

**Recommendation:** option 2, scoped as narrowly as rule 4 already
demonstrates works — but this is a genuine call about how much gate
complexity to accept for a currently-zero-incidence pattern, not something
to guess at unattended.

---

## Decision 2 — is a dedicated `check-macos-portability.sh` "door 4" worth adding for the `\b`/BSD-grep class fixed in this PR?

**Context.** The fix in Decision-free item P2 above (the `\b` GNU-extension
bug in `scan-finance-secrets.sh`) is the *same class* of GNU-vs-BSD-grep
defect that `_portable.sh` and `check-macos-portability.sh` already document
and test for as "door 3" — except door 3 covers `grep -P` (which BSD grep
rejects outright, exit 2) and this was `grep -E` with `\b` (which BSD grep
accepts but silently doesn't anchor as a word boundary, per this session's
research; this repo has no BSD grep to test against directly — the fix
itself doesn't depend on that distinction, but a regression *test* proving
BSD grep's behavior would).

`check-macos-portability.sh` runs on `macos-latest` in CI
(`validate-macos.yml`) specifically to catch this class before it ships
again. This PR fixes the one instance found; it does **not** add a "door 4"
regression test to `check-macos-portability.sh` guarding against `\b`
recurring in a *future* `grep -E` pattern anywhere in the repo (there are
215 shell files; a generic "no `\b` in any `grep -E` pattern" static check
is plausible but wasn't attempted this session).

**Why this wasn't auto-added.** Extending a CI gate that runs on a real
macOS runner, without access to a macOS host to validate the new test
actually exercises BSD grep's real behavior (as every existing door does,
with a documented preflight that refuses to report false-green on a non-stock
toolchain), is exactly the kind of untested-gate-addition risk this repo's
own `docs/best-practices/ci-gate-audit.md` discipline warns against — a gate
added without proof it can fail is not a gate.

**Options:**
1. **Static grep-for-`\b`-in-grep-E-patterns check** — cheap, portable
   (doesn't need a macOS runner to validate the *logic*, only to validate
   the runtime behavior it's inferring from), but a strict textual scan for
   `\b` risks false positives on scripts where `\b` is deliberately quoted/escaped
   differently, or true positives that are actually fine (`grep -P` contexts
   where `\b` **is** valid).
2. **A runtime "door 4"** in `check-macos-portability.sh`, mirroring door 3's
   shape exactly (a known-bad fixture + a must-fail mutant), added and then
   verified on an actual `macos-latest` CI run (not locally, since this
   session has no macOS host).
3. **Leave it** — the one instance is fixed; the class is now written down
   in this doc and in the fix's own inline comment, which is where the next
   reviewer would look.

**Recommendation:** option 2 is the most consistent with existing repo
convention but needs to be built and validated on a real `macos-latest` run
rather than guessed at from a Linux session — flagging for a follow-up PR
rather than shipping unverified.

---

*Run artifacts (finder transcripts, verification notes): this was an
in-session review; no separate `.ravenclaude/runs/` artifact was produced
beyond this document and the accompanying PR diff.*
