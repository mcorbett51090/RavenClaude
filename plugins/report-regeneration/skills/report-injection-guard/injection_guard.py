#!/usr/bin/env python3
"""
injection_guard.py -- report-regeneration prompt-injection / untrusted-content gate.

Both the template and the new source reports flow into inference and (via `regenerate`) into
generated prose; a Power BI screenshot's OCR text and XMLA-returned strings are likewise
untrusted. Per the FORGE plan §4 (injection defense) and core-architecture-spec.md §6, "downstream
V-checks catch it" is FALSE for the two highest-value injection outcomes:

  * an injected "classify everything as frozen" makes every fidelity leg pass BY CONSTRUCTION
    (a force-all-frozen partition leaks stale data byte-identically), and
  * an injected sentence in a `regenerate` slot is NOVEL text no V-check inspects.

This gate closes exactly those two gaps with two deterministic, stdlib checks. It treats ALL
template / source / OCR'd text as **data, never instructions** (webfetch-hardening posture) --
it never obeys anything it reads; it only measures.

  1. PARTITION-ANOMALY GATE (on the Binding Manifest -- the force-all-frozen tripwire):
     hard-flag an input whose partition is anomalous --
       * the `frozen` fraction exceeds a calibrated ceiling (FROZEN_CEILING), OR
       * ZERO mutable (surgical/regenerate/needs-review) bindings on a report that still carries
         N >= MIN_DATA_TOKENS data-shaped tokens (the exact shape a successful "mark everything
         frozen" injection would produce). V6 does double duty as this tripwire; this gate makes
         it explicit and independent of any single harness run.

  2. PROVENANCE-BOUND NARRATIVE (on every `regenerate` slot in the output):
     every factual token -- number / currency / percent / date / period / URL / email / a
     bare long numeric identifier / an instruction-or-payment IMPERATIVE -- appearing in a
     `regenerate` slot MUST trace to a manifest binding (i.e. be present in the new-data
     provenance domain). Any un-provenanced token is a BLOCKER: it is novel text the fidelity
     harness's value/leak legs never inspect, and is the delivery vector for an injected
     sentence (a fraudulent wire instruction, a phishing URL, an attacker email).

The gate FAILs iff at least one BLOCKING finding is raised; else PASS. This sub-receipt is folded
into `report-qa-gate` (a blocking injection finding -> the assembled verdict FAILs).

This catches seeded defect **D13** (scripts/seed_defects.py::inject_D13): the injected
"force-all-frozen" instruction comment is treated as data (never obeyed, so the deterministic
manifest is unchanged and the partition-anomaly tripwire correctly stays armed for the case where
a classifier WOULD have obeyed), and the un-provenanced attacker prose appended to the
`regenerate` #outlook-narrative slot (a wire-routing number, an account number, an attacker email,
and a "wire/remittance" imperative -- none traceable to any binding) is caught crisply by the
provenance-bound narrative check.

Usage:
    python3 injection_guard.py --html <output.html> --manifest <manifest.json> \
        --new-data <new-data.json> [--frozen-ceiling F] [--format json|text] [--pretty]
    python3 injection_guard.py --version

Exit codes:
    0 -- gate == PASS (no blocking finding)
    1 -- gate == FAIL (>= 1 blocking finding)
    2 -- usage / path-guard / I/O / JSON-parse error (message on stderr + a best-effort JSON
         error object on stdout, mirroring qa_gate.py / a11y_lint.py's `_emit_error`)

Design constraints (binding): stdlib only (argparse, html.parser, json, re, sys, pathlib). No
network, no subprocess, no third-party imports. Path-guarded: inputs must resolve to real regular
files; NUL bytes rejected. Python 3.9.6 target: `from __future__ import annotations`; no `X | Y`
unions, no `match` statements. FULLY ML-free / inference-independent -- it never calls a model.
"""
from __future__ import annotations

import argparse
import html.parser
import json
import re
import sys
from pathlib import Path

# The SHARED anchor resolver (../../scripts/rr_anchor.py) — so the provenance-bound narrative check
# resolves the SAME compound css_selector anchors infer emits for id-less regenerate slots, not
# only element_id / simple '#id' (P2 #8).
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import rr_anchor  # noqa: E402

GATE_VERSION = "1.0.0"
SCHEMA = "report-regeneration/injection-guard@1"

# Calibrated partition-anomaly thresholds. The clean acme-widgets manifest is 8/31 frozen
# (~0.26); a force-all-frozen injection drives that toward 1.0 with zero mutable bindings.
# The ceiling sits well above any healthy partition and well below the attack shape.
FROZEN_CEILING = 0.85
MIN_DATA_TOKENS = 3  # >= this many data-shaped tokens + zero mutable bindings == the attack shape

VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})

# Non-rendering subtrees excluded from the rendered-token scans.
NON_RENDERED_TAGS = frozenset({"script", "style", "head", "title"})

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
_MONTH_ALT = "|".join(_MONTHS)

_RE_CURRENCY = re.compile(r"[$€£¥]\s?\d[\d,]*(?:\.\d+)?")
_RE_PERCENT = re.compile(r"[+-]?\d+(?:\.\d+)?%")
_RE_DATE_WORDS = re.compile(r"\b(?:" + _MONTH_ALT + r")\s+\d{1,2},\s*\d{4}", re.IGNORECASE)
_RE_DATE_ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_RE_PERIOD_QY = re.compile(r"\bQ([1-4])\s+(\d{4})\b")
_RE_PERIOD_YQ = re.compile(r"\b(\d{4})-Q([1-4])\b")
_RE_GROUPED_NUM = re.compile(r"\b\d{1,3}(?:,\d{3})+\b")

_RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_RE_URL = re.compile(r"\b(?:https?://|www\.)[^\s<>\"']+", re.IGNORECASE)
# A bare unbroken digit run of 5+ (an account / routing / order number). Legitimate report
# figures render with grouping commas ($4,821,300) or decimals (12.4%), so a 5+ unbroken run is
# not a formatted value; a 4-digit year (2025) is deliberately below the threshold.
_RE_BARE_DIGITS = re.compile(r"\b\d{5,}\b")

# Instruction-injection + payment-redirect imperatives. These are command-shaped tokens that a
# legitimate financial-report NARRATIVE essentially never carries; in a `regenerate` slot they
# are the signature of injected attacker prose (a jailbreak preamble or a BEC wire redirect).
_INJECTION_IMPERATIVES = [
    "ignore previous", "ignore all previous", "disregard previous", "disregard all",
    "previous instructions", "system:", "you must", "do not flag", "classify every",
    "classify all", "mark all", "as frozen", "override", "reclassify",
    "wire", "remit", "reroute", "remittance", "click here",
]

_MUTABLE_CLASSES = frozenset({"surgical", "regenerate", "needs-review"})


class InjectionGuardError(Exception):
    """Raised for any path-guard / I/O / JSON-parse failure (exit 2)."""


# ---- path guard (mirrors harness.py / a11y_lint.py: real regular file, reject NUL/traversal) ----

def safe_read_path(raw: str) -> Path:
    if not raw or "\x00" in raw:
        raise InjectionGuardError("empty or NUL-bearing path")
    if ".." in Path(raw).parts:
        raise InjectionGuardError(f"path traversal ('..') is not allowed: {raw!r}")
    try:
        resolved = Path(raw).resolve()
    except (OSError, RuntimeError) as exc:
        raise InjectionGuardError(f"cannot resolve path {raw!r}: {exc}") from exc
    if not resolved.exists():
        raise InjectionGuardError(f"input file not found: {raw!r} (resolved {resolved})")
    if not resolved.is_file():
        raise InjectionGuardError(f"not a regular file: {raw!r} (resolved {resolved})")
    return resolved


def load_json_file(path: Path) -> object:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InjectionGuardError(f"could not read {path.name}: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InjectionGuardError(f"{path.name} is not valid JSON: {exc}") from exc


# ---- lightweight HTML tree ----

class _Node:
    __slots__ = ("tag", "attr", "children")

    def __init__(self, tag: str, attrs) -> None:
        self.tag = tag
        self.attr = {(k or "").lower(): (v if v is not None else "") for k, v in attrs}
        self.children = []


class _TreeBuilder(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#document", [])
        self.stack = [self.root]
        self.by_id = {}

    def _register(self, node: _Node) -> None:
        ident = node.attr.get("id")
        if ident and ident not in self.by_id:
            self.by_id[ident] = node

    def handle_starttag(self, tag, attrs) -> None:
        node = _Node(tag, attrs)
        self.stack[-1].children.append(node)
        self._register(node)
        if tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs) -> None:
        node = _Node(tag, attrs)
        self.stack[-1].children.append(node)
        self._register(node)

    def handle_endtag(self, tag) -> None:
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data) -> None:
        self.stack[-1].children.append(data)


def parse_html(text: str):
    builder = _TreeBuilder()
    builder.feed(text)
    builder.close()
    return builder.root, builder.by_id


def iter_elements(node: _Node):
    for child in node.children:
        if isinstance(child, _Node):
            yield child
            yield from iter_elements(child)


def rendered_text(node: _Node) -> str:
    """Text content of `node`, skipping non-rendered subtrees, PLUS this node's own accessible-
    name attributes (alt/title/aria-label) -- so a factual token injected into an image's alt on
    a `regenerate` asset is inspected too, not only prose text nodes."""
    parts = []

    def rec(n) -> None:
        if isinstance(n, str):
            parts.append(n)
        elif isinstance(n, _Node):
            if n.tag in NON_RENDERED_TAGS:
                return
            for c in n.children:
                rec(c)

    rec(node)
    for a in ("alt", "title", "aria-label"):
        v = node.attr.get(a, "")
        if v:
            parts.append(" " + v)
    return "".join(parts)


# ---- typed value-space normalization (self-contained; mirrors the harness detector) ----

def _canon_number(raw: str):
    cleaned = raw.replace(",", "").replace("$", "").replace("€", "").replace("£", "") \
        .replace("¥", "").replace("%", "").replace("+", "").strip()
    if not cleaned:
        return None
    try:
        f = float(cleaned)
    except ValueError:
        return None
    return str(int(f)) if f == int(f) else repr(f)


def _canon_date(raw: str):
    low = raw.lower()
    m = re.search(r"\b(" + _MONTH_ALT + r")\s+(\d{1,2}),\s*(\d{4})", low)
    if m:
        return f"{int(m.group(3)):04d}-{_MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"
    m2 = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", raw)
    if m2:
        return f"{int(m2.group(1)):04d}-{int(m2.group(2)):02d}-{int(m2.group(3)):02d}"
    return None


def _find_periods(text: str):
    out = set()
    for m in _RE_PERIOD_QY.finditer(text):
        out.add(f"{m.group(2)}-Q{m.group(1)}")
    for m in _RE_PERIOD_YQ.finditer(text):
        out.add(f"{m.group(1)}-Q{m.group(2)}")
    return out


def extract_typed_values(text: str):
    """Non-ML typed-token extractor. Returns a set of (type, canonical-value)."""
    vals = set()
    for m in _RE_CURRENCY.finditer(text):
        c = _canon_number(m.group())
        if c is not None:
            vals.add(("currency", c))
    for m in _RE_PERCENT.finditer(text):
        c = _canon_number(m.group())
        if c is not None:
            vals.add(("percent", c))
    for m in _RE_DATE_WORDS.finditer(text):
        d = _canon_date(m.group())
        if d is not None:
            vals.add(("date", d))
    for m in _RE_DATE_ISO.finditer(text):
        d = _canon_date(m.group())
        if d is not None:
            vals.add(("date", d))
    for p in _find_periods(text):
        vals.add(("period", p))
    for m in _RE_GROUPED_NUM.finditer(text):
        c = _canon_number(m.group())
        if c is not None:
            vals.add(("number", c))
    return vals


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


# ---- provenance domain (built from the NEW dataset -- what a regenerate slot may legitimately say) ----

def _collect_strings(obj, out: list) -> None:
    if isinstance(obj, dict):
        for v in obj.values():
            _collect_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_strings(v, out)
    elif isinstance(obj, bool):
        return
    elif isinstance(obj, (str, int, float)):
        out.append(str(obj))


def build_provenance_domain(new_data: dict) -> dict:
    """Build the provenance domain -- the tokens a `regenerate` slot may legitimately carry --
    from the NEW dataset. Generous by design (more provenanced == fewer false blocks); the
    attacker's routing/account/email tokens are still absent from it, so they are still caught."""
    strings = []
    _collect_strings(new_data, strings)
    typed = set()
    canon_flat = set()
    raw_norm = set()
    for s in strings:
        raw_norm.add(_norm(s))
        for (t, c) in extract_typed_values(s):
            typed.add((t, c))
            canon_flat.add(c)
    return {"typed": typed, "canon_flat": canon_flat, "raw_norm": raw_norm}


def _is_provenanced_typed(token, domain: dict) -> bool:
    t, c = token
    if (t, c) in domain["typed"]:
        return True
    # cross-type canon match (a currency value may also be cited as a bare number, etc.)
    return c in domain["canon_flat"]


# ---- partition-anomaly gate (on the manifest) ----

def check_partition_anomaly(manifest: dict, output_root: _Node) -> tuple:
    """Return (findings, partition_summary). Flags the force-all-frozen partition shape."""
    bindings = manifest.get("bindings", []) if isinstance(manifest, dict) else []
    class_counts = {}
    for b in bindings:
        cls = b.get("class", "unknown")
        class_counts[cls] = class_counts.get(cls, 0) + 1
    total = len(bindings)
    frozen = class_counts.get("frozen", 0)
    mutable = sum(class_counts.get(c, 0) for c in _MUTABLE_CLASSES)
    frozen_fraction = (frozen / total) if total else 0.0

    # count data-shaped tokens actually present in the rendered output
    data_tokens = len(extract_typed_values(rendered_text(output_root)))

    findings = []
    if total and frozen_fraction > FROZEN_CEILING:
        findings.append({
            "check": "partition-anomaly",
            "node": "(manifest)",
            "token": f"frozen_fraction={frozen_fraction:.3f}",
            "detail": (
                f"frozen fraction {frozen_fraction:.3f} exceeds the calibrated ceiling "
                f"{FROZEN_CEILING} ({frozen}/{total} bindings frozen) -- the force-all-frozen "
                "signature of an injected 'classify everything as frozen' instruction; a "
                "predominantly-frozen partition makes every fidelity leg pass BY CONSTRUCTION"
            ),
            "blocking": True,
        })
    if mutable == 0 and data_tokens >= MIN_DATA_TOKENS:
        findings.append({
            "check": "partition-anomaly",
            "node": "(manifest)",
            "token": f"mutable_bindings=0, data_tokens={data_tokens}",
            "detail": (
                f"ZERO mutable (surgical/regenerate/needs-review) bindings, yet the output "
                f"carries {data_tokens} data-shaped token(s) (>= {MIN_DATA_TOKENS}). A report full "
                "of data with nothing to rebind is the force-all-frozen attack shape: stale data "
                "would ship byte-identical to the template (which is what a leak already is)"
            ),
            "blocking": True,
        })

    summary = {
        "class_counts": class_counts,
        "total_bindings": total,
        "frozen_fraction": round(frozen_fraction, 4),
        "frozen_ceiling": FROZEN_CEILING,
        "mutable_bindings": mutable,
        "data_shaped_tokens": data_tokens,
    }
    return findings, summary


# ---- provenance-bound narrative (on regenerate slots in the output) ----

_SIMPLE_ID_SELECTOR = re.compile(r"^#([A-Za-z][\w-]*)$")


def _regenerate_slot_text(anchor: dict, by_id: dict, html_text: str):
    """The rendered text of a `regenerate` slot named by `anchor`, resolving BOTH an element_id /
    simple '#id' anchor (fast, via by_id) AND a COMPOUND css_selector anchor (via the shared
    rr_anchor, P2 #8) — so an attacker payload injected into a compound-anchored regenerate slot is
    inspected too, not silently skipped. Returns (slot_label, text) or None if it names no node."""
    kind = anchor.get("kind")
    value = anchor.get("value", "")
    if kind == "element_id":
        node = by_id.get(value)
        return (value, rendered_text(node)) if node is not None else None
    if kind == "css_selector":
        m = _SIMPLE_ID_SELECTOR.match(value or "")
        if m:
            node = by_id.get(m.group(1))
            return (m.group(1), rendered_text(node)) if node is not None else None
        if value:
            try:
                resolved = rr_anchor.try_resolve(html_text, anchor)
            except rr_anchor.AnchorError:
                return None
            if resolved is None:
                return None
            sub_root, _sub_ids = parse_html(resolved.outer_text(html_text))
            for child in sub_root.children:
                if isinstance(child, _Node):
                    return (value, rendered_text(child))
    return None


def check_provenance_bound_narrative(manifest: dict, by_id: dict, domain: dict,
                                     html_text: str = "") -> tuple:
    """Return (findings, checked_slots). Every factual/contact/imperative token in a `regenerate`
    slot must trace to the provenance domain; un-provenanced -> BLOCK."""
    findings = []
    checked_slots = []
    bindings = manifest.get("bindings", []) if isinstance(manifest, dict) else []
    for b in bindings:
        if b.get("class") != "regenerate":
            continue
        anchor = b.get("anchor", {})
        resolved = _regenerate_slot_text(anchor, by_id, html_text)
        if resolved is None:
            continue
        slot_id, text = resolved
        checked_slots.append(slot_id)

        # (a) un-provenanced typed values (a figure that does not come from the new source)
        for token in extract_typed_values(text):
            if not _is_provenanced_typed(token, domain):
                findings.append({
                    "check": "provenance-bound-narrative",
                    "node": f"#{slot_id}",
                    "token": f"{token[0]}:{token[1]}",
                    "detail": (
                        f"a {token[0]} value in a `regenerate` slot does not trace to any manifest "
                        "binding / the new-data provenance domain -- an un-provenanced figure"
                    ),
                    "blocking": True,
                })

        # (b) emails -- never legitimate un-provenanced in a regenerated report body
        for email in set(_RE_EMAIL.findall(text)):
            if _norm(email) not in domain["raw_norm"]:
                findings.append({
                    "check": "provenance-bound-narrative", "node": f"#{slot_id}",
                    "token": email,
                    "detail": "an un-provenanced email address in a `regenerate` slot -- the "
                              "delivery vector for a phishing / BEC contact injection",
                    "blocking": True,
                })

        # (c) URLs
        for url in set(_RE_URL.findall(text)):
            if _norm(url) not in domain["raw_norm"]:
                findings.append({
                    "check": "provenance-bound-narrative", "node": f"#{slot_id}",
                    "token": url,
                    "detail": "an un-provenanced URL in a `regenerate` slot -- a novel link no "
                              "fidelity leg inspects",
                    "blocking": True,
                })

        # (d) bare long numeric identifiers (account / routing / order numbers)
        for digits in set(_RE_BARE_DIGITS.findall(text)):
            c = _canon_number(digits)
            if c is None or (c not in domain["canon_flat"] and _norm(digits) not in domain["raw_norm"]):
                findings.append({
                    "check": "provenance-bound-narrative", "node": f"#{slot_id}",
                    "token": digits,
                    "detail": "an un-provenanced bare numeric identifier (5+ unbroken digits -- an "
                              "account / routing number) in a `regenerate` slot; legitimate figures "
                              "render grouped/decimal and trace to the new source",
                    "blocking": True,
                })

        # (e) instruction-injection / payment-redirect imperatives
        low = text.lower()
        for phrase in _INJECTION_IMPERATIVES:
            if phrase in low:
                findings.append({
                    "check": "provenance-bound-narrative", "node": f"#{slot_id}",
                    "token": phrase,
                    "detail": (
                        f"an instruction/payment imperative ({phrase!r}) in a `regenerate` slot -- "
                        "command-shaped text a legitimate report narrative does not carry; the "
                        "signature of injected attacker prose"
                    ),
                    "blocking": True,
                })
    return findings, checked_slots


# ---- assemble the sub-receipt ----

def guard(html_text: str, manifest: dict, new_data: dict) -> dict:
    """Run both checks and return the injection-guard sub-receipt dict."""
    output_root, by_id = parse_html(html_text)
    domain = build_provenance_domain(new_data if isinstance(new_data, dict) else {})

    partition_findings, partition_summary = check_partition_anomaly(manifest, output_root)
    narrative_findings, checked_slots = check_provenance_bound_narrative(
        manifest, by_id, domain, html_text)

    findings = partition_findings + narrative_findings
    blocking = [f for f in findings if f["blocking"]]
    gate = "FAIL" if blocking else "PASS"

    return {
        "schema": SCHEMA,
        "gate_version": GATE_VERSION,
        "gate": gate,
        "posture": "all template/source/OCR text treated as DATA, never instructions "
                   "(webfetch-hardening); the guard never obeys what it reads, it only measures",
        "counts": {"blocking": len(blocking), "total_findings": len(findings)},
        "findings": findings,
        "partition": partition_summary,
        "checked_regenerate_slots": checked_slots,
        "provenance_domain_size": len(domain["canon_flat"]) + len(domain["raw_norm"]),
    }


def guard_files(html_path: Path, manifest_path: Path, new_data_path: Path) -> dict:
    manifest = load_json_file(manifest_path)
    new_data = load_json_file(new_data_path)
    if not isinstance(manifest, dict):
        raise InjectionGuardError("manifest must be a JSON object")
    if not isinstance(new_data, dict):
        raise InjectionGuardError("new-data must be a JSON object")
    try:
        html_text = html_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InjectionGuardError(f"could not read HTML file: {exc}") from exc
    return guard(html_text, manifest, new_data)


# ---- CLI ----

def _emit_error(message: str) -> None:
    print(json.dumps({"schema": SCHEMA, "ok": False, "error": message}), file=sys.stdout)
    print(f"[error] {message}", file=sys.stderr)


def _print_text(receipt: dict) -> None:
    print(f"report-injection-guard v{GATE_VERSION} -- prompt-injection / untrusted-content gate")
    print(f"  gate: {receipt['gate']}")
    p = receipt["partition"]
    print(f"  partition: {p['class_counts']} | frozen_fraction={p['frozen_fraction']} "
          f"(ceiling {p['frozen_ceiling']}) | mutable={p['mutable_bindings']} "
          f"| data_tokens={p['data_shaped_tokens']}")
    print(f"  regenerate slots checked: {receipt['checked_regenerate_slots']}")
    if receipt["findings"]:
        print("  findings:")
        for f in receipt["findings"]:
            tier = "BLOCK" if f["blocking"] else "advisory"
            print(f"    [{tier}] {f['check']} @ {f['node']} :: {f['token']}")
            print(f"           {f['detail']}")
    else:
        print("  no findings -- partition healthy; every regenerate-slot token is provenanced")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="injection_guard.py",
        description="Prompt-injection / untrusted-content gate: partition-anomaly tripwire + "
                    "provenance-bound narrative check over a report-regeneration output.",
    )
    p.add_argument("--html", metavar="PATH", help="path to the output HTML to guard")
    p.add_argument("--manifest", metavar="PATH", help="path to the binding-manifest JSON")
    p.add_argument("--new-data", dest="new_data", metavar="PATH",
                   help="path to the new-dataset JSON (the provenance domain)")
    p.add_argument("--frozen-ceiling", dest="frozen_ceiling", type=float, default=None,
                   help=f"override the frozen-fraction ceiling (default {FROZEN_CEILING})")
    p.add_argument("--format", dest="out_format", choices=["json", "text"], default="text",
                   help="output format (default: text)")
    p.add_argument("--pretty", action="store_true", help="pretty-print the JSON sub-receipt")
    p.add_argument("--version", action="store_true", help="print the gate version and exit")
    return p


def main(argv) -> int:
    global FROZEN_CEILING
    args = build_parser().parse_args(argv)
    if args.version:
        print(GATE_VERSION)
        return 0
    if not (args.html and args.manifest and args.new_data):
        build_parser().print_usage(sys.stderr)
        _emit_error("--html, --manifest and --new-data are all required (or pass --version)")
        return 2
    if args.frozen_ceiling is not None:
        if not (0.0 < args.frozen_ceiling <= 1.0):
            _emit_error("--frozen-ceiling must be in (0.0, 1.0]")
            return 2
        FROZEN_CEILING = args.frozen_ceiling
    try:
        html_path = safe_read_path(args.html)
        manifest_path = safe_read_path(args.manifest)
        new_data_path = safe_read_path(args.new_data)
        receipt = guard_files(html_path, manifest_path, new_data_path)
    except InjectionGuardError as exc:
        _emit_error(str(exc))
        return 2

    if args.out_format == "json":
        print(json.dumps(receipt, indent=2 if args.pretty else None))
    else:
        _print_text(receipt)
    return 1 if receipt["gate"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
