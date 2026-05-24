---
name: cross-platform-determinism
description: For any script that produces a file the repo COMMITS and CI DIFFS — generated HTML, lockfiles, JSON snapshots, fixture files, documentation rendered from source. The output must be byte-identical regardless of who regenerated it or on what OS. This skill catches the specific failure modes that turn a freshness gate into a paper tiger that fails forever — OS-dependent path separators, locale-dependent encodings, nondeterministic ordering, drifting timestamps. Triggers on phrases like "freshness check failing", "regenerated locally but diff doesn't match", "works in CI not on Windows", "generator produces different output", and on any review of a script whose output is committed.
---

# Skill: cross-platform-determinism

A generated artifact that is committed to the repo and diff-checked in CI must be **byte-identical regardless of who regenerated it or on what OS**. If a Windows contributor regenerates and the bytes drift, the freshness gate fails forever — until someone hand-fixes the platform difference, which usually means quietly committing whatever the gate accepts and moving on.

This skill is the checklist for writing — or fixing — that kind of script.

## Why this skill exists (the two real bugs that motivated it)

Both shipped in `scripts/generate-repo-guide.py` (the marketplace's own self-rendered HTML index):

1. **Path separator drift.** `str(path.relative_to(REPO_ROOT))` returns `plugins\ravenclaude-core\skills\foo.md` on Windows and `plugins/ravenclaude-core/skills/foo.md` on Linux. The Linux value got committed; CI regenerates on Linux and diffs match; the next Windows contributor regenerates, all 50+ embedded paths in the HTML flip to backslashes, the diff is enormous, the freshness gate fails, the contributor either gives up or commits the Windows version and breaks it for the next Linux contributor. Fix: `path.relative_to(REPO_ROOT).as_posix()`. Never `str(Path)` for serialized output.
2. **Encoding drift.** The script wrote UTF-8 strings (em-dashes, smart quotes, plugin descriptions with `→`) to `sys.stdout` for the `--check` path. Linux defaults to UTF-8; Windows defaults to cp1252. The Windows run crashes with `UnicodeEncodeError: 'charmap' codec can't encode character '→'`. Fix: explicit `encoding="utf-8"` on every read/write AND set `PYTHONIOENCODING=utf-8` (or reconfigure stdout) so the `--check` path works on Windows.

Both bugs are invisible until a contributor on a non-CI OS regenerates. By then the gate has been green for weeks and nobody trusts it.

## The pattern, named

**Any byte that lands in a committed artifact must be the same byte regardless of OS, locale, filesystem ordering, system clock, Python version, or shell.**

If you can't say that out loud about the output, the freshness gate is a paper tiger.

## When to invoke this skill

- Writing a new script whose output will be committed and diff-checked.
- Reviewing a PR that adds or changes such a script.
- Triaging a freshness / diff CI failure that *only* fails after a contributor regenerated locally.
- Receiving a bug report like "the gate passes in CI but fails when I regenerate."
- Any time a `scripts/check-*-fresh.sh` or equivalent CI step exists in the repo.

## The six categories of nondeterminism (and the fix for each)

### 1. Path separators — the single biggest source of diff churn

`pathlib.Path` and `os.path` both produce backslash separators on Windows when stringified. If any part of the path appears in the output, the output is OS-dependent.

```python
# WRONG — `str()` on a Path uses the OS separator
path=str(path.relative_to(REPO_ROOT))           # 'plugins\foo\bar.md' on Windows
print(f"wrote {output.relative_to(REPO_ROOT)}") # implicit __str__ — same problem
some_dict["src"] = f"{path.parent}/{name}"      # f-string of Path — same problem

# RIGHT — `.as_posix()` always returns forward slashes
path=path.relative_to(REPO_ROOT).as_posix()     # 'plugins/foo/bar.md' on every OS
print(f"wrote {output.relative_to(REPO_ROOT).as_posix()}")
some_dict["src"] = path.parent.as_posix() + "/" + name
```

**Rule:** if a `Path` is going to be serialized — into HTML, JSON, YAML, Markdown, stdout that gets captured into a file, or anywhere else that ends up in the committed artifact — use `.as_posix()`. Reserve `str(Path)` for paths that stay in-process (passing to `subprocess`, `open()`, etc.).

### 2. Encoding — UTF-8 everywhere, explicitly

Linux/macOS default to UTF-8. Windows defaults to cp1252 (or whatever the user's locale is). Without explicit encoding, any non-ASCII byte will either be silently re-encoded or crash.

```python
# WRONG — encoding defaults to locale
text = path.read_text()                  # cp1252 on Windows
path.write_text(text)                    # cp1252 on Windows — UTF-8 source corrupts on write
json.loads(manifest_path.read_text())    # may decode UTF-8 JSON as cp1252
sys.stdout.write(rendered_html)          # crashes on Windows when output contains '→', '—', '"'

# RIGHT — explicit UTF-8 on every I/O
text = path.read_text(encoding="utf-8")
path.write_text(text, encoding="utf-8")
json.loads(manifest_path.read_text(encoding="utf-8"))
sys.stdout.reconfigure(encoding="utf-8")  # then sys.stdout.write(rendered_html) is safe
```

**stdout/stderr special case:** when the script supports a `--check` / `--stdout` mode that prints the artifact (so CI can diff), the print path also needs UTF-8. Two options:
- `sys.stdout.reconfigure(encoding="utf-8", newline="\n")` at the top of `main()`.
- Document `PYTHONIOENCODING=utf-8` as a required env var and set it in the CI invocation.

Prefer the first — it works even when the contributor forgets to set the env var.

**Run the CI's actual command with `PYTHONIOENCODING=utf-8` from Windows once.** That's the test.

### 3. Line endings — LF, always

Windows opens files in text mode with `\r\n` by default. Git's `core.autocrlf` may rewrite line endings on checkout. The combination produces drift that's invisible to `cat` but lethal to `diff`.

```python
# WRONG — newline="" or default means LF on Linux, CRLF on Windows
path.write_text(content, encoding="utf-8")

# RIGHT — pin LF explicitly
path.write_text(content, encoding="utf-8", newline="\n")
```

If the artifact is binary (.docx, .pdf, .png), this doesn't apply. For everything else, force `\n`.

Pair the script-level fix with a `.gitattributes` line:

```
# .gitattributes — root level
repo-guide.html text eol=lf
*.md            text eol=lf
*.json          text eol=lf
```

That stops `core.autocrlf` from "helpfully" rewriting on the next checkout.

### 4. Ordering — sort everything that has no inherent order

Python `dict` iteration order is insertion order (stable since 3.7), but **filesystem iteration order is not stable across OSes**. `Path.iterdir()`, `Path.glob()`, and `os.listdir()` return entries in *filesystem* order, which is alphabetical on most ext4 filesystems and insertion-order on NTFS and APFS.

```python
# WRONG — relies on filesystem order
for entry in skills_dir.iterdir():
    items.append(parse(entry))

# RIGHT — explicit sort
for entry in sorted(skills_dir.iterdir()):
    items.append(parse(entry))

# WRONG — set iteration is order-undefined across runs
for tag in {a.tag for a in agents}: ...

# RIGHT — sort sets before emitting
for tag in sorted({a.tag for a in agents}): ...

# WRONG — dict.items() is insertion-order, but if insertion came from a set …
json.dumps(d)

# RIGHT — sort keys
json.dumps(d, sort_keys=True)
```

**Rule:** anywhere the source of an iteration is *the filesystem* or *a set*, wrap it in `sorted()`. Anywhere you serialize a dict to JSON, pass `sort_keys=True`.

### 5. Timestamps — omit, normalize, or strip before diffing

A timestamp in the output is the most common source of "every regeneration produces a diff" failures. Three options, in order of preference:

1. **Omit.** The artifact is supposed to be a function of the inputs, not of the wall clock. If the timestamp doesn't earn its place, delete it.
2. **Normalize to a deterministic value.** Use the latest input file's `git log` date instead of `datetime.now()`. Then the output changes only when an input changed.
3. **Strip before diffing.** If the timestamp must be there (e.g., shown to humans), the freshness check should strip the timestamp line from both sides before `diff`. This is what `scripts/check-guide-fresh.sh` does for the `Generated YYYY-…` line. The script-level fix is fine; just don't pretend the timestamp is part of the canonical output.

```bash
# In the freshness checker
strip_volatile() {
  grep -Ev 'Generated 20[0-9][0-9]-|Last updated</span>' "$1"
}
diff <(strip_volatile committed) <(strip_volatile regenerated)
```

If you find yourself adding more and more strips, that's a sign the generator should stop emitting that data.

### 6. Locale-dependent string operations

`str.upper()` / `str.lower()` are locale-dependent in some languages (Turkish dotless ı being the canonical example). `locale.setlocale()` anywhere in the process changes formatting for the rest of the run.

```python
# WRONG — locale-sensitive
sorted(items, key=lambda x: x.name.lower())   # Turkish locale produces different order

# RIGHT — case-insensitive sort that's locale-independent
sorted(items, key=lambda x: x.name.casefold())

# WRONG — default float formatting may use locale's decimal separator
f"{value}"   # could produce "3,14" in a comma-decimal locale

# RIGHT — explicit format string
f"{value:.6f}"
```

For RavenClaude-grade work this is rarely the failure mode; sorting with `.casefold()` instead of `.lower()` covers most of it.

## Review checklist (run this on every generator script touching a committed artifact)

Before shipping, the script must pass all of these:

- [ ] **Path separators:** every `Path` that ends up in the output uses `.as_posix()`. No `str(Path)` and no f-string of a `Path` survives into a committed string. (`grep -n 'str(.*\.relative_to\|f".*{.*\.relative_to' script.py` should return zero hits.)
- [ ] **Read encoding:** every `.read_text()`, `open()`, `json.loads(...read_text())`, etc. specifies `encoding="utf-8"`.
- [ ] **Write encoding:** every `.write_text()`, `open(..., "w")`, `print()` that goes into a redirected file specifies `encoding="utf-8"` AND `newline="\n"`.
- [ ] **stdout safety:** if the script has a `--check`/`--stdout` mode, it either calls `sys.stdout.reconfigure(encoding="utf-8")` at startup OR the docs + CI invocation set `PYTHONIOENCODING=utf-8`. Prefer the first.
- [ ] **Line endings:** `.gitattributes` at the repo root forces `text eol=lf` for the artifact's extension.
- [ ] **Ordering:** every `iterdir()`, `glob()`, `listdir()` is wrapped in `sorted()`. Every dict serialized with `json.dumps` uses `sort_keys=True`. No `set` iteration survives into output without sorting.
- [ ] **Timestamps:** the output contains no `datetime.now()` value AT ALL — or the freshness checker strips it from both sides before diffing.
- [ ] **Locale independence:** sorts use `.casefold()` not `.lower()`; numeric formatting uses explicit format strings, not implicit `str(float)`.
- [ ] **Cross-OS smoke test:** regenerate on the OS that ISN'T used by CI, then diff against the committed copy. If non-zero, fix the cause — do NOT commit the new diff to "make the gate happy."

## Anti-patterns

- **Committing the OS-divergent output to make the gate pass.** Whoever regenerates next on the OPPOSITE OS will hit the same failure inverted. The bug isn't in the artifact; it's in the generator.
- **Adding more strip-lines to the freshness checker.** Each new strip line is the script telling you it shouldn't be emitting that field. Fix the generator, not the diff.
- **"It works on my machine" as a closing comment.** The whole point of a committed-and-diffed artifact is that it works on every machine. If only your machine produces the committed bytes, you have not actually verified the generator.
- **Trusting `core.autocrlf`.** It's never "helpfully" inserted CRLF into a file that diffed fine; it does so silently in proportion to how busy the contributor is.
- **`str(Path)` reflex.** Years of Python tutorials show `str(Path)` in print statements. Those tutorials predate Windows-as-a-first-class-CI-platform. For anything that gets serialized, `.as_posix()` is the correct reflex.

## Quick repro recipes

To reproduce the path-separator bug locally on Windows (PowerShell):

```powershell
$env:PYTHONIOENCODING="utf-8"
python scripts/generate-repo-guide.py
# Diff: every plugins/foo/bar.md → plugins\foo\bar.md
git diff repo-guide.html | Select-String '\\\\'
```

To reproduce the encoding bug:

```powershell
# Temporarily clear PYTHONIOENCODING
Remove-Item Env:PYTHONIOENCODING -ErrorAction SilentlyContinue
python scripts/generate-repo-guide.py --check > out.html
# UnicodeEncodeError when output contains '→', '—', '"', etc.
```

If neither command produces a problem after your fix, the script is platform-agnostic for those two failure modes.

## Output (Structured Output Protocol)

When invoked as part of a review or fix, end with the SOP block per [`structured-output.md`](../structured-output/SKILL.md):

```
---RESULT_START---
{
  "status": "complete" | "partial" | "blocked",
  "summary": "audited N generator scripts; M nondeterminism issues found and fixed",
  "deliverables": ["list of files changed", "checklist verdict per script"],
  "handoff_recommendation": null,
  "confidence": 0.0-1.0,
  "risks_or_open_questions": ["any item from the checklist that couldn't be verified"],
  "next_actions": ["e.g., add .gitattributes line", "wire PYTHONIOENCODING into CI"]
}
---RESULT_END---
```
