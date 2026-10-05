"""Render the lifecycle layer: the step-by-step guide, the lay comparison and the per-agent trees.

Pages (all generated from data/lifecycle.json, lifecycle-lines.json, trees.json, the cells and the
lever records; nothing is drafted here):

    lifecycle.html        every concept a harness handles, in order, with one plain line per agent
    compare.html          concept by agent, with a computed direction and a boxed editorial view
    trees/index.html      how to read the trees
    trees/<agent>.html    the request flow, decision points and where to set model, effort and mode

Vendor-derived text is escaped like everywhere else. A claim about an agent is a line tied to its
cells by a hash; general explanations and editorial views are labelled as such.
"""

import lifecycle_common as lc
from render import as_dict, as_list, document, esc, heading, local_link, table, td, th

GENERAL_LABEL = "How this works in general: not a vendor claim"
EDITORIAL_LABEL = "Editorial: our view, not a vendor claim"
BADGE_CLASS = {
    "documented": "s-supported",
    "documented, with limits": "s-partial",
    "partly documented": "s-not-researched",
    "not documented": "s-undocumented",
    "not researched": "s-nodata",
    "not applicable": "s-not-applicable",
}
BADGE_GLYPH = {
    "documented": "●",
    "documented, with limits": "◐",
    "partly documented": "◔",
    "not documented": "?",
    "not researched": "·",
    "not applicable": "–",
}
SCORE_NOTE = (
    "Each row a vendor documents as supported scores 2, as partial 1, and as undocumented or "
    "deliberately not exposed 0. A concept's score is the average over its rows, as a percentage. "
    "A higher score means more documented control, not a better product."
)
CAVEAT_HEAD = (
    "Not documented is not the same as cannot. Columns differ a great deal in how much their "
    "documentation says, so a low score can reflect thin documentation as much as a missing feature."
)
MODEL_ROWS = (
    "F18.model-dependence",
    "F17.auto-routing",
    "F21.shared-model-selection",
    "F09.per-agent-model",
)
LEVER_ORDER = ("model", "effort", "mode", "parallelism", "other")
TREES = "trees/index.html"


class Layer:
    """The lifecycle data joined to the cells; everything derived is computed here."""

    def __init__(self, atlas):
        self.atlas = atlas
        self.life = atlas.life
        self.lines = as_dict(as_dict(atlas.lines).get("agents"))
        self.trees = as_dict(as_dict(atlas.trees).get("agents"))
        self.concepts = as_list(self.life.get("concepts"))
        self.by_id = {c["id"]: c for c in self.concepts}
        self.stages = as_list(self.life.get("stages"))
        self.glossary = as_dict(self.life.get("glossary"))
        self.cells_by_sid = {
            sid: [c for (s, _r), c in atlas.cells.items() if s == sid] for sid in atlas.surface_ids
        }
        self.row_concept = {row: c["id"] for c in self.concepts for row in c["rows"]}

    def cells(self, sid, concept):
        return lc.concept_cells(self.cells_by_sid, sid, concept)

    def agg(self, sid, concept):
        return lc.aggregate(self.cells(sid, concept))

    def line(self, sid, concept):
        return as_dict(as_dict(self.lines.get(sid)).get(concept["id"]))

    def name(self, sid):
        return self.atlas.surface_name(sid)


def badge_html(label, unverified=0):
    glyph = BADGE_GLYPH.get(label, "·")
    mark = ' <span class="uv" role="img" aria-label="unverified">!</span>' if unverified else ""
    return (
        f'<span class="g" role="img" aria-label="{esc(label)}">{glyph}</span> '
        f'<span class="w">{esc(label)}</span>{mark}'
    )


def pct(fraction):
    return "n/a" if fraction is None else f"{round(fraction * 100)}%"


def caveat(layer):
    """The documentation-coverage caveat, with each agent's undocumented count from the cells."""
    counts = {
        sid: sum(1 for c in layer.cells_by_sid[sid] if c["state"] == "undocumented")
        for sid in layer.atlas.surface_ids
    }
    ranked = sorted(counts, key=lambda sid: (-counts[sid], sid))
    detail = ", ".join(f"{layer.name(sid)} {counts[sid]}" for sid in ranked)
    return f"{CAVEAT_HEAD} Checks, out of 127, where the vendor's documentation says nothing, most first: {detail}."


def concept_link(page, concept):
    return local_link(page, "lifecycle.html", concept["name_plain"], f"c-{concept['id']}")


def links_to(layer, page, ids):
    found = [layer.by_id[i] for i in ids if i in layer.by_id]
    return ", ".join(concept_link(page, c) for c in found) if found else "none"


def cell_link(layer, page, sid, row):
    return local_link(page, layer.atlas.harness_path(sid), f"{row}", f"{sid}/{row}")


def conditions_html(cells):
    conditions, gaps = lc.derived_conditions(cells)
    if not conditions:
        return "<p>No condition is documented for these rows.</p>"
    items = "".join(f"<li>{esc(sentence)}</li>" for _cid, sentence in conditions)
    note = ""
    if gaps:
        note = f'<p class="muted">{gaps} limitation sentence(s) only record what the docs do not say.</p>'
    return f"<p><strong>Documented conditions:</strong></p><ul>{items}</ul>{note}"


def agent_rows(layer, page, concept):
    rows = []
    for sid in layer.atlas.surface_ids:
        cells = layer.cells(sid, concept)
        agg = lc.aggregate(cells)
        label = lc.badge(agg)
        entry = layer.line(sid, concept)
        plain = esc(entry.get("plain")) if entry else '<span class="nodata">no line</span>'
        details = []
        if entry:
            details.append(f"<p>{esc(entry.get('technical'))}</p>")
            note = as_dict(entry.get("order_note"))
            if note:
                details.append(f"<p><strong>Documented order:</strong> {esc(note.get('text'))}</p>")
            details.append(conditions_html(cells))
            links = ", ".join(cell_link(layer, page, sid, c["row"]) for c in cells)
            details.append(f'<p class="cite">Atlas entries behind this line: {links}</p>')
        detail_html = (
            f"<details><summary>Details</summary>{''.join(details)}</details>" if details else ""
        )
        agent = local_link(page, f"trees/{sid}.html", layer.name(sid))
        rows.append(
            (
                f"{concept['id']}-{sid}",
                [
                    th(agent, "row"),
                    td(badge_html(label, agg["unverified"]), BADGE_CLASS.get(label, "")),
                    td(plain),
                    td(detail_html),
                ],
            )
        )
    return rows


def render_concept(layer, page, concept):
    body = [
        f'<section class="concept" id="c-{esc(concept["id"])}">',
        f"<h3>{concept['order']}. {esc(concept['name_plain'])}</h3>",
        f'<p class="general"><span class="label">{esc(GENERAL_LABEL)}</span> '
        f"{esc(concept['what_it_does'])}</p>",
        '<ul class="facts">'
        f"<li><strong>Typically comes after:</strong> {links_to(layer, page, concept['typical_after'])}</li>"
        f"<li><strong>Depends on:</strong> {links_to(layer, page, concept['depends_on'])}</li>"
        f"<li><strong>Only if:</strong> {esc(concept['predicate_general'])}</li>"
        f"<li><strong>Who normally does the work:</strong> {esc(concept['who_normally_does_it'])}</li>"
        "</ul>",
        f'<aside class="editorial"><span class="label">{esc(EDITORIAL_LABEL)}</span> '
        f"{esc(concept['matters_for_model_choice'])}</aside>",
    ]
    if concept["gap"] == "full":
        body.append(
            '<p class="gapnote"><strong>Not yet researched for any agent.</strong> '
            "The atlas has no rows for this step, so nothing here says whether an agent does it.</p>"
        )
    else:
        if concept["gap"] == "partial":
            body.append(
                '<p class="gapnote"><strong>Only partly covered.</strong> The rows below are '
                "what the atlas has; the step has parts it has not researched.</p>"
            )
        head = [th(c) for c in ("Agent", "What the docs show", "In plain words", "Details")]
        body.append(
            table(f"{concept['name_plain']}, per agent", head, agent_rows(layer, page, concept))
        )
    body.append("</section>")
    return "\n".join(body)


def intro_block(layer):
    gaps_full = [c["name_plain"] for c in layer.concepts if c["gap"] == "full"]
    gaps_part = [c["name_plain"] for c in layer.concepts if c["gap"] == "partial"]
    legend = "".join(
        f"<li>{badge_html(label)}</li>"
        for label in (
            "documented",
            "documented, with limits",
            "partly documented",
            "not documented",
        )
    )
    return "\n".join(
        [
            "<p>A coding agent is two things. The <strong>model</strong> is the AI that reads text and "
            "writes text. The <strong>harness</strong> is the program around it: it decides what the "
            "model reads, offers it tools, checks permissions, runs commands and shows you the result. "
            "This page walks through everything the harness does, in the order it typically happens, "
            "so you can see which parts of an agent's work the harness does itself, and what each "
            "vendor documents about them.</p>",
            "<p>Each step shows what the vendor's own documentation says for each of eight agents. The "
            "order is the <em>typical</em> order across harnesses; a vendor's documentation seldom "
            "states it, and where it does the step says so.</p>",
            f"<p><strong>The badges</strong> summarise how well a vendor documents the step:</p><ul>{legend}</ul>",
            '<p>A <span class="uv" role="img" aria-label="unverified">!</span> means at least one of '
            "the checks behind it was outside the sample we double-checked.</p>",
            f"<p><strong>Not yet researched:</strong> {esc(', '.join(gaps_full))}. "
            f"<strong>Only partly covered:</strong> {esc(', '.join(gaps_part))}. These are the steps "
            "where a harness often makes up for a weaker model, so the gap matters.</p>",
            f"<p>{esc(caveat(layer))}</p>",
        ]
    )


def glossary_block(layer):
    items = "".join(
        f"<dt>{esc(term)}</dt><dd>{esc(text)}</dd>"
        for term, text in sorted(layer.glossary.items(), key=lambda kv: kv[0].lower())
    )
    return heading(2, "Words used here", "glossary") + f"<dl>{items}</dl>"


def render_lifecycle(layer):
    page = "lifecycle.html"
    body = [intro_block(layer)]
    for stage in layer.stages:
        body.append(heading(2, f"{stage['id']}. {stage['name']}", f"stage-{stage['id']}"))
        body.append(f"<p>{esc(stage['blurb'])}</p>")
        for concept in layer.concepts:
            if concept["stage"] == stage["id"]:
                body.append(render_concept(layer, page, concept))
    body.append(glossary_block(layer))
    return document(page, "Lifecycle", "How a coding agent works, step by step", "\n".join(body))


# --- the comparison ----------------------------------------------------------------------------


def direction_text(layer, concept):
    scored = [(layer.agg(sid, concept)["fraction"], sid) for sid in layer.atlas.surface_ids]
    scored = [(f, s) for f, s in scored if f is not None]
    if not scored:
        return "Nothing to compare: no agent has rows for this step."
    top, bottom = max(f for f, _ in scored), min(f for f, _ in scored)

    def names(fraction):
        return ", ".join(layer.name(s) for f, s in scored if f == fraction)

    if top == bottom:
        return f"The agents document this step to the same degree ({pct(top)})."
    return f"Documents the most: {names(top)} ({pct(top)}). Documents the least: {names(bottom)} ({pct(bottom)})."


def totals_rows(layer, page):
    rows = []
    for sid in layer.atlas.surface_ids:
        counts, fractions = {}, []
        for concept in layer.concepts:
            if not concept["rows"]:
                continue
            agg = layer.agg(sid, concept)
            label = lc.badge(agg)
            counts[label] = counts.get(label, 0) + 1
            if agg["fraction"] is not None:
                fractions.append(agg["fraction"])
        overall = sum(fractions) / len(fractions) if fractions else None
        undocumented = sum(1 for c in layer.cells_by_sid[sid] if c["state"] == "undocumented")
        cells = [th(local_link(page, f"trees/{sid}.html", layer.name(sid)), "row")]
        for label in (
            "documented",
            "documented, with limits",
            "partly documented",
            "not documented",
        ):
            cells.append(td(str(counts.get(label, 0))))
        cells += [td(pct(overall)), td(str(undocumented))]
        rows.append((None, cells))
    return rows


def model_panel(layer, page):
    out = [heading(2, "Where the model comes into it", "model")]
    out.append(
        "<p>These are the checks that tie a harness to a model: whether it depends on the model, picks one "
        "automatically, shares model choice with a platform, or lets each helper agent use its own. "
        "<em>No documented model dependence</em> means the documentation does not describe one, which "
        "is not the same as there being none.</p>"
    )
    head = [th(c) for c in ("Agent", *[r.split(".", 1)[1] for r in MODEL_ROWS])]
    rows = []
    for sid in layer.atlas.surface_ids:
        cells = [th(local_link(page, f"trees/{sid}.html", layer.name(sid)), "row")]
        for row in MODEL_ROWS:
            cell = layer.atlas.cells.get((sid, row))
            if cell is None:
                cells.append(td('<span class="nodata">no data</span>'))
                continue
            word = {
                "supported": "documented",
                "partial": "documented, with limits",
                "undocumented": "not documented",
                "not-exposed": "vendor says none",
            }.get(cell["state"], cell["state"])
            link = cell_link(layer, page, sid, row)
            cells.append(td(f"{esc(word)}<br>{link}", f"s-{cell['state']}"))
        rows.append((None, cells))
    out.append(table("Documented ties between harness and model", head, rows))
    return "\n".join(out)


def render_compare(layer):
    page = "compare.html"
    atlas = layer.atlas
    body = [
        "<p>What each vendor documents about the harness around its model. The grid compares how well "
        "each vendor documents every step of the lifecycle; the sections below name who documents the "
        "most, and add a boxed editorial view of why it matters when you choose a model.</p>",
        f"<p>{esc(SCORE_NOTE)}</p>",
        f'<p class="gapnote"><strong>Read this first:</strong> {esc(caveat(layer))}</p>',
        heading(2, "Overview by agent", "totals"),
    ]
    head = [th("Agent")] + [
        th(label) for label in ("documented", "with limits", "partly documented", "not documented")
    ]
    head += [th("Average score"), th("Checks with no documentation (of 127)")]
    body.append(
        table("Concepts per agent by how well they are documented", head, totals_rows(layer, page))
    )
    body.append(heading(2, "The grid", "grid"))
    head = [th("Step")] + [
        th(local_link(page, f"trees/{s}.html", layer.name(s))) for s in atlas.surface_ids
    ]
    rows = []
    for concept in layer.concepts:
        cells = [th(concept_link(page, concept), "row")]
        for sid in atlas.surface_ids:
            if not concept["rows"]:
                cells.append(td("not yet researched", "s-nodata"))
                continue
            agg = layer.agg(sid, concept)
            label = lc.badge(agg)
            cells.append(
                td(
                    f"{badge_html(label, agg['unverified'])}<br>{pct(agg['fraction'])}",
                    BADGE_CLASS.get(label, ""),
                )
            )
        rows.append((f"g-{concept['id']}", cells))
    body.append(table("Every step by every agent", head, rows, "matrix"))
    body.append(heading(2, "Step by step: who documents most, and why it matters", "directions"))
    for stage in layer.stages:
        body.append(heading(3, f"{stage['id']}. {stage['name']}"))
        for concept in layer.concepts:
            if concept["stage"] != stage["id"]:
                continue
            gap = ""
            if concept["gap"] == "full":
                gap = " Not yet researched for any agent."
            elif concept["gap"] == "partial":
                gap = " Only partly covered by the atlas."
            body.append(
                f'<div class="cell"><h4>{concept_link(page, concept)}</h4>'
                f"<p>{esc(direction_text(layer, concept) if concept['rows'] else 'No agent can be compared.')}{esc(gap)}</p>"
                f'<aside class="editorial"><span class="label">{esc(EDITORIAL_LABEL)}</span> '
                f"{esc(concept['matters_for_model_choice'])}</aside></div>"
            )
    body.append(model_panel(layer, page))
    body.append(heading(2, "What this page cannot tell you", "limits"))
    body.append(
        "<ul><li>How well any agent does a step. This is what the vendor documents, not a measurement.</li>"
        "<li>How much of an agent's quality comes from the harness and how much from the model. The "
        "atlas cannot measure that, so no share is given.</li>"
        "<li>Anything the vendor has changed since the snapshot date.</li>"
        "<li>Steps nobody has researched yet: caching, how malformed requests are handled, and how tool "
        "output is trimmed.</li></ul>"
    )
    return document(
        page, "Compare", "What each agent's harness documents, step by step", "\n".join(body)
    )


# --- the trees ---------------------------------------------------------------------------------


def decision_points_for(layer, sid):
    """``{concept id: [decision point]}`` for the agent, by the concept that owns the cell's row."""
    out = {}
    for dp in as_list(as_dict(layer.trees.get(sid)).get("decision_points")):
        row = str(dp.get("cell", "")).split("/", 1)[-1]
        out.setdefault(layer.row_concept.get(row), []).append(dp)
    return out


def decision_html(layer, page, sid, dp):
    branches = []
    for b in as_list(dp.get("branches")):
        branches.append(
            f"<li><strong>{esc(b.get('answer'))}:</strong> {esc(b.get('outcome'))}"
            f"<blockquote><p>{esc(b.get('clause'))}</p></blockquote></li>"
        )
    row = str(dp.get("cell", "")).split("/", 1)[-1]
    return (
        f'<div class="cell"><p><strong>Decision point:</strong> {esc(dp.get("question"))}</p>'
        f'<ul class="branches">{"".join(branches)}</ul>'
        f'<p class="cite">Source entry: {cell_link(layer, page, sid, row)}. Each branch quotes the '
        "vendor's documentation word for word; the order between decision points is not stated.</p></div>"
    )


def flow_html(layer, page, sid):
    points = decision_points_for(layer, sid)
    out = []
    for stage in layer.stages:
        items = []
        for concept in layer.concepts:
            if concept["stage"] != stage["id"]:
                continue
            if not concept["rows"]:
                items.append(
                    f'<li class="step"><span class="w">{esc(concept["name_plain"])}</span> '
                    f'{badge_html("not researched")} <span class="muted">not yet researched</span></li>'
                )
                continue
            agg = layer.agg(sid, concept)
            label = lc.badge(agg)
            entry = layer.line(sid, concept)
            inner = [
                f'<li class="step"><strong>{concept_link(page, concept)}</strong> {badge_html(label, agg["unverified"])}',
                f"<p>{esc(entry.get('plain'))}</p>" if entry else "",
            ]
            note = as_dict(entry.get("order_note"))
            if note:
                inner.append(f"<p><strong>Documented order:</strong> {esc(note.get('text'))}</p>")
            inner += [decision_html(layer, page, sid, dp) for dp in points.get(concept["id"], [])]
            inner.append("</li>")
            items.append("".join(inner))
        out.append(
            f'<h3 id="stage-{esc(stage["id"])}">{esc(stage["id"])}. {esc(stage["name"])}</h3>'
            f'<p class="muted">{esc(stage["blurb"])}</p><ol class="flow">{"".join(items)}</ol>'
        )
    return "\n".join(out)


def lever_tables(layer, page, sid):
    atlas = layer.atlas
    records = [lv for lv in atlas.levers if lv.get("surface") == sid]
    out = []
    classes = list(LEVER_ORDER) + sorted({lv.get("lever") for lv in records} - set(LEVER_ORDER))
    for cls in classes:
        group = [lv for lv in records if lv.get("lever") == cls]
        if not group:
            continue
        head = [th(c) for c in ("Kind", "Name", "Applies to", "Values", "Default", "Documented")]
        rows = []
        for lv in group:
            literal = (
                f"<code>{esc(lv.get('literal'))}</code>"
                if lv.get("literal")
                else '<span class="nodata">none given</span>'
            )
            values = (
                esc(", ".join(str(v) for v in as_list(lv.get("values"))))
                or '<span class="nodata">not listed</span>'
            )
            state = f"{esc(lv.get('state'))}" + (
                " !" if lv.get("verification") == "unverified" else ""
            )
            rows.append(
                (
                    None,
                    [
                        td(esc(lv.get("location_kind"))),
                        td(literal),
                        td(esc(lv.get("scope"))),
                        td(values),
                        td(
                            esc(lv.get("default"))
                            if lv.get("default")
                            else '<span class="nodata">not stated</span>'
                        ),
                        td(
                            f"{state}<br>{cell_link(layer, page, sid, lv.get('row'))}",
                            f"s-{lv.get('state')}",
                        ),
                    ],
                )
            )
        out.append(
            heading(3, f"Where to set: {cls}")
            + table(f"{layer.name(sid)}: {cls} controls", head, rows)
        )
    return "\n".join(out) or '<p class="nodata">No lever records for this agent.</p>'


def routing_appendix(layer, sid):
    rows = [t for t in layer.atlas.task_rows if t.get("surface") == sid]
    out = [
        heading(2, "Appendix: RavenClaude routing advice", "routing"),
        "<p><strong>This is RavenClaude's own advice, copied from its routing matrix. It is not "
        "vendor guidance.</strong> A task class the matrix has no row for says so.</p>",
    ]
    if not rows:
        out.append('<p class="nodata">No task-shape rows for this agent.</p>')
        return "\n".join(out)
    head = [th(c) for c in ("Task", "Tier", "Rank", "Mode", "Basis")]
    body = []
    for t in rows:
        if t.get("agent"):
            body.append(
                (
                    None,
                    [
                        td(esc(t.get("task_class"))),
                        td(esc(t.get("tier"))),
                        td(esc(t.get("rank"))),
                        td(esc(t.get("interaction_mode"))),
                        td(esc(t.get("basis"))),
                    ],
                )
            )
        else:
            body.append(
                (
                    None,
                    [
                        td(esc(t.get("task_class"))),
                        td(esc(t.get("pending_label")) or "no recommendation"),
                        td(""),
                        td(""),
                        td(""),
                    ],
                )
            )
    out.append(table(f"{layer.name(sid)} routing advice", head, body))
    return "\n".join(out)


def render_tree(layer, sid):
    page = f"trees/{sid}.html"
    body = [
        f"<p>{local_link(page, 'lifecycle.html', 'The step-by-step guide')} explains each step in general; "
        f"{local_link(page, TREES, 'how to read these trees')}.</p>",
        heading(2, "What happens to a request", "flow"),
        "<p>The steps run in the <em>typical</em> order. A documented order, where the vendor states one, "
        "is shown on its step. A decision point appears where the documentation describes a real branch; "
        "an agent with none has none documented.</p>",
        flow_html(layer, page, sid),
        heading(2, "Where to set the model, effort and mode", "levers"),
        "<p>Each row is a place the documentation says a control lives, with its values and default.</p>",
        lever_tables(layer, page, sid),
        routing_appendix(layer, sid),
    ]
    return document(
        page, layer.name(sid), f"{layer.name(sid)}: request flow and controls", "\n".join(body)
    )


def render_trees_index(layer):
    page = TREES
    items = "".join(
        f"<li>{local_link(page, f'trees/{sid}.html', layer.name(sid))}</li>"
        for sid in layer.atlas.surface_ids
    )
    body = [
        "<p>One page per agent. Each has two parts: the <strong>request flow</strong>, which walks the "
        "steps of the lifecycle with what that agent's documentation says at each, and the "
        "<strong>controls</strong>, which says where to set the model, the thinking effort and the mode.</p>",
        "<ul><li><strong>Typical order</strong>: the order harnesses usually follow. Vendors seldom document "
        "it, so most orderings are typical, not documented.</li>"
        "<li><strong>Documented order</strong>: shown only where the vendor's documentation states it.</li>"
        "<li><strong>Decision point</strong>: shown only where the documentation describes a branch, and "
        "each branch quotes it. Many agents have few or none.</li></ul>",
        f'<ul class="cols">{items}</ul>',
    ]
    return document(page, "Decision trees", "Decision trees, one per agent", "\n".join(body))


METHOD_RULES = (
    "Every line about an agent is tied to the cells it came from by a hash; changing a cell fails "
    "validation until the line is revised.",
    "A line may not use a name, number or flag its cells do not contain, may not drop a cell's stated "
    "limitation, and may not say always, never or has no unless the cells do.",
    "How a step works in general is labelled as not a vendor claim; the boxed view on the compare page "
    "is labelled editorial. Step order is the typical order unless a cell states one.",
    "Badges, scores and the documents-the-most line are computed from cell states alone. They say how "
    "much a vendor documents, not how well the agent does it.",
    "No share of an agent's quality is attributed to the harness or to the model: the atlas cannot "
    "measure that.",
)


def method_section(atlas):
    """The method page's paragraph on the lifecycle layer: its rules, its size and its gaps."""
    concepts = [c for c in as_list(as_dict(atlas.life).get("concepts")) if isinstance(c, dict)]
    gaps = [c.get("name_plain", "") for c in concepts if c.get("gap") == "full"]
    parts = [c.get("name_plain", "") for c in concepts if c.get("gap") == "partial"]
    stages = len(as_list(as_dict(atlas.life).get("stages")))
    out = [
        heading(2, "Lifecycle layer"),
        f"<p>{len(concepts)} steps in {stages} stages, each row of the matrix mapped to a step. How the "
        "plain lines are kept honest:</p>",
        "<ul>" + "".join(f"<li>{esc(rule)}</li>" for rule in METHOD_RULES) + "</ul>",
    ]
    if gaps or parts:
        out.append(
            f"<p>Not researched for any agent: {esc(', '.join(gaps) or 'none')}. Only partly "
            f"covered: {esc(', '.join(parts) or 'none')}.</p>"
        )
    return "\n".join(out)


def render_pages(atlas):
    """Every lifecycle page as {relative path: text}; empty when there is no lifecycle data."""
    if not atlas.life:
        return {}
    layer = Layer(atlas)
    pages = {"lifecycle.html": render_lifecycle(layer), "compare.html": render_compare(layer)}
    pages[TREES] = render_trees_index(layer)
    for sid in atlas.surface_ids:
        pages[f"trees/{sid}.html"] = render_tree(layer, sid)
    return pages
