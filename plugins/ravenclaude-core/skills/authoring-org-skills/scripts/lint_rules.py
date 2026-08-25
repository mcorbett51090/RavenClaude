#!/usr/bin/env python3
"""The rule battery for `orgskill lint`.

Split from orgskill.py so the CLI stays readable and the checks stay testable in
isolation. Every threshold is read from schemas/org-skill-rules.json — this file
contains no limit literals, per Phase 0 acceptance test 1.

⛔ THE TIER DISCIPLINE IS NOT DECORATION. A rule's tier comes from the table, never
from a branch here. A heuristic that fires often is still only WARN; a structural
truth is FAIL. If you find yourself wanting to hard-code a tier, the table is the
place to change it.

⛔ PV01/PV02 SCOPING IS THE POINT, NOT THE PATTERN. The fix for a false-positive-prone
check is a SMALLER CHECKED REGION, not a cleverer regex. Measured: a naive first-person
check fired 3/934 on the corpus and all three were false positives — every hit was
"I can" inside a quoted user utterance. So: description field only, quoted spans out,
backticked spans out, fenced spans out, subject position only, and `I` token-exact and
not adjacent to / or -. Do not "improve" this by widening it.

Stdlib only. Python 3.9-safe.
"""

from __future__ import annotations

import os
import re
from typing import Any

# ── the finding record ───────────────────────────────────────────────────────

def finding(rule: dict[str, Any], span: str, message: str) -> dict[str, Any]:
    """Stable finding shape. fire_rate rides along so a report can print the
    measured rate AND the population beside every advisory line — an advisory
    finding without its provenance is indistinguishable from a fact."""
    return {
        "rule_id": rule["id"],
        "tier": rule["tier"],
        "class": rule["class"],
        "span": span,
        "message": message,
        "remediation": rule.get("remediation", ""),
        "claim": rule.get("claim", ""),
        "fire_rate": rule.get("fire_rate"),
    }


# ── frontmatter parsing ──────────────────────────────────────────────────────

_FM_RE = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", re.S)


def split_frontmatter(text: str) -> tuple[str | None, str]:
    m = _FM_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def parse_scalars(block: str) -> tuple[dict[str, str], list[str]]:
    """A deliberately small YAML scalar reader.

    Refuses rather than guesses: anything it cannot confidently read is reported
    as ambiguity, which the caller turns into a fail-closed exit. A misparse here
    would silently skip a FAIL rule and report clean — the exact silent-green class
    this whole tool exists to prevent.
    """
    out: dict[str, str] = {}
    problems: list[str] = []
    key = None
    buf: list[str] = []
    for raw in block.splitlines():
        if not raw.strip():
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):[ \t]*(.*)$", raw)
        if m:
            if key is not None:
                out[key] = " ".join(" ".join(buf).split())
            key, first = m.group(1), m.group(2)
            buf = [first]
        elif raw.startswith((" ", "\t")) and key is not None:
            buf.append(raw.strip())
        else:
            problems.append("frontmatter line is neither a key nor a continuation: %r"
                            % raw[:60])
    if key is not None:
        out[key] = " ".join(" ".join(buf).split())
    for k, v in list(out.items()):
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            out[k] = v[1:-1]
    return out, problems


# ── span masking: the load-bearing half of PV01/PV02 ─────────────────────────

_FENCE = re.compile(r"```.*?```", re.S)
_BACKTICK = re.compile(r"`[^`]*`")
_DQUOTE = re.compile(r'"[^"]*"')
_CURLY = re.compile(r"[“][^”]*[”]")
_SQUOTE = re.compile(r"'[^']{3,}'")   # 3+ so an apostrophe in "user's" is untouched


def mask_unchecked_spans(s: str) -> str:
    """Blank out fenced, backticked and quoted regions.

    A description that quotes what a user says — "report I can show leadership" — is
    following best practice by carrying real trigger phrasing. Matching inside that
    quote is how a person-check ends up with a 100% false-positive rate.
    """
    for pat in (_FENCE, _BACKTICK, _CURLY, _DQUOTE, _SQUOTE):
        s = pat.sub(lambda m: " " * (m.end() - m.start()), s)
    return s


# `I` only as a standalone subject pronoun: token-exact, and NOT adjacent to / or -
# so I/O and I-9 never match.
# An XML/HTML tag: `<name ...>`, `</name>`, `<name/>`. A digit or space after `<`
# is not a tag, so `<300ms` and `a < b` pass; `->` never matches (no `<` at all).
_XML_TAG = re.compile(r"</?[A-Za-z][A-Za-z0-9:._-]*(?:\s[^<>]*)?/?>")

_FIRST_PERSON = re.compile(
    r"(?<![\w/-])(?:I)(?![\w/-])\s+(?:can|will|am|have|would|could|shall)\b"
    r"|(?<![\w/-])I'(?:ll|ve|m|d)\b"
    r"|\b(?:let me|we (?:will|can|shall))\b",
    re.I,
)
_SECOND_PERSON = re.compile(r"\byou can use (?:this|it)\b|\byou should use (?:this|it)\b", re.I)


# ── the checks ───────────────────────────────────────────────────────────────

def _limit(rule: dict[str, Any], text_key: str, default_pat: str) -> int | None:
    """Pull a numeric bound out of the rule's own text. The number lives in the
    table; this reads it rather than restating it."""
    m = re.search(default_pat, str(rule.get(text_key, "")))
    return int(m.group(1)) if m else None


def lint_skill(skill_dir: str, table: dict[str, Any],
               markers: list[str] | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (findings, ambiguities). Ambiguity is fail-closed at the caller."""
    by = {r["id"]: r for r in table["rules"]}
    findings: list[dict[str, Any]] = []
    ambiguity: list[str] = []

    # Case-insensitive, for the same reason verify() is (ZP10): Anthropic's own worked
    # example writes `skill.md`. Matters on a case-SENSITIVE filesystem, and on the
    # extracted tree ZP09 re-lints — where an exact match would turn a vendor
    # disagreement into a hard failure one layer down.
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        for _cand in sorted(os.listdir(skill_dir)) if os.path.isdir(skill_dir) else []:
            if _cand.lower() == "skill.md":
                skill_md = os.path.join(skill_dir, _cand)
                break
    if not os.path.isfile(skill_md):
        ambiguity.append("no SKILL.md in %s" % skill_dir)
        return findings, ambiguity
    try:
        text = open(skill_md, encoding="utf-8").read()
    except UnicodeDecodeError:
        ambiguity.append("SKILL.md is not valid UTF-8")
        return findings, ambiguity

    fm_block, body = split_frontmatter(text)
    if fm_block is None:
        findings.append(finding(by["FM01"], "SKILL.md:1",
                                "no YAML frontmatter block found"))
        return findings, ambiguity

    fm, fm_problems = parse_scalars(fm_block)
    ambiguity.extend(fm_problems)

    name = fm.get("name", "")
    desc = fm.get("description", "")

    # ── name (FM02-FM05, FM09, FM11) ─────────────────────────────────────────
    if not name:
        findings.append(finding(by["FM02"], "frontmatter.name", "`name` is missing or empty"))
    else:
        cap = _limit(by["FM03"], "rule", r"at most (\d+) characters")
        if cap and len(name) > cap:
            findings.append(finding(by["FM03"], "frontmatter.name",
                                    "`name` is %d characters (limit %d)" % (len(name), cap)))
        if not re.fullmatch(r"[a-z0-9-]+", name):
            findings.append(finding(by["FM04"], "frontmatter.name",
                                    "`name` contains characters outside [a-z0-9-]: %r" % name))
        if "<" in name or ">" in name:
            findings.append(finding(by["FM05"], "frontmatter.name", "`name` contains angle brackets"))
        expected = os.path.basename(os.path.normpath(skill_dir))
        if expected and name != expected:
            findings.append(finding(by["FM09"], "frontmatter.name",
                                    "`name` is %r but the directory is %r" % (name, expected)))
        reserved = by["FM11"].get("reserved_words") or []
        if name in reserved:
            findings.append(finding(by["FM11"], "frontmatter.name",
                                    "`name` %r is a reserved word" % name))
        # naming heuristics — all WARN, all measured
        toks = name.split("-")
        stop = {"helper", "helpers", "utils", "util", "tools", "misc", "common", "stuff", "things"}
        if any(t in stop for t in toks):
            findings.append(finding(by["NM01"], "frontmatter.name",
                                    "`name` contains a placeholder token"))
        generic = {"test", "agent", "framework", "system", "service", "engine",
                   "module", "manager", "handler", "tool"}
        if any(t in generic for t in toks):
            findings.append(finding(by["NM02"], "frontmatter.name",
                                    "`name` leans on a generic domain noun"))
        if not re.match(r"^[a-z0-9]+ing(-|$)", name):
            findings.append(finding(by["NM03"], "frontmatter.name",
                                    "`name` is not in gerund form"))

    # ── description (FM06-FM08, DS*, PV*) ────────────────────────────────────
    if not desc:
        findings.append(finding(by["FM06"], "frontmatter.description",
                                "`description` is missing or empty"))
    else:
        cap = _limit(by["FM07"], "rule", r"at most (\d+) characters")
        if cap and len(desc) > cap:
            findings.append(finding(by["FM07"], "frontmatter.description",
                                    "`description` is %d characters (limit %d)" % (len(desc), cap)))
        # ⛔ TAG-SHAPED ONLY. S1 prohibits XML TAGS, not the characters `<` and `>`.
        # Measured on the 934-skill corpus: a bare-angle-bracket predicate fired on 63
        # descriptions, and inspecting them showed the overwhelming majority were ASCII
        # arrows ("inquiry->apply->admit->yield", "not legal advice -> routes hard calls")
        # with only three genuine tags. A FAIL-tier rule whose predicate is broader than
        # its own sourced claim is not ground truth — it is a heuristic wearing a citation,
        # and this one would hard-block a legitimate description over a hyphen and a
        # greater-than sign. Narrow the region to what the claim actually says.
        tag = _XML_TAG.search(desc)
        if tag:
            findings.append(finding(by["FM08"], "frontmatter.description",
                                    "`description` contains an XML tag (%s)" % tag.group(0)))

        verb = re.search(
            r"\b(use|create|build|generate|analy[sz]e|review|design|write|extract|convert|"
            r"validate|scaffold|audit|plan|diagnose|route|score|render|manage|configure|"
            r"implement|test|fix|tune|choose|decide|report|package|lint|check)\w*\b", desc, re.I)
        if not verb:
            findings.append(finding(by["DS01"], "frontmatter.description",
                                    "`description` names no capability verb"))

        mk = markers or []
        if mk and not re.search("|".join(re.escape(m) for m in sorted(mk, key=len, reverse=True)),
                                desc, re.I):
            findings.append(finding(by["DS02"], "frontmatter.description",
                                    "`description` carries no when-to-use trigger clause"))

        if re.match(r"^(helps with|processes data|does stuff|handles)\b.{0,40}$", desc.strip(), re.I):
            findings.append(finding(by["DS03"], "frontmatter.description",
                                    "`description` matches the vague stoplist"))

        masked = mask_unchecked_spans(desc)
        if _FIRST_PERSON.search(masked):
            findings.append(finding(by["PV01"], "frontmatter.description",
                                    "`description` uses first person outside quoted text"))
        if _SECOND_PERSON.search(masked):
            findings.append(finding(by["PV02"], "frontmatter.description",
                                    "`description` addresses the reader in second person"))

    # ── extra frontmatter keys (FM12) ────────────────────────────────────────
    extra = sorted(set(fm) - {"name", "description"})
    if extra:
        findings.append(finding(by["FM12"], "frontmatter",
                                "keys outside {name, description}: %s" % ", ".join(extra)))

    # ── body (FM10, BD01-BD03) ───────────────────────────────────────────────
    if not body.strip():
        findings.append(finding(by["FM10"], "SKILL.md", "the body after the frontmatter is empty"))
    else:
        cap = _limit(by["BD01"], "rule", r"at most (\d+) lines")
        n_lines = len(body.strip().splitlines())
        if cap and n_lines > cap:
            findings.append(finding(by["BD01"], "SKILL.md",
                                    "body is %d lines (guidance: %d)" % (n_lines, cap)))
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", body):
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if link.startswith("/") or ".." in link.split("/"):
                findings.append(finding(by["BD03"], "SKILL.md",
                                        "reference %r escapes the bundle" % link))
                continue
            if not os.path.exists(os.path.join(skill_dir, link.split("#", 1)[0])):
                findings.append(finding(by["BD02"], "SKILL.md",
                                        "referenced bundled file %r does not exist" % link))

    return findings, ambiguity


# ── the honest-scope paragraph, printed with every report ────────────────────

WHAT_THIS_DOES_NOT_CHECK = """\
What this does NOT check — read this before trusting a clean result:
  · not whether the skill is USEFUL, or whether anyone needs it;
  · not whether the body's procedure is CORRECT — no linter can read intent;
  · not whether it will be SELECTED in your org. Selection is relative to the whole
    field of skills installed there, which this tool cannot see (S18). A clean lint
    says nothing about whether the skill will ever fire;
  · not whether the platform SCANNER will accept it (S9). That verdict is Anthropic's,
    it fires on upload AND on edit, and a fail cannot be appealed by anyone.
A clean result means the archive is well-formed. It is not a quality judgement, and
it must never be shipped inside the bundle as one."""
