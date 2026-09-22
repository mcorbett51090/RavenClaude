#!/usr/bin/env python3
"""Refusals R1-R7 — what the studio will not emit, and the one narrow way past R1-R4.

⛔ THE QUARANTINE BYPASS IS THE POINT OF THIS FILE. Plan-A ruled that no R1-R4 refusal
may carry an override flag — "a supply-chain refusal with a --force is a refusal that
will be forced" — and then documented a three-part incantation (fence it, caption it,
follow it with a handling instruction) that turns an R2 FAIL into a PASS. That IS a
--force, spelled out in the shipped documentation, on a surface with no approval
workflow (S10) and an unappealable scanner (S9). Everything in the incantation is
authored by the same person who wrote the adversarial string, so it is self-attestation
with extra steps.

So the quarantine path here requires a FOURTH thing the author cannot supply alone: a
named human reviewer recorded in an EXTERNAL run record. A `reviewer:` line inside
SKILL.md clears nothing, by construction — see `_reviewer_for`, and the test that pins
it. Three of four is still FAIL.

⛔ NO OVERRIDE. There is deliberately no flag, env var or config key that clears an
R1-R4. `no_override_surfaces()` is the machine-checkable statement of that, and the
acceptance battery greps the CLI to prove none appeared.

Region rules:
  · frontmatter description -> UNCONDITIONAL FAIL, no quarantine, no reviewer. The
    description is injected verbatim into the system prompt for every user in the org,
    so an adversarial literal there is an injection vector, not a quotation (S20).
  · SKILL.md body and bundled files -> FAIL, quarantine available.

Stdlib only. Python 3.9-safe.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

# ── the ids this module owns, and which of them can never be overridden ──────

HARD_REFUSALS = ("R1", "R2", "R3", "R4")          # FAIL, no override, quarantine-gated
SOFT_REFUSALS = ("R1B", "R5", "R6", "R7")         # WARN, advisory, measured


def no_override_surfaces() -> tuple[str, ...]:
    """The refusal ids that no flag, env var or config key may clear.

    Exposed as a function rather than a bare constant so the acceptance battery can
    assert against the same object the CLI consults, instead of a copy that drifts.
    """
    return HARD_REFUSALS


# ── placeholder recognition: the difference between a secret and a doc about one ──
#
# gap-delta: "a grep is satisfied by the thing being DESCRIBED." A credential-rotation
# policy that says `Authorization: Bearer <TOKEN>` contains no credential. Every
# credential pattern below is checked against this first, and a placeholder-shaped
# value is not a finding. This is the single most important predicate in the file:
# without it R1 fires on documentation and gets switched off.
_PLACEHOLDER = re.compile(
    r"""^(?:
        [<{\[].*[>}\]]                      # <TOKEN>, {token}, [redacted]
      | \$\{?[A-Za-z_][A-Za-z0-9_]*\}?      # $TOKEN, ${TOKEN}
      | %[A-Za-z_][A-Za-z0-9_]*%            # %TOKEN%
      | (?:YOUR|MY|THE)[_-]?\w*             # YOUR_API_KEY
      | (?:x{3,}|\*{3,}|\.{3,}|_{3,}|-{3,}) # xxx, ***, ..., ___
      | (?:REDACTED|EXAMPLE|SAMPLE|DUMMY|FAKE|PLACEHOLDER|CHANGEME|TODO|ELIDED)\w*
      | (?:token|secret|password|passwd|pass|key|apikey|api_key|credential)s?
      | (?:abc123|foo|bar|baz|test)\w*
    )$""",
    re.X | re.I,
)


_WRAPPERS = "\"'`" + "\u2018\u2019\u201c\u201d"
_TRAILING = ".,;:!?)"


def is_placeholder(value: str) -> bool:
    """True when `value` is documentation standing in for a secret, not a secret.

    ⛔ Strip markup and sentence punctuation BEFORE testing. The capture that feeds
    this is `\S+`-shaped, so in prose it swallows whatever abuts the token: the
    measured failure was `` `Authorization: Bearer <TOKEN>`. `` capturing
    "<TOKEN>`." — which is not `<...>`-shaped, so the placeholder test said "real
    credential" and R1 fired on a credential-ROTATION POLICY. That is precisely the
    described-vs-present false positive this predicate exists to prevent, and it
    would have been the first thing to make an author switch R1 off.
    Stripping cannot manufacture a false negative: a real key with its trailing
    period removed is still a real key and still matches no placeholder shape.
    """
    v = value.strip()
    prev = None
    while v != prev:                     # markup and punctuation can nest: `<T>`.
        prev = v
        v = v.strip(_WRAPPERS).rstrip(_TRAILING)
    if not v:
        return True
    if _PLACEHOLDER.match(v):
        return True
    # A run of one repeated character is never a real credential.
    return len(set(v)) <= 2


# ── R1: literal credentials (FAIL, ground truth) ─────────────────────────────
#
# Provider prefixes are ground truth: `AKIA` + 16 uppercase alnum is an AWS access key
# id by definition, not a heuristic about author habits. That is why R1 may sit at FAIL
# while R1B (entropy) may not.
_CRED_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("GitHub fine-grained PAT", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    ("GitLab PAT", re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}\b")),
    ("Stripe live key", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("npm token", re.compile(r"\bnpm_[A-Za-z0-9]{32,}\b")),
    ("HuggingFace token", re.compile(r"\bhf_[A-Za-z0-9]{32,}\b")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)

# These two carry a VALUE that must be checked against is_placeholder before firing.
_CRED_VALUED: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("bearer token", re.compile(r"[Aa]uthorization:\s*Bearer\s+([^\s`'\"]+)")),
    ("credential in URL", re.compile(r"://([^/\s:@]+):([^/\s:@]+)@")),
)

# ── R1B: high-entropy heuristic (WARN, advisory, measured) ───────────────────
# ⛔ NO `/` IN THE CHARSET. Measured on 934 skills: admitting `/` made every long
# path match — `Network/privateEndpoints/privateDnsZoneGroups`, a docs/research/...
# path — 2 of 3 hits, both false. Standard-base64 `/` is the cost; URL-safe base64
# (`-`, `_`) is what tokens actually use, and R1's provider prefixes are the
# ground-truth net regardless. Narrow the region, do not sharpen the pattern.
# ⛔ The mixed-case/digit test is applied to the MATCH in `_entropy_hit`, not as a
# lookahead. `(?=[^\s]*[A-Z])` scans forward past the token to the next whitespace,
# so it was satisfied by an uppercase letter that was not in the candidate at all —
# which is how the all-lowercase slug `2026-06-04-partner-success-command-center`
# matched a rule that requires an uppercase character. An unbounded lookahead is
# not the predicate it looks like.
_ENTROPY = re.compile(r"\b[A-Za-z0-9+_\-]{40,}\b")
# A 40-hex git SHA / sha1 and a 64-hex sha256 are not credentials; neither is a
# base64-looking data: URI payload. Excluded before the rate is even measured.
_ENTROPY_EXCLUDE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$", re.I)

def _entropy_hit(tok: str) -> bool:
    """True when `tok` looks like an opaque secret rather than a slug or a hash."""
    if _ENTROPY_EXCLUDE.match(tok) or is_placeholder(tok):
        return False
    # Mixed case AND digits, measured on the token itself.
    if not (any(c.isupper() for c in tok) and any(c.islower() for c in tok)
            and any(c.isdigit() for c in tok)):
        return False
    # A hyphen/underscore-separated slug is words, not entropy. Real tokens are one blob.
    return len(re.split(r"[-_]", tok)) <= 3


# ── R2: global-posture override (FAIL, ground truth) ─────────────────────────
_POSTURE = re.compile(
    r"\bignore\s+(?:all\s+)?(?:previous|prior|earlier|above|the\s+above)\s+instructions?\b"
    r"|\bdisregard\s+(?:all\s+)?(?:previous|prior|earlier|the\s+above|your)\b"
    r"|\bforget\s+(?:everything|all\s+(?:previous|prior)|your\s+instructions)\b"
    r"|\byou\s+are\s+now\s+(?:a|an|in)\b"
    r"|\bnew\s+instructions?\s*:"
    r"|\boverride\s+(?:your|the)\s+(?:system|previous|prior)\b"
    r"|\bdisregard\s+(?:your|the)\s+(?:system\s+prompt|guidelines|safety)\b",
    re.I,
)

# ── R3: covert channel / self-concealment / exfiltration (FAIL, ground truth) ─
#
# Two independent shapes. The exfil shape requires BOTH an egress imperative AND a
# reference to conversation/user content, because either alone is ordinary: a skill
# that POSTs to a ticketing API is normal, and a skill that discusses the transcript
# is normal. It is the conjunction that is the covert channel.
_EGRESS = re.compile(
    r"\b(?:POST|PUT|PATCH)\b\s+https?://|\bcurl\b[^\n]*\s-(?:d|-data|F|-form)\b"
    r"|\bfetch\s*\([^)]*method\s*:\s*['\"]POST|\bsend\s+(?:it|this|them)\s+to\s+https?://",
    re.I,
)
_CONVERSATION = re.compile(
    r"\b(?:conversation|transcript|chat\s+history|message\s+history|previous\s+messages"
    r"|the\s+user'?s\s+(?:message|input|prompt|data|files?)|everything\s+the\s+user)\b",
    re.I,
)
_CONCEAL = re.compile(
    r"\bdo\s+not\s+(?:tell|mention|inform|notify|reveal\s+to)\s+the\s+user\b"
    r"|\bwithout\s+(?:the\s+user|them)\s+(?:knowing|noticing|being\s+aware)\b"
    r"|\b(?:hide|conceal)\s+(?:this|it)\s+from\s+the\s+user\b"
    r"|\bdo\s+not\s+(?:reveal|disclose|surface)\s+(?:this|these)\s+(?:instructions?|steps?)\b"
    r"|\bnever\s+mention\s+(?:this|these)\s+(?:instructions?|to\s+the\s+user)\b",
    re.I,
)

# ── R4: tool-authority expansion (FAIL, ground truth) ────────────────────────
_TOOL_AUTH = re.compile(
    r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba|z|k|)sh\b"
    r"|\b(?:ba|z|)sh\s*<\s*\(\s*(?:curl|wget)\b"
    r"|\bpip\s+install\s+(?:--\S+\s+)*(?:https?://|git\+https?://)"
    r"|\bnpm\s+(?:i|install)\s+(?:--\S+\s+)*(?:https?://|git\+)"
    r"|\bIEX\s*\(\s*New-Object\s+Net\.WebClient",
    re.I,
)

# ── R5: persona override on binding matters (WARN, advisory, measured) ───────
_PERSONA = re.compile(
    r"\b(?:you\s+are\s+(?:now\s+)?(?:a|an)|act\s+as(?:\s+if\s+you\s+are)?(?:\s+a|\s+an)?"
    r"|pretend\s+(?:to\s+be|you\s+are)|roleplay\s+as)\b[^.\n]{0,60}?"
    r"\b(?:lawyer|attorney|physician|doctor|clinician|accountant|auditor|"
    r"regulator|compliance\s+officer|security\s+officer|judge)\b",
    re.I,
)

# ── R6: org-confidential material (WARN, advisory, measured) ─────────────────
_CONFIDENTIAL = re.compile(
    r"\b(?:strictly\s+confidential|company\s+confidential|internal\s+use\s+only"
    r"|do\s+not\s+distribute|attorney[\s-]client\s+privileged"
    r"|under\s+NDA|subject\s+to\s+an\s+NDA)\b"
    r"|\b\d{3}-\d{2}-\d{4}\b",                      # US SSN shape
    re.I,
)


# ── quarantine ────────────────────────────────────────────────────────────────

_FENCE_OPEN = re.compile(r"^\s*(?:```|~~~)")
_FRAME = re.compile(
    r"\b(?:adversarial|prompt[\s-]?injection|injection\s+attempt|attack|malicious"
    r"|untrusted|hostile|example\s+of\s+an?\s+attempt|do\s+not\s+follow)\b",
    re.I,
)
_HANDLING = re.compile(
    r"\b(?:do\s+not\s+follow|never\s+(?:follow|execute|obey|comply)|treat\s+(?:it|this|the\s+above)"
    r"\s+as\s+(?:data|untrusted)|refuse\s+(?:it|this)|report\s+(?:it|this)\s+to"
    r"|do\s+not\s+comply|ignore\s+the\s+instruction\s+above)\b",
    re.I,
)

_QUARANTINE_WINDOW = 3          # lines of caption before / handling after the fence


def _fenced_line_spans(lines: list[str]) -> list[tuple[int, int]]:
    """Return [(open_idx, close_idx)] for each fenced block, 0-based, inclusive."""
    spans: list[tuple[int, int]] = []
    open_at: int | None = None
    for i, ln in enumerate(lines):
        if _FENCE_OPEN.match(ln):
            if open_at is None:
                open_at = i
            else:
                spans.append((open_at, i))
                open_at = None
    if open_at is not None:                 # unterminated fence: treat to EOF
        spans.append((open_at, len(lines) - 1))
    return spans


def _quarantine_state(lines: list[str], line_idx: int) -> dict[str, bool]:
    """Which of the three IN-FILE quarantine conditions hold for a hit at line_idx."""
    state = {"fenced": False, "framed": False, "handled": False}
    for open_i, close_i in _fenced_line_spans(lines):
        if not (open_i < line_idx <= close_i):
            continue
        state["fenced"] = True
        before = "\n".join(lines[max(0, open_i - _QUARANTINE_WINDOW):open_i])
        after = "\n".join(lines[close_i + 1:close_i + 1 + _QUARANTINE_WINDOW])
        state["framed"] = bool(_FRAME.search(before))
        state["handled"] = bool(_HANDLING.search(after))
        break
    return state


def load_run_record(path: str | None) -> dict[str, Any]:
    """Read the external run record. A missing/unreadable record is an EMPTY one.

    Fail-closed by construction: no record means no reviewer, which means no
    quarantine clears. There is deliberately no error path that grants clearance.
    """
    if not path:
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _reviewer_for(record: dict[str, Any], span: str, rule_id: str) -> str | None:
    """The named human who reviewed THIS span, from the EXTERNAL run record only.

    ⛔ The record is a separate artifact on purpose. A `reviewer:` line inside SKILL.md
    is written by the same hand that wrote the adversarial string, so honoring it would
    reduce the reviewer gate to self-attestation — which is exactly the bypass this
    whole mechanism exists to close. Nothing in this function reads the skill.
    """
    for entry in record.get("quarantine_reviews", []) or []:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("span", "")).strip() != span:
            continue
        if str(entry.get("rule", "")).strip() not in ("", rule_id):
            continue
        who = str(entry.get("reviewer", "")).strip()
        when = str(entry.get("date", "")).strip()
        if who and when:
            return who
    return None


# ── the scan ──────────────────────────────────────────────────────────────────

def _hits(text: str) -> list[tuple[str, str, int, str]]:
    """Return [(rule_id, label, line_no_1based, matched_text)] for every refusal shape."""
    out: list[tuple[str, str, int, str]] = []

    def add(rule: str, label: str, m: re.Match[str]) -> None:
        line = text.count("\n", 0, m.start()) + 1
        out.append((rule, label, line, m.group(0)[:80]))

    for label, pat in _CRED_PATTERNS:
        for m in pat.finditer(text):
            add("R1", label, m)
    for label, pat in _CRED_VALUED:
        for m in pat.finditer(text):
            value = m.group(2) if pat.groups >= 2 else m.group(1)
            if is_placeholder(value) or (pat.groups >= 2 and is_placeholder(m.group(1))):
                continue
            add("R1", label, m)
    for m in _ENTROPY.finditer(text):
        if _entropy_hit(m.group(0)):
            add("R1B", "high-entropy string", m)
    for m in _POSTURE.finditer(text):
        add("R2", "global-posture override", m)
    for m in _CONCEAL.finditer(text):
        add("R3", "self-concealment", m)
    for m in _EGRESS.finditer(text):
        # Conjunction only: egress ALONE is an ordinary documented API call.
        window = text[max(0, m.start() - 400):m.end() + 400]
        if _CONVERSATION.search(window):
            add("R3", "exfiltration of conversation content", m)
    for m in _TOOL_AUTH.finditer(text):
        add("R4", "tool-authority expansion", m)
    for m in _PERSONA.finditer(text):
        add("R5", "persona override on a binding matter", m)
    for m in _CONFIDENTIAL.finditer(text):
        add("R6", "org-confidential material", m)
    return out


def scan_refusals(skill_dir: str, table: dict[str, Any], body: str, desc: str,
                  run_record: dict[str, Any] | None = None,
                  bundled: list[str] | None = None) -> list[dict[str, Any]]:
    """Return refusal findings for a skill. Never raises on a malformed record."""
    by = {r["id"]: r for r in table["rules"]}
    record = run_record or {}
    findings: list[dict[str, Any]] = []

    def emit(rule_id: str, span: str, message: str, cleared_by: str | None = None) -> None:
        rule = by.get(rule_id)
        if rule is None:                      # a table without the rule cannot enforce it
            return
        # ⛔ A CLEARED QUARANTINE DOES NOT BLOCK — that is what "cleared" means, and the
        # plan's third fixture requires a PASS. It stays in the report, and it still
        # drives scanner_risk to `elevated` (the literal is in the archive either way),
        # but it is no longer a FAIL. Keeping tier `fail` here made the legitimate path
        # unreachable: the CLI printed "QUARANTINED: ... reviewed by <name>" and then
        # exited 2 anyway. The battery missed it because it asserted the presence of the
        # cleared-by LABEL and never the resulting tier — a test that checks the label
        # instead of the behaviour.
        tier = "warn" if cleared_by else rule["tier"]
        f = {
            "rule_id": rule_id,
            "tier": tier,
            "class": rule["class"],
            "span": span,
            "message": message,
            "remediation": rule["remediation"],
            "claim": rule["claim"],
            "fire_rate": rule.get("fire_rate"),
        }
        if cleared_by:
            f["quarantine_cleared_by"] = cleared_by
        findings.append(f)

    # ── the description: unconditional, no quarantine, no reviewer ───────────
    for rule_id, label, _line, matched in _hits(desc):
        if rule_id in HARD_REFUSALS:
            emit(rule_id, "frontmatter.description",
                 "%s in the DESCRIPTION (%r). The description is injected verbatim into "
                 "every user's system prompt, so this is an injection vector, not a "
                 "quotation. There is no quarantine path here." % (label, matched))
        else:
            emit(rule_id, "frontmatter.description", "%s (%r)" % (label, matched))

    # ── the body and any bundled file: quarantine available ──────────────────
    sources: list[tuple[str, str]] = [("SKILL.md", body)]
    for rel in bundled or []:
        try:
            with open(os.path.join(skill_dir, rel), encoding="utf-8") as fh:
                sources.append((rel, fh.read()))
        except (OSError, UnicodeDecodeError):
            continue

    for fname, text in sources:
        lines = text.splitlines()
        for rule_id, label, line_no, matched in _hits(text):
            span = "%s:%d" % (fname, line_no)
            if rule_id not in HARD_REFUSALS:
                emit(rule_id, span, "%s (%r)" % (label, matched))
                continue
            q = _quarantine_state(lines, line_no - 1)
            who = _reviewer_for(record, span, rule_id)
            if q["fenced"] and q["framed"] and q["handled"] and who:
                emit(rule_id, span,
                     "%s (%r) — QUARANTINED: fenced, framed, handled, and reviewed by %s"
                     % (label, matched, who), cleared_by=who)
                continue
            missing = [k for k in ("fenced", "framed", "handled") if not q[k]]
            if not who:
                missing.append("a named reviewer in the run record")
            emit(rule_id, span,
                 "%s (%r) — NOT quarantined; missing: %s"
                 % (label, matched, ", ".join(missing)))
    return findings


# ── scanner risk ──────────────────────────────────────────────────────────────

SCANNER_RISK_NOTE = """\
scanner_risk is this tool's SELF-ASSESSMENT. It is not a prediction of the outcome.
  · The real scanner may disagree in EITHER direction — it can fail a bundle this rates
    `none`, and it can pass one this rates `elevated` (S9).
  · Its verdict is unappealable. A fail cannot be overridden by you, and your admins
    cannot approve it (S9).
  · It re-fires on EVERY edit, not only the first upload — a bundle that passed last
    week can fail on a one-word change.
Therefore: attempt the upload EARLY, not on a deadline. That single operational habit is
worth more than any local prediction this tool can make."""


def scanner_risk(findings: list[dict[str, Any]]) -> tuple[str, list[str]]:
    """Return (none|low|elevated, driving spans). Quarantined hits still drive risk.

    A cleared quarantine means the studio will emit the bundle. It does NOT mean the
    scanner will like it — the literal is still in the archive, which is precisely what
    the classifier reads. Downgrading risk on clearance would be this tool telling the
    author the opposite of the truth.
    """
    hard = [f for f in findings if f["rule_id"] in HARD_REFUSALS]
    if hard:
        return "elevated", ["%s %s" % (f["rule_id"], f["span"]) for f in hard]
    soft = [f for f in findings if f["rule_id"] in SOFT_REFUSALS]
    if soft:
        return "low", ["%s %s" % (f["rule_id"], f["span"]) for f in soft]
    return "none", []
