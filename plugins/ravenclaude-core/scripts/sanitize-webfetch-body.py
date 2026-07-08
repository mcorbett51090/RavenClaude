#!/usr/bin/env python3
"""sanitize-webfetch-body.py — strip injection-shaped blocks from a fetched body
before any agent treats it as content.

Why this exists: during the 2026-06-02 data-viz-designer verification pass, two
canonical sources (ibcs.com/standards, github.com/Financial-Times/chart-doctor
visual-vocabulary directory) returned WebFetch bodies that contained appended
<system-reminder> blocks impersonating system instructions. A deep-researcher
subagent correctly treated them as untrusted DATA — but that defense rested on
the model remembering the contract, not on a deterministic floor. This script
is the floor.

The discipline: any marketplace agent that issues a WebFetch reads the response
body THROUGH this sanitizer before quoting, parsing, or treating any of it as
authoritative. The sanitizer is deterministic, no network, no subprocess, no
eval. It strips the specific tag-shapes observed in the wild + a conservative
set of analogs; everything else passes through verbatim so a fetched canonical
doc's real content survives.

Usage:
    # CLI — read stdin, write sanitized stdout
    cat raw-body.html | python3 sanitize-webfetch-body.py > sanitized-body.html

    # CLI — pass a path, write sanitized to stdout
    python3 sanitize-webfetch-body.py raw-body.html

    # Programmatic
    from sanitize_webfetch_body import sanitize
    clean = sanitize(raw_body)

Exit codes:
    0 — sanitized output written (with or without strips); see stderr for count
    1 — bad arguments
    2 — file not found / IO error
    3 — input too large (over MAX_INPUT_BYTES; refuse rather than partial-pass)

Purity contract (mirrors plugins/ravenclaude-core/skills/pbir-layout-engine
purity contract — same shape, deliberately):
- deterministic (same input → same output, every time)
- no network calls
- no subprocess
- no eval / exec / dynamic import
- reads only argv-named path or stdin
- rejects argv paths containing `..` or absolute paths outside the repo root
- exits non-zero on any IO error rather than partial-pass

References:
- The two observed injection sites (2026-06-02): see
  docs/research/2026-06-02-data-viz-agent/webfetch-injection-memo.md
- Skill that documents the contract callers must follow:
  plugins/ravenclaude-core/skills/webfetch-hardening/SKILL.md
- Audit-gate that proves this script's bidirectionality:
  scripts/audit-gates.sh Gate 48 (good fixture unchanged, bad fixture stripped)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Input size cap. Fetched docs above this are refused outright (exit 3) rather
# than partially scanned — better to fail loud than to silently miss content
# beyond the cap. 8 MiB chosen as a generous-but-bounded limit; raise if a real
# canonical doc legitimately exceeds it and the use case justifies the cost.
MAX_INPUT_BYTES = 8 * 1024 * 1024

# The patterns observed in the wild on 2026-06-02. Conservative, anchored, and
# specific: each one matches a tag-shape that has *no legitimate reason to
# appear inside a fetched canonical doc body*. Real documentation about
# `<system-reminder>` (e.g. someone writing a security tutorial about prompt
# injection) is collateral damage we accept — the floor's job is to remove the
# *machinery* that could be misread as an instruction, not to preserve every
# mention.
#
# Each pattern compiled with DOTALL so `.` matches newlines (block tags span
# multiple lines in practice). IGNORECASE is intentional — real injection
# attempts vary case.
INJECTION_PATTERNS = [
    # 1. <system-reminder> ... </system-reminder> — the exact tag observed.
    re.compile(r"<system-reminder\b[^>]*>.*?</system-reminder>", re.DOTALL | re.IGNORECASE),
    # 2. <system-instruction> ... </system-instruction> — common variant.
    re.compile(r"<system-instruction\b[^>]*>.*?</system-instruction>", re.DOTALL | re.IGNORECASE),
    # 3. <important> ... </important> when followed by an imperative — the
    #    "IMPORTANT: do X" shape. We only strip the tag wrapper, leaving the
    #    text neutered. (This is the most generous pattern; many real docs use
    #    <important>; we accept the collateral damage and prefer the floor.)
    re.compile(r"<important\b[^>]*>\s*(?:IMPORTANT|MUST|NEVER|ALWAYS)[:\s].*?</important>", re.DOTALL | re.IGNORECASE),
    # 4. Bare "SYSTEM:" / "INSTRUCTION:" prompt-injection prefixes when they
    #    appear at the start of a line. Strip the line.
    re.compile(r"(?m)^\s*(?:SYSTEM|INSTRUCTION|SYSTEM PROMPT|NEW INSTRUCTIONS?)\s*[:>][^\n]*\n?", re.IGNORECASE),
    # 5. Markdown-style fenced "system" blocks — ```system ... ```
    re.compile(r"```\s*system\b[^\n]*\n.*?```", re.DOTALL | re.IGNORECASE),
    # 6-9. UNTERMINATED opening tags. Patterns 1-3/5 all require a matching
    #   closing delimiter, so an attacker bypasses them completely by simply
    #   omitting the close (e.g. `<system-reminder>…<EOF>` with no
    #   `</system-reminder>`). These run AFTER the paired patterns above (which
    #   have already removed any closed blocks), so a residual UNCLOSED opening
    #   tag of a high-signal injection shape is stripped through end-of-input.
    #   Collateral damage (a doc that legitimately opens one of these tags and
    #   never closes it loses everything after) is accepted — same floor
    #   philosophy as the paired patterns. There is one unclosed variant for
    #   EACH closed pattern that opens with a tag (1, 2, 3, 5) — pattern 3
    #   (<important>) was previously missing its counterpart, letting an
    #   `<important>IMPORTANT: …<EOF>` block bypass the sanitizer entirely.
    re.compile(r"<system-reminder\b[^>]*>.*\Z", re.DOTALL | re.IGNORECASE),
    re.compile(r"<system-instruction\b[^>]*>.*\Z", re.DOTALL | re.IGNORECASE),
    re.compile(r"<important\b[^>]*>\s*(?:IMPORTANT|MUST|NEVER|ALWAYS)[:\s].*\Z", re.DOTALL | re.IGNORECASE),
    re.compile(r"```\s*system\b.*\Z", re.DOTALL | re.IGNORECASE),
]


def sanitize(raw: str) -> tuple[str, int]:
    """Return (sanitized_body, num_strips). Pure function — no side effects.

    `num_strips` is the count of injection matches removed; callers can use it
    to log a single-line "sanitized N injection(s) from fetched body" trace
    without having to diff the input and output themselves.
    """
    out = raw
    n = 0
    for pattern in INJECTION_PATTERNS:
        out, k = pattern.subn("", out)
        n += k
    return out, n


def _resolve_input(args: argparse.Namespace, repo_root: Path) -> str:
    """Resolve the input source per the purity contract: stdin if no path,
    else the named path with traversal/escape rejection."""
    if not args.path:
        data = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        if len(data) > MAX_INPUT_BYTES:
            print(
                f"sanitize-webfetch-body: input on stdin exceeds {MAX_INPUT_BYTES} bytes",
                file=sys.stderr,
            )
            sys.exit(3)
        return data.decode("utf-8", errors="replace")

    raw_path = args.path
    if ".." in raw_path:
        print(
            f"sanitize-webfetch-body: argv path '{raw_path}' contains '..' — refused",
            file=sys.stderr,
        )
        sys.exit(1)

    p = Path(raw_path)
    # Resolve EVERY input — absolute or relative — and reject anything that lands
    # outside the repo root. The literal-".." guard above is a cheap pre-filter;
    # this is the real containment. It must apply uniformly: gating it on
    # p.is_absolute() left relative inputs checked only for a literal "..", yet a
    # relative path can still resolve outside the root (cwd elsewhere, a symlink).
    try:
        resolved = p.resolve()
        resolved.relative_to(repo_root.resolve())
    except (ValueError, OSError):
        print(
            f"sanitize-webfetch-body: argv path '{raw_path}' resolves outside repo root — refused",
            file=sys.stderr,
        )
        sys.exit(1)

    # Bound-before-consume: check the size via stat() BEFORE reading, so an
    # oversized file is rejected without ever loading it into memory (the stdin
    # path already caps its read; read_bytes() had no such bound and would OOM on
    # a huge file before the len() check below could reject it).
    try:
        size = p.stat().st_size
    except OSError as e:
        print(f"sanitize-webfetch-body: IO error stat-ing '{raw_path}': {e}", file=sys.stderr)
        sys.exit(2)
    if size > MAX_INPUT_BYTES:
        print(
            f"sanitize-webfetch-body: input file '{raw_path}' exceeds {MAX_INPUT_BYTES} bytes",
            file=sys.stderr,
        )
        sys.exit(3)

    try:
        data = p.read_bytes()
    except OSError as e:
        print(f"sanitize-webfetch-body: IO error reading '{raw_path}': {e}", file=sys.stderr)
        sys.exit(2)

    # Belt-and-suspenders against a TOCTOU grow between stat() and read().
    if len(data) > MAX_INPUT_BYTES:
        print(
            f"sanitize-webfetch-body: input file '{raw_path}' exceeds {MAX_INPUT_BYTES} bytes",
            file=sys.stderr,
        )
        sys.exit(3)

    return data.decode("utf-8", errors="replace")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Strip injection-shaped blocks from a fetched body. Reads stdin or a file path; writes sanitized body to stdout.",
    )
    parser.add_argument("path", nargs="?", help="Input file path (else read stdin)")
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress the strip-count stderr line"
    )
    args = parser.parse_args(argv)

    # Repo root is two levels up from this script (plugins/ravenclaude-core/scripts/).
    repo_root = Path(__file__).resolve().parents[3]

    raw = _resolve_input(args, repo_root)
    sanitized, n = sanitize(raw)

    sys.stdout.write(sanitized)
    if not args.quiet:
        print(
            f"sanitize-webfetch-body: stripped {n} injection block(s)",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
