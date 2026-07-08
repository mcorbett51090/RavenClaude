# Hermetic validation — a gate must not regenerate tracked files in place

**Status:** absolute rule for `scripts/audit-gates.sh` and any CI gate.
**Added:** 2026-07-08, after the in-place-regeneration churn was diagnosed.

## The rule

**A validation run must be side-effect-free on tracked files.** A gate that needs
generated output (a dashboard, a rendered page, a report) renders it to a **temp
path** and reads it from there — it never writes the committed artifact and never
leaves the working tree dirty.

## Why it exists (the failure this prevents)

`audit-gates.sh` Gate 13 used to run the dashboard + portal generators **without
`--check`**, writing `plugins/ravenclaude-core/dashboard.html` and `index.html`
**in place**, purely so the ~12 downstream render-test gates
(`check-heimdall-render.mjs`, …, `check-shell-router.mjs`) could extract their
functions from the *current* generator output instead of a possibly-stale
committed file.

The side effect: **every full audit run left those two tracked files modified in
the working tree** (fresh timestamp + any content drift). That churn:

- forced repeated manual `git checkout -- index.html dashboard.html` after every
  local `audit-gates.sh` run (and a stray-file commit if you forgot);
- made `git status` lie about what a change actually touched;
- coupled a _read-only validation_ to a _write_, which is the anti-pattern.

It also made **Gate 97** ("index freshness") a *self-fulfilling* check: it
`--check`-compared the committed `index.html` that Gate 13 had **just rewritten**,
so it never actually tested the file as committed — it tested the generator's
determinism while pretending to test committed freshness.

## The fix (2026-07)

Render the current output to `$TMP` once, and point every consumer at it:

```sh
DASH_HTML="$TMP/render-dashboard.html"
IDX_HTML="$TMP/render-index.html"
python3 scripts/generate-dashboards.py --plugin ravenclaude-core --stdout > "$DASH_HTML"
python3 scripts/generate-index-dashboard.py -o "$IDX_HTML"
# … then every render gate reads the temp file:
node scripts/check-heimdall-render.mjs "$IDX_HTML"
node scripts/check-concern-stats-render.mjs "$DASH_HTML"
```

Enabling changes:

- **`generate-dashboards.py --stdout`** — emit a single `--plugin`'s dashboard HTML
  to stdout without writing the committed file (the generator had no output
  redirect; `generate-index-dashboard.py` already had `-o/--output`).
- **`check-concern-stats-render.mjs`** now takes an optional path arg
  (`process.argv[2]`), like its sibling render gates already did.
- **Gate 97** now runs `--check -o "$IDX_HTML"` against the freshly-rendered temp
  file: an honest **generator-determinism + template-teeth** check (does a fresh
  render round-trip through `--check`, modulo the volatile timestamp surfaces?),
  never touching the committed `index.html`. The hand-edit teeth are preserved by
  appending a fixture to `$IDX_HTML` and asserting `--check` catches it.

Committed-artifact freshness is **not** a PR gate — it self-heals post-merge via
`.github/workflows/regenerate-artifacts.yml`. If you want to check the *committed*
file on demand, `audit-gates.sh --check 97` still reads it directly.

## The proof (and the regression guard)

The invariant is directly observable: **`git status` is clean immediately after a
full `audit-gates.sh` run.** If a future gate reintroduces an in-place write, that
one command surfaces it. Keep it that way:

- generators used by a gate must support a temp/stdout output mode;
- render/structural gates must accept a path argument (never hardcode the
  committed path);
- the only sanctioned in-place mutation is a `backup … / cp back` **teeth**
  fixture that restores the file in the same block **and** registers it with the
  `BACKUPS` + `cleanup`-trap mechanism, so it is restored on any exit path.

## See also

- `scripts/audit-gates.sh` Gate 13 (render prep) and Gate 97 (index freshness).
- `docs/best-practices/ci-gate-audit.md` — the bidirectional (fail-on-bad /
  pass-on-good) gate discipline this composes with.
- `plugins/ravenclaude-core/CLAUDE.md` § "Self-healing artifacts (freshness
  enforced post-merge, not on PRs)".
