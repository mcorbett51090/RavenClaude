"""Shared rules for the lifecycle layer: which cells sit under a concept, what is computed from
them, and the mechanical checks every authored line must pass.

What is computed, never authored: the cells a line cites (all of that agent's cells for the
concept's rows), their state counts, a content hash that goes stale when a cell is edited, and the
conditions ("only if") taken from the cells' own limitations with evidence-gap sentences filtered
out. What is authored: a plain line for a lay reader and a technical line for the details.

Standard library only.
"""

import hashlib
import json
import re

PLAIN_MAX = 280
TECH_MAX = 420
STATE_WEIGHT = {"supported": 2, "partial": 1}  # everything else is 0: it adds no documented control
GAP_MARK = re.compile(
    r"\b(no cited quotes?|cited quotes?|the quote covers|no quote|cited pages?|none states?|"
    r"none of the cited|quotes? (?:name|names|say|says|state|states))\b",
    re.IGNORECASE,
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z`\"(])")

CODE_TOKEN = re.compile(
    r"`[^`]+`"  # anything in backticks
    r"|(?<![\w-])--?[A-Za-z][\w-]*"  # a flag
    r"|\b[a-z]+_[a-z0-9_]+\b"  # snake_case
    r"|\b[a-z]+[A-Z][A-Za-z]+\b"  # camelCase
    r"|\b[\w./-]+\.(?:md|json|toml|yaml|yml|sh|py|js|ts|txt)\b"  # a file name
    r"|\$[A-Z_]+"  # an environment variable reference
    r"|\b[A-Z][A-Z0-9_]{3,}\b"  # CONSTANT_NAMES
    r"|(?<![\w/])/[a-z][\w-]+"  # a slash command
)
ALLOWED_CAPS = {"MCP", "SDK", "IDE", "CLI", "API", "CI", "AI", "SSO", "OS", "URL", "VS"}
NUMBER = re.compile(r"\b\d[\d,.]*\d\b|\b\d\b")
LAY_BANNED = (
    "yaml",
    "json",
    "toml",
    "regex",
    "glob",
    "stdin",
    "stdout",
    "stderr",
    "frontmatter",
    "jwt",
    "oauth",
    "payload",
    "endpoint",
    "schema",
    "boolean",
    "callback",
    "daemon",
    "subprocess",
    "flag",
    "flags",
    "env var",
    "environment variable",
)
SCAFFOLDING = re.compile(
    r"events named|quote truncated|cited quotes?|cited pages?|\bE-[a-z][a-z-]*-\d{3,}\b",
    re.IGNORECASE,
)
QUANTIFIERS = ("always", "every", "all", "never", "any", "each", "entire", "exactly", "everything")
ABSENCE = re.compile(
    r"\b(does not have|doesn't have|has no|have no|lacks?|cannot|can't|no support|not supported|"
    r"unsupported|never)\b",
    re.IGNORECASE,
)
NEGATION = re.compile(r"\b(not|no|never|cannot|without|none|nothing|\w+n't)\b", re.IGNORECASE)


def squash(text):
    return " ".join((text or "").split())


def cell_text(cell):
    return squash(f"{cell.get('value') or ''} {cell.get('limitation') or ''}")


def concept_cells(cells_by_sid, sid, concept):
    """The agent's cells for the concept's rows, in the concept's row order."""
    index = {c.get("row"): c for c in cells_by_sid.get(sid, [])}
    return [index[row] for row in concept["rows"] if row in index]


def cells_sha(cells):
    """A hash over what a line is allowed to say; editing a cell changes it."""
    parts = [
        [c["id"], c["state"], c["verification"], c.get("value") or "", c.get("limitation") or ""]
        for c in sorted(cells, key=lambda c: c["id"])
    ]
    return hashlib.sha256(
        json.dumps(parts, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def aggregate(cells):
    """Counts and a documented-control fraction from the cells' states; nothing is authored."""
    counts = {}
    for c in cells:
        counts[c["state"]] = counts.get(c["state"], 0) + 1
    total = len(cells)
    score = sum(STATE_WEIGHT.get(c["state"], 0) for c in cells)
    # A row that does not apply to the product is left out of the average. A concept with no row that
    # was both applicable and researched has no score, rather than a 0% that reads as "documents nothing".
    applicable = total - counts.get("not-applicable", 0)
    researched = applicable - counts.get("not-researched", 0)
    return {
        "rows": total,
        "counts": dict(sorted(counts.items())),
        "unverified": sum(1 for c in cells if c["verification"] == "unverified"),
        "fraction": (score / (2 * applicable)) if researched > 0 else None,
    }


def badge(agg):
    """A plain word for how well the vendor documents this concept, from the counts only."""
    if not agg["rows"]:
        return "not researched"
    counts = agg["counts"]
    documented = (
        counts.get("supported", 0) + counts.get("partial", 0) + counts.get("not-exposed", 0)
    )
    if documented == 0:
        # "not documented" is a sweep finding: it needs every row that applies to have been swept.
        # Rows nobody researched, or that do not apply, never produce it.
        applicable = agg["rows"] - counts.get("not-applicable", 0)
        if not applicable:
            return "not applicable"
        if counts.get("undocumented", 0) == applicable:
            return "not documented"
        return "not researched"
    if counts.get("undocumented", 0) or counts.get("not-researched", 0):
        return "partly documented"
    if counts.get("partial", 0):
        return "documented, with limits"
    return "documented"


def split_sentences(text):
    return [s for s in SENTENCE_SPLIT.split(squash(text)) if s]


def derived_conditions(cells):
    """``[(cell id, sentence)]`` of product conditions taken from limitations, gap sentences removed."""
    out, gaps = [], 0
    for c in cells:
        for sentence in split_sentences(c.get("limitation") or ""):
            if GAP_MARK.search(sentence):
                gaps += 1
            else:
                out.append((c["id"], sentence))
    return out, gaps


def code_tokens(text):
    found = []
    for m in CODE_TOKEN.finditer(text or ""):
        token = m.group(0).strip("`").rstrip(".,;:)")
        if token and token not in found:
            found.append(token)
    return found


def numbers(text):
    return sorted({n.replace(",", "") for n in NUMBER.findall(text or "")})


def _norm(text):
    return squash(text).lower().replace("`", "")


def technical_problems(line, cells):
    """Code-like tokens and numbers in a line must appear in the cells it cites."""
    corpus = _norm(" ".join(cell_text(c) for c in cells))
    corpus_numbers = {n.replace(",", "") for n in NUMBER.findall(corpus)}
    problems = []
    for token in code_tokens(line):
        if _norm(token).split("=")[0] not in corpus:
            problems.append(f"token not in the cited cells: {token}")
    for n in numbers(line):
        if n not in corpus_numbers:
            problems.append(f"number not in the cited cells: {n}")
    return problems


def lay_problems(plain, glossary_terms):
    """A plain line has no code, no unglossed jargon and none of the pipeline's scaffolding."""
    problems = []
    if not plain or len(plain) < 12:
        problems.append("plain line is empty or too short")
    if len(plain) > PLAIN_MAX:
        problems.append(f"plain line is {len(plain)} characters, over {PLAIN_MAX}")
    if "`" in plain:
        problems.append("plain line contains a backtick")
    for token in code_tokens(plain):
        if token in ALLOWED_CAPS or token.lower() in {t.lower() for t in glossary_terms}:
            continue
        problems.append(f"code-like token in a plain line: {token}")
    lowered = f" {plain.lower()} "
    for word in LAY_BANNED:
        if re.search(rf"(?<![\w-]){re.escape(word)}(?![\w-])", lowered):
            problems.append(f"jargon not allowed in a plain line: {word}")
    if SCAFFOLDING.search(plain):
        problems.append("pipeline scaffolding leaked into a plain line")
    if not plain.rstrip().endswith((".", "?")):
        problems.append("plain line does not end like a sentence")
    return problems


def wording_problems(text, cells):
    """Quantifiers and absence claims need support in the cells they cite."""
    corpus = _norm(" ".join(cell_text(c) for c in cells))
    problems = []
    words = set(re.findall(r"[a-z']+", text.lower()))
    for q in QUANTIFIERS:
        if q in words and not re.search(rf"\b{q}\b", corpus):
            problems.append(f"quantifier not supported by the cited cells: {q}")
    states = {c["state"] for c in cells}
    if ABSENCE.search(text) and "not-exposed" not in states and not ABSENCE.search(corpus):
        if "undocumented" in states or not NEGATION.search(corpus):
            problems.append("absence claim the cited cells do not make")
    if (
        NEGATION.search(text)
        and not NEGATION.search(corpus)
        and not states & {"undocumented", "not-exposed"}
    ):
        problems.append("negation not found in the cited cells")
    return problems


STOP = set(
    "the a an and or of to in on for with is are be by as at it its this that from can may only "
    "when if not no use used uses using which also into per than then they them their there these "
    "those will would should does doing done has have had was were been being such any each other".split()
)


def key_terms(sentence):
    return {w for w in re.findall(r"[a-z]{5,}", sentence.lower()) if w not in STOP}


def stem(word):
    return re.sub(r"(ing|ed|es|s)$", "", word)


def carry_through_problems(plain, technical, cells):
    """Every partial cell with a product condition must leave a trace of it in the line.

    A trace is a word the limitation uses and the cell's own value does not, so a line that only
    repeats the capability cannot pass by sharing its vocabulary with the limitation. When the
    limitation restates the value (fewer than two words of its own), any of its words will do.
    """
    text = f"{plain} {technical}".lower()
    problems = []
    for c in cells:
        if c["state"] != "partial":
            continue
        own = [s for _cid, s in derived_conditions([c])[0]]
        if not own:
            continue
        terms = set().union(*(key_terms(s) for s in own))
        seen = {stem(w) for w in key_terms(c.get("value") or "")}
        distinct = {t for t in terms if stem(t) not in seen}
        terms = (
            distinct if len(distinct) >= 2 else terms
        )  # a restated limitation shares the value's words
        if terms and not any(t in text for t in terms):
            problems.append(f"the limitation of {c['id']} left no trace in the line")
    return problems


def line_problems(entry, cells, glossary_terms):
    """All mechanical problems of one authored line (plain + technical) against its cells."""
    plain, technical = entry.get("plain", ""), entry.get("technical", "")
    problems = lay_problems(plain, glossary_terms)
    if not technical or len(technical) > TECH_MAX:
        problems.append("technical line is missing or over the length limit")
    problems += technical_problems(f"{plain} {technical}", cells)
    problems += wording_problems(f"{plain} {technical}", cells)
    problems += carry_through_problems(plain, technical, cells)
    if entry.get("cells_sha") != cells_sha(cells):
        problems.append("cells_sha does not match: a cited cell changed, or the line was moved")
    note = entry.get("order_note")
    if note is not None:
        ids = {c["id"] for c in cells}
        if not isinstance(note, dict) or note.get("cell") not in ids or not note.get("text"):
            problems.append("order_note must name one of the cited cells")
        elif note.get("quote") and _norm(note["quote"]) not in _norm(
            cell_text(next(c for c in cells if c["id"] == note["cell"]))
        ):
            problems.append("order_note quote is not a verbatim part of its cell")
    return problems
